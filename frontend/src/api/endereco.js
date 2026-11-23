// Endereço da API. Fica num arquivo próprio para ser usado tanto pelo Axios
// quanto pelas fotos guardadas no servidor (que o <img> carrega direto da API).
export const URL_DA_API = (import.meta.env.VITE_API_URL ?? 'http://localhost:8000').replace(/\/+$/, '')
