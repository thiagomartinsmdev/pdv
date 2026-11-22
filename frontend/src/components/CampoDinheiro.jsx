import { lerValorDigitado } from '../utils/dinheiro.js'

/**
 * Input de valor em reais. Aceita "10", "10,50" ou "10.50".
 * O valor é texto (o que a pessoa digitou); use lerValorDigitado() para obter centavos.
 *
 * No React 19, "ref" pode ser recebida como uma prop comum: o pai passa uma ref e
 * ela chega ao <input> interno (por exemplo, para dar foco nele).
 */
export default function CampoDinheiro({ rotulo, valor, aoMudar, ref, ...resto }) {
  const invalido = valor !== '' && lerValorDigitado(valor) === null

  return (
    <label className="campo">
      <span>{rotulo}</span>
      <div className={`campo-dinheiro${invalido ? ' campo-dinheiro--invalido' : ''}`}>
        <span className="campo-dinheiro__prefixo">R$</span>
        <input
          ref={ref}
          type="text"
          inputMode="decimal"
          autoComplete="off"
          value={valor}
          onChange={(evento) => aoMudar(evento.target.value)}
          aria-invalid={invalido}
          {...resto}
        />
      </div>
      {invalido && <small className="campo__erro">Valor inválido. Use o formato 10,50.</small>}
    </label>
  )
}
