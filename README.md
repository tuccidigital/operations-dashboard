# P05 · Painel de Operações

> Portfólio Tucci Digital Solutions. **Dados fictícios** da Lumina Componentes, empresa inventada.

## O problema

Cada gerente da Lumina monta o próprio Excel na segunda-feira. Os números não batem entre as áreas, e Rogério Pacheco, diretor administrativo-financeiro, perde a primeira hora da reunião discutindo qual planilha está certa.

## A solução

Um relatório Power BI construído como projeto (PBIP) em Git: modelo semântico em TMDL e relatório em PBIR, alimentado pelos dados de aprovações (P01), notas fiscais (P03), inspeções e não conformidades (P02), orçamento e produção.

```
Compras, Fiscal e Qualidade  →  um modelo só (estrela)  →  resumo de segunda-feira  →  reunião começa pela ação
```

## Como abrir

Requisitos: Power BI Desktop (versão atual, com "Formato de projeto do Power BI (.pbip)" ligado em Opções > Recursos de visualização, se a sua versão ainda pedir) e Python 3.10+ só se quiser gerar os dados de novo.

1. Copie a pasta do projeto para `C:\tucci-digital-solutions\portfolio\P05-painel-operacoes` (ou ajuste o parâmetro `PastaDados`).
2. Abra `Painel Operacoes.pbip` no Power BI Desktop.
3. Página Inicial > Atualizar. No modo CSV não há credenciais: o Desktop lê os arquivos de `data/`.

Para mudar a pasta: Transformar dados > Editar parâmetros > `PastaDados`.

## Parâmetros

| Parâmetro | Valores | Uso |
| --- | --- | --- |
| `Fonte` | `CSV` (padrão), `Online` | `CSV` lê `data/`; `Online` lê as listas do SharePoint e o Dataverse do tenant (fase 2) |
| `PastaDados` | caminho da pasta `data` | Onde estão os CSVs |

## Modelo

Estrela com 7 fatos (Solicitacoes, Aprovacoes, Notas, Inspecoes, NaoConformidades, OrcamentoMensal, ProducaoDiaria) e as dimensões Data, CentroCusto, Fornecedor, Colaborador, Ativo e Produto. A tabela `Data` é calculada a partir dos próprios dados e termina no fim do ano, sem datas fixas. As medidas ficam em `_Medidas`, em pastas (Compras, Fiscal, Qualidade, Resumo, Referência), todas com descrição.

**Segurança por linha:**

- `Gerente`: vê só os centros de custo dele (mapa e-mail → centro em `MapaGerente`).
- `Diretoria`: vê tudo.

Para testar: Modelagem > Exibir como > `Gerente` e, em "Outro usuário", `caio.ferraz@lumina.example`. Ele deve ver só o CC-200 (Produção).

## Páginas

1. **Resumo de segunda-feira:** 6 indicadores do mês com a variação contra o mês anterior, valor aprovado das últimas 12 semanas, centros de custo, ativos e fornecedores que pedem ação.
2. **Compras:** estados das solicitações, tempo por etapa, ranking de centros de custo, orçamento × realizado.
3. **Fiscal:** conferência de notas e divergências por fornecedor.
4. **Qualidade:** NCs por severidade, disponibilidade e refugo por injetora.
5. **Detalhe do centro de custo:** página de detalhamento (botão direito > Detalhar).

## Como o projeto é gerado

O modelo e o relatório saem de scripts, para ficarem revisáveis no Git:

```bash
python scripts/gerar_dados.py      # CSVs fictícios em data/ (semente fixa)
python scripts/gerar_modelo.py     # TMDL em "Painel Operacoes.SemanticModel"
python scripts/gerar_relatorio.py  # PBIR em "Painel Operacoes.Report" e o tema
python scripts/conferir.py         # campos do relatório x modelo e números de controle
```

Depois de editar no Desktop, salve: o próprio Desktop regrava os arquivos TMDL e PBIR. A partir daí, edite no Desktop (ou com o MCP de modelagem do Power BI) e não rode mais os geradores por cima.

## Testes

`docs/TESTES.md` traz os números de controle somados direto dos CSVs e onde conferir cada um no relatório.

## Limitações conhecidas

- O relatório foi gerado em código e validado contra os esquemas oficiais do PBIR, mas a primeira abertura no Power BI Desktop é a validação final; ajustes de layout são esperados.
- A fonte `Online` fica para a fase 2, com o tenant da Tucci.

## Licença do cliente

Power BI Pro para quem publica e para quem consome (ou capacidade Fabric/Premium).
