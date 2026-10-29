# Interface v053 — seis nomes aprovados e ações correspondentes

A v053 aplica seis revisões já aprovadas pelo usuário. Não acrescenta itens
ou diálogos: mantém 541 nomes de itens aplicados e reduz de 15 para nove as
propostas de nomes ainda pendentes.

| Item | Nome aplicado | Bytes na codificação do projeto |
|---|---|---:|
| 331 | Pílula Açucarada | 18 |
| 372 | Frasco do pânico | 17 |
| 459 | Estátua de barro | 17 |
| 838 | Projétil sônico | 17 |
| 841 | Projétil de gelo | 17 |
| 849 | Projétil crítico | 18 |

As cinco entradas de ações 0124, 0884, 0887, 0882 e 0895 acompanham os nomes
dos itens 331, 838, 841 e 849. Não foi ampliado o limite dessas ações.
Idolo de barro, a exceção de acento autorizada na v052, permanece igual.

## Evidências e limites

`tools/scene_name_fields.py` lê o banco maps em MAP.MCT+0x800, seu cabeçalho
de 0x12F0 bytes, 300 descritores de 16 bytes e as árvores associadas. Verifica
hierarquia, intervalos, tipos, terminadores e padding. Reconheceu 839 campos
de nome de 32 bytes: 837 ASCII e dois nativos preservados. São nomes/contextos
de cenas, muitos próprios, repetidos ou numéricos; não são 839 traduções faltantes.

Os 839 campos e todas as 300 árvores foram comparados com a ISO v052.
Nenhum nome contém referência I. Os 400 nós tipo 3 que herdam nome apontam
a pais tipo 2. Os setters tipados em 0x44950/0x44AB8 copiam nomes e escrevem
flags em +0x20/+0x21: podem sobrescrever o NUL no byte 33 observado antes.
Portanto aquele NUL isolado não prova um limite universal ao longo da vida
do objeto. Os nomes concretos recuperados terminam até o byte 31.

Para os 34 campos de mensagem com I (35 páginas), a análise da receita
compilada admite 18 bytes por nome de item e 31 por nome N0 válido. O maior
resultado conservador foi 91 células por página (limite 99 antes do NUL)
e 332 bytes por corpo (buffer de 1024 incluindo NUL). Os nove chamadores do
outro formatador continuam ligados aos 299 campos mail/diário/wanted sem I,
conforme a investigação v006; não foi repetida uma varredura sem objetivo.

Estas conclusões dependem dos recursos e receitas vinculados e de um estado
válido do jogo: índices válidos e nomes N0 com NUL dentro de seus 32 bytes.
O setter N0 usa strcpy sem limite; não se afirma segurança para saves
malformados, entradas arbitrárias, aliases indiretos ou novos templates em RAM.

A política `six-approved-item-names-bounded-release-v001` vincula pai v052,
revisão humana, evidências, seis IDs e cinco ações por hash. Usa somente os
prefixos comprovados dos campos físicos de 24 bytes. O limite genérico de
16 bytes continua recusando esses seis nomes fora desse perfil explícito.
Não houve mudança de fonte, layout, controles, atributos ou tamanho de arquivo.

Reproduzir a prova local, sem IA ou internet:

```powershell
python tools/scene_name_fields.py --release-proof --current-iso work/interface-v052/MetalSaga-ptbr-interface-v052.iso --output work/prova-seis-nomes-v007.json
```

A comparação com a v052 requer que essa imagem ainda esteja disponível pela
retenção. A análise simples pode ser repetida sem ela; os textos/bytes de
cena exportados ficam exclusivamente em work/.

## Versão para teste

Abrir **Iniciar-Teste.cmd**. O destino atual é
`work/interface-v053/MetalSaga-ptbr-interface-v053.iso`.
`Preparar-Interface.cmd` valida a receita; `Auditar-Traducao.cmd` usa a v053
e separa as nove revisões restantes das seis agora compiladas.

Tamanho: 1.704.427.520 bytes.
SHA-256: `a0b4ca47ed077d5379d4e268d08d1b506b05909c03f6324220960efc980b1f4f`.

A comparação integral v052→v053 confirmou 163 bytes diferentes em exatamente
11 patches de S_PACK.SDA. Todos os demais bytes e o diretório ISO são iguais.
Passaram 137 testes unitários, sem falhas, erros ou ignorados, incluindo
round-trip dos campos e preservação dos atributos. Tamanho, hash, ausência de
transações e preparação do iniciador também foram conferidos. O emulador não
foi iniciado; a validação visual desta revisão permanece para o usuário.

Ao encontrar esses itens durante a partida, conferir nomes completos e ações
correspondentes nas listas e menus. Não é necessário alcançar uma cena agora.
Mantidas cinco ISOs de trabalho e a alpha protegida. Sem OneDrive/desligamento.

## Próximo trabalho

As nove propostas restantes excedem algum perfil de largura observado.
Analisar as caixas reais de inventário, lojas e batalha antes de aplicá-las;
não abreviar nomes aprovados, reduzir a fonte ou liberar limites globais
apenas para eliminar pendências. As evidências desta rodada não autorizam
esses nove casos. Receitas e relatórios históricos permanecem reproduzíveis.
