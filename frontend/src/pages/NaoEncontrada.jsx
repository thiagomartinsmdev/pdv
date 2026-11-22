import { Link } from 'react-router'

export default function NaoEncontrada() {
  return (
    <div className="pagina-aviso">
      <h1>Página não encontrada</h1>
      <p className="texto-suave">O endereço acessado não existe.</p>
      <Link to="/" className="btn btn--primario">
        Ir para o início
      </Link>
    </div>
  )
}
