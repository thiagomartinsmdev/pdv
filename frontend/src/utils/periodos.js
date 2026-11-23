import { dataLocalISO, inicioDoMes, somarDias } from './datas.js'

// Atalhos de período usados nos filtros de vendas e relatórios.
export const PRESETS_PERIODO = [
  { id: 'hoje', rotulo: 'Hoje', calcular: (hoje) => [hoje, hoje] },
  { id: '7d', rotulo: '7 dias', calcular: (hoje) => [somarDias(hoje, -6), hoje] },
  { id: '30d', rotulo: '30 dias', calcular: (hoje) => [somarDias(hoje, -29), hoje] },
  { id: 'mes', rotulo: 'Este mês', calcular: (hoje) => [inicioDoMes(hoje), hoje] },
]

/** periodoDoPreset('7d') -> { inicio: 'AAAA-MM-DD', fim: 'AAAA-MM-DD' } */
export function periodoDoPreset(id, hoje = dataLocalISO()) {
  const [inicio, fim] = PRESETS_PERIODO.find((p) => p.id === id).calcular(hoje)
  return { inicio, fim }
}

/** Qual atalho corresponde ao período (ou undefined, se for personalizado). */
export function presetDoPeriodo(periodo, hoje = dataLocalISO()) {
  return PRESETS_PERIODO.find((p) => {
    const [inicio, fim] = p.calcular(hoje)
    return inicio === periodo.inicio && fim === periodo.fim
  })
}
