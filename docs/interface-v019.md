# Interface v019 — recuperação ampla das descrições adiadas

Esta rodada acrescenta **142 descrições distintas**, usadas por **230 IDs de
itens**, preservando integralmente as 353 traduções da v018. O catálogo conhecido
passa a **495 de 567 descrições traduzidas (87,30%)**, utilizadas por **832 IDs**.
Os aliases são referências ao mesmo texto e não contam como traduções distintas.
São **1.534 campos/ocorrências de interface** acumulados; MAP v030 continua com
5.892 registros alterados. Essas unidades não determinam a porcentagem do jogo.

## Escopo e revisão

O lote reúne armas humanas e de cães, armaduras, equipamentos de veículos,
consumíveis, objetos de missão, decoração, peças genéricas e habilidades.
Todas as inclusões vêm da lista de adiamentos da v018; nenhum texto aprovado
anteriormente foi reescrito. Permanecem os nomes de itens, atributos, preços,
efeitos binários, MAIN/SUB/SE, personagens e referências únicas.

A revisão contextual usa redações completas e concisas, com quebras somente
entre palavras. Mantém condições como a restrição a mecânicos, alvos ocultos,
abrigados, submersos, aéreos e em alta altitude; distingue atrair atenção de
aproximar fisicamente um inimigo. Ataque inicial garantido, efeitos automáticos,
reparação integral e resistência elemental continuam explícitos onde presentes.
Os acentos seguem o perfil aprovado v005, sem reduzir ou redesenhar a fonte.

Tentativas curtas que perderiam condições/efeitos, confundiriam categorias ou
exigiriam retirar preposições de nomes de armas foram descartadas. Propostas
recusadas nesta rodada não substituem as propostas anteriores arquivadas: os
**71 adiamentos remanescentes** mantêm todos os seus metadados da v018.

| Classe do pool conhecido | Quantidade |
|---|---:|
| Traduzidos e aprovados binariamente | 495 |
| Adiados por espaço/linhas | 70 |
| Percentual `80%%` bloqueado | 1 |
| Marcador `???` preservado | 1 |
| Não revistos neste catálogo | 0 |

## Limites preservados

Continua a política `spack-item-description-original-slots-v001`, sem mudança
de permissões: pool S_PACK em **0x2AAA0**, tamanho **0x4EC0**; **1.349 registros
de 128 bytes** em **0x820**; offset relativo da descrição em **item +24**.
São 927 referências para os 567 alvos conhecidos. Nomes, registros e referências
ficam intactos. Não se reutiliza folga de outra string, não se reorganiza o pool,
não há crescimento de slot, arquivo ou extent ISO.

Cada inclusão é conferida contra hashes de origem e de todos os registros
compartilhados, comprimento em bytes, repertório GFI, números, terminologia,
quantidade de linhas e máximo conservador de colunas do original. A fonte usa
dois bytes para os acentos mapeados; contar caracteres Unicode não mede esse
orçamento. As 142 origens ocupam 5.060 bytes; os destinos, 4.722 bytes.

## Diagnóstico local reutilizável

`tools/prepare_item_batch.py` acrescenta `diagnose_budget`, usado pelo planejador
existente. A execução continua local, sem IA, APIs ou internet:

```powershell
python tools/plan_interface_menus.py
```

Atualiza o mesmo **work/planejamento-interface.json**, sem criar um arquivo por
item ou por execução. Cada pendência recebe bytes de origem/destino, excesso,
linhas, colunas e possibilidade de quebra entre palavras. O resumo agrupa as
restrições simultâneas; não some os motivos como se fossem itens distintos.

Nas propostas remanescentes há 69 excessos de bytes e 49 casos em que a quebra
automática não cabe no limite original de colunas. Esses grupos se sobrepõem.
O registro percentual continua bloqueado pela política, mesmo que seu orçamento
caiba. O diagnóstico nunca autoriza edição nem comprova adequação semântica,
largura em pixels ou segurança dos consumidores.

## Como testar

Abra **Iniciar-Teste.cmd**, que usa:

`work/interface-v019/MetalSaga-ptbr-interface-v019.iso`

Durante uma partida normal, confira descrições disponíveis no inventário,
equipamentos, lojas e habilidades: acentos, quebras, leitura e efeitos descritos.
Prefira inicialização limpa, sem restaurar estado de uma ISO anterior. Não é
necessário obter todos os itens imediatamente. O Codex não executou navegação
no PCSX2 nesta rodada; a conferência visual fica com o usuário.

Reprodução e testes:

```powershell
python tools/build_translation_pilot.py --draft translations/regiao-inicial-v030.json --interface-draft translations/interface-v019.json --output work/interface-reproducao-v019 --compact-output --build-iso
python -m unittest discover -s tests -p "test_interface*.py" -v
```

`Preparar-Interface.cmd` valida a receita atual sem gerar outra ISO. A construção
consolidada tem somente ISO e relatório; receita e evidências próprias ficam no
Git. Mantêm-se cinco ISOs de trabalho, além da alpha permanente fora da fila.
Originais, BIOS, saves e recursos gráficos aprovados são preservados.

## Próximo trabalho

As pendências difíceis continuam concentradas em nomes longos, categorias e
efeitos que não admitem encurtamento adequado. Antes de redistribuir o pool,
é necessário provar referências e limites dos consumidores. Não reduzir a
qualidade nem liberar `80%%` para aumentar a contagem. Continuar também a
investigação das lacunas de interface já registradas: composição `%screased`,
contexto de Coat e comandos TITLE/BACK. Fragmentos MAP permanecem posteriores.

Resultados de testes, comparação integral da imagem, hash e retenção ficam no
relatório único **reports/interface-v019.json**. Verificação binária não equivale
a teste visual ou a descoberta de todos os textos do jogo.

## Validações executadas

- **117 testes de interface** passaram em 240,546 s, incluindo seis novos de
  revisão e diagnóstico. Mais seis de planejamento, cinco de retenção e três de
  alpha: **131 testes distintos** aprovados.
- Preservação integral da v018 e dos 71 adiamentos remanescentes; reprodução da
  receita a partir dos alvos versionados, sem depender dos rascunhos de work/.
- Leitura de volta dos 567 alvos e round-trip reverso do recurso; rejeição de
  retomadas sem autorização explícita no preparador. O diagnóstico distingue
  caracteres de bytes e não libera fontes, controles ou espaço adicional.
- Comparação integral v018→v019: **4.702 bytes diferentes em 142 intervalos
  autorizados**. Diretório ISO, demais bytes, diálogos, arte, fontes, referências
  e registros de itens idênticos à v018.
- ISO de **1.704.427.520 bytes**, SHA-256
  `0222ef2d46e7a3d4a8912297d725acf0f61d74b14be8d0a0a49d7dfa10f8a93f`.
- Retenção de cinco imagens de trabalho e alpha conferida por hash/somente
  leitura. Nenhum teste visual no PCSX2 ou envio ao OneDrive nesta rodada.
