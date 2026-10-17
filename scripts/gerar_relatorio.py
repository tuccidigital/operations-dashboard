"""Gera o relatório em formato PBIR (pasta 'Painel Operacoes.Report') e o tema da Tucci.

Rode na pasta do projeto: python scripts/gerar_relatorio.py
Com --validar <pasta-dos-esquemas>, confere cada JSON contra os esquemas oficiais (microsoft/json-schemas).
"""
import hashlib
import json
import shutil
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
REP = RAIZ / "Painel Operacoes.Report"
DEF = REP / "definition"
SCH = "https://developer.microsoft.com/json-schemas/fabric/item/report/definition"
W, H = 1280, 720

TEMA = {
    "name": "Tucci Digital",
    "dataColors": ["#5B6B35", "#2C47A6", "#51565C", "#9DB067", "#8F5B00", "#1C7346", "#B0281F", "#7A8077"],
    "foreground": "#17191C",
    "foregroundNeutralSecondary": "#51565C",
    "background": "#FFFFFF",
    "backgroundLight": "#F2F3EF",
    "backgroundNeutral": "#E5E7E1",
    "tableAccent": "#5B6B35",
    "good": "#1C7346",
    "neutral": "#8F5B00",
    "bad": "#B0281F",
    "maximum": "#5B6B35",
    "center": "#E5E7E1",
    "minimum": "#FFFFFF",
    "textClasses": {
        "callout": {"fontSize": 26, "fontFace": "Segoe UI Semibold", "color": "#17191C"},
        "title": {"fontSize": 12, "fontFace": "Segoe UI Semibold", "color": "#17191C"},
        "header": {"fontSize": 12, "fontFace": "Segoe UI Semibold", "color": "#17191C"},
        "label": {"fontSize": 10, "fontFace": "Segoe UI", "color": "#51565C"},
    },
    "visualStyles": {
        "*": {"*": {
            "background": [{"show": True, "color": {"solid": {"color": "#FFFFFF"}}, "transparency": 0}],
            "border": [{"show": True, "color": {"solid": {"color": "#D2D5CD"}}, "radius": 10}],
            "dropShadow": [{"show": False}],
            "title": [{"show": True, "fontColor": {"solid": {"color": "#17191C"}}, "fontSize": 12}],
        }},
        "page": {"*": {"background": [{"color": {"solid": {"color": "#F2F3EF"}}, "transparency": 0}]}},
    },
}


def gid(*partes):
    return hashlib.sha1("/".join(partes).encode()).hexdigest()[:20]


def lit(v):
    if isinstance(v, bool):
        return {"expr": {"Literal": {"Value": "true" if v else "false"}}}
    if isinstance(v, (int, float)):
        return {"expr": {"Literal": {"Value": f"{v}D"}}}
    return {"expr": {"Literal": {"Value": "'" + v.replace("'", "''") + "'"}}}


def campo(ref):
    """'Tabela[Coluna]' ou '[Medida]' (medidas ficam em _Medidas)."""
    if ref.startswith("["):
        nome = ref[1:-1]
        return {"Measure": {"Expression": {"SourceRef": {"Entity": "_Medidas"}}, "Property": nome}}, f"_Medidas.{nome}", nome
    tabela, col = ref[:-1].split("[")
    return {"Column": {"Expression": {"SourceRef": {"Entity": tabela}}, "Property": col}}, f"{tabela}.{col}", col


def projecao(ref, ativa=False):
    f, qref, nativo = campo(ref)
    p = {"field": f, "queryRef": qref, "nativeQueryRef": nativo}
    if ativa:
        p["active"] = True
    return p


def filtro_in(nome, tabela, coluna, valores, negar=False):
    cond = {"In": {"Expressions": [{"Column": {"Expression": {"SourceRef": {"Source": "f"}}, "Property": coluna}}],
                   "Values": [[{"Literal": {"Value": "'" + v + "'"}}] for v in valores]}}
    if negar:
        cond = {"Not": {"Expression": cond}}
    return {
        "name": nome,
        "field": {"Column": {"Expression": {"SourceRef": {"Entity": tabela}}, "Property": coluna}},
        "type": "Categorical",
        "filter": {"Version": 2, "From": [{"Name": "f", "Entity": tabela, "Type": 0}], "Where": [{"Condition": cond}]},
    }


