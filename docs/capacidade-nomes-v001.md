# Capacidade dos nomes aprovados — investigação v001

Base de análise: interface v050, sobre MAP v043 e fontes/layout v005.
As 16 revisões humanas continuam bloqueadas: esta rodada não aplicou nomes,
não ampliou políticas e não gerou ISO. O avanço foi separar os impedimentos
e produzir uma investigação local reproduzível com testes de instruções.

## Resultado por nome

| ID | Redação aprovada ainda não aplicada | Bytes | Referência de largura |
| --- | --- | ---: | --- |
| 331 | Pílula Açucarada | 18 | Dentro nos seis perfis |
| 354 | Bomba de petróleo | 18 | Acima em algum perfil |
| 372 | Frasco do pânico | 17 | Dentro nos seis perfis |
| 373 | Bomba de petróleo | 18 | Acima em algum perfil |
| 431 | Coleira anti-pulga | 18 | Acima em algum perfil |
| 459 | Estátua de barro | 17 | Dentro nos seis perfis |
| 460 | Ídolo de barro | — | Í não está no codec atual |
| 647 | Retalho de casaco | 17 | Acima em algum perfil |
| 711 | Detector avançado | 18 | Acima em algum perfil |
| 798 | Corrente de cauda | 17 | Acima em algum perfil |
| 826 | Bandeira vermelha | 17 | Acima em algum perfil |
| 836 | Projétil explosivo | 19 | Acima em algum perfil |
| 838 | Projétil sônico | 17 | Dentro nos seis perfis |
| 840 | Projétil elétrico | 19 | Acima em algum perfil |
| 841 | Projétil de gelo | 17 | Dentro nos seis perfis |
| 849 | Projétil crítico | 18 | Dentro nos seis perfis |

Todos os 15 nomes codificáveis cabem fisicamente no campo de 24 bytes,
com NUL. Isso não libera o teto conservador atual de 16 bytes. A simulação
em cópias de 128 bytes preservou atributos/ponteiros a partir de +24 e
permitiu reconstrução exata do registro anterior, sem tocar em S_PACK.

Seis nomes não ultrapassam a soma máxima de avanços dos nomes originais em
nenhum dos seis perfis examinados; nove ultrapassam em pelo menos um. São
perfis de células 22/26 e modos 0/1/2, usando o harness de métricas existente
do layout v004 que integra v005. Não são seis telas executadas. A soma dos
avanços não comprova caixas reais, bearings, clipping, escala dos chamadores,
quebras de linha ou alinhamento com colunas de preço.

## Leitura e cópia: provas novas e limites

O módulo `tools/item_name_capacity.py` executa os bytes originais de três
recortes escalares, com limites de código e memória, para cada um dos 15 nomes:

- **0x197858..0x197910:** varredura do caminho comum de texto. Os acentos são
  entregues ao desenhador como os mesmos pares do codec do projeto; a última
  letra e o NUL são alcançados. Registradores preservados conferidos.
- **0x3E1F0..0x3E2AC:** outro laço de desenho, usado pelo caminho direto de
  rótulos. Espaços avançam sem desenhar um glifo; os demais caracteres, inclusive
  pares acentuados, são percorridos sem corte fixo em 16 bytes nesses trechos.
- **0x1CD474..0x1CD498:** cópia de expansão de variável. Copia todos os bytes
  até NUL, mas não copia o próprio terminador nesse recorte. A área fornecida
  pelo teste tem 32 bytes e sentinela intacta. **O tamanho real do destino
  não foi comprovado**; não inferir que o jogo fornece esses 32 bytes ali.

O teste modela o conteúdo da tabela de classificação do primeiro laço; não
executa sua inicialização. No segundo, modela o classificador para os bytes
ASCII/0x82 dos alvos e a comparação de escape; não executa esses auxiliares
inteiros. Os desenhadores são substituídos por captura de argumentos, sem GPU.
Essas fronteiras são explícitas, assim como nas sondas anteriores de layout.
O alocador, formatador integral, VM e PCSX2 não foram executados.

