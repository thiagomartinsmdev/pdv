// Regras de pagamento do lado do front (as mesmas que a API aplica no servidor).
// Servem para mostrar o troco e avisar dos erros ANTES de enviar a venda.

import { formatarReais } from '../../utils/dinheiro.js'

export const FORMAS_PAGAMENTO = [
  { valor: 'dinheiro', rotulo: 'Dinheiro' },
  { valor: 'pix', rotulo: 'PIX' },
  { valor: 'debito', rotulo: 'Débito' },
  { valor: 'credito', rotulo: 'Crédito' },
]

export function rotuloDaForma(forma) {
  return FORMAS_PAGAMENTO.find((f) => f.valor === forma)?.rotulo ?? forma
}

/**
 * Resume os pagamentos lançados para uma venda de "total" centavos.
 * pagamentos: [{ forma, valor }] com valor em centavos.
 */
export function resumirPagamentos(pagamentos, total) {
  const pago = pagamentos.reduce((soma, p) => soma + p.valor, 0)
  const emDinheiro = pagamentos
    .filter((p) => p.forma === 'dinheiro')
    .reduce((soma, p) => soma + p.valor, 0)
  const foraDinheiro = pago - emDinheiro

  let erro = ''
  if (foraDinheiro > total) {
    erro = `PIX e cartão somam ${formatarReais(foraDinheiro)}, mais que o total. Só existe troco em dinheiro.`
  }

  return {
    pago,
    restante: Math.max(0, total - pago),
    troco: erro ? 0 : Math.max(0, pago - total),
    erro,
    podeConfirmar: total > 0 && pago >= total && !erro,
  }
}
