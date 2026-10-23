# Próximas etapas — menus de personagem e lojas

Planejamento solicitado após a entrega da interface v014. Esta rodada não
traduz textos nem altera a ISO. O próximo trabalho será organizado por telas
completas e mecanismos comprovados, em lotes amplos.

## Base atual e cuidado com a cobertura

A base é interface v014, MAP v030 e layout v005: 641 ocorrências de interface,
incluindo 44 gráficas, com 5.892 traduções MAP. Já existem traduções parciais em
status, veículos, equipamentos e rótulos comuns. A receita ELF tem, por exemplo,
50 campos no grupo vehicle_and_status e 12 em battle_status. Esses grupos não
comprovam que qualquer uma dessas telas esteja completa. A arte do título foi
aprovada em preview e aplicada; a execução da v014 aguarda teste do usuário.

Antes de traduzir novamente, cruzar o catálogo e as receitas existentes para
classificar cada campo como traduzido, preservado por regra, pendente de
localização ou bloqueado tecnicamente. Não converter as 4.297 strings ASCII
catalogadas em uma lista automática de interface: há debug e nomes técnicos.

## Ordem decidida

1. **Personagem, inventário e equipamentos.** Fechar os rótulos ainda em inglês
   das telas de status, atributos, habilidades, uso/organização de itens,
   equipar/remover e confirmações associadas. Esta etapa trata a interface que
   apresenta o inventário; não pressupõe traduzir todos os nomes/descrições dos
   itens. Investigar somente os campos que realmente faltam, sem retraduzir os
   já aprovados para aumentar contagens.
2. **Lojas e serviços.** Comprar/vender, quantidade, preço, total, saldo,
   capacidade, confirmações e recusas. Agrupar lojas de armas/itens/peças e
   serviços semelhantes quando compartilhem estruturas comprovadas. Os valores
   variáveis e as transações do jogo não mudam. Não presumir que toda fala de
   vendedor pertença ao mesmo recurso ou formato.
3. **Gestão de veículos e batalha.** Fechar peças, munição, transferência,
   reparos, aluguel, carga/peso e avisos relacionados ainda pendentes. Preservar
   MAIN/SUB/SE, nomes de tanques e equipamentos únicos. Acumular teste visual
   dos acentos/colunas de batalha sem bloquear a tradução de menus independentes.
4. **Demais interfaces frequentes.** Completar lacunas do Satcom, mensagens,
   nomeação e telas auxiliares. O conteúdo do correio continua sem localização
   comprovada; não confundir seus cabeçalhos já traduzidos com os corpos.
   TITLE/BACK na nomeação exigem contexto de uso; senha e gráficos restantes
   recebem tratamento próprio. Priorizar frequência de uso e reaproveitamento
   técnico; minijogos e ajustes cosméticos isolados podem esperar.
5. **Itens e descrições em escala.** Com a interface consolidada, estruturar as
   tabelas de S_PACK.SDA e investigar arquivos relacionados por evidências.
   Preservar nomes únicos e adiar entradas cujo espaço exija uma solução ainda
   não comprovada. Não presumir texto por extensões/nomes como BTITEM.DAT,
   HWEAPON.DAT, TANK.DAT ou MMBATTLE.BIN.
6. **Fechamento e revisão.** Voltar aos fragmentos MAP e controles pendentes,
   conferir contexto por conversas e executar passagem funcional consolidada.
   Os 123 adiamentos históricos v029 não devem ser reutilizados como contagem
   atual sem verificar a receita MAP v030.

## Forma de execução

- Primeiro próximo lote: personagem/inventário/equipamentos e campos comuns de
  lojas que já tenham mecanismos seguros. A meta é fechar conjuntos coerentes;
  o tamanho depende das entradas reais, sem prometer uma contagem artificial.
- Exportar para revisão local com IDs, offsets, capacidade, origem, contexto e
  controles. Traduzir em lote e preservar nomes, glossário e parâmetros.
- Literais e tabelas já comprovados usam as ferramentas existentes. Recursos
  desconhecidos ficam separados para investigação; não relaxar verificações.
- Rótulos gráficos novos seguem o procedimento das palavras completas: arte
  preparada no tamanho final, revisão visual e aplicação vinculada por hash.
  Não voltar à montagem improvisada de letras nem substituir a família de fonte.
- Uma ISO consolidada por rodada relevante, testes binários e comparação integral
  com a anterior. O usuário testa conjuntos de telas durante o jogo; não exigir
  navegação por string. Preservar alpha e limite de dez ISOs de trabalho.
- Um defeito que impeça abrir menus, usar itens, comprar/vender, salvar ou avançar
  passa à frente desta ordem. Ajustes pequenos de aparência sem impacto funcional
  entram na fila de revisão, sem interromper todo o lote.

Critério de conclusão de cada conjunto: campos conhecidos classificados,
tradução segura aplicada, lacunas e bloqueios explícitos e roteiro de teste
consolidado. A contagem de strings ou a construção da ISO não prova cobertura
completa de uma tela nem execução correta no PCSX2.
