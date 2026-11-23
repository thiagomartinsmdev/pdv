// Regra de estoque usada no admin e no caixa (um lugar só para o limite).

export const ESTOQUE_BAIXO = 10

/** 'esgotado' (0), 'baixo' (até ESTOQUE_BAIXO) ou 'normal'. */
export function situacaoDoEstoque(quantidade) {
  if (quantidade <= 0) return 'esgotado'
  if (quantidade <= ESTOQUE_BAIXO) return 'baixo'
  return 'normal'
}
