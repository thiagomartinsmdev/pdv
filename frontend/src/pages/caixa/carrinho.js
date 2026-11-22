// Estado da venda em andamento (o "carrinho"), controlado por um reducer.
//
// Um reducer é uma função pura: recebe o estado atual e uma ação e devolve o NOVO
// estado, sem alterar o antigo. Toda mudança do carrinho passa por aqui, o que deixa
// as regras em um só lugar e fáceis de testar (ver carrinho.test.js).

import { paraCentavos } from '../../utils/dinheiro.js'

export const carrinhoInicial = { itens: [] } // itens: [{ produto, quantidade }]

export function carrinhoReducer(estado, acao) {
  switch (acao.tipo) {
    case 'adicionar': {
      // O mesmo produto vira uma linha só, que vai para o fim da lista:
      // assim "o último item" (F4) é sempre o último que foi bipado.
      const { produto, quantidade } = acao
      const existente = estado.itens.find((item) => item.produto.id === produto.id)
      const outros = estado.itens.filter((item) => item.produto.id !== produto.id)
      const novaQuantidade = (existente?.quantidade ?? 0) + quantidade
      return { itens: [...outros, { produto, quantidade: novaQuantidade }] }
    }

    case 'alterarQuantidade': {
      if (acao.quantidade <= 0) {
        return carrinhoReducer(estado, { tipo: 'remover', produtoId: acao.produtoId })
      }
      return {
        itens: estado.itens.map((item) =>
          item.produto.id === acao.produtoId ? { ...item, quantidade: acao.quantidade } : item,
        ),
      }
    }

    case 'remover':
      return { itens: estado.itens.filter((item) => item.produto.id !== acao.produtoId) }

    case 'removerUltimo':
      return { itens: estado.itens.slice(0, -1) }

    case 'limpar':
      return carrinhoInicial

    default:
      throw new Error(`Ação desconhecida: ${acao.tipo}`)
  }
}

export function subtotalDoItem(item) {
  return paraCentavos(item.produto.preco) * item.quantidade
}

export function totalDoCarrinho(itens) {
  return itens.reduce((soma, item) => soma + subtotalDoItem(item), 0)
}

export function quantidadeDeUnidades(itens) {
  return itens.reduce((soma, item) => soma + item.quantidade, 0)
}

export function quantidadeNoCarrinho(itens, produtoId) {
  return itens.find((item) => item.produto.id === produtoId)?.quantidade ?? 0
}

/**
 * Interpreta o que foi digitado no campo do caixa.
 * "7891000000014" -> 1 unidade do código; "5*7891000000014" -> 5 unidades.
 * Também vale para nomes: "3*pão de queijo".
 */
export function interpretarEntrada(texto) {
  const limpo = texto.trim()
  const multiplicado = limpo.match(/^(\d{1,4})\s*\*\s*(.+)$/)
  if (multiplicado) {
    return {
      quantidade: Math.max(1, Number.parseInt(multiplicado[1], 10)),
      termo: multiplicado[2].trim(),
    }
  }
  return { quantidade: 1, termo: limpo }
}
