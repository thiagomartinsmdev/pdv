import { useCallback, useEffect, useMemo, useState } from 'react'
import { useNavigate } from 'react-router'

import { buscarUsuarioLogado, login } from '../api/auth.js'
import { armazenamentoToken, definirAoSessaoExpirar } from '../api/client.js'
import { AuthContext } from './AuthContext.js'

/**
 * Guarda quem está logado e oferece entrar() e sair() para toda a aplicação.
 *
 * Ao abrir a página, se já existe um token salvo, pergunta à API (/auth/me) quem
 * é o usuário. Enquanto isso, "carregando" fica true, e as rotas protegidas esperam
 * em vez de mandar a pessoa para o login.
 */
export function AuthProvider({ children }) {
  // useState: um valor que, quando muda, faz o React redesenhar os componentes que o usam.
  const [usuario, setUsuario] = useState(null)
  const [carregando, setCarregando] = useState(() => Boolean(armazenamentoToken.ler()))
  const navigate = useNavigate()

  // useCallback: mantém a mesma função entre renderizações (evita efeitos repetidos).
  const sair = useCallback(() => {
    armazenamentoToken.remover()
    setUsuario(null)
  }, [])

  const entrar = useCallback(async (email, senha) => {
    const resposta = await login(email, senha)
    armazenamentoToken.salvar(resposta.access_token)
    setUsuario(resposta.usuario)
    return resposta.usuario
  }, [])

  // useEffect: código que roda DEPOIS de desenhar a tela (efeitos colaterais).
  // Este informa ao cliente HTTP o que fazer quando a API responder 401.
  useEffect(() => {
    definirAoSessaoExpirar(() => {
      sair()
      navigate('/login', {
        replace: true,
        state: { aviso: 'Sua sessão expirou. Entre novamente.' },
      })
    })
  }, [sair, navigate])

  // Roda uma vez ao abrir a aplicação ([] = sem dependências): restaura a sessão.
  useEffect(() => {
    if (!armazenamentoToken.ler()) return
    buscarUsuarioLogado()
      .then(setUsuario)
      .catch(() => {
        // 401 já foi tratado pelo interceptor; outros erros (API fora do ar)
        // simplesmente deixam o usuário deslogado.
      })
      .finally(() => setCarregando(false))
  }, [])

  // useMemo: só recria o objeto quando algo muda, evitando redesenhos desnecessários.
  const valor = useMemo(
    () => ({
      usuario,
      carregando,
      ehAdmin: usuario?.perfil === 'admin',
      entrar,
      sair,
    }),
    [usuario, carregando, entrar, sair],
  )

  return <AuthContext.Provider value={valor}>{children}</AuthContext.Provider>
}
