// Marcador temporário para as telas que serão feitas nas próximas etapas.
export default function EmConstrucao({ titulo, etapa }) {
  return (
    <section>
      <h1 className="titulo-pagina">{titulo}</h1>
      <div className="cartao">
        <p className="texto-suave">Esta tela será construída na etapa {etapa}.</p>
      </div>
    </section>
  )
}
