# Interface v021 — cinco frentes e mensagens do sistema

Uma única imagem consolida **285 campos/ocorrências novos**, preservando as
traduções aprovadas da v020, MAP v030, layout/fontes v005 e arte v014.
Total de interface: **2.057 campos/ocorrências**. Essas contagens não medem a
porcentagem de todo o jogo.

| Frente de nomes | Novos registros |
|---|---:|
| Equipamentos genéricos | 37 |
| Consumíveis e materiais | 105 |
| Móveis e acessórios | 56 |
| Habilidades | 51 |
| Objetos genéricos de missão/recompensa | 19 |
| **Subtotal de nomes** | **268** |
| Mensagens do sistema de instalação | **17** |

São **457 registros de nomes traduzidos**, com **442 rótulos PT-BR distintos**.
Ocorrências compartilhadas continuam iguais. Exemplos novos: Capacete de obra,
Casaco antifogo, Antídoto, Cápsula de cura, Arroz, Pó de ouro, Sucata metálica,
Relógio mural, Guarda-pó, Golpe giratório e Concentração.

Os 189 registros de nomes aprovados na v020 permanecem idênticos, inclusive
seus patches. Nomes próprios, armas humanas, motores/C Units, LOVE machine,
componentes únicos e aliases protegidos não foram traduzidos por conveniência.
As descrições permanecem em **536/567**, compartilhadas por 883 IDs. Não houve
repack do pool de descrições nem liberação de controles MAP ou do `80%%`.

## Perfil explícito de nomes: teto observado de 16 bytes

`spack-reviewed-generic-names-observed-ceiling-v002` é opt-in e separado do
perfil histórico `spack-reviewed-generic-item-names-original-slots-v001`.
Receitas antigas mantêm o limite de cada nome original. Não alterar seus defaults.

A fonte imutável contém **1.349 registros ×128**, com nomes NUL antes de +24,
em S_PACK **0x820**. O maior nome tem **16 bytes**, testemunhado pelo ID **954**.
Todos os bytes entre o NUL original e +24 foram conferidos como zero. A v002
permite usar somente esse preenchimento do próprio registro, com alvo de no
máximo **16 bytes mais NUL**. Os bytes **+17..+127** permanecem intactos em todos
os registros; nenhuma referência, atributo, tamanho de arquivo ou extent muda.
Não se concede toda a janela de 24 bytes, nem espaço de outro nome.

Dos 268 registros novos, **264** usam parte do preenchimento original. As
origens ocupam 2.767 bytes e os alvos 3.537; o aumento fica distribuído nas
próprias áreas zeradas. Isso não aumenta S_PACK ou a ISO.

As evidências adicionais, vinculadas por hash, são:

- **0x1B34EC..0x1B3504:** o mesmo caminho genérico calcula base + ID×128 e
  encaminha o nome para VA **0x2967C8** (arquivo **0x1977C8**). Não há nesse
  trecho um limite dependente do comprimento anterior daquele nome ou do ID.
  O encaminhamento foi executado para todos os 1.349 índices em RAM sintética.
- **0x1977C8..0x197858:** preparação da formatação, com área temporária de
  0x1000 bytes antes dos registradores salvos. O formatador não foi executado.
- **0x197858..0x197910:** percorre caracteres até NUL, com caminhos de um ou
  dois bytes e encaminhamento ao desenhador. Não há nesse trecho corte no
  comprimento anterior do nome. A inspeção não executa GPU ou todos os chamadores.

O teto continua sendo o maior comprimento de nome já presente no original,
não uma declaração de capacidade universal. A largura em pixels depende das
letras e do contexto; essa expansão exige teste visual consolidado. Não liberar
17..23 bytes, controles, nomes protegidos ou outras regiões por semelhança.

## Pendências de nomes: histórico e diagnóstico atual

Das **505 ocorrências selecionadas**, 457 estão aprovadas, **47 permanecem
pendentes** e uma foi preservada por categoria protegida. A seleção não é o
catálogo completo de nomes a traduzir: muitos dos 1.041 nomes não vazios devem
continuar em inglês por regra do usuário.

Os adiamentos anteriores que não foram retomados mantêm suas propostas,
motivos e hashes históricos. O planejador acrescenta um diagnóstico atual
separado, sem apagar essa evidência e sem promover candidatos automaticamente:

| Primeira restrição atual da proposta arquivada | Ocorrências |
|---|---:|
| Orçamento/controles de nome | 37 |
| Glifos maiúsculos ainda ausentes (`Ó`, `Í`) | 2 |
| Proteções nominais de Repair Kit, Fang e Bus Stop Sign | 4 |
| Passa nas guardas individuais, mas exige revisão editorial/aliases | 4 |

Uma primeira recusa pode esconder outras restrições. Os quatro que passam na
guarda individual continuam pendentes: Sugar Pill, Dance Earrings, Dance Shoes
e Grenade Gun. Não usar esse resultado como aprovação de redação ou de todos
os aliases; a ocorrência de Grenade Gun entre armas humanas continua protegida.
Nenhuma exceção global foi criada para homônimos ou nomes do glossário.

## Entrada 12 de NDATA: 17 mensagens de instalação

Política específica **ndata-install-crlf-original-loaded-region-v001**, em
`tools/install_texts.py`. Traduz ausência/erro de HDD, espaço necessário,
confirmação, andamento, conclusão, cancelamento e recuperação de instalação,
com **Sim/Não** e os avisos de não desligar o console ou abrir a bandeja.
O trabalho modifica textos, sem instalar o jogo, formatar HDD, ativar recursos
do emulador ou alterar configurações.

