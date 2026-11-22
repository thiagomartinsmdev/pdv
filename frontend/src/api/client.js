// Cliente HTTP (Axios) configurado para a API do PDV.
// Todas as chamadas à API passam por aqui, então token e erros de sessão são
// tratados em um lugar só, e não em cada tela.
import axios from 'axios'

const CHAVE_TOKEN = 'pdv:token'

// O token fica no localStorage para sobreviver ao recarregar a página.
// try/catch porque o navegador pode bloquear o acesso (ex.: modo privado restrito).
export const armazenamentoToken = {
  ler() {
    try {
      return localStorage.getItem(CHAVE_TOKEN)
    } catch {
      return null
    }
  },
  salvar(token) {
    try {
      localStorage.setItem(CHAVE_TOKEN, token)
    } catch {
      /* sem armazenamento: a sessão dura só enquanto a aba estiver aberta */
    }
  },
  remover() {
    try {
      localStorage.removeItem(CHAVE_TOKEN)
    } catch {
      /* nada a fazer */
    }
  },
}

export const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL ?? 'http://localhost:8000',
  timeout: 15000,
})

// Interceptor de requisição: roda antes de TODA chamada e anexa o token.
api.interceptors.request.use((config) => {
  const token = armazenamentoToken.ler()
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Função chamada quando a API responde 401 (token expirado/inválido).
// Quem a define é o AuthProvider, que sabe fazer logout e redirecionar.
let aoSessaoExpirar = null

export function definirAoSessaoExpirar(funcao) {
  aoSessaoExpirar = funcao
}

// Interceptor de resposta: roda depois de toda resposta com erro.
api.interceptors.response.use(
  (resposta) => resposta,
  (erro) => {
    // 401 no próprio login significa "senha errada", e não "sessão expirada".
    const ehLogin = erro.config?.url?.endsWith('/auth/login')
    if (erro.response?.status === 401 && !ehLogin) {
      aoSessaoExpirar?.()
    }
    return Promise.reject(erro)
  },
)
