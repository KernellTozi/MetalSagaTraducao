# Interface v004 — ajuda do Satcom e armamento

Lote consolidado: **519 campos de interface**, sendo 277 literais ELF, 98 mensagens
de sistema, 100 campos do diário e **44 páginas completas de ajuda do Satcom**.
São 46 campos novos frente à v003; páginas possuem extensões diferentes, portanto
contagens de campos não representam porcentagem do jogo. A ajuda nova ocupa
15.072 bytes na origem e 14.487 bytes traduzidos, antes do preenchimento com zeros.

As páginas abordam condução e reboque, blindagem, avarias, categorias MAIN/SUB/SE,
montagem, equipamentos, procurados, funções do Satcom, habilidades, presentes e
androides. Imagens ilustrativas e seus textos rasterizados permanecem originais.
O lote não libera automaticamente outras entradas de NDATA, mensagens ainda não
identificadas, nomeação gráfica nem os fragmentos opacos do MAP.

## Executar e reproduzir

- `Preparar-Interface.cmd`: valida MAP v030 + interface v004 localmente, sem ISO nova.
- `Testar-Interface.cmd` ou `Iniciar-Teste.cmd`: abre a ISO consolidada v004.
- ISO: `work/interface-v004/MetalSaga-ptbr-interface-v004.iso`.
- Exportação local: `python tools/help_text.py --output work/ajuda-exportada-nova.json`.
  Arquivo novo obrigatório; contém originais e deve permanecer fora do Git.

Construção reproduzível, com diretório de saída novo:

```powershell
python tools/build_translation_pilot.py --draft translations/regiao-inicial-v030.json --interface-draft translations/interface-v004.json --output work/interface-v004 --build-iso
```

Nenhuma dessas ferramentas usa IA ou APIs. A tradução foi preparada na receita;
as ferramentas locais fazem extração, validação e reinserção binárias.

## Estrutura comprovada

Política opt-in `ndata-html-help-fixed-load-v004`, em `tools/help_text.py`.
Somente índices SDA **127, 129 e 131–172**: 44 páginas ASCII com HTML/FONT/BR/IMG.
A tabela do ELF em **0x322368** tem 64 pares de offset/tamanho de oito bytes;
as 44 páginas possuem descritores únicos correspondentes ao SDA original.
Os pares ausentes não foram promovidos a páginas.

Janelas vinculadas por SHA-256, além do hash integral do ELF original:

| Arquivo ELF | Evidência |
|---|---|
| 0xD4160–0xD424C | Seleção do descritor, leitura do offset e tamanho, carregamento e buffer |
| 0xD4FB8–0xD54A0 | Parser de marcações, FONT/IMG e fechamento HTML |
| 0xD4F38–0xD4F80 | Reconhecimento de BR e altura de linha |

O carregador obtém o par em 0xD41A8/0xD41E0. O parser compara o fechamento com
`HTML` (literal em 0x3490A8), devolve 6 em 0xD50FC e o chamador encerra a passagem
em 0xD42D0/0xD43D8. Assim, o preenchimento após `</HTML>` fica fora do documento.
A análise das instruções é estática; não equivale a execução dessas telas no jogo.

Não alterar offsets, descritores, tamanhos carregados, extents ou arquivos de fonte.
Cada tradução cabe no intervalo originalmente lido, com zeros no restante.
Preservar a sequência exata de tags, atributos, nomes de imagens, números,
percentuais `%%` e CR/LF originais. Tokens PT-BR usam o mapeamento de dois bytes
do projeto, com layout v005; não são CP932 padrão. O compilador faz readback e
reversão integral dos recursos e rejeita sobreposição e crescimento.

## MAIN, SUB e SE

Por orientação do usuário, preservar essas categorias também nas referências
textuais. Duas novas entradas ELF trocam apenas Main/Sub por MAIN/SUB; a descrição
de tiro passa a “Tiro MAIN”. No diário, apenas Sub → SUB no corpo 56.
O filho MAP v030 revisa oito registros (nove segmentos), mantendo 5.892 registros
traduzidos e os demais textos, controles, rótulos e adiamentos da v029.
Receitas antigas continuam reproduzíveis; não foram reescritas.

Regra opt-in `preserve-main-sub-se-v001`, em `tools/weapon_terms.py`, verifica
referências reconhecidas por ocorrência. A verificação não substitui revisão de
contexto nem reconhece automaticamente toda paráfrase ou palavra em imagem.

## Teste visual consolidado pendente

O Codex não navegou no PCSX2 nesta rodada. Abrir o Satcom e percorrer a ajuda:
verificar acentos, separação de palavras, cores, rolagem, imagens e cortes de linha.
O cálculo auxiliar de linhas em 0xD42C8/0xD4318 avança por bytes; os acentos usam
dois bytes. As quebras explícitas foram preservadas, mas eventuais quebras
automáticas/altura de rolagem precisam de observação. Não promover esse contexto
a visualmente aprovado apenas pelo sucesso dos testes binários.

Conferir MAIN/SUB/SE no combate, informações do veículo, diário sobre armas e
nas conversas de construção de tanques quando alcançadas no save corrido.
A alpha v001 permanece intacta fora da retenção; no máximo dez ISOs em work/.

## Entrega OneDrive

O pedido desta rodada autoriza uma cópia, sem automatizar cópias futuras.
`tools/copy_onedrive.py` exige diretório explícito de construção concluída, relatório
válido, tamanho/hash integrais e ausência de transações ou arquivos parciais.
Copia para `C:\Users\Kernell\OneDrive\METAL SAGA\MetalSaga-PTBR.iso`, verifica o
temporário, preserva a origem e substitui somente esse arquivo após validação.
O hash final é conferido novamente. A sincronização em nuvem depende do OneDrive;
o relatório confirma a cópia local, não a conclusão do upload.


## Verificações executadas nesta entrega

- 40 testes automatizados aprovados: ajuda (6), cópia isolada (3), interface (20), retenção (4), layout individual v005 (4) e preservação da alpha (3).
- Compilação completa: 5.892 diálogos alterados, 1.339 inalterados, zero recusas; 519 campos de interface. Exportador local executado: 44 páginas.
- Comparação integral da ISO com o original na construção e com a v003 pelo verificador independente: 14.429 bytes diferentes em 56 patches; diretório, fontes/layout e todo o restante iguais à v003.
- ISO de 1.704.427.520 bytes, SHA-256 `672b08b36679c5226a93a07b7074f7c5b11118ae7d0119f4d945d98e8d1db178`. Dez ISOs sob work/; alpha permanece fora da retenção.
- Cópia local para OneDrive concluída e conferida pelo mesmo tamanho/hash, com origem preservada e sem transações pendentes. Upload em nuvem não confirmado.
- Evidências próprias em `reports/interface-v004-validation.json`, `reports/interface-v004-delta.json`, `reports/interface-v004-format-evidence.json` e `reports/onedrive-interface-v004.json`. PCSX2 não foi executado nesta rodada.
