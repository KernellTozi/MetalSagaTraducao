# Interface v042 — revisão humana dos itens e primeira escolha

O usuário entregou `METAL_SAGA_DECISOES_PARA_CODEX.md`, autorizou aplicar as
decisões e pediu corrigir a primeira escolha, gerar a versão e desligar o
computador ao terminar. Foi lida somente essa entrada externa explicitamente
indicada; cópia imutável de trabalho em
`work/revisao-humana-itens-v001/decisoes-originais.md`. O arquivo do Desktop
permanece intacto. Hash da entrada:
`02e5267f988dbf3234ad981a029e79468c7ba5e8316ffd5844fa32e741285b48`.

## Resultado editorial

- **72 IDs alterados**, exatamente a seção A: 69 revisões e três nomes antes
  pendentes, Cafeína, Secreção doce e Muco pegajoso.
- **35 escolhas da seção D já iguais**, sem reescrita; outras 134 da seção E
  também conferidas e mantidas. Zero conflitos de ID, origem ou auditoria.
- **16 escolhas da seção B não aplicadas**: preservados seus nomes atuais.
  Quinze excedem o teto de 16 bytes e Ídolo de barro requer Í ainda não mapeado.
- **Uma alternativa sem confirmação**: 861 continua Sentidos finos;
  Hipersentidos e Superpercepção não foram aplicados.
- 18 nomes explicitamente protegidos da seção C conferidos, além da
  preservação integral de todos os nomes fora dos 72 IDs autorizados.

Receita própria: `translations/revisao-humana-itens-v001.json`, com IDs,
hashes de origem/registro, tradução auditada, destino autorizado, notas e
vínculo ao pai interface v041. Não contém um catálogo extraído de nomes
originais. O diff bilíngue completo fica somente em
`work/revisao-humana-itens-v001/conferencia/diff-nomes.md`.

Interface v042 contém **519 nomes de itens/habilidades aplicados**, três a
mais que 516; 22 propostas antigas permanecem pendentes. Somando a interface,
o total é **3.814 campos**. As revisões dos nomes já traduzidos não contam
como novos campos. A lista da auditoria v040 não foi sobrescrita.

## Exceções restritas, sem liberação global

Política opt-in `spack-user-reviewed-item-names-observed-ceiling-v003`, em
`tools/item_names.py` e `tools/item_name_user_review.py`. O compilador deriva
o resultado exato a partir do pai vinculado por hash e das 72 decisões.
Qualquer alteração não autorizada é rejeitada antes de compilar.

Os mesmos limites permanecem: 16 bytes, glifos conhecidos, números e níveis
imutáveis, zero padding comprovado, ponteiros/IDs/atributos e teto físico de
24 bytes preservados. Não foi alterada a política global de terminologia.

Três usos descritivos de Remote foram autorizados por registro:
360 Granada Remota, 874 Laser remoto, 875 Laser remoto EX. A exceção remove
somente o aviso de Remote nesses pares origem/destino exatos; o comando
Remote e qualquer outro nome protegido continuam sob as regras anteriores.

Dois grupos de nomes originalmente iguais recebem tratamento por registro:

| IDs | Decisão |
| --- | --- |
| 142 / 780 | 142 mantém Traje de criada; somente 780 recebe Roupa empregada |
| 822 / 823 / 824 | Sucata leve / Sucata média / Sucata pesada |

São campos físicos independentes de 128 bytes; seus getters e o limite de
nome são os mesmos já verificados. Não se deduplicam IDs nem se altera um
pool compartilhado. Todos os outros grupos repetidos mantêm consistência.
A política legada continua rejeitando essas diferenças e as traduções de
Remote sem o opt-in. Não generalizar as exceções para futuros nomes.

Os pesos das sucatas por ordem de ID e o nome Detector básico (710) são
decisões provisórias do usuário, ainda sem comprovação dos pesos/alcances
jogando. Não apresentar as hipóteses editoriais como efeitos confirmados.

## Nomes correspondentes em batalha

Trinta rótulos já traduzidos de batalha repetem os nomes alterados e precisam
seguir as mesmas escolhas. Política opt-in
`spack-user-reviewed-item-action-labels-fixed-fields-v002`, vinculada ao mesmo
manifesto, sincroniza apenas essas contrapartes existentes. Metadados,
identidades de origem e todos os demais rótulos são preservados. A proteção
de Remote só admite os três destinos exatos nas ações 112, 134 e 135.

O vínculo aqui é textual/estrutural, não descoberta de novas identidades
canônicas. Não mudar habilidades, efeitos ou inimigos por inferência do nome.
Campos e limites originais de batalha, números, controles e atributos não
foram relaxados. As mesmas traduções de Beam Sword são mantidas em suas duas
ocorrências; Regeneration segue Regeneração conforme os dois itens aprovados.

## Primeira escolha corrigida

Somente `map.sel.1df48484`, em `translations/regiao-inicial-v038.json`, filho
da v037:

