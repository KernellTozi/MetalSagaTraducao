# Lote ampliado v020

## Escopo e progresso

O recorte `0x040EF454..0x1FF30844` contém 6.763 registros. Foram acrescentadas
800 ocorrências: 464 alvos próprios, 303 propostas de reutilização por identidade
dos segmentos originais e 33 adiamentos. Foram conferidas as 235 reutilizações
com conteúdo alfabético e os demais casos de pausas e controles. A igualdade de
bytes não foi tratada como prova de identidade de contexto.

| Versão | Registros no recorte | Traduzidos | Segmentos traduzidos |
| --- | ---: | ---: | ---: |
| v019 | 5.963 | 4.681 | 4.926 |
| v020 | 6.763 | 5.321 | 5.602 |

O ganho é de 640 registros traduzidos. Os 5.963 registros da v019 permanecem
idênticos em texto e metadados. A regressão compara a lista anterior completa
ao sufixo da nova lista, após os oitocentos registros acrescentados. Isso não
representa realocação física de textos no jogo.

São aproximadamente 73,59% dos 7.231 registros textuais catalogados no MAP.MCT.
Essa medida inclui escolhas e mensagens de sistema; não mede palavras nem
representa a tradução completa do jogo. Ainda há 468 registros
catalogados anteriores ao limite deste lote, além dos casos preservados no recorte.

## Sequências e decisões

| Intervalo novo | Conteúdo |
| --- | --- |
| `0x040EF454..0x040F10D4` | Jack, Rachel, Wayne, recompensa e variantes de resolução; golpe do falso tesouro |
| `0x04CD88A4..0x04CD92A0` | Confronto com os agentes e variantes |
| `0x04D3090C..0x04D3356C` | Segundo túnel, Mega Mole, trabalhadores, toupeiras e retirada dos agentes |
| `0x057BA02C..0x057DDCA8` | Veículo enterrado, Hell's Keep, cortina de areia, Eddy, caça, mineração e serviços |
| `0x0622A074..0x06230A74` | Upgrade de Remote no Satcom, Doc Optica, Saturday e laboratório de lentes |
| `0x064928BC..0x0653F900` | Ônibus, ponto, ruínas do forte, armadilhas e Exército Blueberry |
| `0x07B2366C..0x084ACAB0` | Forever Land, crianças, Golem, relato do orfanato, barricada e reparo do caminhão |
| `0x0853F4EC..0x08541580` | Orochi, fuga e perseguição, comércio e Mr. TNT |
| `0x0970E0BC..0x0971EDA8` | Monte Macaco, Granddaddy Kong, Dr. Zeus e saltos |
| `0x0A1378CC..0x0A13A32C` | Variantes de Kaede e Gorou, reaproveitadas após revisão |

São agrupamentos de sequências disponíveis. Não comprovam todos os falantes,
retratos ou condições de roteiro, nem a cobertura integral de cada local.

Wayne mantém rudeza e o gesto de poupar os civis; a decisão de Rachel e as
variantes do protagonista permanecem distintas. O golpe conserva suas desculpas
exageradas e hesitações. Não há confirmação nova de relações entre personagens.

Os testemunhos sobre a cortina de areia continuam contraditórios, com a torre,
o dragão e os rumores sobre Eddy separados de fatos confirmados. A direção do
segundo túnel continua a nordeste de Hell's Keep. O trabalhador entediado repete
literalmente a mesma fala, preservando a piada. As instruções técnicas mantêm
as restrições de Remote, as 3/4 lentes e as 10 toneladas de sucata.

Em Forever Land, conservar a responsabilidade de Jared, o contraponto de Julie,
a timidez de Gaspar, as falas de Syd e a caracterização das demais crianças.
O relato do orfanato mantém violência, fuga, acolhimento de outras crianças e a
mudança abrupta para o escorrega. As pistas sobre Golem, Fang e Rouge Rogues não
foram transformadas em revelações explícitas. Modelos de tanques e nomes próprios
permanecem. Não houve tradução em massa de tabelas de itens e inimigos.

## Integridade e limites

Os 1.442 registros preservados incluem 333 adiamentos. Os 33 novos casos são:
22 com controles opacos, nove com terceira string sem edição liberada, um com
ambas as condições e um com bytes nativos cuja edição segue bloqueada.

A compilação revisada tem zero recusas e zero violações de terminologia. Os
excessos foram resolvidos reformulando os alvos, sem ampliar slots ou relaxar
as verificações. Controles, páginas, quebras, escolhas e spans vazios continuam
vinculados aos originais. A exceção ASCII `nao` continua somente em
`map.msg.1df8bec0`. Não há realocação de registros, ampliação de blocos SSD ou
extents. São 1.498 grupos SSD e 566 avisos conservadores de largura; esses avisos
não equivalem a medição em pixels.

A suíte completa passou: 117 testes em 312,186 segundos.

A política distingue Remote, Challenger, Tiger e The Professor dos usos comuns
em minúsculas. O teste específico verifica os dois usos. A nova regressão do
lote verifica a preservação integral da v019, os adiamentos, os comandos, o rumo
do túnel, a repetição intencional, as 10 toneladas e a exclusão de veículos
submersos da função Remote.

Fontes v002 e espaçamento v003 continuam assumidos provisoriamente corretos
pelo usuário. A ISO desta entrega não foi executada no PCSX2 pelo Codex.
Na próxima sessão manual, observar páginas, escolhas, acentos, espaçamento e
largura em conversas acessíveis de Hell's Keep ou Forever Land. As instruções
de lentes e Remote são outras amostras quando estiverem disponíveis.

## Uso e reprodução

- `Preparar-Regiao-Inicial.cmd`: compila e valida a v020 sem gerar outra ISO.
- `Testar-Regiao-Inicial.cmd` ou `Iniciar-Teste.cmd`: abre a versão atual.
- ISO: `work/regiao-inicial-v020/MetalSaga-ptbr-regiao-inicial-v020.iso`.
- Plano, revisão bilíngue e relatório: `work/regiao-inicial-v020/`.
- Metadados próprios: `reports/regiao-inicial-v020-validation.json`.

```powershell
python tools/build_translation_pilot.py --draft translations/regiao-inicial-v020.json --output work/reconstrucao-v020 --build-iso
python tools/prepare_translation_lot.py --parent translations/regiao-inicial-v019.json --start-offset 040ef454 --lot-id regiao-inicial-v020 --output work/preparacao-v020-repro
python -m unittest discover -s tests
```


## ISO e retenção verificadas

A ISO possui 1,704,427,520 bytes. A comparação integral confirmou que os
443,002 bytes diferentes correspondem exatamente aos patches
previstos, incluindo fontes e espaçamento. O diretório do disco permanece
idêntico. Originais, BIOS, saves e configurações não foram alterados.

SHA-256: `2a5977fdfdbb6a25590c541def5d60f174ef8cc19fb8dd24dbf52102540ff6e8`.

A retenção removeu `work/desenvolvimento/MetalSaga-ptbr-desenvolvimento.iso`,
a imagem gerada mais antiga elegível. Não havia journal de recuperação pendente.
Receitas, snapshots e relatórios permanecem. Há dez imagens de trabalho após a
construção, v011 a v020; a original em `JOGO/` fica fora da contagem. O atalho
legado `development` exige reconstrução antes de voltar a ser usado. Para este
lote, usar o atalho da região inicial com o perfil explícito de fontes e ELF.
