"""A loja inteira em UM processo — porta 8000.

Três módulos no mesmo código: Catálogo, Estoque e Pedidos.
Eles conversam por chamada de função e guardam tudo no mesmo banco: dados/monolito.json.

Rotas:
  /produto/<id>     nome, preço e quantidade em estoque
  /comprar/<id>     compra uma unidade
  /relatorio        pedidos confirmados x baixas de estoque
  /bug/estoque      simula um bug fatal no módulo de Estoque
"""
import time

from base import Banco, cair_em_breve, servir

DESCONTO = 10       # % de desconto em todos os produtos (experimento 1)
TEMPO_DE_SUBIDA = 10  # simulado: o monolito carrega todos os módulos ao subir

banco = Banco("monolito.json", {"estoque": {"1": 5, "2": 5, "3": 5}, "baixas": 0, "pedidos": []})

# ---------- módulo Catálogo ----------
PRODUTOS = {"1": ("Teclado mecânico", 250.0), "2": ("Mouse sem fio", 90.0), "3": ("Monitor 24 pol", 900.0)}


def catalogo_buscar(pid):
    nome, preco = PRODUTOS[pid]
    return {"id": pid, "nome": nome, "preco": round(preco * (1 - DESCONTO / 100), 2)}


# ---------- módulo Estoque ----------
def estoque_consultar(pid):
    return banco.dados["estoque"][pid]


def estoque_baixar(pid):
    if banco.dados["estoque"][pid] <= 0:
        return False
    banco.dados["estoque"][pid] -= 1
    banco.dados["baixas"] += 1
    return True


# ---------- módulo Pedidos ----------
def pedidos_comprar(pid):
    produto = catalogo_buscar(pid)
    with banco.trava:
        if not estoque_baixar(pid):
            return 409, {"erro": "sem estoque"}
        pedido = {
            "numero": len(banco.dados["pedidos"]) + 1,
            "produto": produto["nome"],
            "valor": produto["preco"],
            "status": "confirmado",
        }
        banco.dados["pedidos"].append(pedido)
        banco.salvar()  # uma gravação só: pedido e estoque mudam juntos
    return {"pedido": pedido}


# ---------- rotas ----------
def produto(pid):
    inicio = time.perf_counter()
    dados = {**catalogo_buscar(pid), "em_estoque": estoque_consultar(pid)}
    dados["tempo_interno_ms"] = round((time.perf_counter() - inicio) * 1000, 3)
    return dados


def relatorio():
    confirmados = sum(1 for p in banco.dados["pedidos"] if p["status"] == "confirmado")
    baixas = banco.dados["baixas"]
    return {
        "pedidos_confirmados": confirmados,
        "pedidos_pendentes": 0,
        "baixas_de_estoque": baixas,
        "consistente": confirmados == baixas,
    }


def bug(modulo="estoque"):
    cair_em_breve()
    return {"aviso": f"bug fatal no módulo {modulo}: o processo vai cair em instantes"}


if __name__ == "__main__":
    servir("monolito", 8000,
           {"produto": produto, "comprar": pedidos_comprar, "relatorio": relatorio, "bug": bug},
           tempo_de_subida=TEMPO_DE_SUBIDA)
