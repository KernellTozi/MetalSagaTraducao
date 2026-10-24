# Interface v017 — descrições de equipamentos e organização

Acrescenta **114 descrições**, usadas por **126 IDs de itens**, sobre a v016
integralmente preservada. Total de interface: **1.153 campos/ocorrências**.
Inclui armas pessoais, equipamentos de cães, proteção de cabeça, tronco, braços,
pés e acessórios defensivos. Nomes, atributos, preços e efeitos binários intactos.

Foram revisadas 175 descrições distintas: 114 aplicadas e **61 adiadas** por
orçamento de bytes ou colunas/linhas. As 392 restantes do catálogo não foram
revisadas nesta etapa. Propostas adiadas, IDs, hashes e motivos ficam no mesmo
`translations/interface-v017.json`, em `description_review`, sem entrar na
compilação. Não remover acentos, efeitos, artigos ou nomes para forçar espaço.
Adiamento por espaço não é falha de execução observada.

## Estrutura e evidências

Política `spack-item-description-original-slots-v001`, em `tools/item_descriptions.py`.
O bloco contém **strings NUL de tamanho variável**, não slots de 64 bytes.
A tabela em 0x37070 também não foi confundida com os registros deste lote.

| Recurso S_PACK | Origem comprovada |
|---|---|
| SDA pai | raiz entrada 0 → 0x800, cinco entradas |
| Itens | entrada 0 → 0x820, 1.349 registros de 128 bytes |
| Pool de descrições | entrada 1 → 0x2AAA0, tamanho 0x4EC0 (20.160 bytes) |
| Referência | u32 em item +24; FFFFFFFF indica ausência no caminho observado |

São 927 referências para 567 offsets distintos de descrição. Referências
compartilhadas permanecem compartilhadas. Validar limites, NULs e ausência de
aliases interiores. Este catálogo não prova descoberta de todas as tabelas do jogo.

Evidências, com ELF inteiro e janelas vinculadas por hash:

- `0x6CDA0..0x6CDAC`: encaminha SDA ao inicializador VA 0x16FA68, com estado em
  VA 0x475ADC.
- `0x70A68..0x70B98`: número de itens pela diferença de offsets/128, alocação e
  cópias dos blocos. Cópia de itens em `0x70B74..0x70B84`, descrições em
  `0x70B88..0x70B98`. Ponteiros VA 0x475AE8 (itens) e 0x475AEC (descrições).
  Não foi executado o alocador/copiador completo.
- `0x118CB4..0x118CD0`: lê referência +24, compara com -1 e soma à base do pool,
  encaminhando texto ao consumidor VA 0x20D608. O probe executa somente
  `0x118CC4..0x118CD0`, com base/offset em memória sintética, parando antes do
  consumidor. Não executa a escolha do item nem o menu inteiro.

Os getters SDA e o contador original de comprimento também são executados nos
probes existentes. Não executam PCSX2, GPU, I/O ou renderização.

## Reinserção e integridade

Cada tradução usa só o comprimento original e seu NUL. Sobras viram zeros
dentro desse intervalo. Nenhum offset ou registro de item é alterado; pool,
arquivo, extents e todos os nomes permanecem intactos. Preservar linhas,
máximo de caracteres por linha e números. Colunas não são medição de pixels.

Usar extensão GFI PT-BR com round-trip Unicode/bytes, não CP932 padrão.
Bytes nativos, variáveis e novos controles são bloqueados. Preservar dano,
alcance, alvos e características; casos difíceis ficam adiados. Hashes de
arquivo/pool/texto e de todos os itens que compartilham a descrição vinculam
IDs, nomes e atributos. Não liberar outros recursos por semelhança.

## Testar e reproduzir

Abra **Iniciar-Teste.cmd**, para
`work/interface-v017/MetalSaga-ptbr-interface-v017.iso`. Em inicialização limpa,
confira descrições no inventário/equipamento e nas lojas acessíveis. Observar
acentos, quebras, bordas e manutenção do nome/atributos. Há descrições ainda
em inglês. Não é necessário atingir todos os itens imediatamente.

```powershell
python tools/build_translation_pilot.py --draft translations/regiao-inicial-v030.json --interface-draft translations/interface-v017.json --output work/interface-reproducao-v017 --compact-output --build-iso
python -m unittest discover -s tests -p "test_interface*.py" -v
python -m unittest discover -s tests -p "test_iso_retention.py" -v
```

## Limpeza solicitada

Cinco iniciadores na raiz: Iniciar-Teste, Preparar-Interface, Extrair-Dialogos,
Reinserir-Dialogos e Auditar-Traducao. Dez atalhos duplicados/experimentais
apagados; ferramentas, receitas e documentação histórica preservadas.

O limite cai de dez para cinco ISOs de trabalho. As cinco mais antigas foram
apagadas imediatamente; a construção v017 substitui mais uma na mesma fila.
Alpha em dist/, originais, BIOS, saves, anexos, ativos gráficos aprovados e
dependências locais preservados. Não apagar work/ indiscriminadamente: contém
recursos necessários à reprodução. Nenhuma cópia OneDrive ou execução PCSX2.

## Validação executada

- 103 testes de interface passaram em 293,475 s. Os sete do perfil novo foram
  reconferidos após consolidar os vínculos de nomes por hash. Passaram também
  seis de planejamento, cinco de retenção e três de alpha: **117 testes distintos**.
- Os 567 offsets distintos foram conferidos pelo trecho original de encaminhamento
  e pelo contador de bytes limitado, com leitura de volta das traduções. Testes
  recusam IDs, hashes, referências interiores, nomes/dados alterados, controles,
  números diferentes, crescimento e violações de linhas/colunas. Reversão binária
  recupera o S_PACK original integralmente.
- Comparação integral v016→v017: **4.125 bytes alterados em 114 intervalos**,
  somente nas descrições autorizadas. Diretório ISO e todos os demais bytes
  permanecem idênticos, incluindo MAP, fontes e arte aprovada.
- ISO de 1.704.427.520 bytes, SHA-256
  `662554b0edb01cf0627a0af126a2fbfab7be14a5689d92486ba1bbf886ab954d`.
- Só ISO e relatório na pasta da construção; cinco ISOs de trabalho ao final.
  Iniciador conferido sem abrir PCSX2. Alpha conferida por hash e somente leitura.
  A validação visual continua pendente. Resumo e limpeza no único
  `reports/interface-v017.json`.
