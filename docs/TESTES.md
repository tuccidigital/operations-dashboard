# Testes · Painel de Operações

Conferências para fazer na primeira abertura no Power BI Desktop. Os números de controle foram somados direto dos CSVs por `scripts/conferir.py` (e gravados em `docs/numeros-de-controle.json`); se o relatório mostrar outro valor, a medida ou o relacionamento está errado.

## 1. Abre e atualiza sem credenciais

- [ ] Abrir `Painel Operacoes.pbip`, Página Inicial > Atualizar, com `Fonte = CSV` e `PastaDados` apontando para `data\`.
- [ ] Nenhuma tabela com erro na atualização; nenhum visual com "Não é possível exibir o visual".

## 2. Números de controle

Sem filtro (ou com o filtro indicado), cada valor deve bater exatamente:

| # | Número | Valor esperado | Onde conferir |
| --- | --- | --- | --- |
| 1 | Valor aprovado (todo o período) | R$ 3.178.873,19 | Página Compras, cartão "Valor aprovado", sem filtro de mês |
| 2 | Valor aprovado no mês de set/2026 | R$ 370.829,02 | Resumo de segunda-feira, com o mês set/2026 |
| 3 | % de notas com divergência | 4,7% | Página Fiscal, sem filtro |
| 4 | % de solicitações aprovadas no SLA | 89,2% | Página Compras, sem filtro |
| 5 | Índice de refugo | 2,59% | Página Qualidade, sem filtro |
| 6 | Não conformidades (todo o período) | 72 | Página Qualidade, sem filtro |

Para recalcular depois de gerar dados novos: `python scripts/conferir.py`.

## 3. Segurança por linha

- [ ] Modelagem > Exibir como > marcar `Gerente` e, em "Outro usuário", `caio.ferraz@lumina.example`.
- [ ] O relatório mostra só o centro de custo CC-200 (Produção): orçamento, solicitações e notas de outros centros somem.
- [ ] Exibir como `Diretoria`: tudo volta a aparecer.

## 4. Qualidade do modelo

- [ ] Nenhuma medida com erro (painel Dados, ícone de alerta).
- [ ] Medidas em pastas (Compras, Fiscal, Qualidade, Resumo, Referência) e com descrição.
- [ ] A tabela `Data` está marcada como tabela de datas e termina em 31/12 do último ano dos dados.

## 5. Visual

- [ ] Tema `tucci-powerbi-theme.json` aplicado (série 1 musgo, série 2 cobalt).
- [ ] Toda página tem a legenda "Dados fictícios".
- [ ] Detalhar a partir de um centro de custo abre a página de detalhe filtrada.
