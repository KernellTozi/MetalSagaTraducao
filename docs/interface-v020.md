# Interface v020 — três blocos consolidados

A rodada acrescenta **238 campos/ocorrências** à v019, em uma única ISO:

| Bloco | Inclusões |
|---|---:|
| Nomes genéricos de itens, acessórios e habilidades | 189 registros / 183 rótulos distintos |
| Descrições antes adiadas | 41 textos / 51 referências de itens |
| Confirmação de melhoria e rótulos compartilhados | 8 campos |

Total acumulado: **1.772 campos/ocorrências de interface**. MAP v030 continua
com 5.892 registros alterados; layout/fontes v005 e arte v014 permanecem iguais.
Essas unidades são diferentes e não constituem uma porcentagem de todo o jogo.

## 1. Inventário, acessórios e habilidades

Os 189 registros abrangem 12 nomes de equipamento genérico, 52 de consumíveis/
materiais, 47 de móveis/acessórios, 62 de habilidades e 16 de objetos genéricos.
Exemplos: Granada, Spray alcalino, Incenso de cura, Suco, Gelo, Macacão jeans,
Luvas de couro, Aquário, Ar-condicionado, Holofote, Reparo I/II, Precisão,
Contra-ataque, Anjo da guarda e Lança-chamas.

Nomes de armas humanas, motores, C Units, LOVE machine, personagens, tanques,
cidades e componentes únicos continuam preservados. Nomes repetidos dentro da
tabela recebem a mesma tradução em todos os seus IDs; não separar ocorrências
para obter nomes diferentes. Nomes distintos que já eram distintos podem
continuar com termos próximos em português. Alterar o nome pode mudar a ordem
da ordenação alfabética; o ID, atributos, preço e identidade do item não mudam.

Política opt-in: **spack-reviewed-generic-item-names-original-slots-v001**, em
`tools/item_names.py`. Usa a tabela já identificada de **1.349 registros × 128
bytes**, em **S_PACK 0x820**, com **1.041 registros de nome não vazio**.
O nome termina em NUL antes de +24; +24 contém o offset da descrição.

**O maior nome original tem 16 bytes.** A janela de 24 bytes não autoriza
expansão: cada tradução continua dentro do comprimento do próprio nome de
origem. O NUL final original permanece zero, e a sobra até ele é zerada. Não
alterar os demais bytes do registro, atributos, offsets, SDA pai ou extents ISO.
Não usar os oito bytes aparentes de folga como nova capacidade.

As seleções editoriais e os hashes dos nomes/registros ficam na receita.
Controles `%`, pipes, quebras e NUL injetado são proibidos. Números e marcadores
de nível EX/I/II/III permanecem vinculados; tamanhos P/M/G/GG/XGG são a
localização explícita dos tamanhos S/M/L/XL/XXL dos pacotes de placas.

Evidências do ELF original, vinculadas por SHA-256:

- **0x70A68..0x70B9C:** calcula quantidade pelo tamanho >>7, aloca e copia os
  registros; a base em RAM é obtida de **0x475AE8**.
- **0x6D938..0x6D950:** lê ID em objeto +8 e devolve base + ID×128. A execução
  limitada desse getter foi conferida para os 1.349 índices em memória sintética.
- **0x1B34D0..0x1B3530:** encaminha o início do registro como nome para a rotina
  de texto em VA **0x2967C8**, cujo início corresponde ao arquivo **0x1977C8**.
  Não confundir endereço virtual com offset do ELF.
- **0x705A8..0x70610:** compara nomes na ordenação. Isso explica a possível
  mudança de ordem alfabética, sem interpretar comparação como alteração de ID.

Não foi executado o formatador inteiro nem provados todos os consumidores do
jogo. O limite original por nome é uma guarda conservadora; renderização,
largura em pixels e quebras dessa família aguardam teste visual do usuário.

