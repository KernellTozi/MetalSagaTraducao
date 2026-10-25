# Diálogos v036 — rótulos em posições de byte

Mais **75 referências de rótulos traduzidas**, acumulando **867 / 1.527**
referências do catálogo de falantes. Foram reaproveitados de um a dois bytes
separadores antes do rótulo; nenhum corpo ou opção foi encurtado. A v035 exigia
que o novo rótulo começasse alinhado a quatro bytes, deixando parte dessa folga
inutilizável. A nova política trata somente posições de byte comprovadas.

| Novos rótulos | Ocorrências |
|---|---:|
| Homem | 24 |
| Gato | 15 |
| Cão | 11 |
| Transportador | 9 |
| Alto-falante | 8 |
| Mercador | 5 |
| Rapaz | 2 |
| Ancião | 1 |

Ancião mantém o espaço final original. São 64 msgn e 11 smnn. Dos 75 registros,
50 já tinham algum campo alterado; os outros 25 agora mudam somente pelo rótulo.
Portanto, há **6.024 registros MAP com algum campo alterado**, mas continuam
**5.983 registros com corpo/opções traduzidos**, no catálogo de 7.231 registros.
As interjeições/expressões preservadas nesses corpos não contam como traduções.

Restam **53 referências a funções revistas sem espaço**, contra 128 na v035:
20 Trabalhador, 20 Homem, oito Transportador e uma ocorrência de Mecânico severo,
Gato, Técnico de manutenção, Rapaz e Cão. Outras 607 referências incluem nomes,
termos preservados, marcadores e rótulos não selecionados; não são traduções
automaticamente autorizadas. Os 27 adiamentos técnicos de corpos permanecem:
19 nomes N$3 preservados e oito ocorrências nativas sem contexto comprovado.

## Uso e reprodução

Abra **Iniciar-Teste.cmd**. Imagem atual:

`work/interface-v036/MetalSaga-ptbr-interface-v036.iso`

SHA-256: `32f2769c7e5b1ef1d4a36bde78e837e74337ea5d24c71c78b4bb7616f01a0036`

Tamanho: 1.704.427.520 bytes. A interface mantém seus 3.526 campos e a mesma
arte/título v014, fontes e layout v005. `Preparar-Interface.cmd` valida sem
criar ISO; `Auditar-Traducao.cmd` mantém o catálogo substituível em
`work/dialogos-pendencias-atual.json`. O console do construtor agora distingue
registros alterados, corpos/opções e rótulos, evitando tratar todos como falas.

Construção em pasta nova:

```powershell
python tools/build_translation_pilot.py --draft translations/regiao-inicial-v036.json --interface-draft translations/interface-v036.json --output work/interface-v036-reproducao --compact-output --build-iso
```

Reproduzir a seleção em arquivos novos:

```powershell
python tools/prepare_speaker_labels.py --byte-packed --parent translations/regiao-inicial-v035.json --output translations/regiao-inicial-v036-reproducao.json --report reports/rotulos-falantes-v036-reproducao.json
```

O modo `--relocate` continua reproduzindo o alinhamento de quatro bytes da v035.
Os dois modos não podem ser combinados na mesma preparação. A receita v036 herda
integralmente os 553 rótulos fixos e os 239 remanejados anteriormente; o novo
campo `speaker_label_byte_packing` acrescenta seus próprios 75 IDs. Não substituir
um dos campos antigos para encaixar o novo. O preparador preserva as entradas
herdadas do mesmo perfil quando a preparação seguinte parte de uma receita que
já o contém. Nenhuma etapa local exige IA, APIs ou internet.

## Política específica e evidência

`map-generic-speaker-label-byte-tail-borrow-v003`, em
`tools/speaker_label_space.py`, reutiliza os consumidores comprovados e acrescenta
uma permissão explícita para o início desalinhado do rótulo. As políticas v001 e
v002, suas receitas e o compilador legado permanecem com as restrições anteriores.
O novo perfil é opt-in e não altera o layout das instruções SSD em disco.

