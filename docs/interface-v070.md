# Metal Saga PT-BR — candidata final v070

Esta é uma candidata para a revisão jogando, não uma declaração de cobertura
ou validação visual de 100% do jogo. Integra os relatos de 06/11/2026 sobre a
interface v069 e o trabalho tecnicamente seguro das pendências conhecidas.

## Correções aplicadas

| Relato | Resultado |
|---|---|
| NAME no menu principal | NOME, com glifos do atlas original |
| OPTIONS MENU ao apertar Start | AJUSTES, no mesmo estilo do cabeçalho |
| Tank Stop | Sem tanques, letras mais pesadas e fundo preto com fade |
| Ship Stop | Sem navios, com o mesmo tratamento e símbolo preservado |
| Unknown Cave | Caverna desconhecida, duas ocorrências de nomes de nós |
| Trader Camp | Acampamento de mercadores, 16 ocorrências de nomes de nós |
| Noooooo de McKinley | Nãããão!!; outra ocorrência de grito também revista |
| Sell price ao vender equipamento | Venda, preservando o valor e seu alinhamento |
| Yes/No na saída dos minigames | Sim/Não na segunda tabela de opções |
| Diário sobre Binramen | MC… sei lá o quê... Será / que é o MC Hamir? |
| Máq./Veíc./Descon. | Máquinas/Veículos/Desconhecidos por extenso |
| Minério ignoto | Minério pequeno, conforme pedido anterior e ordem atual de resolver as pendências |

O título próprio Binramen e MC Hamir permanecem iguais. A barra na explicação
da tabela acima representa a quebra de linha original, não uma barra visível.
Os nove títulos de entrada dos acampamentos já herdam **- Acampamento -**
via aliases do registro `map.supr.1fbbfa34`; foram conferidos e preservados.
O inglês nesses registros originais não representa inglês na ISO compilada.
Hunter, Soldier, MAIN/SUB/SE, músicas, personagens, equipamentos e demais
decisões de preservação permanecem. Poker/Blackjack e Royal Flush, Straight
Flush, Full House e Flush continuam conforme a v069.

## Mecanismos e evidências

Receita `translations/interface-v070.json`, pai v069 integral, MAP v048
herdando v047, layout `ptbr-layout-v005`. Ferramentas:
`tools/final_candidate.py`, `tools/category_pool.py`, manifesto
`translations/candidata-final-v001.json`.

### Cabeçalhos e avisos

Somente NAME em `[4,60,62,72]` e OPTIONS MENU em `[4,216,156,228]` são
revisados no plano S_PACK+0x8C830. Letras são compostas no tamanho nativo;
J é derivado da base U do próprio EQUIPMENT LIST, preservando a curva inferior
e a haste direita. Não se altera fonte GFI global ou outro cabeçalho.

HMAPAC.SDA+0x80 mantém o plano 256×256/8bpp, paleta e alpha originais.
São alteradas somente as faixas `[90,44,192,70]` e `[90,118,192,144]`.
O fade horizontal preto é recuperado da moda dos pixels pretos das colunas
das duas inscrições, com interpolação entre colunas vizinhas quando as letras
ocultam toda a amostra. Os valores são convertidos aos índices pretos/alpha
existentes. GANM 0/2 e os símbolos ficam intactos.

Arial Black instalada localmente é vinculada por hash no manifesto. Sem TTF
distribuída. O reforço por dilatação foi descartado por fechar os espaços
internos; a versão entregue usa o peso próprio da fonte, sem essa dilatação.
É aproximação visual do original, sujeita à conferência do usuário.

### ELF, diário e nomes de locais

- Formato em 0x341670: `%%I%02d%s`, quebra e `%11dG` imutáveis.
  O rótulo Venda ocupa a mesma coluna de dez caracteres.
- Yes/No em 0x349A18/0x349A20: células originais de oito bytes. A chamada
  0x14C500..0x14C530 constrói os dois ponteiros em a2/a3 para o mesmo
  construtor; não depende de supor que a ausência de referência direta a
  Yes signifique texto sem uso. Ambos os valores continuam terminados em NUL.
- Diário 16: somente corpo, capacidade 51 bytes. Reticência nativa 81 63,
  quantidade/ordem de controles e o separador de linha são preservados.
- Locais: 18 campos de 32 bytes em nós tipo 2/7 já compreendidos. Alteração
  limitada ao prefixo usado pelo nome e aos zeros dentro do mesmo campo;
  árvores, offsets, flags, corpos e scripts ficam intactos.
- Gritos: somente `map.msg.040f10d4` e `map.msg.01dee21c`, pelos slots e
  controles existentes. Não substituir No globalmente. O segundo mantém
  McKinley, Eddy, hesitação e a expressão *gasp*.
- Item 665: somente os 24 bytes do campo comprovado; Minério pequeno ocupa
  exatamente 16 bytes no codec experimental. Demais dados do item intactos.

### Categorias completas sem aumentar o executável

O banco ELF `[0x349248,0x349290)` tem 72 bytes. Os nove nomes finais com NULs
cabem nesse mesmo intervalo: Desconhecidos, Bio, Cyber, Máquinas, Veículos,
Alvos, Normal, Furtivo e Abrigo. Bio/Cyber são mantidos como categorias usuais.

As referências dos três conjuntos originais são recenseadas:

- primeiro banco: ponteiros absolutos em dados, incluindo aliases;
- segundo: tabela de seis ponteiros em 0x2654C0;
- terceiro: seis pares LUI/ADDIU que constroem ponteiros na pilha.

