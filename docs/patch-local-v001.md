# Patch local da tradução — formato v001

Foi gerado e verificado um pacote da **interface v054 / MAP v044 / layout v005**:

`work/entrega/MetalSaga-ptbr-v054.mspatch`

Tamanho: **872.465 bytes** (aproximadamente 852 KiB).
SHA-256: `9ea80e82776f59c73d59f83e3f79df6d193e713306714b2f7b9fa68d5f097857`.

O pacote foi aplicado a uma cópia da ISO original. O resultado completo de
1.704.427.520 bytes teve exatamente o SHA-256 da v054:
`ebeea1bebd13cf0576c99b9eaf656036d3e23cfe7168aa37b95432e3b448fe5e`.
A cópia temporária foi removida após a verificação; não ficou outra ISO
permanente. Originais e cinco ISOs de trabalho permanecem preservados.

É um formato próprio do projeto; **não é xdelta, IPS nem BPS**. A aplicação
usa o script Python abaixo, inteiramente local e sem dependências externas.
O pacote foi preparado somente localmente: não foi publicado nem copiado
ao OneDrive. Scripts, testes e metadados próprios podem ser versionados;
o pacote derivado permanece fora do Git.

## Gerar novamente

Criar primeiro a pasta de saída. O comando usa a ISO atual do iniciador,
confere o relatório da construção e recusa transações pendentes. A origem
padrão é JOGO/Metal Saga.iso, cujo SHA-256 exigido é
`ef8405bf9e34bffd7846bcf3386a73464864823e20cd46ee9dacec514028b403`.

```powershell
python tools/translation_patch.py create --output work/entrega/outro-pacote.mspatch
```

O nome de saída precisa ser novo. Nenhum pacote existente é substituído.
Para selecionar uma construção anterior, passar `--image` com a ISO e seu
relatório válido. Usar `--original` somente para uma cópia da revisão original
exigida; o gerador confere o hash integral.

## Aplicar

Em uma cópia local do projeto, com Python disponível:

```powershell
python tools/translation_patch.py apply --original "JOGO/Metal Saga.iso" --patch "work/entrega/MetalSaga-ptbr-v054.mspatch" --output "work/entrega/MetalSaga-ptbr-v054-recriada.iso"
```

A ferramenta recusa sobrescrever qualquer arquivo, inclusive a origem.
Primeiro valida o manifesto e o hash integral da ISO original; reconstrói
em um arquivo temporário; confere todo o resultado antes de publicá-lo no
caminho escolhido. Erros removem somente o temporário criado pela operação.
A origem não é aberta para gravação.

Ao aplicar pela CLI em uma saída .iso dentro de work/, a retenção existente
reserva uma vaga entre as cinco ISOs apenas depois da reconstrução validada.
Não pode apagar a entrada dessa aplicação; alpha e originais ficam protegidos.
Essa operação cria uma cópia para uso manual: não troca o iniciador principal
nem gera um relatório de compilação que se passaria por uma nova construção.

## Formato e validações

ZIP com exatamente `manifest.json` e `delta.bin`, sem extrair caminhos do
arquivo. O manifesto vincula formato, tamanho igual de origem/destino, páginas
de 4.096 bytes, quantidade de intervalos e SHA-256 de origem, destino e delta.
Cada intervalo contém offset uint64, tamanho uint32 e bytes da página alterada;
os intervalos são ordenados, alinhados, não sobrepostos e limitados à imagem.
Na v054 são 974 páginas, somando 3.989.504 bytes antes da compressão.

A análise usa blocos de 1 MiB e páginas, com memória limitada, sem carregar a
ISO inteira. Não executa código do pacote. Rejeita entradas extras, caminhos
ZIP, campos duplicados, contagens booleanas, limites inválidos, truncamentos,
intervalos sobrepostos, delta corrompido e resultado com hash incorreto.

Testes unitários e o round-trip integral estão documentados em
reports/patch-local-v001.json. Esse teste comprova reconstrução binária;
não substitui uma partida no PCSX2 nem torna a v054 uma versão final aprovada.
