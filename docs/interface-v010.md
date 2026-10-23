# Interface v010 — nomeação e legendas dos botões

Continuação da interface v009. Acrescenta **quatro literais ELF**: cabeçalho da
nomeação e três variantes das instruções dos botões. São 12 ocorrências de
rótulos traduzidas dentro desses quatro campos, não 12 registros adicionais.
Total compilado: **620 campos/ocorrências**, preservando os 616 anteriores,
os diálogos MAP v030, gráficos e fontes/layout v005.

## Alterações e limitações

- Cabeçalho: **DIGITE SEU NOME**.
- INPUT → **INS.** (Inserir); SELECT → **SEL.** (Selecionar); END → **FIM**.
- CANCEL → **CANC.** (Cancelar); DELETE → **APAGAR** nas variantes correspondentes.
- TITLE e BACK permanecem intactos: o consumidor textual foi localizado, mas a
  função exata desses dois comandos ainda precisa de conferência do fluxo de
  entrada. Não traduzir BACK como sair/apagar nem TITLE como tipo/título por
  adivinhação. Confirmação “Nome correto?” já pertence ao lote anterior.

Abreviações foram usadas nos slots curtos de cinco/seis bytes para preservar a
posição das instruções e dos símbolos desenhados separadamente. Não houve
remoção de acentos para encurtar palavras: as palavras escolhidas neste lote
não exigem acentos. Não foi alterada a tabela de caracteres selecionáveis.

## Estrutura comprovada

Política opt-in `name-entry-fixed-literals-v001`, implementada em
`tools/name_entry_text.py`. Não altera o catálogo ASCII histórico ou libera
strings com bytes nativos em geral.

| Campo | Offset ELF | Comprimento sem NUL |
|---|---|---:|
| Cabeçalho | 0x33B3B8 | 22 |
| Legenda 1 | 0x32A310 | 51 |
| Legenda 2 | 0x32A348 | 51 |
| Legenda 3 | 0x32A380 | 51 |

As legendas contêm bytes `81 40` intercalados com espaços e cinco palavras ASCII
cada. O extrator conservador de ASCII não incluía os literais completos.
Somente os spans das palavras são editáveis; `81 40`, espaços entre spans,
endereços, comprimento total e NUL final permanecem intactos. Slots encurtados
recebem espaços ASCII **dentro do próprio span**, sem deslocar os campos seguintes.
Não se presume uma codificação geral a partir desses dois bytes preservados.

No cabeçalho, a tradução ocupa o prefixo do slot e o restante recebe zeros;
o endereço e o NUL original também permanecem preservados. São recusados aliases
interiores detectados pelo analisador conservador já existente; isso não é
prova de que toda referência indireta do executável foi descoberta.

## Evidências dos consumidores

- `0x177788`/`0x17779C` carregam `0x44` no registrador salvo s2. Em `0x1777F0`,
  o ADDIU `-0x5C48` resolve VA `0x43A3B8`. A chamada em `0x1777F4` encaminha o
  cabeçalho para `0x20A368`. A distância e o uso de s2 explicam por que a busca
  conservadora de referências imediatas não tinha aprovado esse literal.
- `0x10B368..0x10B39C` ajusta o objeto para `+0x294` e encaminha o texto ao
  consumidor `0x20D608` sem trocar a1.
- `0x10A9C8..0x10AA5C` seleciona as três legendas por LUI/ADDIU e encaminha
  a1 ao mesmo consumidor, incluindo argumentos em delay slots de branch/JAL.
- `0x10E614` preserva a1 em s0; `0x10E6B0..0x10E6BC` encaminha a string ao
  formatador em `0x326C18`. O lote não introduz parâmetros printf.

ELF inteiro e quatro janelas de código vinculados por hash. Foram inspecionadas
instruções e dependências, sem executar o jogo nem simular o leitor inteiro.
Não liberar outras legendas ou bytes nativos por semelhança.

## Uso e próximos passos

**Iniciar-Teste.cmd**, na raiz do projeto, abre a ISO consolidada v010:
`work/interface-v010/MetalSaga-ptbr-interface-v010.iso`.
`Preparar-Interface.cmd` recompila/valida sem criar outra ISO. As receitas v009
e anteriores continuam preservadas; `Iniciar-Teste.cmd interface-v009` seleciona
a imagem anterior enquanto ela existir na retenção.

```powershell
python tools/build_translation_pilot.py --draft translations/regiao-inicial-v030.json --interface-draft translations/interface-v010.json --output work/interface-v010 --build-iso
```

O diretório deve ser novo. Para conferência visual, começar uma nova partida
sem restaurar savestate e observar o cabeçalho, a linha inferior dos comandos,
as posições dos ícones e a confirmação do nome. Não é necessário salvar por cima
de uma partida existente. A nova tela ainda não recebeu validação no PCSX2.

Próximo passo: confirmar TITLE/BACK e os contextos das variantes; depois compor
o conjunto de senha com sua tipografia própria. Conteúdo do correio permanece
pendente. O botão Instalar da v009 continua apenas traduzido, sem ativação ou
confirmação de disponibilidade em execução. Não houve cópia OneDrive nesta rodada.

## Verificações executadas

- 54 testes de interface aprovados, incluindo quatro novos da nomeação; os
  quatro foram repetidos após acrescentar a recusa de aliases interiores.
- Compilação concluída: 5.892 registros MAP alterados, 1.339 preservados, zero
  recusas; 620 campos/ocorrências de interface. Os gráficos e fontes não mudam.
- Comparação integral v009→v010: **55 bytes diferentes em quatro patches ELF**,
  exatamente nos campos previstos; todo o restante, incluindo diretório ISO,
  instruções, texturas, diálogos e layout, permanece igual.
- ISO de 1.704.427.520 bytes; SHA-256
  `eed0c6fd2c22bc73d56f92371dbd61e95f9d4ce519869962979ec3c944e36ce7`.
- Mantidas dez ISOs de trabalho e alpha fora da retenção. Não houve teste de
  execução no PCSX2 nem validação visual nova. Relatórios:
  `reports/interface-v010-validation.json`, `reports/interface-v010-delta.json`
  e `reports/name-entry-v001-evidence.json`.
