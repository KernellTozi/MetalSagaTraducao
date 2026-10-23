# Interface v015 — inventário, personagem, lojas e serviços

Lote amplo sobre a v014, sem alterar sua arte aprovada, fontes/layout ou diálogos.
Acrescenta **278 textos distintos de interface S_PACK**, usados por **333 IDs de
ponteiro**, e **um formato multilinha de atributos do personagem**. Total:
**920 campos/ocorrências de interface**, contra 641 da v014. O MAP v030 mantém
5.892 traduções, 1.339 preservados e zero recusas. Não somar IDs compartilhados
como traduções distintas nem converter essa contagem em porcentagem do jogo.

## Conteúdo desta rodada

- Inventário: usar/equipar/descartar, ordenação, quantidade, confirmações e avisos.
- Personagem/equipamentos: classe, ataque, defesa, proteção, condição e habilidade;
  bloco ELF de título/ataque/defesa/EXP com parâmetros e quebras preservados.
- Compra/venda de itens, equipamentos, peças e obuses: escolhas, preços/quantidades,
  falta de dinheiro/espaço e venda de peças necessárias ao funcionamento do tanque.
- Melhorias, presentes, mercado negro, reparos, troca de sucata/selos,
  abastecimento, aluguel, depósito, habilidades, montagem, Hunter Office,
  resgate e pintura, incluindo explicações e confirmações compatíveis.

Os cabeçalhos de lojas usam títulos naturais curtos, como Itens, Equipamentos,
Peças, Obuses, Reparos e Pintura. Os prompts foram revisados em conjunto, sem
truncamento automático ou remoção de acentos. Os nomes próprios e termos
Hunter, Soldier, MAIN/SUB/SE, LOVE Machine e demais nomes protegidos permanecem.
Isto não traduz as tabelas gerais de nomes/descrições dos itens, nem comprova
que todos os menus do jogo foram localizados.

## Política de reinserção S_PACK

`tools/spack_ui.py`, opt-in `spack-ui-counted-alias-preserving-repack-v001`.
A receita está **dentro de `translations/interface-v015.json`**, junto das demais
traduções; não foi criado um rascunho separado por loja ou tela.

A tabela original de 8.192 bytes está em 0x35070, entrada 0 do SDA de 22 entradas
em 0x35000. Possui 378 offsets relativos e 317 alvos únicos. O conteúdo é
reorganizado **dentro dos mesmos 8.192 bytes**, mantendo contagem, IDs e grafo
dos 61 aliases. Cada tradução aparece uma vez, vinculada ao ID canônico e ao
hash do texto original. Atualizam-se todos os offsets que apontam para ela.

O resultado ocupa **7.956 bytes**, com **236 bytes livres**. O SDA pai, seus
offsets, o tamanho do arquivo, os demais 21 recursos internos e os extents ISO
permanecem idênticos. Os nomes/descrições dos itens em outras tabelas não mudam.
O relatório registra offsets antigos/novos, IDs compartilhados e hashes.

Guardas: hash integral de origem e do bloco, count e limites exatos, strings NUL,
Unicode/bytes reversíveis, sequência printf/pipes, prefixo literal `%%I%02d%s`,
números fixos, espaços de concatenação, nomes/glossário e termos de armamento.
O limite por entrada é `max(comprimento original, 31)` bytes: **guarda conservadora
do novo perfil, não limite universal de buffer comprovado para todos os leitores**.
Os textos longos não crescem frente à própria origem. O lote inteiro é recusado
se ultrapassar o bloco; nenhuma alteração parcial é entregue.

## Evidências do leitor e consumidores

Janelas completas e ELF original vinculados por hash na receita e no relatório:

- 0x6CB94..0x6CBE8 e 0x6CC24..0x6CCC8: caminho de S_PACK, leitura do cabeçalho,
  seleção e carga da entrada raiz 1; o tamanho/offset original de carga não muda.
- 0x6CE04..0x6CE1C: seleção da entrada SDA interna 0 e armazenamento do ponteiro
  em VA 0x475B18. Helper SDA 0x3ED10..0x3ED20: `base + offset[índice]`.
- 0x1E8D14..0x1E8D30: acesso à tabela de texto como
  `base + u32(base + 4 + 4*ID)`, encaminhando a1 ao consumidor VA 0x14FCC0.
  Instruções originais executadas em memória simulada para **todos os 378 IDs**.
- 0x50CC0 → 0x4F3B0 → 0x3DB20: caminho comum de texto. Em
  0x3DBAC..0x3DBC8, mede o comprimento e prepara alocação `(bytes + 32) & ~3`;
  0x3DBE0..0x3DC78 copia caracteres, transforma pipe em LF e trata dois bytes.
  O contador de bytes original foi executado em seu caminho não alinhado,
  em **0x2266CC** e **0x2267F0..0x22680C**.
