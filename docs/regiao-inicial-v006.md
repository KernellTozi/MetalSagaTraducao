# Região inicial — lote consolidado v006

O recorte `0x1DF47F0C..0x1DF66C80` contém 444 registros: 384 traduzidos
e 60 preservados, incluindo onze bloqueados. São 416 segmentos traduzidos e
92 grupos SSD. A v005 tinha 385 registros, 343 traduzidos e 370 segmentos.
Os 385 registros anteriores permanecem integralmente iguais no plano compilado.

## Conteúdo e contexto

O acréscimo de 59 ocorrências inclui conversas e alternativas de Rachel:
preocupação com a profissão de Hunter, ciúmes, reações ao braço mecânico,
agradecimentos após eventos e lembranças familiares. Também inclui descrições
de fotografias e falas da família. Não são necessariamente cenas consecutivas.

Foram revisados 44 alvos únicos e reutilizadas 14 ocorrências com todos os
segmentos de origem idênticos. Reticências, hesitações, risadas, nomes e marcas
como `*sniff*`, `*sob*` e `*glare*` foram preservados. O texto é uma tradução
de trabalho contextual; a revisão narrativa e visual permanece aberta.

O novo bloqueio `map.msg.1df6435c` contém `%I$0`, controle opaco de nome de
item. O registro inteiro permanece intacto. Não houve tradução de tabelas de
equipamentos ou alteração de controles para aumentar a cobertura.

## Integridade e execução

89 testes automatizados passaram, incluindo comparação integral do prefixo v005,
preservação dos bloqueios, controle de tokens, limites de slots e leitura de
retorno. A construção compara a ISO completa com as modificações previstas,
confere hashes e preserva diretórios e extents. Todos os registros usam slots,
sem realocação. Avisos conservadores de largura permanecem no relatório.

Não foi executado teste visual desta versão no PCSX2. O perfil de fontes v002
e espaçamento v003 segue a premissa autorizada pelo usuário, sem nova aprovação
tipográfica. Uma tentativa de usar `Ó` maiúsculo foi recusada pelo codec: essa
letra não faz parte dos 18 glifos atuais. A frase foi reformulada naturalmente,
sem remover acentos nem ampliar o mapeamento.

- `Preparar-Regiao-Inicial.cmd`: compila e valida localmente, sem gerar ISO.
- `Testar-Regiao-Inicial.cmd` ou `Iniciar-Teste.cmd`: abre a ISO atual.
- ISO: `work/regiao-inicial-v006/MetalSaga-ptbr-regiao-inicial-v006.iso`.
- Plano e revisão bilíngue: `work/regiao-inicial-v006/`.
- Evidências publicáveis: `reports/regiao-inicial-v006-validation.json`.

Reconstrução em uma pasta nova:

```powershell
python tools/build_translation_pilot.py --output work/reconstrucao-v006 --build-iso
python -m unittest discover -s tests
```

Para a próxima validação manual, observar opções de resposta a Rachel, troca de
páginas, nomes dinâmicos, acentos e largura das linhas. Algumas respostas exigem
eventos específicos; não é necessário alcançar todas em uma sessão.

A retenção removeu a ISO experimental antiga `MetalSaga-ptbr-fontes-v002.iso`
para manter dez imagens de trabalho. Receitas e relatórios continuam preservados;
os mesmos bitmaps integram as ISOs consolidadas. A ISO original não foi alterada.
O atalho histórico `--iso fonts` precisa de reconstrução desse experimento para
voltar a funcionar; o iniciador padrão aponta para a v006 existente.