O wrapper em **0x1977C8** reserva 0x1000 bytes antes dos registradores salvos
para o temporário de formatação, conforme evidência anterior v021. Há outros
chamadores e buffers que precisam de prova própria. A nova inspeção localizou,
entre eles, os formatos de peso em **0x33DC08** e de nome/preço em **0x341658**;
este último contém campo de largura mínima 20, sem precisão máxima de string.
Não é autorização para todos os nomes nem prova de alinhamento em tela.

## Inventário dos caminhos e batalha

A varredura bruta do ELF encontrou **54 candidatos de lw com imediato 0x5AE8**
e **190 chamadas diretas ao getter de registro em VA 0x16C938**. São raízes
para investigação, não 244 leitores de nomes comprovados. Muitos acessam
atributos; alguns encaminham ponteiros. Os registradores-base dos candidatos,
aliases, chamadas indiretas e fluxos entre funções não foram todos resolvidos.
Zero stores com esse imediato não prova ausência de gravações por outros meios.
Offsets e janelas vinculadas por hash ficam no relatório local detalhado.

Existem **oito rótulos de ação relacionados** aos nomes revisados, determinados
por igualdade da origem na tabela e registrados sem aplicação automática:

| Item | Rótulos relacionados |
| --- | --- |
| 331 | battle.action.0124 |
| 354 e 373 | battle.action.0106 compartilhado |
| 836 | battle.action.0881 |
| 838 | battle.action.0884 |
| 840 | battle.action.0886 |
| 841 | battle.action.0887 |
| 849 | battle.action.0882 e battle.action.0895 |

Uma aplicação futura deve manter a consistência também nessas ações. Projétil
explosivo e Projétil elétrico excedem o teto observado independente de 18 bytes
das ações, apesar do campo físico de 32 bytes. Não liberar essa política por
resolver apenas a tabela de itens. Hunter/Soldier, MAIN/SUB/SE e nomes únicos
continuam preservados.

## Próximo experimento definido

Começar pelos seis nomes dentro da referência de largura, conferindo os
destinos reais da expansão em 0x1CD474 e as cópias/formatações dos menus que
podem exibi-los. Resolver capacidade de buffer separadamente de largura.
Conferir os cinco rótulos de ação associados a esse subconjunto: 0124, 0884,
0887, 0882 e 0895. Só criar perfil opt-in depois de comprovar os caminhos
necessários; não promover pelo resultado positivo dos laços isolados.

Os nove nomes mais largos precisam também de prova do espaço real das telas
ou de adaptação de apresentação. Não reduzir a fonte global, cortar artigos,
remover acentos ou trocar as decisões humanas. O caso Í permanece uma frente
isolada de codec/fontes/métricas e ainda não foi implementado nesta rodada.
Não repetir a varredura bruta como se ela resolvesse as referências: usar os
offsets já produzidos para investigar os consumidores concretos.

## Execução e verificações

Execute **Auditar-Traducao.cmd**. Seu alvo explícito, que ainda estava em v049,
foi corrigido para **v050**; após a auditoria bem-sucedida, roda o diagnóstico
dos itens. Os dois relatórios substituíveis são:

- `work/dialogos-pendencias-atual.json`;
- `work/capacidade-nomes-atual.json`.

Não há novo iniciador. O diagnóstico usa somente Python local, sem IA, APIs,
rede, aplicação de patches ou abertura do emulador. Execução direta:

```powershell
python tools/item_name_capacity.py
python -m unittest discover -s tests -p test_item_name_capacity.py
```

Passaram **46 testes**, incluindo 11 novos e regressões dos limites de nomes,
revisões humanas, tabelas de batalha e lote de nomes pendentes. Conferem laços
originais, pares acentuados, fim das strings, guardas, entradas truncadas,
recusa de fonte divergente e manutenção do bloqueio de todas as 16 propostas
no compilador histórico. O iniciador real foi executado separadamente, com
retorno zero, auditoria vinculada à v050/980 rótulos e diagnóstico dos 16 nomes.

A ISO v050 foi reconferida por SHA-256, tamanho e transações, permanecendo
`cc5932c63c5497b69c9e14396aef1ce917584e7c3359e8bcdeae3e5fec22c080`.
Sem execução no PCSX2, nova ISO, OneDrive ou desligamento. O resumo técnico
está em `reports/capacidade-nomes-v001.json`; origens completas e diagnósticos
detalhados permanecem em work/. Esta investigação não aumenta a contagem
de traduções aplicadas.
