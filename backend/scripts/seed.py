"""Popula o banco com dados de exemplo: um admin, um operador e 20 produtos.

Uso (dentro da pasta backend/, com o venv ativo):
    python -m scripts.seed

Pode ser executado várias vezes: registros que já existem (mesmo e-mail ou
mesmo código de barras) são mantidos como estão.
"""

from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.core.security import gerar_hash_senha
from app.models import PerfilUsuario, Produto, Usuario

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

# (nome, código de barras EAN-13, preço, estoque)
# Preços como string para o Decimal ser exato (Decimal(0.1) herdaria o erro do float).
PRODUTOS = [
    ("Pão francês (unidade)", "7891000000014", "0.90", 500),
    ("Pão de forma tradicional 500g", "7891000000021", "8.49", 40),
    ("Pão de queijo (unidade)", "7891000000038", "1.50", 200),
    ("Bolo de fubá (fatia)", "7891000000045", "4.50", 30),
    ("Sonho de creme", "7891000000052", "6.00", 25),
    ("Croissant", "7891000000069", "7.50", 20),
    ("Leite integral 1L", "7891000000076", "5.29", 60),
    ("Café torrado e moído 500g", "7891000000083", "18.90", 30),
    ("Açúcar refinado 1kg", "7891000000090", "4.99", 50),
    ("Manteiga com sal 200g", "7891000000106", "12.90", 25),
    ("Queijo muçarela fatiado 150g", "7891000000113", "9.90", 20),
    ("Presunto fatiado 150g", "7891000000120", "7.90", 20),
    ("Ovos brancos (dúzia)", "7891000000137", "11.90", 30),
    ("Refrigerante de cola 2L", "7891000000144", "9.99", 40),
    ("Suco de laranja 1L", "7891000000151", "8.50", 25),
    ("Água mineral 500ml", "7891000000168", "2.50", 100),
    ("Biscoito recheado de chocolate 130g", "7891000000175", "3.79", 60),
    ("Achocolatado em pó 400g", "7891000000182", "8.90", 30),
    ("Arroz branco tipo 1 5kg", "7891000000199", "27.90", 20),
    ("Feijão carioca 1kg", "7891000000205", "8.79", 25),
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


def criar_produtos(db: Session) -> int:
    codigos_existentes = set(db.scalars(select(Produto.codigo_barras)))
    novos = [
        Produto(
            nome=nome,
            codigo_barras=codigo,
            preco=Decimal(preco),
            quantidade_estoque=estoque,
        )
        for nome, codigo, preco, estoque in PRODUTOS
        if codigo not in codigos_existentes
    ]
    db.add_all(novos)
    return len(novos)


def executar_seed(db: Session) -> None:
    usuarios_criados = criar_usuarios(db)
    produtos_criados = criar_produtos(db)
    db.commit()

    print(f"Usuários criados: {usuarios_criados} (já existentes foram mantidos)")
    print(f"Produtos criados: {produtos_criados} (já existentes foram mantidos)")
    print()
    print("Usuários de teste:")
    for dados in USUARIOS:
        print(f"  {dados['perfil']:<9} {dados['email']:<18} senha: {dados['senha']}")


def main() -> None:
    with SessionLocal() as db:
        executar_seed(db)


if __name__ == "__main__":
    main()
