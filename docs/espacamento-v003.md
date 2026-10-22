# Espaçamento PT-BR v003 — correção experimental no cache de glifos

## Estado

O usuário relatou melhora no desenho v002, mas confirmou espaçamento excessivo
na captura de `Teste: ação.`. Essa imagem valida a melhora relativa do desenho,
sem aprovar as métricas. Não houve novo teste visual após a correção abaixo.

A ISO experimental v003 conserva os bitmaps v002 e modifica o executável somente
no trecho declarado. O resultado ainda precisa de validação manual no PCSX2.
Nenhuma alteração foi promovida à ISO de desenvolvimento nem às receitas v004.

## Evidências no executável original

Revisão SHA-256:
`25756885a1a01a4ddd82045fd78e1928c09873f810cf182b99b248914fb1ea71`.

Endereços abaixo são offsets no ELF; endereço virtual = offset + `0xFF000`.

| Offset | Comportamento observado |
| --- | --- |
| `0x197148` | Classifica código: ASCII classe 1; os pares PT-BR classe -1 |
| `0x197974` | Consulta essa classificação ao adicionar um glifo ao cache |
| `0x19797C..0x1979FB` | Dispatch: classes 1/2 fazem lookup e ligam bit 0; classes -3/-2/-1 fazem lookup e desligam bit 0 |
| `0x197A10` | Guarda o código original na entrada do cache |
| `0x197E5C..0x197E7C` | Bit 0 seleciona largura: célula inteira ou metade + 2 |
| `0x1988BC` | Um consumidor consulta essas dimensões para desenhar e avançar a posição |
| `0x3DF48` | Outro consumidor consulta dimensões e acumula o avanço |

O cabeçalho GFI contém tamanho de célula, não uma tabela de métricas por letra.
Redesenhar os pixels não muda esse bit de largura. A nova célula tinha corpo de
letra latina, mas continuava sendo medida como largura inteira.

## Correção restrita

`tools/glyph_spacing.py` substitui 128 bytes de instruções dentro da função
existente. Não usa área vazia como código, não amplia o ELF, não adiciona segmento
nem desloca ponteiros. O hash original do trecho é
`f767e2885d654c47501d9477398b5bdb011afdb7912ea89403547e0f35d99760`.

A revisão reúne os dois ramos duplicados de lookup e preserva a seleção original,
acrescentando uma exceção para exatamente `8240..824E` e `8259..825B`:

- A busca do bitmap recebe o código de dois bytes original, sem substituição por
  ASCII: os acentos e cedilhas continuam desenhados.
- Somente o bit de largura passa a ser igual ao das letras ASCII.
- Os outros bits da entrada do cache permanecem iguais.
- NUL/controles e códigos fora das classes aceitas seguem os destinos antigos.
- O registrador temporário s4 já é salvo no prólogo original e recebe uma nova
  atribuição em `0x197AB4` antes de seu próximo uso original.
- Os slots de atraso MIPS são explícitos; não há instrução de salto dentro deles.

A largura retornada esperada passa de 22 para 13 na fonte menor e de 26 para 15
na maior, exatamente como no caminho ASCII. Esses números são dimensões do motor,
não uma promessa de distância final em pixels após escala, margens e controles.
Todos os 18 bitmaps v002 cabem nessas larguras, sem perder pixels horizontais.
O tamanho do desenho não foi reduzido para corrigir o espaçamento.

## Validação e limites

O interpretador local executa as instruções originais e as novas, incluindo slots
de atraso, operações inteiras e acesso ao cache. A chamada de lookup é simulada,
com argumentos registrados e registradores voláteis deliberadamente alterados.
Comparou-se cada código de 16 bits: 65.536 entradas, com diferença exclusivamente
nos 18 códigos PT-BR. Outros testes cobrem flags iniciais pares/ímpares, limites
dos intervalos e classes fora da faixa. O interpretador não emula o PS2 completo.

A varredura de saltos diretos nas seções executáveis não encontrou entradas
externas no trecho substituído. A antiga tabela indireta continua intacta no ELF,
mas não é usada pelo novo dispatch. A varredura não prova ausência de toda
referência indireta; isso permanece uma limitação da análise estática.

O construtor comparou a ISO inteira ao original: somente duas mensagens, 36
células de fonte e a janela do ELF diferem. Tamanhos, diretórios e LBAs ficaram
iguais. Não houve execução do PCSX2 pelo Codex nesta etapa.

Ainda pendentes: validar aparência no jogo, outros contextos de desenho/medição,
quebras automáticas e opções de resposta. Não generalizar o teste às demais
fontes ou a controles dinâmicos ainda desconhecidos.

## Uso local

Executar `Testar-Espacamento.cmd`, com o emulador isolado fechado. A ISO é:
`work/MetalSaga-ptbr-espacamento-v003.iso`.

Usar novo jogo e os primeiros diálogos com Nina, sem savestate. A primeira fala
mostra `Teste expandido:` / `Mesmo registro`; a próxima contém:

```
Teste: ação.
á é í ó ú
Ç Á É Ã Õ
```

Comparar `ação` com a captura anterior: o espaço artificial entre ç/ã e a letra
seguinte deve desaparecer. Nas linhas com letras isoladas existem espaços
intencionais; eles devem permanecer regulares. Observar também perda de desenho,
sobreposição, altura e funcionamento da página inglesa seguinte. A melhora é
esperada pela análise, mas não está visualmente confirmada.

Reproduzir sem internet, IA ou APIs (usar novos nomes de saída):

```
python -m unittest discover -s tests
python tools/validate_glyph_spacing.py --output work/relatorios-reinsercao/auditoria-espacamento.json
python tools/build_accent_experiment.py --profile v003 --output work/novo-teste-espacamento.iso --report reports/novo-teste-espacamento.json
```

Os geradores recusam sobrescrever arquivos existentes. Fechar esta ISO e voltar
à v002 reverte o experimento; os originais e a ISO de desenvolvimento permanecem
preservados. Promover o mecanismo à reinserção exigirá um perfil que vincule
explicitamente fonte, patch de executável e hashes, mantendo compatibilidade das
receitas antigas.
