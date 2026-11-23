import { useState } from 'react'

import { atualizarProduto, criarProduto } from '../../api/produtos.js'
import CampoDinheiro from '../../components/CampoDinheiro.jsx'
import Modal from '../../components/Modal.jsx'
import { centavosParaApi, centavosParaTexto, lerValorDigitado, paraCentavos } from '../../utils/dinheiro.js'
import { mensagemDeErro } from '../../utils/erros.js'

/** Cadastro (produto = null) ou edição de um produto. */
export default function ModalProduto({ produto, aoSalvar, aoFechar }) {
  const editando = Boolean(produto)
  // O estado inicial vem do produto (na edição) ou fica vazio (no cadastro).
  const [campos, setCampos] = useState(() => ({
    nome: produto?.nome ?? '',
    codigo_barras: produto?.codigo_barras ?? '',
    preco: produto ? centavosParaTexto(paraCentavos(produto.preco)) : '',
    quantidade_estoque: String(produto?.quantidade_estoque ?? 0),
  }))
  const [erro, setErro] = useState('')
  const [enviando, setEnviando] = useState(false)

  // Uma função só para todos os campos: "nome" atualiza campos.nome, e assim por diante.
  function alterar(nome, valor) {
    setCampos((atuais) => ({ ...atuais, [nome]: valor }))
  }

  async function aoEnviar(evento) {
    evento.preventDefault()
    const preco = lerValorDigitado(campos.preco)
    const estoque = Number(campos.quantidade_estoque)
    if (preco === null) {
      setErro('Informe um preço válido, por exemplo 8,49.')
      return
    }
    if (!Number.isInteger(estoque) || estoque < 0) {
      setErro('O estoque deve ser um número inteiro maior ou igual a zero.')
      return
    }

    const dados = {
      nome: campos.nome.trim(),
      codigo_barras: campos.codigo_barras.trim(),
      preco: centavosParaApi(preco),
      quantidade_estoque: estoque,
    }

    setEnviando(true)
    setErro('')
    try {
      const salvo = editando ? await atualizarProduto(produto.id, dados) : await criarProduto(dados)
      aoSalvar(salvo)
    } catch (falha) {
      setErro(mensagemDeErro(falha))
      setEnviando(false)
    }
  }

  return (
    <Modal titulo={editando ? 'Editar produto' : 'Novo produto'} aoFechar={aoFechar}>
      <form className="formulario" onSubmit={aoEnviar}>
        {erro && (
          <div className="alerta alerta--erro" role="alert">
            {erro}
          </div>
        )}

        <label className="campo">
          <span>Nome</span>
          <input
            value={campos.nome}
            onChange={(e) => alterar('nome', e.target.value)}
            minLength={2}
            maxLength={120}
            required
            autoFocus
          />
        </label>

        <label className="campo">
          <span>Código de barras</span>
          <input
            value={campos.codigo_barras}
            onChange={(e) => alterar('codigo_barras', e.target.value)}
            maxLength={50}
            inputMode="numeric"
            required
          />
        </label>

        <div className="formulario__linha">
          <CampoDinheiro
            rotulo="Preço"
            valor={campos.preco}
            aoMudar={(valor) => alterar('preco', valor)}
            placeholder="0,00"
            required
          />
          <label className="campo">
            <span>Estoque</span>
            <input
              type="number"
              min="0"
              step="1"
              value={campos.quantidade_estoque}
              onChange={(e) => alterar('quantidade_estoque', e.target.value)}
              required
            />
          </label>
        </div>

        {editando && (
          <p className="texto-suave texto-pequeno">
            Alterar o preço não muda as vendas já registradas: cada venda guarda o preço cobrado.
          </p>
        )}

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
