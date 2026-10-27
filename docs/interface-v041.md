# Interface v041 — seis botões de pintura

Em 26/10/2026 o usuário pediu trabalhar nos botões enquanto revisa os itens e
aprovou manter os desenhos apresentados: “pintura não é realmente importante,
então pode manter o desenho apresentado”. A evidência de aprovação da arte
está em `reports/pintura-graficos-aprovacao-v001.json`, vinculada à comparação
e ao hash dos pixels aprovados. Isso não é validação da execução no PCSX2.

## Escopo aplicado

`translations/interface-v041.json` herda integralmente a v040 e acrescenta
somente os seis rótulos revisados da textura principal de pintura:

| Original | Tradução |
| --- | --- |
| Edit | Editar |
| Vehicle | Veículo |
| Tools | Ferramentas |
| Stamp Select | Escolher carimbo |
| Stamp Edit | Editar carimbo |
| Palette | Paleta |

Sem nova rodada de desenho ou alterações nas máscaras já apresentadas. Corpo
de 16 pixels, linha de base comum e paleta original permanecem iguais à
proposta. Os demais seis recortes do pacote continuam originais: misto
Chassis/Main, Zoom, Sub Gun, SE, legenda de componente e botão decorado de
carimbo. MAIN/SUB/SE não recebem alterações de pixels. O usuário indicou baixa
prioridade para refinamentos de pintura; não ampliar esta rodada para eles.

Total acumulado: **3.811 campos de interface**, seis a mais que v040. Diálogos
MAP v037, fontes/layout v005, arte inicial v014, Carregando e créditos são
preservados. Pôsteres wanted e títulos de minijogos continuam intocados.

## Política de edição

`tools/paint_menu_graphics.py` implementa o opt-in
`paint-six-reviewed-main-menu-buttons-v001`. Ele gera os rasters a partir
do mesmo código da proposta e exige o hash aprovado do plano de pixels:
`76c68dc7cf4ea9eaed43dddeabc5010637578b7db9a6ed7826f3c2c4aacdd16c`.
Não depende dos PNGs locais para reconstruir a arte.

O patch contém somente o plano de pixels da textura 13 de S_PAINT:
**offset 0x34770, tamanho 0x20000**. Cada diferença de índice precisa estar
no interior de um dos seis retângulos explícitos, mantendo suas bordas de
dois pixels. Cabeçalho, paleta/alpha, GANM, hotspot, estruturas SDA e demais
recursos não mudam. O round-trip restitui os bytes originais.

A receita vincula fonte/ELF, janelas e tabela de carregamento, aprovação,
identidades dos seis rótulos, traduções, geometria e hashes das máscaras e
dos recortes. Mudanças, omissões, duplicatas ou raster divergente são recusados.
A política antiga de pacotes locais continua sem integração automática.

Os oito encaminhamentos originais de textura/GANM foram executados novamente
nos limites já documentados em `docs/pintura-graficos-proposta-v001.md`.
Isso não executa dispatch completo, upload, GPU ou PCSX2. O resultado em jogo
permanece para teste manual periódico do usuário.

## Proteção das legendas e da auditoria de itens

As **228 legendas de pintura** traduzidas anteriormente são compiladas como
patches separados em 0xAE6A0. Não se importa um S_PAINT inteiro baseado no
original, o que apagaria essas traduções. O teste compõe arte+legendas em
memória, confere todos os intervalos e reverte até o original exato.

Todos os nomes, propostas, adiamentos e decisões dos itens são idênticos à
v040. A lista que o usuário está revisando permanece válida. **Não regenerar
nem sobrescrever** `work/auditoria-itens-v040/`; os arquivos podem estar sendo
anotados pelo usuário. Nenhuma escolha editorial foi aplicada nesta rodada.

## Reprodução e teste visual

```powershell
python tools/build_translation_pilot.py --draft translations/regiao-inicial-v037.json --interface-draft translations/interface-v041.json --compact-output --build-iso --output work/minha-v041
python -m unittest discover -s tests -p test_paint_menu_graphics.py
```

Construir em pasta nova. Iniciar-Teste.cmd/alias interface aponta para a v041
somente depois da comparação integral concluída. Preparar-Interface.cmd
valida o lote correspondente. ISO:
`work/interface-v041/MetalSaga-ptbr-interface-v041.iso`.

Ao chegar à pintura, observar os seis rótulos, posição, recorte e legibilidade,
inclusive o í de Veículo, além das legendas e rótulos protegidos. Não é
necessário repetir a navegação automaticamente ou alcançar a cena agora.

Relatórios de construção e comparação:
`reports/interface-v041.json` e `reports/interface-v041-delta.json`.
Preservar limite de cinco ISOs de trabalho e alpha fora da retenção.

## Resultado de integridade

Passaram **47 testes distintos**, sete novos. Comparação integral v040→v041:
**5.288 bytes diferentes**, exclusivamente no plano de pixels autorizado.
Diretório ISO e todos os demais bytes idênticos, incluindo o S_PACK completo
com os nomes de itens da auditoria e as legendas de pintura em S_PAINT.
Preflight da nova imagem aprovado: 1.704.427.520 bytes, SHA-256
`a0baac76fc34b299be98c0f5618fc64b914e53a3b3ef7246faaf09aee57645ca`.
Cinco ISOs de trabalho e hash da alpha conferidos. Sem navegação PCSX2,
OneDrive ou desligamento nesta rodada. O iniciador passou para v041 somente
após concluir essa comparação.