- Uma varredura local encontrou 244 leituras com imediato 0x5B18 e nenhum
  ADDIU direto para o pool nas até 12 instruções seguintes antes de clobber.
  Essa varredura **não é prova completa de todos os aliases/fluxos do executável**.

Os probes não executam I/O, alocador, GPU, fluxo completo do jogo ou PCSX2.
Round-trip e validação estrutural não substituem teste visual/funcional.

## Formato do personagem

Política `character-status-single-multiline-v001`, campo ELF 0x32B6A0 (51 bytes).
O consumidor 0x118A20..0x118A88 carrega o endereço em s0 e o encaminha em a1 a
VA 0x20D608, com os demais argumentos preservados. A nova string ocupa 50 bytes,
mantém os parâmetros, as sete quebras e o NUL original. O rótulo Tít. é uma
abreviação; Ataque, Defesa e EXP permanecem nos respectivos campos. Nenhuma
regex genérica do catálogo foi relaxada. Coat continua pendente de contexto.

## Preservados e limitações

**39 alvos S_PACK permanecem idênticos logicamente**, embora seus offsets possam
mudar: 18 nomes/termos protegidos, 15 códigos/símbolos/termos estáveis, dois bytes
nativos, um marcador técnico e três entradas de composição. O relatório enumera
os IDs. Dur, Normal e Item já são adequados; Drive continua igual aos tutoriais.

A confirmação de melhoria em 0x35CE7 usa `%screased` com `in`/`de`.
As três entradas continuam bloqueadas. Os nomes de atributos interpolados já
podem aparecer em português nessa mensagem ainda inglesa; resolver a composição
exige tratar o chamador, sem substituir bytes arbitrariamente. Grand Master e
Rent-a-Tank permanecem por proteção nominal. Os nativos 826E/8277 não são acentos
da extensão PT-BR. Não se editam nomes de personagens/tanques/cidades/procurados.

Esta é a primeira versão funcionalmente pendente desse repack: conferir acentos,
larguras, colunas e transações no PCSX2. Não declarar todas as fontes ou telas
aprovadas com base nos diálogos de Nina.

## Uso, saídas compactas e teste

`Iniciar-Teste.cmd`/`Testar-Interface.cmd` apontam para a ISO v015.
Na pasta `work/interface-v015/` há **somente a ISO e `relatorio.json`**.
O novo `--compact-output` evita duplicar plano, rascunho e revisão bilíngue do
MAP inalterado. Receitas Unicode, caminhos e hashes continuam preservados no
Git/relatório; a opção histórica sem a flag mantém as saídas anteriores.

```powershell
python tools/build_translation_pilot.py --draft translations/regiao-inicial-v030.json --interface-draft translations/interface-v015.json --output work/interface-reproducao-v015 --build-iso --compact-output
python tools/plan_interface_menus.py
python -m unittest discover -s tests -p "test_interface*.py" -v
```

O planejamento também atualiza o **mesmo** `work/planejamento-interface.json`,
agora cruzando a v015, sem criar arquivos por data. Evidências resumidas e delta
ficam em **um único `reports/interface-v015.json`**.

O usuário faz o teste, sem navegação automática: inicialização limpa, status e
inventário, uso/equipamento/descarte/ordenação; uma loja acessível para verificar
compra/venda, quantidade, saldo e confirmação. Depois, durante a passagem normal,
reparos, aluguel, depósito e demais serviços. Conferir também a mensagem de
modificação pendente e os nomes preservados, sem exigir acesso imediato a tudo.

Uma única ISO consolidada foi criada nesta rodada; alpha e originais preservados,
dez ISOs de trabalho. Sem OneDrive ou desligamento.

## Validação executada

- **87 testes de interface** passaram em 276,563 s; os seis testes de planejamento
  também passaram. Os 11 testes novos de S_PACK estão incluídos na suíte.
- Identidade de repack do original byte a byte; recuperação dos 378 IDs e dos 61
  aliases pelas instruções originais; comprimento dos 317 textos pelo contador
  original no caminho limitado; recusa de controles, números, nomes, nativos,
  hashes, IDs, espaços de concatenação e overflow. Preflight compacto verificado
  em diretório temporário isolado, com somente um relatório e sem ISO.
- Comparação integral v014→v015: **6.818 bytes diferentes em dois patches**
  (8.192 bytes de intervalo S_PACK e 52 bytes de intervalo ELF, incluindo NUL).
  Todos os bytes restantes e o diretório ISO permanecem idênticos.
- ISO de **1.704.427.520 bytes**, SHA-256
  `2008cf7e98df4f70c039d4a9fee06e009262856cdd1339f15c053d388f0cb40b`.
- Iniciador conferido sem executar o emulador. Resultado visual/funcional desta
  versão continua pendente do teste manual do usuário.
