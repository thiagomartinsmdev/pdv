import { createContext } from 'react'

// Um "contexto" é uma forma de compartilhar dados com qualquer componente da árvore
// sem passá-los de pai para filho manualmente. Aqui ele guarda o usuário logado.
// O valor é fornecido pelo AuthProvider e lido com o hook useAuth().
export const AuthContext = createContext(null)
