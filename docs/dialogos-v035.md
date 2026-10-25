# Diálogos v035 — rótulos maiores com folga interna

Traduzidos **mais 239 rótulos**, reutilizando somente zeros separadores depois
das falas/opções já compiladas. As traduções anteriores não foram encurtadas.
Total acumulado: **792 referências de rótulos traduzidas**, das 1.527 conhecidas.

| Novos rótulos | Ocorrências |
|---|---:|
| Homem | 113 |
| Trabalhador | 69 |
| Transportador | 39 |
| Mecânico severo | 6 |
| Mercador | 3 |
| Rapaz | 3 |
| Técnico de manutenção | 2 |
| Cozinheiro | 2 |
| Ancião | 2 |

O espaço final de Ancião permanece, como no rótulo original. São 226 msgn e
13 smnn, todos com corpo/opções já alterados na v034. Portanto, continuam
**5.999 registros MAP alterados**, dos quais **5.983 têm corpo/opções traduzidos**.
Não contar estes rótulos como novas falas. A interface mantém os mesmos 3.526
campos, fontes/layout v005 e arte/título v014.

Dos 367 rótulos adiados por capacidade na v034, **128 continuam pendentes**,
incluindo Gato, Cão, Alto-falante e outras ocorrências das funções acima sem
folga suficiente. Outros 607 rótulos incluem nomes, termos protegidos, marcadores
e funções ainda não selecionadas. Os 27 adiamentos técnicos de corpos não
mudam: 19 nomes N$3 preservados e oito ocorrências nativas de contexto desconhecido.

## Usar e reproduzir

Abra **Iniciar-Teste.cmd**, agora apontando para:

`work/interface-v035/MetalSaga-ptbr-interface-v035.iso`

SHA-256: `ddedfe278309fa6e7f1d22d24d08b7bdb5f7406e70b6475e11fb26deb65a8675`

Tamanho: 1.704.427.520 bytes. `Preparar-Interface.cmd` valida sem criar ISO;
`Auditar-Traducao.cmd` atualiza somente o catálogo local substituível em
`work/dialogos-pendencias-atual.json`, com offsets/capacidades originais e
compilados separados. Não há IA, APIs ou rede na análise/construção.

Construção em pasta nova:

```powershell
python tools/build_translation_pilot.py --draft translations/regiao-inicial-v035.json --interface-draft translations/interface-v035.json --output work/interface-v035-reproducao --compact-output --build-iso
```

Reprodução da seleção, também em arquivos novos:

```powershell
python tools/prepare_speaker_labels.py --relocate --parent translations/regiao-inicial-v034.json --output translations/regiao-inicial-v035-reproducao.json --report reports/rotulos-falantes-v035-reproducao.json
```

O preparador conserva os remanejamentos herdados quando usado sobre uma receita
que já os contém. É uma seleção do mapa editorial explícito, sem tradução
automática de nomes/funções novas. Uma modificação posterior dos corpos pode
invalidar o hash do registro compilado usado nesta rodada: revisar e vincular
novamente os alvos afetados, sem ignorar a recusa ou mover dados silenciosamente.

## Nova política, sem relaxar as anteriores

`map-generic-speaker-label-same-record-tail-borrow-v002`, implementada em
`tools/speaker_label_space.py`, é uma etapa opt-in posterior à compilação de
corpos e ao overlay fixo da v034. As políticas antigas, seus hashes, slots,
fingerprints e a marca `label.editable=false` continuam inalterados.

Para cada alvo, a receita vincula ID, hash original do registro/rótulo, hash
do registro após compilar as traduções herdadas e posição final explícita.
Somente msgn/smnn/2snm já reconhecidos, em modo slots, sem outros bloqueios e
fora das decisões de preservação podem participar. O mapa editorial da v034
continua limitando rigorosamente os nomes de função e as traduções permitidas.

O algoritmo mantém o início do corpo e das opções. Encontra o NUL real da
string imediatamente anterior e exige que o intervalo até o rótulo original
contenha somente zeros. A cauda deve conter exatamente o rótulo original e
seus zeros. Calcula a posição final como `(tamanho_registro - bytes_alvo - 1)
& ~3`, mantendo alinhamento de quatro bytes. Essa posição precisa ficar após
o NUL anterior e antes do rótulo original; caso contrário, o alvo é adiado.

