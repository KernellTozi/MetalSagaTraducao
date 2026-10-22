# Fontes PT-BR v002 — revisão experimental

## Evidências e objetivo

O usuário confirmou o funcionamento do piloto v004 (três alterações), mas
reprovou a aparência dos caracteres na captura de `Teste: ação.`. Isso valida
aquele piloto funcionalmente, sem aprovar tipografia, todas as famílias de texto
ou `repack`. Os testes visuais são realizados manualmente pelo usuário.

O gerador v001 centralizava o recorte em uma célula quadrada e usava a caixa
incluindo sombras para posicionar a cedilha. Também redimensionava letras para
reservar espaço. Os caracteres novos seguem o caminho de dois bytes do motor,
com avanço de largura inteira: a revisão de bitmap não corrige essa métrica.

## Implementação

`tools/gfi_refined.py` implementa um perfil separado, preservando o gerador v001,
seus hashes e a política atual da ISO de desenvolvimento. Não muda o codec:
os mesmos 18 pares e células reservadas continuam em uso.

- Contorno principal detectado em intensidade >= 7/15, sem usar o halo como
  ponto de fixação da cedilha.
- Acentos com traço de 1,8 pixel (célula 22) ou 2 pixels (26), supersampling 4x
  e halo discreto. Maior contraste em relação ao traço anterior de 1,3 pixel.
- Corpo das minúsculas a/e/o/u preservado pixel a pixel, sem redução. O ponto
  de i é removido antes de desenhar o acento.
- Maiúsculas conservam largura e linha de base, com compressão vertical mínima
  necessária para reservar espaço acima do contorno (normalmente duas linhas).
- c/C com cedilha não sofrem redimensionamento; podem subir uma linha para
  acomodar a cauda na mesma célula. A cauda parte do contorno sólido inferior.
- Alinhamento horizontal conserva a posição nativa do corpo, em vez de
  centralizar o recorte. A largura de avanço continua sendo a do motor.

Nenhum byte do executável, banco ASCII, cabeçalho GFI ou tabela de linhas muda.
Não foram acrescentados caracteres além dos 18 já mapeados.

## Reprodução e teste

Python e Pillow local em `work/python-deps`, já disponíveis neste ambiente:

```
python tools/preview_gfi.py
python -m unittest discover -s tests
python tools/build_accent_experiment.py --profile v002 --output work/MetalSaga-ptbr-fontes-v002.iso --report reports/fontes-v002-validation.json
```

O construtor exige caminhos novos e recusa sobrescrever resultados existentes.
A comparação ampliada fica em `work/fontes-v002/comparacao.png`, com corpo
original, v001 e v002 para cada uma das duas fontes.

Executar `Testar-Fontes.cmd` com o emulador isolado fechado. O iniciador faz
boot limpo; iniciar novo jogo e alcançar os primeiros diálogos com Nina,
sem carregar savestate antigo. A primeira fala mostra `Teste expandido:` e
`Mesmo registro`. A próxima mostra:

```
Teste: ação.
á é í ó ú
Ç Á É Ã Õ
```

A segunda página inglesa foi preservada. Esta ISO modifica apenas duas falas
e 36 células de fonte; a opção de mecânico do piloto v004 não foi incluída.
Os demais caracteres podem ser inspecionados no atlas; ainda precisam de teste
visual em uma amostra adicional no jogo.

Verificar cedilha ligada de forma natural, acentos distinguíveis, altura das
letras, ausência de cortes e distância entre linhas. O espaçamento horizontal
ainda pode parecer largo. A próxima investigação de métricas deve localizar o
cálculo de avanço do motor; não alterar o executável por tentativa arbitrária.

## Validação executada

- 66 testes automatizados passaram, incluindo preservação das células e dos
  corpos minúsculos nas duas fontes reais.
- ISO comparada integralmente ao original: somente os intervalos previstos
  diferem; tamanho, diretórios e executável preservados.
- Fontes de referência e MAP lidos e conferidos contra hashes do inventário.
- Atlas inspecionado visualmente fora do emulador.
- PCSX2 não executado pelo Codex nesta revisão; aparência no jogo pendente.

O perfil v002 não foi promovido automaticamente à reinserção de desenvolvimento.
Essa promoção depende da avaliação visual e deve atualizar os hashes de fonte
explicitamente, sem invalidar receitas e experimentos históricos.
