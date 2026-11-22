import { useContext } from 'react'

import { AuthContext } from '../contexts/AuthContext.js'

// Hook ("gancho") personalizado: qualquer componente chama useAuth() para saber
// quem está logado e para usar entrar() / sair().
export function useAuth() {
  const contexto = useContext(AuthContext)
  if (!contexto) {
    throw new Error('useAuth() precisa ser usado dentro do <AuthProvider>.')
  }
  return contexto
}
