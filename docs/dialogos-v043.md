# Rótulos do Exército Blueberry — MAP v043 / interface v050

Esta rodada traduz 32 referências de falantes cuja função estava em inglês,
preservando integralmente todos os corpos, opções e comandos da v049.
Não são 32 diálogos inéditos: 21 registros já tinham alterações anteriores;
os outros 11 passam a ter somente o rótulo traduzido, com silêncios e gritos
mantidos. O total fica em 6.043 registros MAP alterados, dos quais 5.991 têm
corpo/opções modificados, e 980 referências de falantes traduzidas.

## Decisões contextuais

| Rótulo | Tradução | Ocorrências |
| --- | --- | ---: |
| BB Trooper | Soldado BB | 8 |
| BB Trooper #1 | Soldado BB #1 | 8 |
| BB Trooper #2 | Soldado BB #2 | 5 |
| BB Trooper #3 | Soldado BB #3 | 5 |
| BB Trooper #4 | Soldado BB #4 | 3 |
| BB Trooper #5 | Soldado BB #5 | 1 |
| BB Trooper #6 | Soldado BB #6 | 1 |
| Ex-BB Trooper | Ex-soldado BB | 1 |

A revisão considerou as 32 falas originais e traduções anteriores. A cena
com Rosa em Beldaire identifica o grupo como Exército Blueberry; a fala
`map.msg.0be1be30`, entre as falas numeradas, cita esse exército. Os diálogos
de contratação de proteção em `0x12835580` e `0x1D0BE710` e a fala do
ex-integrante em `0x038DF66C` são coerentes com essa função. Não se atribui
um nome próprio novo aos indivíduos nem se altera a sigla BB ou a numeração.

**Soldier**, enquanto classe preservada pelo usuário, permanece Soldier em
todas as ocorrências. Esta revisão se aplica ao termo distinto Trooper nos
32 rótulos exatos, sem substituição global de vocabulário. Hunter, Punk,
nomes de personagens, inimigos, cidades, tanques e itens não mudam.

## Reinserção e limites

Política opt-in `map-reviewed-bb-occupation-original-slots-v006`, módulo
`tools/speaker_faction_review.py`, manifesto `translations/rotulos-bb-v006.json`.
Pais vinculados por hash: MAP v042 e interface v049. O conjunto completo é
recalculado e comparado ao manifesto; os destinos admitidos são explícitos.

São 31 registros msgn e uma escolha smnn (`map.smnn.0be1c7bc`). Os destinos
usam somente ASCII: Soldado BB tem 10 bytes, os numerados 13 bytes, e
Ex-soldado BB 13 bytes. Cabem nos slots originais de 11 ou 15 bytes, com NUL
e padding preservados. Não há reposicionamento, revisão de corpos, crescimento
de registros ou alteração de ponteiros/SSD/extents.

O transporte reutiliza o mecanismo fixo de rótulos já comprovado, extraído
para `apply_fixed_slots` com um validador específico. A política histórica
continua recusando esses termos; sua lista ROLES não foi ampliada. A nova
camada preserva os relatórios, offsets e fingerprints das camadas anteriores.
Os descritores originais continuam com label.editable=false.

Além do round-trip estrutural, o teste executa os recortes originais de busca
do rótulo antes/depois e os recortes de comprimento, argumentos da alocação,
cópia e getter com memória simulada. O alocador é simulado. Não são execução
integral da VM, renderizador, retratos, caminho SIMD ou PCSX2.

## Pendências preservadas

Os 13 rótulos sem espaço da v049 continuam byte a byte iguais, incluindo suas
falas. Há outras 534 referências fora desse recorte; incluem nomes, marcadores,
termos preservados e funções ainda não liberadas. Não são 534 traduções
obrigatórias comprovadas.

Mantêm-se as 16 revisões humanas de itens bloqueadas, os 19 nomes N$3
preservados e as três raízes especiais sem semântica comprovada. Não reabrir
o painel japonês de cães excluído pelo usuário. Interface conserva 3.848
unidades heterogêneas e 541 nomes de itens aplicados. Não calcular porcentagem
total do jogo a partir destas contagens.

## Como executar e reproduzir

Abra **Iniciar-Teste.cmd** para a ISO v050; **Preparar-Interface.cmd** valida
a receita sem criar outra imagem. **Auditar-Traducao.cmd** atualiza o catálogo
local de pendências. Os testes visuais permanecem para a partida normal do
usuário, conferindo a identificação dos soldados e o avanço da escolha de
Beldaire. Não é necessário provocar os erros nativos ou alcançar cada fala.

```powershell
python tools/build_translation_pilot.py --draft translations/regiao-inicial-v043.json --interface-draft translations/interface-v050.json --compact-output --build-iso --output work/minha-v050
python -m unittest discover -s tests -p test_speaker_faction_review.py
```

Usar pasta nova para reproduzir a construção. As ferramentas executam
localmente sem IA/APIs. A retenção mantém cinco ISOs de trabalho; a alpha
permanente fica separada. Nenhuma transferência OneDrive, desligamento ou
navegação autônoma no emulador foi solicitada nesta rodada.

ISO: `work/interface-v050/MetalSaga-ptbr-interface-v050.iso`.
Tamanho: 1.704.427.520 bytes. SHA-256:
`cc5932c63c5497b69c9e14396aef1ce917584e7c3359e8bcdeae3e5fec22c080`.
Preflight integral aprovado, sem transação pendente. Alpha conferida pelo
hash histórico. Fonte/layout v005 e todos os gráficos anteriores preservados.


## Resultado da validação

**199 testes passaram**, nove específicos novos, zero falhas/erros/pulados.
A comparação integral com v049 confirmou **288 bytes em 32 registros MAP**;
diretório, extents, tamanho e todos os demais bytes permanecem iguais, incluindo
ELF, fontes e gráficos. Não houve execução no PCSX2. O nome do falante e o
avanço da escolha continuam aguardando conferência na partida do usuário.

A auditoria de nomes conferiu 10.698 campos/594 termos e 541 nomes de itens,
com 65 ocorrências preservadas e zero sem decisão. Ledger atualizado em
translations/consistencia-nomes-decisoes-v007.json. Os hashes contextuais e
as evidências da entrega estão consolidados em reports/interface-v050.json;
a comparação integral está em reports/interface-v050-delta.json.
