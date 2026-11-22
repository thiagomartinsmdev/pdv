import { useId } from 'react'
import { createPortal } from 'react-dom'

import { useAtalhos } from '../hooks/useAtalhos.js'

/**
 * Janela sobre a tela. Esc ou clique fora fecham (se aoFechar for informado).
 *
 * createPortal desenha o modal direto no <body>, fora da árvore de elementos da
 * página. Assim ele fica por cima de tudo, sem herdar estilos ou cortes do layout.
 */
export default function Modal({ titulo, aoFechar, children, largura = 'media' }) {
  const idTitulo = useId()
  useAtalhos({ Escape: () => aoFechar?.() })

  return createPortal(
    <div
      className="modal-fundo"
      onMouseDown={(evento) => evento.target === evento.currentTarget && aoFechar?.()}
    >
      <div
        className={`modal modal--${largura}`}
        role="dialog"
        aria-modal="true"
        aria-labelledby={idTitulo}
      >
        <header className="modal__cabecalho">
          <h2 id={idTitulo}>{titulo}</h2>
          {aoFechar && (
            <button
              type="button"
              className="btn btn--fantasma modal__fechar"
              onClick={aoFechar}
              aria-label="Fechar"
            >
              ✕
            </button>
          )}
        </header>
        {children}
      </div>
    </div>,
    document.body,
  )
}
