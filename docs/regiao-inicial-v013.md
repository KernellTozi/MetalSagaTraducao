# Lote consolidado v013 — ampliação por offsets anteriores

## Cobertura

O intervalo conhecido agora é `0x1D0B5680..0x1FF30844`. Foram incluídas 200
ocorrências anteriores ao início da v012: 139 alvos únicos revisados, 48 aliases
por identidade de todos os segmentos originais e treze novos bloqueios.

| Lote | Registros | Traduzidos | Segmentos traduzidos |
| --- | ---: | ---: | ---: |
| v012 | 1.363 | 1.083 | 1.140 |
| v013 | 1.563 | 1.241 | 1.303 |

O acréscimo efetivo é de 158 registros traduzidos. Os 322 preservados incluem
oitenta adiamentos. Pausas, nomes, títulos de lugares e outras ocorrências sem
alteração não são contados como traduções novas.

Os 1.363 registros anteriores permanecem integralmente iguais no plano,
incluindo metadados, controles e a exceção `nao`. Como os novos offsets são
menores, o recorte anterior aparece depois dos duzentos registros acrescentados
na lista ordenada. Não houve deslocamento físico de nenhum recurso do jogo.

O nome histórico do lote não significa tradução completa de uma cidade ou
região. Continuam existindo outros registros anteriores ao novo limite inicial
e casos ainda sem edição liberada.

## Contexto e tom

| Trecho aproximado | Conteúdo e decisões |
| --- | --- |
| `0x1D0B5680..0x1D0B832C` | Serviços e famílias em Newfolk, comentários sobre o Exército Blueberry e intimidação; diferença entre indignação dos moradores e linguagem burocrática dos soldados |
| `0x1D0B98FC..0x1D0BBBC0` | Frog Race, Hunter com informações pagas, rotas, flerte e bebedeira; preservei Dragon Choppers, rumos e referências práticas |
| `0x1D0BC644..0x1D0BF56C` | Oficina, filhos do mecânico, soldados e repetições de história/despedida; reaproveitamento revisado por contexto |
| `0x1DC5E184..0x1DC5FB98` | Variantes de casamento, conversa entre pais, cerimônia irreverente e narrador satírico; Spiffy Tube e troca de munição em 10 minutos preservados |
| `0x1DF07A5C..0x1DF47BBC` | Reação de Tank Eater, ferimentos, bar e serviços de Junkyard; Big Medals, Gigantic Medals e Ghost Tank mantidos como nomes |

As falas foram lidas em sequência com alternativas e repetições. Falantes sem
rótulo são inferidos do diálogo, não identificados automaticamente por retrato.
Não transformar variantes de finais em uma única história contínua.

No casamento, o afeto dos pais é separado da pressa cômica do celebrante e da
ironia da franquia que prospera e depois quebra. Não foram acrescentados filhos
ou outros eventos. Na conversa sobre Nina, preservar o constrangimento do rapaz
sem ampliar a intensidade do comentário original. A referência cultural
`livin' la vida loca` permanece.

Frog Race, Dragon Choppers, Spiffy Tube, Big Medals, Gigantic Medals e Blueberry
foram acrescentados à política. Blueberry Army recebe Exército Blueberry.
Itens, inimigos e tabelas de equipamentos não foram traduzidos em massa.

## Ferramenta local

`prepare_translation_lot.py` agora permite ampliar o início ou o fim do intervalo,
por `--start-offset` ou `--end-offset`, respectivamente. É obrigatório escolher
exatamente um deles. Limites que reduzam o intervalo ou início negativo são
recusados. O comando antigo com `--end-offset` continua disponível.

Exemplo para reproduzir a preparação desta rodada em outra pasta:

```powershell
python tools/prepare_translation_lot.py --parent translations/regiao-inicial-v012.json --start-offset 1d0b5680 --lot-id regiao-inicial-v013 --output work/preparacao-v013-repro
```

O preparador não traduz nem cria ISO. Exporta contexto original somente em
`work/`, conserva os adiamentos e exclui a exceção ASCII da fonte de aliases.
Os alvos novos ficam vazios até revisão, bloqueando a compilação de rascunho
incompleto. A ampliação modifica somente o catálogo e o escopo da receita.

## Validação e bloqueios

106 testes passaram. O teste novo compara integralmente todos os registros da
v012, verifica as contagens da preparação pelo início, nomes e detalhe dos
10 minutos. Outro teste recusa limites ambíguos ou que encolham o recorte.
As recusas intermediárias foram corrigidas nos alvos, sem relaxar verificações.
A compilação final não teve recusas ou violações terminológicas.

Dos treze novos bloqueios, seis têm controles opacos, seis têm terceira string
sem edição liberada e um reúne as duas condições. Todos permanecem intactos,
assim como os 67 adiamentos da v012. Não houve ampliação de slots ou registros.

A construção verificou hashes, leitura de retorno, limites SSD, diretórios e
diferenças integrais da ISO. Todos os registros alterados usam slots existentes,
sem realocação. O relatório conserva 181 avisos conservadores de largura no lote
completo. Não são medições em pixels nem aprovação visual.

Não houve execução desta versão no PCSX2. No teste manual, observar uma conversa
de Newfolk e uma amostra dos serviços ou casamento: identificação de falante,
tom, largura, acentos, páginas, opções e nomes dinâmicos. Não é necessário
alcançar todos os eventos em uma sessão.

## Uso local

- `Preparar-Regiao-Inicial.cmd`: compila e valida a v013 sem outra ISO.
- `Testar-Regiao-Inicial.cmd` ou `Iniciar-Teste.cmd`: abre a ISO atual.
- ISO: `work/regiao-inicial-v013/MetalSaga-ptbr-regiao-inicial-v013.iso`.
- Plano, revisão bilíngue e relatório: `work/regiao-inicial-v013/`.
- Metadados publicáveis: `reports/regiao-inicial-v013-validation.json`.

```powershell
python tools/build_translation_pilot.py --output work/reconstrucao-v013 --build-iso
python -m unittest discover -s tests
```

SHA-256: `7b71b9d56fda75639d54ea5b2e60d0486a8dcc860c3394ea524f9146b71a5f3b`.

A retenção removeu a ISO antiga v006 para manter dez imagens de trabalho.
Receita e relatórios estão preservados; `--iso region-v006` exige reconstrução.
A v012 continua disponível. ISO original, BIOS, saves e configurações não foram
alterados.
