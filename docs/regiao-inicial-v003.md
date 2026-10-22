# Região inicial — lote consolidado v003

**Histórico:** a versão atual está em `docs/regiao-inicial-v004.md`. Os iniciadores
simples abrem a v004. Para reproduzir este lote, usar
`--draft translations/regiao-inicial-v003.json` explicitamente.

## Entrega e continuidade

O lote passa de 98 para 193 registros, mantendo os primeiros 98 exatamente como
no plano v002. A nova versão acrescenta 95 ocorrências, das quais 80 recebem
tradução, 14 preservam nomes/pausas/expressões e uma permanece bloqueada.

| Versão | Registros no recorte | Traduzidos | Preservados | Segmentos traduzidos |
| --- | ---: | ---: | ---: | ---: |
| v002 | 98 | 85 | 13, incluindo 6 bloqueados | 92 |
| v003 | 193 | 165 | 28, incluindo 7 bloqueados | 177 |

Intervalo inclusivo: `0x1DF47F0C..0x1DF56AC0`, em 28 agrupamentos SSD. Não se
presume que um bloco SSD corresponda a uma cena ou personagem. O recorte não
comprova tradução completa da cidade ou de todas as rotas de jogo.

## Conteúdo acrescentado

Inclui armazenamento, modificações de tanques, Mercado Negro, Centro de Memória,
posto de serviço, apresentações de Dr. Mortem e Igor, conversas de retorno com
Emily, opções de música/download, atendimento de Rachel no bar e o conflito
envolvendo Derringer Jack até as falas de confronto.

Não foram modificadas tabelas de equipamentos, tanques, inimigos ou procurados.
`Derringer Jack` permanece intacto em todas as ocorrências do trecho, com teste
de regressão específico para impedir sua substituição. `Junkyard` permanece em
inglês no registro MC do Centro de Memória. As profissões Hunter e Soldier, nomes,
expressões e risadas seguem `docs/glossario.md` e `translations/politica.json`.

A primeira fala mantém `Você quer mesmo ser um` / `Hunter?`. Reformulações de
frases novas respeitam português natural e contexto. Por exemplo, a opção de
amizade usa `Somos amigos.`, mantendo o sentido sem uma construção forçada para
caber. A revisão literária e a apresentação visual ainda não estão concluídas.

## Fonte autoral e reprodução

`translations/regiao-inicial-v003.json` herda v002, que herda o piloto v001.
Os arquivos históricos não foram reescritos. A narração de aposentadoria é
reutilizada em nova ocorrência apenas após comparar os segmentos originais.
Cada ocorrência continua com ID, offset, controles e validação próprios.

Os iniciadores `Preparar-Regiao-Inicial.cmd` e `Preparar-Piloto-Inicial.cmd`
agora compilam este lote por padrão, sem gerar outra ISO. A saída nova em
`work/pilotos/` contém o rascunho expandido, plano, revisão e relatório.

```
python tools/build_translation_pilot.py --output work/minha-revisao-v003
python tools/build_translation_pilot.py --output work/minha-construcao-v003 --build-iso
python -m unittest discover -s tests
```

Para compilar versões históricas, informar `--draft` explicitamente. O gerador
aceita somente um diretório novo dentro de work e recusa herança circular,
reutilização sem fonte idêntica e alteração de rótulos protegidos.

Foi acrescentado `tools/summarize_translation_build.py` para automatizar a
exportação de metadados apropriados ao Git, sem copiar textos originais:

```
python tools/summarize_translation_build.py --build-dir work/minha-construcao-v003 --output reports/meu-resumo-v003.json
```

O resumo deriva do relatório de construção; não constitui novo teste de execução.
`--tests-passed` apenas registra uma contagem já obtida pelo executor, não executa
testes. O relatório entregue informa 85 testes efetivamente executados nesta fase.

## Integridade e bloqueios

Os 85 testes passaram. Além das verificações anteriores, a suíte compara todo o
lote v002 com o prefixo correspondente da v003, protege Junkyard e impede que
uma tradução altere Derringer Jack. Todos os registros modificados usam slots,
sem repack, realocação ou alteração de tamanho.

A comparação integral da ISO confirmou apenas os intervalos previstos: 165
registros MAP, 36 células nas fontes e a janela de 128 bytes do ELF do perfil de
espaçamento. Diretórios, LBAs, tamanhos e demais bytes permanecem idênticos à
referência. São 19.641 bytes diferentes, incluindo fontes e executável.

A v003 mantém os seis bloqueios anteriores e acrescenta `map.msg.1df4e7c0`,
que contém nome e título dinâmicos com `%N$0` e `%T$0`. Esses sete registros
continuam byte a byte originais. Não foram liberados controles para ampliar
artificialmente a cobertura.

Há 19 avisos conservadores de largura, preservados no relatório. O cálculo legado
conta acentos como duas unidades, enquanto o perfil experimental muda o avanço
do glifo. Os avisos não comprovam corte nem garantem que o texto caiba visualmente.
O usuário autorizou continuar supondo os caracteres corretos; não houve teste
visual adicional no PCSX2, nem navegação automática nesta fase.

## ISO e teste futuro

ISO consolidada:
`work/regiao-inicial-v003/MetalSaga-ptbr-regiao-inicial-v003.iso`.

`Iniciar-Teste.cmd`, `Testar-Regiao-Inicial.cmd` e `Testar-Piloto-Inicial.cmd`
apontam para esta versão. A versão v002 permanece acessível por
`Iniciar-Teste.cmd region-v002`. Usar boot limpo, sem restaurar savestate antigo.

Quando houver teste manual, conferir a conversa inicial, salvamento e exibição
de Junkyard, nomes e escolhas do bar, mudança de páginas e margens. Alguns textos
dinâmicos e preços permanecerão em inglês devido aos sete bloqueios conhecidos.

A ISO de desenvolvimento v004, originais, BIOS e saves pessoais não foram
alterados. O total é nove ISOs de trabalho, abaixo do limite de dez; nenhuma ISO
de produção precisou ser removida nesta entrega. Receitas e relatórios permanecem
versionados/localmente preservados conforme sua natureza.
