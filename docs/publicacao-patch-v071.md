# Patch público v071

Pacote: `dist/publicacao-v071/MetalSaga-PTBR-v071-Patch.zip`.
Tamanho: 1.251.101 bytes (cerca de 1,19 MiB).
SHA-256 do ZIP:
`6386708773d5ba63719aa055f9fb78201ee3edc45305a1a847c401ba83e5c573`.

Inclui as correções de uso de itens, montanhas e ajuda documentadas em
`docs/interface-v071.md`, além do conteúdo herdado da v070. Continua candidata
para revisão em partida, sem alegação de cobertura total ou aprovação visual
de todas as telas. Os 13 rótulos curtos de falantes permanecem bloqueados.

## Aplicação pelo jogador

1. Extraia todos os arquivos do ZIP.
2. Abra `Aplicar-Patch.cmd` e escolha a ISO original americana de Metal Saga,
   serial SLUS-21293. Também pode arrastá-la sobre o iniciador.
3. Aguarde a criação de `MetalSaga-PTBR-v071.iso` na pasta da original;
   reserve pelo menos 2 GB livres.
4. Abra a nova ISO no PCSX2.

Não aplique sobre tradução anterior, CHD ou imagem modificada. O pacote
funciona offline no Windows 11 x64, sem Python. Recusa saída existente,
preserva arquivos parciais preexistentes e verifica o resultado antes de
entregá-lo. Não modifica a ISO original.

## Identificação e verificações

Origem e resultado têm 1.704.427.520 bytes.

| Imagem | SHA-256 |
|---|---|
| Original exigida | `ef8405bf9e34bffd7846bcf3386a73464864823e20cd46ee9dacec514028b403` |
| Traduzida v071 | `3365db67d5feebd4795a1b5b706724c84d0982da30b5b6fd6993b6f3b52e11cf` |

Delta: 1.411.069 bytes; SHA-256
`0645b5251d8efe2dbb0b02f1b38ca4454336d71a2cc6cffa807b4e8d61779e49`.
O construtor conferiu a origem, target, arquivo oficial do xdelta, decoder,
delta, ZIP e reconstrução completa. O aplicador PowerShell incluído também
reconstruiu a ISO real com hash idêntico; a imagem temporária foi removida.
Sete testes negativos passaram (tamanho/hash incorreto, saída/partial
existentes, delta adulterado, destino igual à origem e escape do manifesto).
Evidência: `reports/patch-interface-v071.json`.

## Reprodução e distribuição

```powershell
python tools/build_public_patch.py --build-dir work/interface-v071 --cache work/publicacao-v070 --output dist/publicacao-v071
python -m unittest discover -s tests -p test_public_patch_applier.py -v
```

A saída deve ser uma pasta nova. O cache oficial já conferido é reutilizado.
Xdelta 3.2.2, VCDIFF com `-a -A= -S none`, decoder oficial Apache-2.0;
licenças das dependências acompanham o ZIP. Procedimento e referências
históricas em `docs/publicacao-patch-v070.md`.

Compartilhe somente o ZIP do patch: contém delta, aplicadores, decoder,
manifesto, instruções e licenças, sem ISO, BIOS, saves ou recursos originais.
Não houve upload automático a sites/Releases. ZIP e binários ficam fora do
Git; ferramentas e documentos próprios são versionados. As cópias de
manutenção e da Área de Trabalho continuam v070.
