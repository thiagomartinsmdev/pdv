import { PRESETS_PERIODO, periodoDoPreset, presetDoPeriodo } from '../utils/periodos.js'

/**
 * Seleção de período: atalhos (Hoje, 7 dias...) e datas personalizadas.
 * Componente "controlado": quem usa guarda o período e recebe as mudanças em aoMudar.
 */
export default function FiltroPeriodo({ periodo, aoMudar }) {
  const ativo = presetDoPeriodo(periodo)

  return (
    <div className="filtro-periodo">
      <div className="filtro-periodo__presets" role="group" aria-label="Período">
        {PRESETS_PERIODO.map((preset) => (
          <button
            key={preset.id}
            type="button"
            className={`chip${ativo?.id === preset.id ? ' chip--ativo' : ''}`}
            aria-pressed={ativo?.id === preset.id}
            onClick={() => aoMudar(periodoDoPreset(preset.id))}
          >
            {preset.rotulo}
          </button>
        ))}
      </div>

      <div className="filtro-periodo__datas">
        <label>
          <span className="sr-only">Data inicial</span>
          <input
            type="date"
            value={periodo.inicio}
            max={periodo.fim}
            onChange={(e) => e.target.value && aoMudar({ ...periodo, inicio: e.target.value })}
          />
        </label>
        <span className="texto-suave">até</span>
        <label>
          <span className="sr-only">Data final</span>
          <input
            type="date"
            value={periodo.fim}
            min={periodo.inicio}
            onChange={(e) => e.target.value && aoMudar({ ...periodo, fim: e.target.value })}
          />
        </label>
      </div>
    </div>
  )
}
