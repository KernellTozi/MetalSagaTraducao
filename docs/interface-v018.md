# Interface v018 — lote amplo de descrições

Acrescenta **239 descrições distintas** à v017, preservando integralmente seus
textos, fontes/layout v005, arte v014, correio e diálogos MAP v030. O pool passa
a ter **353 descrições traduzidas**, compartilhadas por **602 IDs de itens**.
São **1.392 campos/ocorrências de interface** acumulados. Não converter esses
números em porcentagem de todo o jogo ou contar aliases como traduções distintas.

## Escopo

Armamento MAIN/SUB/SE, chassis, motores/C Unit, recuperação de HP/SP, alguns
consumíveis, obuses, componentes de montagem, instruções de projetos, objetos
de missão, presentes/móveis e parte das habilidades. Nem todos os textos de
cada grupo couberam. Todos os nomes de itens, tanques, personagens e componentes
únicos continuam intactos, assim como preços, atributos e efeitos binários.

Os 392 alvos que faltavam receberam propostas e revisão inicial no contexto dos
nomes dos itens que os referenciam. Isso encerra a triagem deste catálogo de
567 alvos, sem comprovar todas as tabelas do jogo ou aprovação editorial final:

| Classe | Quantidade |
|---|---:|
| Traduzidos dentro dos slots originais | 353 |
| Adiados por espaço/linhas | 212 |
| Bloqueado pela sintaxe percentual | 1 |
| Marcador `???` revisado e preservado | 1 |
| Ainda não revistos neste pool | 0 |

As 61 propostas adiadas da v017 permanecem preservadas sem retomada nesta rodada.
A v018 acrescenta 152 adiamentos: 151 de espaço e um técnico. Não substituir
sinônimos a ponto de perder alcance, duração, alvos, estados ou condição de uso.
Efeitos de provocar atenção foram distinguidos de aproximar fisicamente um
inimigo. Reparo de peças de veículo continua distinto de reparo genérico.

MAIN/SUB/SE, C Unit, Max Load e nomes únicos citados em componentes/projetos
permanecem literais. HP/SP e números não mudam. Sucata continua sendo o material.
As instruções de uso não traduzem nem renomeiam os equipamentos.

## Políticas e ferramenta local

Continua a política binária **spack-item-description-original-slots-v001**:
pool S_PACK 0x2AAA0/0x4EC0, referências item+24 e registros de 128 bytes em
0x820. Cada campo fica no seu comprimento original com o NUL preservado;
mesma quantidade de linhas e limite conservador de colunas do original.
Não há repack do pool, alteração de referências, expansão de arquivo ou edição
de nomes/atributos. Evidências e limites em `docs/interface-v017.md`.

O campo opt-in **item-description-unique-name-references-v002** acrescenta a
verificação nominal de referências únicas de peças/projetos. O perfil antigo
continua reproduzível, sem ativar retroativamente a nova regra. A verificação
normaliza quebras para reconhecer nomes como Drill Claw divididos entre linhas.

`tools/prepare_item_batch.py` prepara propostas Unicode explícitas, sem traduzir
automaticamente e sem IA/APIs/rede. Trabalha sobre receitas e o original somente
para leitura. Faz quebras só entre palavras; não corta palavras, remove acentos,
comprime fontes ou aplica tradução parcial num binário. O compilador continua
sendo a etapa que decide os patches permitidos.

O ledger **item-review-ledger-v002** verifica IDs/classes sem duplicação,
contagem de aprovados/pendentes/preservados e hashes das fontes. O compilador e
o planejador conferem esse ledger. Propostas recusadas ficam em `description_review`
da mesma receita; não se perde o trabalho nem se espalham arquivos por item.

Por padrão, a ferramenta recusa IDs já revistos. `--resume-deferred` permite
reavaliar somente IDs pendentes explicitamente enviados, sem sobrescrever os
aprovados ou os marcadores preservados. Não significa liberar espaço novo.

Exemplo para uma próxima revisão, criando uma receita nova:

```powershell
python tools/prepare_item_batch.py --parent translations/interface-v018.json --proposals work/itens-propostas.json --output translations/interface-v019.json --version interface-v019 --resume-deferred
```

O JSON de propostas deve mapear IDs exatos a texto Unicode. O exemplo só funciona
com uma seleção nova dos IDs pendentes: a ferramenta recusa a reutilização de
todos os IDs da rodada anterior. Ela também recusa sobrescrever um arquivo de
saída existente. O usuário não precisa executar esse comando para jogar.

## Bloqueio e próximo passo

`item.description.03226` contém `80%%`. A regra atual bloqueia qualquer percentual
neste pool, independentemente de estar permitido em outros consumidores. A
proposta fica arquivada, sem alterar bytes ou liberar o controle por semelhança.
O marcador `???` é mantido como original, sem inventar a função dos itens ligados.

Próximo trabalho: agrupar os 212 casos de espaço por causa e investigar uma
política de reorganização **somente após provar todas as referências e os
limites dos consumidores**. Os buracos deixados por strings curtas não são
automaticamente capacidade autorizada. Alternativa segura: revisão contextual
de redações completas, sem forçar efeitos/nomes ou remover acentos.

## Uso e reprodução

Abra **Iniciar-Teste.cmd**. A imagem consolidada é
`work/interface-v018/MetalSaga-ptbr-interface-v018.iso`. Em inicialização limpa,
confira os textos disponíveis no inventário, lojas, veículo e habilidades.
Observar acentos, quebras, alvos/efeitos e nomes intactos; há descrições ainda
em inglês. Não é necessário obter cada item imediatamente. Teste visual pendente.

```powershell
python tools/build_translation_pilot.py --draft translations/regiao-inicial-v030.json --interface-draft translations/interface-v018.json --output work/interface-reproducao-v018 --compact-output --build-iso
python tools/plan_interface_menus.py
python -m unittest discover -s tests -p "test_interface*.py" -v
```

O planejador reutiliza `work/planejamento-interface.json`, agora distinguindo o
marcador preservado e o bloqueio percentual. Uma ISO e um relatório na pasta da
construção; resumo/evidências/delta no único `reports/interface-v018.json`.
Cinco ISOs de trabalho; alpha, originais, saves e BIOS preservados. Sem OneDrive
ou execução do PCSX2 nesta rodada.

## Validação executada

- **111 testes de interface** passaram em 289,190 s, incluindo os oito do lote
  novo, também reconferidos com os casos nominais finais. Mais seis de planejamento,
  cinco de retenção e três de alpha: **125 testes distintos**.
- Os 567 offsets foram conferidos pelo encaminhamento original e pelo contador
  limitado de bytes. Leitura de volta dos textos e 927 referências, preservação
  das traduções antigas, nomes/atributos, classes disjuntas e hashes; recusa de
  sobrescrita de aprovados e retomada de pendentes sem opção explícita.
- A ferramenta de preparação reproduziu a receita completa em teste a partir
  dos campos versionados e do original, sem o JSON de propostas de work/.
- Delta integral v017→v018: **6.932 bytes em 239 intervalos autorizados**.
  Os demais bytes e o diretório ISO são idênticos. Os novos textos usavam
  7.826 bytes de origem e ocupam 6.932 bytes de destino; não há expansão.
- ISO de 1.704.427.520 bytes, SHA-256
  `88747504295d06b5d49aaaf3b85ab1076bf2d967ccd18d8049e172aee6a1fc49`.
- Cinco ISOs de trabalho e alpha conferida por hash/somente leitura. Iniciador
  conferido sem executar o emulador; teste visual permanece pendente.
