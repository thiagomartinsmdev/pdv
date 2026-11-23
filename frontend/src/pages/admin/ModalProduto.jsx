import { useState } from 'react'

import { listarCategorias } from '../../api/categorias.js'
import { atualizarProduto, criarProduto } from '../../api/produtos.js'
import CampoDinheiro from '../../components/CampoDinheiro.jsx'
import ImagemProduto from '../../components/ImagemProduto.jsx'
import Modal from '../../components/Modal.jsx'
import { useConsulta } from '../../hooks/useConsulta.js'
import { centavosParaApi, centavosParaTexto, lerValorDigitado, paraCentavos } from '../../utils/dinheiro.js'
import { mensagemDeErro } from '../../utils/erros.js'
import { ehFotoDoServidor, ehLinkDeImagemValido } from '../../utils/links.js'

/** Cadastro (produto = null) ou edição de um produto. */
export default function ModalProduto({ produto, aoSalvar, aoFechar }) {
  const editando = Boolean(produto)
  // O estado inicial vem do produto (na edição) ou fica vazio (no cadastro).
  const [campos, setCampos] = useState(() => ({
    nome: produto?.nome ?? '',
    codigo_barras: produto?.codigo_barras ?? '',
    preco: produto ? centavosParaTexto(paraCentavos(produto.preco)) : '',
    quantidade_estoque: String(produto?.quantidade_estoque ?? 0),
    categoria_id: produto?.categoria_id ? String(produto.categoria_id) : '',
    imagem_url: produto?.imagem_url ?? '',
  }))
  const [erro, setErro] = useState('')
  const [enviando, setEnviando] = useState(false)
  // Link cuja imagem não carregou (para avisar sem bloquear o cadastro).
  const [linkComFalha, setLinkComFalha] = useState(null)

  // Inclui as inativas para mostrar corretamente a categoria atual de um produto antigo.
  const { dados: categorias } = useConsulta(() => listarCategorias({ incluir_inativas: true }), [])
  const opcoes = (categorias ?? []).filter(
    (c) => c.ativo || String(c.id) === campos.categoria_id,
  )

  const link = campos.imagem_url.trim()
  const linkInvalido = link !== '' && !ehLinkDeImagemValido(link)
  const linkPrevia = link && !linkInvalido ? link : null

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
    if (linkInvalido) {
      setErro('O link da imagem deve começar com http:// ou https://.')
      return
    }

    const dados = {
      nome: campos.nome.trim(),
      codigo_barras: campos.codigo_barras.trim(),
      preco: centavosParaApi(preco),
      quantidade_estoque: estoque,
      // Vazio = sem categoria / sem imagem.
      categoria_id: campos.categoria_id ? Number(campos.categoria_id) : null,
      imagem_url: link || null,
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

        <div className="formulario__linha">
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
          <label className="campo">
            <span>Categoria</span>
            <select
              value={campos.categoria_id}
              onChange={(e) => alterar('categoria_id', e.target.value)}
            >
              <option value="">Sem categoria</option>
              {opcoes.map((categoria) => (
                <option key={categoria.id} value={String(categoria.id)}>
                  {categoria.nome}
                  {categoria.ativo ? '' : ' (desativada)'}
                </option>
              ))}
            </select>
          </label>
        </div>

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

        <div className="campo-imagem">
          <label className="campo">
            <span>Link da imagem (opcional)</span>
            {/* type="text": o navegador recusaria o caminho de uma foto do servidor num type="url". */}
            <input
              type="text"
              inputMode="url"
              value={campos.imagem_url}
              onChange={(e) => alterar('imagem_url', e.target.value)}
              placeholder="https://..."
              maxLength={500}
              aria-invalid={linkInvalido}
            />
            {linkInvalido && (
              <small className="campo__erro">O link deve começar com http:// ou https://.</small>
            )}
            {ehFotoDoServidor(link) && (
              <small className="texto-suave texto-pequeno">
                Foto guardada no servidor. Apague o campo para remover ou cole um link para trocar.
              </small>
            )}
            {linkPrevia && linkComFalha === linkPrevia && (
              <small className="campo__aviso">
                A imagem não carregou. Confira o link; sem ela, o caixa mostra a inicial do nome.
              </small>
            )}
          </label>

          <div className="campo-imagem__previa">
            <span className="texto-suave texto-pequeno">Pré-visualização</span>
            <ImagemProduto
              // key: um link novo recria a prévia e zera o estado de "falhou".
              key={linkPrevia ?? 'sem-imagem'}
              nome={campos.nome || '?'}
              url={linkPrevia}
              tamanho={96}
              aoFalhar={() => setLinkComFalha(linkPrevia)}
            />
          </div>
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
