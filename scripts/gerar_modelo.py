"""Gera o modelo semântico em TMDL (pasta 'Painel Operacoes.SemanticModel').

Rode na pasta do projeto: python scripts/gerar_modelo.py
O modelo é descrito aqui de forma compacta; o TMDL é gerado com lineageTags estáveis (uuid5).
"""
import uuid
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
SM = RAIZ / "Painel Operacoes.SemanticModel"
DEF = SM / "definition"
NS = uuid.UUID("6f1d3c2a-7b8e-4c5d-9a1f-2e3d4c5b6a70")


def tag(*partes):
    return str(uuid.uuid5(NS, "/".join(partes)))


# tipo -> (dataType TMDL, tipo M)
TIPOS = {
    "texto": ("string", "type text"),
    "inteiro": ("int64", "Int64.Type"),
    "numero": ("double", "type number"),
    "moeda": ("decimal", "Currency.Type"),
    "datahora": ("dateTime", "type datetime"),
    "data": ("dateTime", "type date"),
}

MOEDA = '\\R$ #,0.00;-\\R$ #,0.00;\\R$ #,0.00'

# Cada tabela: arquivo CSV, colunas (nome, tipo, formato, resumir, oculta), passos M extras, colunas derivadas.
TABELAS = [
    dict(nome="CentroCusto", csv="centros_custo.csv", colunas=[
        ("Codigo", "texto"), ("Nome", "texto"), ("OrcamentoMensal", "moeda", MOEDA, "none"), ("GerenteId", "texto", None, None, True), ("DiretorId", "texto", None, None, True)]),
    dict(nome="Colaborador", csv="colaboradores.csv", colunas=[
        ("Id", "texto", None, None, True), ("Nome", "texto"), ("Email", "texto"), ("Cargo", "texto"), ("CentroCusto", "texto"), ("GestorId", "texto", None, None, True), ("NivelAlcada", "inteiro", "0", "none")]),
    dict(nome="Fornecedor", csv="fornecedores.csv", colunas=[
        ("Id", "texto", None, None, True), ("Nome", "texto"), ("CNPJ", "texto"), ("Categoria", "texto"), ("PrazoPagamentoDias", "inteiro", "0", "none"), ("Email", "texto")]),
    dict(nome="Produto", csv="produtos.csv", colunas=[
        ("Codigo", "texto"), ("Descricao", "texto"), ("Categoria", "texto"), ("PrecoReferencia", "moeda", MOEDA, "none"), ("FornecedorPadraoId", "texto", None, None, True)]),
    dict(nome="Ativo", csv="ativos.csv", colunas=[("Codigo", "texto"), ("Nome", "texto"), ("Tipo", "texto"), ("Area", "texto")]),
    dict(nome="MapaGerente", csv="mapa_gerentes.csv", oculta=True, colunas=[("Email", "texto"), ("CentroCusto", "texto")]),
    dict(nome="Feriado", csv="feriados.csv", oculta=True, colunas=[("Data", "data", "dd/mm/yyyy"), ("Nome", "texto")]),
    dict(nome="Solicitacoes", csv="solicitacoes.csv", colunas=[
        ("Id", "texto", None, None, True), ("Codigo", "texto"), ("Tipo", "texto"), ("SolicitanteId", "texto", None, None, True), ("CentroCusto", "texto", None, None, True),
        ("FornecedorId", "texto", None, None, True), ("ValorTotal", "moeda", MOEDA, "sum"), ("Urgente", "texto"), ("Status", "texto"),
        ("DataCriacao", "datahora", "dd/mm/yyyy hh:nn"), ("DataConclusao", "datahora", "dd/mm/yyyy hh:nn"), ("TotalEtapas", "inteiro", "0", "none"), ("Atrasada", "texto")],
        derivadas=[
            ("DataCriacaoDia", "data", "dd/mm/yyyy", "Date.From([DataCriacao])"),
            ("HorasTotais", "numero", "0.0", "if [DataConclusao] = null then null else Duration.TotalHours([DataConclusao] - [DataCriacao])"),
        ]),
    dict(nome="Aprovacoes", csv="aprovacoes.csv", colunas=[
        ("Id", "texto", None, None, True), ("SolicitacaoId", "texto", None, None, True), ("Etapa", "inteiro", "0", "none"), ("AprovadorId", "texto", None, None, True),
        ("AprovadorNome", "texto"), ("Decisao", "texto"), ("Canal", "texto"), ("DataDecisao", "datahora", "dd/mm/yyyy hh:nn"), ("DuracaoHoras", "numero", "0.0", "none")]),
    dict(nome="Notas", csv="notas.csv", colunas=[
        ("ChaveAcesso", "texto"), ("Numero", "inteiro", "0", "none"), ("Serie", "inteiro", "0", "none"), ("DataEmissao", "data", "dd/mm/yyyy"), ("FornecedorId", "texto", None, None, True),
        ("ValorTotal", "moeda", MOEDA, "sum"), ("SolicitacaoId", "texto", None, None, True), ("ValorPedido", "moeda", MOEDA, "sum"), ("Resultado", "texto"), ("Motivo", "texto"), ("StatusLancamento", "texto")]),
    dict(nome="Inspecoes", csv="inspecoes.csv", colunas=[
        ("Id", "texto", None, None, True), ("AtivoCodigo", "texto", None, None, True), ("InspetorId", "texto", None, None, True), ("Inicio", "datahora", "dd/mm/yyyy hh:nn"), ("Fim", "datahora", "dd/mm/yyyy hh:nn"), ("Resultado", "texto")],
        derivadas=[("Dia", "data", "dd/mm/yyyy", "Date.From([Inicio])")]),
    dict(nome="NaoConformidades", csv="nao_conformidades.csv", colunas=[
        ("Id", "texto", None, None, True), ("InspecaoId", "texto", None, None, True), ("AtivoCodigo", "texto", None, None, True), ("Severidade", "texto"), ("Estado", "texto"),
        ("Abertura", "datahora", "dd/mm/yyyy hh:nn"), ("Prazo", "datahora", "dd/mm/yyyy hh:nn"), ("Fechamento", "datahora", "dd/mm/yyyy hh:nn"), ("ResponsavelId", "texto", None, None, True)],
        derivadas=[
            ("AberturaDia", "data", "dd/mm/yyyy", "Date.From([Abertura])"),
            ("DiasParaFechar", "numero", "0.0", "if [Fechamento] = null then null else Duration.TotalDays([Fechamento] - [Abertura])"),
        ]),
    dict(nome="OrcamentoMensal", csv="orcamento_mensal.csv", colunas=[("CentroCusto", "texto", None, None, True), ("Mes", "data", "mmm/yyyy"), ("Valor", "moeda", MOEDA, "sum")]),
    dict(nome="ProducaoDiaria", csv="producao_diaria.csv", colunas=[
        ("Data", "data", "dd/mm/yyyy"), ("Injetora", "texto", None, None, True), ("PecasBoas", "inteiro", "#,0", "sum"), ("Refugo", "inteiro", "#,0", "sum"), ("HorasParadas", "numero", "0.0", "sum")]),
]

