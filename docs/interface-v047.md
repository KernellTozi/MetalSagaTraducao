# Interface v047 — instruções e sobras da pintura

Rodada de 28/10/2026, sobre a interface v046 e MAP v040. Nenhuma nova tradução
de diálogo ou nome de item. A ISO mantém fontes/layout v005 e a arte anterior.

## Entrega

| Recurso | Alteração |
| --- | --- |
| RMGALAN, textura 1 | Regras da corrida contra os ataques do tanque |
| RMGDANCE, textura 0 | Regras das poses dos Muscle Men |
| RMGDANCE, textura 15 | Regras da dança |
| RMGKAERU, textura 0 | Regras e controles das apostas em sapos |
| RMGTANK, textura 0 | Regras, cápsulas e controles do minigame de tiro |
| S_PAINT, textura 13, sprite 1 | Chassis → Chassi; barra e Main Gun originais preservados |
| S_PAINT, textura 6, sprite 0 | Chassis → Chassi; Sub e S E originais preservados |
| S_PAINT, textura 8, sprite 19 | Edit → Editar no botão de carimbos |

Os seis botões de pintura aprovados anteriormente permanecem idênticos.
Zoom é preservado. Pôsteres Wanted e títulos WIN/LOSE/ROUND/START decorativos
permanecem como solicitado. O START mostrado no painel dos sapos é o recorte
original do seletor, sem recriação de suas letras.

Há cinco painéis completos e três rótulos novos. A métrica interna acumulada
passa de 3.840 para 3.848 unidades heterogêneas de interface; cinco unidades
representam painéis, não frases. MAP mantém 6.024 registros alterados, sendo
5.983 com corpo/opções modificados; 912 referências de falantes traduzidas.
Os 541 nomes de itens aplicados não mudaram.

## Evidências e limites de edição

Ferramenta: `tools/interface_remainder_graphics.py`. A política dos painéis é
`five-latin-minigame-instruction-panels-v001`; a da pintura é
`paint-six-approved-plus-chassi-and-stamp-labels-v002`.

Cada painel é uma textura indexada 512 × 512, 8 bpp, com cabeçalho/paleta de
1.040 bytes e plano de pixels de 262.144 bytes. O GANM adjacente contém um
sprite de `[0,0,512,400]`. Alterações limitadas ao interior `[4,4,508,396]`;
borda e região inferior permanecem idênticas. Offsets, hashes e geometria
estão vinculados à receita; nenhum arquivo SDA cresce. A associação adjacente
e o conteúdo visual não constituem censo completo de todos os consumidores.

Os textos usam máscaras da fonte GFI já disponível no projeto: corpo de
18 pixels, títulos de 24/26 pixels e quebras medidas antes de desenhar.
Não há compressão horizontal para fazê-los caber. A fonte GFI instalada na
ISO não é alterada nesta rodada. Os índices são escolhidos na paleta original,
incluindo seus valores originais de alpha. Ícones são copiados sem modificar
um único índice, com hash de cada origem/destino. Não aplicar o alpha do fundo
como filtro para a paleta das letras: isso tornava a prévia inicial ilegível;
o teste de contraste impede essa regressão.

Os dois Chassi usam a grade de desenho já utilizada na pintura, com um C
adicional desenhado em coordenadas inteiras. O carimbo tem célula menor:
Editar recebe redução uniforme para 14 pixels, mantendo o quadro de dois
pixels e uma área verde simples dentro dele. Não confundir essa escolha
local com mudança geral da fonte ou aprovação visual do usuário.

O encaminhamento original do carimbo foi executado em RAM sintética nas
janelas ELF `0x64A34–0x64A70`: textura em `0xF140`, tamanho `0x4410`, GANM em
`0x13550`; destinos `0x1ACC58` e `0x19AF80`. Bases de objeto/contexto/recurso
fornecidas ao teste. Não executa carregamento completo, seleção do sprite,
GPU ou PCSX2. As provas anteriores dos botões e do componente são mantidas.

