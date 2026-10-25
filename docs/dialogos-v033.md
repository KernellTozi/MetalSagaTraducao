# Diálogos v033 — controles restantes, texto nativo e auditoria consolidada

Rodada focada nas pendências do MAP.MCT. **14 registros recuperados e traduzidos**,
com oito variantes de controle/lexema original e seis registros que continham
bytes japoneses. As 5.969 traduções anteriores permanecem intactas.

| Medida | Antes | Agora |
|---|---:|---:|
| Registros MAP alterados | 5.969 | **5.983** |
| Registros conhecidos | 7.231 | 7.231 |
| Adiamentos técnicos | 41 | **27** |
| Destes, nomes N$3 preservados | 19 | 19 |
| Registros nativos adiados | 14 | **8** |
| Outros controles adiados | 8 | **0** |

Isso não comprova que todo o jogo foi descoberto/traduzido. Os 160 registros
sinalizados para revisão editorial incluem nomes, expressões e efeitos; não são
160 falas narrativas automaticamente liberadas. A tabela de rótulos de falantes
continua protegida e foi catalogada separadamente nesta rodada.

## Conteúdo e uso

Traduzidos o vendedor de mapas Sodam Insein, convite/despedida de Hanz,
preocupação com o estado do protagonista, depoimento do Ex-BB Trooper,
uma fala de Syd, quatro comemorações de clientes do bar e o aviso de acesso
à sala de máquinas do trem. Nomes dos quatro mapas coincidem com os já
traduzidos no inventário. Risadas de Syd, estrela e pontuação nativas permanecem.

Abra **Iniciar-Teste.cmd**, usando:

`work/interface-v033/MetalSaga-ptbr-interface-v033.iso`

SHA-256: `7d70d3e99632b6e8df1a7c66db1e66c4d69eaea3ceec878a037ed5b550566f9e`

Tamanho: 1.704.427.520 bytes. Preflight de hash/tamanho/relatório/journal/partial
e inicialização limpa permanecem obrigatórios. Nenhuma navegação PCSX2 foi
realizada nesta rodada. O usuário confere essas cenas em partida normal,
observando nomes, títulos, opções, preços, estrela, pontuação e avanço das falas.

`Preparar-Interface.cmd` valida as receitas atuais sem gerar ISO. Reprodução em
uma pasta nova, sem sobrescrever imagens:

```powershell
python tools/build_translation_pilot.py --draft translations/regiao-inicial-v033.json --interface-draft translations/interface-v033.json --output work/interface-v033-reproducao --compact-output --build-iso
```

## Política v014: preservação de variantes do original

`fixed-record-reviewed-dialogue-quirks-v014` herda v013. Ferramenta
`tools/control_dialogue_quirks.py`; lexer histórico e permissões anteriores
permanecem iguais. Somente as seguintes formas adicionais foram reconhecidas:

- `%M_1` e `%M_4`: o leitor retorna zero para o primeiro argumento omitido,
  sem consumir `_`; o handler salta o separador e lê 1 ou 4. Produz comando
  de tipo 8, com valores empacotados 0/1 ou 0/4. Não inferir por isso personagem,
  retrato ou semântica geral de todos os parâmetros M.
- `%T0`: argumento literal zero, distinto da variável de `%T$0`. Handler e
  accessors preservam o lookup original de entidade/título, sem ler variável.
- `%NO`: o `O` é letra, não zero. O leitor retorna argumento zero sem consumi-lo.
  No caminho inspecionado ele fica como resíduo literal. O lexema completo é
  preservado, sem substituição silenciosa por `%N0`.
- `%500 G`, `%5000 G`, `%8000 G` e `%1000 G`: preservação exata dos lexemas
  observados. No dispatch genérico inspecionado, o primeiro dígito após `%`
  segue o handler padrão de descarte. O restante fica literal. Não foi executado
  o renderizador completo de escolhas, nem comprovada a apresentação final
  desses preços. Não foram removidos `%`, trocados números ou alterada cobrança.

Essas duas últimas famílias contêm possíveis problemas preexistentes. Reconhecer
seu consumo e preservar bytes autoriza traduzir as frases ao redor; não significa
que o erro de origem foi corrigido. Conferência visual e prova específica do
caminho das escolhas precedem uma eventual correção futura.

Evidências: leitor 0x1B5A30..0x1B5AD0; M em 0x1B5C5C..0x1B5CAC; N em
0x1B5CAC..0x1B5CE0; T em 0x1B5D2C..0x1B5D74; dispatch em 0x33DD60 e
descarte padrão em 0x1B5E84. Probes de instruções originais em RAM sintética:
dois M, quatro T literais, N sem argumento e três dígitos no dispatch padrão.
Não executam inicialização de entidades, renderização completa ou PS2.

Lexemas completos, resíduos, ordem, quebras, escolhas, spans vazios, rótulos,
cabeçalhos, offsets e tamanhos permanecem vinculados. Somente slots fixos,
sem crescimento por segmento frente à origem; sem repack para esta família.
Uma falha recusa o lote inteiro. Outros índices/sintaxes continuam bloqueados.

## Seis registros nativos específicos

`tools/dialogue_native_review.py` permite edição somente de seis IDs vinculados
ao hash integral do registro original: 07B264E0, 128226B4, 128226FC, 12822744,
12822790 e 13709CC0, todos da família msg. Não libera entradas japonesas em geral.

