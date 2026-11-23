import { describe, expect, it } from 'vitest'

import { ehFotoDoServidor, ehLinkDeImagemValido, enderecoDaImagem } from './links.js'

const FOTO = '/uploads/produtos/3f2a9c1b7e4d4a6f.jpg'

describe('ehLinkDeImagemValido', () => {
  it.each([
    'https://exemplo.com/pao.jpg',
    'http://cdn.exemplo.com.br/a.png',
    '  https://x.io/b  ',
    FOTO,
  ])('aceita %s', (link) => {
    expect(ehLinkDeImagemValido(link)).toBe(true)
  })

  it.each([
    '',
    'javascript:alert(1)',
    'ftp://exemplo.com/a.jpg',
    'exemplo.com/a.jpg',
    'data:image/png;base64,AAAA',
    `https://exemplo.com/${'a'.repeat(500)}`,
    '/uploads/produtos/../../app/main.py',
    '/uploads/outra/3f2a9c1b7e4d4a6f.jpg',
    '/uploads/produtos/3f2a9c1b7e4d4a6f.gif',
  ])('recusa "%s"', (link) => {
    expect(ehLinkDeImagemValido(link)).toBe(false)
  })
})

describe('ehFotoDoServidor', () => {
  it('reconhece só o caminho de fotos do servidor', () => {
    expect(ehFotoDoServidor(FOTO)).toBe(true)
    expect(ehFotoDoServidor('https://exemplo.com/uploads/produtos/3f2a9c1b7e4d4a6f.jpg')).toBe(false)
    expect(ehFotoDoServidor(null)).toBe(false)
  })
})

describe('enderecoDaImagem', () => {
  it('põe o endereço da API na frente das fotos do servidor', () => {
    expect(enderecoDaImagem(FOTO, 'http://localhost:8000')).toBe(`http://localhost:8000${FOTO}`)
  })

  it('mantém links externos e vazios como estão', () => {
    expect(enderecoDaImagem('https://exemplo.com/a.jpg', 'http://api')).toBe('https://exemplo.com/a.jpg')
    expect(enderecoDaImagem(null)).toBe(null)
    expect(enderecoDaImagem('')).toBe('')
  })
})
