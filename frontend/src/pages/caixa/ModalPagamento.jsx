import { useRef, useState } from 'react'

import CampoDinheiro from '../../components/CampoDinheiro.jsx'
import Modal from '../../components/Modal.jsx'
import { useAtalhos } from '../../hooks/useAtalhos.js'
import { centavosParaTexto, formatarReais, lerValorDigitado } from '../../utils/dinheiro.js'
import { mensagemDeErro } from '../../utils/erros.js'
import { FORMAS_PAGAMENTO, resumirPagamentos, rotuloDaForma } from './pagamento.js'

/**
 * Modal de pagamento. Permite lançar uma ou mais formas (pagamento misto) e mostra
 * o restante ou o troco em tempo real.
 *
 * Fluxo pelo teclado: digite o valor e Enter (lança o pagamento); com o total coberto,
 * F2 (ou Enter no botão) confirma a venda. Esc volta para a venda.
 *
 * aoConfirmar({ pagamentos, desconto }) recebe valores em centavos e deve devolver
 * uma Promise; se ela falhar, a mensagem de erro aparece aqui no modal.
 */
export default function ModalPagamento({ subtotal, aoConfirmar, aoFechar }) {
  const [pagamentos, setPagamentos] = useState([]) // [{ forma, valor (centavos) }]
  const [forma, setForma] = useState('dinheiro')
  const [valorTexto, setValorTexto] = useState('')
  const [descontoTexto, setDescontoTexto] = useState('')
  const [erro, setErro] = useState('')
  const [enviando, setEnviando] = useState(false)
  const valorRef = useRef(null)
  const confirmarRef = useRef(null)

  // Valores "derivados": calculados a cada renderização a partir do estado.
  // Não precisam de useState próprio, pois sempre dá para recalculá-los.
  const desconto = lerValorDigitado(descontoTexto) ?? 0
  const descontoInvalido = descontoTexto !== '' && lerValorDigitado(descontoTexto) === null
  const total = subtotal - desconto
  const resumo = resumirPagamentos(pagamentos, total)
  const descontoExcessivo = desconto >= subtotal

  function lancarPagamento(evento) {
    evento?.preventDefault()
    // Enter com o campo vazio e o total já coberto = confirmar a venda.
    if (valorTexto === '' && resumo.restante === 0) {
      confirmar()
      return
    }
    // Campo vazio = paga exatamente o que falta.
    const valor = valorTexto === '' ? resumo.restante : lerValorDigitado(valorTexto)
    if (!valor) {
      setErro('Informe um valor maior que zero.')
      return
    }
    setPagamentos((atuais) => [...atuais, { forma, valor }])
    setValorTexto('')
    setErro('')
    // Se agora cobre o total, leva o foco para o botão de confirmar.
    if (resumo.pago + valor >= total) {
      setTimeout(() => confirmarRef.current?.focus(), 0)
    }
  }

  function removerPagamento(indice) {
    setPagamentos((atuais) => atuais.filter((_, i) => i !== indice))
    valorRef.current?.focus()
  }

  async function confirmar() {
    if (!resumo.podeConfirmar || descontoExcessivo || descontoInvalido || enviando) return
    setEnviando(true)
    setErro('')
    try {
      await aoConfirmar({ pagamentos, desconto })
    } catch (falha) {
      setErro(mensagemDeErro(falha))
      setEnviando(false)
    }
  }

  useAtalhos({ F2: confirmar })

  const podeConfirmar = resumo.podeConfirmar && !descontoExcessivo && !descontoInvalido

  return (
    <Modal titulo="Pagamento" aoFechar={enviando ? undefined : aoFechar} largura="grande">
      <div className="pagamento">
        <div className="pagamento__lancamento">
          <div className="pagamento__formas" role="radiogroup" aria-label="Forma de pagamento">
            {FORMAS_PAGAMENTO.map((opcao) => (
              <button
                key={opcao.valor}
                type="button"
                role="radio"
                aria-checked={forma === opcao.valor}
                className={`btn-forma${forma === opcao.valor ? ' btn-forma--ativa' : ''}`}
                onClick={() => {
                  setForma(opcao.valor)
                  valorRef.current?.focus()
                }}
              >
                {opcao.rotulo}
              </button>
            ))}
          </div>

          <form onSubmit={lancarPagamento} className="pagamento__valor">
            <CampoDinheiro
              ref={valorRef}
              rotulo={`Valor em ${rotuloDaForma(forma)}`}
              valor={valorTexto}
              aoMudar={setValorTexto}
              placeholder={centavosParaTexto(resumo.restante)}
              autoFocus
            />
            <button type="submit" className="btn btn--secundario">
              Lançar
            </button>
          </form>

          <CampoDinheiro
            rotulo="Desconto (opcional)"
            valor={descontoTexto}
            aoMudar={setDescontoTexto}
            placeholder="0,00"
          />

          {pagamentos.length > 0 && (
            <ul className="pagamento__lista">
              {pagamentos.map((p, indice) => (
                <li key={indice}>
                  <span>{rotuloDaForma(p.forma)}</span>
                  <strong>{formatarReais(p.valor)}</strong>
                  <button
                    type="button"
                    className="btn btn--fantasma btn--icone"
                    onClick={() => removerPagamento(indice)}
                    aria-label={`Remover pagamento em ${rotuloDaForma(p.forma)}`}
                  >
                    ✕
                  </button>
                </li>
              ))}
            </ul>
          )}
        </div>

        <div className="pagamento__resumo">
          <dl className="resumo-valores">
            <div>
              <dt>Subtotal</dt>
              <dd>{formatarReais(subtotal)}</dd>
            </div>
            {desconto > 0 && (
              <div>
                <dt>Desconto</dt>
                <dd>− {formatarReais(desconto)}</dd>
              </div>
            )}
            <div className="resumo-valores__destaque">
              <dt>Total</dt>
              <dd>{formatarReais(total)}</dd>
            </div>
            <div>
              <dt>Pago</dt>
              <dd>{formatarReais(resumo.pago)}</dd>
            </div>
            {resumo.restante > 0 ? (
              <div className="resumo-valores__restante">
                <dt>Falta</dt>
                <dd>{formatarReais(resumo.restante)}</dd>
              </div>
            ) : (
              <div className="resumo-valores__troco">
                <dt>Troco</dt>
                <dd>{formatarReais(resumo.troco)}</dd>
              </div>
            )}
          </dl>

          {descontoExcessivo && (
            <div className="alerta alerta--erro">O desconto deve ser menor que o subtotal.</div>
          )}
          {resumo.erro && <div className="alerta alerta--erro">{resumo.erro}</div>}
          {erro && (
            <div className="alerta alerta--erro" role="alert">
              {erro}
            </div>
          )}

          <button
            ref={confirmarRef}
            type="button"
            className="btn btn--sucesso btn--bloco btn--grande"
            onClick={confirmar}
            disabled={!podeConfirmar || enviando}
          >
            {enviando ? 'Registrando...' : 'Confirmar venda (F2)'}
          </button>
          <button
            type="button"
            className="btn btn--fantasma btn--bloco"
            onClick={aoFechar}
            disabled={enviando}
          >
            Voltar para a venda (Esc)
          </button>
        </div>
      </div>
    </Modal>
  )
}
