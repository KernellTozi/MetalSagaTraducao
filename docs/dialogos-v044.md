# Revisão contextual — MAP v044 / interface v051

Esta rodada aplica 11 rótulos descritivos e revisa cinco corpos já traduzidos,
preservando os limites atuais de itens e os demais recursos da v050. Não são
cinco diálogos novos descobertos; a cobertura de corpos/opções permanece 5.991.
Os nomes de personagens, cidades, tanques, procurados e equipamentos continuam
preservados conforme as decisões existentes.

## Conferência do que falta

A auditoria da v050 tem zero corpos nativos e zero outros controles pendentes
no catálogo conhecido; os 19 adiamentos técnicos são nomes N$3 preservados.
Isso não prova cobertura de todo o jogo. A busca dirigida por palavras inglesas
comuns encontrou casos de nomes preservados, como The Professor e IS-3; ela é
uma triagem limitada, não uma prova linguística de completude.

Continuam as 16 revisões de itens, com análise específica em
docs/capacidade-nomes-v001.md, e 13 rótulos sem espaço. As outras referências
incluem nomes/expressões preservados e termos que exigem decisão contextual;
não são automaticamente uma dívida de tradução. Esta rodada aproveita um
subconjunto seguro dessas referências enquanto os buffers de itens seguem
sem autorização para crescer.

## Onze rótulos

| Tradução | Ocorrências | Contexto revisado |
| --- | ---: | --- |
| Bárbaro A | 3 | Incursão contra os mercadores |
| Bárbaro B | 2 | Mesma conversa; identificador B mantido |
| Bárbaro C | 2 | Mesma conversa; identificador C mantido |
| Bárbaro D | 1 | Aviso a Maxwell; identificador D mantido |
| Ex-bárbaro | 1 | Relato da derrota da Liga dos Bárbaros Incivilizados |
| Ex-ladrão | 1 | Conversa sobre a gazua e Oliver |
| Cápsula (Binramen) | 1 | Descrição da cápsula, com Binramen preservado |

A função Barbarian corresponde aos membros da Liga já mencionada em português
nas falas; não foi renomeada uma tabela de inimigos ou de chefes. O prefixo de
ex-integrante continua explícito. O recipiente Cápsula foi localizado, mantendo
o nome do procurado entre parênteses. Hunter, Soldier, Punk, nomes próprios e
marcadores desconhecidos permanecem iguais. As imagens dos Wanted não mudam.

Os 11 rótulos cabem nos slots originais de 11, 15 ou 19 bytes, com NUL e padding.
As falas e sons desses 11 registros permanecem intactos. Só a ocorrência da
cápsula estava totalmente inalterada antes: o total de registros MAP alterados
passa de 6.043 para 6.044 pelo rótulo, não por nova tradução de corpo. São
991 referências de falantes traduzidas, 13 bloqueadas no recorte de espaço e
523 outras referências fora desse recorte, sem aprovação automática.

## Cinco revisões de fala

| Registro | Revisão |
| --- | --- |
| map.msgn.1282e1d0 | “Minha pontaria é ruim” dá uma formulação natural; preserva a probabilidade de errar todos os alvos e a falta de balas. |
| map.smsg.0e77864c | Recupera que as cargas vão sobretudo para o oeste e compara o frete de grãos/álcool com o de verduras. As opções da conversa não mudam. |
| map.msgn.0be22c78 | Recupera a abundância de Scorpions e a orientação de que o leste é o melhor lugar para ganhar dinheiro; Torikami permanece. |
| map.msgn.0e7781f4 | Recupera a ida à casa para contar à esposa e aos filhos o que aconteceu, mantendo a lembrança das expressões deles. |
| map.msgn.0e76d6c4 | Torna natural a preocupação da interlocutora com a ferida, preservando a ordem para procurar tratamento. |

Os controles de linha/página, escolhas e demais segmentos foram preservados.
Não houve remoção de artigos, acentos ou fatos para fechar orçamentos. As cinco
revisões passam sem avisos conservadores de largura no compilador; isso não
substitui a inspeção das caixas no renderizador.

