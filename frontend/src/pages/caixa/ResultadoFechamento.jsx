import { formatarDataHora } from '../../utils/datas.js'
import { formatarReais, paraCentavos } from '../../utils/dinheiro.js'
import { FORMAS_PAGAMENTO } from './pagamento.js'

/** Resumo exibido depois do fechamento: esperado x informado e a diferença. */
export default function ResultadoFechamento({ caixa, aoContinuar }) {
  const { resumo } = caixa
  const diferenca = paraCentavos(caixa.diferenca)

  let situacao = { classe: 'ok', texto: 'Caixa conferido: os valores batem.' }
  if (diferenca > 0) {
    situacao = { classe: 'sobra', texto: `Sobra de ${formatarReais(diferenca)} no caixa.` }
  } else if (diferenca < 0) {
    situacao = { classe: 'falta', texto: `Falta de ${formatarReais(-diferenca)} no caixa.` }
  }

  return (
    <div className="caixa-centralizado">
      <div className="cartao cartao--estreito">
        <h1 className="titulo-cartao">Caixa fechado</h1>
        <p className="texto-suave">
          {formatarDataHora(caixa.aberto_em)} até {formatarDataHora(caixa.fechado_em)}
        </p>

        <div className={`fechamento-situacao fechamento-situacao--${situacao.classe}`}>
          {situacao.texto}
        </div>

        <table className="tabela-resumo">
          <tbody>
            <tr>
              <th>Vendas concluídas</th>
              <td>{resumo.quantidade_vendas}</td>
            </tr>
            <tr>
              <th>Total vendido</th>
              <td>{formatarReais(paraCentavos(resumo.total_vendido))}</td>
            </tr>
            {FORMAS_PAGAMENTO.map((forma) => (
              <tr key={forma.valor} className="tabela-resumo__detalhe">
                <th>{forma.rotulo}</th>
                <td>{formatarReais(paraCentavos(resumo.total_por_forma[forma.valor]))}</td>
              </tr>
            ))}
            <tr className="tabela-resumo__separador">
              <th>Fundo de troco (abertura)</th>
              <td>{formatarReais(paraCentavos(caixa.valor_abertura))}</td>
            </tr>
            <tr>
              <th>Dinheiro esperado na gaveta</th>
              <td>{formatarReais(paraCentavos(resumo.valor_esperado_dinheiro))}</td>
            </tr>
            <tr>
              <th>Dinheiro contado</th>
              <td>{formatarReais(paraCentavos(caixa.valor_informado_fechamento))}</td>
            </tr>
            <tr className="tabela-resumo__total">
              <th>Diferença</th>
              <td>{formatarReais(diferenca)}</td>
            </tr>
          </tbody>
        </table>

        <button type="button" className="btn btn--primario btn--bloco" onClick={aoContinuar}>
          Abrir novo caixa
        </button>
      </div>
    </div>
  )
}
