import { describe, expect, it } from 'vitest'

import { periodoDoPreset, presetDoPeriodo } from './periodos.js'

const HOJE = '2026-11-22'

describe('periodos', () => {
  it.each([
    ['hoje', { inicio: '2026-11-22', fim: '2026-11-22' }],
    ['7d', { inicio: '2026-11-16', fim: '2026-11-22' }], // 7 dias contando hoje
    ['30d', { inicio: '2026-10-24', fim: '2026-11-22' }],
    ['mes', { inicio: '2026-11-01', fim: '2026-11-22' }],
  ])('%s', (id, esperado) => {
    expect(periodoDoPreset(id, HOJE)).toEqual(esperado)
  })

  it('reconhece o atalho de um período, ou nenhum se for personalizado', () => {
    expect(presetDoPeriodo({ inicio: '2026-11-16', fim: '2026-11-22' }, HOJE)?.id).toBe('7d')
    expect(presetDoPeriodo({ inicio: '2026-11-10', fim: '2026-11-12' }, HOJE)).toBeUndefined()
  })
})
