import { useState } from 'react'

import { abrirCaixa } from '../../api/caixa.js'
import CampoDinheiro from '../../components/CampoDinheiro.jsx'
import { useAuth } from '../../hooks/useAuth.js'
import { centavosParaApi, lerValorDigitado } from '../../utils/dinheiro.js'
import { mensagemDeErro } from '../../utils/erros.js'

/** Tela exibida quando o usuário não tem caixa aberto. */
export default function AbrirCaixa({ aoAbrir }) {
  const { usuario } = useAuth()
  const [valor, setValor] = useState('')
  const [erro, setErro] = useState('')
  const [enviando, setEnviando] = useState(false)

  async function aoEnviar(evento) {
    evento.preventDefault()
    const centavos = lerValorDigitado(valor)
    if (centavos === null) {
      setErro('Informe o valor em dinheiro deixado na gaveta (pode ser 0).')
      return
    }
    setEnviando(true)
    setErro('')
    try {
      aoAbrir(await abrirCaixa(centavosParaApi(centavos)))
    } catch (falha) {
      setErro(mensagemDeErro(falha))
      setEnviando(false)
    }
  }

  return (
    <div className="caixa-centralizado">
      <form className="cartao cartao--estreito formulario" onSubmit={aoEnviar}>
        <div>
          <h1 className="titulo-cartao">Abrir caixa</h1>
          <p className="texto-suave">
            Olá, {usuario.nome}. Conte o dinheiro da gaveta (fundo de troco) e informe o valor.
          </p>
        </div>

        {erro && <div className="alerta alerta--erro">{erro}</div>}

        <CampoDinheiro
          rotulo="Valor de abertura"
          valor={valor}
          aoMudar={setValor}
          placeholder="0,00"
          autoFocus
        />

        <button type="submit" className="btn btn--primario btn--bloco" disabled={enviando}>
          {enviando ? 'Abrindo...' : 'Abrir caixa'}
        </button>
      </form>
    </div>
  )
}
