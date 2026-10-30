# Nove nomes restantes — geometria dos primeiros painéis

Base atual: interface v053, MAP v044, fonte/layout v005. Esta investigação
não modifica a ISO nem libera os nove nomes. O diagnóstico anterior comparava
larguras com os maiores nomes originais; esta etapa identifica dimensões
solicitadas por dois consumidores concretos do ELF original.

## Resultado do conjunto

| Item | Revisão aprovada ainda pendente | Bytes | Maior avanço, tamanho 22, modos 0/1/2 |
|---|---|---:|---:|
| 354 | Bomba de petróleo | 18 | 187 |
| 373 | Bomba de petróleo | 18 | 187 |
| 431 | Coleira anti-pulga | 18 | 198 |
| 647 | Retalho de casaco | 17 | 187 |
| 711 | Detector avançado | 18 | 187 |
| 798 | Corrente de cauda | 17 | 187 |
| 826 | Bandeira vermelha | 17 | 187 |
| 836 | Projétil explosivo | 19 | 198 |
| 840 | Projétil elétrico | 19 | 187 |

Não são medidas em pixels de uma captura PCSX2. Os avanços vêm do harness
existente que executa o cálculo de métricas com a extensão PT-BR e modela
as suas dependências, sem renderização GPU. A fonte não foi redimensionada.

## Painel com nome desenhado diretamente

Offsets de arquivo ELF, não endereços virtuais:

- 0x1B3580 passa largura 0x110 (272) ao método virtual do retângulo;
  0x1B3588 passa altura 0xD0 (208).
- 0x1B3B54 passa X de desenho +0x26 (38); 0x1B3B58 passa tamanho 22.
- 0x1B3B64 chama o caminho direto de texto VA 0x13D1A8 com o ponteiro
  do registro de item calculado em 0x1B3B14..0x1B3B24.

Se origem e recorte efetivos coincidirem, restam 234 unidades desde o início
do nome. Os nove avanços ficam abaixo desse valor, com margem de pelo menos
36 unidades. A identificação do método virtual, escala, relação entre as
origens e recorte efetivo ainda precisa ser fechada. Não é prova de que todas
as listas do jogo aceitam os nomes nem de que os glifos não têm overhang.

## Painel que formata nome e preço

0x1D54EC solicita largura 400 pelo wrapper VA 0x14FC40. A chamada em
0x1D5508 aplica margens 8/8 pelo setter VA 0x14F040, cujas stores estão
em 0x50040..0x50050. A largura interna condicional é 384.

O construtor usa tamanho inicial 22 (0x509F0). O nome é encaminhado ao
formatador em 0x1D5544..0x1D5550, com literal em 0x341658. O formato tem
campo `%-20s` para o nome e `%8d` para o preço, além do ícone e moeda.
Todos os nove nomes aprovados têm no máximo 19 bytes e permanecem em um
campo de 20 bytes após o preenchimento. Os acentos são pares do codec do
projeto: bytes de printf e células de glifo não são a mesma medida.

O 20 é largura mínima, não precisão máxima: uma string maior não seria
truncada por esse formato. A ferramenta testa esse caso explicitamente.
Não foi executado o printf integral, o método virtual do retângulo nem o
desenho completo; preço, ícone, moeda e clipping exigem sua própria conferência.

## Impedimentos que continuam separados

Os nove nomes continuam bloqueados para aplicação. Inventário, listas de
lojas e ações de batalha não foram cobertos integralmente pelos dois painéis.
Os itens 354/373 compartilham battle.action.0106. Os itens 836/840 correspondem
às ações 0881/0886; os dois nomes têm 19 bytes e também excedem o teto
conservador de 18 dessas ações. Não liberar esse teto por caber em 32 bytes.

A prova de mensagens da v053 foi construída com máximo de 18 bytes por item.
Um lote que passe a 19 precisa recalcular os orçamentos, além de comprovar
os consumidores relevantes. Não reaproveitar a autorização dos seis nomes
da v053 para estes nove.

## Reproduzir e continuar

```powershell
python tools/item_name_boxes.py --output work/caixas-nomes-v001.json
python -m unittest discover -s tests -p test_item_name_boxes.py -v
```

Execução integralmente local, sem IA, API, internet ou dependência nova de
desmontador. O relatório próprio reports/caixas-nomes-v001.json vincula os
hashes de ELF/S_PACK/receita/revisão humana e as janelas de instruções.
Nenhum arquivo de referência é gravado.

Validação desta rodada: 28 testes distintos passaram, sem falhas, erros ou
ignorados: oito do novo diagnóstico e 20 de regressão da capacidade e da
liberação exata da v053. Incluem fonte alterada, opcode com registrador
incorreto, padding em bytes, string longa sem truncamento e rejeição de
saída sobre arquivos de referência/relatórios versionados. Nenhum teste
equivale à execução visual dos painéis no PCSX2.

Próximo passo concreto: resolver o método virtual e a origem do painel direto;
depois identificar as colunas de inventário/lojas e os consumidores das três
ações relacionadas. Não repetir o censo bruto nem alterar nomes aprovados
para eliminar a fila. A imagem disponível para jogar permanece a v053 em
Iniciar-Teste.cmd; não foi criada uma ISO repetida para esta análise.
