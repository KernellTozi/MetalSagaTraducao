# Fontes dos nomes dinâmicos — investigação v005

Investigação somente leitura sobre interface v052/MAP v044, layout v005.
Não houve nova tradução, liberação de nomes, nova ISO ou execução no PCSX2.

## Resultado concreto

O objetivo era fechar as entradas que faltavam antes de ampliar seis nomes.
Foram identificados os métodos de duas classes de cena, a inicialização da
tabela N e um formatador adicional que também consulta itens. Isso aproxima
a investigação das origens reais, mas ainda não basta para liberar o lote.

### Nomes de objetos de cena: retorno virtual conhecido

Os construtores em arquivo 0x798B8 e 0x79EC8 atribuem tipos 2 e 3 e vtables
0x4041F0 e 0x404198. O descritor virtual em +0x48/+0x4C tem ajuste zero e
aponta respectivamente para 0x79EB8 e 0x7A3B0. Ambos retornam objeto+0x3C.

Os finais de preenchimento em **0x79A18..0x79A20** e
**0x7A028..0x7A030** guardam o payload em objeto+0x3C e escrevem NUL em
payload+**0x21/33**. O novo teste executa essas duas instruções e os getters,
conferindo ponteiro e preservação dos outros bytes. Não executa a limpeza
anterior, o setter inteiro, alocador ou todo o ciclo de vida.

Portanto, nesses caminhos há **até 33 bytes antes do terminador forçado**.
Isso não é limite de caracteres, não exclui outras escritas posteriores nem
resolve todos os subclasses/retornos virtuais da chamada 0x473C8.

### A tabela N vem de outra estrutura

A rotina original **0x1784AC..0x178520** foi executada com pools sintéticos,
incluindo chamadas virtuais reais e seus delay slots. Grava exatamente **39
ponteiros**, em 0x47558C + 4×índice, preservando as regiões vizinhas:

| Índices inicializados | Objetos | Stride | Getter original |
|---|---:|---:|---|
| 0..9 | 10, construtor com tipo 13 | 0x240 | 0x7F6C0 |
| 10..38 | 29, construtor com tipo 14 | 0x2A0 | 0x827C8 |

Os construtores dos pools aparecem nas chamadas 0x17810C e 0x17815C;
suas vtables são 0x403D50 e 0x403C80. O primeiro getter lê objeto+0x228 e
retorna registro+0x10. O segundo lê objeto+0x290. Nos resets observados,
esses campos apontam para objeto+0x120. Assim, no modelo que reproduz esses
resets, **N0 aponta ao offset 0x130 do primeiro objeto**, e não ao payload
limitado pelo NUL de 33 bytes dos tipos 2/3.

Essa distinção evita uma conclusão incorreta: **o limite de 33 não comprova
o comprimento máximo do nome N0**. Também não se deve inferir identidade
canônica de personagem, nem que o handler recuse todos os índices acima de
38, somente porque este inicializador grava 39 entradas. O conteúdo/nul dos
nomes, carregamento de saves e todas as variantes de registros não foram
executados por essa sonda.

### Outro consumidor de itens confirmado por código

O formatador em **0x10E0E8** também expande referências I e N. O handler I em
0x10E1E8 lê global 0x475280+0x868, equivalente a 0x475AE8, e usa stride 128.
O caminho N em 0x10E19C consulta a tabela já localizada. Copia o resultado
em 0x10E200 e chama strlen em 0x10E20C para avançar o destino.

Há nove chamadas diretas exatas: **0x123F50, 0x123F60, 0x124310, 0x1243BC,
0x1243DC, 0x129474, 0x129684, 0x129754 e 0x12C1F8**. Não são nove novos
diálogos descobertos. São nove caminhos de um consumidor que precisa entrar
na análise de capacidade antes de ampliar nomes globalmente.

Essa parte é evidência estática, vinculada ao ELF e às janelas dos chamadores.
**O formatador adicional não foi executado** e suas capacidades de destino
ainda não foram comprovadas. Não transferir para ele os limites de 128/1.024
bytes ou 99 células das outras rotinas.

## Ferramenta local

```powershell
python tools/name_source_paths.py
python -m unittest discover -s tests -p test_name_source_paths.py
```

Saída substituível: **work/fontes-nomes-atual.json**. Somente biblioteca padrão
e módulos próprios; sem internet, IA ou APIs. Não foi criado mais um .cmd.
Os PCs do executor são virtuais também nos registradores de retorno, evitando
confundir um retorno em offset com um ponteiro de função virtual.

O inicializador é executado com tabelas, objetos e registros fornecidos pelo
teste. As instruções, vtables e getters são do ELF original. Memória não mapeada,
escritas em regiões somente leitura e saída das janelas permitidas são recusadas.
Os construtores, GPU e o funcionamento completo do PS2 não são emulados.

## Próxima execução delimitada

1. Investigar os registros de nome alcançados pelo getter 0x7F6C0, começando
   pelos resets e escrita do campo textual em +0x10. Não aplicar o limite 33
   de outra classe como atalho.
2. Rastrear entradas e separações dos nove chamadores do formatador 0x10E0E8,
   começando pelos destinos de pilha. Os offsets já estão catalogados.
3. Completar as variantes relevantes de 0x473C8. Só então preparar a política
   por ID para os seis itens e as cinco ações. Não repetir o censo 54/190.

Se a capacidade de um caminho continuar incerta, manter a redação humana em
fila. Os testes de 35 páginas anteriores são evidências condicionais úteis,
mas não comprovam esses novos destinos. O lote de nomes não foi promovido.

A versão de teste continua **v052**, pelo mesmo Iniciar-Teste.cmd. Sem nova
ISO, alterações de fonte, OneDrive ou desligamento. Não é necessário teste
manual nesta rodada: não houve mudança no jogo.

## Verificações executadas

**44 testes distintos passaram**, oito novos de proveniência e as regressões
de emissor, buffers e fallback do item 460. Zero falhas, erros ou ignorados.
Não somar reexecuções ou os 39 stores à contagem de unittest. Os compiladores
de produção não foram alterados nesta rodada.

O preflight reconferiu tamanho, hash e ausência de transações da ISO v052:
SHA-256 `26a23155f5fe8e7aa994871c7100e35929f90b59ecd96e1d9a542b8d7079b449`.
Resumo próprio em reports/fontes-nomes-v005.json; resultados detalhados e logs
somente em work/. Validação visual da v052 continua sendo a da partida do usuário.
