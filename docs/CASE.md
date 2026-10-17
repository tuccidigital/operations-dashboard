---
titulo: Painel de Operações
resumo: Um painel só para a reunião de segunda-feira, com compras, fiscal e qualidade batendo entre as áreas. Power BI em PBIP, TMDL e Git.
setor: Indústria de transformação de plástico
stack: Power BI (PBIP, TMDL, PBIR), DAX, Power Query, segurança por linha
ficticio: true
video: /cases/painel-operacoes.mp4
---

## Problema

Na Lumina, cada gerente montava o próprio Excel na segunda-feira. Os números de compras, notas fiscais e qualidade não batiam entre as áreas, e Rogério Pacheco, diretor administrativo-financeiro, perdia a primeira hora da reunião discutindo qual planilha estava certa.

## O que construímos

Um relatório Power BI construído como projeto em Git: o modelo semântico em TMDL e o relatório em PBIR, revisáveis linha a linha como código.

1. **Compras, fiscal e qualidade** entram num modelo só, em estrela.
2. **Um conjunto de medidas** documentadas, com pastas e descrição, usadas por todas as páginas.
3. **Resumo de segunda-feira:** seis indicadores do mês contra o mês anterior e o que pede ação.
4. **Segurança por linha:** cada gerente vê o seu centro de custo; a diretoria vê tudo.

## Como funciona

- **Resumo de segunda-feira.** Valor aprovado, tempo de aprovação, aprovações no prazo, notas divergentes, não conformidades e refugo, cada um com a variação contra o mês anterior.
- **Compras.** Estado das solicitações, tempo por etapa de aprovação e orçamento contra realizado por centro de custo.
- **Fiscal.** Notas divergentes por fornecedor e a lista do que precisa de ação.
- **Qualidade.** Não conformidades por severidade, disponibilidade e refugo por injetora.
- **Detalhe.** Botão direito num centro de custo, qualquer página, e as solicitações dele aparecem.

## Resultado esperado

Uma versão dos números para toda a empresa. A reunião de segunda começa pela lista do que pede ação, não pela discussão de qual planilha está certa.

## Licenças necessárias

Power BI Pro para quem publica e para quem consome, ou capacidade Fabric/Premium.

## Quanto tempo levou

Modelo, medidas e relatório: cerca de 2 semanas de trabalho, partindo de fontes já organizadas.

*Empresa fictícia, dados fictícios.*
