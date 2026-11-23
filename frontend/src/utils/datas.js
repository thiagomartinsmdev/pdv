const formatadorDataHora = new Intl.DateTimeFormat('pt-BR', {
  dateStyle: 'short',
  timeStyle: 'short',
})

/** "2026-11-22T14:05:00-03:00" -> "22/11/2026, 14:05" (no fuso do navegador). */
export function formatarDataHora(iso) {
  return iso ? formatadorDataHora.format(new Date(iso)) : '—'
}

// Datas "de calendário" (sem hora) circulam como texto AAAA-MM-DD, o formato da API
// e do <input type="date">. Elas são montadas pelos componentes da data local, e não
// com toISOString(), que usa UTC e erraria o dia depois das 21h no horário de Brasília.

/** Date -> "AAAA-MM-DD" no fuso local. */
export function dataLocalISO(data = new Date()) {
  const ano = data.getFullYear()
  const mes = String(data.getMonth() + 1).padStart(2, '0')
  const dia = String(data.getDate()).padStart(2, '0')
  return `${ano}-${mes}-${dia}`
}

/** "2026-11-30" + 1 -> "2026-12-01" (passa de mês e de ano corretamente). */
export function somarDias(iso, dias) {
  const [ano, mes, dia] = iso.split('-').map(Number)
  return dataLocalISO(new Date(ano, mes - 1, dia + dias))
}

export function inicioDoMes(iso) {
  return `${iso.slice(0, 8)}01`
}

/** "2026-11-05" -> "05/11" (ou "05/11/2026" com ano=true). */
export function formatarData(iso, { ano = false } = {}) {
  const [a, m, d] = iso.split('-')
  return ano ? `${d}/${m}/${a}` : `${d}/${m}`
}
