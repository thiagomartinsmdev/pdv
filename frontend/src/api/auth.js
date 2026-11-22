import { api } from './client.js'

export async function login(email, senha) {
  const { data } = await api.post('/auth/login', { email, senha })
  return data // { access_token, token_type, expira_em_minutos, usuario }
}

export async function buscarUsuarioLogado() {
  const { data } = await api.get('/auth/me')
  return data
}
