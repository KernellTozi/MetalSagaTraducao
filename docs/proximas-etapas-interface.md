# Próximas etapas — menus de personagem e lojas

**Estado após a v017:** primeiro lote de descrições de equipamentos entregue:
114 textos/126 itens, com nomes e dados intactos. Das 175 propostas revistas,
61 aguardam solução de espaço; 392 descrições ainda não foram revistas.
O catálogo local único inclui essas classes. Ver `docs/interface-v017.md`.
Limpeza reduz os iniciadores da raiz a cinco e as ISOs de trabalho a cinco.

**Estado após a v016:** foram localizados e traduzidos os corpos das 41 mensagens
da tabela Satcom em S_PACK e as descrições das 40 fichas de procurados, mais
38 assuntos. São 119 campos novos, 1.039 acumulados. Remetentes, nomes,
recompensas e tabelas de offsets permanecem intactos. A localização do correio
deixa de ser pendência para essas 41 entradas; não presumir cobertura de todo
o jogo. Ver `docs/interface-v016.md`. O catálogo local único incorpora 203 campos
dessas tabelas, sem criar revisões por mensagem. As descrições históricas abaixo
de correio ainda não localizado continuam apenas como histórico.

**Estado após a v015:** o lote amplo planejado abaixo foi aplicado: 278 textos
distintos da tabela UI S_PACK, usados por 333 IDs, e um formato do personagem.
São 920 ocorrências de interface, com 39 alvos S_PACK preservados. O perfil
opt-in, limites, testes e pendências estão em `docs/interface-v015.md`. O catálogo
local único agora cruza a v015. As descrições abaixo de tabela ainda não editável
registram a fase anterior ao novo compilador; não autorizam outras tabelas.

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

## Levantamento consolidado executado após a v014

O pedido de ampliar o trabalho e reduzir arquivos foi atendido com um único
catálogo local reutilizável: **`work/planejamento-interface.json`**. A ferramenta
`tools/plan_interface_menus.py` atualiza esse mesmo JSON de forma atômica, sem
pastas por data, rascunhos separados, PNGs, ISOs ou tradução nesta rodada.
Os textos originais/bytes extraídos ficam somente nesse arquivo fora do Git.
Scripts, testes e este documento são versionados; os catálogos anteriores não
foram apagados nem regenerados desnecessariamente.

### Descoberta principal: a interface dentro de S_PACK

A primeira entrada do SDA em **0x35000**, que possui 22 entradas, começa em
**0x35070** e termina em **0x37070**: um bloco de **8.192 bytes**.
Seu primeiro u32 é **378**, seguido por 378 offsets relativos de 32 bits.
O cabeçalho ocupa **0x5EC/1.516 bytes**, exatamente o primeiro offset de texto.
Todos os ponteiros têm limites e NUL válidos; os alvos distintos não se sobrepõem.

- **378 IDs de ponteiro**, preservados individualmente no catálogo.
- **317 alvos de texto distintos**, com **61 referências compartilhadas**.
- **315 alvos em bytes ASCII** e dois com bytes nativos não mapeados
  (`82 6E` e `82 77`), preservados sem tentativa de interpretar como acentos PT-BR.
- 6.348 bytes de conteúdo, 317 terminadores e 1.516 bytes de cabeçalho:
  **11 bytes não ocupados** no bloco. Isso não autoriza usar esses bytes como
  capacidade extra nem comprova o tamanho do buffer em execução.

As strings incluem ações do inventário, status/equipamento, compra/venda de
itens/armas/peças/munição, modificações, presentes, mercado paralelo, reparos,
sucata, abastecimento, aluguel, armazenamento, Hunter Office, resgate e pintura.
Portanto, investigar **a tabela de interface de S_PACK passa a ser necessário
agora**, enquanto a tradução das tabelas gerais de nomes/descrições de itens
permanece para depois. Não tratar todo S_PACK como uma única etapa de itens.

Esses 317 alvos não equivalem a 317 traduções novas: existem nomes próprios,
símbolos, textos compartilhados e termos que devem permanecer. Os registros
estão classificados como **identificados, ainda não editáveis**. Falta vincular
o leitor em execução, seus limites, os consumidores e a política de reinserção.
Não presumir que o formato de offset observado libera repack automaticamente.

Uma mensagem em **0x35CE7** monta uma palavra inglesa com `%screased`.
Preservar somente a sequência printf não garante português correto: precisamos
conferir os argumentos e a composição da frase antes de editar esse caso.
O catálogo preserva controles, bytes, NUL, offsets, hashes e todos os IDs que
compartilham cada alvo. Não separar aliases para obter traduções diferentes
sem nova evidência sobre os consumidores.

### Personagem e catálogo ELF

Foram cruzadas as **4.297 entradas históricas e os dois literais adicionais já
liberados**, totalizando 4.299 entradas, com a receita v014. Há 298 campos dessa
lista já traduzidos e três restaurações explícitas de Total. Esses números não
substituem as 641 ocorrências totais da interface, que incluem outros recursos.

A seleção conservadora deixa **22 candidatos com referência a revisar** e
**23 candidatos sem referência suficiente**. Não são aprovações de tradução:
incluem formatos, rótulos compartilhados e situações que exigem contexto.
Nomes/títulos, fragmentos curtos, formatos sem texto e possíveis nomes técnicos
são classificados separadamente por heurísticas, sem declarar falsos positivos
comprovados nem ignorá-los definitivamente.

Também foi identificado o literal multilinha em **0x32B6A0**, com **51 bytes**,
contendo campos de título/ataque/defesa/EXP. Possui referência candidata em
**0x118A20/0x118A28**, mas fica fora do catálogo histórico por conter quebras de
linha. Precisa de política específica e prova de consumo/aliases; não ampliar
a regex geral para aceitar indiscriminadamente outros dados.

### Próximo lote amplo, com dependências definidas

1. Vincular leitor/consumidores da tabela UI de S_PACK, confirmar alocação,
   comprimentos máximos e possíveis referências externas. Provar round-trip
   sem alterações antes de liberar edição; investigar redistribuição somente
   dentro do bloco comprovado, preservando o grafo de aliases e bytes nativos.
2. Em paralelo técnico, conferir o formatador multilinha do personagem e os
   rótulos ELF selecionados. Preservar campos existentes e resolver termos
   ambíguos pelo contexto, como Coat, em vez de adivinhar equivalentes.
3. Preparar **um único lote consolidado** de personagem/inventário e lojas/
   serviços compatíveis, em vez de uma versão por tela. A mesma revisão local
   deve agrupar a frase, seus valores/controles e os contextos compartilhados.
4. Executar testes, construir uma ISO consolidada e comparar a imagem integral.
   O usuário verifica menus e compras/vendas em uma passagem normal. Recursos
   bloqueados ficam registrados no mesmo catálogo, sem impedir os demais.

Reprodução local, sem IA/API ou internet:

```powershell
python tools/plan_interface_menus.py
python -m unittest discover -s tests -p "test_menu_planning.py" -v
```

**Seis testes passaram**, cobrindo aliases não monotônicos, bytes nativos,
ponteiros/cabeçalhos/terminadores inválidos, offsets interiores, controles e
preservação da classificação dos campos já traduzidos. O levantamento foi
executado contra os originais vinculados por hash. A v014 permanece no iniciador;
não houve nova ISO, teste no PCSX2, cópia OneDrive ou tradução nesta rodada.
