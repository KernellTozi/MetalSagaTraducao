# Interface v039 — créditos finais

Rodada de 26/10/2026 após a investigação documentada em
`docs/descoberta-desconhecidos-v002.md`. Base integral interface v038 e MAP v037,
fontes/layout v005 e arte do título v014 preservados.

## Tradução e preservação

Foram revisadas as 51 linhas elegíveis dos créditos finais de FD_END:
**50 alteradas** e o termo comum **Marketing preservado**. São 48 cabeçalhos
de funções alterados e duas frases de encerramento. As 241 linhas de nomes,
empresas e layout permanecem byte a byte iguais; com Marketing, 242 das
292 linhas não mudam. A ocorrência de Atlus na frase de apresentação também
é preservada. Não foram acrescentados nomes aos créditos finais.

Receita própria: `translations/creditos-v001.json`; vinculada por SHA-256
em `translations/interface-v039.json`. Originais e revisão bilíngue ficam
fora do Git. Interface acumulada: **3.804 campos**, acréscimo de 50 sobre
3.754. Isso não representa porcentagem global do jogo. Os 6.024 registros
MAP alterados, 5.983 corpos/opções e 912 referências de rótulos não mudaram.

## Política de reinserção

`tools/credits_translation.py` implementa o opt-in
`credits-roles-same-slot-lzss-font22-v001`, reaproveitando a preparação
anterior. Cobre o conjunto elegível inteiro exatamente uma vez, verifica
IDs/hashes/janelas do ELF e bloqueia edição de nomes ou linhas extras.
Preserva os prefixos nativos 819F, CRLF, contagem e ordem das linhas,
restrição de 35 bytes por linha e o slot comprimido de 4.096 bytes.

A tradução descompactada ocupa **4.373 bytes**, 151 acima dos 4.222 originais.
Não foi removida acentuação ou significado para manter o orçamento histórico.
Uma política nova e explícita permite até **256 bytes adicionais somente na
saída descompactada**; tamanho do arquivo, slot e extents ISO não crescem.
O pacote local antigo mantém o limite original por padrão.

Evidência necessária para essa extensão:

- 0x19B70C–0x19B714 passa o tamanho u32 do fluxo à solicitação de alocação.
- 0x1390B4–0x1390C4 grava esse mesmo tamanho em objeto+0x50; o leitor de
  linhas usa esse campo, e não uma constante 4.222.
- 0x139A90–0x139AA0 passa fonte **22**, seguida pelo encaminhamento do
  buffer ao setter em 0x139AA4–0x139AB0.

Esses encaminhamentos foram executados em RAM sintética. Foram fornecidos
endereços de objetos/stack e retorno de alocação: o alocador real, construção
completa, desenho, rolagem e PCSX2 não foram executados. Não tratar os testes
de argumentos como validação visual da nova tela.

O fluxo traduzido consome **2.433 bytes** do slot 4.096, contra 2.351 no
fluxo original. Descompressão Python e laço original do jogo conferem; replay,
releitura e bytes externos ao slot também. O compilador histórico continua
reproduzível: as receitas anteriores não ganham créditos automaticamente.

## Como executar

`Iniciar-Teste.cmd` abre a versão consolidada v039, sem restaurar savestate.
ISO: `work/interface-v039/MetalSaga-ptbr-interface-v039.iso`.
`Preparar-Interface.cmd` valida o lote atual sem gerar outra imagem.

Reconstrução explícita em pasta nova:

```powershell
python tools/build_translation_pilot.py --draft translations/regiao-inicial-v037.json --interface-draft translations/interface-v039.json --compact-output --build-iso --output work/minha-v039
```

Não é necessário alcançar o final agora. Na passagem contínua, observar
acentuação, centralização, largura e rolagem dos cabeçalhos, frases finais e
nomes preservados. Os créditos não têm aprovação visual nesta rodada.

## Validação e próximos conjuntos

Passaram **66 testes distintos**, incluindo 20 novos: 12 da investigação e
oito dos créditos. Incluem corrupção de cabeçalhos/offsets, metadados variáveis,
caudas opacas, aliases, decodificação de 571 conteúdos distintos, três execuções
originais do decoder, nomes protegidos, Unicode, controles, orçamento e
preservação integral da receita v038. Relatório de construção e comparação
integral: `reports/interface-v039.json` e `reports/interface-v039-delta.json`.

A comparação integral v038→v039 encontrou **2.341 bytes diferentes**, todos
dentro do slot autorizado de créditos. Diretório ISO, arquivos, fontes,
diálogos e todos os demais bytes permaneceram idênticos. Tamanho da nova ISO:
1.704.427.520 bytes. SHA-256:
`6f3c8b3c6f88e99fc7f5092e648c68c364e62f8f1119d78a9cca9914ed700896`.
O preflight integral da nova imagem passou; cinco ISOs de trabalho e o hash
da alpha preservada foram conferidos. Nenhuma navegação PCSX2, cópia OneDrive
ou desligamento foi executado.

Teste local dos créditos:

```powershell
python -m unittest discover -s tests -p test_credits_translation.py
```

Próximo conjunto: concluir associação dos recortes de pintura e compor seus
rótulos em conjunto; depois agrupar os atlas de carregamento/minijogos e
cartazes genéricos já triados. MAIN/SUB/SE e nomes protegidos permanecem
intactos. As três raízes opacas não justificam reiniciar uma engenharia extensa
de modelos antes desses textos conhecidos. TITLE, fontes maiúsculas faltantes,
49 rótulos sem espaço e nativos preservam seus bloqueios específicos.
