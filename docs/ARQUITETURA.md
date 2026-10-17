# Arquitetura · Painel de Operações

## Componentes

| Parte | Formato | Onde |
| --- | --- | --- |
| Dados de demonstração | CSV com `;` e ponto decimal, UTF-8 | `data/` (gerados por `scripts/gerar_dados.py`) |
| Modelo semântico | TMDL (compatibilidade 1601) | `Painel Operacoes.SemanticModel/definition` |
| Relatório | PBIR | `Painel Operacoes.Report/definition` |
| Tema | JSON do Power BI com a paleta Grafite & Musgo | `tucci-powerbi-theme.json` |

## Fluxo dos dados

1. Power Query lê cada CSV com a função `LerCsv` (campo vazio vira nulo) e tipa as colunas com cultura `en-US`.
2. Colunas derivadas no Power Query: dia de criação, horas até a decisão, dia de abertura da NC e dias até o fechamento.
3. A tabela `Data` é calculada em DAX do primeiro ao último ano com dados, terminando em 31/12.
4. Na fase 2 (`Fonte = Online`), as mesmas tabelas vêm das listas do SharePoint (P01, P03) e do Dataverse (P02), com o mesmo esquema de colunas.

## Relações

Todas um-para-muitos, filtro simples, das dimensões para os fatos. Três relações ficam inativas para não haver caminho ambíguo:

- `Aprovacoes[AprovadorId] → Colaborador[Id]` (use `USERELATIONSHIP` para analisar por aprovador)
- `Notas[SolicitacaoId] → Solicitacoes[Id]`
- `NaoConformidades[InspecaoId] → Inspecoes[Id]`

## Segurança

Papéis `Gerente` (filtra `CentroCusto` pelo e-mail do usuário via `MapaGerente`) e `Diretoria` (sem filtro). No serviço, atribua os grupos do Microsoft 365 a cada papel.

## Licenças para o cliente

Power BI Pro para quem publica e quem consome, ou capacidade Fabric/Premium.

## Decisões

- **Arquivos gerados por script:** o primeiro corte do modelo e do relatório é reproduzível e revisável no Git; depois da primeira abertura, o Desktop vira a ferramenta de edição.
- **Medidas de mês ancoradas na data de referência** (último dia com dados), nunca em data fixa: o resumo continua certo quando entram dados novos.
- **Variação contra o mês anterior em medidas explícitas** em vez de grupo de cálculo: mais simples de ler para quem mantém.
