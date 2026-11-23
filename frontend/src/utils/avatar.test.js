import { describe, expect, it } from 'vitest'

import { TOTAL_CORES_AVATAR, corDoNome, inicialDoNome } from './avatar.js'

describe('inicialDoNome', () => {
  it.each([
    ['Pão francês', 'P'],
    ['  bolo de fubá', 'B'],
    ['água mineral', 'Á'],
    ['(promo) Café', 'P'],
    ['7 grãos', '7'],
    ['', '?'],
    [null, '?'],
  ])('%s -> %s', (nome, esperado) => {
    expect(inicialDoNome(nome)).toBe(esperado)
  })
})

describe('corDoNome', () => {
  it('é sempre a mesma para o mesmo nome (sem diferenciar maiúsculas)', () => {
    expect(corDoNome('Pão francês')).toBe(corDoNome('PÃO FRANCÊS'))
  })

  it(`fica entre 1 e ${TOTAL_CORES_AVATAR}`, () => {
    const nomes = ['Pão', 'Leite', 'Café', 'Bolo', 'Sonho', 'Arroz', 'Feijão', 'Suco', '']
    for (const nome of nomes) {
      expect(corDoNome(nome)).toBeGreaterThanOrEqual(1)
      expect(corDoNome(nome)).toBeLessThanOrEqual(TOTAL_CORES_AVATAR)
    }
  })

  it('distribui nomes diferentes entre várias cores', () => {
    const nomes = ['Pão', 'Leite', 'Café', 'Bolo', 'Sonho', 'Arroz', 'Feijão', 'Suco', 'Água']
    expect(new Set(nomes.map(corDoNome)).size).toBeGreaterThanOrEqual(4)
  })
})