O primeiro consumidor copia onze ponteiros, não onze slots de texto. As
janelas desses consumidores estão vinculadas por hash. Todas as palavras
absolutas alinhadas do ELF são recenseadas independentemente do catálogo de
referências; os pares de código mantêm registradores/opcodes e parte alta.
Só a parte baixa necessária ao novo endereço é revista. As strings antigas
dos bancos secundários continuam fisicamente preservadas.

O compilador coalesce somente os seis patches históricos contidos no banco
primário. O comparador reconstrói a sobreposição anterior dentro dos mesmos
72 bytes antes de comparar a ISO integralmente. Não há segmento novo, BSS,
reserva de heap, crescimento de arquivo ou mudança de diretórios.

## Limitação real: 13 rótulos de falantes

Worker×9, Man, Transporter, Cat e Dog continuam em inglês nos 13 rótulos
explícitos sem espaço. Não confundir com os nomes padrão já traduzidos.
Retomamos a investigação: os 12 consumidores de 0x4B599C foram classificados;
seis passam esse endereço como limite inferior para a função de faixa de
memória em 0x2A0130, com argumentos conferidos por execução simbólica limitada.

Isso ainda não prova uma reserva persistente para o hook em todos os caminhos
de heap, reset e carregamento. A limpeza da BSS alcança 0x4B59A0. O protótipo
continua bloqueado para aplicação; não se aumentou o ELF nem se inseriram
marcadores na candidata final. Relatório `reports/falantes-memoria-v002.json`,
reprodutor `tools/classify_speaker_storage.py`, contexto em
`docs/falantes-lookup-v001.md`. Não repetir buscas de padding já esgotadas.

Dummy, UP, DOWN e Damage Override ficam preservados por decisão contextual
anterior do usuário. Referências editoriais remanescentes incluem nomes
próprios e termos protegidos; não são automaticamente frases esquecidas.
Novos textos fora dos recursos conhecidos ainda podem aparecer em partida.

## Reprodução e manutenção

```powershell
python tools/final_candidate.py
python -m unittest discover -s tests -p test_final_candidate.py -v
python -m unittest discover -s tests -p test_speaker_storage_classification.py -v
python tools/build_translation_pilot.py --draft translations/regiao-inicial-v048.json --interface-draft translations/interface-v070.json --compact-output --build-iso --output work/interface-v070
```

O construtor exige pasta de saída nova. Preparação e compilação utilizam os
originais imutáveis; nenhum cache de investigação substitui essa conferência.
Resultados intermediários e previews ficam em `work/final-v070/`, fora do Git.

`tools/package_final_candidate.py` verifica a construção, prepara o plano e
consulta a Área de Trabalho pelo Windows. Com `--apply`, confere as cópias
integrais de manutenção e da Área de Trabalho antes de remover qualquer ISO
antiga reconhecida. Recusa arquivos desconhecidos ou destinos com conteúdo
diferente e registra falhas de exclusão, inclusive arquivos em uso.

A autorização atual de apagar as versões anteriores substitui a proteção
específica da v059 somente depois da nova cópia de manutenção conferida.
O novo backup é `dist/manutencao-v070/MetalSaga-ptbr-manutencao-v070.iso`;
não deve ser usado como destino de patches futuros. Receitas, relatórios,
scripts e histórico Git das versões antigas permanecem preservados.

## Conferência em partida

Abra Iniciar-Teste.cmd; conferir NOME/AJUSTES, as duas proibições e seu fade,
os dois locais, venda de equipamento, sair dos minigames, Binramen, grito de
McKinley e categorias completas nas diferentes telas. Os testes e a inspeção
de previews não equivalem a essa passagem no PCSX2.

## Resultado da entrega

- Construção válida, zero recusas: 6.044 registros MAP alterados, 5.991 com
  corpo/opções alterados, 991 referências de falantes, 4.666 unidades UI.
- SHA-256: `5a576e647291e9255b04856e22dfb5bdaabd4ecbe1ebee751f26e856eb439f4c`.
  Tamanho: 1.704.427.520 bytes em cada uma das três cópias atuais.
- Comparação integral v069→v070 aprovada: 5.094 bytes diferentes em 50
  patches previstos; diretório, fontes e layout idênticos. Relatório
  `reports/interface-v070-delta.json`.
- 30 testes distintos aprovados: 11 de recursos/compilação, quatro de cópia
  e ordem segura de exclusão, três de classificação de memória, sete de
  preflight e cinco de retenção. Fixtures de exclusão/cópia são pequenas e
  isoladas em diretórios temporários, sem tocar as ISOs reais.
- Preflight aprovado; sem journal ou arquivo parcial pendente. Atalhos
  simulados e apontando para v070. Auditor de nomes históricos: zero bloqueios.
- Cópias de manutenção e Área de Trabalho conferidas por tamanho e SHA-256
  integral antes de remover as ISOs antigas. Manutenção somente leitura.
  As versões v066–v069 e o backup v059 foram removidos pela entrega; v065
  já havia sido retirada pela retenção ao construir a nova imagem.
  Nenhuma falha de exclusão. Ledger em `reports/entrega-candidata-v070.json`.
- Área de Trabalho: `C:\Users\Kernell\Desktop\MetalSaga-PTBR-Candidata-Final-v070.iso`.
- Restam uma ISO de trabalho e uma de manutenção no workspace, além da
  entrega externa solicitada. A ISO original continua em JOGO e não entra
  nessa contagem ou limpeza. Receitas e relatórios históricos preservados.
- Não houve navegação no PCSX2 pelo Codex. A decisão de considerar a candidata
  pronta cabe à revisão do usuário. Os 13 rótulos bloqueados permanecem
  explícitos no relatório, sem tentativa insegura de escondê-los.

Resumo verificável em `reports/interface-v070.json`.
