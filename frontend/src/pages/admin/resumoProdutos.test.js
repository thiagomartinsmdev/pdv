import { describe, expect, it } from 'vitest'

import { resumirProdutos } from './resumoProdutos.js'

const item = (nome, quantidade) => ({ produto: { nome }, quantidade })

describe('resumirProdutos', () => {
  it('mostra todos quando são até 2 produtos', () => {
    const resumo = resumirProdutos([item('Pão francês', 3), item('Leite integral', 1)])
    expect(resumo.texto).toBe('Pão francês ×3, Leite integral ×1')
    expect(resumo.completo).toBe(resumo.texto)
  })

  it('mostra 2 e "+1 item" (singular)', () => {
    const resumo = resumirProdutos([item('A', 1), item('B', 2), item('C', 3)])
    expect(resumo.texto).toBe('A ×1, B ×2 +1 item')
    expect(resumo.completo).toBe('A ×1, B ×2, C ×3')
  })

  it('mostra 2 e "+N itens" (plural)', () => {
    const resumo = resumirProdutos([item('A', 1), item('B', 1), item('C', 1), item('D', 1)])
    expect(resumo.texto).toBe('A ×1, B ×1 +2 itens')
  })

  it('um produto só', () => {
    expect(resumirProdutos([item('Café 500g', 2)]).texto).toBe('Café 500g ×2')
  })
})
