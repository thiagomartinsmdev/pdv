import { useState } from 'react'

import { atualizarCategoria, criarCategoria } from '../../api/categorias.js'
import Modal from '../../components/Modal.jsx'
import { mensagemDeErro } from '../../utils/erros.js'

/** Cadastro (categoria = null) ou edição de uma categoria. */
export default function ModalCategoria({ categoria, sugestaoOrdem, aoSalvar, aoFechar }) {
  const editando = Boolean(categoria)
  const [nome, setNome] = useState(categoria?.nome ?? '')
  const [ordem, setOrdem] = useState(String(categoria?.ordem ?? sugestaoOrdem))
  const [erro, setErro] = useState('')
  const [enviando, setEnviando] = useState(false)

  async function aoEnviar(evento) {
    evento.preventDefault()
    const numeroOrdem = Number(ordem)
    if (!Number.isInteger(numeroOrdem) || numeroOrdem < 0) {
      setErro('A ordem deve ser um número inteiro maior ou igual a zero.')
      return
    }
    const dados = { nome: nome.trim(), ordem: numeroOrdem }

    setEnviando(true)
    setErro('')
    try {
      const salva = editando
        ? await atualizarCategoria(categoria.id, dados)
        : await criarCategoria(dados)
      aoSalvar(salva)
    } catch (falha) {
      setErro(mensagemDeErro(falha))
      setEnviando(false)
    }
  }

  return (
    <Modal titulo={editando ? 'Editar categoria' : 'Nova categoria'} aoFechar={aoFechar} largura="pequena">
      <form className="formulario" onSubmit={aoEnviar}>
        {erro && (
          <div className="alerta alerta--erro" role="alert">
            {erro}
          </div>
        )}

        <label className="campo">
          <span>Nome</span>
          <input
            value={nome}
            onChange={(e) => setNome(e.target.value)}
            minLength={2}
            maxLength={60}
            required
            autoFocus
          />
        </label>

        <label className="campo">
          <span>Ordem da aba no caixa</span>
          <input
            type="number"
            min="0"
            max="9999"
            step="1"
            value={ordem}
            onChange={(e) => setOrdem(e.target.value)}
            required
          />
          <small className="texto-suave texto-pequeno">
            Menor número aparece primeiro. Use intervalos (10, 20, 30) para encaixar outras
            depois.
          </small>
        </label>

        <div className="botoes-lado-a-lado">
          <button type="button" className="btn btn--secundario" onClick={aoFechar}>
            Cancelar
          </button>
          <button type="submit" className="btn btn--primario" disabled={enviando}>
            {enviando ? 'Salvando...' : 'Salvar'}
          </button>
        </div>
      </form>
    </Modal>
  )
}
