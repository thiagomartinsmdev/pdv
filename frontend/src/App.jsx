import { Navigate, Route, Routes } from 'react-router'

import EmConstrucao from './components/EmConstrucao.jsx'
import Layout from './components/Layout.jsx'
import RotaProtegida from './components/RotaProtegida.jsx'
import { useAuth } from './hooks/useAuth.js'
import Login from './pages/Login.jsx'
import NaoEncontrada from './pages/NaoEncontrada.jsx'
import { rotaInicial } from './utils/rotas.js'

/**
 * Mapa de rotas da aplicação.
 *
 * As rotas são aninhadas: cada nível "envolve" o de dentro.
 *   RotaProtegida (exige login)
 *     └─ Layout (cabeçalho + menu)
 *          ├─ /caixa                   qualquer perfil
 *          └─ RotaProtegida (só admin)
 *               └─ /admin/produtos, /admin/vendas, /admin/relatorios
 */
export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />

      <Route element={<RotaProtegida />}>
        <Route element={<Layout />}>
          <Route index element={<PaginaInicial />} />
          <Route path="caixa" element={<EmConstrucao titulo="Caixa" etapa={7} />} />

          <Route path="admin" element={<RotaProtegida perfis={['admin']} />}>
            <Route index element={<Navigate to="relatorios" replace />} />
            <Route path="produtos" element={<EmConstrucao titulo="Produtos" etapa={8} />} />
            <Route path="vendas" element={<EmConstrucao titulo="Vendas" etapa={8} />} />
            <Route path="relatorios" element={<EmConstrucao titulo="Relatórios" etapa={8} />} />
          </Route>
        </Route>
      </Route>

      <Route path="*" element={<NaoEncontrada />} />
    </Routes>
  )
}

/** "/" leva cada perfil para a sua tela inicial. */
function PaginaInicial() {
  const { usuario } = useAuth()
  return <Navigate to={rotaInicial(usuario)} replace />
}
