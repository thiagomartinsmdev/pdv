"""Popula o banco com dados de exemplo: um admin, um operador, 6 categorias e 20 produtos.

Uso (dentro da pasta backend/, com o venv ativo):
    python -m scripts.seed

Pode ser executado várias vezes: registros que já existem (mesmo e-mail, mesmo
código de barras ou mesmo nome de categoria) são mantidos como estão. A categoria
só é preenchida nos produtos que ainda não têm uma.
"""

from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.core.security import gerar_hash_senha
from app.models import Categoria, PerfilUsuario, Produto, Usuario

USUARIOS = [
    {
        "nome": "Administrador",
        "email": "admin@pdv.com",
        "senha": "admin123",
        "perfil": PerfilUsuario.ADMIN,
    },
    {
        "nome": "Operador de Caixa",
        "email": "operador@pdv.com",
        "senha": "operador123",
        "perfil": PerfilUsuario.OPERADOR,
    },
]

# Categorias na ordem das abas do caixa.
CATEGORIAS = ["Pães", "Salgados", "Doces", "Bebidas", "Frios", "Mercearia"]

# (nome, código de barras EAN-13, preço, estoque, categoria)
# Preços como string para o Decimal ser exato (Decimal(0.1) herdaria o erro do float).
PRODUTOS = [
    ("Pão francês (unidade)", "7891000000014", "0.90", 500, "Pães"),
    ("Pão de forma tradicional 500g", "7891000000021", "8.49", 40, "Pães"),
    ("Pão de queijo (unidade)", "7891000000038", "1.50", 200, "Salgados"),
    ("Bolo de fubá (fatia)", "7891000000045", "4.50", 30, "Doces"),
    ("Sonho de creme", "7891000000052", "6.00", 25, "Doces"),
    ("Croissant", "7891000000069", "7.50", 20, "Pães"),
    ("Leite integral 1L", "7891000000076", "5.29", 60, "Bebidas"),
    ("Café torrado e moído 500g", "7891000000083", "18.90", 30, "Mercearia"),
    ("Açúcar refinado 1kg", "7891000000090", "4.99", 50, "Mercearia"),
    ("Manteiga com sal 200g", "7891000000106", "12.90", 25, "Frios"),
    ("Queijo muçarela fatiado 150g", "7891000000113", "9.90", 20, "Frios"),
    ("Presunto fatiado 150g", "7891000000120", "7.90", 20, "Frios"),
    ("Ovos brancos (dúzia)", "7891000000137", "11.90", 30, "Mercearia"),
    ("Refrigerante de cola 2L", "7891000000144", "9.99", 40, "Bebidas"),
    ("Suco de laranja 1L", "7891000000151", "8.50", 25, "Bebidas"),
    ("Água mineral 500ml", "7891000000168", "2.50", 100, "Bebidas"),
    ("Biscoito recheado de chocolate 130g", "7891000000175", "3.79", 60, "Doces"),
    ("Achocolatado em pó 400g", "7891000000182", "8.90", 30, "Mercearia"),
    ("Arroz branco tipo 1 5kg", "7891000000199", "27.90", 20, "Mercearia"),
    ("Feijão carioca 1kg", "7891000000205", "8.79", 25, "Mercearia"),
]


def criar_usuarios(db: Session) -> int:
    emails_existentes = set(db.scalars(select(Usuario.email)))
    novos = [
        Usuario(
            nome=dados["nome"],
            email=dados["email"],
            senha_hash=gerar_hash_senha(dados["senha"]),
            perfil=dados["perfil"],
        )
        for dados in USUARIOS
        if dados["email"] not in emails_existentes
    ]
    db.add_all(novos)
    return len(novos)


def criar_categorias(db: Session) -> dict[str, Categoria]:
    """Cria as categorias que faltam e devolve todas pelo nome."""
    existentes = {c.nome: c for c in db.scalars(select(Categoria))}
    for ordem, nome in enumerate(CATEGORIAS, start=1):
        if nome not in existentes:
            existentes[nome] = Categoria(nome=nome, ordem=ordem * 10)
            db.add(existentes[nome])
    db.flush()  # gera os ids, ainda dentro da transação
    return existentes


def criar_produtos(db: Session, categorias: dict[str, Categoria]) -> tuple[int, int]:
    """Cria os produtos que faltam e preenche a categoria dos que ainda não têm.

    Devolve (produtos criados, produtos associados a uma categoria).
    """
    existentes = {p.codigo_barras: p for p in db.scalars(select(Produto))}
    criados = associados = 0
    for nome, codigo, preco, estoque, categoria in PRODUTOS:
        produto = existentes.get(codigo)
        if produto is None:
            db.add(
                Produto(
                    nome=nome,
                    codigo_barras=codigo,
                    preco=Decimal(preco),
                    quantidade_estoque=estoque,
                    categoria=categorias[categoria],
                )
            )
            criados += 1
        elif produto.categoria_id is None:
            # Não sobrescreve uma categoria escolhida pelo admin.
            produto.categoria = categorias[categoria]
            associados += 1
    return criados, associados


def executar_seed(db: Session) -> None:
    usuarios_criados = criar_usuarios(db)
    total_categorias = len(db.scalars(select(Categoria.id)).all())
    categorias = criar_categorias(db)
    produtos_criados, produtos_associados = criar_produtos(db, categorias)
    db.commit()

    print(f"Usuários criados: {usuarios_criados} (já existentes foram mantidos)")
    print(f"Categorias criadas: {len(categorias) - total_categorias}")
    print(f"Produtos criados: {produtos_criados} (já existentes foram mantidos)")
    print(f"Produtos existentes associados a uma categoria: {produtos_associados}")
    print()
    print("Usuários de teste:")
    for dados in USUARIOS:
        print(f"  {dados['perfil']:<9} {dados['email']:<18} senha: {dados['senha']}")


def main() -> None:
    with SessionLocal() as db:
        executar_seed(db)


if __name__ == "__main__":
    main()
