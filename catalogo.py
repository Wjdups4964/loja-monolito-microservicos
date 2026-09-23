"""Serviço de Catálogo — porta 9001.

Dono dos nomes e preços. Não tem banco: os produtos estão no código.

Rota:
  /produtos/<id>
"""
from base import servir

DESCONTO = 10         # % de desconto em todos os produtos (experimento 1)
TEMPO_DE_SUBIDA = 15  # simulado

PRODUTOS = {"1": ("Teclado mecânico", 250.0), "2": ("Mouse sem fio", 90.0), "3": ("Monitor 24 pol", 900.0)}


def produtos(pid):
    nome, preco = PRODUTOS[pid]
    return {"id": pid, "nome": nome, "preco": round(preco * (1 - DESCONTO / 100), 2)}


if __name__ == "__main__":
    servir("catálogo", 9001, {"produtos": produtos}, tempo_de_subida=TEMPO_DE_SUBIDA)
