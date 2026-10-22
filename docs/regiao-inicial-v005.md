# Região inicial — lote consolidado v005

O intervalo `0x1DF47F0C..0x1DF630B8` passa de 326 para 385 registros.
São 343 registros traduzidos, 42 preservados (incluindo os mesmos dez bloqueios),
370 segmentos traduzidos e 76 agrupamentos SSD. Nenhum dos 326 registros do
plano anterior foi alterado; o teste compara todos os seus metadados e alvos.

Os 59 registros acrescentados cobrem variantes de fechaduras e diálogos da
clínica, com Dr. Mortem, Igor e reações após eventos. Há 30 alvos únicos
revisados e 29 ocorrências reutilizadas por identidade de todos os segmentos
originais, incluindo rótulos protegidos. Isso não comprova equivalência de
personagem/cena automaticamente: a revisão do contexto continua necessária.
Mantivemos nomes, risadas, fala telegráfica de Igor e controles do motor.

Todos os textos cabem nos slots existentes. Cinco recusas iniciais (quatro
excessos de bytes e uma quebra extra) foram corrigidas nos alvos; as verificações
não foram relaxadas. A leitura de retorno, hashes, limites SSD e comparação
integral da ISO são executados pelo construtor. Avisos conservadores de largura
continuam no relatório; não substituem teste visual.

## Execução

- `Preparar-Regiao-Inicial.cmd`: compila o lote atual localmente, sem nova ISO.
- `Testar-Regiao-Inicial.cmd`: abre a ISO v005 no ambiente isolado já preparado.
- ISO: `work/regiao-inicial-v005/MetalSaga-ptbr-regiao-inicial-v005.iso`.
- Plano, revisão bilíngue e relatório completo: `work/regiao-inicial-v005/`.
- Metadados publicáveis: `reports/regiao-inicial-v005-validation.json`.

Para reconstruir em uma pasta nova:

```powershell
python tools/build_translation_pilot.py --output work/reconstrucao-v005 --build-iso
python -m unittest discover -s tests
```

Não houve novo teste de execução no PCSX2 nesta entrega. No próximo teste,
observar as alternativas de arrombamento, a apresentação da clínica, as falas
de Igor e os retornos após eventos: nomes dinâmicos, acentos, largura, páginas
e opções devem permanecer legíveis e funcionais. Os estados dependem do avanço
do jogo; não é preciso alcançar todos em uma sessão. O perfil tipográfico segue
a premissa autorizada pelo usuário, sem nova confirmação visual.

## Preparação reutilizável de lotes

Nova ferramenta local, sem IA, rede ou APIs:

```powershell
python tools/prepare_translation_lot.py --parent translations/regiao-inicial-v005.json --end-offset HEXADECIMAL --lot-id proximo-lote --output work/preparacao-proximo-lote
```

Substituir `HEXADECIMAL` pelo limite investigado. A ferramenta exige que o lote
pai compile, conserva IDs, separa bloqueios e propõe aliases apenas para fontes
binárias idênticas. Exporta contexto original somente em `work/`, copia os
rascunhos herdados e cria alvos vazios para revisão. Alvos vazios são recusados
explicitamente pelo compilador. Não traduz, não cria ISO e não libera formatos.

A preparação exploratória até `0x1DF6F6C8` também foi preservada localmente em
`work/preparacao-v005/`: 192 alvos únicos e quatro novos bloqueios seriam
necessários para chegar a 577 registros. Esse recorte maior não integra a ISO
entregue; inclui cenas adicionais e permanece pendente de tradução contextual.
