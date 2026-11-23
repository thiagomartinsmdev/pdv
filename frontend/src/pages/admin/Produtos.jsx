import { useState } from 'react'

import { atualizarProduto, desativarProduto, listarProdutos } from '../../api/produtos.js'
import ImagemProduto from '../../components/ImagemProduto.jsx'
import Modal from '../../components/Modal.jsx'
import { useAtraso } from '../../hooks/useAtraso.js'
import { useConsulta } from '../../hooks/useConsulta.js'
import { formatarReais, paraCentavos } from '../../utils/dinheiro.js'
import { mensagemDeErro } from '../../utils/erros.js'
import ModalProduto from './ModalProduto.jsx'
import './admin.css'

const ESTOQUE_BAIXO = 10

export default function Produtos() {
  const [busca, setBusca] = useState('')
  const [mostrarInativos, setMostrarInativos] = useState(false)
  const [modal, setModal] = useState(null) // { tipo: 'form' | 'desativar', produto }
  const [aviso, setAviso] = useState(null) // { tipo: 'sucesso' | 'erro', texto }

  const buscaAtrasada = useAtraso(busca.trim())
  const { dados: produtos, carregando, erro, recarregar } = useConsulta(
    () =>
      listarProdutos({ busca: buscaAtrasada || undefined, incluir_inativos: mostrarInativos }),
    [buscaAtrasada, mostrarInativos],
  )

  function aoSalvar(produto) {
    setModal(null)
    setAviso({ tipo: 'sucesso', texto: `Produto "${produto.nome}" salvo.` })
    recarregar()
  }

  async function desativar(produto) {
    try {
      await desativarProduto(produto.id)
      setAviso({ tipo: 'sucesso', texto: `Produto "${produto.nome}" desativado.` })
      recarregar()
    } catch (falha) {
      setAviso({ tipo: 'erro', texto: mensagemDeErro(falha) })
    }
    setModal(null)
  }

  async function reativar(produto) {
    try {
      await atualizarProduto(produto.id, { ativo: true })
      setAviso({ tipo: 'sucesso', texto: `Produto "${produto.nome}" reativado.` })
      recarregar()
    } catch (falha) {
      setAviso({ tipo: 'erro', texto: mensagemDeErro(falha) })
    }
  }

  return (
    <section>
      <div className="pagina-cabecalho">
        <h1 className="titulo-pagina">Produtos</h1>
        <button
          type="button"
          className="btn btn--primario"
          onClick={() => setModal({ tipo: 'form', produto: null })}
        >
          + Novo produto
        </button>
      </div>

      <div className="barra-filtros">
        <input
          type="search"
          className="campo-busca"
          placeholder="Buscar por nome ou código"
          value={busca}
          onChange={(e) => setBusca(e.target.value)}
          aria-label="Buscar produtos"
        />
        <label className="caixa-selecao">
          <input
            type="checkbox"
            checked={mostrarInativos}
            onChange={(e) => setMostrarInativos(e.target.checked)}
          />
          Mostrar inativos
        </label>
      </div>

      {aviso && (
        <div className={`alerta alerta--${aviso.tipo} alerta--fechavel`} role="status">
          <span>{aviso.texto}</span>
          <button type="button" className="btn btn--fantasma btn--icone" onClick={() => setAviso(null)} aria-label="Fechar aviso">
            ✕
          </button>
        </div>
      )}
      {erro && <div className="alerta alerta--erro">{erro}</div>}

      <div className={`cartao cartao--tabela${carregando ? ' atualizando' : ''}`}>
        {produtos === undefined ? (
          <p className="tabela-vazia">Carregando produtos...</p>
        ) : produtos.length === 0 ? (
          <p className="tabela-vazia">Nenhum produto encontrado.</p>
        ) : (
          <table className="tabela">
            <thead>
              <tr>
                <th>Produto</th>
                <th>Código de barras</th>
                <th>Categoria</th>
                <th className="col-numero">Preço</th>
                <th className="col-numero">Estoque</th>
                <th>Situação</th>
                <th className="col-acoes-texto">
                  <span className="sr-only">Ações</span>
                </th>
              </tr>
            </thead>
            <tbody>
              {produtos.map((produto) => (
                <tr key={produto.id} className={produto.ativo ? '' : 'linha--inativa'}>
                  <td>
                    <div className="celula-produto">
                      <ImagemProduto nome={produto.nome} url={produto.imagem_url} tamanho={40} />
                      <span className="celula-destaque">{produto.nome}</span>
                    </div>
                  </td>
                  <td className="celula-codigo">{produto.codigo_barras}</td>
                  <td>
                    {produto.categoria ? (
                      produto.categoria.nome
                    ) : (
                      <span className="texto-suave">Sem categoria</span>
                    )}
                  </td>
                  <td className="col-numero">{formatarReais(paraCentavos(produto.preco))}</td>
                  <td className="col-numero">
                    {produto.quantidade_estoque}
                    {produto.ativo && produto.quantidade_estoque <= ESTOQUE_BAIXO && (
                      <span className="badge badge--aviso">baixo</span>
                    )}
                  </td>
                  <td>
                    <span className={`badge ${produto.ativo ? 'badge--sucesso' : 'badge--neutro'}`}>
                      {produto.ativo ? 'ativo' : 'inativo'}
                    </span>
                  </td>
                  <td className="col-acoes-texto">
                    <button
                      type="button"
                      className="btn btn--fantasma"
                      onClick={() => setModal({ tipo: 'form', produto })}
                    >
                      Editar
                    </button>
                    {produto.ativo ? (
                      <button
                        type="button"
                        className="btn btn--perigo"
                        onClick={() => setModal({ tipo: 'desativar', produto })}
                      >
                        Desativar
                      </button>
                    ) : (
                      <button
                        type="button"
                        className="btn btn--secundario"
                        onClick={() => reativar(produto)}
                      >
                        Reativar
                      </button>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      {modal?.tipo === 'form' && (
        <ModalProduto produto={modal.produto} aoSalvar={aoSalvar} aoFechar={() => setModal(null)} />
      )}

      {modal?.tipo === 'desativar' && (
        <Modal titulo="Desativar produto?" aoFechar={() => setModal(null)} largura="pequena">
          <p>
            <strong>{modal.produto.nome}</strong> deixará de aparecer no caixa. As vendas antigas
            continuam intactas, e você pode reativá-lo depois.
          </p>
          <div className="botoes-lado-a-lado">
            <button type="button" className="btn btn--secundario" onClick={() => setModal(null)}>
              Voltar
            </button>
            <button
              type="button"
              className="btn btn--perigo"
              onClick={() => desativar(modal.produto)}
              autoFocus
            >
              Desativar
            </button>
          </div>
        </Modal>
      )}
    </section>
  )
}
