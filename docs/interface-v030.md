# Interface v030 e MAP v031 — serviços e conclusão da entrada de nomes

Rodada consolidada com **69 registros de diálogo novos** e **dois campos
gráficos novos**. Todas as 5.892 traduções MAP e os 3.449 campos de interface
anteriores foram preservados. Nenhuma fonte GFI ou arte do título foi redesenhada.

| Catálogo | Antes | Agora |
|---|---:|---:|
| Registros MAP alterados | 5.892 | **5.961** |
| Adiamentos técnicos MAP | 123 | **49** |
| Campos/ocorrências de interface | 3.449 | **3.451** |
| Descrições de itens | 566/567 | 566/567 |
| Referências às descrições traduzidas | 925 | 925 |
| Nomes de itens traduzidos | 516 | 516 |
| Nomes de itens pendentes | 25 | 25 |

As 74 retomadas explícitas incluem **cinco preservações**, sem mudança de
bytes: nomes dinâmicos, reticências e marcador de andar. Não contam como
tradução. A cobertura MAP por registros conhecidos é 82,44% (5.961/7.231);
isso não mede todo o jogo, quantidade de palavras ou aprovação visual.

## Conteúdo do lote

- Reparos e desconto de família com a mãe; reparos e venda de veículo.
- Tarifas das três classes do trem, hospedagem e empréstimo para passagem.
- Ofertas de leilão, pagamentos, recompensas e recebimento de dinheiro.
- Entregas de presentes, encomendas, fabricação e espaço no inventário.
- Treinos, aulas de dança, sequência de batalhas e vitórias do cão.
- Ofertas de Ruby Lens e Bus Stop Sign, venda a Rosa e entrada em Hell's Keep.
- Falas curtas com nome dinâmico preservado, sem atribuir identidade canônica
  ao seletor apenas por seu número.

Hunter, nomes próprios e de objetos únicos, expressões e comandos originais
foram preservados. O corpo e as opções de cada ocorrência são revisados
juntos; a reutilização exige igualdade exata da origem, sem trocar tokens
entre variantes. Originais e comparação bilíngue permanecem somente em work/.

## Uso local e teste visual consolidado

Abra **Iniciar-Teste.cmd**. A imagem atual é:

`work/interface-v030/MetalSaga-ptbr-interface-v030.iso`

SHA-256: `1deb57e06fc864d13f850492e881ccc9ba72289fd3ab1e2603db1646a15370d6`

Tamanho: 1.704.427.520 bytes. O iniciador confere tamanho, hash, relatório,
transações e arquivos parciais antes de iniciar o ambiente isolado, sem
restaurar save state. Nenhuma navegação PCSX2 foi realizada nesta rodada.

Na passagem normal, conferir valores variáveis em reparos/passagens/pagamentos,
ordem das três classes e alternativas, nomes recebidos em encomendas, quebras
de linha e avanço das falas. Nomes dinâmicos podem ser longos; o teste binário
não garante que todos caibam visualmente. Não é necessário alcançar cada cena
agora, nem alterar saves para testar.

Na entrada de nomes, conferir **FIM** ativo e inativo na categoria que antes
exibia END. Deve conservar a moldura e o comportamento de concluir o nome.
TITLE permanece original; esta rodada não comprova seu retorno no chamador.
O painel de senha DESTRAVAR/TRAVAR/SAIR e a legenda VOL. permanecem iguais à v029.

`Preparar-Interface.cmd` valida as duas receitas sem gerar ISO. Para reproduzir
a construção em uma pasta **nova**, executar na raiz:

```powershell
python tools/build_translation_pilot.py --draft translations/regiao-inicial-v031.json --interface-draft translations/interface-v030.json --output work/interface-v030-reproducao --compact-output --build-iso
```

`Auditar-Traducao.cmd` usa a v030. Para construções compactas, o auditor
recompila o plano em memória a partir da cadeia de receitas vinculada por hash,
recusando alterações ou contagens divergentes. Não cria outra cópia de originais
nem usa IA, APIs ou internet. O planejador de menus também usa v030:

```powershell
python tools/plan_interface_menus.py
python tools/plan_remaining_texts.py --build-dir work/interface-v030 --output work/pendencias-atualizadas.json
```

O primeiro substitui apenas seu JSON próprio de planejamento. O segundo exige
um caminho de saída ainda inexistente. Não repetir a construção apenas para
atualizar uma lista de pendências.

## Política de variáveis v012

Ferramenta `tools/control_variable_refs.py`, política opt-in
`fixed-record-reviewed-variable-selectors-slots-v012`. Herda v011; reconhece
somente os 21 seletores adicionais encontrados e conferidos:

