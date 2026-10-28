# MAP v041 / interface v048 — oito avisos nativos

Rodada de 28/10/2026. As oito ocorrências antes adiadas receberam **Erro.**,
sem alterar outras traduções. O painel japonês do minigame de cães permanece
original por decisão expressa do usuário e deixa de ser dívida de tradução.

## O que foi identificado

Não são oito falas japonesas diferentes: há um corpo binário repetido oito
vezes, com cinco fingerprints distintos de registro por diferenças no
cabeçalho. Cada ocorrência é `msg`, tamanho 44 bytes, cabeçalho de 32 e corpo
de oito bytes seguido de quatro zeros. Capacidade física: 11 bytes mais NUL.
O corpo é `82 CE 82 AE 81 5B 81 42`, decodificado para leitura como `ばぐー。`.
Essa leitura não transforma CP932 no codec de reinserção do projeto.

| Ocorrência | Contexto estrutural original |
| --- | --- |
| `040EF0EC` | Após batalha e duas condições; seguida por exit |
| `1033E304` | Após batalha e condição; seguida por cmvw e exit |
| `1DF7EC14` | Último comando, após mark; caminho anterior termina em exit |
| `1DF7ED3C` | Último comando, após mark; caminho anterior contém scjp |
| `1DF7EE6C` | Último comando, após mark; caminho anterior contém scjp |
| `1DF88CD4` | Último comando, após mark; caminho anterior termina em exit |
| `1DF88D9C` | Último comando, após mark; caminho anterior contém scjp |
| `1DF88E6C` | Último comando, após mark; caminho anterior contém scjp |

Os oito blocos SSD foram enquadrados pelo parser existente. A análise local
inclui comandos, marcadores, registros vizinhos e fingerprints integrais dos
blocos. O contexto detalhado, com textos originais, fica somente em
`work/native-eight-v001/contexto.json`.