class Pagina:
    def __init__(self, nome, titulo, drill=None):
        self.nome, self.titulo, self.visuais, self.drill = nome, titulo, [], drill
        self.z = 0

    def visual(self, tipo, x, y, w, h, papeis=None, titulo=None, objetos=None, filtros=None, ordenar=None):
        self.z += 1000
        nome = gid(self.nome, str(len(self.visuais)), tipo)
        v = {"visualType": tipo}
        if papeis:
            qs = {}
            for papel, refs in papeis.items():
                qs[papel] = {"projections": [projecao(r, ativa=(papel in ("Category", "Rows"))) for r in refs]}
            v["query"] = {"queryState": qs}
            if ordenar:
                f, _, _ = campo(ordenar[0])
                v["query"]["sortDefinition"] = {"sort": [{"field": f, "direction": ordenar[1]}], "isDefaultSort": False}
        if objetos:
            v["objects"] = objetos
        cont = {}
        if titulo:
            cont["title"] = [{"properties": {"show": lit(True), "text": lit(titulo)}}]
        if cont:
            v["visualContainerObjects"] = cont
        d = {
            "$schema": f"{SCH}/visualContainer/2.0.0/schema.json",
            "name": nome,
            "position": {"x": x, "y": y, "z": self.z, "width": w, "height": h, "tabOrder": self.z},
            "visual": v,
        }
        if filtros:
            d["filterConfig"] = {"filters": filtros}
        self.visuais.append(d)
        return d

    def texto(self, x, y, w, h, linhas):
        paragrafos = []
        for t, tam, negrito, cor in linhas:
            estilo = {"fontSize": f"{tam}pt", "color": cor}
            if negrito:
                estilo["fontWeight"] = "bold"
            paragrafos.append({"textRuns": [{"value": t, "textStyle": estilo}]})
        return self.visual("textbox", x, y, w, h, objetos={"general": [{"properties": {"paragraphs": paragrafos}}]})

    def cartao(self, x, y, w, h, medida, titulo):
        return self.visual("card", x, y, w, h, {"Values": [medida]}, titulo=titulo,
                           objetos={"categoryLabels": [{"properties": {"show": lit(False)}}]})

    def json(self):
        d = {"$schema": f"{SCH}/page/2.0.0/schema.json", "name": self.nome, "displayName": self.titulo,
             "displayOption": "FitToPage", "height": H, "width": W}
        if self.drill:
            tabela, col = self.drill
            fnome = gid(self.nome, "drill")
            d["filterConfig"] = {"filters": [{
                "name": fnome, "field": {"Column": {"Expression": {"SourceRef": {"Entity": tabela}}, "Property": col}},
                "type": "Categorical", "howCreated": "Drillthrough"}]}
            d["pageBinding"] = {"name": gid(self.nome, "binding"), "type": "Drillthrough", "parameters": [{
                "name": gid(self.nome, "param"), "boundFilter": fnome,
                "fieldExpr": {"Column": {"Expression": {"SourceRef": {"Entity": tabela}}, "Property": col}}}]}
        return d


def cabecalho(p, titulo, sub):
    p.texto(24, 12, 900, 56, [(titulo, 20, True, "#17191C"), (sub, 10, False, "#51565C")])
    p.texto(1000, 18, 256, 40, [("Dados fictícios · Lumina Componentes", 9, False, "#51565C")])


