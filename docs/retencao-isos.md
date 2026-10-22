# Retenção de ISOs

Conforme esclarecimento do usuário, manter somente as dez ISOs geradas mais
recentes em `work/`, por data de modificação. Os experimentos de diário, acentos
e desenvolvimento participam da mesma fila, sem exceções fixas. Antes de criar
outra imagem, o construtor reserva uma vaga e remove a mais antiga elegível.

Na conferência após a v017 há dez imagens: três experimentos antigos e v011 a
v017. As v008, v009 e v010 foram removidas nas construções anteriores. Não foram
recriadas para completar uma sequência de versões. Os experimentos antigos serão
substituídos pelas próximas construções, começando pelo experimento do diário.

A ISO original em `JOGO/` fica fora da contagem e nunca é removida. Links,
arquivos desconhecidos, hardlinks e imagens com recuperação transacional pendente
continuam protegidos. Se essas condições impedirem a retenção, a construção falha
em vez de apagar recursos indevidos. Receitas e relatórios permanecem no projeto.

Conferência local, sem apagar arquivos:

```powershell
python tools/iso_retention.py
```

Quatro testes de retenção passaram após a atualização, incluindo ausência de
experimentos fixados por padrão. Remoções reais nos testes ficam restritas a
pastas temporárias isoladas.


Na construção da v018, foi removida a ISO antiga do experimento do diário
(`work/MetalSaga-ptbr-experimento.iso`). A conferência posterior confirmou dez
imagens: acentos v001, desenvolvimento e v011 a v018. A receita e os relatórios
do diário permanecem; seu atalho requer reconstrução da imagem.


Na construção da v019, foi removida `work/MetalSaga-ptbr-acentos-v001.iso`,
a mais antiga elegível. Há dez imagens após a retenção: desenvolvimento e
v011 a v019. Receitas e relatórios do teste de acentos permanecem preservados;
o atalho histórico `accents` requer reconstrução da imagem.


Na construção da v020, foi removida a imagem antiga de desenvolvimento
(`work/desenvolvimento/MetalSaga-ptbr-desenvolvimento.iso`), sem journal de
recuperação pendente. Receitas, snapshots e relatórios continuam preservados.
A conferência posterior confirmou dez ISOs: v011 a v020. O atalho legado
`development` requer reconstrução; a versão atual abre pelo atalho da região.
