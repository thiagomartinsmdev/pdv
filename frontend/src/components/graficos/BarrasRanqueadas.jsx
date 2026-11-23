import { formatarReais } from '../../utils/dinheiro.js'

const porcentagem = new Intl.NumberFormat('pt-BR', { style: 'percent', maximumFractionDigits: 1 })

/**
 * Lista de barras horizontais, da maior para a menor: nome, barra e valor em cada linha.
 *
 * Usada no lugar de um gráfico de pizza: comparar comprimentos de barras alinhadas na
 * mesma base é bem mais preciso do que comparar ângulos de fatias.
 *
 * itens: [{ chave, rotulo, centavos }]
 */
export default function BarrasRanqueadas({ itens, titulo }) {
  const ordenados = [...itens].sort((a, b) => b.centavos - a.centavos)
  const maximo = Math.max(1, ...ordenados.map((i) => i.centavos))
  const total = ordenados.reduce((soma, i) => soma + i.centavos, 0)

  return (
    <ul className="barras-ranqueadas" aria-label={titulo}>
      {ordenados.map((item) => {
        const fracao = total > 0 ? item.centavos / total : 0
        return (
          <li key={item.chave} title={`${item.rotulo}: ${formatarReais(item.centavos)}`}>
            <span className="barras-ranqueadas__nome">{item.rotulo}</span>
            <span className="barras-ranqueadas__trilho" aria-hidden="true">
              {item.centavos > 0 && (
                <span
                  className="barras-ranqueadas__barra"
                  style={{ width: `${(item.centavos / maximo) * 100}%` }}
                />
              )}
            </span>
            <span className="barras-ranqueadas__valor">
              {formatarReais(item.centavos)}
              <small>{porcentagem.format(fracao)}</small>
            </span>
          </li>
        )
      })}
    </ul>
  )
}
