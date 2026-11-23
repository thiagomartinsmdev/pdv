/**
 * Mesma regra da API para o link da imagem: http(s), com domínio, até 500 caracteres.
 * Validar aqui também mostra o erro na hora, antes de enviar o formulário.
 */
export function ehLinkDeImagemValido(texto) {
  const link = String(texto ?? '').trim()
  if (!link || link.length > 500) return false
  try {
    const url = new URL(link)
    return (url.protocol === 'http:' || url.protocol === 'https:') && Boolean(url.hostname)
  } catch {
    return false
  }
}