Os quatro textos do bar foram contextualizados com mensagens vizinhas sobre
agradecer uma rodada e elogiar a generosidade do protagonista. O aviso do trem
está entre chegada a East Zero e acesso a carga/restaurante/cassino. Essa
evidência local não exige atribuir identidades canônicas a índices de retrato.

O texto novo usa o codec PT-BR do projeto, mantendo apenas **☆ = 81 99** no
fim da fala de Syd e **。 = 81 42** antes da primeira quebra no aviso do trem.
São bytes nativos já presentes nessas origens, não mapeamentos CP932 de acentos.
O codec global não mudou. Símbolos, posições e quantidade são exigidos; não
se pode inserir japonês arbitrário ou usar esses símbolos em outros registros.

Verificados os hashes das seis origens e os glifos de suas sequências nativas
nas duas GFI originais. JIS e bitmaps ficam fora da linha 0x23 reservada ao PT-BR.
Fontes/layout v005 e todos os bancos gráficos permanecem idênticos à v032.
Decodificação combinada é usada somente para leitura/verificação de largura
desses registros; a entrada editável continua restrita ao codec e símbolos
explicitamente autorizados. Não usar UTF-8/CP932/Windows-1252 como substituto
da codificação do projeto.

## Auditoria local reutilizável

**Auditar-Traducao.cmd** agora consolida as pendências em um único arquivo:

`work/dialogos-pendencias-atual.json`

Pode ser executado novamente sem IA/APIs/internet. Substitui apenas sua própria
saída, preservando originais e sem criar ISO. Reconstrói o plano em memória
pelas receitas vinculadas por hash e usa mmap no arquivo grande. A ferramenta
anterior de cobertura continua disponível por CLI para reproduções históricas.

O catálogo local contém IDs, offsets, capacidades, textos/bytes de origem,
referências e grupos para investigação. Esses originais ficam somente em work/.
O resumo público em `reports/dialogos-pendencias-v033.json` contém metadados.

Auditoria adicional: **2.741 blocos / 61.356 comandos SSD**. Dos comandos fora
dos 13 layouts textuais conhecidos, foram examinados **54.125 registros** e
781.072 bytes de payload por um filtro de sequências ASCII com espaços.
Foram encontrados **zero novos candidatos por esse filtro**. Isso não cobre
textos curtos, nativos, comprimidos ou fora dos SSD indexados e não comprova
100% de cobertura do MAP.MCT.

Rótulos de falantes: **134 valores únicos / 1.527 referências**, incluindo
nomes próprios, marcadores e possíveis funções genéricas. Foram deduplicados
com offsets/capacidades/hashes e mantidos não editáveis. Exemplos genéricos
incluem Innkeeper, Old Woman e Railroad Staff, mas não se autoriza tradução
por aparência: investigar o consumidor, limites e possíveis vínculos a retratos
antes de liberar edição. Nomes próprios/Hunter/Soldier permanecem protegidos.

Primeira evidência desse consumidor: calls de msgn em 0x1C6548 e das escolhas
nomeadas em 0x1C6DE0 encaminham o ponteiro à rotina 0x1FD968. Quatorze palavras
de instrução foram vinculadas ao ELF original. O setter retém a origem,
transforma o retorno de um helper com +4/máscara de alinhamento, armazena outro
retorno em objeto+0x34 e encaminha origem/destino a um terceiro helper. Isso
sugere alocação por comprimento e cópia de string, mas os helpers, desenho e
dependências de retrato ainda precisam de prova. Essa inspeção estática não
executou instruções e não libera os rótulos; evidências ficam no resumo público.

## Pendências e verificação

Os 27 adiamentos restantes são 19 nomes de tanques N$3 já destinados à
preservação e oito ocorrências japonesas com a mesma sequência curta. Não
foram declaradas debug, falsos positivos ou traduzidas por adivinhação. Ainda
precisam de contexto; permanecem não editáveis. Os 160 sinais editoriais,
458 sugestões de nomes/expressões e 603 registros de controles/pontuação são
categorias de triagem, não autorização nem quantidade obrigatória de traduções.

Comparação integral v032→v033: **917 bytes em 14 registros MAP**, com todos os
demais bytes, interface, fontes, arte e diretório idênticos. Evidências, testes
e limitações em `reports/interface-v033.json`; triagem estrutural em
`reports/plano-pendencias-v010.json`. A interface mantém 3.526 campos.

**107 testes distintos aprovados**: 53 de controles, quatro de codec nativo,
quatro de regressão real do lote, 12 de reinserção, seis de cobertura, sete de
auditoria consolidada, sete de preflight, seis de planejamento, cinco de retenção
e três da alpha. Reexecuções não somadas. A suíte completa de interface não
foi repetida: seus textos/renderizadores não mudaram, e a comparação integral
da imagem e a recompilação final conferem todos os recursos anteriores.

Próxima frente recomendada: investigar os rótulos genéricos dos falantes sem
alterar nomes próprios; contextualizar as oito ocorrências nativas repetidas;
revisar rubricas/expressões e conferir os lexemas suspeitos no jogo. Não contar
preservações como tradução nem repetir a investigação dos N$3 já decididos.

Mantidas cinco ISOs de trabalho e alpha permanente protegida. Nenhum original,
BIOS, save ou configuração foi modificado. O desligamento solicitado na rodada
anterior já foi atendido; não é uma instrução recorrente desta rodada.
