const formatadorDataHora = new Intl.DateTimeFormat('pt-BR', {
  dateStyle: 'short',
  timeStyle: 'short',
})

/** "2026-11-22T14:05:00-03:00" -> "22/11/2026, 14:05" (no fuso do navegador). */
export function formatarDataHora(iso) {
  return iso ? formatadorDataHora.format(new Date(iso)) : '—'
}
