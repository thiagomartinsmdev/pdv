// Tela inicial de cada perfil após o login.
export function rotaInicial(usuario) {
  return usuario?.perfil === 'admin' ? '/admin/relatorios' : '/caixa'
}
