# Lote ampliado v014

## Aumento efetivo de traduções

O intervalo conhecido agora é `0x1C64A06C..0x1FF30844`. A rodada acrescenta
400 ocorrências, o dobro da anterior, com 291 alvos únicos revisados, cem aliases
por identidade de todos os segmentos originais e nove novos bloqueios.

| Lote | Registros | Traduzidos | Segmentos traduzidos |
| --- | ---: | ---: | ---: |
| v013 | 1.563 | 1.241 | 1.303 |
| v014 | 1.963 | 1.572 | 1.652 |

O aumento efetivo é de **331 registros traduzidos**, contra 158 na rodada
anterior. Os 391 preservados incluem 89 adiamentos. Nomes, pausas e outras
ocorrências sem alteração não são contados como traduções novas.

Os 1.563 registros da v013 permanecem integralmente iguais no plano, inclusive
metadados, controles e a exceção `nao`. Como a ampliação acrescenta offsets
anteriores, eles aparecem depois dos quatrocentos novos na lista ordenada.
Não houve deslocamento físico de recursos do jogo.

São aproximadamente 21,74% dos 7.231 registros textuais catalogados no MAP.MCT.
Essa proporção é por registro e inclui opções, interfaces e outras mensagens;
não é uma medição exclusiva de diálogos, por palavras ou da tradução completa
do jogo. O nome histórico do lote também não comprova cobertura integral de
uma cidade ou região.

## Revisão contextual

| Trecho aproximado | Conteúdo e decisões |
| --- | --- |
| `0x1C64A06C..0x1CF57258` | Ponte, bens confiscados, Grand Master, veículo enterrado e comerciantes; instruções práticas e nomes preservados |
| `0x1D0A6C4C..0x1D0AAAA4` | Recrutamento dos mecânicos, alternativas de viagem/casamento, família e reações a ferimentos; diferença entre fala informal do irmão e cuidadosa da irmã |
| `0x1D0AAFA4..0x1D0AD7A4` | Nikolai, pintura e sequência Growgaine; negação da calvície, entusiasmo, efeitos inesperados e frustração mantidos distintos |
| `0x1D0ADAFC..0x1D0AF070` | Conversa familiar delicada; hesitação dos pais e pertencimento à família sem inventar explicações de origem |
| `0x1D0AF344..0x1D0B0198` | Alex e subordinados; diplomacia calculada, interrupções diretas e proposta de troca de informações |
| `0x1D0B0740..0x1D0B561C` | Fregueses, rumores, Exército Blueberry, contexto de Newfolk e serviços; distinguir versões dos acontecimentos e fala promocional dos soldados |

As falas foram lidas em sequência com respostas alternativas e reutilizações.
As atribuições sem rótulo explícito são inferidas do diálogo, não identificadas
automaticamente por retrato. A revisão narrativa e visual continua necessária.

Grand Master e as variantes Growgaine, Growgaine 3, Growgaine T, Growgaine L e
Growgaine A ficam preservados. Letras e números fazem parte da identificação e
das piadas. O L de Long conserva a palavra inglesa com explicação em português.
Memory Center continua Centro de Memória, conforme os lotes anteriores.
League of Uncivilized Barbarians recebe Liga dos Bárbaros Incivilizados.

As direções das ruínas conservam norte pelo deserto, noroeste e sul de East Zero.
O número 21 e `*cough*` do bar permanecem, assim como a relação entre álcool e
artilharia. O marcador literal 0 de espaços no inventário também foi preservado.
Há testes para esses detalhes. Não houve tradução em massa de tabelas de itens,
armas, tanques ou inimigos.

## Bloqueios e validação

Os nove novos adiamentos são sete controles opacos, uma terceira string sem
edição liberada e um caso que reúne as duas condições. Permanecem intactos,
assim como os oitenta adiamentos anteriores. Não houve ampliação de slots,
registros ou extents, nem relaxamento de controles para aumentar as contagens.

108 testes passaram. O novo teste reproduz a preparação de quatrocentos registros,
confere contagens, compara toda a v013 e verifica nomes de Growgaine, direções,
marcadores numéricos e a exclusividade da exceção `nao`. A política terminológica
também testa que as variantes de Growgaine não sejam confundidas.

As recusas intermediárias foram corrigidas nos alvos, reformulando frases para
caber e respeitando a posição de comandos, nomes dinâmicos, quebras e páginas.
A compilação final não teve recusas ou violações terminológicas.

A construção verificou hashes, leitura de retorno, limites SSD, diretórios e
diferenças integrais da ISO. Todos os registros modificados usam slots existentes,
sem realocação. O relatório mantém 221 avisos conservadores de largura no lote
completo. Não representam medição em pixels nem aprovação visual.

Não houve execução desta versão no PCSX2. No teste manual, priorizar uma conversa
de recrutamento/família e uma amostra de Nikolai ou Alex. Observar falante, tom,
acentos, largura, passagem de páginas, escolhas e nomes dinâmicos. Não é preciso
alcançar todas as variantes em uma sessão.

## Uso local

- `Preparar-Regiao-Inicial.cmd`: compila e valida a v014 sem nova ISO.
- `Testar-Regiao-Inicial.cmd` ou `Iniciar-Teste.cmd`: abre a versão atual.
- ISO: `work/regiao-inicial-v014/MetalSaga-ptbr-regiao-inicial-v014.iso`.
- Plano, revisão bilíngue e relatório: `work/regiao-inicial-v014/`.
- Metadados publicáveis: `reports/regiao-inicial-v014-validation.json`.

```powershell
python tools/build_translation_pilot.py --output work/reconstrucao-v014 --build-iso
python -m unittest discover -s tests
```

Para reproduzir somente a preparação em outra pasta:

```powershell
python tools/prepare_translation_lot.py --parent translations/regiao-inicial-v013.json --start-offset 1c64a06c --lot-id regiao-inicial-v014 --output work/preparacao-v014-repro
```

SHA-256 da ISO: `ad7d4b0997c073c0d7c18c556ebe9f9d11a160b999fa4a49c0687ace4c504425`.

A retenção removeu a ISO antiga v007 para manter dez imagens de trabalho.
Receita e relatórios continuam preservados; `--iso region-v007` exige reconstrução.
A v013 permanece disponível. ISO original, BIOS, saves e configurações não foram
alterados.
