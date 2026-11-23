import { describe, expect, it } from 'vitest'

import { ehLinkDeImagemValido } from './links.js'

describe('ehLinkDeImagemValido', () => {
  it.each(['https://exemplo.com/pao.jpg', 'http://cdn.exemplo.com.br/a.png', '  https://x.io/b  '])(
    'aceita %s',
    (link) => {
      expect(ehLinkDeImagemValido(link)).toBe(true)
    },
  )

  it.each([
    '',
    'javascript:alert(1)',
    'ftp://exemplo.com/a.jpg',
    'exemplo.com/a.jpg',
    'data:image/png;base64,AAAA',
    `https://exemplo.com/${'a'.repeat(500)}`,
  ])('recusa "%s"', (link) => {
    expect(ehLinkDeImagemValido(link)).toBe(false)
  })
})