RELACOES = [
    ("Solicitacoes", "CentroCusto", "CentroCusto", "Codigo", True),
    ("Solicitacoes", "FornecedorId", "Fornecedor", "Id", True),
    ("Solicitacoes", "SolicitanteId", "Colaborador", "Id", True),
    ("Solicitacoes", "DataCriacaoDia", "Data", "Data", True),
    ("Aprovacoes", "SolicitacaoId", "Solicitacoes", "Id", True),
    ("Aprovacoes", "AprovadorId", "Colaborador", "Id", False),  # alternativa: USERELATIONSHIP
    ("Notas", "FornecedorId", "Fornecedor", "Id", True),
    ("Notas", "DataEmissao", "Data", "Data", True),
    ("Notas", "SolicitacaoId", "Solicitacoes", "Id", False),
    ("Inspecoes", "AtivoCodigo", "Ativo", "Codigo", True),
    ("Inspecoes", "Dia", "Data", "Data", True),
    ("NaoConformidades", "AtivoCodigo", "Ativo", "Codigo", True),
    ("NaoConformidades", "AberturaDia", "Data", "Data", True),
    ("NaoConformidades", "InspecaoId", "Inspecoes", "Id", False),
    ("OrcamentoMensal", "CentroCusto", "CentroCusto", "Codigo", True),
    ("OrcamentoMensal", "Mes", "Data", "Data", True),
    ("ProducaoDiaria", "Data", "Data", "Data", True),
    ("ProducaoDiaria", "Injetora", "Ativo", "Codigo", True),
]