Origem: NDATA entrada **12**, offset **0x96800**, leitura original de **875 bytes**
(`0x36B`), com **17 registros CRLF**. O extent da entrada tem 2.048 bytes, mas
essa sobra não foi liberada. A tradução usa **804 bytes** e preenche com NUL
somente o restante da leitura original. O descritor e o padding externo ficam
intactos. O perfil legado de recursos continua rejeitando a tabela 12.

Evidências do ELF original:

- Descritor em **0x348ED0**, par **0x96800 / 0x36B**.
- **0xBD8B4..0xBD914:** copia o descritor, chama a leitura em VA 0x195968
  (arquivo **0x96968**) e encaminha o resultado ao parser em VA 0x194B10
  (arquivo **0x95B10**), o leitor CRLF já vinculado por hash.
- **0xBEEC4..0xBEEEC:** prepara o tamanho e chama o substituidor em VA 0x194E50
  (arquivo **0x95E50**), com o literal **%INSTALLSIZE%** em **0x3208A0**.
  O token é mantido nas duas ocorrências, com a mesma ordem de pipes.

O contador original foi executado sobre o payload modificado e retornou 17.
Mantêm-se a ordem dos registros, os tokens, os números e o limite conservador
de 511 bytes por registro do leitor comum. Colunas ficam no máximo observado
da própria tabela; escolhas CRLF variáveis não são slots de dois bytes só
porque a palavra inglesa `No` tinha duas letras. Isso não comprova largura em
pixels, execução do substituidor completo ou funcionamento de uma instalação.

## Nomeação e lacunas preservadas

TITLE/BACK continuam sem tradução por falta de conclusão segura sobre a ação
dos comandos. A investigação acompanhou o construtor da tela em **0x10AB40**,
a tabela virtual em **0x3061C8** e rotinas ligadas, sem liberar semântica a partir
de nomes ou botões presumidos. Não chamar o rótulo TITLE de caixa/título/voltar
por adivinhação. Coat também permanece pendente. Não foram redesenhadas fontes
ou texturas nesta rodada.

## Uso e reprodução local

Abra **Iniciar-Teste.cmd**. Imagem consolidada:

`work/interface-v021/MetalSaga-ptbr-interface-v021.iso`

Em partida normal, conferir listas de equipamentos, inventário/lojas, móveis,
habilidades e objetos: acentos, nomes inteiros, alinhamento, seleção e efeitos
inalterados. Não é necessário obter cada item nem realizar instalação de HDD
para continuar o projeto. O usuário faz a conferência visual; não houve
navegação do PCSX2 pelo agente.

```powershell
python tools/plan_interface_menus.py
python tools/build_translation_pilot.py --draft translations/regiao-inicial-v030.json --interface-draft translations/interface-v021.json --output work/interface-reproducao-v021 --compact-output --build-iso
python -m unittest discover -s tests -p "test_interface*.py" -v
```

O planejador reutiliza **work/planejamento-interface.json**, incluindo os nomes,
motivos históricos, diagnóstico atual e 17 mensagens novas. Ferramentas binárias
locais, sem IA/APIs/rede. A receita contém traduções e metadados próprios; textos
originais exportados e binários continuam fora do Git.

Uma ISO e um relatório de construção. Manter cinco ISOs de trabalho, além da
alpha permanente protegida. OneDrive e desligamento somente por novo pedido.
Evidências, integridade e testes finais em **reports/interface-v021.json**.

## Validações executadas

- **153 testes de interface** passaram em 307,139 s na receita final, além de
  seis de planejamento, cinco de retenção e três de alpha: **167 testes
  distintos**. A execução preliminar não foi somada novamente à contagem.
- Getter de registros e encaminhamento genérico de nomes conferidos para todos
  os **1.349 índices**, leitura de volta e round-trip, nomes repetidos coerentes,
  recusa de padding não zero, glifos inválidos, controles e tetos não autorizados.
- Todos os patches anteriores, inclusive os 189 nomes da v020, continuam
  idênticos; atributos, offsets de descrição e os bytes +17..+127 foram conferidos
  em todos os registros. Perfis históricos continuam recusando crescimento.
- NDATA: 17 registros, token preservado, contador original, leitura de volta,
  descritor e padding externo imutáveis. Nenhuma operação de HDD foi executada.
- Auditoria das traduções canônicas de diálogos após resolver a herança da v030:
  416 rótulos ingleses exatos de pelo menos seis bytes, com caixa ignorada e
  espaços normalizados, em 5.183 segmentos; nenhuma ocorrência encontrada.
  Isso não resolve contexto, flexões, sinônimos ou reutilizações por alias.
- Comparação integral v020→v021: **4.103 bytes diferentes em 269 intervalos
  autorizados**; demais bytes e diretório ISO idênticos. Os 17 campos NDATA
  compõem um único intervalo, por isso campos e patches têm contagens diferentes.
- ISO de **1.704.427.520 bytes**, SHA-256
  `9aeb41ee8f1452bc24e65ac0a0c50aae5a659a66e15c5ecd9ef28ca6b3934a43`.
- Iniciador conferido sem abrir PCSX2; cinco imagens de trabalho e alpha
  preservada. O teste visual da expansão de nomes permanece pendente do usuário.