def paginas():
    ps = []

    # 1 · Resumo de segunda-feira
    p = Pagina("resumo", "Resumo de segunda-feira")
    cabecalho(p, "Resumo de segunda-feira", "Mês da data de referência contra o mês anterior. Os números batem com as áreas porque vêm do mesmo modelo.")
    kpis = [("Valor aprovado", "Valor aprovado"), ("Tempo médio de aprovação (h)", "Tempo de aprovação (h)"),
            ("% aprovadas no SLA", "Aprovadas no prazo"), ("% notas com divergência", "Notas divergentes"),
            ("NCs", "Não conformidades"), ("Índice de refugo %", "Refugo")]
    for i, (base, rot) in enumerate(kpis):
        x = 24 + i * 206
        p.cartao(x, 80, 196, 92, f"[{base} · mês]", rot)
        p.cartao(x, 176, 196, 56, f"[{base} · variação]", "contra o mês anterior")
    p.visual("lineChart", 24, 248, 760, 220, {"Category": ["Data[InicioSemana]"], "Y": ["[Valor aprovado]", "[Orçamento]"]},
             titulo="Valor aprovado por semana · últimas 12 semanas",
             filtros=[filtro_in(gid("resumo", "f12"), "Data", "Ultimas12Semanas", ["Sim"])])
    p.visual("tableEx", 796, 248, 460, 220, {"Values": ["CentroCusto[Nome]", "[Valor aprovado · mês]", "[Consumo do orçamento %]", "[Solicitações atrasadas]"]},
             titulo="Centros de custo", ordenar=("[Consumo do orçamento %]", "Descending"))
    p.visual("tableEx", 24, 480, 616, 220, {"Values": ["Ativo[Codigo]", "[NCs abertas]", "[NCs vencidas]", "[Índice de refugo %]"]},
             titulo="O que pede ação na fábrica", ordenar=("[NCs vencidas]", "Descending"))
    p.visual("tableEx", 652, 480, 604, 220, {"Values": ["Fornecedor[Nome]", "[Notas divergentes]", "[Valor divergente]", "[Notas sem pedido]"]},
             titulo="Fornecedores com divergência", ordenar=("[Valor divergente]", "Descending"))
    ps.append(p)

    # 2 · Compras
    p = Pagina("compras", "Compras")
    cabecalho(p, "Compras e aprovações", "Solicitações de compra, reembolso e férias aprovadas pelo P01 Central de Aprovações.")
    p.visual("slicer", 24, 80, 300, 70, {"Values": ["Data[Mes]"]}, titulo="Mês")
    p.cartao(336, 80, 220, 70, "[Valor aprovado]", "Valor aprovado")
    p.cartao(568, 80, 220, 70, "[Tempo médio de aprovação (h)]", "Tempo médio de aprovação (h)")
    p.cartao(800, 80, 220, 70, "[% aprovadas no SLA]", "Aprovadas no prazo")
    p.cartao(1032, 80, 224, 70, "[Consumo do orçamento %]", "Consumo do orçamento")
    p.visual("funnel", 24, 164, 400, 260, {"Category": ["Solicitacoes[Status]"], "Y": ["[Solicitações]"]}, titulo="Solicitações por estado")
    p.visual("clusteredColumnChart", 436, 164, 400, 260, {"Category": ["Aprovacoes[Etapa]"], "Y": ["[Tempo médio por etapa (h)]"]}, titulo="Tempo médio por etapa (h)")
    p.visual("clusteredBarChart", 848, 164, 408, 260, {"Category": ["CentroCusto[Nome]"], "Y": ["[Valor aprovado]"]},
             titulo="Valor aprovado por centro de custo", ordenar=("[Valor aprovado]", "Descending"))
    p.visual("clusteredColumnChart", 24, 436, 1232, 264, {"Category": ["Data[Mes]"], "Y": ["[Valor aprovado]", "[Orçamento]"]},
             titulo="Valor aprovado e orçamento por mês")
    ps.append(p)

    # 3 · Fiscal
    p = Pagina("fiscal", "Fiscal")
    cabecalho(p, "Conferência de notas", "Notas fiscais conferidas com o pedido pelo P03 Robô de NF-e.")
    p.cartao(24, 80, 300, 80, "[Notas]", "Notas recebidas")
    p.cartao(336, 80, 300, 80, "[% notas com divergência]", "Com divergência")
    p.cartao(648, 80, 300, 80, "[Valor divergente]", "Valor divergente")
    p.cartao(960, 80, 296, 80, "[Notas sem pedido]", "Sem pedido")
    p.visual("clusteredBarChart", 24, 176, 500, 524, {"Category": ["Fornecedor[Nome]"], "Y": ["[Notas divergentes]"]},
             titulo="Notas divergentes por fornecedor", ordenar=("[Notas divergentes]", "Descending"))
    p.visual("tableEx", 536, 176, 720, 524,
             {"Values": ["Notas[Numero]", "Fornecedor[Nome]", "Notas[DataEmissao]", "Notas[ValorTotal]", "Notas[ValorPedido]", "Notas[Resultado]", "Notas[Motivo]"]},
             titulo="Notas que pedem ação",
             filtros=[filtro_in(gid("fiscal", "naoconf"), "Notas", "Resultado", ["Conferida"], negar=True)])
    ps.append(p)

    # 4 · Qualidade
    p = Pagina("qualidade", "Qualidade")
    cabecalho(p, "Qualidade e produção", "Inspeções e não conformidades do P02 e produção diária das 38 injetoras.")
    p.cartao(24, 80, 300, 80, "[NCs abertas]", "NCs abertas")
    p.cartao(336, 80, 300, 80, "[NCs vencidas]", "NCs vencidas")
    p.cartao(648, 80, 300, 80, "[Tempo médio de fechamento (dias)]", "Fechamento médio (dias)")
    p.cartao(960, 80, 296, 80, "[Índice de refugo %]", "Refugo")
    p.visual("clusteredColumnChart", 24, 176, 400, 250, {"Category": ["NaoConformidades[Severidade]"], "Y": ["[NCs]"]}, titulo="NCs por severidade")
    p.visual("lineChart", 436, 176, 820, 250, {"Category": ["Data[Mes]"], "Y": ["[Disponibilidade %]"]}, titulo="Disponibilidade das injetoras por mês")
    p.visual("clusteredBarChart", 24, 438, 1232, 262, {"Category": ["Ativo[Codigo]"], "Y": ["[Índice de refugo %]"]},
             titulo="Refugo por injetora", ordenar=("[Índice de refugo %]", "Descending"),
             filtros=[filtro_in(gid("qualidade", "inj"), "Ativo", "Tipo", ["Injetora"])])
    ps.append(p)

    # 5 · Detalhe (drill-through por centro de custo)
    p = Pagina("detalhe", "Detalhe do centro de custo", drill=("CentroCusto", "Nome"))
    cabecalho(p, "Detalhe do centro de custo", "Clique com o botão direito num centro de custo em qualquer página e escolha Detalhar.")
    p.cartao(24, 80, 300, 80, "[Valor aprovado]", "Valor aprovado")
    p.cartao(336, 80, 300, 80, "[Consumo do orçamento %]", "Consumo do orçamento")
    p.cartao(648, 80, 300, 80, "[Solicitações atrasadas]", "Solicitações atrasadas")
    p.visual("tableEx", 24, 176, 1232, 524,
             {"Values": ["Solicitacoes[Codigo]", "Solicitacoes[Tipo]", "Solicitacoes[Status]", "Solicitacoes[ValorTotal]", "Solicitacoes[DataCriacao]",
                         "Solicitacoes[HorasTotais]", "Solicitacoes[Atrasada]"]},
             titulo="Solicitações do centro de custo", ordenar=("Solicitacoes[DataCriacao]", "Descending"))
    ps.append(p)
    return ps


