# Interface v046 — saída da nomeação e destinos genéricos

Continuação solicitada após a v045. Esta rodada resolve cinco lacunas pequenas
com evidência própria: uma legenda existente da entrada de nomes e quatro
registros da tabela de destinos. Não redesenha gráficos nem modifica fontes,
itens, diálogos, nomes próprios ou regras do jogo.

## Alterações

| Contexto | Original | Na v046 |
| --- | --- | --- |
| Círculo na variante TITLE da entrada de nomes | TITLE | SAIR |
| Destino 14 | Lake Bridge E | Pte. do lago L |
| Destino 16 | Isle W | Ilha O |
| Destino 22 | Medical Lab | Lab. médico |
| Destino 23 | Transport Pod | Cáp. transp. |

Pte. significa ponte; L corresponde a leste e O a oeste. As abreviações dos
destinos respeitam o teto observado de 14 bytes e os campos já existentes.
Lab. médico e Cáp. transp. usam caracteres já disponíveis no perfil v005.
Nenhum acento foi removido, nenhum glifo novo foi criado.

Os **outros 21 destinos permanecem byte a byte iguais**, incluindo Junkyard,
Junkyard E, cidades, seus sufixos e nomes protegidos como Antitank Fort. Não
trocar automaticamente os sufixos de nomes próprios pelo padrão dos genéricos.
Lista completa local em `work/lacunas-interface-v001/destinos.md`.

Total da interface: **3.840 campos**, quatro novos; SAIR é revisão de uma
legenda já contada. Permanecem 541 nomes de itens, zero pendências naquele
recorte, 6.024 registros MAP alterados e todas as decisões anteriores.

## TITLE: significado comprovado e limite da conclusão

O slot literal é **0x32A31E**, cinco bytes dentro da primeira legenda em
0x32A310. As outras variantes usam CANCEL/DELETE e continuam iguais. A nova
política `name-entry-title-exit-reviewed-v003` herda a prova de BACK/VOL. e
acrescenta provas da saída. A política antiga continua exigindo TITLE.

As evidências de inicialização, pedido de estado 4 e seleção de legenda
continuam preservadas. Novos caminhos originais executados em RAM sintética:

- Wrapper de estado 4 em **0x10D650..0x10D658** chama **0x10BF18** com o objeto.
- Ramo TITLE em **0x10BF94..0x10BFAC**, com modo +0x3038=1: limpa +0x303C,
  avança o subestado +0x88 para 2 e preserva os demais bytes do objeto.
- Teste terminal original, incluindo o **LH real em 0x10BFC8** e sua branch,
  retorna concluído quando +0x9E=0; valores 1/65535 continuam não concluídos.
- **0x10D658..0x10D688** propaga essa conclusão e, com +0x303C=0, salta as
  chamadas de confirmação de nome em 0x10D674/0x10D67C.
- **0x10D6CC** transmite o resultado ao chamador. Apenas esse trecho é
  executado; não se simula restauração MMI, callbacks, fade completo ou GPU.

Isso sustenta **SAIR da operação de nomeação sem confirmar o nome pelo caminho
TITLE**. O destino externo continua sem prova completa; não declarar que
sempre retorna à tela de título. A redação SAIR descreve o que foi demonstrado,
sem atribuir um destino não comprovado. O comportamento não é alterado.

Somente os cinco bytes TITLE viram `SAIR `, com o último espaço preservando o
slot. Pares nativos, ícones, separadores, demais legendas, cabeçalho, NUL e
endereços permanecem. O interpretador local ganhou LH com sinal e SLTU de
32 bits para executar esses caminhos; **nenhuma instrução do ELF é editada**.

## Tabela de destinos: estrutura e encaminhamento

S_PACK.SDA, nó SDA 0x35000, entrada 3, intervalo **0x7E720..0x7ED60**.
São 25 registros variáveis com ponteiros relativos e nomes nos primeiros
32 bytes. O campo de flags começa em +32; campos escritos em RAM em +36/+40
e caudas variáveis permanecem fora dos patches. Não é um pool só de strings.

