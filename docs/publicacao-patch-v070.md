# Publicação da tradução como patch — v070

Compartilhar o pacote de patch, sem incluir a ISO original ou traduzida.
O destinatário precisa fornecer uma ISO original byte a byte compatível.
Não foi feito upload automático do ZIP nesta entrega.

## Arquivo pronto

`dist/publicacao-v070/MetalSaga-PTBR-v070-Patch.zip`

- ZIP: 1.250.763 bytes, cerca de 1,19 MiB.
- Patch xdelta: 1.410.728 bytes, cerca de 1,35 MiB.
- SHA-256 do ZIP: `3155d6e5c9c633ea5ff93d13cec5d98a9661194a81255ded832a7bfea99ce8d6`.
- Não contém ISO, BIOS, saves, emulador, fontes do jogo ou contêineres originais.
- Inclui patch, iniciador `.cmd`, aplicador PowerShell, manifesto, instruções,
  decoder oficial xdelta3 e suas informações/licenças de terceiros.

O pacote entrega a candidata v070, com as mesmas limitações descritas em
`docs/interface-v070.md`, incluindo os 13 rótulos curtos de falantes ainda
em inglês. Não foi promovida a uma versão visualmente aprovada.

## Como o jogador aplica

1. Extrair todo o ZIP para uma pasta no Windows 11 x64.
2. Abrir `Aplicar-Patch.cmd` e selecionar a ISO original americana.
   Também pode arrastar a ISO para cima do iniciador.
3. Aguardar a criação de `MetalSaga-PTBR-v070.iso` na pasta da original.
   Reservar pelo menos 2 GB livres. A ISO original não é alterada.
4. Abrir a nova ISO no PCSX2.

Não depende de Python, IA, APIs ou internet na máquina do jogador. Para quem
já utiliza uma interface xdelta compatível, o arquivo `.xdelta` também está
no pacote. Não aplicar sobre CHD, outra tradução, modificação ou ISO refeita.
O hash exato é obrigatório, independentemente do nome exibido pelo arquivo.

## Identificação das imagens

Metal Saga, PlayStation 2, USA/NTSC-U, serial SLUS-21293.
Origem e resultado têm 1.704.427.520 bytes cada.

| Imagem | SHA-256 |
|---|---|
| Original exigida | `ef8405bf9e34bffd7846bcf3386a73464864823e20cd46ee9dacec514028b403` |
| Traduzida v070 | `5a576e647291e9255b04856e22dfb5bdaabd4ecbe1ebee751f26e856eb439f4c` |

O aplicador verifica tamanho/hash da origem, hash do patch e decoder, recusa
sobrescrever arquivos existentes e só entrega o resultado depois de conferir
seu hash integral. Um arquivo `.partial` preexistente é preservado, não apagado.
O SHA-256 é uma conferência de integridade, não uma assinatura digital.

## Construção e testes

Ferramenta própria `tools/build_public_patch.py`; aplicadores próprios em
`release/Aplicar-Patch.ps1` e `release/Aplicar-Patch.cmd`. Binários e ZIP ficam
somente em dist/work, fora do Git.

O xdelta3 oficial 3.2.2 para Windows x86-64 foi obtido do release do autor,
com SHA-256 do arquivo conferido contra o digest publicado no GitHub:
`d48f7651d86b78fdca397057b46601f89131f37219675df736db70af44ec3379`.
O decoder é distribuído sem alterações, sob Apache-2.0. Licenças de liblzma
(xz 5.8.3, 0BSD) e BLAKE3 1.8.5 (CC0) acompanham o pacote, conforme as
dependências fixadas no CMake desse release.

Foi usado VCDIFF sem armor, sem nomes de arquivos no cabeçalho e sem
compressão secundária, para compatibilidade com decoders xdelta anteriores.
O ZIP faz a compressão externa do pacote. Comandos equivalentes:

```text
xdelta3 -a -A= -S none -9 -D -e -s Original.iso Traduzida.iso Traducao.xdelta
xdelta3decode -D -R -d -s Original.iso Traducao.xdelta Recriada.iso
```

O construtor valida as duas imagens, faz a reconstrução completa, confere
tamanho/SHA-256 e remove a ISO temporária. O aplicador PowerShell do pacote
também foi executado com a ISO real e reconstruiu exatamente a v070.
Sete testes negativos passaram: origem de tamanho errado, hash errado, saída
existente, `.partial` preexistente, patch adulterado, destino igual à origem
e caminho de manifesto fora da pasta. Fixtures pequenas e isoladas.

Reprodução com cache local dos arquivos oficiais e licenças:

```powershell
python tools/build_public_patch.py --build-dir work/interface-v070 --cache work/publicacao-v070 --output dist/publicacao-v070
python -m unittest discover -s tests -p test_public_patch_applier.py -v
```

Exige diretório de saída novo e preserva metadados históricos. A geração
continua exigindo os originais locais; o pacote público não os fornece.
Evidências em `reports/patch-interface-v070.json`.

## Onde publicar

O ZIP pode ser anexado manualmente a uma Release do repositório autorizado,
com o hash da origem exigida, versão, instruções e limitações. Não anexar
as imagens em work/dist, BIOS ou arquivos originais. O pacote gerado ainda
não foi anexado a uma Release.

Referências técnicas primárias:
- [xdelta3: comandos e compatibilidade](https://github.com/jmacd/xdelta/blob/v3.2.2/site/docs/commandline.md).
- [Binários oficiais 3.2.2](https://github.com/jmacd/xdelta/releases/tag/v3.2.2).
- [Licença xdelta3](https://github.com/jmacd/xdelta/blob/v3.2.2/xdelta3/LICENSE).
