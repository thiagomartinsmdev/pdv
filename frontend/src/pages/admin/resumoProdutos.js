// Resumo dos produtos de uma venda para a coluna "Produtos" do histórico.

/**
 * itens: [{ produto: { nome }, quantidade }] (como vêm da API)
 * Devolve:
 *   texto:    "Pão francês ×3, Leite integral ×1 +2 itens" (no máximo `limite` produtos)
 *   completo: todos os produtos, para o tooltip (atributo title)
 */
export function resumirProdutos(itens, limite = 2) {
  const nomes = itens.map((item) => `${item.produto.nome} ×${item.quantidade}`)
  const completo = nomes.join(', ')
  const restantes = nomes.length - limite

  if (restantes <= 0) {
    return { texto: completo, completo }
  }
  const sufixo = restantes === 1 ? '+1 item' : `+${restantes} itens`
  return { texto: `${nomes.slice(0, limite).join(', ')} ${sufixo}`, completo }
}
