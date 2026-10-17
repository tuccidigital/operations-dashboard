"""Gera os dados fictícios do P05 a partir da lumina-seed (cópia em scripts/seed).

Rode na pasta do projeto: python scripts/gerar_dados.py
Semente fixa: o resultado é sempre o mesmo. Tudo é fictício (Lumina Componentes).

Saída em data/ (CSV com ; e ponto decimal, UTF-8):
  centros_custo, colaboradores, fornecedores, produtos, ativos, mapa_gerentes, feriados,
  solicitacoes, itens_solicitacao, aprovacoes, notas, inspecoes, nao_conformidades,
  orcamento_mensal, producao_diaria
"""
import csv
import random
from datetime import date, datetime, timedelta
from pathlib import Path

random.seed(20261016)
RAIZ = Path(__file__).resolve().parent.parent
SEED = RAIZ / "scripts" / "seed"  # cópia da lumina-seed (00-padroes), para o repositório ser autossuficiente
DATA = RAIZ / "data"
DATA.mkdir(exist_ok=True)

INICIO = date(2026, 1, 1)
FIM = date(2026, 9, 30)

FERIADOS = {
    date(2026, 1, 1): "Confraternização Universal",
    date(2026, 2, 16): "Carnaval",
    date(2026, 2, 17): "Carnaval",
    date(2026, 4, 3): "Sexta-feira Santa",
    date(2026, 4, 21): "Tiradentes",
    date(2026, 5, 1): "Dia do Trabalho",
    date(2026, 6, 4): "Corpus Christi",
    date(2026, 9, 7): "Independência do Brasil",
    date(2026, 10, 12): "Nossa Senhora Aparecida",
    date(2026, 11, 2): "Finados",
    date(2026, 11, 15): "Proclamação da República",
    date(2026, 11, 20): "Dia Nacional de Zumbi e da Consciência Negra",
    date(2026, 12, 25): "Natal",
}


def ler(nome):
    with open(SEED / nome, encoding="utf-8") as f:
        return list(csv.DictReader(f, delimiter=";"))


def grava(nome, cab, linhas):
    with open(DATA / nome, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f, delimiter=";")
        w.writerow(cab)
        w.writerows(linhas)


def dias_uteis(a, b):
    d = a
    while d <= b:
        if d.weekday() < 5 and d not in FERIADOS:
            yield d
        d += timedelta(days=1)


def peso_mes(m):  # sazonalidade leve: menos pedidos em julho
    return 0.7 if m == 7 else 1.0


def iso(dt):
    return dt.strftime("%Y-%m-%dT%H:%M:%S")


centros = ler("centros_custo.csv")
colabs = ler("colaboradores.csv")
fornecedores = ler("fornecedores.csv")
produtos = ler("produtos.csv")
alcadas = ler("alcadas.csv")

for nome in ["centros_custo.csv", "colaboradores.csv", "fornecedores.csv", "produtos.csv"]:
    linhas = ler(nome)
    grava(nome, list(linhas[0].keys()), [list(l.values()) for l in linhas])

colab = {c["Id"]: c for c in colabs}
gerente_cc = {c["Codigo"]: c["GerenteId"] for c in centros}
diretor_cc = {c["Codigo"]: c["DiretorId"] for c in centros}

grava("feriados.csv", ["Data", "Nome"], [(d.isoformat(), n) for d, n in sorted(FERIADOS.items())])
grava("mapa_gerentes.csv", ["Email", "CentroCusto"],
      [(colab[c["GerenteId"]]["Email"], c["Codigo"]) for c in centros]
      + [(colab[c["DiretorId"]]["Email"], c["Codigo"]) for c in centros])

# ---------------------------------------------------------------- P01 · Solicitações e aprovações
uteis = list(dias_uteis(INICIO, FIM))
orc_total = sum(int(c["OrcamentoMensal"]) for c in centros)
pesos_cc = [int(c["OrcamentoMensal"]) / orc_total for c in centros]


def cadeia(solicitante, cc, valor):
    gestor = colab[solicitante]["GestorId"] or diretor_cc[cc]
    if valor <= 5000:
        etapas = [gestor]
    elif valor <= 25000:
        etapas = [gestor, gerente_cc[cc]]
    else:
        etapas = [gerente_cc[cc], diretor_cc[cc]]
    out = []
    for e in etapas:
        e = sem_autoaprovacao(e, solicitante, cc)
        if not out or out[-1] != e:
            out.append(e)
    return out


def sem_autoaprovacao(e, solicitante, cc):
    """Ninguém aprova a própria solicitação: sobe um nível; no topo, vai para o outro diretor (mesma regra do P01)."""
    if e == solicitante:
        e = colab[e]["GestorId"] or diretor_cc[cc]
    if e == solicitante:
        e = next(d for d in sorted(set(diretor_cc.values()), key=int) if d != solicitante)
    return e


