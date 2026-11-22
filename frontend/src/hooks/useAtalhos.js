import { useEffect, useRef } from 'react'

/**
 * Registra atalhos de teclado enquanto o componente estiver na tela.
 *
 *   useAtalhos({ F2: finalizar, Escape: cancelar }, ativo)
 *
 * Com ativo=false os atalhos ficam desligados (ex.: a tela do caixa desliga os
 * dela enquanto um modal está aberto, para o Esc fechar só o modal).
 */
export function useAtalhos(atalhos, ativo = true) {
  // Guardamos os atalhos numa ref para o listener sempre chamar a versão mais
  // recente das funções, sem precisar ser removido e registrado de novo a cada tecla.
  const atalhosRef = useRef(atalhos)
  useEffect(() => {
    atalhosRef.current = atalhos
  })

  useEffect(() => {
    if (!ativo) return undefined

    function aoTeclar(evento) {
      const acao = atalhosRef.current[evento.key]
      if (acao) {
        evento.preventDefault() // ex.: impede o F4 de abrir algo do navegador
        acao(evento)
      }
    }

    window.addEventListener('keydown', aoTeclar)
    // A função devolvida pelo useEffect é a "limpeza": roda quando o componente sai da
    // tela (ou antes de o efeito rodar de novo). Sem ela, os listeners se acumulariam.
    return () => window.removeEventListener('keydown', aoTeclar)
  }, [ativo])
}
