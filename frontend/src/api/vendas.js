import { api } from './client.js'

/** dados: { itens: [{produto_id, quantidade}], pagamentos: [{forma, valor}], desconto } */
export async function registrarVenda(dados) {
  const { data } = await api.post('/vendas', dados)
  return data
}

/** params: { inicio, fim, status, limite, deslocamento } */
export async function listarVendas(params = {}) {
  const { data } = await api.get('/vendas', { params })
  return data
}

export async function cancelarVenda(id) {
  const { data } = await api.post(`/vendas/${id}/cancelar`)
  return data
}