O cálculo da posição é `tamanho_registro - bytes_alvo - 1`, em vez de arredondar
para baixo a um múltiplo de quatro. Exige posição estritamente posterior ao NUL
da string anterior, anterior ao rótulo original e não alinhada a quatro bytes.
Mantém os testes de zeros separadores, rótulo/cauda original, família conhecida,
slots, ausência de bloqueios, função/target editorial exatos e preservações.
Se não há folga nem por byte, o registro é adiado. Não cresce nenhum registro.

Cada alvo vincula ID, hash original do registro/rótulo, hash do registro já
compilado e offset final explícito. Não são modificados corpos, opções, tokens,
terminadores anteriores, cabeçalhos, nomes próprios, fronteiras SSD ou extents ISO.
A leitura estrutural e a releitura independente conferem a nova posição. O wrapper
de offsets compilados acumula as 239 posições v002 e as 75 v003; os metadados
originais de extração e `label.editable=false` continuam intactos.

Evidências adicionais à v035:

- Os leitores msgn e smnn/2snm incrementam os ponteiros **um byte** no percurso
  entre o NUL anterior e o rótulo. Os probes originais de busca e percurso foram
  executados em memória sintética antes/depois para cada alvo, sem arredondamento
  imposto pelo código Python.
- O setter chama a mesma cópia em 0x2265B4. Seu teste inicial usa o OR dos
  ponteiros de origem/destino e máscara de sete para selecionar o ramo escalar.
  Foi executado esse código original com **destino alinhado a 16 bytes** e cada
  classe de origem desalinhada de 1 a 7 módulo oito, inclusive textos PT-BR.
- Na compilação de cada rótulo, foram conferidas as duas classes módulo oito
  compatíveis com seu resíduo módulo quatro. O retorno, bytes, NUL, origem e
  sentinela do destino precisam coincidir. Os probes anteriores de comprimento
  em bytes, pedido de alocação e getter continuam aplicados.

Isso executa somente trechos delimitados em memória sintética. O alocador segue
substituído; SIMD alinhado, chamador completo, objetos, renderização, retratos e
PCSX2 não foram executados. Não generalizar para formatos desconhecidos, alterar
alignment de registros/SSD ou declarar validação visual. Nomes próprios, Hunter,
Soldier e profissões/expressões preservadas fora da seleção continuam intactos.

## Validação e continuidade

**63 testes distintos aprovados**: seis novos do perfil por byte, sete da v035 e
50 de auditoria, reinserção, cobertura, codec nativo, controles, preflight,
retenção e alpha. Reexecuções não somadas. Incluem preservação integral dos perfis
anteriores, offsets acumulados, hashes/posição adulterados, duplicação, decisões
imutáveis, overflow, codec, sentinelas e recusa desses novos alvos pela política
v002. Não houve alteração de fonte ou ampliação do mapeamento de caracteres.

Comparação integral v035→v036: **481 bytes diferentes em 75 registros MAP**.
O relatório está em `reports/interface-v036.json`;
os únicos intervalos alterados são os 75 rótulos e zeros usados para acomodá-los.
Demais bytes, diretório, fontes, arte e interface permanecem idênticos. Triagem
em `reports/rotulos-falantes-v036.json` e `reports/dialogos-pendencias-v036.json`.
Preflight e iniciador em dry-run aprovados; cinco ISOs e alpha protegida mantidos.

Na próxima partida normal, conferir os títulos de NPCs, animais e avisos,
especialmente Cão e Ancião, observando acentos, corte e associação com a fala.
Não se exige acesso imediato a cenas distantes. A conferência visual permanece
pendente; não houve OneDrive ou desligamento nesta rodada.

Os 53 casos restantes não cabem nem removendo o alinhamento conservador. A próxima
frente precisa de revisão contextual específica ou outra estrutura de armazenamento
com evidência própria. Não repetir tentativas de obter zeros inexistentes, retirar
acentos ou cortar artigos/frases para aumentar contagens. Preservar os nomes N$3
já decididos e manter as oito ocorrências nativas separadas até obter contexto.