Das **429 ocorrências selecionadas para propostas**, 189 foram aprovadas, 239
ficam adiadas e uma foi explicitamente preservada por categoria protegida.
Nos adiamentos: 236 propostas excedem o orçamento, duas exigem glifos ainda
ausentes do mapeamento atual (`Ó` e `Â`) e uma esbarra na proteção do nome Fang.
Essas categorias registram a primeira recusa; um texto pode ter mais de uma
restrição. Os demais nomes não são dívida automática de tradução: muitos devem
continuar em inglês por decisão do usuário. Não comprimir nomes, retirar acentos,
inventar abreviações obscuras ou remover preposições para aumentar a contagem.
As propostas adiadas não são aprovação editorial; reavaliar significado e contexto
antes de aplicá-las, mesmo que uma restrição de espaço venha a ser resolvida.

## 2. Descrições recuperadas

São **536 de 567 descrições traduzidas (94,53% deste pool conhecido)**, usadas
por **883 IDs de itens**. Todas as 495 traduções da v019 permanecem idênticas;
os 41 IDs novos vieram da lista de adiamentos, com retomada explícita.

Foram recuperadas descrições de armas, lentes/pistolas, alvos especiais,
consumíveis, decoração, habilidades e medalhas de vitórias consecutivas.
Mantêm-se os números, materiais, efeitos, condições e MAIN/SUB/SE. As quebras
ocorrem entre palavras; casos complicados continuam sem alteração.

Restam **29 adiamentos de espaço/linhas**, o registro percentual `80%%`
tecnicamente bloqueado e o marcador `???` preservado. Os 30 adiamentos mantêm
integralmente as propostas/metadados da v019. Não se reorganiza o pool nem se
libera o percentual por semelhança com outros recursos.

O perfil continua **spack-item-description-original-slots-v001**: pool em
**0x2AAA0 / 0x4EC0**, sem crescimento, com todos os offsets de descrição
imutáveis. As novas origens ocupam 1.438 bytes; os destinos, 1.340 bytes.
A garantia de nomes intactos dessa ferramenta refere-se aos seus próprios
patches; a v020 autoriza separadamente os 189 nomes genéricos acima. O relatório
integrado explicita essa diferença para não afirmar que nenhum nome mudou.

## 3. Melhoria de peças e rótulos compartilhados

A confirmação de melhoria usa a política opt-in
**spack-in-de-cremento-preview-v001**. Traduz somente o rótulo **142** da tabela
UI S_PACK, usando “incremento/decremento”. Preserva os prefixos originais
compartilhados `in`/`de` nos IDs **143/145** e **144/146**, todos os aliases e
os parâmetros printf. Não há patch no código do ELF para essa confirmação.

O trecho **0x1F0320..0x1F040C** encaminha formato, nome e número de item,
atributo e prefixo para `sprintf`. As tabelas de quatro halfwords em
**0x349FB8** e **0x349FC0** selecionam atributos **22/29/28/31** e prefixos
**143/144/145/146**. `tools/spack_composition.py` executa somente o trecho
sem desvios de **0x1F038C..0x1F03E8**, incluindo o delay slot da chamada,
e para antes de invocar o formatador. As 16 combinações sintéticas foram
conferidas. Isso não executa cálculo de preço, transação, renderização ou PS2.

O repack continua restrito à tabela UI existente de **8.192 bytes**. Todas as
outras traduções e os aliases são preservados pelo compilador; o perfil histórico
continua bloqueando o rótulo 142 sem a opção e os hashes específicos.

Sete literais ELF adicionais usam o perfil fixo já existente: **Dir.**, **Esq.**,
três cabeçalhos **Saldo** e duas ocorrências **MAIN/SUB** em maiúsculas. Endereços,
NULs, espaços de alinhamento e controles permanecem preservados. Não declarar
menus inteiros concluídos por esses sete campos.

## Ferramentas locais e teste

