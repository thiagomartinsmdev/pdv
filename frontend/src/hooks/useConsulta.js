import { useCallback, useEffect, useRef, useState } from 'react'

import { mensagemDeErro } from '../utils/erros.js'

/**
 * Busca dados na API e refaz a busca quando as dependências mudam.
 *
 *   const { dados, carregando, erro, recarregar } =
 *     useConsulta(() => listarVendas({ inicio, fim }), [inicio, fim])
 *
 * Enquanto uma nova busca acontece, "dados" continua com o resultado anterior:
 * a tela mostra os dados antigos (esmaecidos) em vez de piscar ou pular.
 */
export function useConsulta(buscar, dependencias = []) {
  const [versao, setVersao] = useState(0)
  // Identifica a busca atual. Quando muda, o efeito abaixo busca de novo.
  const chave = JSON.stringify([dependencias, versao])
  const [resultado, setResultado] = useState({ chave: null, dados: undefined, erro: '' })

  const buscarRef = useRef(buscar)
  useEffect(() => {
    buscarRef.current = buscar
  })

  useEffect(() => {
    let ativo = true
    buscarRef.current().then(
      (dados) => ativo && setResultado({ chave, dados, erro: '' }),
      (falha) =>
        ativo && setResultado((anterior) => ({ ...anterior, chave, erro: mensagemDeErro(falha) })),
    )
    // Se as dependências mudarem antes da resposta, a resposta antiga é ignorada.
    // Isso evita mostrar o resultado de um filtro que já não está selecionado.
    return () => {
      ativo = false
    }
  }, [chave])

  const recarregar = useCallback(() => setVersao((v) => v + 1), [])

  return {
    dados: resultado.dados,
    erro: resultado.erro,
    // "carregando" é derivado: a última resposta recebida não é da busca atual.
    carregando: resultado.chave !== chave,
    recarregar,
  }
}
