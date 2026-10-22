# Lote ampliado v017

## Escopo e progresso

O recorte passa a `0x0E77A270..0x1FF30844`, com oitocentas novas ocorrências.
Foram revisados 419 alvos próprios e 333 propostas de reutilização por identidade
de todos os segmentos originais. Outros 48 registros permanecem bloqueados.
As reutilizações foram conferidas junto das sequências disponíveis, sem tratar
igualdade de bytes como prova suficiente de contexto narrativo.

| Lote | Registros no recorte | Registros traduzidos | Segmentos traduzidos |
| --- | ---: | ---: | ---: |
| v016 | 3.563 | 2.806 | 2.950 |
| v017 | 4.363 | 3.432 | 3.611 |

O ganho é de **626 registros traduzidos**, sem contar pausas, nomes e mensagens
preservadas. Os 3.563 registros da v016 continuam idênticos em texto e metadados;
o teste compara a lista completa anterior ao sufixo da lista nova, após os
oitocentos registros acrescentados. Não houve deslocamento físico de registros.

São aproximadamente 47,46% dos 7.231 registros textuais catalogados no MAP.MCT.
Essa proporção inclui escolhas, mensagens de sistema e outros recursos; não mede
palavras, apenas diálogos ou a tradução completa do jogo. O nome histórico do lote
também não comprova cobertura integral de uma cidade ou região.

## Sequências trabalhadas

| Intervalo novo | Conteúdo e decisões |
| --- | --- |
| `0x0E77A270..0x0E7850EC` | Alice One, culto, transporte, estação, ferimento do protagonista, tratamento e pesquisa. Preservar gravidade, culpa, conflitos e ligação com Grey |
| `0x0F6A702C..0x0F6A7354` | Comércio e rumor sobre criatura no deserto. Não transformar descrição imprecisa em identificação confirmada |
| `0x0F830DBC..0x0F83D33C` | Fort Gears, Maus, recompensa por Binramen, fanáticos por tanques e história local. Manter nomes e divergências com a cidade superior |
| `0x1033AB1C..0x10344DAC` | Antitank Fort, golpista, captura, opiniões sobre veículos e relatos de combate. Preservar alternativas, pensamentos e pedidos de clemência |
| `0x10CF40BC..0x10CF6BBC` | Vila dos Aposentados, rivalidade familiar, carteiras roubadas, cuidados com idosos e Power Suit. Manter ambiguidade dos motivos do chefe |
| `0x12120B6C..0x121228EC` | Negociação de veículo raro com Rosa, propostas únicas e caminhão de bombeiros. Não alterar as regras nem a decisão sobre dinheiro próprio |
| `0x122EA8F4..0x122EB264` | Primeiro túnel, irmãos dos assaltantes e restrição de passagem. Preservar mensagens temporizadas |
| `0x128221CC..0x1282F838` | East Zero, MC Hamir, Murasame, ursinho, Curry Guru, Exército Blueberry, caça e serviços. Separar boatos de direções e instruções práticas |

Os intervalos são limites do recorte, não uma identificação automática de todas
as cenas ou condições de roteiro. Falantes sem vínculo comprovado com retratos
continuam inferidos pelas falas e pelos rótulos disponíveis.

O ferimento continua no braço direito e o estado permanece crítico. As desculpas
e a irritação dos companheiros mantêm intensidades diferentes. A referência à
Professora Grey aponta para Lorelei Bay. Explorer fica preservado como apelido
de Eddy, sem impor essa grafia ao substantivo comum explorador em outros casos.

Os moradores de Fort Gears e Antitank Fort dão versões conflitantes da fundação
e da proteção das cidades. Essas divergências foram mantidas. Maus e Binramen
continuam vinculados à recompensa. A fala da coleção mantém que Rosa não quer
dinheiro emprestado, e a negociação oferece uma única proposta a cada comprador.

Retirement Compound recebe Vila dos Aposentados, coerente com a v015. Os itens
Power Suit e os nomes Maus, Gepard, Bazooka Pooches, Murasame, MC Hamir, Zed e
Francine permanecem. Não houve tradução em massa de tabelas de itens ou inimigos.

O relato do primeiro serviço mantém 100G, canivete borboleta e punk armado.
Direções: sudeste para novatos, nordeste/sudoeste para veteranos e floresta a
sudoeste. A montagem exige quatro componentes, enquanto o cliente levou três.
Os pensamentos do golpista e as mensagens com comandos de espera foram conservados.

## Bloqueios e integridade

Os 931 registros sem alteração incluem 191 adiamentos. Os 48 novos casos são:

- 27 com controles opacos.
- Doze com terceira string sem edição liberada.
- Quatro que reúnem essas duas condições.
- Cinco com bytes nativos cuja edição permanece bloqueada.

Não houve flexibilização dessas verificações. As recusas das revisões
intermediárias foram corrigidas nos alvos, reformulando o texto dentro dos slots
e preservando a quantidade e a ordem de controles, quebras, páginas, escolhas
e spans vazios. A exceção ASCII `nao` continua apenas em `map.msg.1df8bec0`.

111 testes passaram na execução final da suíte completa. O teste novo reproduz
a preparação e verifica a preservação da v016, os bloqueios,
nomes, direções, números e comandos temporizados. A suíte também cobre extração,
reinserção, fontes, instruções do patch de espaçamento, construção de imagens e
retenção isolada. A compilação final não tem recusas nem violações de terminologia.

A ISO tem 1.704.427.520 bytes. A comparação integral confirmou que os 276.913
bytes diferentes correspondem exatamente aos patches previstos, incluindo fontes
e espaçamento, e que o diretório do disco permanece idêntico. O recorte reúne
950 grupos SSD. Não houve realocação de registros ou ampliação de extents.
O relatório mantém 356 avisos conservadores de largura.

Avisos de largura são conservadores e não equivalem a medição em pixels.
Nenhuma aprovação binária substitui teste no PCSX2. Esta versão não foi executada
no emulador pelo Codex. No próximo teste manual, uma conversa de Fort Gears ou
Antitank Fort permite observar tom, escolhas, acentos, largura e páginas. A cena
do ferimento e a negociação com Rosa são amostras adicionais quando estiverem
acessíveis; não é necessário alcançar todas as variantes numa sessão.

## Uso e reprodução

- `Preparar-Regiao-Inicial.cmd`: compila e valida a v017 sem gerar outra ISO.
- `Testar-Regiao-Inicial.cmd` ou `Iniciar-Teste.cmd`: abre a versão atual.
- ISO: `work/regiao-inicial-v017/MetalSaga-ptbr-regiao-inicial-v017.iso`.
- Plano, relatório completo e revisão bilíngue: `work/regiao-inicial-v017/`.
- Metadados próprios: `reports/regiao-inicial-v017-validation.json`.

```powershell
python tools/build_translation_pilot.py --draft translations/regiao-inicial-v017.json --output work/reconstrucao-v017 --build-iso
python -m unittest discover -s tests
```

Preparação reproduzível, sem tradução automática nem ISO:

```powershell
python tools/prepare_translation_lot.py --parent translations/regiao-inicial-v016.json --start-offset 0e77a270 --lot-id regiao-inicial-v017 --output work/preparacao-v017-repro
```

A retenção removeu a ISO experimental v010 para manter dez imagens de trabalho.
Sua receita e seus relatórios permanecem. O atalho histórico exige reconstrução
caso volte a ser necessário; a v016 continua disponível. Originais, BIOS, saves
e configurações não foram alterados.

SHA-256 da ISO:
`3c6d87912bed853057707add957bc5f0f3ffaf15ead9473721554ee1af40cde8`.