# (pasta, nome, expressão DAX, formato, descrição)
MEDIDAS = [
    # Referência
    ("Referência", "Data de referência", "CALCULATE ( MAX ( ProducaoDiaria[Data] ), REMOVEFILTERS () )", "dd/mm/yyyy",
     "Último dia com dados. As medidas de mês atual e anterior se ancoram nela, nunca numa data fixa."),
    # Compras
    ("Compras", "Solicitações", "COUNTROWS ( Solicitacoes )", "#,0", "Quantidade de solicitações (compra, reembolso e férias)."),
    ("Compras", "Valor aprovado", 'CALCULATE ( SUM ( Solicitacoes[ValorTotal] ), Solicitacoes[Status] = "Aprovado" )', MOEDA, "Soma das solicitações aprovadas."),
    ("Compras", "Tempo médio de aprovação (h)", 'AVERAGEX ( FILTER ( Solicitacoes, NOT ISBLANK ( Solicitacoes[HorasTotais] ) ), Solicitacoes[HorasTotais] )', "0.0",
     "Horas da criação até a decisão final, média das solicitações concluídas."),
    ("Compras", "% aprovadas no SLA",
     'VAR Aprovadas = CALCULATE ( COUNTROWS ( Solicitacoes ), Solicitacoes[Status] = "Aprovado" )\nVAR NoPrazo = CALCULATE ( COUNTROWS ( Solicitacoes ), Solicitacoes[Status] = "Aprovado", Solicitacoes[Atrasada] = "Não" )\nRETURN DIVIDE ( NoPrazo, Aprovadas )',
     "0.0%", "Aprovadas sem nenhuma etapa fora do prazo (24 h por etapa, 4 h se urgente)."),
    ("Compras", "Solicitações atrasadas", 'CALCULATE ( COUNTROWS ( Solicitacoes ), Solicitacoes[Atrasada] = "Sim" )', "#,0", "Solicitações com ao menos uma etapa fora do prazo."),
    ("Compras", "Tempo médio por etapa (h)", "AVERAGE ( Aprovacoes[DuracaoHoras] )", "0.0", "Média de horas que cada etapa de aprovação levou."),
    ("Compras", "Orçamento", "SUM ( OrcamentoMensal[Valor] )", MOEDA, "Orçamento mensal dos centros de custo no período."),
    ("Compras", "Consumo do orçamento %", "DIVIDE ( [Valor aprovado], [Orçamento] )", "0.0%", "Valor aprovado sobre o orçamento do período."),
    ("Compras", "Valor aprovado no ano", "TOTALYTD ( [Valor aprovado], Data[Data] )", MOEDA, "Acumulado no ano até a data do contexto."),
    ("Compras", "Centros acima do orçamento", "COUNTROWS ( FILTER ( VALUES ( CentroCusto[Codigo] ), [Consumo do orçamento %] > 1 ) )", "#,0",
     "Centros de custo com consumo acima de 100% no período."),
    # Fiscal
    ("Fiscal", "Notas", "COUNTROWS ( Notas )", "#,0", "Notas fiscais recebidas."),
    ("Fiscal", "Notas divergentes", 'CALCULATE ( COUNTROWS ( Notas ), Notas[Resultado] = "Divergente" )', "#,0", "Notas com valor fora de ±2% do pedido."),
    ("Fiscal", "% notas com divergência", "DIVIDE ( [Notas divergentes], [Notas] )", "0.0%", "Notas divergentes sobre o total de notas."),
    ("Fiscal", "Valor divergente", 'SUMX ( FILTER ( Notas, Notas[Resultado] = "Divergente" ), ABS ( Notas[ValorTotal] - Notas[ValorPedido] ) )', MOEDA,
     "Soma das diferenças absolutas entre nota e pedido."),
    ("Fiscal", "Notas sem pedido", 'CALCULATE ( COUNTROWS ( Notas ), Notas[Resultado] = "Sem pedido" )', "#,0", "Notas sem pedido aprovado do fornecedor."),
    # Qualidade
    ("Qualidade", "Inspeções", "COUNTROWS ( Inspecoes )", "#,0", "Inspeções realizadas."),
    ("Qualidade", "NCs", "COUNTROWS ( NaoConformidades )", "#,0", "Não conformidades abertas no período."),
    ("Qualidade", "NCs abertas", 'CALCULATE ( COUNTROWS ( NaoConformidades ), NaoConformidades[Estado] <> "Fechada" )', "#,0", "NCs ainda não fechadas."),
    ("Qualidade", "NCs vencidas",
     'VAR Ref = [Data de referência]\nRETURN CALCULATE ( COUNTROWS ( NaoConformidades ), NaoConformidades[Estado] <> "Fechada", NaoConformidades[Prazo] < Ref )',
     "#,0", "NCs abertas com prazo anterior à data de referência."),
    ("Qualidade", "Tempo médio de fechamento (dias)", "AVERAGE ( NaoConformidades[DiasParaFechar] )", "0.0", "Dias entre abertura e fechamento das NCs fechadas."),
    ("Qualidade", "Índice de refugo %", "DIVIDE ( SUM ( ProducaoDiaria[Refugo] ), SUM ( ProducaoDiaria[PecasBoas] ) + SUM ( ProducaoDiaria[Refugo] ) )", "0.00%",
     "Refugo sobre o total produzido."),
    ("Qualidade", "Disponibilidade %", "1 - DIVIDE ( SUM ( ProducaoDiaria[HorasParadas] ), COUNTROWS ( ProducaoDiaria ) * 24 )", "0.0%",
     "Horas em operação sobre as horas do período (24 h por injetora por dia útil)."),
]

