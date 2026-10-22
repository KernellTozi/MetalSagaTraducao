# Primeiro lote contextual da cena inicial

## Base de trabalho

O usuário autorizou prosseguir assumindo os caracteres corretos. O perfil de
fontes v002 com espaçamento v003 é, portanto, a base provisória deste piloto.
Isso é uma premissa autorizada, não um teste visual adicional. O patch continua
isolado da ISO de desenvolvimento e das receitas históricas v004.

Escolheu-se a cena inicial porque seu primeiro diálogo já tem localização
funcional conhecida e as duas escolhas de carreira fornecem contexto narrativo.
O lote é pequeno, cobre um intervalo fechado e usa apenas slots comprovados.
Não depende de liberar formatos opacos ou de ampliar registros.

## Conteúdo

- Intervalo inclusivo no MAP: `0x1DF47F0C..0x1DF49C2C`.
- 26 registros: 25 mensagens e uma seleção com duas opções.
- 23 registros traduzidos, três pausas preservadas sem alteração.
- Inclui a conversa sobre tornar-se Hunter, a escolha de carreira, falas das duas
  alternativas e a narração do final alternativo de mecânico.
- Inclui as primeiras reações familiares; não significa que toda a cidade esteja
  traduzida nem que esses registros estejam todos na mesma rota de execução.

Os textos PT-BR próprios estão em `translations/piloto-inicial-v001.json`.
O glossário provisório está em `docs/glossario.md`. A revisão narrativa é
rascunho: foram priorizados sentido, tom familiar e humor, mantendo controles
e espaços binários. Nomes e o termo Hunter permanecem preservados.

O campo `block_offset` identifica o agrupamento SSD. Não foi demonstrado que
todo bloco corresponda a uma conversa independente. Os IDs e offsets permanecem
estáveis; a ferramenta de revisão não inventa personagens a partir do cabeçalho.

## Como reproduzir

Dar duplo clique em `Preparar-Piloto-Inicial.cmd` recompila e valida o rascunho
em uma pasta nova sob `work/pilotos/`, sem criar cópias adicionais da ISO.
Editar apenas as traduções em `translations/piloto-inicial-v001.json` para
revisar a versão autoral. As cópias exportadas preservam o rascunho anterior.

```
python tools/build_translation_pilot.py --output work/meu-piloto --build-iso
```

Usar um diretório novo sob `work/`. Sem `--build-iso`, o comando apenas compila,
valida e exporta a revisão. O processo é local, sem IA, APIs ou internet.
O desenho das fontes usa o Pillow já instalado em `work/python-deps`.

Saídas:

- `plano.json`: metadados originais, textos de origem e traduções para reinserção.
- `rascunho.json`: cópia exata do rascunho autoral usado.
- `revisao.jsonl`: uma ocorrência por ID, contexto SSD e resultado do compilador.
- `relatorio.json`: contagens, comprimentos, controles, avisos e hashes.
- `MetalSaga-ptbr-piloto-inicial-v001.iso`: somente se solicitado e se todo o lote
  for válido.

O plano mantém o formato v004. Não aplicar com o comando legado `apply` esperando
o mesmo visual: aquele comando continua instalando as fontes v001. Para este
piloto, usar o construtor próprio, que vincula explicitamente fontes v002 e patch
de largura v003. Essa separação evita alterar silenciosamente receitas antigas.

## Testes e integridade

O compilador existente verifica hash do MAP, identidade dos registros, controles
e sua ordem, quebras, páginas, opções, buffers e tamanho de slots. Cada registro
traduzido é relido e decodificado a partir dos bytes produzidos. A operação é
integral: qualquer erro impede a construção da ISO.

As fontes produzidas devem coincidir com os hashes da v002. O executável deve
ser a revisão original antes de receber o patch de largura v003. Não se modifica
o tamanho de nenhum arquivo, registro, bloco ou extent. A ISO é comparada byte a
byte ao original, permitindo somente os intervalos previstos.

Há quatro avisos conservadores de largura no compilador legado, que ainda conta
caracteres acentuados como duas unidades. Eles são mantidos no relatório, sem
ser apagados por se presumir correto o novo perfil. Não houve overflow em bytes.
Quebras e margens visuais continuam pendentes de avaliação no jogo.

Os testes adicionais cobrem o lote completo, pausas sem alterações, exclusão de
registro, adulteração de controle e overflow. Falhas de controle ou capacidade
retornam zero patches aplicáveis para o lote inteiro.

## Validação futura

Executar `Testar-Piloto-Inicial.cmd`, iniciar novo jogo e não carregar savestate.
A primeira fala passa a ser `Você quer mesmo ser / Hunter?`. Seguir a conversa
e observar espaçamento, acentos, nomes dinâmicos, mudança de páginas e escolhas.
As opções são `Vou ser Hunter.` e `Está bem, serei mecânico.`.

Não é preciso percorrer as duas rotas na mesma sessão. A alternativa de mecânico
contém um final; para conferir a outra, iniciar novamente ou usar somente dados
do ambiente isolado. Os saves pessoais e configurações originais são preservados.

Próximo passo técnico: consolidar um perfil explícito de fontes/executável na
reinserção transacional, preservando replay e rollback das versões antigas.
Depois da avaliação do piloto, expandir por cenas e revisar os termos provisórios.
