import { useEffect, useState } from 'react'

/**
 * Devolve "valor" só depois que ele para de mudar por "ms" milissegundos ("debounce").
 * Usado na busca: não chama a API a cada tecla, só quando a pessoa para de digitar.
 */
export function useAtraso(valor, ms = 300) {
  const [atrasado, setAtrasado] = useState(valor)

  useEffect(() => {
    const temporizador = setTimeout(() => setAtrasado(valor), ms)
    return () => clearTimeout(temporizador)
  }, [valor, ms])

  return atrasado
}
