# Interface v058 — lote completo de armas aprovado

Aplicadas em uma única versão consolidada as decisões do arquivo
METAL_SAGA_ARMAS_INSTRUCOES_CODEX.md recebido do usuário. Foi usada a tabela
completa do Markdown, explicitamente equivalente ao CSV mencionado no texto;
nenhum CSV adicional foi necessário e nenhuma sugestão automática foi aplicada.
SHA-256 do documento: 4a622a8682d61f865c797eb4af7c435396aea7e38ba7fc5996f00adcf2ee8dcf.
O original recebido permanece em work/revisao-armas-v001/.

| Resultado da aprovação | Quantidade |
|---|---:|
| Registros auditados | 175 |
| ALTERAR — aplicados | 86 |
| ALTERAR — já aplicados | 0 |
| MANTER — preservados | 89 |
| Fallback sem acento | 0 |
| Conflitos ou nomes bloqueados | 0 |
| Referências de ações de batalha atualizadas | 91 |
| Munições especiais do anexo preservadas | 15 |

Os 175 registros continuam distribuídos em 100 portáteis/personagens/cães,
30 MAIN, 21 SUB e 24 SE. O item 1042, Rede elétrica, é MANTER e não foi
regravado. Bare Hands continua sendo dois registros distintos, 19/74, ambos
com Mãos nuas. Gibson, Vulcan, Gatling, modelos, nomes exclusivos e demais
MANTER mantêm os valores atuais. Categorias MAIN/SUB/SE não foram alteradas.

O relatório bilíngue completo fica em
work/revisao-armas-v001/APLICACAO-ARMAS-APROVADAS.md, com os 175 IDs,
originais, valores anteriores e resultados. Os dados originais ficam fora
do Git. Decisões próprias e hashes estão em translations/armas-aprovadas-v001.json.

## Codificação, espaço e desenhos

Todos os 175 valores foram conferidos pelo codificador real do projeto e
coincidiram com as estimativas do documento. Todos os novos nomes têm até
16 bytes. Nenhum acento foi removido; nenhuma fonte, glifo ou métrica foi
criada ou modificada. Mantido o perfil aprovado ptbr-layout-v005.

Os nomes ocupam somente os prefixos NUL das posições originais em registros
S_PACK de stride 128, campo de nome de 24 bytes. O novo teto permanece 16;
23 bytes físicos não foram liberados. Nas ações, alterou-se somente o campo
de nome de 32 bytes, com os mesmos textos de até 16 bytes. Os identificadores,
calibres, ordem dos registros, estatísticas, descrições, referências e lógica
de combate ficaram intactos. A ordenação visual que o próprio jogo faça
pelo nome pode naturalmente refletir as novas palavras.

Foram executados os ponteiros e encaminhamentos originais para cada ID,
o contador de bytes e as métricas de cada caractere nos três modos conhecidos
de fonte 22. Maior avanço: **176**; margem até a coluna de preço: **66**;
margem do painel direto: **58**. A geometria da loja foi novamente exercitada
com as instruções originais e preço modelado de oito dígitos. Evidência em
reports/armas-aprovadas-largura-v001.json. Isso não executa GPU, todos os
formatadores ou todas as caixas reais do jogo; a aparência aguarda teste do usuário.

As exceções antigas de nomes de itens com 18/19 bytes não foram ampliadas.
O envelope anterior de mensagens continua conservador: os novos nomes não
ultrapassam 16 e, portanto, não aumentam o máximo global já comprovado de 19.

## Aliases e proteções

As 91 referências de ações com o mesmo nome original receberam exatamente
o nome aprovado da arma correspondente. Não são 91 armas adicionais.
Campos de inimigos/procurados e pôsteres não foram editados.

Existe uma repetição de Grenade Gun no item **946**, uma habilidade fora
dos 175 IDs revisados. Como o usuário autorizou somente ALTERAR, o item 55
passa a Lança-granadas e **946 permanece intacto**. Essa exceção de alias é
explícita no manifesto; não se ampliou a autorização para outras habilidades.

Somente quatro proteções terminológicas recebem exceções locais aprovadas:
item 5 (Tiger Claw), 59 (Remote Wrench), 247 (Swatter) e 252 (Drill Gun),
com suas respectivas referências de ação. Tiger, Remote, Swatter e Drill Gun
continuam protegidos em todos os outros contextos. O compilador legado
continua recusando as armas protegidas sem este perfil opt-in.

## Integração e reprodução

Ferramenta tools/approved_weapon_names.py, política exata
human-approved-86-weapon-names-fixed-fields-v001. A receita filha v058
valida integralmente o pai v057, o documento por hash, os 175 IDs e nomes
originais, as decisões e os hashes de cada registro. Não promove o catálogo
de sugestões da v055 para aprovação.

```powershell
python tools/approved_weapon_names.py --prepare
python tools/build_translation_pilot.py --draft translations/regiao-inicial-v044.json --interface-draft translations/interface-v058.json --compact-output --build-iso --output work/interface-v058-reproducao
python -m unittest discover -s tests -p test_approved_weapon_names.py -v
```

O preparo usa o documento guardado e a auditoria local original; a compilação
usa os manifestos versionados e os arquivos de referência. Sem IA, APIs ou
internet para o processamento binário. Os builds anteriores permanecem reproduzíveis.

A primeira tentativa de integração foi bloqueada pela regra legada de
ações de 18 bytes, que não recompilava diretamente as exceções antigas de
19. Foi corrigido o reaproveitamento da saída validada do pai, sem relaxar
a regra antiga ou a nova de 16. Nenhuma ISO foi gerada na tentativa bloqueada.

## Versão de teste e verificação

**Iniciar-Teste.cmd** abre
work/interface-v058/MetalSaga-ptbr-interface-v058.iso.

SHA-256: `45724669564ec8bd9ef5303d85c4a4387707464de5c519776e70f93fb2d6a0fd`.
Tamanho: 1704427520 bytes.

São **627 nomes de itens aplicados** (541 anteriores + 86) e **4155 unidades
heterogêneas de interface**. MAP v044 continua com 6044 registros alterados,
5991 corpos/opções e 991 referências de falantes. Mundo aberto e os desenhos
de batalha/Satcom da versão anterior permanecem iguais.

Passaram 76 testes distintos: 11 do novo lote e 65 de regressão. Incluem
round-trip, guarda de 16 bytes, preservação dos 89 MANTER/15 munições,
aliases, estatísticas, identidade de todos os patches anteriores, instruções
de layout e rejeição de alterações fora da aprovação. Relatórios públicos:
reports/interface-v058.json e reports/interface-v058-delta.json.

O PCSX2 não foi executado nesta rodada. Na próxima partida, conferir nomes
em equipamento, lojas e ações de batalha; observar acentos, largura, preços
e seleção. As métricas e a integridade não equivalem a validação visual.
Mantidas cinco ISOs de trabalho e a alpha protegida. Sem envio ao OneDrive.
O desligamento foi solicitado para depois da conclusão e do registro da entrega.
