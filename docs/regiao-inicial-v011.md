# Lote consolidado v011

## Cobertura

O intervalo de estruturas conhecidas `0x1DF47F0C..0x1F3288B4` passa de 977 para
1.177 registros. São 990 traduzidos e 187 preservados, incluindo 25 adiados.
Há 1.044 segmentos traduzidos em 227 grupos SSD. O teste compara integralmente
os 977 registros da v010, sem alteração dos alvos ou metadados anteriores.

| Lote | Registros | Traduzidos | Segmentos traduzidos |
| --- | ---: | ---: | ---: |
| v010 | 977 | 829 | 877 |
| v011 | 1.177 | 990 | 1.044 |

O acréscimo de 200 ocorrências contém 158 alvos únicos preparados, 37 aliases
por identidade de todos os segmentos originais e cinco bloqueios estruturais.
Um dos alvos preparados foi adiado por capacidade, em vez de receber uma
abreviação artificial. O acréscimo efetivo é de 161 registros traduzidos.

O nome histórico do lote não indica cobertura integral da cidade inicial.
Há grandes intervalos entre alguns grupos SSD; a enumeração considera as
estruturas reconhecidas pelo índice, sem afirmar que todos os bytes ou textos
entre os offsets foram traduzidos.

## Revisão contextual

| Trecho aproximado | Conteúdo e decisões |
| --- | --- |
| `0x1DF87058..0x1DF88B14` | Preparação e variantes do desafio de Rosa; distinguir veículo próprio de alugado e vitória de derrota |
| `0x1DF8919C..0x1DF8B608` | Roupas, locadora, caminho para Newfolk e casamento; hesitações, proposta sincera, brincadeira e retorno após salvar mantidos distintos |
| `0x1DF8B814..0x1DF8C900` | Humor familiar, oficina e pesquisador cheio de gaguejos; a opinião preconceituosa pertence ao personagem, sem virar afirmação do narrador |
| `0x1DF8CD4C..0x1DF8E1EC` | Ressurreição, resgate, reencontro com cães e comentário sobre Doc Solomon; ironia do doutor separada do alívio da família |
| `0x1F28704C..0x1F288220` | Resultados e revanches dos duelos; estado da disputa preservado |
| `0x1F326A0C..0x1F3288B4` | Veículo, humor ao examinar sucata e exploração; comando Drive, menu HELP, nome Trash Heap e aviso de nível 3 preservados |

As atribuições de fala sem rótulo são inferidas da conversa, não identificadas
automaticamente por retratos. As respostas alternativas e repetições foram
revisadas junto das falas próximas. Latidos, nomes dinâmicos dos cães, risadas
e marcações entre asteriscos permanecem. A sequência para Newfolk mantém
noroeste, contorno das montanhas, nordeste, ponte e leste.

Rent-a-Tank, Trash Heap, Ziggurat e Alex foram acrescentados à política.
`transport pod` como equipamento genérico foi traduzido como cápsula de
transporte. Sua remoção da lista global de nomes protegidos não altera o título
`- Transport Pod -` preservado na v010, nem qualquer registro anterior.

## Bloqueios e ferramenta

Permanecem íntegros os dezenove adiados da v010 e os seguintes novos casos:

| Registro | Motivo |
| --- | --- |
| `map.msg.1df88cd4` | Bytes nativos sem edição liberada |
| `map.msg.1df88d9c` | Bytes nativos sem edição liberada |
| `map.msg.1df88e6c` | Bytes nativos sem edição liberada |
| `map.msg.1f288494` | Controle opaco |
| `map.msg.1f288584` | Controle opaco |
| `map.msg.1df8bec0` | Resposta negativa com capacidade de apenas três bytes |

No último caso, o original `No.` tem três bytes. `Não` ocupa quatro no codec
atual, antes de acrescentar pontuação. O registro inteiro continua no original.
Não remover o til, inventar abreviação ou mudar o sentido para aumentar a conta
de traduções. Ampliar esse tipo de slot exige investigação separada.

`prepare_translation_lot.py` agora exclui também adiamentos manuais da fonte
de aliases. Antes, a filtragem considerava apenas `blocked_reasons` estruturais;
um adiamento por capacidade poderia virar referência sem alvo num lote futuro.
Um teste sintético reproduz esse caso e exige um alvo novo pendente, sem alias.

## Verificação

99 testes passaram. Incluem comparação do prefixo, bloqueios, capacidade da
resposta negativa, referências Drive/HELP, nome Trash Heap, nível 3 e exclusão
de adiamentos manuais na preparação. As recusas intermediárias foram corrigidas
nos alvos. A compilação final não teve recusas ou violações terminológicas.

A construção verificou hashes, leitura de retorno, limites SSD, diretórios e
diferenças integrais da ISO. Todos os registros alterados usam slots existentes,
sem realocação. O relatório conserva 138 avisos conservadores de largura no
lote completo; isso não é medição de pixels ou aprovação visual.

Não foi executado teste desta versão no PCSX2. A tipografia continua sob a
premissa provisória autorizada pelo usuário. No teste manual, observar uma
variante de desafio ou casamento e uma amostra da exploração: tom, falante,
acentos, largura, páginas, opções e nomes dinâmicos.

## Uso local

- `Preparar-Regiao-Inicial.cmd`: compila e valida sem nova ISO.
- `Testar-Regiao-Inicial.cmd` ou `Iniciar-Teste.cmd`: abre a v011.
- ISO: `work/regiao-inicial-v011/MetalSaga-ptbr-regiao-inicial-v011.iso`.
- Plano, revisão bilíngue e relatório: `work/regiao-inicial-v011/`.
- Metadados publicáveis: `reports/regiao-inicial-v011-validation.json`.

```powershell
python tools/build_translation_pilot.py --output work/reconstrucao-v011 --build-iso
python -m unittest discover -s tests
```

SHA-256: `a252c02de6df245a312475ee92244deedf0894355785da7f4284f83703b74d05`.

A retenção removeu a ISO antiga v004 para manter dez imagens de trabalho.
Receita e relatórios estão preservados; `--iso region-v004` exige reconstrução.
A v010 continua disponível. ISO original, BIOS, saves e configurações não foram
modificados.
