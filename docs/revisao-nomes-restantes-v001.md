# Sugestões dos nomes restantes — revisão pendente

O usuário pediu mapear os nomes restantes e receber sugestões antes de decidir
se serão aplicadas. A base permanece interface v042; não modificar a ISO ou as
receitas por causa desta entrega.

Foram conferidos os 22 IDs pendentes da auditoria completa v042 e os 16 IDs
de revisões humanas bloqueadas: 38 IDs distintos, sem duplicação. A alternativa
não confirmada do ID 861 aparece separadamente. Os 500 nomes preservados no
original continuam fora da dívida de tradução; não reabrir nomes protegidos.

Entrega local em `work/revisao-nomes-restantes-v001/sugestoes.md` e
`work/revisao-nomes-restantes-v001/sugestoes.json`: original, nome atual,
sugestão, bytes, contexto de descrição disponível, hashes/offsets e campos de
decisão humana inicialmente vazios. Não há importação automática. O catálogo
bilíngue permanece fora do Git; metadados em
`reports/revisao-nomes-restantes-v001.json`.

Quatro sugestões do grupo de 22 cabem no teto de 16 bytes: IDs 342, 625, 631 e
695. Isso não libera aplicação: Fang exige revisão terminológica, e os demais
continuam sujeitos às políticas vinculadas. Dezessete excedem o teto e Óculos
requer o glifo Ó. As 16 revisões bloqueadas mantêm a escolha anterior e mostram
alternativas compactas para avaliação; não sobrepor essas opções à preferência
do usuário. Ídolo de barro exige Í. Não remover acentos, artigos ou material
distintivo para simular encaixe seguro.

Melhorias propostas frente às sugestões antigas: Presa grande em vez de
Presona, Placa de ônibus em vez de Placa de parada, Máquina de vendas e
Geladeira de uma porta para conservar a informação original. Todas pendentes.

Verificações executadas: cobertura exata dos 22 e dos 16 IDs, unicidade dos
38, codificação pelo codec real, limite de bytes das alternativas compactas e
hash inalterado da receita v042. Não houve construção, alteração de ISO,
execução do PCSX2 ou teste visual nesta rodada. Esperar a revisão do usuário
antes de compilar qualquer uma dessas decisões.