solicitacoes, itens, aprovacoes = [], [], []
seq = {"Compra": 0, "Reembolso": 0, "Férias": 0}
prefixo = {"Compra": "COM", "Reembolso": "REE", "Férias": "FER"}
n_alvo = 640
for i in range(n_alvo):
    dia = random.choice(uteis)
    if random.random() > peso_mes(dia.month):
        dia = random.choice(uteis)
    tipo = random.choices(["Compra", "Reembolso", "Férias"], [0.72, 0.18, 0.10])[0]
    cc = random.choices([c["Codigo"] for c in centros], pesos_cc)[0]
    pessoas = [c for c in colabs if c["CentroCusto"] == cc] or colabs
    solicitante = random.choice(pessoas)["Id"]
    criado = datetime.combine(dia, datetime.min.time()) + timedelta(hours=random.randint(8, 17), minutes=random.randint(0, 59))
    urgente = random.random() < 0.15
    fornecedor = ""
    valor = 0.0
    if tipo == "Compra":
        fornecedor = random.choice(fornecedores)["Id"]
        cand = [p for p in produtos if p["FornecedorPadraoId"] == fornecedor] or produtos
        for k in range(random.randint(1, 4)):
            p = random.choice(cand)
            preco = round(float(p["PrecoReferencia"]) * random.uniform(0.85, 1.15), 2)
            qtd = random.choice([1, 2, 4, 6, 10, 16, 24]) if float(p["PrecoReferencia"]) < 1000 else random.choice([1, 1, 2])
            sub = round(preco * qtd, 2)
            valor += sub
            itens.append((len(itens) + 1, i + 1, p["Codigo"], p["Descricao"], qtd, f"{preco:.2f}", f"{sub:.2f}"))
    elif tipo == "Reembolso":
        valor = round(random.uniform(80, 2800), 2)
    seq[tipo] += 1
    codigo = f"{prefixo[tipo]}-2026-{seq[tipo]:06d}"
    etapas = cadeia(solicitante, cc, valor) if tipo != "Férias" else [sem_autoaprovacao(colab[solicitante]["GestorId"] or diretor_cc[cc], solicitante, cc)]
    sla = 4 if urgente else 24
    t = criado
    status = "Aprovado"
    atrasada = False
    for n, aprovador in enumerate(etapas, start=1):
        # ~12% das etapas passam do prazo
        horas = random.uniform(0.5, sla * 0.9) if random.random() > 0.12 else random.uniform(sla * 1.05, sla * 2.5)
        if horas > sla:
            atrasada = True
        decisao = "Aprovado"
        if random.random() < 0.08 / len(etapas):
            decisao = "Reprovado"
        t = t + timedelta(hours=horas)
        canal = random.choices(["Teams", "App"], [0.7, 0.3])[0]
        aprovacoes.append((len(aprovacoes) + 1, i + 1, n, aprovador, colab[aprovador]["Nome"], decisao, canal, iso(t), f"{horas:.2f}"))
        if decisao == "Reprovado":
            status = "Reprovado"
            break
    conclusao = t
    if conclusao.date() > FIM:  # ainda em andamento no fim do período
        status, conclusao = "Em andamento", None
    solicitacoes.append((i + 1, codigo, tipo, solicitante, cc, fornecedor, f"{valor:.2f}", "Sim" if urgente else "Não", status,
                         iso(criado), iso(conclusao) if conclusao else "", len(etapas), "Sim" if atrasada else "Não"))

grava("solicitacoes.csv", ["Id", "Codigo", "Tipo", "SolicitanteId", "CentroCusto", "FornecedorId", "ValorTotal", "Urgente", "Status",
                           "DataCriacao", "DataConclusao", "TotalEtapas", "Atrasada"], solicitacoes)
grava("itens_solicitacao.csv", ["Id", "SolicitacaoId", "ProdutoCodigo", "Descricao", "Quantidade", "PrecoUnitario", "Subtotal"], itens)
grava("aprovacoes.csv", ["Id", "SolicitacaoId", "Etapa", "AprovadorId", "AprovadorNome", "Decisao", "Canal", "DataDecisao", "DuracaoHoras"], aprovacoes)

