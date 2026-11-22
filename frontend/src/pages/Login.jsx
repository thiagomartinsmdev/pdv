import { useState } from 'react'
import { Navigate, useLocation, useNavigate } from 'react-router'

import { useAuth } from '../hooks/useAuth.js'
import { mensagemDeErro } from '../utils/erros.js'
import { rotaInicial } from '../utils/rotas.js'

// Usuários criados pelo script de seed, para facilitar a demonstração.
const USUARIOS_DEMO = [
  { perfil: 'Admin', email: 'admin@pdv.com', senha: 'admin123' },
  { perfil: 'Operador', email: 'operador@pdv.com', senha: 'operador123' },
]

export default function Login() {
  const { usuario, entrar } = useAuth()
  const navigate = useNavigate()
  const location = useLocation()

  // Campos "controlados": o valor do input vem do estado, e cada tecla atualiza o estado.
  const [email, setEmail] = useState('')
  const [senha, setSenha] = useState('')
  const [erro, setErro] = useState('')
  const [enviando, setEnviando] = useState(false)

  // Já logado? Não faz sentido mostrar o login.
  if (usuario) {
    return <Navigate to={rotaInicial(usuario)} replace />
  }

  async function aoEnviar(evento) {
    evento.preventDefault() // impede o navegador de recarregar a página
    setErro('')
    setEnviando(true)
    try {
      const logado = await entrar(email, senha)
      // Volta para a página que a pessoa tentou abrir, ou vai para a tela inicial do perfil.
      navigate(location.state?.de ?? rotaInicial(logado), { replace: true })
    } catch (falha) {
      setErro(mensagemDeErro(falha))
      setEnviando(false)
    }
  }

  function preencher(demo) {
    setEmail(demo.email)
    setSenha(demo.senha)
    setErro('')
  }

  return (
    <div className="pagina-login">
      <div className="cartao cartao--login">
        <div className="login__marca">
          <img src="/favicon.svg" alt="" width="44" height="44" />
          <div>
            <h1>PDV Padaria</h1>
            <p className="texto-suave">Sistema de caixa</p>
          </div>
        </div>

        {location.state?.aviso && !erro && (
          <div className="alerta alerta--aviso">{location.state.aviso}</div>
        )}
        {erro && (
          <div className="alerta alerta--erro" role="alert">
            {erro}
          </div>
        )}

        <form onSubmit={aoEnviar} className="formulario">
          <label className="campo">
            <span>E-mail</span>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              autoComplete="username"
              autoFocus
              required
            />
          </label>

          <label className="campo">
            <span>Senha</span>
            <input
              type="password"
              value={senha}
              onChange={(e) => setSenha(e.target.value)}
              autoComplete="current-password"
              required
            />
          </label>

          <button type="submit" className="btn btn--primario btn--bloco" disabled={enviando}>
            {enviando ? 'Entrando...' : 'Entrar'}
          </button>
        </form>

        <div className="login__demo">
          <p className="texto-suave">Usuários de demonstração:</p>
          <div className="login__demo-botoes">
            {USUARIOS_DEMO.map((demo) => (
              <button
                key={demo.email}
                type="button"
                className="btn btn--secundario"
                onClick={() => preencher(demo)}
              >
                {demo.perfil}
              </button>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}
