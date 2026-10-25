# Interface v023 — consumíveis e acessórios

Rodada em **duas frentes**, com 16 ocorrências novas e 15 rótulos distintos:

| Frente | IDs e nomes |
|---|---|
| Consumíveis/materiais: 9 | 331 Pílula doce; 352 Bomba de fótons; 354/373 Bomba a gasolina; 355 Granada de raio; 372 Frasco do pavor; 374 Tônico Nitro; 385 Tripa de formiga; 619 Testosterona |
| Móveis/acessórios: 7 | 433 Lenço camuflado; 449 Brincos de baile; 451 Sapato de baile; 727 Tela de paisagem; 747 Ramo de gérbera; 774 Quimono; 782 Collant |

As duas ocorrências de Petrol Bomb compartilham exatamente o mesmo alvo.
As descrições disponíveis foram consultadas: Photon Grenade é um consumível
de feixe, Thunder Grenade é elétrico, o reagente Testosterone é usado na
montagem de peças e a paisagem é decoração de parede. Frasco do pavor e
Tônico Nitro partem do próprio nome; não se infere efeito adicional onde
não existe descrição vinculada. Collant e Quimono são nomes correntes em
português. Não foram modificados efeitos, preços, atributos ou referências.

São **493 registros de nomes traduzidos**, 477 rótulos distintos e
**2.093 campos/ocorrências de interface**. Isso não mede a porcentagem do jogo.
Os 477 nomes anteriores e seus patches, 536 descrições/883 IDs, MAP v030,
layout/fontes v005, arte v014 e mensagens de sistema permanecem idênticos.

## Adiamentos e limites

Foram retomados explicitamente 12 adiamentos: IDs **331, 352, 354, 355, 372,
373, 385, 433, 449, 451, 727 e 747**. Quatro nomes não haviam sido selecionados:
374, 619, 774 e 782. O ledger fica em 527 selecionados, 493 aceitos,
**33 pendentes** e um preservado. Os dados históricos dos outros adiamentos
permanecem integralmente iguais.

Não houve liberação nova do formato: mantém-se o teto observado de 16 bytes
mais NUL no próprio preenchimento zerado. Não há repack ou mudança de fonte.
Nomes únicos, aliases protegidos, glifos ausentes e propostas sem redação
natural dentro do teto continuam bloqueados. O planejador local informa
39 nomes ainda não selecionados, incluindo termos que devem ser preservados;
não são 39 traduções automaticamente autorizadas.

## Uso e reprodução

Abra **Iniciar-Teste.cmd**. A versão consolidada é:

`work/interface-v023/MetalSaga-ptbr-interface-v023.iso`

Em partida normal, conferir nomes, acentos, alinhamento e seleção no inventário,
lojas, acessórios e decoração. Não é preciso obter cada item para prosseguir.
A validação visual continua pendente; não houve execução do PCSX2 pelo agente.

```powershell
python tools/plan_interface_menus.py
python tools/build_translation_pilot.py --draft translations/regiao-inicial-v030.json --interface-draft translations/interface-v023.json --output work/interface-reproducao-v023 --compact-output --build-iso
python -m unittest discover -s tests -p test_interface_v023.py -v
```

As ferramentas funcionam localmente, sem IA/APIs. O planejador reutiliza
`work/planejamento-interface.json`; fontes e bytes originais ficam fora do Git.

## Verificações

Passaram **26 testes distintos**: cinco do lote, sete do teto de nomes, seis
de planejamento, cinco de retenção e três da alpha. Conferem preservação dos
477 nomes anteriores e patches, apenas 12 retomadas, aliases, codificação,
limites, round-trip dos recursos e atributos intactos nos 1.349 registros.

Hash da imagem e comparação integral com a v022 ficam em
`reports/interface-v023.json`. Uma única ISO nova; retenção de cinco imagens
de trabalho e alpha permanente protegida. OneDrive/desligamento só por novo
pedido. Pendências seguintes: nomes sem solução natural dentro do teto,
descrições sem espaço e semântica de TITLE/BACK.

Comparação executada: **204 bytes diferentes em 16 intervalos autorizados**;
demais bytes e diretório ISO idênticos. SHA-256:
`b7fca2c6227be9cea4682129c6bc1ae7905d2e7999f6ed9237c9faec1b6a7840`.
Iniciador conferido sem abrir o PCSX2.
