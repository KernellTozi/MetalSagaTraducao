# Região inicial — lote consolidado v002

**Histórico:** a versão atual é descrita em `docs/regiao-inicial-v003.md`.
Os iniciadores simples apontam para a v003; para reproduzir este lote, informar
`--draft translations/regiao-inicial-v002.json` ao compilador.

## Resultado

O lote cresce de 26 para 98 registros: 85 traduzidos, sete mantidos porque são
pausas/expressões já adequadas e seis adiados por bloqueios estruturais. São
92 segmentos traduzidos, incluindo corpo e escolhas de mensagens compostas,
distribuídos por 13 blocos SSD. Bloco SSD não é uma identificação comprovada de
personagem ou cena; os rótulos existentes permanecem protegidos.

O intervalo inclusivo é `0x1DF47F0C..0x1DF4DFEC`. Contém conversa familiar,
alternativas de carreira, McKinley, Scarlet, Dr. Mortem/Igor, lava-tanques e
retorno à oficina. É um recorte de arquivos da região inicial, sem afirmar que
todos esses diálogos ocorrerão em uma única rota ou que a cidade inteira esteja
traduzida. Inventários de itens, tanques, procurados e inimigos não foram editados.

A fala inicial é `Você quer mesmo ser um` / `Hunter?`, com o artigo preservado e
31 bytes no slot de 31 bytes. `Hunter` e `Soldier` são termos protegidos por
orientação do usuário. O lote também restaura `*sigh*` e conserva risadas e
expressões. `docs/glossario.md` registra as demais regras de preservação.

## Arquivos autorais e revisão

`translations/regiao-inicial-v002.json` herda o piloto v001 e sobrescreve somente
as traduções revisadas, acrescentando as novas. Assim, a versão histórica e seus
hashes permanecem recuperáveis. O artefato `rascunho.json` exportado é expandido,
com todo o lote disponível em um único JSON para leitura.

Uma tradução de McKinley é reutilizada em outra ocorrência somente porque os
segmentos originais são idênticos. Os IDs não são fundidos; cada ocorrência tem
offset, bytes e metadados próprios. Heranças circulares, aliases incompatíveis,
IDs ausentes e alterações de rótulos protegidos são rejeitados.

Os arquivos originais, planos bilíngues e relatórios de revisão completos ficam
em `work/`. Somente traduções autorais, scripts, testes e metadados apropriados
entram no Git. Os hashes dos arquivos herdados e da política acompanham o lote.

`translations/politica.json` e `tools/translation_policy.py` fazem verificações
locais de nomes/termos conhecidos e expressões preservadas, além de exigir sucata
quando junk aparece como material. A lista não reconhece automaticamente todos
os nomes próprios possíveis. Nenhum verificador local garante sozinho gramática,
contexto ou qualidade literária; essas responsabilidades continuam com a revisão
da tradução. A regra de junk não proíbe traduzir trash como lixo quando adequado.

## Bloqueios preservados

| Registro | Motivo |
| --- | --- |
| `map.smnn.1df49f00` | Papel da terceira string não liberado |
| `map.smsg.1df4c1ec` | Controle opaco de preço |
| `map.smsg.1df4d28c` | Nome dinâmico e preço opacos |
| `map.smsg.1df4d364` | Nome dinâmico e preço opacos |
| `map.smsg.1df4d5cc` | Preço opaco |
| `map.smsg.1df4d6a8` | Preço opaco |

Esses registros são copiados sem alterar qualquer byte. É esperado que algumas
perguntas de preço e respostas associadas continuem em inglês. Os demais registros
não são bloqueados por isso. Não houve relaxamento de parser ou controle.

## Executar localmente

- `Preparar-Regiao-Inicial.cmd`: compila e valida o lote em uma nova pasta
  `work/pilotos/`, sem construir outra ISO.
- `Testar-Regiao-Inicial.cmd` ou `Iniciar-Teste.cmd`: abre a ISO consolidada
  já construída, no emulador isolado.
- `Testar-Piloto-Inicial.cmd` também aponta para a versão consolidada atual.
- A versão antiga continua acessível explicitamente por `Iniciar-Teste.cmd pilot`.

Para editar, alterar o texto de `translations/regiao-inicial-v002.json`.
Chaves de mensagens compostas são `body` e `choices`; rótulos não são editáveis.
LF e TAB devem permanecer na mesma sequência, assim como comandos `%...`.
O compilador preserva tamanhos de registros, segmentos, blocos e extents.

```
python tools/build_translation_pilot.py --output work/minha-revisao
python tools/build_translation_pilot.py --output work/minha-construcao --build-iso
python -m unittest discover -s tests
python tools/iso_retention.py
```

Cada saída deve ser nova. Revisões comuns não geram ISO. A construção exige
fontes v002 e patch de espaçamento v003, com hashes conferidos; não altera a
ISO transacional v004 nem promove silenciosamente o novo perfil às receitas antigas.

## Integridade e limites

Os 83 testes passaram. O teste do lote ampliado cobre deferrals, rótulos,
reutilização por fonte idêntica e bloqueio integral por violação de nome protegido.
O compilador também confere buffers, terminadores, controles, offsets, bytes de
origem e releitura. Todos os 85 registros modificados usam slots; não há repack.

A ISO foi comparada integralmente ao original: apenas intervalos previstos de
MAP, 36 células GFI e a janela de 128 bytes do ELF mudaram. Diretórios, LBAs e
tamanhos ficaram iguais. O relatório próprio está em
`reports/regiao-inicial-v002-validation.json`.

O compilador mantém dez avisos conservadores de largura. A métrica legada ainda
conta acentos como duas unidades. Esses avisos não são prova de corte, mas também
não podem ser apagados supondo que o novo perfil resolva todo layout. O usuário
autorizou trabalhar assumindo os caracteres corretos; não houve novo teste visual.

## Retenção de ISOs

Todos os construtores atuais reservam uma vaga antes de gerar uma ISO. São
permitidas até dez ISOs de trabalho, excluindo a referência imutável em `JOGO`.
O excedente elegível mais antigo é removido; relatórios e receitas ficam guardados.
O comando sem `--apply` apenas apresenta o plano de retenção.

Não remover automaticamente links, arquivos sem prefixo de saída conhecido,
imagens ligadas a journal pendente, ISO de desenvolvimento, experimento do diário
ou ISO-base do perfil de acentos v001. Se a retenção não puder cumprir o limite
com segurança, recusar a construção. A política usa mtime para ordenar antiguidade;
os construtores devem ser executados sequencialmente. Não houve remoção de ISO
nesta entrega: o total final é oito ISOs de trabalho.

## Próximo avanço

Expandir para o próximo agrupamento de diálogos com as mesmas regras e manter
uma versão consolidada por lote. Investigar os controles opacos separadamente,
sem permitir que preços ou nomes dinâmicos sejam tratados como texto comum.
Quando houver teste manual, conferir primeiro fala inicial, escolha de carreira,
nomes, preços ainda em inglês, risadas, margens e avanço de páginas.
