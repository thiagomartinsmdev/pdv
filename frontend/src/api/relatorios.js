import { api } from './client.js'

/** params: { inicio, fim, limite_produtos } (datas no formato AAAA-MM-DD) */
export async function relatorioVendas(params) {
  const { data } = await api.get('/relatorios/vendas', { params })
  return data
}
