# Interface v032 — títulos do personagem e recompensas de minijogo

Rodada extensa com **75 campos novos**: 73 títulos da ficha do personagem e
duas mensagens de recompensa do minijogo de tanques. Os títulos incluem
progressão de Hunter, mecânica, combate, feitos e companheiros. São apelidos
da ficha, distintos do comando **TITLE** na entrada de nomes, que continua
preservado até esclarecer seu chamador.

| Catálogo | Estado atual |
|---|---:|
| Campos/ocorrências de interface | **3.526**, antes 3.451 |
| Títulos únicos na tabela investigada | 78: **73 traduzidos e cinco preservados** |
| Diálogos MAP alterados | 5.969, todos preservados nesta rodada |
| Adiamentos técnicos MAP | 41 |
| Descrições de itens | 566/567, usadas por 925 referências |
| Nomes de itens traduzidos/pendentes | 516/25 |

Não medir a porcentagem do jogo inteiro por essas contagens. Títulos que
compartilham a mesma célula contam uma vez. A aprovação do layout em Nina
não constitui aprovação visual de todas as fichas/menus.

## Tradução e revisão

Hunter permanece nas designações correspondentes. Preservados **Gamer,
Moocher Breeder, Bargain Hunter, Cyber Hunter e Yokozuna**, por empréstimo
usual, referência nominal ou decisão conservadora de preservação. Nenhum
nome de personagem, tanque, cidade, equipamento ou procurado foi substituído.

As redações são títulos curtos e naturais, com adaptações de apelidos quando
necessário. Seasoned/Veteran continuam distintos; Palm's Pal/Palm's Friend
recebem redações diferentes. O título compartilhado Pro Mechanic usa **Pro de
oficina**, que atende aos dois grupos. O grupo que inclui Repair Girl recebeu
redações femininas ou neutras quando apropriado. Não atribuir identidade
canônica ao personagem apenas pelo índice de grupo.

As duas mensagens de recompensa recebem **Ganhou**, conservando os quatro
espaços iniciais/finais, `%dG` ou `%s`, os valores e os nomes dos prêmios.
Somente os textos mudam; lógica, item, pagamento e ações permanecem originais.
Não foram traduzidos identificadores internos de minijogos para aumentar a
contagem. Originais e revisão bilíngue permanecem em work/.

## Execução e reprodução

Abra **Iniciar-Teste.cmd**. Imagem consolidada:

`work/interface-v032/MetalSaga-ptbr-interface-v032.iso`

SHA-256: `a0724bee61e4bd573d07785dc9ac4ebedf209d088c796282ed1ae444176ce701`

Tamanho: 1.704.427.520 bytes. O iniciador valida hash, tamanho, relatório e
ausência de journal/partial antes de iniciar. Nenhuma navegação PCSX2 foi
realizada nesta rodada. O usuário confere em partida normal: títulos na ficha,
nomes dinâmicos em diálogos que usam o título, acentos, comprimento/alinhamento,
progressão dos títulos e os dois avisos de recompensa quando aparecerem.
Não é necessário obter todos os títulos ou alcançar cenas distantes agora.

`Preparar-Interface.cmd` valida sem gerar ISO; `Auditar-Traducao.cmd` usa a
construção compacta atual. Para reconstruir em uma pasta nova:

```powershell
python tools/build_translation_pilot.py --draft translations/regiao-inicial-v032.json --interface-draft translations/interface-v032.json --output work/interface-v032-reproducao --compact-output --build-iso
```

O planejador mantém um único `work/planejamento-interface.json` e separa
os títulos das strings ELF legadas, cujos hashes cobrem intervalos diferentes.
Títulos vinculam a célula inteira; o catálogo legado vincula apenas o texto
anterior ao NUL. Não intercambiar essas duas provas de capacidade.

## Estrutura comprovada dos títulos

Ferramenta `tools/character_titles.py`; perfil opt-in
`character-title-original-cells-v001`.

