// Cores dos gráficos.
//
// As cores são definidas UMA vez, como variáveis no :root do global.css. O Recharts
// desenha em SVG e recebe as cores como valores prontos (não entende var(--...)),
// então elas são lidas do CSS na hora de desenhar.

function lerVariavel(nome) {
  return getComputedStyle(document.documentElement).getPropertyValue(nome).trim()
}

export function coresDoGrafico() {
  return {
    serie: lerVariavel('--cor-grafico-serie'),
    serieDestaque: lerVariavel('--cor-grafico-destaque'), // coluna sob o mouse
    faixaHover: lerVariavel('--cor-primaria-clara'), // faixa do dia sob o mouse
    grade: lerVariavel('--cor-grafico-grade'),
    eixo: lerVariavel('--cor-grafico-eixo'),
    textoEixo: lerVariavel('--cor-grafico-texto'),
  }
}