| Sintaxe | Índices adicionais permitidos |
|---|---|
| `%$n` inteiro | 0, 2, 5, 10, 11, 12, 13, 14, 16, 17, 18 |
| `%I$n` nome de item | 1, 2, 9, 10, 15, 19 |
| `%N$n` nome indireto | 1, 2, 6, 10 |

Leitor original em 0x1B5A30..0x1B5AD0; handlers de inteiro em
0x1B5DEC..0x1B5E84, item em 0x1B5D74..0x1B5DA4 e nome em
0x1B5CAC..0x1B5CE0. SHA do ELF e provas herdadas vinculam esses caminhos.
Foram executados **106 casos em RAM sintética**: consumo da sequência,
seletor/contexto, limites de inteiro com sinal, formato `%d` em 0x349DC0,
stride 128 de item e lookup de ponteiro indireto com stride 4. Os valores e
endereços da tabela são sintéticos. Isso não executa desenho, formatação
completa, inicialização das tabelas ou PS2, nem prova limites de índices em jogo.

Os nomes resolvidos são encaminhados intactos; não se altera a tabela de
itens/entidades por esta política. Comandos, índices, ordem, spans vazios,
quebras, rótulos, cabeçalhos, offsets e tamanhos permanecem vinculados.
Somente slots fixos, sem crescimento por segmento frente à origem e sem
repack para os registros com essas referências. Falha em qualquer registro
recusa o lote inteiro. Políticas anteriores não ganham permissões novas.

Sufixo `f` minúsculo continua bloqueado, mesmo quando o lexer mostra apenas
`%$2` ou `%$13`; o handler usa outra gramática de ponto flutuante. N$3 não
foi liberado. Outros índices, zeros à esquerda, controles desconhecidos e
bytes nativos continuam bloqueados. Lexer histórico/fingerprints de extração
não foram modificados.

## Botão gráfico FIM

Ferramenta `tools/name_finish_graphics.py`, política
`name-entry-two-finish-sprites-v001`, recurso `DATA/FDATA/FNAME_DT.SDA`.
Textura da entrada 2 em **0x4CC0**, extensão **0x40440**, 512×512/8 bpp.
Upload original de 0x40410 bytes; cauda opaca de 48 bytes permanece intacta.
GANM da entrada 5 em **0x86980**: 36 sprites, sem alteração dos descritores.

Somente os interiores dos sprites **14**, [426,216,475,240), e **34**,
[426,440,475,464), recebem FIM. Header, paleta/alpha, molduras, outras
categorias/alfabetos e bytes externos aos dois interiores são idênticos.
GFI original existente, célula 24 pixels, largura natural de 33 pixels,
centralizada, sem redução horizontal. O raster é vinculado por SHA-256.

Foram conferidos upload em 0x10C254..0x10C274, associação GANM em
0x19AF90..0x19AFA4, argumentos das três categorias em 0x10C5B8 e
0x10C8F4 e ramo de conclusão em 0x10B974..0x10B9B0. Os probes limitados
comprovam índices inativos 32/33/34 e ativos 12/13/14. Não executam GPU,
validador completo de nome nem jogo. Preview inspecionado:
`work/nome-fim-v030-comparacao.png`; não é captura do PCSX2.

## Integridade e pendências

Comparação integral v029→v030: **5.845 bytes diferentes em 70 patches**
autorizados (69 MAP e uma textura). Diretório e demais bytes idênticos;
fontes/layout v005 e título v014 preservados. Testes de comandos, rejeição,
atomicidade, slots, round-trip, preservação das traduções anteriores, texturas,
preflight, retenção e alpha: **319 testes distintos aprovados**, registrados
em `reports/interface-v030.json`. Reexecuções focadas não foram somadas.

Triagem em `reports/plano-pendencias-v008.json`:

- **19** nomes de tanques N$3 preservados, ainda tecnicamente bloqueados.
- **14** registros com bytes nativos sem edição autorizada.
- **16** outros: oito com formato numérico `f`; três com `%` incompleto;
  dois com `%N`; um `%M_1`, um `%M_4` e um `%T0`.
- **160** sugestões conservadoras de revisão de preservados, 114 combinações
  de origem. Isso não são 160 traduções obrigatórias ou aprovadas; inclui
  decisões de preservação e não substitui contexto.

TITLE, 25 nomes de itens e lacunas de contexto/recursos ainda exigem provas
específicas. Próxima rodada: revisar o uso de TITLE e os oito formatos numéricos
`f` em conjunto, mantendo frentes independentes e sem repetir tentativa de
encurtar os 25 nomes ou traduzir N$3. Recursos gráficos aparentemente inativos
não são liberados por semelhança. Manter validação visual acumulada em partida.

Há cinco ISOs de trabalho; alpha permanente, original, saves e configurações
preservados. Nenhuma cópia ao OneDrive ou desligamento nesta rodada. Somente
scripts, testes, receitas e documentação próprios são versionados.