Só essa cauda é recomposta com o novo rótulo, NUL e padding. O corpo/opções,
seus terminadores e cabeçalho permanecem byte a byte idênticos à v034. O
registro, bloco SSD e extent ISO conservam tamanho e posição. Não se toma
espaço de outro registro nem se corrige o texto para fazê-lo caber.

O registro completo é reparsed em sombra neutra para os pares PT-BR, conferindo
os offsets anteriores e o novo offset do rótulo. Há um único patch por ID,
sem sobreposição. O documento preserva os metadados da extração; o wrapper
`compiled_speaker_label_offsets` registra as novas posições para leitura
independente e auditoria. Qualquer inconsistência interrompe o lote inteiro.

## Caminho do leitor comprovado e limites

Hash integral do ELF original e cinco janelas adicionais vinculados à receita.
Offsets de arquivo, com VA = offset + 0xFF000:

- msgn: 0x1C64A0..0x1C64B0 busca NUL do corpo; 0x1C6508..0x1C6538 percorre
  zeros até o primeiro byte do rótulo, antes do encaminhamento já estudado.
- smnn/2snm: a busca em 0x1C6D8C..0x1C6D98 parte das opções; o laço
  0x1C6D9C..0x1C6DD0 encontra o primeiro byte após os zeros. O wrapper de
  2snm e o chamador compartilhado já estão vinculados pelas políticas anteriores.
- Helper de busca 0x2262C8: seu ramo escalar em 0x22643C..0x226468 foi executado
  com entrada sintética desalinhada e alvo NUL. Os laços originais, incluindo
  delay slots e anulação de branch-likely, foram executados para os registros
  compilados antes/depois. Conferida a posição encontrada, não apenas uma
  expressão Python equivalente.
- Os probes da v034 continuam conferindo comprimento em bytes, pedido de
  alocação, cópia com sentinelas e getter estático para cada novo rótulo.

Não foram executados o chamador completo, busca/cópia SIMD alinhada, alocador,
objetos, GPU, retratos ou PCSX2. Esse escopo não resolve todos os caminhos de
texto ou comprova apresentação visual. Nomes próprios e profissões protegidas
permanecem intactos. Não generalizar para controles desconhecidos ou outras
estruturas, nem declarar os 128 alvos restantes impossíveis em todo o motor:
somente não cabem neste mecanismo conservador.

## Verificação e próximos passos

**65 testes distintos aprovados**: sete novos de remanejamento, oito da v034,
50 de auditoria, reinserção, codec nativo, controles, cobertura, preflight,
retenção e alpha. Reexecuções não entram na soma. Incluem preservação de todos
os segmentos/metadados herdados, reversão dos deltas, padding insuficiente,
nomes/controles injetados, hashes/posição alterados, duplicação e manutenção
dos remanejamentos na preparação seguinte. O probe também cobre rótulo iniciado
por um par PT-BR reconhecido, sem ampliar o codec para caracteres não mapeados.

Delta integral v034→v035: **2.368 bytes diferentes em 239 registros MAP**.
Demais bytes da imagem, diretório, fontes, interface e arte idênticos. Evidências:
`reports/interface-v035.json`, `reports/rotulos-falantes-v035.json` e
`reports/dialogos-pendencias-v035.json`. Preflight completo e iniciador em
dry-run aprovados. Cinco ISOs de trabalho; alpha permanente protegida.

O usuário pode conferir os novos nomes de função em partida normal, observando
acentos, corte, largura, associação com fala/retrato e opções. Não houve teste
visual nesta rodada e não se exige navegação imediata a cenas distantes.

Para os 128 rótulos sem espaço, a próxima investigação precisa avaliar outra
estratégia de armazenamento ou revisão contextual específica, com prova própria.
Não insistir em tomar espaço inexistente nem alterar frases para inflar a contagem.
As oito ocorrências nativas ainda exigem contexto; N$3 já tem decisão definitiva
de preservação e não deve ser reinvestigado. Sem OneDrive ou desligamento automático.
