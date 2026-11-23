import { useState } from 'react'

import ImagemProduto from '../../components/ImagemProduto.jsx'
import { formatarReais, paraCentavos } from '../../utils/dinheiro.js'
import { situacaoDoEstoque } from '../../utils/estoque.js'
import {
  ABA_MAIS_VENDIDOS,
  ABA_TODOS,
  filtrarPorNome,
  produtosDaAba,
} from './catalogo.js'

// Clicar num cartão ou numa aba NÃO tira o foco do campo de código: o leitor de
// código de barras continua funcionando a qualquer momento.
const manterFocoNoCampo = (evento) => evento.preventDefault()

/**
 * Grade de produtos com abas de categoria. Um clique (ou toque) num cartão chama
 * aoEscolher(produto); quem decide se adiciona (estoque etc.) é o PontoDeVenda.
 *
 * filtro: termo vindo do campo de código (null = sem filtro). Com filtro, a busca
 * considera todos os produtos, qualquer que seja a aba selecionada.
 */
export default function GradeProdutos({
  produtos,
  categorias,
  maisVendidos,
  filtro,
  quantidades,
  carregando,
  erro,
  aoEscolher,
  aoTentarDeNovo,
}) {
  const [aba, setAba] = useState(ABA_TODOS)

  const abas = [
    { id: ABA_TODOS, rotulo: 'Todos' },
    ...categorias.map((categoria) => ({ id: categoria.id, rotulo: categoria.nome })),
    { id: ABA_MAIS_VENDIDOS, rotulo: 'Mais vendidos' },
  ]
  // Se a aba selecionada sumiu (ex.: categoria desativada), volta para "Todos".
  const abaAtual = abas.some((a) => a.id === aba) ? aba : ABA_TODOS
  const lista = filtro
    ? filtrarPorNome(produtos, filtro)
    : produtosDaAba(abaAtual, { produtos, maisVendidos })

  return (
    <section className="catalogo" aria-label="Produtos">
      <div className="catalogo__abas" role="tablist" aria-label="Categorias">
        {abas.map((item) => {
          const selecionada = !filtro && item.id === abaAtual
          return (
            <button
              key={item.id}
              type="button"
              role="tab"
              aria-selected={selecionada}
              className={`catalogo__aba${selecionada ? ' catalogo__aba--ativa' : ''}`}
              onMouseDown={manterFocoNoCampo}
              onClick={() => setAba(item.id)}
            >
              {item.rotulo}
            </button>
          )
        })}
      </div>

      {filtro && (
        <p className="catalogo__busca texto-suave" role="status">
          {lista.length} produto(s) para a busca digitada no campo. Apague o texto para voltar
          às abas.
        </p>
      )}

      <div className={`catalogo__grade${carregando ? ' atualizando' : ''}`}>
        {erro ? (
          <div className="catalogo__vazio">
            <div className="alerta alerta--erro">{erro}</div>
            <button type="button" className="btn btn--secundario" onClick={aoTentarDeNovo}>
              Tentar novamente
            </button>
          </div>
        ) : lista.length === 0 ? (
          <p className="catalogo__vazio texto-suave">
            {carregando
              ? 'Carregando produtos...'
              : abaAtual === ABA_MAIS_VENDIDOS && !filtro
                ? 'Ainda não há vendas nos últimos 30 dias.'
                : 'Nenhum produto aqui.'}
          </p>
        ) : (
          lista.map((produto) => (
            <CartaoProduto
              key={produto.id}
              produto={produto}
              noCarrinho={quantidades.get(produto.id) ?? 0}
              aoEscolher={aoEscolher}
            />
          ))
        )}
      </div>
    </section>
  )
}

function CartaoProduto({ produto, noCarrinho, aoEscolher }) {
  const situacao = situacaoDoEstoque(produto.quantidade_estoque)
  const esgotado = situacao === 'esgotado'
  const preco = formatarReais(paraCentavos(produto.preco))

  return (
    <button
      type="button"
      className={`cartao-produto${esgotado ? ' cartao-produto--esgotado' : ''}`}
      onMouseDown={manterFocoNoCampo}
      onClick={() => aoEscolher(produto)}
      disabled={esgotado}
      aria-label={
        esgotado
          ? `${produto.nome}, ${preco}, esgotado`
          : `Adicionar ${produto.nome}, ${preco}${noCarrinho ? `, ${noCarrinho} no carrinho` : ''}`
      }
    >
      <span className="cartao-produto__imagem">
        {/* key: se o admin trocar a foto, o cartão tenta carregar o link novo. */}
        <ImagemProduto
          key={produto.imagem_url ?? ''}
          nome={produto.nome}
          url={produto.imagem_url}
          preencher
        />
        {noCarrinho > 0 && <span className="cartao-produto__no-carrinho">×{noCarrinho}</span>}
        {situacao !== 'normal' && (
          <span
            className={`badge cartao-produto__selo ${esgotado ? 'badge--cancelada' : 'badge--aviso'}`}
          >
            {esgotado ? 'esgotado' : 'baixo'}
          </span>
        )}
      </span>
      <span className="cartao-produto__nome">{produto.nome}</span>
      <span className="cartao-produto__preco">{preco}</span>
    </button>
  )
}
