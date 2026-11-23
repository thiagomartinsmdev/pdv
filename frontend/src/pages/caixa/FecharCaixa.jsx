import { useState } from 'react'

import { fecharCaixa } from '../../api/caixa.js'
import CampoDinheiro from '../../components/CampoDinheiro.jsx'
import { centavosParaApi, lerValorDigitado } from '../../utils/dinheiro.js'
import { formatarDataHora } from '../../utils/datas.js'
import { mensagemDeErro } from '../../utils/erros.js'

/**
 * Fechamento com conferência "às cegas": o operador conta a gaveta e informa o valor
 * SEM ver quanto o sistema espera. Só depois de confirmar ele vê o esperado e a
 * diferença. Isso evita que a contagem seja "ajustada" para bater com o sistema.
 */
export default function FecharCaixa({ sessao, aoVoltar, aoFechar }) {
  const [valor, setValor] = useState('')
  const [erro, setErro] = useState('')
  const [enviando, setEnviando] = useState(false)

  async function aoEnviar(evento) {
    evento.preventDefault()
    const centavos = lerValorDigitado(valor)
    if (centavos === null) {
      setErro('Informe o valor em dinheiro contado na gaveta.')
      return
    }
    setEnviando(true)
    setErro('')
    try {
      aoFechar(await fecharCaixa(centavosParaApi(centavos)))
    } catch (falha) {
      setErro(mensagemDeErro(falha))
      setEnviando(false)
    }
  }

  return (
    <div className="caixa-centralizado">
      <form className="cartao cartao--estreito formulario" onSubmit={aoEnviar}>
        <div>
          <h1 className="titulo-cartao">Fechar caixa</h1>
          <p className="texto-suave">
            Caixa aberto em {formatarDataHora(sessao.aberto_em)} ·{' '}
            {sessao.resumo.quantidade_vendas} venda(s).
          </p>
        </div>

        <p>
          Conte todo o <strong>dinheiro em espécie</strong> da gaveta (incluindo o fundo de troco)
          e informe o valor. PIX e cartões não entram nesta contagem.
        </p>

        {erro && <div className="alerta alerta--erro">{erro}</div>}

        <CampoDinheiro
          rotulo="Dinheiro contado na gaveta"
          valor={valor}
          aoMudar={setValor}
          placeholder="0,00"
          autoFocus
        />

        <div className="botoes-lado-a-lado">
          <button type="button" className="btn btn--secundario" onClick={aoVoltar}>
            Voltar ao caixa
          </button>
          <button type="submit" className="btn btn--primario" disabled={enviando}>
            {enviando ? 'Fechando...' : 'Confirmar fechamento'}
          </button>
        </div>
      </form>
    </div>
  )
}
