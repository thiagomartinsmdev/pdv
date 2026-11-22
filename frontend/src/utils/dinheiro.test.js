import { describe, expect, it } from 'vitest'

import {
  centavosParaApi,
  centavosParaTexto,
  formatarReais,
  lerValorDigitado,
  paraCentavos,
} from './dinheiro.js'

describe('paraCentavos', () => {
  it.each([
    ['8.49', 849],
    ['0.90', 90],
    ['10', 1000],
    ['10.5', 1050],
    ['-5.00', -500],
    ['-0.50', -50],
    [null, 0],
  ])('%s -> %i', (entrada, esperado) => {
    expect(paraCentavos(entrada)).toBe(esperado)
  })

  it('não sofre com erro de ponto flutuante', () => {
    // Em float: 0.1 + 0.2 = 0.30000000000000004
    expect(paraCentavos('0.10') + paraCentavos('0.20')).toBe(30)
  })
})

describe('centavosParaApi / centavosParaTexto', () => {
  it('formata para a API e para digitação', () => {
    expect(centavosParaApi(849)).toBe('8.49')
    expect(centavosParaApi(5)).toBe('0.05')
    expect(centavosParaApi(-200)).toBe('-2.00')
    expect(centavosParaTexto(1050)).toBe('10,50')
  })
})

describe('formatarReais', () => {
  it('usa o padrão brasileiro', () => {
    // O Intl usa um espaço especial (NBSP) depois do "R$".
    expect(formatarReais(123450).replace(/\s/g, ' ')).toBe('R$ 1.234,50')
  })
})

describe('lerValorDigitado', () => {
  it.each([
    ['10', 1000],
    ['10,5', 1050],
    ['10,50', 1050],
    ['10.50', 1050],
    ['R$ 1.234,56', 123456],
    ['  7,35 ', 735],
  ])('"%s" -> %i', (entrada, esperado) => {
    expect(lerValorDigitado(entrada)).toBe(esperado)
  })

  it.each(['', 'abc', '10,555', '-5', '1,2,3'])('"%s" é inválido', (entrada) => {
    expect(lerValorDigitado(entrada)).toBeNull()
  })
})
