// Inicial e cor de fundo para produtos sem foto.

export const TOTAL_CORES_AVATAR = 6

/** "  pão francês" -> "P"; "água" -> "Á". Primeira letra ou número do nome. */
export function inicialDoNome(nome) {
  const caractere = [...String(nome ?? '').trim()].find((c) => /[\p{L}\p{N}]/u.test(c))
  return caractere ? caractere.toLocaleUpperCase('pt-BR') : '?'
}

/**
 * Número de 1 a TOTAL_CORES_AVATAR calculado a partir do nome.
 * O mesmo nome dá sempre a mesma cor, então o produto é reconhecido pela cor também.
 */
export function corDoNome(nome) {
  let hash = 0
  for (const caractere of String(nome ?? '').toLowerCase()) {
    hash = (hash * 31 + caractere.codePointAt(0)) % 1_000_003
  }
  return (hash % TOTAL_CORES_AVATAR) + 1
}
