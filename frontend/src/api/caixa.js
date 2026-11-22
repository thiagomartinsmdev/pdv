import { api } from './client.js'

/** Caixa aberto do usuário logado, ou null. */
export async function buscarCaixaAtual() {
  const { data } = await api.get('/caixa/atual')
  return data
}

export async function abrirCaixa(valorAbertura) {
  const { data } = await api.post('/caixa/abrir', { valor_abertura: valorAbertura })
  return data
}

export async function fecharCaixa(valorInformado) {
  const { data } = await api.post('/caixa/fechar', { valor_informado: valorInformado })
  return data
}
