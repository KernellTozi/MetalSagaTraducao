# Interface v054 — nove revisões restantes de nomes

Aplicadas as nove revisões aprovadas ainda pendentes, sem abreviar nomes,
remover novos acentos, reduzir fonte ou aumentar registros. São revisões de
nomes já traduzidos: continuam 541 nomes aplicados, 6.044 registros MAP
alterados e 3.848 unidades heterogêneas de interface. A fila específica de
16 revisões humanas bloqueadas fica encerrada: uma exceção autorizada na
v052, seis revisões na v053 e nove nesta versão. Isso não significa que
todos os nomes, recursos ou testes do jogo estejam concluídos.

| ID de item | Nome aprovado aplicado | Bytes | Ação correspondente |
|---|---|---:|---|
| 354 | Bomba de petróleo | 18 | battle.action.0106 |
| 373 | Bomba de petróleo | 18 | mesma ação 0106 |
| 431 | Coleira anti-pulga | 18 | — |
| 647 | Retalho de casaco | 17 | — |
| 711 | Detector avançado | 18 | — |
| 798 | Corrente de cauda | 17 | — |
| 826 | Bandeira vermelha | 17 | — |
| 836 | Projétil explosivo | 19 | battle.action.0881 |
| 840 | Projétil elétrico | 19 | battle.action.0886 |

## Impedimentos identificados e tratamento

1. **Referência de largura insuficiente.** O diagnóstico inicial comparava
   nomes com o maior nome original, não com o painel consumidor. A nova
   ferramenta executa os métodos originais de geometria em memória simulada.
   O construtor VA 0x2B4F98 instala vtable 0x409680. Seu método +0x5C é
   VA 0x2B5268, que aplica os insets e chama 0x2B5170. O setter base
   0x142720 grava a geometria, o clamp 0x2B53F8 mantém o mínimo da skin,
   e o getter 0x2B52D8 recupera posição e tamanho lógicos.
2. **Origem do painel direto.** O caminho de desenho em ELF+0x40060..0x400DC
   obtém a posição pelo getter virtual +0x6C antes de chamar o desenhador
   do painel em 0x1B3A98. Quatro casos de posição/tamanho e ambas as skins
   foram exercitados nos testes. O painel do nome solicita 272; nome começa
   em +38, tamanho 22. Os avanços máximos são 187/198, abaixo dos 234 restantes.
3. **Separação de nome e preço em lojas.** A instrução R5900 MULT tem
   registrador de destino: o parâmetro 17 em 0x1D52A0 resulta em **22×17=374**
   unidades por linha, e não 17 caracteres nem metade desse valor. A rotina
   0x14E898 foi executada. A rotina 0x14EA98 coloca a coluna de oito dígitos
   em +264; nome inicia após ícone de 22. O orçamento até o preço é 242,
   deixando pelo menos 44 unidades de avanço. Nenhuma fonte foi diminuída.
4. **Listas e rótulos de ação.** Os chamadores observados solicitam largura
   320 para a lista de itens (0x118B30) e 288 para ações (0x11D090), tamanho
   de fonte 22. A construção do rótulo passa por VA 0x20F198; o chamador
   de ação usa `%s` e ponteiro do registro, não precisão de 18 bytes.
   Os 19 bytes dos dois projéteis cabem com NUL no campo físico de 32.
   A autorização nova é somente para essas duas ações e para a ação 0106;
   o validador genérico continua recusando ações de 19 bytes.
5. **Orçamento de mensagens dependente dos nomes.** Recompilado MAP v044
   e recalculados os mesmos 34 campos/35 páginas com limite independente
   de 19 bytes por item. Máximos: **92 células por página** antes do NUL,
   contra limite 99; **333 bytes por corpo**, abaixo de 1.024 incluindo NUL.
   O limite N0 continua condicionado a um nome válido com NUL dentro de 32
   bytes. Não se afirma que strcpy aceita entradas arbitrárias.
6. **Aliases.** Os itens 354/373 compartilham a origem e a ação 0106;
   ambos recebem a mesma redação aprovada. Todos os demais aliases fora
   do conjunto são recusados. As receitas anteriores ficam preservadas.

## Política e reprodução

`nine-approved-item-names-bounded-release-v002` em
`tools/remaining_item_name_release.py` vincula pai v053, revisão humana,
prova e os nove itens/três ações por hash. Somente os prefixos dos nomes
nos campos de 24 bytes e os campos das três ações são alterados.
Atributos, ponteiros, controles, tamanho de arquivos e fontes ficam iguais.
O limite legado de 16 para nomes e 18 para ações continua ativo fora deste
perfil. Idolo de barro e as seis revisões da v053 não mudam.

Ferramentas locais, sem IA, API ou internet:

```powershell
python tools/item_box_proof.py --output work/prova-nove-nomes-v002.json
python tools/item_name_capacity.py --current-recipe translations/interface-v054.json
python tools/build_translation_pilot.py --draft translations/regiao-inicial-v044.json --interface-draft translations/interface-v054.json --compact-output --build-iso --output work/interface-v054-reproducao
```

O relatório reports/prova-nove-nomes-v002.json registra instruções, hashes,
geometria, margens e todos os orçamentos. A sonda executa instruções escalares
originais, com memória RAM limitada e callback de atualização interceptado;
transferências de bits de ponto flutuante são modeladas, sem cálculo GPU.
São caminhos conhecidos e vinculados à fonte, não uma prova de todas as
chamadas indiretas, estados corrompidos, mutações de RAM ou layouts do jogo.

## ISO e teste futuro

Abrir **Iniciar-Teste.cmd** para
`work/interface-v054/MetalSaga-ptbr-interface-v054.iso`.

Tamanho: 1.704.427.520 bytes.
SHA-256: `ebeea1bebd13cf0576c99b9eaf656036d3e23cfe7168aa37b95432e3b448fe5e`.
Relatório de comparação integral: reports/interface-v054-delta.json.
Relatório consolidado e testes: reports/interface-v054.json.

Validação final: **159 testes distintos**, zero falhas, erros ou ignorados.
A comparação integral v053→v054 confirmou **176 bytes diferentes em 12
patches S_PACK**; todos os demais bytes, diretório ISO e fontes são iguais.
Conferidos tamanho, SHA-256, ausência de transações e comando do iniciador.

O PCSX2 não foi iniciado nesta rodada. A conferência visual permanece
pendente: durante a partida, observar os nomes completos nas listas de itens,
menus de personagens, lojas e ações de batalha, sem sobrepor preço/quantidade
nem cortar as últimas letras. As provas binárias não substituem essa revisão.
Não é necessário atingir todos os itens imediatamente.

Mantidas cinco ISOs de trabalho e a alpha separada e protegida. A v053
permanece disponível como pai para comparação enquanto retida. Nenhuma
cópia automática para OneDrive. O desligamento solicitado se aplica somente
ao encerramento desta rodada, sem criar agendamento recorrente.