`python tools/plan_interface_menus.py` atualiza o mesmo
**work/planejamento-interface.json**, agora incluindo todos os registros de nomes,
fontes legíveis, IDs, offsets, hashes e classes. Nenhuma IA/API/rede é utilizada
nessa análise ou na compilação binária. Os textos originais exportados ficam em work/,
fora do Git; as receitas versionadas contêm traduções e metadados próprios.

Abra **Iniciar-Teste.cmd** para usar
**work/interface-v020/MetalSaga-ptbr-interface-v020.iso**. Em partida normal,
confira inventário/lojas, móveis/acessórios, lista de habilidades e confirmação
de melhoria de peças: nomes completos, acentos, alinhamento, seleção, preços e
efeitos. Não é necessário chegar a cada habilidade imediatamente. Teste visual
pendente do usuário; não houve navegação no PCSX2 nesta rodada.

Reprodução:

```powershell
python tools/build_translation_pilot.py --draft translations/regiao-inicial-v030.json --interface-draft translations/interface-v020.json --output work/interface-reproducao-v020 --compact-output --build-iso
python -m unittest discover -s tests -p "test_interface*.py" -v
```

Uma ISO e um relatório por construção. Cinco ISOs de trabalho, alpha permanente
protegida, originais/BIOS/saves preservados. OneDrive somente por novo pedido.
O relatório único de evidências e integridade é **reports/interface-v020.json**.

## Validações executadas

- **135 testes de interface** passaram em 295,172 s. Mais seis de planejamento,
  cinco de retenção e três de alpha: **149 testes distintos**. Os quatro testes
  da composição foram reconferidos com a comparação adicional do orçamento
  lexical expandido; não representam quatro testes distintos a mais.
- Getter original de registros para os **1.349 índices**, leitura de volta e
  round-trip dos nomes; atributos e offsets de descrição intactos em todos os
  registros, com nomes protegidos e ocorrências compartilhadas conferidos.
- **16 combinações** de argumentos da confirmação verificadas em memória
  sintética. As fixtures expandidas em Python cabem no orçamento das fixtures
  anteriores. Isso não executa o `sprintf` do jogo nem comprova todo o expansor.
- Preservação de traduções anteriores, dos 30 adiamentos de descrição restantes,
  fontes/layout, título e recursos alheios; patches disjuntos e origens vinculadas.
- Comparação integral v019→v020: **7.882 bytes diferentes em 238 intervalos
  autorizados**. Todos os demais bytes e o diretório ISO permanecem idênticos.
  A reorganização interna da tabela UI é o patch específico já comprovado,
  conservando conteúdos/aliases das outras entradas.
- ISO de **1.704.427.520 bytes**, SHA-256
  `31610ae575843c062f701b84ad84fc904057b8b6d6da7229812302d4a4a5a47f`.
- Iniciador conferido sem abrir PCSX2. Cinco ISOs de trabalho e alpha permanente
  conferidas; sem envio ao OneDrive ou alteração dos saves.

## Recuperação após queda de energia

A interrupção ocorreu durante os testes, antes da construção da ISO v020.
A v019 foi reconferida integralmente por SHA-256 e tamanho. Os JSON salvos
foram lidos com sucesso; não havia `.partial` ou transação ativa da v020.
O log interrompido foi preservado localmente, sem ser contado como aprovação.

Uma falha já identificada no validador foi corrigida: o segundo byte de um
acento GFI podia parecer a letra ASCII I. Os marcadores de nível agora são
comparados no texto Unicode, e há regressão específica para “Maiô”. A mudança
não altera a fonte nem a codificação do jogo. A bateria completa foi reiniciada;
seus resultados finais constam no relatório, separados da execução interrompida.

## Próximos passos

Investigar os limites dos consumidores antes de permitir crescimento de nomes
ou reorganização das descrições. Resolver a proteção contextual de Fang e a
cobertura de glifos maiúsculos somente com política específica, preservando
acentos. Seguem pendentes Coat, TITLE/BACK, demais textos gráficos e o teste
consolidado em partida. Não retomar os fragmentos MAP para inflar contagens.