# ---------------------------------------------------------------- P03 · Notas fiscais
notas = []
compras_aprovadas = [s for s in solicitacoes if s[2] == "Compra" and s[8] == "Aprovado"]
for k, s in enumerate(compras_aprovadas):
    emissao = datetime.fromisoformat(s[10]) + timedelta(days=random.randint(2, 12))
    if emissao.date() > FIM:
        continue
    valor = float(s[6])
    r = random.random()
    if r < 0.06:
        valor_nf = round(valor * random.choice([0.9, 1.06, 1.12]), 2)
        resultado, motivo = "Divergente", f"Valor da nota {valor_nf:.2f} x pedido {valor:.2f}"
    else:
        valor_nf, resultado, motivo = valor, "Conferida", ""
    lanc = "Lançada" if resultado == "Conferida" and random.random() > 0.02 else ("Erro" if resultado == "Conferida" else "Pendente")
    numero = 10000 + k
    notas.append((f"NFe{numero:044d}"[:47], numero, 1, emissao.date().isoformat(), s[5], f"{valor_nf:.2f}", s[0], f"{valor:.2f}", resultado, motivo, lanc))
for k in range(28):  # notas sem pedido
    emissao = random.choice(uteis)
    f = random.choice(fornecedores)
    numero = 20000 + k
    notas.append((f"NFe{numero:044d}"[:47], numero, 1, emissao.isoformat(), f["Id"], f"{random.uniform(300, 9000):.2f}", "", "", "Sem pedido", "Nenhum pedido aprovado do fornecedor", "Pendente"))
grava("notas.csv", ["ChaveAcesso", "Numero", "Serie", "DataEmissao", "FornecedorId", "ValorTotal", "SolicitacaoId", "ValorPedido", "Resultado", "Motivo", "StatusLancamento"], notas)

# ---------------------------------------------------------------- P02 · Ativos, inspeções e NCs
ativos = [(f"IJ-{i:02d}", f"Injetora IJ-{i:02d}", "Injetora", "Galpão A" if i <= 14 else "Galpão B" if i <= 28 else "Galpão C") for i in range(1, 39)]
ativos += [(f"M-{i:03d}", f"Molde M-{i:03d}", "Molde", "Ferramentaria") for i in range(1, 61)]
grava("ativos.csv", ["Codigo", "Nome", "Tipo", "Area"], ativos)

inspetores = [c for c in colabs if c["CentroCusto"] == "CC-400"]
inspecoes, ncs = [], []
for d in uteis:
    for _ in range(random.randint(2, 5)):
        a = random.choice(ativos)
        quem = random.choice(inspetores)
        ini = datetime.combine(d, datetime.min.time()) + timedelta(hours=random.randint(6, 21), minutes=random.randint(0, 59))
        nc = random.random() < 0.11
        inspecoes.append((len(inspecoes) + 1, a[0], quem["Id"], iso(ini), iso(ini + timedelta(minutes=random.randint(12, 45))), "Não conforme" if nc else "Conforme"))
        if nc:
            sev = random.choices(["Baixa", "Média", "Alta"], [0.5, 0.35, 0.15])[0]
            prazo = ini + timedelta(days={"Alta": 3, "Média": 7, "Baixa": 15}[sev])
            fechou = random.random() < 0.85
            fech = ini + timedelta(days=random.uniform(0.5, {"Alta": 5, "Média": 10, "Baixa": 20}[sev])) if fechou else None
            if fech and fech.date() > FIM:
                fech = None
            estado = "Fechada" if fech else ("Em tratamento" if random.random() < 0.6 else "Aberta")
            ncs.append((len(ncs) + 1, len(inspecoes), a[0], sev, estado, iso(ini), iso(prazo), iso(fech) if fech else "", random.choice(inspetores)["Id"]))
grava("inspecoes.csv", ["Id", "AtivoCodigo", "InspetorId", "Inicio", "Fim", "Resultado"], inspecoes)
grava("nao_conformidades.csv", ["Id", "InspecaoId", "AtivoCodigo", "Severidade", "Estado", "Abertura", "Prazo", "Fechamento", "ResponsavelId"], ncs)

# ---------------------------------------------------------------- Orçamento e produção
orc = []
for c in centros:
    for m in range(1, 13):
        base = int(c["OrcamentoMensal"])
        orc.append((c["Codigo"], f"2026-{m:02d}-01", base))
grava("orcamento_mensal.csv", ["CentroCusto", "Mes", "Valor"], orc)

prod = []
for d in dias_uteis(INICIO, FIM):
    for i in range(1, 39):
        horas_paradas = round(max(0.0, random.gauss(1.2, 1.5)), 1) if random.random() < 0.35 else 0.0
        pecas = int(random.uniform(1800, 9000) * (24 - horas_paradas) / 24)
        refugo = int(pecas * random.uniform(0.008, 0.045))
        prod.append((d.isoformat(), f"IJ-{i:02d}", pecas, refugo, horas_paradas))
grava("producao_diaria.csv", ["Data", "Injetora", "PecasBoas", "Refugo", "HorasParadas"], prod)

print(f"solicitações {len(solicitacoes)}, aprovações {len(aprovacoes)}, notas {len(notas)}, inspeções {len(inspecoes)}, NCs {len(ncs)}, produção {len(prod)}")
