import { URL_DA_API } from '../api/endereco.js'

// Foto guardada no servidor (ex.: importada pelo script de fotos em lote).
// Mesmo formato que a API aceita: /uploads/produtos/<nome>.<jpg|png|webp>.
const FOTO_DO_SERVIDOR = /^\/uploads\/produtos\/[A-Za-z0-9_-]{8,80}\.(?:jpg|png|webp)$/

export function ehFotoDoServidor(texto) {
  return FOTO_DO_SERVIDOR.test(String(texto ?? '').trim())
}

/**
 * Mesma regra da API para a imagem: link http(s) com domínio, até 500 caracteres,
 * ou o caminho de uma foto guardada no servidor.
 * Validar aqui também mostra o erro na hora, antes de enviar o formulário.
 */
export function ehLinkDeImagemValido(texto) {
  const link = String(texto ?? '').trim()
  if (!link || link.length > 500) return false
  if (ehFotoDoServidor(link)) return true
  try {
    const url = new URL(link)
    return (url.protocol === 'http:' || url.protocol === 'https:') && Boolean(url.hostname)
  } catch {
    return false
  }
}

/**
 * Endereço que o <img> deve carregar. Fotos do servidor vêm como caminho relativo
 * ("/uploads/produtos/..."), que precisa do endereço da API na frente: o frontend roda
 * em outra porta (5173) e, sem isso, o navegador procuraria a foto no próprio Vite.
 */
export function enderecoDaImagem(url, base = URL_DA_API) {
  if (!url) return url
  return ehFotoDoServidor(url) ? `${base}${url.trim()}` : url
}
