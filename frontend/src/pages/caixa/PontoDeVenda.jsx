import { useCallback, useEffect, useReducer, useRef, useState } from 'react'

import { listarCategorias } from '../../api/categorias.js'
import { buscarPorCodigo, listarMaisVendidos, listarProdutos } from '../../api/produtos.js'
import { registrarVenda } from '../../api/vendas.js'
import Modal from '../../components/Modal.jsx'
import { useAtalhos } from '../../hooks/useAtalhos.js'
import { useConsulta } from '../../hooks/useConsulta.js'
import { centavosParaApi, formatarReais, paraCentavos } from '../../utils/dinheiro.js'
import { formatarDataHora } from '../../utils/datas.js'
import { mensagemDeErro } from '../../utils/erros.js'
import {
  carrinhoInicial,
  carrinhoReducer,
  interpretarEntrada,
  quantidadeDeUnidades,
  quantidadeNoCarrinho,
  totalDoCarrinho,
} from './carrinho.js'
import { termoDeFiltro } from './catalogo.js'
import GradeProdutos from './GradeProdutos.jsx'
import ListaItens from './ListaItens.jsx'
import ModalPagamento from './ModalPagamento.jsx'

/**
 * Tela principal do caixa: à esquerda, o campo de código e a grade de produtos;
 * à direita, o carrinho, o total e as ações.
 *
 * Atalhos: F2 finaliza, F4 remove o último item, Esc cancela a venda em andamento.
 * O campo de código fica sempre com o foco, para o leitor de código de barras
 * (que "digita" o código e aperta Enter) funcionar a qualquer momento. Letras
 * digitadas nele também filtram a grade; números (bipe) não filtram.
 */
