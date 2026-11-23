import { api } from './client.js'

/** params: { incluir_inativas } (inativas só aparecem para admin) */
export async function listarCategorias(params = {}) {
  const { data } = await api.get('/categorias', { params })
  return data
}

export async function criarCategoria(dados) {
  const { data } = await api.post('/categorias', dados)
  return data
}

/** Altera só os campos enviados (inclusive "ativo", para reativar). */
export async function atualizarCategoria(id, dados) {
  const { data } = await api.patch(`/categorias/${id}`, dados)
  return data
}

/** Exclusão lógica: a categoria fica inativa. */
export async function desativarCategoria(id) {
  await api.delete(`/categorias/${id}`)
}
