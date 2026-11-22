import { formatarReais, paraCentavos } from '../../utils/dinheiro.js'
import { subtotalDoItem } from './carrinho.js'

/** Tabela com os itens da venda em andamento. */
export default function ListaItens({ itens, aoAlterarQuantidade, aoRemover }) {
  if (itens.length === 0) {
    return (
      <div className="lista-itens lista-itens--vazia">
        <p>Nenhum item na venda.</p>
        <p className="texto-suave">
          Passe o código de barras no leitor ou digite o código ou o nome do produto.
        </p>
      </div>
    )
  }

  return (
    <div className="lista-itens">
      <table className="tabela tabela--itens">
        <thead>
          <tr>
            <th className="col-num">#</th>
            <th>Produto</th>
            <th className="col-qtd">Qtd.</th>
            <th className="col-valor">Unitário</th>
            <th className="col-valor">Subtotal</th>
            <th className="col-acoes">
              <span className="sr-only">Ações</span>
            </th>
          </tr>
        </thead>
        <tbody>
          {/* "key" ajuda o React a saber qual linha mudou entre uma renderização e outra. */}
          {itens.map((item, indice) => (
            <tr key={item.produto.id} className={indice === itens.length - 1 ? 'linha--ultima' : ''}>
              <td className="col-num">{indice + 1}</td>
              <td>
                <div className="item__nome">{item.produto.nome}</div>
                <div className="item__codigo">{item.produto.codigo_barras}</div>
              </td>
              <td className="col-qtd">
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
              </td>
              <td className="col-valor">{formatarReais(paraCentavos(item.produto.preco))}</td>
              <td className="col-valor">
                <strong>{formatarReais(subtotalDoItem(item))}</strong>
              </td>
              <td className="col-acoes">
                <button
                  type="button"
                  className="btn btn--fantasma btn--icone"
                  onClick={() => aoRemover(item)}
                  aria-label={`Remover ${item.produto.nome}`}
                >
                  ✕
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