| Antes | Agora |
| --- | --- |
| Vou ser Hunter. | Eu quero ser um Hunter. |

A segunda opção continua **Está bem, serei mecânico.** Separador TAB, ordem
das opções, controles, registro e referências não mudam. Conjunto codificado
ocupa **51 dos 55 bytes disponíveis**. Os demais 7.230 registros do catálogo
mantêm suas decisões e textos; não há aliases apontando para essa escolha.
Número de registros MAP traduzidos continua 6.024, com 5.983 corpos/opções e
912 referências de rótulos; uma revisão não aumenta a cobertura.

## Auditoria adicional e verificações

`tools/audit_human_item_decisions.py` reconcilia a entrada humana com o pai e
o lote novo. A execução real conferiu A/B/C/D/E, zero conflitos, e produziu
uma concordância de **69 possíveis referências literais** a termos anteriores
em campos de interface/diálogo. São candidatos para revisão contextual,
incluindo palavras comuns que podem continuar corretas. Não houve substituição
global nem alteração de descrições. Dados completos em
`work/revisao-humana-itens-v001/conferencia/concordancia.json`.

Passaram **90 testes distintos**, 12 novos: escopo de 72 IDs, 35 ratificados,
16 bloqueados, alternativa preservada, atributos/ponteiros, limites e codec,
exceções restritas/legado, 30 contrapartes, artigo/controle/capacidade da escolha,
reversão e preservação de todas as demais decisões. Inclui regressões de
nomes, batalha, política global, pintura, carregamento, auditoria, preflight,
retenção, alpha e quatro verificações do compilador de diálogos.

Adicional de largura em `tools/measure_item_name_widths.py` e
`reports/revisao-humana-itens-v001-larguras.json`: 474 probes únicos do layout
v004 herdado pelo v005, tamanhos 22/26 e modos 0/1/2, para os 72 nomes.
Compara soma de avanços ao envelope observado nos 1.041 nomes originais;
não mede recortes reais de todos os menus nem executa desenho/GPU.
Somente **939 — Poder de reserva** supera o máximo original no modo 1:
175 contra 173 no tamanho 22, e 204 contra 203 no tamanho 26. Nos outros
modos fica dentro do envelope. A escolha cabe em 16 bytes e foi mantida
como aprovada; não houve prova de overflow visual. Conferir esse nome nas
telas reais e não declarar que o limite em bytes garante largura perfeita.

O comparador de ISOs agora normaliza somente os prefixos dos 72 slots de
nomes autorizados, pois os patches antigos/novos podem ter comprimentos
distintos dentro do mesmo campo. Compara a união dos prefixos contra a fonte
imutável, sem autorizar expansão acima de 24 bytes, realocação ou mudanças
de atributos. Não é uma tolerância genérica para diferenças inesperadas.

## Construção e teste manual

```powershell
python tools/build_translation_pilot.py --draft translations/regiao-inicial-v038.json --interface-draft translations/interface-v042.json --compact-output --build-iso --output work/minha-v042
python -m unittest discover -s tests -p test_human_item_revision.py
python tools/audit_human_item_decisions.py --output work/minha-conferencia-humana
```

Usar pastas novas. Após comparação integral aprovada, Iniciar-Teste.cmd aponta
para `work/interface-v042/MetalSaga-ptbr-interface-v042.iso` e
Preparar-Interface.cmd valida MAP v038/interface v042.

Teste manual futuro: primeira decisão, inventário/lojas e nomes de ações de
batalha, especialmente Laser remoto, Comprimido/Soro e os três tipos de sucata.
Conferir largura visual nas telas; teto em bytes não prova todos os contextos.
Fonte/layout v005, pintura aprovada, Carregando, pôsteres e títulos de minijogos
permanecem iguais. Sem navegação autônoma PCSX2 ou cópia OneDrive nesta rodada.
O desligamento solicitado ocorre somente depois de salvar, verificar e enviar
os arquivos próprios ao GitHub.

## Integridade da entrega

ISO v042 concluída, com 1.704.427.520 bytes e SHA-256
`5a687f70e0ae3bf79966204fbd36ea944951c5d6ebf75ebfc99d64c1e247fa69`.
A comparação integral com v041 confirmou somente 1.035 bytes diferentes,
em 103 patches: 72 nomes de itens, 30 rótulos de ações e uma escolha MAP.
Diretório da ISO, fontes, layout e todos os demais bytes foram preservados.
Relatórios: `reports/interface-v042.json` e `reports/interface-v042-delta.json`.
Isso não constitui teste de execução no PCSX2.

A auditoria atualizada fica em `work/auditoria-itens-v042/`, com resumo próprio
em `reports/auditoria-itens-v042.json`; a auditoria v040 permanece intacta.
Retenção conferida: cinco ISOs de trabalho. A alpha permanente foi conferida
por SHA-256 e permanece fora da retenção, sem alteração.