def escrever():
    if DEF.exists():
        shutil.rmtree(DEF)
    (DEF / "pages").mkdir(parents=True)
    res = REP / "StaticResources" / "RegisteredResources"
    res.mkdir(parents=True, exist_ok=True)
    (res / "tucci-powerbi-theme.json").write_text(json.dumps(TEMA, ensure_ascii=False, indent=2), encoding="utf-8")
    (RAIZ / "tucci-powerbi-theme.json").write_text(json.dumps(TEMA, ensure_ascii=False, indent=2), encoding="utf-8")

    def grava(caminho, obj):
        caminho.parent.mkdir(parents=True, exist_ok=True)
        caminho.write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding="utf-8")

    grava(REP / "definition.pbir", {
        "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definitionProperties/2.0.0/schema.json",
        "version": "4.0", "datasetReference": {"byPath": {"path": "../Painel Operacoes.SemanticModel"}}})
    grava(DEF / "version.json", {"$schema": f"{SCH}/versionMetadata/1.0.0/schema.json", "version": "2.0.0"})
    grava(DEF / "report.json", {
        "$schema": f"{SCH}/report/1.3.0/schema.json",
        "themeCollection": {"customTheme": {"name": "tucci-powerbi-theme.json", "reportVersionAtImport": "5.61", "type": "RegisteredResources"}},
        "layoutOptimization": "None",
        "resourcePackages": [{"name": "RegisteredResources", "type": "RegisteredResources",
                              "items": [{"name": "tucci-powerbi-theme.json", "path": "tucci-powerbi-theme.json", "type": "CustomTheme"}]}],
        "settings": {"useStylableVisualContainerHeader": True, "defaultDrillFilterOtherVisuals": True, "allowChangeFilterTypes": True,
                     "useEnhancedTooltips": True},
    })
    ps = paginas()
    grava(DEF / "pages" / "pages.json", {"$schema": f"{SCH}/pagesMetadata/1.0.0/schema.json",
                                         "pageOrder": [p.nome for p in ps], "activePageName": ps[0].nome})
    arquivos = [REP / "definition.pbir", DEF / "version.json", DEF / "report.json", DEF / "pages" / "pages.json"]
    for p in ps:
        grava(DEF / "pages" / p.nome / "page.json", p.json())
        arquivos.append(DEF / "pages" / p.nome / "page.json")
        for v in p.visuais:
            c = DEF / "pages" / p.nome / "visuals" / v["name"] / "visual.json"
            grava(c, v)
            arquivos.append(c)
    grava(RAIZ / "Painel Operacoes.pbip", {
        "$schema": "https://developer.microsoft.com/json-schemas/fabric/pbip/pbipProperties/1.0.0/schema.json",
        "version": "1.0", "artifacts": [{"report": {"path": "Painel Operacoes.Report"}}], "settings": {"enableAutoRecovery": True}})
    print(f"{len(ps)} páginas, {sum(len(p.visuais) for p in ps)} visuais")
    return arquivos


