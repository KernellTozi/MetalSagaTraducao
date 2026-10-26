# Interface v038 — legendas de pintura

Tradução das doze legendas de cores/padrões de pintura, aplicadas às 228
referências da tabela de S_PAINT.SDA. São **12 traduções distintas**, não 228
frases novas. Interface acumula 3.754 campos; MAP permanece em 6.024 registros
alterados, 5.983 corpos/opções e 912 referências de rótulos traduzidas.

A receita `translations/interface-v038.json` herda integralmente a interface
v037 e continua vinculada a `translations/regiao-inicial-v037.json`, ao layout
v005 aprovado e à arte v014. As únicas diferenças da receita são o nome da
imagem, o estado da rodada e a nova seção opt-in `paint_captions`.

## Conteúdo e limites

Nomes aplicados: Azul-bebê, Rosa-claro, Espiral, Aço frio, Madeira, Guepardo,
Leopardo, Floresta, Deserto, Selva, Entardecer e Pântano. Os nomes descrevem
cores/padrões da pintura; não alteram nomes de tanques, equipamentos ou inimigos.
“Leopardo” é o rótulo curto do padrão felino de neve; “Entardecer” corresponde
ao padrão do crepúsculo. A apresentação dessas legendas precisa ser conferida
na tela real, inclusive a correspondência com o padrão selecionado.

Os botões rasterizados do editor de pintura ainda não foram traduzidos nesta
versão: são outro mecanismo. MAIN/SUB/SE, parâmetros de cores e imagens dos
padrões continuam intactos. Créditos finais, destinos, TITLE, oito textos nativos,
49 rótulos sem espaço e 25 nomes de itens permanecem nas respectivas pendências
do [mapa de descoberta](descoberta-v001.md).

## Política técnica

`tools/paint_captions.py` implementa
`paint-caption-fixed-cells-observed-ten-byte-ceiling-v001`, sem realocação.
A entrada 22 de S_PAINT contém 228 registros de 36 bytes em 0xAE6A0. O campo
do nome começa em +1, tem 23 bytes incluindo NUL; byte +0 e parâmetros +24..35
ficam intocados. Cada nome tem exatamente 19 referências, todas traduzidas
juntas. A configuração exige os doze grupos completos, sem IDs duplicados ou
seleções parciais.

O limite adotado é **dez bytes codificados**, maior comprimento de nome já
presente na tabela original, embora haja espaço físico maior. Não liberar os
22 bytes possíveis por suposição. Após o texto, o campo continua zerado; não
alterar descritores SDA, offsets, tamanho do recurso ou extents da ISO.
Exigir hashes do ELF original, recurso inteiro, tabela, janelas de instruções
e nome de cada grupo. Rejeitar controles/delimitadores, texto sem tradução,
glifos sem mapeamento e excesso de orçamento. As fontes existentes são usadas
sem novos códigos, desenhos ou métricas.

O encaminhamento original da tabela até 0x4F810 foi conferido para os 228
registros na descoberta. Nesta rodada foram acrescentadas janelas dos caminhos
0x4F810→0x3F838→0x3F910→0x3DB20. O código transfere o nome ao campo de texto;
0x3DBAC chama a rotina de comprimento, seguida do pedido de alocação
`(comprimento_em_bytes + 32) & ~3` em 0x3DBB8–0x3DBCC. Os probes executam
trechos de encaminhamento, strlen e cálculo desse pedido para as doze origens
e os doze destinos. O harness fornece registradores salvos e salta prólogos;
não executa alocador, construtor completo, conversão de glifos, GPU ou PCSX2.
Essas limitações continuam explícitas no relatório.

Leitura independente verifica as 228 células, a consistência dos aliases e a
preservação dos bytes adjacentes. Reversão de todos os patches deve recuperar
exatamente o arquivo original. A comparação da versão consolidada com v037
também exige igualdade de todos os bytes fora destes campos.

## Reprodução e teste

Preparar/validar pelo iniciador existente `Preparar-Interface.cmd`. Para
reconstruir em um diretório novo dentro de work/, usar o construtor local:

```powershell
python tools/build_translation_pilot.py --draft translations/regiao-inicial-v037.json --interface-draft translations/interface-v038.json --output work/interface-v038-reconstrucao --build-iso --compact-output
```

O construtor recusa reutilizar a mesma saída. A retenção mantém cinco ISOs de
trabalho; a alpha permanente em dist/ fica fora dessa fila. Não copiar para
OneDrive automaticamente.

A imagem entregue é `work/interface-v038/MetalSaga-ptbr-interface-v038.iso`.
Abrir pelo `Iniciar-Teste.cmd`, com preflight de integridade e sem restaurar
estado antigo automaticamente. O usuário pode testar a pintura quando chegar
a essa tela em sua partida: verificar os nomes listados, acentos, largura,
troca de seleção e correspondência entre legenda/padrão. Não é necessário
alcançá-la imediatamente para continuar engenharia independente.

## Verificações

72 testes distintos aprovados na suíte da rodada: oito novos de pintura,
descoberta existente, interface ELF histórica, fontes/layout e proteção da
ISO/retenção/alpha. A execução do planejador atualizado contabilizou 228 campos
e 12 traduções distintas de pintura, mantendo os demais catálogos anteriores.
Dados da construção e comparação integral ficam em `reports/interface-v038.json`.
Nenhum teste visual foi executado nesta rodada; o estado permanece pendente.

Comparação integral v037→v038: **1.748 bytes** modificados, exclusivamente nas
228 células autorizadas. Demais bytes, diretório ISO, diálogos, fontes, arte e
outros recursos idênticos. ISO de 1.704.427.520 bytes, SHA-256
`0b4c931e141de804200d4e42c4fe125f9013707308b1e829871f5159102727c0`.
Preflight integral aprovado. Mantidas cinco ISOs de trabalho e a alpha separada.