- **71 células de 16 bytes** em 0x3198F0..0x319D60 e **oito células de oito
  bytes** em 0x348BF8..0x348C38; uma destas é vazia e permanece intacta.
- Dez ponteiros de grupo em **0x264478**. Grupos com **47, 7, 7, 8, 8, 1, 1,
  1, 1 e 1** referências. Os dois grupos de oito são contíguos, sem sentinela
  NUL entre eles; não presumir terminador zero em todas as tabelas.
- São 82 referências, incluindo três à célula vazia, 79 referências a textos
  não vazios e 78 textos únicos. Pro Mechanic tem dois consumidores de grupo.
- Lookup original em **0x6BB60..0x6BB84**: seleciona o grupo e o ponteiro por
  índices de quatro bytes, retornando a string no delay slot do retorno.
- Chamador da ficha em **0x118A18..0x118A34**, encaminhamento ao formatador
  em **0x118A68..0x118A8C**. Outros usos conferidos nos call sites em
  **0x1B5D64** e **0x1CD378**; não foi alterada a gramática de comandos MAP.

Foram executadas **79 combinações não vazias de grupo/índice**, cada uma com
lookup, argumentos do chamador e encaminhamento da string ao formatador,
usando instruções originais e RAM sintética. Formatação completa, desenho,
estado de desbloqueio e PS2 não foram executados. A contagem estática dos
grupos não comprova uma proteção de limites no runtime.

Cada célula deve conter ASCII original, NUL e cauda totalmente zerada. A
tradução pode ocupar somente os 15 ou sete bytes anteriores ao NUL final do
próprio campo; não recebe bytes de células vizinhas. O maior título original
tem 15 bytes. Ponteiros, aliases, código, limites das seções e campos vazios
permanecem intactos. As referências conhecidas devem corresponder exatamente
aos ponteiros dos grupos; referências internas à célula bloqueiam a operação.
Essa análise de referências é conservadora, sem promessa de censo exaustivo
de caminhos indiretos.

Configuração exige revisão de todos os 78 textos e as cinco preservações
explícitas. Rejeita IDs repetidos/ausentes, hashes divergentes, overflow,
controles/NUL injetados, glifos não suportados e violação terminológica. Não
transfere esta capacidade aos nomes de itens, cujo perfil continua separado.

## Recompensas e integridade

Strings ELF em **0x337610** e **0x337628**, sob a política fixa já existente.
O consumidor monetário em **0x160194..0x1601AC** encaminha o valor original
de contexto+0x1788 ao formatador. O consumidor de item em
**0x160268..0x160290** encaminha base+ID×128 a `%s`. Probes limitados conferem
os argumentos; não executam distribuição de prêmio ou emulador.

Relatório final em `reports/interface-v032.json`: comparação integral com
v031, hashes, testes, preservação de recursos anteriores e limites visuais.
Passaram **326 testes distintos**, incluindo 257 de interface, 48 de controles,
sete de preflight, seis de planejamento, cinco de retenção e três da alpha.
Os sete testes de títulos e quatro de integração foram repetidos após a revisão
editorial/guarda de referências; não foram somados novamente. Comparação final:
**879 bytes em 75 campos ELF**, com os demais bytes e o diretório idênticos.
As fontes/layout v005 e arte do título v014 permanecem iguais. A imagem
interna anterior à revisão editorial foi descartada após conferir seu hash;
não era uma versão publicada. O registro dessa revisão fica em work/.

Mantidas cinco ISOs de trabalho e alpha permanente protegida. Originais,
BIOS, saves e configurações preservados. Sem cópia ao OneDrive. O usuário
solicitou desligamento pelo terminal ao concluir: executar somente após
validar, documentar e enviar o trabalho ao GitHub.

Próximos alvos continuam comando TITLE, 25 nomes bloqueados e os demais
controles/bytes nativos MAP. Não repetir os títulos já encerrados nem chamar
preservações de novas traduções. Revisão contextual e visual segue acumulada
para a passagem normal do usuário.