Foram reaproveitados os 25 casos comprovados do lookup em
**0x11F35C..0x11F378**. Acrescentaram-se 25 casos de encaminhamento em
**0x11F3B0..0x11F3C8**, passando diretamente o ponteiro de nome e tamanho de
fonte 22 ao construtor **0x110198**. A chamada de strlen em **0x1101D0** também
é vinculada; os novos bytes foram contados pela rotina original. Os maiores
nomes originais têm 14 bytes; o lote não ultrapassa esse envelope, apesar do
campo físico de 32 bytes. Não se autoriza usar seus 31 bytes por suposição.

Somente os quatro campos de nome recebem texto/NUL/zeros. Ponteiros, IDs,
flags de desbloqueio, coordenadas, outras entradas e caudas permanecem.
Não houve execução completa do construtor, census de todos os consumidores
ou teste de seleção/transporte no PCSX2. A prova é delimitada a esses caminhos.

Manifesto: `translations/lacunas-interface-v001.json`, ligado por hash à v045.
`tools/interface_gaps.py` exige o conjunto exato e os textos acima; alterações
extras são recusadas. As políticas históricas não são liberadas automaticamente.

## Verificações

**121 testes distintos aprovados**, oito novos. Incluem saída e confirmação,
LH com sinal, SLTU sem sinal, preservação dos bytes nativos, bloqueio da política
antiga, quatro destinos, 21 preservações, round-trip e recusa de alterações extras.

Medição de avanços do layout existente: 165 probes de glifos, 12 casos de
destinos (fonte 22/modos 0,1,2) e seis casos TITLE/SAIR (22/26/modos 0,1,2).
Os quatro destinos ficam no envelope original e SAIR é sempre mais estreito
que TITLE. A grafia genérica lago em minúsculo evita alargar a linha em três
pixels no modo proporcional; não houve redimensionamento ou edição de bitmap.
Essas medições não comprovam os recortes reais de todos os menus.

A concordância dos nomes mantém 65 ocorrências corretas e zero sem decisão;
ledger `translations/consistencia-nomes-decisoes-v003.json`, sem novas trocas.
Isso continua sendo uma busca delimitada, não prova de cobertura semântica total.

**Nenhum PCSX2 foi executado nesta rodada.** Em partida normal, conferir SAIR
na entrada de nome sem texto digitado, preservar funcionamento de VOL./CANC./
APAGAR/FIM e observar os quatro nomes quando os destinos estiverem disponíveis.
Não é necessário desbloquear cada destino agora. Manter os testes agrupados.

## Reprodução

```powershell
python tools/build_translation_pilot.py --draft translations/regiao-inicial-v040.json --interface-draft translations/interface-v046.json --compact-output --build-iso --output work/minha-v046
python -m unittest discover -s tests -p test_interface_gaps.py
python tools/audit_name_consistency.py --recipe translations/interface-v046.json --decisions translations/consistencia-nomes-decisoes-v003.json --output work/minha-conferencia-v046.json
```

Usar novas saídas. Sem IA/APIs/rede nas operações binárias. Pôsteres wanted,
gráficos dispensados de cassino/minijogos e créditos não foram reabertos.
Fontes maiúsculas não foram ampliadas apenas para esta entrega. Estruturas
nativas opacas, rótulos de falantes sem espaço e gráficos sem edição comprovada
continuam separados; esta etapa não comprova tradução de toda a interface.

## Entrega consolidada

`Iniciar-Teste.cmd` usa
`work/interface-v046-final/MetalSaga-ptbr-interface-v046.iso`.
`Preparar-Interface.cmd` valida interface v046/MAP v040. Tamanho da imagem:
1.704.427.520 bytes; SHA-256
`eaa4c7d4b0cffabd6d8a090bddfe1048f7a9c63b2ce8dceb764d6ec34d35d0b3`.

Preflight integral e comparação v045 → v046 aprovados: **46 bytes diferentes
em cinco patches**, uma legenda ELF e quatro campos S_PACK. Diretório e todos
os demais bytes permanecem, inclusive instruções, fontes, gráficos e MAP.
Relatórios: `reports/interface-v046.json` e `reports/interface-v046-delta.json`.
Cinco ISOs de trabalho mantidas; alpha permanente conferida por SHA-256.
Sem transferência OneDrive ou desligamento solicitado nesta rodada.