def validar(arquivos, pasta):
    from jsonschema import Draft7Validator
    from referencing import Registry, Resource
    base = Path(pasta)
    reg = Registry()
    por_url = {}
    for f in base.rglob("*.json"):
        rel = f.relative_to(base).as_posix()
        url = "https://developer.microsoft.com/json-schemas/fabric/" + rel
        conteudo = json.loads(f.read_text(encoding="utf-8"))
        res = Resource.from_contents(conteudo, default_specification=__import__("referencing.jsonschema").jsonschema.DRAFT7)
        reg = reg.with_resource(url, res)
        if conteudo.get("$id"):
            reg = reg.with_resource(conteudo["$id"], res)
        por_url[url] = conteudo
    erros = 0
    for a in arquivos:
        doc = json.loads(a.read_text(encoding="utf-8"))
        sch = doc.get("$schema")
        if sch not in por_url:
            print("sem esquema local:", a.relative_to(RAIZ), sch)
            continue
        v = Draft7Validator(por_url[sch], registry=reg)
        for e in v.iter_errors(doc):
            erros += 1
            print(f"ERRO {a.relative_to(RAIZ)}: {'/'.join(map(str, e.absolute_path))}: {e.message[:200]}")
    print("validação:", "ok" if not erros else f"{erros} erro(s)")
    return erros


if __name__ == "__main__":
    arqs = escrever()
    if "--validar" in sys.argv:
        sys.exit(1 if validar(arqs, sys.argv[sys.argv.index("--validar") + 1]) else 0)
