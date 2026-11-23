import { useState } from 'react'

import { cancelarVenda } from '../../api/vendas.js'
import Modal from '../../components/Modal.jsx'
import { formatarDataHora } from '../../utils/datas.js'
import { formatarReais, paraCentavos } from '../../utils/dinheiro.js'
import { mensagemDeErro } from '../../utils/erros.js'
import { rotuloDaForma } from '../caixa/pagamento.js'

const reais = (valor) => formatarReais(paraCentavos(valor))

/** Detalhes de uma venda, com a opção de cancelar (confirmação em duas etapas). */
export default function ModalDetalheVenda({ venda, aoCancelar, aoFechar }) {
  const [confirmando, setConfirmando] = useState(false)
  const [enviando, setEnviando] = useState(false)
  const [erro, setErro] = useState('')
  const cancelada = venda.status === 'cancelada'

  async function cancelar() {
    setEnviando(true)
    setErro('')
    try {
      aoCancelar(await cancelarVenda(venda.id))
      setConfirmando(false)
    } catch (falha) {
      setErro(mensagemDeErro(falha))
      setConfirmando(false)
    } finally {
      setEnviando(false)
    }
  }

  return (
    <Modal titulo={`Venda nº ${venda.id}`} aoFechar={enviando ? undefined : aoFechar} largura="grande">
      <div className="detalhe-venda__meta">
        <span>{formatarDataHora(venda.data_hora)}</span>
        <span>Operador: {venda.usuario.nome}</span>
        <span>Caixa nº {venda.sessao_caixa_id}</span>
        <span className={`badge ${cancelada ? 'badge--perigo' : 'badge--sucesso'}`}>
          {venda.status}
        </span>
      </div>

      {erro && (
        <div className="alerta alerta--erro" role="alert">
          {erro}
        </div>
      )}

      <div className="tabela-rolavel">
        <table className="tabela">
          <thead>
            <tr>
              <th>Produto</th>
              <th className="col-numero">Qtd.</th>
              <th className="col-numero">Unitário</th>
              <th className="col-numero">Subtotal</th>
            </tr>
          </thead>
          <tbody>
            {venda.itens.map((item) => (
              <tr key={item.id}>
                <td>{item.produto.nome}</td>
                <td className="col-numero">{item.quantidade}</td>
                <td className="col-numero">{reais(item.preco_unitario)}</td>
                <td className="col-numero">{reais(item.subtotal)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="detalhe-venda__rodape">
        <div>
          <h3 className="subtitulo">Pagamentos</h3>
          <ul className="lista-simples">
            {venda.pagamentos.map((p) => (
              <li key={p.forma}>
                <span>{rotuloDaForma(p.forma)}</span>
                <span>
                  {reais(p.valor)}
                  {paraCentavos(p.troco) > 0 && (
                    <span className="texto-suave"> (troco {reais(p.troco)})</span>
                  )}
                </span>
              </li>
            ))}
          </ul>
        </div>

        <dl className="resumo-valores">
          <div>
            <dt>Subtotal</dt>
            <dd>{reais(venda.subtotal)}</dd>
          </div>
          {paraCentavos(venda.desconto) > 0 && (
            <div>
              <dt>Desconto</dt>
              <dd>− {reais(venda.desconto)}</dd>
            </div>
          )}
          <div className="resumo-valores__destaque">
            <dt>Total</dt>
            <dd>{reais(venda.total)}</dd>
          </div>
          <div>
            <dt>Troco</dt>
            <dd>{reais(venda.troco)}</dd>
          </div>
        </dl>
      </div>

      {!cancelada && (
        <div className="detalhe-venda__acoes">
          {confirmando ? (
            <div className="confirmacao">
              <p>
                Cancelar esta venda? Os itens voltam para o estoque e ela deixa de contar nos
                relatórios e no fechamento do caixa.
              </p>
              <div className="botoes-lado-a-lado">
                <button
                  type="button"
                  className="btn btn--secundario"
                  onClick={() => setConfirmando(false)}
                  disabled={enviando}
                >
                  Voltar
                </button>
                <button
                  type="button"
                  className="btn btn--perigo"
                  onClick={cancelar}
                  disabled={enviando}
                  autoFocus
                >
                  {enviando ? 'Cancelando...' : 'Confirmar cancelamento'}
                </button>
              </div>
            </div>
          ) : (
            <button type="button" className="btn btn--secundario texto-perigo" onClick={() => setConfirmando(true)}>
              Cancelar venda
            </button>
          )}
        </div>
      )}
    </Modal>
  )
}
