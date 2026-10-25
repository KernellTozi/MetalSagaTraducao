# Interface v031 / MAP v032 — sucata para construção de tanques

Rodada normal, limitada a **oito diálogos** de contagem e coleta de sucata,
escolha de projeto e adiamento da construção. Inclui Dr. Palm e seu assistente;
preserva o tom depreciativo do assistente e a insistência de Palm em adiar.
Não altera valores, nomes de tanques ou opções de execução do jogo.

São **5.969 registros MAP traduzidos**, contra 5.961 da v030. Todos os patches
anteriores permanecem idênticos. Adiamentos caem de 49 para **41**: 19 nomes
N$3 preservados, 14 registros nativos e oito com outros controles não liberados.
Interface continua com 3.451 campos, 566 descrições/925 referências e 516 nomes
de itens/25 pendentes. Fontes/layout v005, título v014 e gráficos anteriores
permanecem byte a byte iguais. Não é uma porcentagem de todo o jogo.

## Como testar e reproduzir

Abra **Iniciar-Teste.cmd**. ISO:

`work/interface-v031/MetalSaga-ptbr-interface-v031.iso`

SHA-256: `375f1dede3ffb0f7adf40affd2da934e4dfe117991e94040b12ea9edb8d9efbe`

Tamanho: 1.704.427.520 bytes. O iniciador exige relatório concluído, tamanho,
hash e ausência de transações/arquivos parciais, sem restaurar save state.
Nenhuma navegação PCSX2 foi realizada nesta rodada. Conferir as cenas quando
aparecerem na passagem normal; não é necessário alcançar Dr. Palm agora.

Observar a quantidade de toneladas com duas casas decimais, nomes dinâmicos,
quebras e escolhas do projeto. Nenhum dos oito textos gera aviso conservador
de linha mais larga que sua origem. Isso não substitui avaliação visual,
especialmente quando o nome do tanque é longo. O separador decimal original
do jogo não foi trocado por vírgula.

`Preparar-Interface.cmd` valida sem criar ISO. `Auditar-Traducao.cmd` usa a
construção compacta atual; o plano é reconstruído em memória com hashes.
Para reproduzir a ISO em uma pasta nova:

```powershell
python tools/build_translation_pilot.py --draft translations/regiao-inicial-v032.json --interface-draft translations/interface-v031.json --output work/interface-v031-reproducao --compact-output --build-iso
```

## Controle decimal restrito

Ferramenta `tools/control_scaled100.py`; política opt-in
`fixed-record-scaled100-preserved-slots-v013`, herdeira da v012. Autoriza
somente **%$0f100, %$2f100 e %$13f100**, tratados como tokens completos e
imutáveis, inclusive o divisor literal 100. Não libera o sufixo f em geral,
outros índices/divisores, formatos malformados ou bytes nativos.

O handler original em **0x1B5DEC..0x1B5E84** lê primeiro a variável e depois
o literal após f pelo leitor **0x1B5A30..0x1B5AD0**. Converte os inteiros com
sinal para precisão simples, divide e encaminha ao formato **%.2f**, localizado
em **0x349DB8**. A sequência original não foi modificada.

Executados **24 probes** dos caminhos de instruções e do leitor original,
com RAM sintética e modelo FP32 finito: três tokens, oito valores por token,
incluindo zero, valores próximos de 100 e limites com sinal. O helper de
conversão em 0x183E38 foi substituído por um retorno sentinela para verificar
o encaminhamento ao formatador. O helper completo, o formatador, o emissor e
o PS2 não foram executados. Esses probes comprovam consumo/argumentos/caminho,
sem constituir validação visual ou promessa de arredondamento no emulador.

Mantidos slots originais, orçamento de bytes por segmento, limites de opções,
ordem dos tokens, quebras, spans vazios, rótulos, cabeçalhos, offsets e tamanhos.
Sem repack ou crescimento para esta família. Uma falha recusa o lote inteiro.
O lexer/fingerprints históricos e as permissões das políticas antigas continuam
iguais; v012 ainda bloqueia os três tokens com f.

## Verificações e continuidade

Foram aprovados **90 testes distintos**: 48 de controles, 12 de reinserção,
três de preservação do lote, seis de cobertura, sete de preflight, seis de
planejamento, cinco de retenção e três da alpha. A suíte completa de interface
da v030 não foi repetida: nenhum texto ou renderizador dessa interface mudou.
A construção recompila a interface e a comparação integral confere todos os
bytes da imagem: **943 bytes diferentes em somente oito registros MAP**;
todos os demais bytes, incluindo fontes e arte anteriores, são iguais. Evidências em
`reports/interface-v031.json`; triagem em `reports/plano-pendencias-v009.json`.

Uma ISO nova consolidada; mantidas cinco ISOs de trabalho e a alpha permanente.
Originais, BIOS, saves e configurações preservados. Sem OneDrive ou desligamento.
Próximas pendências continuam TITLE no chamador, controles restantes e nomes
bloqueados por espaço/identidade; não liberar formatos por semelhança nem
encurtar nomes sacrificando o contexto.
