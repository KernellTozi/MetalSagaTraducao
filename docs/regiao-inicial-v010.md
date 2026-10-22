# Região inicial — lote ampliado v010

## Cobertura e preservação

O intervalo `0x1DF47F0C..0x1DF86FD4` contém 977 registros: 829 traduzidos e
148 preservados, incluindo dezenove bloqueados. São 877 segmentos traduzidos
em 174 grupos SSD. O teste compara integralmente os 777 registros da v009:
nenhum alvo ou metadado anterior foi alterado.

| Lote | Registros | Traduzidos | Segmentos traduzidos |
| --- | ---: | ---: | ---: |
| v009 | 777 | 666 | 706 |
| v010 | 977 | 829 | 877 |

São 200 ocorrências adicionais, com 177 alvos únicos revisados, vinte aliases
baseados na identidade de todos os segmentos originais e três novos bloqueios.
O acréscimo efetivo é de 163 registros traduzidos. Títulos de lugares, pausas e
outras ocorrências sem alteração não são contados como novas traduções.
O nome histórico do lote não significa cobertura integral da região inicial.

## Contexto e tom

As falas foram lidas por sequência textual, considerando variantes de eventos.
Identidades sem rótulo explícito são inferidas da conversa, sem mapeamento
automático comprovado de retratos.

| Trecho aproximado | Revisão contextual |
| --- | --- |
| `0x1DF7AEE8..0x1DF7C15C` | Transportador, viajante e entusiasta de armas; informalidade, exageros e brincadeiras preservados |
| `0x1DF7C44C..0x1DF7EBCC` | Desafios de Rosa, revanche e alternativas após vitória/derrota; formalidade de Sebastian separada da provocação de Rosa |
| `0x1DF7F16C..0x1DF7FF34` | Conversa de Eddy e Rosa sobre tanques; modelos IS-3, 74 e KV-2, torque e potência para os canhões preservados |
| `0x1DF8021C..0x1DF817E8` | Bar e encontros com companheiros; humor nas rodadas de bebida e preocupação familiar sem misturar os tons |
| `0x1DF81A74..0x1DF83220` | História do mundo e Doc Solomon; orgulho e humor do pesquisador, instruções práticas mantidas |
| `0x1DF8330C..0x1DF83ED4` | Aprendiz, livros, Laura e conversa pessoal; hesitações e insinuações sem explicações acrescentadas |
| `0x1DF85114..0x1DF86FD4` | Títulos de lugares intactos, despedida robótica e outras alternativas do desafio; registro formal e pausas preservados na despedida |

As orientações de Doc Solomon mantêm 440 libras no supino, marcos de
30/60/90 por cento e os locais das recompensas: direita da pia, esquerda da pia,
barril, debaixo da mesa e atrás da geladeira. A despedida mantém a referência
a 62 segundos. Há testes explícitos para esses detalhes. Não se trata de uma
auditoria semântica automática de todas as frases; a revisão humana continua
necessária, inclusive para conferir a atribuição dos falantes.

Nomes de veículos, cidades e personagens foram acrescentados à política local.
Os títulos de local do novo intervalo permanecem idênticos ao original. Itens,
inimigos e tabelas de equipamentos não foram traduzidos nesta entrega.

## Bloqueios e verificação

`map.msg.1df7ec14`, `map.msg.1df7ed3c` e `map.msg.1df7ee6c` contêm bytes nativos
cuja edição não está liberada; os três registros ficam inteiros. Os dezesseis
bloqueios anteriores também permanecem. Não houve relaxamento do codec,
controle de páginas, slots, cabeçalhos ou parsers.

96 testes passaram após os ajustes finais. O teste novo verifica prefixo,
bloqueios, segmentos protegidos, títulos de lugares e detalhes práticos.
As recusas intermediárias foram corrigidas reformulando os alvos. A compilação
final não tem recusas ou violações terminológicas.

A construção verificou hashes, leitura de retorno, limites SSD, diretórios e
diferenças integrais da ISO. Todos os registros alterados usam slots existentes,
sem realocação. O relatório conserva 117 avisos de largura no lote completo.
São estimativas conservadoras, sem medição de pixels ou aprovação visual.
Não houve execução desta versão no PCSX2. O perfil de tipografia continua sob
a premissa provisória autorizada pelo usuário.

## Uso local

- `Preparar-Regiao-Inicial.cmd`: compila e valida a v010, sem outra ISO.
- `Testar-Regiao-Inicial.cmd` ou `Iniciar-Teste.cmd`: abre a ISO atual.
- ISO: `work/regiao-inicial-v010/MetalSaga-ptbr-regiao-inicial-v010.iso`.
- Plano, revisão bilíngue e relatório: `work/regiao-inicial-v010/`.
- Metadados publicáveis: `reports/regiao-inicial-v010-validation.json`.

```powershell
python tools/build_translation_pilot.py --output work/reconstrucao-v010 --build-iso
python -m unittest discover -s tests
```

SHA-256 da ISO: `7b9f25e4e697868d8e502a2dba50012b791784a3da00b04465c9fb23e4a49c4c`.

No próximo teste manual, priorizar uma conversa de duelo/revanche e as
instruções de Doc Solomon. Observar tom, identificação de falante, largura,
acentos, passagem de páginas, nomes dinâmicos e opções. Não é necessário atingir
todos os eventos em uma sessão.

A retenção removeu a ISO antiga v003 para manter dez imagens de trabalho.
Receita e relatórios continuam preservados; o atalho histórico `--iso region-v003`
exige reconstrução. A v009 permanece disponível. ISO original, BIOS, saves e
configurações não foram modificados.
