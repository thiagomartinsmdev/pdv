import { api } from './client.js'

export async function buscarPorCodigo(codigoBarras) {
  const { data } = await api.get(`/produtos/codigo/${encodeURIComponent(codigoBarras)}`)
  return data
}

export async function listarProdutos(params = {}) {
  const { data } = await api.get('/produtos', { params })
  return data
}
