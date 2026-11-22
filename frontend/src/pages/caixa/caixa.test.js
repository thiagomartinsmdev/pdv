import { describe, expect, it } from 'vitest'

import {
  carrinhoInicial,
  carrinhoReducer,
  interpretarEntrada,
  quantidadeDeUnidades,
  totalDoCarrinho,
} from './carrinho.js'
import { resumirPagamentos } from './pagamento.js'

const pao = { id: 1, nome: 'Pão francês', preco: '0.90' }
const leite = { id: 2, nome: 'Leite', preco: '5.29' }

function aplicar(...acoes) {
  return acoes.reduce(carrinhoReducer, carrinhoInicial)
}

describe('carrinho', () => {
  it('soma o total em centavos', () => {
    const { itens } = aplicar(
      { tipo: 'adicionar', produto: pao, quantidade: 10 },
      { tipo: 'adicionar', produto: leite, quantidade: 2 },
    )
    expect(totalDoCarrinho(itens)).toBe(1958) // 10 x 0,90 + 2 x 5,29
    expect(quantidadeDeUnidades(itens)).toBe(12)
  })

  it('bipar o mesmo produto soma a quantidade e move a linha para o fim', () => {
    const { itens } = aplicar(
      { tipo: 'adicionar', produto: pao, quantidade: 1 },
      { tipo: 'adicionar', produto: leite, quantidade: 1 },
      { tipo: 'adicionar', produto: pao, quantidade: 2 },
    )
    expect(itens.map((i) => [i.produto.id, i.quantidade])).toEqual([
      [2, 1],
      [1, 3],
    ])
  })

  it('removerUltimo tira o último item bipado (F4)', () => {
    const { itens } = aplicar(
      { tipo: 'adicionar', produto: pao, quantidade: 1 },
      { tipo: 'adicionar', produto: leite, quantidade: 1 },
      { tipo: 'removerUltimo' },
    )
    expect(itens.map((i) => i.produto.id)).toEqual([1])
  })

  it('quantidade zero remove o item', () => {
    const { itens } = aplicar(
      { tipo: 'adicionar', produto: pao, quantidade: 1 },
      { tipo: 'alterarQuantidade', produtoId: 1, quantidade: 0 },
    )
    expect(itens).toEqual([])
  })

  it('não altera o estado anterior (função pura)', () => {
    const antes = aplicar({ tipo: 'adicionar', produto: pao, quantidade: 1 })
    carrinhoReducer(antes, { tipo: 'limpar' })
    expect(antes.itens).toHaveLength(1)
  })
})

describe('interpretarEntrada', () => {
  it.each([
    ['7891000000014', { quantidade: 1, termo: '7891000000014' }],
    ['5*7891000000014', { quantidade: 5, termo: '7891000000014' }],
    [' 3 * pão de queijo ', { quantidade: 3, termo: 'pão de queijo' }],
    ['0*123', { quantidade: 1, termo: '123' }],
  ])('"%s"', (texto, esperado) => {
    expect(interpretarEntrada(texto)).toEqual(esperado)
  })
})

describe('resumirPagamentos', () => {
  it('calcula o troco em dinheiro', () => {
    const resumo = resumirPagamentos([{ forma: 'dinheiro', valor: 2000 }], 1470)
    expect(resumo).toMatchObject({ pago: 2000, restante: 0, troco: 530, podeConfirmar: true })
  })

  it('pagamento insuficiente mostra o restante e não confirma', () => {
    const resumo = resumirPagamentos([{ forma: 'pix', valor: 1000 }], 2500)
    expect(resumo).toMatchObject({ restante: 1500, troco: 0, podeConfirmar: false })
  })

  it('pagamento misto: o troco sai do dinheiro', () => {
    const resumo = resumirPagamentos(
      [
        { forma: 'credito', valor: 3000 },
        { forma: 'dinheiro', valor: 5000 },
      ],
      5000,
    )
    expect(resumo).toMatchObject({ troco: 3000, podeConfirmar: true })
  })

  it('PIX acima do total é recusado', () => {
    const resumo = resumirPagamentos([{ forma: 'pix', valor: 1500 }], 1000)
    expect(resumo.erro).toMatch(/Só existe troco em dinheiro/)
    expect(resumo.podeConfirmar).toBe(false)
  })
})