export default function PontoDeVenda({ sessao, aoFecharCaixa }) {
  // useReducer: como o useState, mas as mudanças passam por uma função (o reducer)
  // que concentra as regras do carrinho. "despachar" envia uma ação para ele.
  const [carrinho, despachar] = useReducer(carrinhoReducer, carrinhoInicial)
  const [entrada, setEntrada] = useState('')
  const [buscando, setBuscando] = useState(false)
  const [erro, setErro] = useState('')
  const [resultados, setResultados] = useState(null) // busca por nome: { quantidade, produtos }
  const [modal, setModal] = useState(null) // 'pagamento' | 'cancelar' | null
  const [ultimaVenda, setUltimaVenda] = useState(null)
  // useRef: guarda uma referência ao <input> real do navegador, para dar foco nele.
  const campoRef = useRef(null)

  const { itens } = carrinho
  const total = totalDoCarrinho(itens)

  // Produtos, categorias e mais vendidos da grade, carregados juntos.
  const catalogo = useConsulta(
    () => Promise.all([listarProdutos(), listarCategorias(), listarMaisVendidos({ dias: 30 })]),
    [],
  )
  const [produtos, categorias, maisVendidos] = catalogo.dados ?? [[], [], []]
  const filtro = termoDeFiltro(entrada)
  const quantidades = new Map(itens.map((item) => [item.produto.id, item.quantidade]))

  const focarCampo = useCallback(() => campoRef.current?.focus(), [])

  // Sempre que um modal fecha, o foco volta para o campo de código.
  useEffect(() => {
    if (modal === null) focarCampo()
  }, [modal, focarCampo])

  // ---------- Itens ----------

  function adicionar(produto, quantidade) {
    const desejado = quantidadeNoCarrinho(itens, produto.id) + quantidade
    if (desejado > produto.quantidade_estoque) {
      setErro(
        `Estoque insuficiente para ${produto.nome}: disponível ${produto.quantidade_estoque}.`,
      )
      return
    }
    despachar({ tipo: 'adicionar', produto, quantidade })
    setErro('')
    setResultados(null)
  }

  async function aoEnviarEntrada(evento) {
    evento.preventDefault()
    const { quantidade, termo } = interpretarEntrada(entrada)
    if (!termo) return

    // Limpa já: o leitor pode bipar o próximo produto antes de esta busca terminar.
    // Por isso também não bloqueamos novos envios enquanto "buscando" é true.
    setEntrada('')
    setBuscando(true)
    setErro('')
    try {
      if (/^\d+$/.test(termo)) {
        adicionar(await buscarPorCodigo(termo), quantidade)
      } else {
        const produtos = await listarProdutos({ busca: termo })
        if (produtos.length === 0) {
          setErro(`Nenhum produto encontrado para "${termo}".`)
        } else if (produtos.length === 1) {
          adicionar(produtos[0], quantidade)
        } else {
          setResultados({ quantidade, produtos })
        }
      }
    } catch (falha) {
      setErro(mensagemDeErro(falha))
    } finally {
      setBuscando(false)
      focarCampo()
    }
  }

  // Clique/toque num cartão da grade: 1 unidade, com a mesma regra de estoque do leitor.
  function escolherDaGrade(produto) {
    adicionar(produto, 1)
    focarCampo()
  }

  function alterarQuantidade(item, quantidade) {
    const { nome, quantidade_estoque: disponivel } = item.produto
    if (quantidade > disponivel) {
      setErro(`Estoque insuficiente para ${nome}: disponível ${disponivel}.`)
    } else {
      despachar({ tipo: 'alterarQuantidade', produtoId: item.produto.id, quantidade })
      setErro('')
    }
    focarCampo()
  }

  function remover(item) {
    despachar({ tipo: 'remover', produtoId: item.produto.id })
    focarCampo()
  }

  // ---------- Atalhos ----------

  function abrirPagamento() {
    if (itens.length === 0) {
      setErro('Adicione ao menos um item antes de finalizar.')
      return
    }
    setResultados(null)
    setModal('pagamento')
  }

  function removerUltimo() {
    if (itens.length > 0) despachar({ tipo: 'removerUltimo' })
  }

  function pedirCancelamento() {
    if (resultados) {
      setResultados(null) // primeiro Esc só fecha a lista de busca
    } else if (itens.length > 0) {
      setModal('cancelar')
    }
  }

  function cancelarVenda() {
    despachar({ tipo: 'limpar' })
    setErro('')
    setModal(null)
  }

  // Desligados enquanto um modal está aberto (cada modal tem os seus atalhos).
  useAtalhos({ F2: abrirPagamento, F4: removerUltimo, Escape: pedirCancelamento }, modal === null)

  // ---------- Finalização ----------

  async function finalizar({ pagamentos, desconto }) {
    const venda = await registrarVenda({
      itens: itens.map((item) => ({ produto_id: item.produto.id, quantidade: item.quantidade })),
      pagamentos: pagamentos.map((p) => ({ forma: p.forma, valor: centavosParaApi(p.valor) })),
      desconto: centavosParaApi(desconto),
    })
    setUltimaVenda(venda)
    despachar({ tipo: 'limpar' })
    setErro('')
    setModal(null)
    catalogo.recarregar() // atualiza o estoque e os mais vendidos na grade
  }

  function aoClicarFecharCaixa() {
    if (itens.length > 0) {
      setErro('Finalize ou cancele a venda em andamento antes de fechar o caixa.')
      focarCampo()
      return
    }
    aoFecharCaixa()
  }

  return (
    <div className="pdv">
      <section className="pdv__principal">
        <form onSubmit={aoEnviarEntrada} className="pdv__leitor">
          <label htmlFor="campo-codigo" className="sr-only">
            Código de barras ou nome do produto
          </label>
          <input
            id="campo-codigo"
            ref={campoRef}
            className="pdv__campo-codigo"
            value={entrada}
            onChange={(e) => setEntrada(e.target.value)}
            // Se o foco "sumir" (clique numa área vazia), ele volta para cá.
            onBlur={() =>
              setTimeout(() => {
                if (document.activeElement === document.body) focarCampo()
              }, 0)
            }
            placeholder="Código de barras ou nome  ·  use 3*código para quantidade"
            autoComplete="off"
            autoFocus
          />
          <button type="submit" className="btn btn--primario btn--grande">
            {buscando ? 'Buscando...' : 'Adicionar'}
          </button>
        </form>

        {erro && (
          <div className="alerta alerta--erro" role="alert">
            {erro}
          </div>
        )}

        {resultados && (
          <div className="resultados-busca">
            <p className="texto-suave">Vários produtos encontrados. Escolha um (Esc fecha):</p>
            <ul>
              {resultados.produtos.map((produto) => (
                <li key={produto.id}>
                  <button
                    type="button"
                    onClick={() => {
                      adicionar(produto, resultados.quantidade)
                      focarCampo()
                    }}
                  >
                    <span>{produto.nome}</span>
                    <span className="texto-suave">
                      {formatarReais(paraCentavos(produto.preco))} · estoque{' '}
                      {produto.quantidade_estoque}
                    </span>
                  </button>
                </li>
              ))}
            </ul>
          </div>
        )}

        <GradeProdutos
          produtos={produtos}
          categorias={categorias}
          maisVendidos={maisVendidos}
          filtro={filtro}
          quantidades={quantidades}
          carregando={catalogo.carregando}
          erro={catalogo.erro}
          aoEscolher={escolherDaGrade}
          aoTentarDeNovo={catalogo.recarregar}
        />
      </section>

      <aside className="pdv__lateral">
        <ListaItens itens={itens} aoAlterarQuantidade={alterarQuantidade} aoRemover={remover} />

        {/* Total + Finalizar: em telas pequenas vira uma barra fixa no rodapé. */}
        <div className="pdv__fechamento">
          <div className="pdv__total">
            <span>Total</span>
            <strong>{formatarReais(total)}</strong>
            <small>
              {itens.length} item(ns) · {quantidadeDeUnidades(itens)} unidade(s)
            </small>
          </div>
          <button
            type="button"
            className="btn btn--primario btn--grande btn--bloco pdv__finalizar"
            onClick={abrirPagamento}
          >
            Finalizar venda <kbd>F2</kbd>
          </button>
        </div>

        <div className="pdv__acoes">
          <button
            type="button"
            className="btn btn--secundario btn--bloco"
            onClick={() => {
              removerUltimo()
              focarCampo()
            }}
            disabled={itens.length === 0}
          >
            Remover último <kbd>F4</kbd>
          </button>
          <button
            type="button"
            className="btn btn--perigo btn--bloco"
            onClick={pedirCancelamento}
            disabled={itens.length === 0}
          >
            Cancelar venda <kbd>Esc</kbd>
          </button>
        </div>

        {ultimaVenda && (
          <div className="pdv__ultima-venda">
            <span className="texto-suave">Última venda · nº {ultimaVenda.id}</span>
            <div className="ultima-venda__linha">
              <span>Total</span>
              <strong>{formatarReais(paraCentavos(ultimaVenda.total))}</strong>
            </div>
            <div className="ultima-venda__linha ultima-venda__troco">
              <span>Troco</span>
              <strong>{formatarReais(paraCentavos(ultimaVenda.troco))}</strong>
            </div>
          </div>
        )}

        <div className="pdv__sessao">
          <span className="texto-suave">Caixa aberto em {formatarDataHora(sessao.aberto_em)}</span>
          <button type="button" className="btn btn--fantasma" onClick={aoClicarFecharCaixa}>
            Fechar caixa
          </button>
        </div>
      </aside>

      {modal === 'pagamento' && (
        <ModalPagamento
          subtotal={total}
          aoConfirmar={finalizar}
          aoFechar={() => setModal(null)}
        />
      )}

      {modal === 'cancelar' && (
        <ModalConfirmarCancelamento
          total={total}
          aoConfirmar={cancelarVenda}
          aoVoltar={() => setModal(null)}
        />
      )}
    </div>
  )
}

function ModalConfirmarCancelamento({ total, aoConfirmar, aoVoltar }) {
  return (
    <Modal titulo="Cancelar venda em andamento?" aoFechar={aoVoltar} largura="pequena">
      <p>
        Todos os itens ({formatarReais(total)}) serão removidos. Nada foi registrado ainda, então o
        estoque não é alterado.
      </p>
      <div className="botoes-lado-a-lado">
        <button type="button" className="btn btn--secundario" onClick={aoVoltar}>
          Voltar (Esc)
        </button>
        <button type="button" className="btn btn--perigo" onClick={aoConfirmar} autoFocus>
          Cancelar venda (Enter)
        </button>
      </div>
    </Modal>
  )
}
