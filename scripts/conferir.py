"""Conferências sem o Power BI Desktop.

1. Todo campo citado no relatório existe no modelo (tabela, coluna ou medida).
2. Os 5 números de controle, somados direto dos CSVs, para comparar com o relatório (docs/TESTES.md).
Rode: python scripts/conferir.py
"""
import csv
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "scripts"))
import gerar_modelo as m  # noqa: E402

# 1. Campos do relatório x modelo
colunas = defaultdict(set)
for t in m.TABELAS:
    for c in t["colunas"]:
        colunas[t["nome"]].add(c[0])
    for d in t.get("derivadas", []):
        colunas[t["nome"]].add(d[0])
colunas["Data"] |= {"Data", "Ano", "MesNum", "Mes", "AnoMes", "InicioSemana", "DiaUtil", "Feriado", "Ultimas12Semanas"}
medidas = {x[1] for x in m.MEDIDAS}

faltando = set()
for f in (RAIZ / "Painel Operacoes.Report" / "definition").rglob("*.json"):
    texto = f.read_text(encoding="utf-8")
    for ent, prop in re.findall(r'"Entity": "([^"]+)"\}\}, "Property": "([^"]+)"', texto.replace("\n", "").replace("  ", "")):
        if ent == "_Medidas":
            if prop not in medidas:
                faltando.add(f"[{prop}]")
        elif prop not in colunas.get(ent, set()):
            faltando.add(f"{ent}[{prop}]")
# medidas citadas dentro de outras medidas
for _, nome, expr, _, _ in m.MEDIDAS:
    for ref in re.findall(r"(?<![\w\]])\[([^\]]+)\]", expr):
        if ref not in medidas and not any(ref in cs for cs in colunas.values()):
            faltando.add(f"[{ref}] (em '{nome}')")
print("Campos inexistentes:", sorted(faltando) or "nenhum")


# 2. Números de controle
def ler(n):
    with open(RAIZ / "data" / n, encoding="utf-8") as f:
        return list(csv.DictReader(f, delimiter=";"))


sol, notas, ncs, prod = ler("solicitacoes.csv"), ler("notas.csv"), ler("nao_conformidades.csv"), ler("producao_diaria.csv")
valor_aprovado = sum(float(s["ValorTotal"]) for s in sol if s["Status"] == "Aprovado")
set_aprov = sum(float(s["ValorTotal"]) for s in sol if s["Status"] == "Aprovado" and s["DataCriacao"].startswith("2026-09"))
pct_div = sum(1 for n in notas if n["Resultado"] == "Divergente") / len(notas)
refugo = sum(int(p["Refugo"]) for p in prod) / (sum(int(p["PecasBoas"]) for p in prod) + sum(int(p["Refugo"]) for p in prod))
aprov = [s for s in sol if s["Status"] == "Aprovado"]
sla = sum(1 for s in aprov if s["Atrasada"] == "Não") / len(aprov)
controle = [
    ("Valor aprovado (todo o período)", f"R$ {valor_aprovado:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")),
    ("Valor aprovado · mês (set/2026)", f"R$ {set_aprov:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")),
    ("% notas com divergência", f"{pct_div * 100:.1f}%".replace(".", ",")),
    ("% aprovadas no SLA", f"{sla * 100:.1f}%".replace(".", ",")),
    ("Índice de refugo %", f"{refugo * 100:.2f}%".replace(".", ",")),
    ("NCs (todo o período)", str(len(ncs))),
]
for k, v in controle:
    print(f"{k}: {v}")
json.dump(dict(controle), open(RAIZ / "docs" / "numeros-de-controle.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2)
sys.exit(1 if faltando else 0)
