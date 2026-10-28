# Interface v045 — quatorze nomes pendentes resolvidos

O usuário pediu resolver as pendências após a v044. Esta rodada resolve os
14 nomes genéricos do catálogo pendente, com decisões compactas de redação
dentro do teto atual. Não representa uma nova revisão humana de cada nome.
As 16 revisões anteriormente bloqueadas são um conjunto separado e conservam
seus nomes anteriores; não foram aplicadas por analogia.

## Nomes finais

| ID | Nome final | Bytes do projeto |
| --- | --- | ---: |
| 625 | Presa | 5 |
| 631 | Presa grande | 12 |
| 635 | Peça cilíndr. | 15 |
| 650 | Lâm. de espada | 15 |
| 695 | Placa de ônibus | 16 |
| 701 | Sucata cibern. | 14 |
| 741 | Jarro de porcel. | 16 |
| 753 | Guaxinim | 8 |
| 762 | Máq. de vendas | 15 |
| 765 | Roupeiro orient. | 16 |
| 768 | Geladeira comum | 15 |
| 781 | Vest. garçonete | 16 |
| 786 | Mira infraverm. | 15 |
| 1037 | Cinturão | 9 |

Não foram removidos acentos nem criados glifos. As abreviações conservam
peça cilíndrica, lâmina de espada, sucata cibernética, porcelana, máquina de
vendas, estilo oriental, vestido de garçonete e infravermelho. Não substituem
material por outro ou infravermelho por térmico. O nome Cinturão corresponde
ao contexto de Champion Belt; a descrição continua Você é o campeão!

O guaxinim continua identificado como figura de barro pela descrição existente.
A geladeira permanece distinguível das variantes dupla/chique. Sua descrição
específica agora diz `Geladeira compacta|de uma porta.`, preservando o caráter
compacto e a informação de uma porta. A descrição é exclusiva do ID 768;
nenhuma descrição compartilhada de roupeiros ou componentes foi especializada
para um único item.

Resultado: **541 nomes traduzidos, zero pendentes no recorte conhecido**,
500 preservados e 308 registros vazios entre os 1.349 IDs. Os 500 preservados
incluem nomes protegidos e decisões intencionais; não equivalem a 500 traduções
faltantes. São **3.836 campos de interface**, mais 14, sem contar a revisão de
descrição como um campo novo. MAP mantém 6.024 registros com alguma alteração.

## Consistência e referências narrativas

A busca ampliada aos 541 nomes encontrou quatro referências literais a
Bus Stop Sign. Elas agora usam Placa de ônibus, inclusive o gênero feminino
em uma placa rara. Foram preservados opções, preços, controles e demais falas:

- `map.msg.0e551d94`
- `map.msgn.0e76fcc4`
- `map.smsg.06493b00`
- `map.smsg.0e5517d4`

Fang também é nome próprio: **sete ocorrências de personagem** permanecem.
Duas menções à arma **Twin Fang** continuam intactas. Só os componentes 625 e
631 usam Presa/Presa grande. As proteções globais de Fang e Bus Stop Sign não
foram removidas; exceções são de pares origem/destino/ID exatos.

O rótulo Homem de `map.msgn.0e76fcc4` já usava a política de cauda alinhada.
Seu hash de corpo compilado foi recalculado após a revisão, executando o
compilador de registro e o cálculo de posicionamento existentes. Origem,
rótulo Homem e offset de destino são os mesmos. Não dispensar essa verificação
nem atualizar hashes de ligação por suposição.

A conferência local abrange 10.682 campos e 594 termos: **65 matches residuais,
todos classificados e corretos; zero sem decisão**. O ledger v002 herda as 81
decisões anteriores e acrescenta 13: nove preservações de Fang/Twin Fang e
quatro referências corrigidas de placa. São 94 decisões históricas (29
correções e 65 preservações), não 94 problemas ainda presentes.

## Construção e limites

Manifesto: `translations/nomes-pendentes-resolvidos-v001.json`; receita
`translations/interface-v045.json`, sobre MAP `regiao-inicial-v040.json`.
`tools/pending_name_resolution.py` vincula ao hash da v044 os 14 nomes,
uma descrição, quatro falas e o único hash de ligação de rótulo revisto.
As políticas anteriores seguem preservadas e os demais campos são recusados.

Nenhum teto foi aumentado: nomes até 16 bytes nos campos físicos existentes;
repack da descrição no mesmo pool, com aliases e referências conferidos;
nenhum crescimento de registro, SSD ou extent ISO. Fontes/layout v005 e arte
permanecem. Fonte original, BIOS, saves e alpha não são alvos de edição.

Auditoria completa atualizada em `work/auditoria-itens-v045/`, sem sobrescrever
as auditorias que o usuário possa estar revisando. Comparou os 1.349 campos
principais e 50 campos de variantes de motores à ISO real; 26 variantes são
preenchidas e permanecem preservadas. Resumo público em
`reports/auditoria-itens-v045.json`.

## Verificações realizadas

- **113 testes aprovados**, oito novos, incluindo os 527 nomes anteriores,
  escopo exato, controles/nomes próprios, rejeição de alterações extras,
  atributos, round-trip combinado de nomes/descrições, quatro referências
  narrativas e preservação da posição e texto do rótulo Homem.
- **444 probes** de glifos/layout nas fontes 22/26 e modos 0/1/2. Nenhum dos
  14 nomes ultrapassa o maior avanço observado nos originais.
- Prévia técnica de glifos GFI existentes, sem estreitamento horizontal,
  inspecionada em `work/nomes-pendentes-v001/previa-nomes.png`.
- Auditor local com ledger: zero matches sem decisão no recorte literal.

Não houve execução do PCSX2 nesta rodada. A prévia e os probes não comprovam
todos os recortes de menus. Conferir em partida normal inventário/mobília,
componentes e as quatro falas da placa, quando encontradas, sem exigir que o
usuário alcance cada cena agora. Não há cópia OneDrive ou desligamento pedido.

## Reprodução local

```powershell
python tools/build_translation_pilot.py --draft translations/regiao-inicial-v040.json --interface-draft translations/interface-v045.json --compact-output --build-iso --output work/minha-v045
python -m unittest discover -s tests -p test_pending_name_resolution.py
python tools/audit_name_consistency.py --recipe translations/interface-v045.json --decisions translations/consistencia-nomes-decisoes-v002.json --output work/minha-conferencia-v045.json
```

Usar novas saídas. Não utiliza IA, APIs ou rede para extração, compilação e
conferência binária. A receita e os relatórios preservam as decisões para
reprodução, mesmo quando uma ISO antiga sair da retenção.

## Entrega e integridade

`Iniciar-Teste.cmd` abre `work/interface-v045/MetalSaga-ptbr-interface-v045.iso`.
`Preparar-Interface.cmd` valida interface v045/MAP v040. A imagem tem
1.704.427.520 bytes e SHA-256
`094d74c2181446647aeceb29ef53dd33095b8c3e6a11b447ed7e2ae6af40ba7c`.

Preflight integral aprovado. Comparação completa v044 → v045: **4.215 bytes
em 176 patches físicos**, sendo quatro registros MAP e 172 patches S_PACK.
Incluem os 14 nomes e o repack da descrição com os ponteiros necessários;
não são 176 traduções novas. Os demais bytes e o diretório ISO permanecem.
Nenhuma diferença em fontes, ELF ou gráficos. Retenção conferida em cinco
ISOs e alpha permanente conferida por SHA-256.
Relatórios: `reports/interface-v045.json` e `reports/interface-v045-delta.json`.
