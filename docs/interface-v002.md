# Interface v002 — lote ampliado

## Escopo

Atendendo ao pedido de lotes maiores, esta rodada acrescenta **185 strings**, mais que o dobro das 88 novas da rodada anterior. Total acumulado: **273 strings de interface**. Preserva integralmente as 88 entradas v001 e os 5.892 diálogos v029, com layout v005. Os 123 pequenos adiamentos do MAP continuam pausados.

Conjuntos tratados de uma vez:

- Opções: som, velocidade do texto, vibração, volumes, posição da tela, aceitar/voltar/padrão.
- Nomeação: confirmação do nome e prompts textuais disponíveis. O título gráfico/sem referência comprovada da tela de nomeação não foi liberado.
- Status e veículos: equipar/remover/trocar, peças, munição, blindagem, transferência, sobrecarga, C Unit, encaixes e parâmetros numéricos.
- Batalha e campo: avisos de alcance/condição, recompensas, detecção e efeitos. Isso não traduz os botões desenhados nas texturas de batalha.
- Pintura/carimbos e minijogos: seletores, sair/voltar, inventário, dinheiro insuficiente, prêmios com valores/nomes variáveis e novas tentativas.

Nomes protegidos como Hunter, Soldier, Teleporter, Moocher, Mine/Metal Detector e C Unit permanecem. Alguns rótulos usam abreviações usuais para respeitar o orçamento. A receita completa está em `translations/interface-v002.json`, com `parent_recipe` e os 185 `added_ids` explícitos. Não há tradução automática durante a compilação.

## Uso

`Preparar-Interface.cmd` valida a v002 localmente sem criar outra ISO. `Testar-Interface.cmd` e `Iniciar-Teste.cmd` abrem a imagem consolidada atual:

`work/interface-v002/MetalSaga-ptbr-interface-v002.iso`

Para construir novamente em uma pasta nova sob work/:

```powershell
python tools/build_translation_pilot.py --draft translations/regiao-inicial-v029.json --interface-draft translations/interface-v002.json --output work/interface-v002 --build-iso
```

O alias `interface-v001` mantém a imagem de trabalho anterior enquanto retida; a **alpha permanente é a cópia separada de v001** descrita em `docs/alpha-v001.md`. Construções futuras não alteram aquela cópia.

## Segurança e pendências

Mantém a política de hashes, endereços fixos, referências, bloqueio de aliases internos e orçamento da string original. Além da sequência exata de printf, separadores e espaços iniciais, o compilador agora exige também espaços finais originais. Isso evita juntar rótulos/valores dinâmicos ou perder padding. Não são modificados ponteiros, código de fontes, nomes de entidades ou arquivos originais.

`reports/interface-v002-deferred.json` registra 14 propostas deixadas para depois por referência, contexto ou orçamento. Esse total cobre somente as propostas revistas nesta rodada, **não todas as pendências da interface**. Alguns nomes de minijogos permaneceram em inglês para evitar abreviações ruins. Não liberar uma string por caber ou por parecer uma interface.

As capturas do usuário também mostraram estatísticas, cabeçalhos de veículos, tela de nomeação e avisos de Memory Card. A confirmação de nome e as opções textuais avançaram neste lote. Estatísticas em `0x32C6C0` têm quebras de linha e um cabeçalho anterior de 16 bytes; o cabeçalho de veículos em `0x32C810` também não segue o literal NUL isolado do catálogo atual. Foram localizados, mas **não editados**: precisam de um perfil comprovado para essa estrutura e suas referências. O título de nomeação em `0x33B3B8` não tem referência segura reconhecida pelo catálogo. Não ampliar a regex para tratar essas origens automaticamente.

Os avisos de Memory Card e os títulos New Game/Load Game ainda precisam ter a origem localizada. Alguns rótulos de Satcom/batalha estão em FBS_DATA.SDA e dependem de importação fiel de textura, conforme o manual v001. Corpos de mensagens, DIARY.DAT e ajuda ainda não estão totalmente localizados/traduzidos. Esses trabalhos continuam na etapa de interface, antes dos itens.

## Validação e roteiro

Os testes verificam a preservação integral de v001, IDs novos, controles, alinhamento, orçamento, glyph round-trip, proteção da alpha, retenção e rotinas do layout aprovado. A construção verifica a ISO inteira contra os patches esperados; a comparação adicional com v001 exige diferenças somente nos 185 novos intervalos. Evidências em `reports/interface-v002-tests.json` e `reports/interface-v002-validation.json`.

Não foi executado o PCSX2 nesta rodada. A validação visual será conjunta: opções, confirmação de nome, status/equipamentos, peças/munição, Satcom, avisos de dinheiro e minijogos. Conferir acentos, rótulos, parâmetros numéricos, alinhamento de colunas, seleção/volta e ausência de cortes. Não é necessário testar cada string individualmente. A v005 aprovada nas falas de Nina não comprova todos os contextos de interface.


## Resultado da rodada

- 25 testes direcionados passaram, sem erros, falhas ou skips; não foi repetida a suíte histórica inteira.
- ISO criada com 273 strings de interface e 5.892 diálogos traduzidos preservados. Tamanho: 1.704.427.520 bytes.
- SHA-256: `53452968ea41da630b832cda77443188a3aeabb9d0f32334f8cb1465d45c8d11`.
- Comparação integral com a alpha: 2.256 bytes diferentes, somente nos 185 novos patches. MAP, fontes e demais recursos idênticos; diretórios e extents inalterados.
- Alpha novamente conferida pelo hash durante a comparação e ainda somente leitura após construir.
- Dez ISOs sob work/; v023 removida como a mais antiga elegível. A alpha permanente fica adicionalmente em dist/, fora dessa fila. Receitas e relatórios históricos preservados.
- Iniciador conferido em dry-run. Não houve execução ou aprovação visual no PCSX2 nesta rodada.
