# Lote consolidado v021

## Escopo e progresso

O recorte `0x00011074..0x1FF30844` abrange os 7.231 registros textuais do catálogo
conhecido do MAP.MCT. Esta expansão acrescenta as 468 ocorrências restantes:
268 alvos próprios, 184 reutilizações por identidade de todos os segmentos
originais e 16 adiamentos. Foram conferidas as 141 reutilizações com conteúdo
alfabético e os demais registros de pausas e controles.

| Versão | Registros no recorte | Traduzidos | Segmentos traduzidos |
| --- | ---: | ---: | ---: |
| v020 | 6.763 | 5.321 | 5.602 |
| v021 | 7.231 | 5.636 | 5.930 |

O ganho é de 315 registros traduzidos. Os 6.763 registros da v020 permanecem
idênticos em texto e metadados. A regressão compara a lista anterior completa
ao sufixo da nova lista e compara os offsets ao conjunto integral de instruções
textuais reconhecidas pelo índice SSD. Isso não representa realocação física.

São aproximadamente 77,94% dos registros textuais catalogados. O catálogo inclui
escolhas, pausas, nomes e mensagens de sistema; a proporção não mede palavras nem
a tradução completa do jogo. Não há comprovação de que todo recurso textual do
jogo esteja no MAP.MCT ou tenha sido reconhecido pelos parsers atuais.

## Sequências trabalhadas

| Intervalo novo | Conteúdo |
| --- | --- |
| `0x00011074..0x000146EC` | Iwasaki Medical Laboratory, Miracle Dispenser, esterilização, acesso e inspeção |
| `0x004DB994..0x004E8658` | Interior do Tiamat, pesquisa, Alpha X02D, recrutamento, autodestruição e presentes |
| `0x01DEB2AC..0x01DF7584` | Ziggurat, Eddy e companheiros, Murasame, Alex, Noah, míssil, fuga e finais alternativos |
| `0x037390A4..0x0373EC34` | Agentes, acampamento e serviços |
| `0x038A602C..0x038B0C58` | Veículos enterrados, fantasmas e monumento |
| `0x038D51E4..0x038DF7CC` | Morgue Town, Rachel, procurados, Hunters, Klepto Cobain e fugitivos |
| `0x040ED89C..0x040EF324` | Esgoto, Jack, Wayne, Rachel e escolhas de intervenção |

São agrupamentos das sequências disponíveis, não identificação comprovada de
todos os falantes, retratos ou condições de roteiro. Nomes próprios, modelos e
itens únicos foram preservados; não houve tradução em massa de tabelas de itens.

Alpha conserva formalidade e limites de compreensão, inclusive quando examina
roupas e presentes. A ativação mantém comandos e nome dinâmico. Murasame mantém
a motivação de vingança e a variante posterior à morte de Alex. A exposição
sobre Noah não foi convertida em narração externa. O final ruim conserva a
semana, os noventa por cento e a ironia das baratas.

Rachel mantém preocupação e confiança disfarçada. As referências musicais e a
postura de Klepto Cobain foram adaptadas dentro dos slots, conservando o nome.
O monumento mantém sua inscrição e as pausas da voz dos mortos. O diálogo de
Eddy conserva a variante Ziggarut, sem normalização automática de nomes.

## Bloqueios e auditoria

Há 1.595 registros preservados, incluindo 349 adiamentos. Os 16 novos bloqueios
são dez com controles opacos, quatro com terceira string sem edição liberada,
um com ambas as condições e um com bytes nativos cuja edição segue bloqueada.
Não houve flexibilização de verificações.

A compilação revisada tem zero recusas e zero violações de terminologia. Os
excessos foram corrigidos nos alvos, mantendo controles, páginas, quebras,
escolhas e spans vazios. A exceção ASCII `nao` continua somente em
`map.msg.1df8bec0`. Não houve ampliação de registros, blocos SSD ou extents.
São 1.595 grupos SSD e 618 avisos conservadores de largura; não são medidas em pixels.

A suíte completa passou: 121 testes em 380,625 segundos. Além da preservação
do catálogo, foram exercitados os três testes próprios da auditoria.

A nova auditoria local separa os preservados em 349 adiados, 599 de controles e
pontuação, 458 sugestões de nomes/expressões e 189 a revisar. A última categoria
é conservadora e inclui nomes compostos, gritos e risadas, além de títulos
genéricos. Não interpretar suas sugestões como aprovação automática. Consultar
`docs/auditoria-cobertura.md` e usar `Auditar-Traducao.cmd` para repetir a triagem.

A próxima etapa recomendada é revisar os preservados, começando pelos títulos
genéricos, e tratar os bloqueios por formato. O catálogo completo dentro do
recorte não elimina a necessidade de revisão contextual e validação visual.

Fontes v002 e espaçamento v003 continuam assumidos provisoriamente corretos
pelo usuário. Esta versão não foi executada no PCSX2 pelo Codex. No teste manual,
observar páginas, escolhas, acentos e largura em conversas acessíveis; Alpha,
Morgue Town e Ziggurat são amostras possíveis sem exigir todas as variantes.

## Uso e reprodução

- `Preparar-Regiao-Inicial.cmd`: compila e valida a v021 sem gerar outra ISO.
- `Testar-Regiao-Inicial.cmd` ou `Iniciar-Teste.cmd`: abre a versão atual.
- `Auditar-Traducao.cmd`: gera nova triagem em `work/auditorias/`.
- ISO: `work/regiao-inicial-v021/MetalSaga-ptbr-regiao-inicial-v021.iso`.
- Plano, revisão bilíngue e relatório: `work/regiao-inicial-v021/`.
- Metadados próprios: `reports/regiao-inicial-v021-validation.json`.

```powershell
python tools/build_translation_pilot.py --draft translations/regiao-inicial-v021.json --output work/reconstrucao-v021 --build-iso
python tools/prepare_translation_lot.py --parent translations/regiao-inicial-v020.json --start-offset 00011074 --lot-id regiao-inicial-v021 --output work/preparacao-v021-repro
python -m unittest discover -s tests
```


## ISO, auditoria e retenção verificadas

A ISO possui 1,704,427,520 bytes. A comparação integral confirmou que os
467,954 bytes diferentes correspondem exatamente aos patches
previstos, incluindo fontes e espaçamento. O diretório do disco permaneceu
idêntico. Originais, BIOS, saves e configurações não foram alterados.

SHA-256: `0548698ebbfcd5ef886c20d525dfb1b0d0e3402311754481c01b0bc89daf8f56`.

A auditoria foi executada sobre a compilação final em `work/auditoria-v021-final/`.
Seu resumo sem textos originais está em `reports/regiao-inicial-v021-coverage.json`.
Os arquivos detalhados ficam somente em `work/`.

A retenção removeu a ISO v011, a mais antiga elegível. Receitas e relatórios
permanecem. Há dez imagens de trabalho, v012 a v021; a original em `JOGO/` fica
fora da contagem. O atalho histórico v011 exige reconstrução para ser utilizado.