A nova receita vincula o hash exato da v046 por `interface_remainder_review`.
Só libera os dois conjuntos gráficos acima, nome de ISO e estado descritivo.
Receitas históricas continuam aceitas pelos perfis originais. A integração
compõe a textura 13 sobre os seis botões aprovados; não importa um SDA inteiro
baseado no original por cima das 228 legendas já traduzidas.

## Validação realizada

- 133 testes passaram, incluindo 12 novos. Fontes de teste e casos anteriores
  preservados; testes novos cobrem geometria, overflow, contraste, ícones,
  paleta/alpha, round-trip, vinculação da receita e composição da pintura.
- Comparação de todos os bytes da ISO contra v046: exatamente **225.797 bytes
  diferentes em oito planos de pixels**, todos previstos. Diretório, extents,
  tamanho, ELF, MAP, fontes e demais bytes permanecem iguais.
- SHA-256 integral e ausência de transação pendente conferidos pelo preflight.
- Auditoria de nomes: 10.690 campos examinados, 65 referências classificadas
  para preservação, zero sem decisão. As novas três legendas da pintura entram
  no recorte literal; os cinco painéis têm inspeção e manifesto próprios.
- Cinco ISOs de trabalho após retenção. Alpha original conferida pelo hash
  histórico, independente e fora da fila de retenção.
- As comparações de imagens foram inspecionadas localmente. **PCSX2 não foi
  executado; a apresentação em jogo ainda depende de avaliação do usuário.**

## Executar e conferir

Abra `Iniciar-Teste.cmd`. Ele aponta para:

`work/interface-v047/MetalSaga-ptbr-interface-v047.iso`

Tamanho: 1.704.427.520 bytes. SHA-256:
`46bf798661588ff274e3f6cc7b71b2a1026738344856fe259f14feb54defb1ed`.

`Preparar-Interface.cmd` valida a receita atual sem gerar outra ISO.
Para reproduzir a construção em outra pasta nova:

```powershell
python tools/build_translation_pilot.py --draft translations/regiao-inicial-v040.json --interface-draft translations/interface-v047.json --compact-output --build-iso --output work/interface-v047-rebuild
```

Comparações antes/depois desta entrega ficam em
`work/interface-v047-preview-aprovacao/`. Esse nome de pasta identifica o
material para avaliação, **não uma aprovação já recebida**. Para gerar novas
comparações localmente, sem Codex, APIs ou outra ISO:

```powershell
python tools/interface_remainder_graphics.py --preview work/comparacao-interface-v047
python -m unittest discover -s tests -p test_interface_remainder_graphics.py
```

Na partida normal, observar as cinco telas de regras e os três rótulos da
pintura: leitura dos acentos, corte de bordas, contraste, identificação correta
dos controles e manutenção dos desenhos anteriores. Não é necessário alcançar
todas as telas imediatamente nem repetir navegação automaticamente.

## O que permanece

`reports/interface-lacunas-v002.json` classifica os 20 candidatos do catálogo
gráfico anterior sem duplicar: cinco painéis novos, três texturas de pintura
atualizadas, Carregando já pronto, dois pôsteres preservados, oito atlas de
títulos decorativos preservados e **um painel japonês de regras do minigame de
cães ainda sem uso/contexto demonstrado na versão inglesa**. Não substituir
essa imagem por uma tradução presumida.

Os três recursos especiais de semântica desconhecida continuam descritos na
descoberta v002; não se demonstrou que guardem textos. Ausência de frases ASCII
não prova ausência de codificação nativa. A triagem cobre 119 atlas conhecidos,
não garante toda a interface nem todo o jogo.

Em filas separadas continuam oito ocorrências nativas MAP, 49 rótulos msgn
sem o espaço necessário e 16 revisões editoriais de itens anteriormente
bloqueadas. Elas não foram liberadas por semelhança nem contadas como lacunas
gráficas resolvidas. O próximo passo útil é a revisão contextual em partida
normal e investigar ocorrências restantes com evidência concreta de tela/save.
Sem cópia para OneDrive nesta rodada. Desligamento solicitado pelo usuário
somente após salvar documentação, conferir Git e concluir o push.
