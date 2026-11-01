# Backup v059 e protótipo dos 13 nomes de falantes

## Referência preservada

Por nova ordem do usuário, a v059 substitui as cópias antigas como backup.
A imagem foi copiada de forma independente e marcada como somente leitura:

`dist/backup-v059/MetalSaga-ptbr-backup-v059.iso`

SHA-256:
`ab243c520f6e84169d52ee765cb71faeeeb605fb79b34aecd9adc126ea008094`.
Tamanho de cada cópia: 1704427520 bytes. Não é um hardlink e fica fora da
retenção de work/. Não usar esse arquivo como destino de experimentos.

A nova base de investigação é outra cópia independente:

`work/falantes-lookup-v001/MetalSaga-ptbr-falantes-base-v059.iso`

As duas cópias foram conferidas integralmente antes da limpeza. Foram
removidas somente as ISOs geradas v055, v056, v057, v058 e a antiga alpha
v001, todas vinculadas aos hashes históricos. A nova autorização substitui
a regra anterior de manter aquela alpha permanentemente. ISO original,
extraídos, BIOS, saves e configurações não foram alterados.

Restam três cópias da mesma v059: backup, imagem do iniciador e base de
investigação. Receitas, ferramentas e relatórios antigos foram preservados
para reprodução; não são ISOs adicionais. Ledger: reports/backup-v059.json.
Ferramenta da operação: tools/preserve_v059.py, com plano sem alterações
por padrão e execução somente mediante `--apply`. Ela não é uma política
automática de limpeza nem autorização de substituir backups futuros.

## Nova hipótese: nome completo em uma tabela separada

Os 13 casos restantes são Worker×9, Man, Transporter, Cat e Dog. Os alvos
continuam **Trabalhador, Homem, Transportador, Gato e Cão**, sem abreviações
ou remoção de acentos. O protótipo não volta a procurar zeros nos registros
nem reduz os textos dos diálogos para abrir espaço.

O setter original em ELF+0x1FD968 calcula o tamanho, aloca um destino e copia
o nome recebido. Em 0x1FD9D8, chama strlen; o delay slot encaminha S2 como
entrada. A cópia em 0x1FDA18 também usa S2. O novo método pretende substituir
**esse ponteiro antes da contagem e da cópia**, mantendo a alocação original
adequada ao nome completo.

1. Somente os 13 rótulos vinculados seriam trocados por marcadores curtos
   `~0` a `~4`, dentro dos slots existentes, conservando NUL e zeros finais.
2. A rotina reconhece o chamador msgn pelo RA salvo em SP+0, VA 0x2C5550;
   outros chamadores seguem o caminho original.
3. Reconhece somente prefixo `~`, índice ASCII 0–4 e NUL imediatamente
   depois. Cada byte é conferido antes da leitura seguinte.
4. Troca A0 e S2 pelo endereço do nome completo e faz tail-call para o
   strlen original, sem mudar RA, SP ou os demais registradores vivos.
5. O setter original aloca/copia o nome; os nomes da tabela ficam
   deliberadamente desalinhados para selecionar o strcpy escalar já testado.

O programa e sua tabela ocupam **170 bytes**. Os cinco nomes completos foram
resolvidos em RAM simulada; os 13 registros receberam propostas locais com
comparação de todos os bytes fora do rótulo. A travessia original msgn
continua localizando o mesmo início do campo. Nos 7231 registros do catálogo,
nenhum rótulo compilado coincide com os cinco marcadores. Isso não é uma
prova universal de fontes de texto desconhecidas ou geradas em execução.

## O que passou e o que ainda impede aplicação

A rotina MIPS gerada foi executada com limites de leitura, incluindo nomes
normais, vazios, marcadores incompletos/inválidos, outros chamadores e oito
alinhamentos de entrada. As sondas originais conferem comprimento,
arredondamento de alocação, cópia, sentinelas e getter do nome. O alocador
real, liberação, ciclo de vida, chamador completo, GPU e jogo não foram
executados. Não equivale a validação funcional no PCSX2.

**Nenhuma alteração de falante foi aplicada a uma ISO.** A base nova e o
backup continuam com o hash v059. O programa usa o endereço **sintético**
0x6A0000 apenas na sonda. Esse endereço nunca foi liberado como RAM livre do
jogo. O protótipo não tem opção de aplicar/build e publica
`can_apply_to_iso: false`.

## Investigação de armazenamento: caminho concreto para a próxima etapa

O ELF tem um único PT_LOAD, offset 0x1000, VA 0x100000, tamanho em arquivo
3444848 e tamanho em memória 3889564. O fim declarado da imagem é
**0x4B599C**. A inicialização limpa BSS de 0x449080 em passos de 16 bytes:
o limite real da última escrita é **0x4B59A0**, quatro bytes além daquele fim.
Portanto, colocar código simplesmente no primeiro byte depois da BSS o
deixaria exposto à limpeza de inicialização.

O intervalo de arquivo 0x54–0x1000 está zerado e fora do segmento atual.
Há espaço físico para outra entrada de programa em 0x54 e para 170 bytes
em 0x100, **mas esses zeros não são atualmente carregados como código**.
Uma alternativa é declarar um segundo segmento, com a rotina depois da
limpeza BSS em 0x4B59A0, e reservar a memória até 0x4B5A50.

Essa alternativa permanece **bloqueada**: existem 12 referências conservadoras
a 0x4B599C no código/dados. Uma limita a limpeza BSS; outra fornece o
argumento de syscall 0x3D na inicialização. As demais participam de dados,
tamanhos e caminhos de alocação ainda não completamente rastreados. Alterar
somente o cabeçalho ELF ou só um endereço pode deixar o heap sobrescrever
a rotina. Não promover essas referências a patches automaticamente.

O relatório guarda offsets, palavras de referência e hashes das janelas,
permitindo retomar pela classificação dos 12 consumidores. Próxima etapa:
provar a reserva em todos os caminhos de inicialização/reset/alocação,
preservando o limite da limpeza BSS; depois validar o carregamento do novo
segmento e produzir uma ISO experimental separada. Não ampliar registros
MAP, SSDs ou extents ISO como atalho.

Referência de estrutura, sem código externo incorporado:
[definições ELF do PCSX2](https://github.com/PCSX2/pcsx2/blob/master/pcsx2/Elfheader.h).
Essas definições não comprovam o comportamento da BIOS instalada, do heap
do Metal Saga ou a compatibilidade funcional da alteração proposta.

## Reprodução local

```powershell
python tools/speaker_lookup_prototype.py
python -m unittest discover -s tests -p test_speaker_lookup_prototype.py -v
python -m unittest discover -s tests -p test_preserve_v059.py -v
```

O primeiro comando confere a base de trabalho, recompila o MAP original pelo
lote v044 e gera somente a sonda e as propostas locais. Não usa IA/APIs ou
internet. Metadados públicos em reports/falantes-lookup-v001.json; bytes dos
13 registros e programa de sonda somente em work/falantes-lookup-v001/.
Não transportar proposta-local.json para o reinseridor legado: os marcadores
isolados exibiriam nomes incorretos sem uma rotina instalada e comprovada.

Passaram **57 testes distintos**: dez do protótipo, seis da preservação/
limpeza e 41 de regressão de falantes, preflight e retenção. Os testes de
remoção usam somente fixtures pequenas em diretórios temporários isolados;
não executam retenção/remoção contra as ISOs reais. Uma falha inicial nas
fixtures expôs o tamanho padrão capturado na definição da função; foi
corrigido para usar o limite configurado em execução e a suíte passou.
O limite real de 1704427520 bytes permaneceu igual durante a operação.
