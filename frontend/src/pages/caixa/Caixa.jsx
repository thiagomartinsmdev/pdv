import { useEffect, useState } from 'react'

import { buscarCaixaAtual } from '../../api/caixa.js'
import Carregando from '../../components/Carregando.jsx'
import { mensagemDeErro } from '../../utils/erros.js'
import AbrirCaixa from './AbrirCaixa.jsx'
import FecharCaixa from './FecharCaixa.jsx'
import PontoDeVenda from './PontoDeVenda.jsx'
import ResultadoFechamento from './ResultadoFechamento.jsx'
import './caixa.css'

/** Busca o caixa atual e devolve { sessao, erro } (nunca lança exceção). */
async function obterCaixa() {
  try {
    return { sessao: await buscarCaixaAtual(), erro: '' }
  } catch (falha) {
    return { sessao: null, erro: mensagemDeErro(falha) }
  }
}

/**
 * Decide qual tela do caixa mostrar:
 *   sem caixa aberto      -> AbrirCaixa
 *   caixa aberto          -> PontoDeVenda (ou FecharCaixa, se pedido)
 *   acabou de fechar      -> ResultadoFechamento
 */
export default function Caixa() {
  const [sessao, setSessao] = useState(null)
  const [carregando, setCarregando] = useState(true)
  const [erro, setErro] = useState('')
  const [fechando, setFechando] = useState(false)
  const [fechamento, setFechamento] = useState(null)

  function aplicar(resultado) {
    setSessao(resultado.sessao)
    setErro(resultado.erro)
    setCarregando(false)
  }

  // Carga inicial, ao abrir a tela. O estado só muda quando a resposta chega (no .then).
  useEffect(() => {
    let ativo = true
    obterCaixa().then((resultado) => {
      // Se o usuário saiu da tela antes da resposta, ignoramos o resultado.
      if (ativo) {
        setSessao(resultado.sessao)
        setErro(resultado.erro)
        setCarregando(false)
      }
    })
    // Limpeza: roda quando o componente sai da tela.
    return () => {
      ativo = false
    }
  }, [])

  // Recarga a pedido do usuário: mostra o "carregando" e busca de novo.
  async function recarregar() {
    setCarregando(true)
    aplicar(await obterCaixa())
  }

  async function irParaFechamento() {
    await recarregar() // atualiza o resumo com as vendas feitas até agora
    setFechando(true)
  }

  if (carregando) {
    return <Carregando texto="Carregando caixa..." />
  }

  if (erro) {
    return (
      <div className="caixa-centralizado">
        <div className="cartao cartao--estreito">
          <div className="alerta alerta--erro">{erro}</div>
          <button type="button" className="btn btn--primario" onClick={recarregar}>
            Tentar novamente
          </button>
        </div>
      </div>
    )
  }

  if (fechamento) {
    return <ResultadoFechamento caixa={fechamento} aoContinuar={() => setFechamento(null)} />
  }

  if (!sessao) {
    return <AbrirCaixa aoAbrir={setSessao} />
  }

  if (fechando) {
    return (
      <FecharCaixa
        sessao={sessao}
        aoVoltar={() => setFechando(false)}
        aoFechar={(caixaFechado) => {
          setFechamento(caixaFechado)
          setSessao(null)
          setFechando(false)
        }}
      />
    )
  }

  return <PontoDeVenda sessao={sessao} aoFecharCaixa={irParaFechamento} />
}
