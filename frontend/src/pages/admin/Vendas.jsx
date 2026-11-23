import { useState } from 'react'

import { listarVendas } from '../../api/vendas.js'
import FiltroPeriodo from '../../components/FiltroPeriodo.jsx'
import { useConsulta } from '../../hooks/useConsulta.js'
import { formatarDataHora } from '../../utils/datas.js'
import { formatarReais, paraCentavos } from '../../utils/dinheiro.js'
import { periodoDoPreset } from '../../utils/periodos.js'
import { rotuloDaForma } from '../caixa/pagamento.js'
import ModalDetalheVenda from './ModalDetalheVenda.jsx'
import './admin.css'

const POR_PAGINA = 50
const LIMITE_MAXIMO = 500 // o máximo que a API devolve por consulta

export default function Vendas() {
  const [periodo, setPeriodo] = useState(() => periodoDoPreset('hoje'))
  const [status, setStatus] = useState('')
  const [limite, setLimite] = useState(POR_PAGINA)
  const [selecionada, setSelecionada] = useState(null)

  const { dados: vendas, carregando, erro, recarregar } = useConsulta(
    () => listarVendas({ ...periodo, status: status || undefined, limite }),
    [periodo, status, limite],
  )

  // Mudou o filtro: volta para a primeira página.
  function mudarPeriodo(novo) {
    setPeriodo(novo)
    setLimite(POR_PAGINA)
  }

  function mudarStatus(novo) {
    setStatus(novo)
    setLimite(POR_PAGINA)
  }

  function aoCancelar(vendaAtualizada) {
    setSelecionada(vendaAtualizada) // o modal passa a mostrar "cancelada"
    recarregar()
  }

  const podeCarregarMais = vendas?.length === limite && limite < LIMITE_MAXIMO

  return (
    <section>
      <h1 className="titulo-pagina">Histórico de vendas</h1>

      <div className="barra-filtros">
        <FiltroPeriodo periodo={periodo} aoMudar={mudarPeriodo} />
        <label className="campo-inline">
          <span>Status</span>
          <select value={status} onChange={(e) => mudarStatus(e.target.value)}>
            <option value="">Todos</option>
            <option value="concluida">Concluídas</option>
            <option value="cancelada">Canceladas</option>
          </select>
        </label>
      </div>

      {erro && <div className="alerta alerta--erro">{erro}</div>}

      <div className={`cartao cartao--tabela${carregando ? ' atualizando' : ''}`}>
        {vendas === undefined ? (
          <p className="tabela-vazia">Carregando vendas...</p>
        ) : vendas.length === 0 ? (
          <p className="tabela-vazia">Nenhuma venda no período.</p>
        ) : (
          <table className="tabela tabela--clicavel">
            <thead>
              <tr>
                <th>Nº</th>
                <th>Data e hora</th>
                <th>Operador</th>
                <th className="col-numero">Itens</th>
                <th>Pagamento</th>
                <th className="col-numero">Total</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              {vendas.map((venda) => (
                <tr
                  key={venda.id}
                  className={venda.status === 'cancelada' ? 'linha--inativa' : ''}
                  onClick={() => setSelecionada(venda)}
                >
                  <td>
                    {/* Botão real dentro da linha: permite abrir pelo teclado (Tab + Enter). */}
                    <button type="button" className="link-botao" onClick={() => setSelecionada(venda)}>
                      {venda.id}
                    </button>
                  </td>
                  <td>{formatarDataHora(venda.data_hora)}</td>
                  <td>{venda.usuario.nome}</td>
                  <td className="col-numero">
                    {venda.itens.reduce((soma, item) => soma + item.quantidade, 0)}
                  </td>
                  <td>{venda.pagamentos.map((p) => rotuloDaForma(p.forma)).join(' + ')}</td>
                  <td className="col-numero celula-destaque">
                    {formatarReais(paraCentavos(venda.total))}
                  </td>
                  <td>
                    <span
                      className={`badge ${venda.status === 'cancelada' ? 'badge--perigo' : 'badge--sucesso'}`}
                    >
                      {venda.status}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      {vendas && vendas.length > 0 && (
        <div className="paginacao">
          <span className="texto-suave">Mostrando {vendas.length} venda(s)</span>
          {podeCarregarMais && (
            <button
              type="button"
              className="btn btn--secundario"
              onClick={() => setLimite((l) => Math.min(l + POR_PAGINA, LIMITE_MAXIMO))}
              disabled={carregando}
            >
              Carregar mais
            </button>
          )}
        </div>
      )}

      {selecionada && (
        <ModalDetalheVenda
          // "key" recria o modal ao trocar de venda, zerando o estado interno dele.
          key={selecionada.id}
          venda={selecionada}
          aoCancelar={aoCancelar}
          aoFechar={() => setSelecionada(null)}
        />
      )}
    </section>
  )
}
