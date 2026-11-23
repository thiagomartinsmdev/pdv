import { lazy, Suspense } from 'react'
import { Navigate, Route, Routes } from 'react-router'

import Carregando from './components/Carregando.jsx'
import Layout from './components/Layout.jsx'
import RotaProtegida from './components/RotaProtegida.jsx'
import { useAuth } from './hooks/useAuth.js'
import Caixa from './pages/caixa/Caixa.jsx'
import Login from './pages/Login.jsx'
import NaoEncontrada from './pages/NaoEncontrada.jsx'
import { rotaInicial } from './utils/rotas.js'

// As telas de admin são carregadas sob demanda ("code splitting"): o código delas,
// incluindo a biblioteca de gráficos, só é baixado quando um admin abre uma delas.
// Assim o operador de caixa não paga por um código que nunca vai usar.
const Produtos = lazy(() => import('./pages/admin/Produtos.jsx'))
const Vendas = lazy(() => import('./pages/admin/Vendas.jsx'))
const Relatorios = lazy(() => import('./pages/admin/Relatorios.jsx'))

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
          <Route path="caixa" element={<Caixa />} />

          <Route path="admin" element={<RotaProtegida perfis={['admin']} />}>
            <Route index element={<Navigate to="relatorios" replace />} />
            <Route path="produtos" element={<SobDemanda pagina={Produtos} />} />
            <Route path="vendas" element={<SobDemanda pagina={Vendas} />} />
            <Route path="relatorios" element={<SobDemanda pagina={Relatorios} />} />
          </Route>
        </Route>
      </Route>

      <Route path="*" element={<NaoEncontrada />} />
    </Routes>
  )
}

/** Suspense mostra o "carregando" enquanto o código da página lazy é baixado. */
function SobDemanda({ pagina: Pagina }) {
  return (
    <Suspense fallback={<Carregando />}>
      <Pagina />
    </Suspense>
  )
}

/** "/" leva cada perfil para a sua tela inicial. */
function PaginaInicial() {
  const { usuario } = useAuth()
  return <Navigate to={rotaInicial(usuario)} replace />
}
