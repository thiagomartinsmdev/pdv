import { useState } from 'react'

import {
  atualizarCategoria,
  desativarCategoria,
  listarCategorias,
} from '../../api/categorias.js'
import Modal from '../../components/Modal.jsx'
import { useConsulta } from '../../hooks/useConsulta.js'
import { mensagemDeErro } from '../../utils/erros.js'
import ModalCategoria from './ModalCategoria.jsx'
import './admin.css'

/** Categorias de produto: viram as abas da grade do caixa, na ordem definida aqui. */
export default function Categorias() {
  const [mostrarInativas, setMostrarInativas] = useState(false)
  const [modal, setModal] = useState(null) // { tipo: 'form' | 'desativar', categoria }
  const [aviso, setAviso] = useState(null) // { tipo: 'sucesso' | 'erro', texto }

  const { dados: categorias, carregando, erro, recarregar } = useConsulta(
    () => listarCategorias({ incluir_inativas: mostrarInativas }),
    [mostrarInativas],
  )

  // Próxima ordem sugerida: 10 depois da maior, para sobrar espaço entre as abas.
  const sugestaoOrdem = (categorias ?? []).reduce((maior, c) => Math.max(maior, c.ordem), 0) + 10

  function aoSalvar(categoria) {
    setModal(null)
    setAviso({ tipo: 'sucesso', texto: `Categoria "${categoria.nome}" salva.` })
    recarregar()
  }

  async function executar(acao, textoSucesso) {
    try {
      await acao()
      setAviso({ tipo: 'sucesso', texto: textoSucesso })
      recarregar()
    } catch (falha) {
      setAviso({ tipo: 'erro', texto: mensagemDeErro(falha) })
    }
    setModal(null)
  }

  return (
    <section>
      <div className="pagina-cabecalho">
        <div>
          <h1 className="titulo-pagina">Categorias</h1>
          <p className="texto-suave subtitulo-pagina">
            Cada categoria ativa vira uma aba na grade de produtos do caixa.
          </p>
        </div>
        <button
          type="button"
          className="btn btn--primario"
          onClick={() => setModal({ tipo: 'form', categoria: null })}
        >
          + Nova categoria
        </button>
      </div>

      <div className="barra-filtros">
        <label className="caixa-selecao">
          <input
            type="checkbox"
            checked={mostrarInativas}
            onChange={(e) => setMostrarInativas(e.target.checked)}
          />
          Mostrar inativas
        </label>
      </div>

      {aviso && (
        <div className={`alerta alerta--${aviso.tipo} alerta--fechavel`} role="status">
          <span>{aviso.texto}</span>
          <button
            type="button"
            className="btn btn--fantasma btn--icone"
            onClick={() => setAviso(null)}
            aria-label="Fechar aviso"
          >
            ✕
          </button>
        </div>
      )}
      {erro && <div className="alerta alerta--erro">{erro}</div>}

      <div className={`cartao cartao--tabela${carregando ? ' atualizando' : ''}`}>
        {categorias === undefined ? (
          <p className="tabela-vazia">Carregando categorias...</p>
        ) : categorias.length === 0 ? (
          <p className="tabela-vazia">Nenhuma categoria cadastrada.</p>
        ) : (
          <table className="tabela">
            <thead>
              <tr>
                <th className="col-numero col-ordem">Ordem</th>
                <th>Nome</th>
                <th>Situação</th>
                <th className="col-acoes-texto">
                  <span className="sr-only">Ações</span>
                </th>
              </tr>
            </thead>
            <tbody>
              {categorias.map((categoria) => (
                <tr key={categoria.id} className={categoria.ativo ? '' : 'linha--inativa'}>
                  <td className="col-numero col-ordem">{categoria.ordem}</td>
                  <td className="celula-destaque">{categoria.nome}</td>
                  <td>
                    <span className={`badge ${categoria.ativo ? 'badge--sucesso' : 'badge--neutro'}`}>
                      {categoria.ativo ? 'ativa' : 'inativa'}
                    </span>
                  </td>
                  <td className="col-acoes-texto">
                    <button
                      type="button"
                      className="btn btn--fantasma"
                      onClick={() => setModal({ tipo: 'form', categoria })}
                    >
                      Editar
                    </button>
                    {categoria.ativo ? (
                      <button
                        type="button"
                        className="btn btn--perigo"
                        onClick={() => setModal({ tipo: 'desativar', categoria })}
                      >
                        Desativar
                      </button>
                    ) : (
                      <button
                        type="button"
                        className="btn btn--secundario"
                        onClick={() =>
                          executar(
                            () => atualizarCategoria(categoria.id, { ativo: true }),
                            `Categoria "${categoria.nome}" reativada.`,
                          )
                        }
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
        <ModalCategoria
          categoria={modal.categoria}
          sugestaoOrdem={sugestaoOrdem}
          aoSalvar={aoSalvar}
          aoFechar={() => setModal(null)}
        />
      )}

      {modal?.tipo === 'desativar' && (
        <Modal titulo="Desativar categoria?" aoFechar={() => setModal(null)} largura="pequena">
          <p>
            A aba <strong>{modal.categoria.nome}</strong> deixará de aparecer no caixa. Os produtos
            dela continuam à venda e aparecem na aba "Todos". Você pode reativá-la depois.
          </p>
          <div className="botoes-lado-a-lado">
            <button type="button" className="btn btn--secundario" onClick={() => setModal(null)}>
              Voltar
            </button>
            <button
              type="button"
              className="btn btn--perigo"
              onClick={() =>
                executar(
                  () => desativarCategoria(modal.categoria.id),
                  `Categoria "${modal.categoria.nome}" desativada.`,
                )
              }
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
