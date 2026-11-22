import { api } from './client.js'

/** dados: { itens: [{produto_id, quantidade}], pagamentos: [{forma, valor}], desconto } */
export async function registrarVenda(dados) {
  const { data } = await api.post('/vendas', dados)
  return data
}
