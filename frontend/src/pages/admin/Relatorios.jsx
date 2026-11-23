import { useState } from 'react'

import { relatorioVendas } from '../../api/relatorios.js'
import FiltroPeriodo from '../../components/FiltroPeriodo.jsx'
import BarrasRanqueadas from '../../components/graficos/BarrasRanqueadas.jsx'
import GraficoVendasPorDia from '../../components/graficos/GraficoVendasPorDia.jsx'
import { useConsulta } from '../../hooks/useConsulta.js'
import { formatarReais, paraCentavos } from '../../utils/dinheiro.js'
import { periodoDoPreset } from '../../utils/periodos.js'
import { FORMAS_PAGAMENTO } from '../caixa/pagamento.js'
import './admin.css'

const numero = new Intl.NumberFormat('pt-BR')

export default function Relatorios() {
  const [periodo, setPeriodo] = useState(() => periodoDoPreset('7d'))
  const { dados: relatorio, carregando, erro } = useConsulta(
    () => relatorioVendas({ ...periodo, limite_produtos: 10 }),
    [periodo],
  )

  return (
    <section>
      <h1 className="titulo-pagina">Relatórios</h1>

      {/* Filtro em uma linha só, acima de tudo: vale para todos os números da página. */}
      <div className="barra-filtros">
        <FiltroPeriodo periodo={periodo} aoMudar={setPeriodo} />
      </div>

      {erro && <div className="alerta alerta--erro">{erro}</div>}

      {relatorio === undefined ? (
        !erro && <p className="texto-suave">Carregando relatório...</p>
      ) : (
        // Ao trocar o período, os dados antigos ficam esmaecidos até os novos chegarem.
        <div className={`relatorio${carregando ? ' atualizando' : ''}`}>
          <Indicadores relatorio={relatorio} />

          <div className="cartao">
            <GraficoVendasPorDia dias={relatorio.vendas_por_dia} />
          </div>

          <div className="relatorio__colunas">
            <div className="cartao">
              <h2 className="subtitulo">Recebido por forma de pagamento</h2>
              <p className="texto-suave texto-pequeno espaco-abaixo">
                Em dinheiro, já descontado o troco
              </p>
              <BarrasRanqueadas
                titulo="Recebido por forma de pagamento"
                itens={FORMAS_PAGAMENTO.map((forma) => ({
                  chave: forma.valor,
                  rotulo: forma.rotulo,
                  centavos: paraCentavos(relatorio.total_por_forma[forma.valor]),
                }))}
              />
            </div>

            <div className="cartao">
              <h2 className="subtitulo espaco-abaixo">Produtos mais vendidos</h2>
              <ProdutosMaisVendidos produtos={relatorio.produtos_mais_vendidos} />
            </div>
          </div>
        </div>
      )}
    </section>
  )
}

function Indicadores({ relatorio }) {
  return (
    <div className="indicadores">
      <div className="indicador indicador--principal">
        <span className="indicador__rotulo">Total vendido</span>
        <strong className="indicador__valor">
          {formatarReais(paraCentavos(relatorio.total_vendido))}
        </strong>
      </div>
      <div className="indicador">
        <span className="indicador__rotulo">Vendas</span>
        <strong className="indicador__valor">{numero.format(relatorio.quantidade_vendas)}</strong>
      </div>
      <div className="indicador">
        <span className="indicador__rotulo">Ticket médio</span>
        <strong className="indicador__valor">
          {formatarReais(paraCentavos(relatorio.ticket_medio))}
        </strong>
      </div>
      <div className="indicador">
        <span className="indicador__rotulo">Vendas canceladas</span>
        <strong className="indicador__valor">
          {numero.format(relatorio.quantidade_canceladas)}
        </strong>
      </div>
    </div>
  )
}

function ProdutosMaisVendidos({ produtos }) {
  if (produtos.length === 0) {
    return <p className="texto-suave">Nenhuma venda no período.</p>
  }
  const maximo = Math.max(...produtos.map((p) => p.quantidade))

  return (
    <div className="tabela-rolavel">
      <table className="tabela tabela--ranking">
        <thead>
          <tr>
            <th className="col-posicao">#</th>
            <th>Produto</th>
            <th className="col-numero">Qtd.</th>
            <th className="col-numero">Total</th>
          </tr>
        </thead>
        <tbody>
          {produtos.map((produto, indice) => (
            <tr key={produto.produto_id}>
              <td className="col-posicao">{indice + 1}</td>
              <td>
                <div>{produto.nome}</div>
                {/* Barra fina de proporção: a tabela já traz os números ao lado. */}
                <span className="barra-fina" aria-hidden="true">
                  <span style={{ width: `${(produto.quantidade / maximo) * 100}%` }} />
                </span>
              </td>
              <td className="col-numero">{numero.format(produto.quantidade)}</td>
              <td className="col-numero">{formatarReais(paraCentavos(produto.total))}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