# Indicadores do resumo de segunda-feira: valor no mês da data de referência, mês anterior e variação.
RESUMO = [
    ("Valor aprovado", MOEDA), ("Tempo médio de aprovação (h)", "0.0"), ("% aprovadas no SLA", "0.0%"),
    ("% notas com divergência", "0.0%"), ("NCs", "#,0"), ("Índice de refugo %", "0.00%"),
]
for base, fmt in RESUMO:
    MEDIDAS.append(("Resumo", f"{base} · mês",
                    f"VAR Ref = [Data de referência]\nRETURN CALCULATE ( [{base}], DATESBETWEEN ( Data[Data], DATE ( YEAR ( Ref ), MONTH ( Ref ), 1 ), Ref ) )",
                    fmt, f"{base} no mês da data de referência."))
    MEDIDAS.append(("Resumo", f"{base} · mês anterior",
                    f"VAR Ref = [Data de referência]\nVAR Ini = EDATE ( DATE ( YEAR ( Ref ), MONTH ( Ref ), 1 ), -1 )\nRETURN CALCULATE ( [{base}], DATESBETWEEN ( Data[Data], Ini, EOMONTH ( Ini, 0 ) ) )",
                    fmt, f"{base} no mês anterior ao da data de referência."))
    MEDIDAS.append(("Resumo", f"{base} · variação",
                    f"VAR Atual = [{base} · mês]\nVAR Antes = [{base} · mês anterior]\nRETURN DIVIDE ( Atual - Antes, Antes )",
                    "+0.0%;-0.0%;0.0%", f"Variação de {base} contra o mês anterior."))


