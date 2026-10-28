# Interface v043 — nomes aprovados, acentos compatíveis e percepção

Aplicação exclusiva do lote recebido em `Texto colado.txt`, SHA-256
`5cd5c28bb4f2bdc74bcc73fa55922741c21dfebcdf3e41fc6062ad5be00da7f1`.
Uma cópia da instrução permanece em `work/nomes-aprovados-v002/`.
Base: interface v042, MAP v038, layout v005 e arte v014.

## Nove nomes aplicados

| ID | Nome final | Bytes do projeto |
| --- | --- | ---: |
| 103 | Oculos | 6 |
| 109 | Máscara hóquei | 16 |
| 112 | Turbante aramida | 16 |
| 118 | Orelha de coelho | 16 |
| 130 | Casaco polímero | 16 |
| 178 | Placas polímero | 16 |
| 342 | Kit de reparo | 13 |
| 425 | Orelha de coelho | 16 |
| 861 | Superpercepção | 16 |

Oculos é a única remoção de acento: Ó maiúsculo continua sem mapeamento e o
usuário autorizou esse fallback. Todos os caracteres já disponíveis permanecem
acentuados. Não foram criados glifos nem alteradas fontes. A autorização de
fallback não foi aplicada retroativamente a outros registros.
As construções compactas sem preposição foram aprovadas explicitamente para
este lote; não são uma nova licença geral para encurtar traduções.

Os oito primeiros IDs estavam pendentes. O ID 861 é uma revisão existente.
Resultado: **527 nomes aplicados, 14 pendentes**, e **3.822 campos de interface**.
As outras sugestões e as 16 revisões bloqueadas não foram aplicadas.
Todos os demais nomes, textos, controles, descrições e diálogos permanecem.
Os IDs 118/425 continuam registros independentes. Kit de reparo não substitui
Kit mecânico. Não há contrapartes com essas origens na tabela de ações de
batalha; nenhuma ação precisou ser reescrita.

## Conferência do ID 861 e correção da auditoria anterior

A fonte imutável identifica o ID 861 como **Keen Senses**, não Sixth Sense.
Nome em S_PACK, offset `0x1B6A0`, registro de 128 bytes. O código verifica o
hash original de registro/nome e a descrição vinculada ao mesmo ID:
`item.description.03269`, hash
`2f89dfe244520e3b895731a16c95b76fc6e2cf8a9d65d1e58ec13bd511b235ae`.
A descrição informa aumento temporário da chance de ataque preventivo.
Ela também é compartilhada por outros IDs; isso não identifica todos esses
IDs como a mesma habilidade nem autoriza renomeá-los.

Superpercepção ocupa **16 bytes**, não 17, pelo codec real:
`53 75 70 65 72 70 65 72 63 65 70 82 40 82 43 6F`.
As afirmações anteriores de 17 bytes e de Sixth Sense para este ID estavam
incorretas e ficam corrigidas aqui. As receitas históricas não são reescritas.
Não foi necessário usar Superpercepcao. Nenhum ID deste lote ficou sem aplicar.

## Vínculos e preservação

Manifesto `translations/nomes-aprovados-v002.json`, vinculado ao hash da v042.
`tools/item_name_approved_batch.py` exige os nove IDs e destinos exatos,
origens/nomes anteriores, limite inalterado e o vínculo da descrição de 861.
A configuração usa `approved_extension` explícito, conservando a autorização
restrita de 72 nomes da v042 e seus 30 rótulos de batalha. Não ampliar o manifesto
sem uma nova revisão e política vinculada.

O bloqueio de Repair Kit é dispensado somente para ID 342, origem Repair Kit
e destino Kit de reparo neste opt-in. A política global e as compilações antigas
continuam estritas. A comparação entre versões normaliza somente a união dos
prefixos autorizados, inclusive o crescimento de Superpercepção no próprio slot.
Teto de 16 bytes, campo físico de 24, IDs, atributos e referências intactos.

## Validação e teste visual

**97 testes passaram**, sete novos: escopo exato, preservação dos outros
campos, identificação de 861, fallback único, codec, limites, bloqueios,
rejeição de alterações extras e round-trip binário de toda a tabela.
A medição dos nove nomes fez **438 probes** de glifos/perfis nas fontes 22/26
e modos 0/1/2. Nenhum nome superou o maior avanço observado nos originais.
Isso não comprova encaixe em todos os recortes e menus do jogo.

Foi gerada e inspecionada a prévia técnica antes/depois em
`work/nomes-aprovados-v002/previa-nomes.png`, usando os glifos GFI existentes
e o compositor local já disponível, sem compressão horizontal. Ela permite
conferir os desenhos, mas não reproduz todos os chamadores de layout do jogo.
**Não houve execução do PCSX2 nesta rodada.** A aprovação visual nos menus
reais continua pendente para o usuário, em inventário/equipamentos/lojas e
na lista de habilidades para Superpercepção. Observar cortes e espaçamento,
além da distinção Kit de reparo/Kit mecânico.

## Reprodução

```powershell
python tools/build_translation_pilot.py --draft translations/regiao-inicial-v038.json --interface-draft translations/interface-v043.json --compact-output --build-iso --output work/minha-interface-v043
python -m unittest discover -s tests -p test_approved_name_batch.py
```

Usar uma pasta de saída nova. A entrega consolidada fica em
`work/interface-v043-final/MetalSaga-ptbr-interface-v043.iso`.
Após preflight e delta integral aprovados, Iniciar-Teste.cmd aponta para v043.
Sem cópia OneDrive e sem desligamento automático nesta rodada.

## Integridade da entrega concluída

ISO com 1.704.427.520 bytes; SHA-256
`cd893b79d21c345ce3533940d67fa10865128b949be1e7272a2b28261dc7eec5`.
Preflight integral aprovado, sem transação ou construção parcial pendente.
Comparação completa v042 → v043: **127 bytes em nove patches**, todos nos
nomes autorizados de S_PACK.SDA. Diretório e todos os demais bytes da imagem
permanecem iguais, inclusive fontes, textos e ações de batalha.
Relatórios: `reports/interface-v043.json` e `reports/interface-v043-delta.json`.
Mantidas cinco ISOs de trabalho; alpha permanente conferida por SHA-256.
