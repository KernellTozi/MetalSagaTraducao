# Região inicial — lote consolidado v004

## Cobertura e preservação

O lote acrescenta 133 registros ao recorte anterior. São 326 ocorrências no total:
288 traduzidas e 38 preservadas, incluindo dez adiadas por bloqueios conhecidos.
Há 306 segmentos traduzidos em 62 agrupamentos SSD. A contagem não identifica
automaticamente personagens ou rotas, nem comprova tradução integral da cidade.

| Versão do lote | Registros | Traduzidos | Preservados | Segmentos traduzidos |
| --- | ---: | ---: | ---: | ---: |
| v003 | 193 | 165 | 28 | 177 |
| v004 | 326 | 288 | 38 | 306 |

Os 193 registros anteriores permanecem idênticos no plano compilado, verificado
por teste. O novo intervalo termina em `0x1DF5FF98` e começa, como antes, em
`0x1DF47F0C`. Todos os registros modificados usam slots; não há repack ou mudança
de tamanho, mesmo em mensagens longas.

## Contexto acrescentado

Inclui desfechos e reações do conflito de Jack, recompensas, o episódio de Biff e
Montoya no laboratório, história da cidade, Stan e Emily, reações familiares ao
braço mecânico, retornos após eventos, explicação da garagem e interações com
portas do bar. São estados e alternativas distintos; não ocorrerão necessariamente
na mesma sequência ou sessão de jogo.

Nomes, profissões protegidas e expressões seguem o glossário. `Junkyard` permanece
em inglês, inclusive no título de local. `Junk Mountain`, uma descrição geográfica
genérica, é tratada como `Montanha de Sucata`. `Great Destruction` recebe a forma
de trabalho `Grande Destruição`. Inventários e tabelas de equipamentos, tanques,
inimigos e procurados não foram editados.

O erro de Biff ao chamar Dr. Mortem de `Dr. Martin` foi preservado; corrigir esse
nome destruiria a intenção da resposta seguinte. O texto de Igor mantém uma fala
mais simples e telegráfica. Stan conserva hesitações, nomes e expressões de riso.
Os alvos são rascunhos contextuais, não revisão literária ou visual final.

## Bloqueios e reutilização

A v004 mantém os sete bloqueios anteriores e acrescenta:

| Registro | Motivo |
| --- | --- |
| `map.msg.1df5e3bc` | Nome de item com controle opaco `%I$0` |
| `map.msg.1df5e4a4` | Nome de item com controle opaco `%I$0` |
| `map.msg.1df5f13c` | Nome de item com controle opaco `%I$0` |

Esses registros não têm qualquer byte alterado. São mensagens sobre presentes,
cujo nome é inserido pelo jogo. Não substituir o controle por texto fixo nem
remover o nome para liberar uma tradução.

Ocorrências idênticas de despedidas, aposentadoria e fechaduras reutilizam a
tradução por alias, após comparar os segmentos de origem. IDs, offsets e
cabeçalhos continuam independentes. O carregador agora rejeita chaves duplicadas
no mesmo JSON, impedindo que uma edição sobrescreva silenciosamente outra.
Sobreposições explícitas entre versões herdadas continuam permitidas.

## Execução local

`translations/regiao-inicial-v004.json` herda a v003. O rascunho expandido,
incluindo todo o conteúdo anterior, é exportado em uma única cópia `rascunho.json`.
As fontes continuam sendo o perfil v002 com espaçamento v003 assumido correto
pelo usuário. A numeração v004 deste lote não altera a política da reinserção
transacional histórica v004.

- `Preparar-Regiao-Inicial.cmd`: recompila e valida o lote, sem criar outra ISO.
- `Iniciar-Teste.cmd`, `Testar-Regiao-Inicial.cmd` e `Testar-Piloto-Inicial.cmd`:
  abrem a ISO consolidada atual.
- `Iniciar-Teste.cmd region-v003`: abre a versão anterior, se ainda armazenada.

```
python tools/build_translation_pilot.py --output work/minha-revisao-v004
python tools/build_translation_pilot.py --output work/minha-construcao-v004 --build-iso
python -m unittest discover -s tests
```

Usar uma pasta de saída nova. Para reproduzir lotes históricos, especificar
`--draft translations/regiao-inicial-v003.json` ou outro arquivo autoral da versão.
Não há chamadas de IA, API ou internet na compilação e verificação local.

## Verificação e limites

Os 87 testes passaram, incluindo preservação do prefixo anterior, nomes, rótulos,
traduções reutilizadas, chaves duplicadas, controles e slots. A ISO foi comparada
integralmente à original: apenas registros previstos do MAP, 36 células GFI e a
janela de 128 bytes do ELF mudam. São 29.461 bytes diferentes. Tamanho, diretórios,
LBAs e demais bytes permanecem idênticos à referência.

Foram mantidos 29 avisos conservadores de largura. A fórmula legada conta acentos
como duas unidades; o perfil de espaçamento modifica o avanço de glifo. Esses
avisos não são comprovação de cortes, mas continuam pendentes de avaliação visual.
Não houve nova execução ou navegação automática no PCSX2.

ISO atual: `work/regiao-inicial-v004/MetalSaga-ptbr-regiao-inicial-v004.iso`.
Relatório próprio: `reports/regiao-inicial-v004-validation.json`.

## Correção no isolamento dos testes de retenção

Uma inicialização de ISO fictícia dos testes contou seu arquivo temporário junto
das ISOs reais e antecipou a remoção de
`work/MetalSaga-ptbr-dialogo-inicial-v001.iso`, o experimento elegível mais antigo.
A fonte original e recursos pessoais não foram alterados. O plano e o relatório
daquela ISO continuam preservados; o incidente está em
`reports/iso-retention-test-isolation.json`.

Os testes de inicialização agora substituem a retenção real por uma simulação.
Os testes próprios de retenção continuam usando somente uma raiz temporária
isolada. A inicialização também valida prefixos parciais antes de invocar a
retenção, para não remover imagens ao recusar uma cópia inválida.

A suíte completa foi repetida: os caminhos, tamanhos e mtimes das ISOs de produção
ficaram iguais antes e depois. Os oito testes específicos de inicialização também
passaram após a proteção adicional do prefixo. O total final é nove ISOs de
trabalho, abaixo do limite de dez.

Se houver necessidade de reconstruir o primeiro experimento removido, seus bytes
podem ser produzidos a partir da referência e do plano preservado, usando um
relatório de saída novo:

```
python tools/build_dialogue_iso.py --plan work/dialogue-inicial-v001.json --output work/MetalSaga-ptbr-dialogo-inicial-v001.iso --report work/reconstrucao-dialogo-inicial.json
```

Essa reconstrução não foi executada nesta entrega para evitar outra ISO redundante.