def q(nome):
    """Nome TMDL: aspas simples quando há espaço ou caractere especial."""
    simples = nome.replace("_", "").isalnum() and nome.isascii()
    return nome if simples else "'" + nome.replace("'", "''") + "'"


def bloco_m(t):
    tipos = ", ".join(f'{{"{c[0]}", {TIPOS[c[1]][1]}}}' for c in t["colunas"])
    linhas = [
        "let",
        f'    Origem = if Fonte = "CSV" then LerCsv("{t["csv"]}") else error "A fonte Online entra na fase 2, com o tenant da Tucci.",',
        f'    Tipado = Table.TransformColumnTypes(Origem, {{{tipos}}}, "en-US")',
    ]
    ultimo = "Tipado"
    for i, (nome, tipo, _fmt, expr) in enumerate(t.get("derivadas", [])):
        linhas[-1] += ","
        passo = f"Derivada{i + 1}"
        linhas.append(f'    {passo} = Table.AddColumn({ultimo}, "{nome}", each {expr}, {TIPOS[tipo][1]})')
        ultimo = passo
    linhas += ["in", f"    {ultimo}"]
    return linhas


def tabela(t):
    out = [f"table {q(t['nome'])}", f"\tlineageTag: {tag('t', t['nome'])}"]
    if t.get("oculta"):
        out.append("\tisHidden")
    out.append("")
    colunas = [(c[0], c[1], c[2] if len(c) > 2 else None, c[3] if len(c) > 3 else None, c[4] if len(c) > 4 else False) for c in t["colunas"]]
    colunas += [(d[0], d[1], d[2], None, False) for d in t.get("derivadas", [])]
    for nome, tipo, fmt, resumo, oculta in colunas:
        dt = TIPOS[tipo][0]
        out.append(f"\tcolumn {q(nome)}")
        out.append(f"\t\tdataType: {dt}")
        if fmt:
            out.append(f"\t\tformatString: {fmt}")
        if oculta:
            out.append("\t\tisHidden")
        out.append(f"\t\tlineageTag: {tag('c', t['nome'], nome)}")
        out.append(f"\t\tsummarizeBy: {resumo or 'none'}")
        out.append(f"\t\tsourceColumn: {nome}")
        out.append("")
        if tipo == "data":
            out.insert(len(out) - 1, "\t\tannotation UnderlyingDateTimeDataType = Date")
            out.insert(len(out) - 1, "")
    out.append(f"\tpartition {q(t['nome'])} = m")
    out.append("\t\tmode: import")
    out.append("\t\tsource =")
    out += ["\t\t\t\t" + l for l in bloco_m(t)]
    out.append("")
    return "\n".join(out) + "\n"


