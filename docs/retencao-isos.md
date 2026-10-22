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
