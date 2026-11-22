import { NavLink, Outlet, useNavigate } from 'react-router'

import { useAuth } from '../hooks/useAuth.js'

// Links do menu. "perfis" indica quem pode ver cada um.
const LINKS = [
  { para: '/caixa', texto: 'Caixa', perfis: ['admin', 'operador'] },
  { para: '/admin/produtos', texto: 'Produtos', perfis: ['admin'] },
  { para: '/admin/vendas', texto: 'Vendas', perfis: ['admin'] },
  { para: '/admin/relatorios', texto: 'Relatórios', perfis: ['admin'] },
]

/** Estrutura comum das telas logadas: cabeçalho com menu e, abaixo, a página atual. */
export default function Layout() {
  const { usuario, sair } = useAuth()
  const navigate = useNavigate()

  function aoSair() {
    sair()
    navigate('/login', { replace: true })
  }

  const linksVisiveis = LINKS.filter((link) => link.perfis.includes(usuario.perfil))

  return (
    <div className="layout">
      <header className="cabecalho">
        <div className="cabecalho__marca">
          <img src="/favicon.svg" alt="" width="28" height="28" />
          <span>PDV Padaria</span>
        </div>

        <nav className="cabecalho__menu" aria-label="Menu principal">
          {/* NavLink sabe se é a rota atual e permite destacar o link ativo. */}
          {linksVisiveis.map((link) => (
            <NavLink
              key={link.para}
              to={link.para}
              className={({ isActive }) => `menu-link${isActive ? ' menu-link--ativo' : ''}`}
            >
              {link.texto}
            </NavLink>
          ))}
        </nav>

        <div className="cabecalho__usuario">
          <span className="cabecalho__nome">{usuario.nome}</span>
          <span className={`badge badge--${usuario.perfil}`}>{usuario.perfil}</span>
          <button type="button" className="btn btn--fantasma" onClick={aoSair}>
            Sair
          </button>
        </div>
      </header>

      <main className="conteudo">
        <Outlet />
      </main>
    </div>
  )
}
