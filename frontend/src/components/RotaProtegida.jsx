import { Navigate, Outlet, useLocation } from 'react-router'

import { useAuth } from '../hooks/useAuth.js'
import AcessoNegado from '../pages/AcessoNegado.jsx'
import Carregando from './Carregando.jsx'

/**
 * Envolve rotas que exigem login (e, opcionalmente, um perfil).
 *
 * <Outlet /> é onde o React Router desenha a rota filha. Então este componente
 * funciona como um "porteiro": ou deixa passar (Outlet), ou redireciona.
 *
 * Importante: isto é só para a experiência do usuário. Quem garante a segurança
 * de verdade é a API, que confere o token e o perfil em toda requisição.
 */
export default function RotaProtegida({ perfis }) {
  const { usuario, carregando } = useAuth()
  const location = useLocation()

  if (carregando) {
    return <Carregando texto="Verificando sessão..." />
  }

  if (!usuario) {
    // Guarda a página pedida para voltar a ela depois do login.
    return <Navigate to="/login" replace state={{ de: location.pathname }} />
  }

  if (perfis && !perfis.includes(usuario.perfil)) {
    return <AcessoNegado />
  }

  return <Outlet />
}
