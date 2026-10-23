# Pacote de texturas de interface — transporte sem perda

Ferramenta local: `tools/interface_texture_pack.py`, política
`six-textures-original-palette-v002`. Requer Pillow, já disponível na instalação
local em `work/python-deps`. Não usa IA, APIs, quantização ou fontes externas.

Escopo: entradas 0, 1 e 2 de FBS_DATA.SDA e F_COMMON.SDA, já inspecionadas na
primeira investigação de interface. Não generalizar para outras texturas, layouts,
paletas ou para RTITLE.SDA. A ferramenta anterior `interface_textures.py` continua
disponível para seus previews RGB históricos.

```powershell
python tools/interface_texture_pack.py export --output work/texturas-pacote-novo
python tools/interface_texture_pack.py import --pack work/texturas-pacote-novo --output work/texturas-reconstruidas-novas
```

São sempre diretórios novos sob work/. Os originais não são escritos e nenhuma ISO
é alterada. Manifesto e PNGs ficam fora do Git. O importador produz cópias dos dois
SDA e um relatório de readback/round-trip, somente após validar o pacote completo.

Os PNGs usam **modo P, com índices e paleta originais**. Não converter para RGB/RGBA,
redimensionar, otimizar/reordenar cores nem mudar transparência. Somente os índices
dos pixels podem mudar. O manifesto é comparado ao catálogo reconstruído do
original: não pode autorizar outros caminhos, offsets, entradas ou dimensões.

O alpha é transportado como bytes crus da paleta original. Um editor comum pode
mostrar opacidade diferente da do PS2; isso não autoriza normalizar alpha. O
round-trip preserva esses bytes integralmente. O header, paleta, dados posteriores
aos pixels, índices do SDA e entradas não selecionadas permanecem intactos.
Nos dados 4 bpp, o nibble baixo vem primeiro; para um número ímpar de pixels,
o nibble alto não utilizado também é preservado.

Foram executados testes com as seis imagens reais sem edição, com mudança
controlada de um pixel e com rejeição de paleta/alpha/modo/dimensão/manifesto
alterados. A edição de um pixel mudou somente um byte de índice esperado. O
transporte não comprova recortes/UVs do renderizador, não faz tradução automática
nem valida o aspecto dos rótulos no jogo. O próximo trabalho é mapear esses
recortes e preparar os desenhos PT-BR preservando MAIN/SUB/SE.

Pacote pronto nesta rodada: `work/interface-textures-v002/`.
Reconstrução comprovada: `work/interface-textures-v002-roundtrip/`.
Metadados próprios: `reports/interface-textures-v002-roundtrip.json`.
