import { describe, expect, it } from 'vitest'

import { situacaoDoEstoque } from '../../utils/estoque.js'
import {
  ABA_MAIS_VENDIDOS,
  ABA_TODOS,
  filtrarPorNome,
  normalizarTexto,
  produtosDaAba,
  termoDeFiltro,
} from './catalogo.js'

const pao = { id: 1, nome: 'Pão francês', categoria_id: 10 }
const paoQueijo = { id: 2, nome: 'Pão de queijo', categoria_id: 20 }
const suco = { id: 3, nome: 'Suco de laranja', categoria_id: 30 }
const semCategoria = { id: 4, nome: 'Avulso', categoria_id: null }
const produtos = [pao, paoQueijo, suco, semCategoria]

describe('termoDeFiltro (o campo do caixa filtra a grade só com letras)', () => {
  it.each([
    ['pão', 'pao'],
    ['  Pão FRANCÊS ', 'pao frances'],
    ['3*queijo', 'queijo'],
    ['7891000000014', null], // bipe do leitor: não filtra
    ['5*7891000000014', null],
    ['', null],
    ['   ', null],
  ])('"%s" -> %s', (entrada, esperado) => {
    expect(termoDeFiltro(entrada)).toBe(esperado)
  })
})

describe('produtosDaAba', () => {
  const maisVendidos = [suco, pao]

  it('Todos mostra todos os produtos, inclusive sem categoria', () => {
    expect(produtosDaAba(ABA_TODOS, { produtos, maisVendidos })).toEqual(produtos)
  })

  it('uma categoria mostra só os produtos dela', () => {
    expect(produtosDaAba(10, { produtos, maisVendidos })).toEqual([pao])
  })

  it('Mais vendidos mantém a ordem do ranking', () => {
    expect(produtosDaAba(ABA_MAIS_VENDIDOS, { produtos, maisVendidos })).toEqual([suco, pao])
  })
})

describe('filtrarPorNome', () => {
  it('ignora acentos e maiúsculas', () => {
    expect(filtrarPorNome(produtos, normalizarTexto('PAO'))).toEqual([pao, paoQueijo])
  })

  it('sem termo devolve a lista inteira', () => {
    expect(filtrarPorNome(produtos, null)).toEqual(produtos)
  })
})

describe('situacaoDoEstoque', () => {
  it.each([
    [0, 'esgotado'],
    [-1, 'esgotado'],
    [1, 'baixo'],
    [10, 'baixo'],
    [11, 'normal'],
  ])('%i -> %s', (quantidade, esperado) => {
    expect(situacaoDoEstoque(quantidade)).toBe(esperado)
  })
})