A frase sobre o peixe em map.msg.0be140fc já estava correta; a quebra de
linha do JSON havia sido interpretada incorretamente na triagem inicial. Foi
conferida e preservada, sem contar como revisão ou alteração. A ferramenta
recusa agora a inclusão de corpos idênticos ao pai neste perfil.

## Implementação e integridade

Política opt-in `map-contextual-final-dialogue-review-v007`, em
tools/dialogue_context_finish.py; manifesto translations/revisao-contextual-v007.json.
Pais vinculados por hash: MAP v043 e interface v050. A lista de rótulos e os
cinco textos são exatos; mudanças adicionais são recusadas. A política de
rótulos histórica continua bloqueando esses termos, sem alterar sua ROLES.

Os rótulos reutilizam o transporte de slots fixos, com codec, termos protegidos,
busca original do rótulo, cópia/getter e round-trip estrutural. A revisão de
corpos passa primeiro pelo compilador histórico com o rótulo original protegido;
depois é mesclado somente o intervalo do corpo sobre o registro compilado pai.
O rótulo traduzido/movido e as escolhas existentes são conferidos e preservados.
O alvo precisa caber antes do próximo segmento efetivamente compilado, além
do slot original. Nenhum dos cinco IDs é pai ou filho de alias de tradução.

Headers, tamanhos, SSD, extents, fingerprints e offsets permanecem. Os wrappers
compilados de offsets também ficam iguais. Não há edição de ELF, fontes,
gráficos, tabelas de itens ou atributos. Os relatórios das políticas anteriores
permanecem separados e íntegros. Os laços de busca/cópia usam memória sintética;
alocador, renderizador, retratos e jogo completo não são executados por isso.

## Execução local

Abra **Iniciar-Teste.cmd** para a ISO v051; **Preparar-Interface.cmd** valida
as receitas sem construir outra imagem. **Auditar-Traducao.cmd** audita v051 e
continua executando o diagnóstico de nomes vinculado à base v050: a configuração
de itens é idêntica nas duas versões, não uma revisão nova daqueles 16 nomes.

```powershell
python tools/build_translation_pilot.py --draft translations/regiao-inicial-v044.json --interface-draft translations/interface-v051.json --compact-output --build-iso --output work/minha-v051
python -m unittest discover -s tests -p test_dialogue_context_finish.py
```

Usar nova pasta para reprodução. Não houve navegação no PCSX2: conferir nomes,
quebras, escolhas e avanço das falas em uma partida normal, sem precisar buscar
imediatamente todas as cenas. Respeita-se o limite de cinco ISOs de trabalho e a alpha
independente. Sem cópia OneDrive ou desligamento nesta rodada.


## Validação consolidada

Passaram **106 testes distintos**, incluindo nove do perfil novo. Os nove foram
reexecutados no escopo final e a travessia original dos rótulos também foi
conferida após as revisões; repetições não são somadas como testes adicionais.
A comparação integral v050 → v051 confirmou **539 bytes em 16 registros MAP**,
exatamente os 11 rótulos e cinco corpos. Todos os demais bytes, diretório e
extents são iguais, incluindo ELF, fontes, gráficos e itens.

O lote usa work/interface-v051-final/MetalSaga-ptbr-interface-v051.iso,
1.704.427.520 bytes. SHA-256:
5c3489e7837ae4938e00f84a9a5599c11e48ebb259366b7377e1fe351f725c12.
A imagem intermediária redundante foi removida após conferir tamanho/hash;
os relatórios locais de diagnóstico ficaram preservados. A alpha permanente
foi reconferida pelo hash histórico.

A auditoria de nomes examinou 10.698 campos/594 termos e 541 nomes de itens:
65 correspondências preservadas, zero sem decisão. Ledger em
translations/consistencia-nomes-decisoes-v008.json. A ISO passou na conferência
de tamanho/hash/transações; o iniciador do jogo foi verificado em dry-run,
sem abrir o PCSX2. Evidências em reports/interface-v051.json e
reports/interface-v051-delta.json.
