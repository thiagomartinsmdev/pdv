// Regras da grade de produtos do caixa (funções puras, testadas em catalogo.test.js).

import { interpretarEntrada } from './carrinho.js'

export const ABA_TODOS = 'todos'
export const ABA_MAIS_VENDIDOS = 'mais-vendidos'

/** "Pão Francês" -> "pao frances": sem acentos e em minúsculas, para a busca. */
export function normalizarTexto(texto) {
  return String(texto ?? '')
    .normalize('NFD')
    .replace(/\p{Diacritic}/gu, '')
    .toLowerCase()
    .trim()
}

/**
 * O que foi digitado no campo do caixa filtra a grade só quando tem letras.
 * Números (código de barras do leitor) não filtram. "3*pão" filtra por "pão".
 * Devolve o termo normalizado, ou null quando não há filtro.
 */
export function termoDeFiltro(entrada) {
  const { termo } = interpretarEntrada(entrada)
  return /\p{L}/u.test(termo) ? normalizarTexto(termo) : null
}

/** Produtos de uma aba: todos, uma categoria (id numérico) ou os mais vendidos. */
export function produtosDaAba(aba, { produtos, maisVendidos }) {
  if (aba === ABA_TODOS) return produtos
  if (aba === ABA_MAIS_VENDIDOS) return maisVendidos
  return produtos.filter((produto) => produto.categoria_id === aba)
}

/** Produtos cujo nome contém o termo (já normalizado), ignorando acentos. */
export function filtrarPorNome(produtos, termo) {
  if (!termo) return produtos
  return produtos.filter((produto) => normalizarTexto(produto.nome).includes(termo))
}
