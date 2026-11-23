import { formatarReais, paraCentavos } from '../../utils/dinheiro.js'
import { subtotalDoItem } from './carrinho.js'

/**
 * Carrinho da venda em andamento, em linhas compactas (cabe na coluna da direita).
 * O último item (o que o F4 remove) fica destacado.
 */
export default function ListaItens({ itens, aoAlterarQuantidade, aoRemover }) {
  if (itens.length === 0) {
    return (
      <div className="lista-itens lista-itens--vazia">
        <span className="lista-itens__icone" aria-hidden="true" />
        <p className="lista-itens__titulo">Bipe o primeiro produto</p>
        <p className="texto-suave">
          Use o leitor, digite o código ou o nome, ou toque num produto da grade.
        </p>
      </div>
    )
  }

  return (
    <ol className="lista-itens" aria-label="Itens da venda">
      {/* "key" ajuda o React a saber qual linha mudou entre uma renderização e outra. */}
      {itens.map((item, indice) => (
        <li
          key={item.produto.id}
          className={`item-carrinho${indice === itens.length - 1 ? ' item-carrinho--ultimo' : ''}`}
        >
          <div className="item-carrinho__info">
            <span className="item-carrinho__nome">{item.produto.nome}</span>
            <span className="item-carrinho__unitario">
              {formatarReais(paraCentavos(item.produto.preco))} un.
            </span>
          </div>

          <div className="item-carrinho__controles">
            <div className="quantidade">
              <button
                type="button"
                className="btn btn--secundario btn--icone"
                onClick={() => aoAlterarQuantidade(item, item.quantidade - 1)}
                aria-label={`Diminuir ${item.produto.nome}`}
              >
                −
              </button>
              <span>{item.quantidade}</span>
              <button
                type="button"
                className="btn btn--secundario btn--icone"
                onClick={() => aoAlterarQuantidade(item, item.quantidade + 1)}
                aria-label={`Aumentar ${item.produto.nome}`}
              >
                +
              </button>
            </div>
            <strong className="item-carrinho__subtotal">
              {formatarReais(subtotalDoItem(item))}
            </strong>
            <button
              type="button"
              className="btn btn--fantasma btn--icone"
              onClick={() => aoRemover(item)}
              aria-label={`Remover ${item.produto.nome}`}
            >
              ✕
            </button>
          </div>
        </li>
      ))}
    </ol>
  )
}
