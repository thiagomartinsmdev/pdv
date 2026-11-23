import { describe, expect, it } from 'vitest'

import { dataLocalISO, formatarData, inicioDoMes, somarDias } from './datas.js'

describe('datas de calendário', () => {
  it('usa a data local, e não UTC', () => {
    // 23h do dia 05 em qualquer fuso continua sendo dia 05 para o usuário.
    expect(dataLocalISO(new Date(2026, 10, 5, 23, 30))).toBe('2026-11-05')
  })

  it('soma dias atravessando mês e ano', () => {
    expect(somarDias('2026-11-30', 1)).toBe('2026-12-01')
    expect(somarDias('2026-12-31', 1)).toBe('2027-01-01')
    expect(somarDias('2026-03-01', -1)).toBe('2026-02-28')
  })

  it('início do mês e formatação', () => {
    expect(inicioDoMes('2026-11-22')).toBe('2026-11-01')
    expect(formatarData('2026-11-05')).toBe('05/11')
    expect(formatarData('2026-11-05', { ano: true })).toBe('05/11/2026')
  })
})
