import { Link } from 'react-router'

import { useAuth } from '../hooks/useAuth.js'
import { rotaInicial } from '../utils/rotas.js'

export default function AcessoNegado() {
  const { usuario } = useAuth()

  return (
    <div className="pagina-aviso">
      <h1>Acesso negado</h1>
      <p className="texto-suave">Esta área é exclusiva para administradores.</p>
      <Link to={rotaInicial(usuario)} className="btn btn--primario">
        Voltar para o início
      </Link>
    </div>
  )
}
