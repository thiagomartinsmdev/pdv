// Transforma um erro do Axios em uma mensagem amigável para exibir na tela.
export function mensagemDeErro(erro, padrao = 'Ocorreu um erro inesperado. Tente novamente.') {
  if (!erro?.response) {
    return 'Não foi possível conectar ao servidor. Verifique se a API está rodando.'
  }

  const detalhe = erro.response.data?.detail

  // Erros de regra de negócio da nossa API: {"detail": "mensagem em português"}
  if (typeof detalhe === 'string') {
    return detalhe
  }

  // Erros de validação do FastAPI: {"detail": [{"loc": ["body", "campo"], "msg": ...}]}
  if (Array.isArray(detalhe) && detalhe.length > 0) {
    const campos = [...new Set(detalhe.map((d) => d.loc?.at(-1)).filter(Boolean))]
    return campos.length > 0
      ? `Verifique o(s) campo(s): ${campos.join(', ')}.`
      : 'Verifique os dados informados.'
  }

  return padrao
}