def tabela_data():
    dax = [
        "VAR Inicio = DATE ( YEAR ( MIN ( Solicitacoes[DataCriacaoDia] ) ), 1, 1 )",
        "VAR Fim = DATE ( YEAR ( MAX ( ProducaoDiaria[Data] ) ), 12, 31 )",
        "RETURN",
        "    ADDCOLUMNS (",
        "        CALENDAR ( Inicio, Fim ),",
        '        "Ano", YEAR ( [Date] ),',
        '        "MesNum", MONTH ( [Date] ),',
        '        "Mes", FORMAT ( [Date], "mmm/yy" ),',
        '        "AnoMes", YEAR ( [Date] ) * 100 + MONTH ( [Date] ),',
        '        "InicioSemana", [Date] - WEEKDAY ( [Date], 2 ) + 1,',
        '        "DiaUtil", IF ( WEEKDAY ( [Date], 2 ) <= 5, "Sim", "Não" )',
        "    )",
    ]
    cols = [("Data", "dateTime", "dd/mm/yyyy", "[Date]"), ("Ano", "int64", "0", "[Ano]"), ("MesNum", "int64", "0", "[MesNum]"),
            ("Mes", "string", None, "[Mes]"), ("AnoMes", "int64", "0", "[AnoMes]"), ("InicioSemana", "dateTime", "dd/mm/yyyy", "[InicioSemana]"),
            ("DiaUtil", "string", None, "[DiaUtil]")]
    out = ["table Data", f"\tlineageTag: {tag('t', 'Data')}", "\tdataCategory: Time", ""]
    for nome, dt, fmt, src in cols:
        out.append(f"\tcolumn {nome}")
        out.append(f"\t\tdataType: {dt}")
        if nome == "Data":
            out.append("\t\tisKey")
        if fmt:
            out.append(f"\t\tformatString: {fmt}")
        out.append(f"\t\tlineageTag: {tag('c', 'Data', nome)}")
        out.append("\t\tsummarizeBy: none")
        out.append(f"\t\tsourceColumn: {src}")
        if nome == "Mes":
            out.append("\t\tsortByColumn: AnoMes")
        out.append("")
    out.append("\tcolumn Feriado = LOOKUPVALUE ( Feriado[Nome], Feriado[Data], Data[Data] )")
    out.append("\t\tdataType: string")
    out.append(f"\t\tlineageTag: {tag('c', 'Data', 'Feriado')}")
    out.append("\t\tsummarizeBy: none")
    out.append("")
    out.append("\tcolumn Ultimas12Semanas =")
    out.append("\t\t\tVAR Ref = MAX ( ProducaoDiaria[Data] )")
    out.append('\t\t\tRETURN IF ( Data[Data] > Ref - 84 && Data[Data] <= Ref, "Sim", "Não" )')
    out.append("\t\tdataType: string")
    out.append(f"\t\tlineageTag: {tag('c', 'Data', 'Ultimas12Semanas')}")
    out.append("\t\tsummarizeBy: none")
    out.append("")
    out.append("\tpartition Data = calculated")
    out.append("\t\tmode: import")
    out.append("\t\tsource =")
    out += ["\t\t\t\t" + l for l in dax]
    out.append("")
    return "\n".join(out) + "\n"


def tabela_medidas():
    out = ["table _Medidas", f"\tlineageTag: {tag('t', '_Medidas')}", ""]
    for pasta, nome, expr, fmt, desc in MEDIDAS:
        linhas = expr.split("\n")
        out.append(f"\t/// {desc}")
        if len(linhas) == 1:
            out.append(f"\tmeasure {q(nome)} = {linhas[0]}")
        else:
            out.append(f"\tmeasure {q(nome)} =")
            out += ["\t\t\t" + l for l in linhas]
        out.append(f"\t\tformatString: {fmt}")
        out.append(f"\t\tdisplayFolder: {pasta}")
        out.append(f"\t\tlineageTag: {tag('m', nome)}")
        out.append("")
    out.append("\tcolumn Value")
    out.append("\t\tdataType: string")
    out.append("\t\tisHidden")
    out.append(f"\t\tlineageTag: {tag('c', '_Medidas', 'Value')}")
    out.append("\t\tsummarizeBy: none")
    out.append("\t\tsourceColumn: Value")
    out.append("")
    out.append("\tpartition _Medidas = m")
    out.append("\t\tmode: import")
    out.append("\t\tsource =")
    out.append('\t\t\t\tlet Fonte = #table(type table [Value = text], {}) in Fonte')
    out.append("")
    return "\n".join(out) + "\n"


