# Lote ampliado v019

## Escopo e progresso

O recorte `0x0A13A3E8..0x1FF30844` contém 5.963 registros. A ampliação acrescenta
800 ocorrências: 481 alvos próprios, 284 propostas de reutilização por identidade
de todos os segmentos originais e 35 adiamentos. Foram revisadas as 248
reutilizações com conteúdo alfabético, além das pausas e controles restantes.
Igualdade de bytes não foi tratada como prova de contexto narrativo idêntico.

| Versão | Registros no recorte | Traduzidos | Segmentos traduzidos |
| --- | ---: | ---: | ---: |
| v018 | 5.163 | 4.034 | 4.251 |
| v019 | 5.963 | 4.681 | 4.926 |

O ganho é de 647 registros traduzidos. Os 5.163 registros da v018 continuam
idênticos em texto e metadados, comparados integralmente ao sufixo da lista nova.
A ordem da lista não representa realocação física dos registros no jogo.

O total traduzido equivale a aproximadamente 64,74% dos 7.231 registros textuais
catalogados no MAP.MCT. Essa proporção inclui mensagens de sistema e escolhas;
não mede palavras, somente diálogos ou a tradução completa do jogo.

## Contexto e decisões

| Intervalo novo | Sequências |
| --- | --- |
| `0x0A13A3E8..0x0A13B320` | Família de Gorou, Orochi, Kaede e reações ao braço mecânico |
| `0x0A60FE64..0x0A6198FC` | Serviços de Torikami, Noah, Grande Destruição, caça, lenda de Yaheiji, chuva e relatos dos habitantes |
| `0x0AF86624..0x0AF8EB8C` | Variantes de serviços e conversas de Torikami, preservadas como ocorrências distintas |
| `0x0B8FB88C..0x0B8FEFB8` | Kaede, presentes, Ghost Tank e variantes familiares |
| `0x0BE06BE4..0x0BE1FCF0` | Beldaire, família, modelos e coleção de tanques, Disassembler, Exército Blueberry e corrida |

Os intervalos agrupam sequências disponíveis; não comprovam todos os falantes,
retratos ou condições de roteiro.

A lenda conserva o sacrifício a cada cem anos e a mudança de assunto para a
propaganda do Dragon Inn. Moradores discordam sobre a morte de Orochi: não
normalizar crenças, gratidão e hostilidade em uma única interpretação. O relato
sobre Noah mantém sua atribuição a um personagem e a incerteza sobre o Hunter
que o teria destruído. As instruções de caça conservam rumos e nomes próprios.

Rosa e Arthur descrevem os tanques como entusiastas; Carl aborda manutenção,
chassi, motores e sistemas. Modelos e nomes franceses permanecem. A história
sobre Carl é uma provocação desmentida, mantida com suas diferentes reações.
A foto do Disassembler conserva semelhanças, sem afirmar parentesco. Sebastian
mantém formalidade, inclusive no pedido de ajuda e na questão da lente quebrada.

A extorsão do Exército Blueberry conserva o uso irônico de “proteção”, o disfarce
de bandidos e as variantes com ou sem participação do protagonista na batalha.
Não houve tradução em massa de tabelas de itens ou inimigos.

## Integridade e limites

Há 1.282 registros preservados, incluindo 300 adiamentos. Os 35 novos casos são:
20 com controles opacos, dez com terceira string sem edição liberada e cinco
com ambas as condições. Esses bloqueios não foram flexibilizados.

A compilação revisada tem zero recusas e zero violações de terminologia.
Páginas, quebras, escolhas, comandos e spans vazios continuam vinculados aos
originais. Excedentes foram resolvidos reformulando os alvos. A exceção ASCII
`nao` permanece somente em `map.msg.1df8bec0`. Não houve ampliação de registros,
blocos SSD ou extents. O recorte reúne 1.301 grupos SSD e 486 avisos conservadores
de largura; não são medições em pixels.

A suíte completa passou: 115 testes em 242,600 segundos.

A política distingue S Tank/S Tanks do possessivo inglês 's tank pela grafia,
sem alterar a checagem dos demais nomes. O teste específico exige preservar o
modelo e permite traduzir o possessivo comum. A nova regressão de lote verifica
a preservação integral da v018, os adiamentos, os fatos da lenda, as direções,
os dois motores e os comandos temporizados da fala de Rosa.

Fontes v002 e espaçamento v003 continuam assumidos provisoriamente corretos
pelo usuário. Esta versão não foi executada no PCSX2 pelo Codex. Observar
acentos, espaçamento, páginas, escolhas e largura em conversas acessíveis de
Torikami ou Beldaire; não é necessário alcançar todas as variantes numa sessão.

## Execução e reprodução

- `Preparar-Regiao-Inicial.cmd`: compila e valida a v019 sem gerar nova ISO.
- `Testar-Regiao-Inicial.cmd` ou `Iniciar-Teste.cmd`: abre a versão atual.
- ISO: `work/regiao-inicial-v019/MetalSaga-ptbr-regiao-inicial-v019.iso`.
- Revisão bilíngue, plano e relatório: `work/regiao-inicial-v019/`.
- Metadados próprios: `reports/regiao-inicial-v019-validation.json`.

```powershell
python tools/build_translation_pilot.py --draft translations/regiao-inicial-v019.json --output work/reconstrucao-v019 --build-iso
python tools/prepare_translation_lot.py --parent translations/regiao-inicial-v018.json --start-offset 0a13a3e8 --lot-id regiao-inicial-v019 --output work/preparacao-v019-repro
python -m unittest discover -s tests
```


## ISO e retenção verificadas

A ISO possui 1,704,427,520 bytes. A comparação integral confirmou que os
391,490 bytes diferentes correspondem exatamente aos patches
previstos, incluindo fontes e espaçamento. O diretório do disco permanece
idêntico. Não houve alteração dos originais, BIOS, saves ou configurações.

SHA-256: `47585269bd676454d541668b1dff3a837ecfb7ebcdea99a88f3304d60b8d2aff`.

A retenção removeu `work/MetalSaga-ptbr-acentos-v001.iso`, a imagem gerada mais
antiga elegível. Receitas e relatórios permanecem. A conferência posterior
confirmou dez imagens de trabalho; a original em `JOGO/` fica fora da contagem.
O atalho histórico `accents` exige reconstrução para voltar a funcionar.
