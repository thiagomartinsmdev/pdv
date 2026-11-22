// Valores em dinheiro no frontend.
//
// Em JavaScript, 0.1 + 0.2 === 0.30000000000000004 (o mesmo problema do float no Python).
// Por isso, toda conta é feita em CENTAVOS INTEIROS (R$ 8,49 = 849). A API envia e
// recebe valores como texto ("8.49"); a conversão acontece só nas pontas.

const formatador = new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' })

/** Texto da API ("8.49", "-5.00") -> centavos (849, -500). */
export function paraCentavos(valor) {
  if (valor === null || valor === undefined || valor === '') return 0
  const [inteiro, decimal = ''] = String(valor).split('.')
  const negativo = inteiro.startsWith('-')
  const centavos =
    Math.abs(Number.parseInt(inteiro, 10)) * 100 +
    Number.parseInt(decimal.padEnd(2, '0').slice(0, 2), 10)
  return negativo ? -centavos : centavos
}

/** Centavos (849) -> texto no formato da API ("8.49"). */
export function centavosParaApi(centavos) {
  const sinal = centavos < 0 ? '-' : ''
  const absoluto = Math.abs(centavos)
  const reais = Math.floor(absoluto / 100)
  const resto = String(absoluto % 100).padStart(2, '0')
  return `${sinal}${reais}.${resto}`
}

/** Centavos (849) -> texto para digitação ("8,49"). */
export function centavosParaTexto(centavos) {
  return centavosParaApi(centavos).replace('.', ',')
}

/** Centavos (123450) -> "R$ 1.234,50" (só para exibir). */
export function formatarReais(centavos) {
  return formatador.format(centavos / 100)
}

/**
 * Lê o que a pessoa digitou ("10", "10,5", "10.50", "R$ 1.234,56") e devolve centavos.
 * Retorna null se o texto estiver vazio ou não for um valor válido.
 */
export function lerValorDigitado(texto) {
  const limpo = String(texto ?? '')
    .replace(/R\$|\s/g, '')
    .trim()
  if (!limpo) return null

  // Com vírgula, o ponto é separador de milhar ("1.234,56"); sem vírgula, o ponto é decimal.
  const normalizado = limpo.includes(',') ? limpo.replace(/\./g, '').replace(',', '.') : limpo
  if (!/^\d+(\.\d{1,2})?$/.test(normalizado)) return null
  return paraCentavos(normalizado)
}
