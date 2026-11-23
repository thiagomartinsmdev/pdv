import { useState } from 'react'
import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts'

import { formatarData } from '../../utils/datas.js'
import { formatarReais, paraCentavos } from '../../utils/dinheiro.js'
import { CORES_GRAFICO } from './cores.js'

const compacto = new Intl.NumberFormat('pt-BR', {
  style: 'currency',
  currency: 'BRL',
  notation: 'compact',
  maximumFractionDigits: 1,
})
const inteiro = new Intl.NumberFormat('pt-BR', {
  style: 'currency',
  currency: 'BRL',
  maximumFractionDigits: 0,
})

/**
 * Colunas com o total vendido em cada dia do período.
 * Uma série só, então não há legenda: o título do cartão diz o que está no gráfico.
 * Os valores exatos aparecem no tooltip e na visão em tabela.
 */
export default function GraficoVendasPorDia({ dias }) {
  const [verTabela, setVerTabela] = useState(false)

  // O Recharts trabalha com números; os centavos ficam guardados para o tooltip.
  const dados = dias.map((dia) => {
    const centavos = paraCentavos(dia.total)
    return { ...dia, centavos, valor: centavos / 100, rotulo: formatarData(dia.data) }
  })
  const maximo = Math.max(0, ...dados.map((d) => d.valor))
  // Eixo: valores inteiros abaixo de 10 mil; acima disso, formato compacto ("R$ 12 mil").
  const formatarEixo = (v) => (maximo < 10_000 ? inteiro.format(v) : compacto.format(v))
  const totalDoPeriodo = dados.reduce((soma, d) => soma + d.centavos, 0)

  return (
    <div className="grafico">
      <div className="grafico__cabecalho">
        <div>
          <h2 className="subtitulo">Vendas por dia</h2>
          <p className="texto-suave texto-pequeno">Total vendido em cada dia (vendas concluídas)</p>
        </div>
        <button type="button" className="btn btn--fantasma" onClick={() => setVerTabela((v) => !v)}>
          {verTabela ? 'Ver gráfico' : 'Ver tabela'}
        </button>
      </div>

      {verTabela ? (
        <div className="tabela-rolavel tabela-rolavel--limitada">
          <table className="tabela">
            <thead>
              <tr>
                <th>Dia</th>
                <th className="col-numero">Vendas</th>
                <th className="col-numero">Total</th>
              </tr>
            </thead>
            <tbody>
              {dados.map((d) => (
                <tr key={d.data}>
                  <td>{formatarData(d.data, { ano: true })}</td>
                  <td className="col-numero">{d.quantidade_vendas}</td>
                  <td className="col-numero">{formatarReais(d.centavos)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : (
        <div
          className="grafico__area"
          role="img"
          aria-label={`Gráfico de colunas: vendas por dia, ${dados.length} dias, total de ${formatarReais(totalDoPeriodo)}. Use "Ver tabela" para os valores.`}
        >
          <ResponsiveContainer width="100%" height={280}>
            <BarChart data={dados} margin={{ top: 8, right: 8, bottom: 0, left: 0 }} barCategoryGap="20%">
              {/* Grade só horizontal, fina e sólida: guia o olho sem competir com os dados. */}
              <CartesianGrid vertical={false} stroke={CORES_GRAFICO.grade} />
              <XAxis
                dataKey="rotulo"
                tickLine={false}
                axisLine={{ stroke: CORES_GRAFICO.eixo }}
                tick={{ fill: CORES_GRAFICO.textoEixo, fontSize: 12 }}
                interval="preserveStartEnd"
                minTickGap={12}
              />
              <YAxis
                tickFormatter={formatarEixo}
                tickLine={false}
                axisLine={false}
                tick={{ fill: CORES_GRAFICO.textoEixo, fontSize: 12 }}
                width={76}
                allowDecimals={false}
              />
              {/* O dia inteiro (a faixa toda) é a área de hover, não só a coluna. */}
              <Tooltip
                cursor={{ fill: 'rgb(42 120 214 / 8%)' }}
                content={<TooltipDia />}
                isAnimationActive={false}
              />
              <Bar
                dataKey="valor"
                fill={CORES_GRAFICO.serie}
                radius={[4, 4, 0, 0]} // ponta arredondada, base reta
                maxBarSize={24}
                activeBar={{ fill: CORES_GRAFICO.serieDestaque }}
                isAnimationActive={false}
              />
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}
    </div>
  )
}

/** Tooltip: o valor em destaque primeiro, o dia e a quantidade depois. */
function TooltipDia({ active, payload }) {
  if (!active || !payload?.length) return null
  const dia = payload[0].payload
  return (
    <div className="grafico__tooltip">
      <strong>{formatarReais(dia.centavos)}</strong>
      <span>{formatarData(dia.data, { ano: true })}</span>
      <span>{dia.quantidade_vendas} venda(s)</span>
    </div>
  )
}
