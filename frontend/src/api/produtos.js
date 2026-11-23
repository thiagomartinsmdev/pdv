import { api } from './client.js'

export async function buscarPorCodigo(codigoBarras) {
  const { data } = await api.get(`/produtos/codigo/${encodeURIComponent(codigoBarras)}`)
  return data
}

/** params: { busca, incluir_inativos } */
export async function listarProdutos(params = {}) {
  const { data } = await api.get('/produtos', { params })
  return data
}

export async function criarProduto(dados) {
  const { data } = await api.post('/produtos', dados)
  return data
}

/** Altera só os campos enviados (inclusive "ativo", para reativar). */
export async function atualizarProduto(id, dados) {
  const { data } = await api.patch(`/produtos/${id}`, dados)
  return data
}

/** Exclusão lógica: o produto fica inativo. */
export async function desativarProduto(id) {
  await api.delete(`/produtos/${id}`)
}

/** params: { dias, limite } — mais vendidos dos últimos dias (aba do caixa). */
export async function listarMaisVendidos(params = {}) {
  const { data } = await api.get('/produtos/mais-vendidos', { params })
  return data
}