A leitura como aviso técnico de erro é uma **inferência contextual**: repetição,
posição após testes de batalha e marcadores finais, somada à forma da palavra.
Como referência lexical geral, a [IPA japonesa](https://www.ipa.go.jp/archive/publish/qv6pgp00000010b6-att/000027629.pdf)
descreve バグ como erro/defeito de programa. Essa referência não documenta Metal
Saga nem prova sozinha o sentido da grafia alongada em hiragana encontrada aqui.
Não há comprovação de que os oito caminhos sejam inalcançáveis. Por isso as
mensagens foram traduzidas, **sem removê-las ou mudar o fluxo dos scripts**.

## Evidências executadas e limitações

`tools/dialogue_native_eight.py` reaproveita o índice SSD e valida cada origem
por ID, endereço, hash integral, tamanho, corpo e padding exatos.

- 41 casos do lookup/setter original de marcadores, com listas derivadas dos
  blocos e casos de marcador ausente. Janelas `0x1BDD94–0x1BDDE4` e
  `0x1BDDF0–0x1BDDF8`, somente RAM sintética.
- Três casos da parte do `if` posterior à comparação, em
  `0x1C54C0–0x1C54EC`: condição falsa, busca sem resultado e busca com resultado.
  A comparação e o retorno do lookup são fornecidos nesse recorte; o lookup
  original é testado separadamente. Os retornos observados são 2, 2 e 3.
- Vínculo da rotina de `if` pela tabela virtual em `0x30B4F4` e conferência do
  caminho de `exit` em `0x1CCF80`, que retorna 8.
- Os quatro pares nativos possuem glifos nas duas GFI originais, fora do banco
  reservado aos acentos PT-BR. Os cinco caracteres ASCII do destino já existem.

Isso não executa a VM completa, o dispatch integral, as comparações originais,
os resultados de batalhas, as transições entre scripts ou o PCSX2. Não atribui
nome canônico a personagem/cena nem prova ausência de outros caminhos de entrada.
Nenhuma instrução do ELF ou dos comandos SSD foi alterada.

## Edição restrita e preservação

Política opt-in: `eight-source-bound-native-fallbacks-ascii-slots-v001`.
Manifesto `translations/dialogos-nativos-oito-v001.json`; receita MAP
`translations/regiao-inicial-v041.json`; interface
`translations/interface-v048.json`.

A receita filha retoma explicitamente os oito IDs, vinculando o pai MAP v040
e a interface v047 por hash. O compilador primeiro reproduz integralmente o
pai com as políticas históricas e depois aplica uma camada separada, limitada
a esses oito registros e à tradução exata `Erro.`. Se uma verificação falhar,
nenhum conjunto de patches é retornado para a construção.

O destino usa **45 72 72 6F 2E**, cinco bytes ASCII, mais sete zeros dentro dos
mesmos 12 bytes finais. O teto conservador é oito bytes, igual ao corpo de
origem, embora o slot tenha 11. Cabeçalho, índice, parâmetros, endereços,
tamanho, terminadores válidos, marcas e condições permanecem preservados.

A entrada nativa genérica continua bloqueada. Os seis IDs aprovados na v033
não foram ampliados, e o reinseridor legado continua recusando esses oito sem
a camada explícita. Os metadados de bloqueio histórico da extração permanecem
nos registros; a autorização específica fica no wrapper compilado
`compiled_native_fallback_overlay`. Não promover esses metadados para uma
liberação geral nem editar registros semelhantes apenas porque repetem o corpo.

## Resultado e verificação

- MAP: **6.032 registros alterados**, oito a mais; 5.991 com corpo/opções
  alterados e 912 referências de falantes traduzidas, com sobreposição entre
  essas categorias. Não somar as duas últimas contagens.
- **Zero ocorrências nativas pendentes** no catálogo conhecido. Os 19
  adiamentos restantes são os nomes de tanques N$3 já destinados à preservação.
- Interface mantém 3.848 unidades, 541 nomes de itens e todos os gráficos v047.
- A revisão automática de nomes e o auditor de pendências continuam locais;
  os 49 rótulos sem espaço e as 16 revisões de itens não mudaram nesta rodada.

Testes incluem rejeição por mutação de origem/destino, atomicidade do lote,
comparação de todos os outros registros/patches com o pai, round-trip pelos
parsers existentes, casos originais de marcadores/if e auditoria de pendências.
**149 testes passaram**, incluindo os 12 novos e os quatro testes legados
específicos de texto nativo. A comparação integral v047 → v048 confirmou
**64 bytes diferentes em oito registros MAP**, todos previstos; nenhum byte
da interface, fontes, ELF ou gráficos mudou. O relatório da entrega está em
`reports/interface-v048.json`, com delta em `reports/interface-v048-delta.json`.
**Validação visual dessas ocorrências permanece pendente; nenhum PCSX2 foi
executado.** Não é necessário provocar um estado de erro ou jogar até cada
ocorrência para continuar o projeto.

## Uso local

`Iniciar-Teste.cmd` abre `work/interface-v048/MetalSaga-ptbr-interface-v048.iso`.
Tamanho: 1.704.427.520 bytes. SHA-256 integral:
`b8ac33b1e2a8d5bf408903fcbb36e65ee6e1dcd6e33df2808f7a82d22ce944c5`.
`Preparar-Interface.cmd` valida a receita v048/MAP v041 sem gerar outra ISO.
`Auditar-Traducao.cmd` foi atualizado: seu destino é
`work/dialogos-pendencias-atual.json`, sem depender do build antigo v038.

Para reproduzir a construção, usar uma pasta nova:

```powershell
python tools/build_translation_pilot.py --draft translations/regiao-inicial-v041.json --interface-draft translations/interface-v048.json --compact-output --build-iso --output work/minha-v048
python -m unittest discover -s tests -p test_native_eight.py
```

A extração, compilação, auditoria e os testes binários funcionam offline,
sem IA ou APIs. A consulta lexical acima foi pesquisa pontual, não dependência
de execução. Originais imutáveis; cinco ISOs de trabalho e alpha independente.
Sem OneDrive ou desligamento solicitado nesta rodada.

## Painel japonês excluído

A decisão do usuário está em `reports/interface-lacunas-v003.json`: a imagem
`RMGDOG.0.000` fica preservada. As contagens históricas v001/v002 não foram
reescritas. Dos 20 atlas candidatos, nove estão cobertos e onze preservados
por decisão do usuário. Isso não comprova cobertura de toda a interface nem
de todo o jogo. Três recursos especiais continuam sem prova de conter textos.
O auditor também mantém 129 sinais de revisão editorial, 456 candidatos a
nomes/expressões e 595 registros de controles/pontuação como triagem. Esses
grupos não são traduções pendentes confirmadas nem podem ser promovidos
automaticamente. A eliminação dos oito adiamentos nativos não encerra a revisão
de qualidade durante a partida.
