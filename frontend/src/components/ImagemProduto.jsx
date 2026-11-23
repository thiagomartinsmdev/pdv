import { useState } from 'react'

import { corDoNome, inicialDoNome } from '../utils/avatar.js'

/**
 * Foto do produto ou, se não houver (ou se o link não carregar), a inicial do nome
 * sobre um fundo colorido. "tamanho" é o lado do quadrado, em pixels.
 *
 * Quem usa passa key={url} quando o link pode mudar (ex.: pré-visualização), para o
 * estado "falhou" ser reiniciado a cada link novo.
 */
export default function ImagemProduto({ nome, url, tamanho = 48, aoFalhar }) {
  const [falhou, setFalhou] = useState(false)
  const estilo = { width: tamanho, height: tamanho, fontSize: Math.round(tamanho * 0.42) }

  if (url && !falhou) {
    return (
      <span className="imagem-produto" style={estilo}>
        <img
          src={url}
          alt=""
          loading="lazy"
          referrerPolicy="no-referrer"
          onError={() => {
            setFalhou(true)
            aoFalhar?.()
          }}
        />
      </span>
    )
  }

  return (
    <span
      className={`imagem-produto imagem-produto--inicial imagem-produto--cor-${corDoNome(nome)}`}
      style={estilo}
      aria-hidden="true"
    >
      {inicialDoNome(nome)}
    </span>
  )
}