def main():
    (DEF / "tables").mkdir(parents=True, exist_ok=True)
    (DEF / "roles").mkdir(exist_ok=True)
    for f in (DEF / "tables").glob("*.tmdl"):
        f.unlink()
    (SM / "definition.pbism").write_text('{\n  "version": "4.0",\n  "settings": {}\n}\n', encoding="utf-8")
    (DEF / "database.tmdl").write_text("database\n\tcompatibilityLevel: 1601\n", encoding="utf-8")
    nomes = [t["nome"] for t in TABELAS] + ["Data", "_Medidas"]
    model = [
        "model Model",
        "\tculture: pt-BR",
        "\tdefaultPowerBIDataSourceVersion: powerBI_V3",
        "\tsourceQueryCulture: pt-BR",
        "\tdataAccessOptions",
        "\t\tlegacyRedirects",
        "\t\treturnErrorValuesAsNull",
        "",
        "annotation PBI_QueryOrder = " + str(["Fonte", "PastaDados", "LerCsv"] + [t["nome"] for t in TABELAS] + ["_Medidas"]).replace("'", '"'),
        "",
    ] + [f"ref table {q(n)}" for n in nomes] + [""]
    (DEF / "model.tmdl").write_text("\n".join(model), encoding="utf-8")

    pasta_padrao = r"C:\tucci-digital-solutions\portfolio\P05-painel-operacoes\data"
    expr = [
        'expression Fonte = "CSV" meta [IsParameterQuery=true, List={"CSV", "Online"}, DefaultValue="CSV", Type="Text", IsParameterQueryRequired=true]',
        f"\tlineageTag: {tag('e', 'Fonte')}",
        "",
        "\tannotation PBI_ResultType = Text",
        "",
        f'expression PastaDados = "{pasta_padrao}" meta [IsParameterQuery=true, Type="Text", IsParameterQueryRequired=true]',
        f"\tlineageTag: {tag('e', 'PastaDados')}",
        "",
        "\tannotation PBI_ResultType = Text",
        "",
        "expression LerCsv =",
        "\t\t(arquivo as text) as table =>",
        "\t\tlet",
        '\t\t    Conteudo = Csv.Document(File.Contents(PastaDados & "\\" & arquivo), [Delimiter = ";", Encoding = 65001, QuoteStyle = QuoteStyle.Csv]),',
        "\t\t    Cabecalho = Table.PromoteHeaders(Conteudo, [PromoteAllScalars = true]),",
        "\t\t    // Campo vazio no CSV vira nulo, para datas e números não darem erro na tipagem.",
        "\t\t    SemVazios = Table.ReplaceValue(Cabecalho, \"\", null, Replacer.ReplaceValue, Table.ColumnNames(Cabecalho))",
        "\t\tin",
        "\t\t    SemVazios",
        f"\tlineageTag: {tag('e', 'LerCsv')}",
        "",
        "\tannotation PBI_ResultType = Function",
        "",
    ]
    (DEF / "expressions.tmdl").write_text("\n".join(expr), encoding="utf-8")

    for t in TABELAS:
        (DEF / "tables" / f"{t['nome']}.tmdl").write_text(tabela(t), encoding="utf-8")
    (DEF / "tables" / "Data.tmdl").write_text(tabela_data(), encoding="utf-8")
    (DEF / "tables" / "_Medidas.tmdl").write_text(tabela_medidas(), encoding="utf-8")

    rel = []
    for de_t, de_c, para_t, para_c, ativa in RELACOES:
        rel.append(f"relationship {tag('r', de_t, de_c, para_t)}")
        if not ativa:
            rel.append("\tisActive: false")
        rel.append(f"\tfromColumn: {q(de_t)}.{q(de_c)}")
        rel.append(f"\ttoColumn: {q(para_t)}.{q(para_c)}")
        rel.append("")
    (DEF / "relationships.tmdl").write_text("\n".join(rel), encoding="utf-8")

    filtro = ("CentroCusto[Codigo] IN CALCULATETABLE ( VALUES ( MapaGerente[CentroCusto] ), "
              "MapaGerente[Email] = USERPRINCIPALNAME () )")
    (DEF / "roles" / "Gerente.tmdl").write_text(
        "role Gerente\n\tmodelPermission: read\n\n"
        f"\ttablePermission CentroCusto = {filtro}\n\n"
        "", encoding="utf-8")
    (DEF / "roles" / "Diretoria.tmdl").write_text(
        "role Diretoria\n\tmodelPermission: read\n", encoding="utf-8")
    print(f"{len(TABELAS) + 2} tabelas, {len(RELACOES)} relações, {len(MEDIDAS)} medidas em {DEF}")


if __name__ == "__main__":
    main()
