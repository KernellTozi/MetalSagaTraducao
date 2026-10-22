# Lote ampliado v016

## Escopo

O intervalo passa a `0x1282F8CC..0x1FF30844`. Foram acrescentadas oitocentas
ocorrências: 507 alvos próprios revisados, 270 reutilizações por identidade de
todos os segmentos originais e 23 bloqueios técnicos. As reutilizações também
foram conferidas no contexto disponível; a identidade binária sozinha não
constitui revisão de tom.

| Lote | Registros no recorte | Registros traduzidos | Segmentos traduzidos |
| --- | ---: | ---: | ---: |
| v015 | 2.763 | 2.165 | 2.275 |
| v016 | 3.563 | 2.806 | 2.950 |

O ganho efetivo é de **641 registros traduzidos**, sem contar nomes, risadas,
pausas e outras ocorrências intencionalmente preservadas. Os 2.763 registros
anteriores permanecem idênticos em texto e metadados. O teste compara toda a
lista da v015 ao sufixo da nova lista, após os oitocentos registros acrescentados.

São aproximadamente 38,81% dos 7.231 registros textuais catalogados no MAP.MCT.
Essa proporção inclui opções, mensagens de sistema e outros textos; não mede
palavras, apenas diálogos ou a tradução completa do jogo. O nome histórico do lote
também não comprova cobertura integral de uma região.

## Cenas e decisões

| Intervalo novo | Conteúdo e critérios |
| --- | --- |
| `0x1282F8CC..0x128363DC` | Comércio, estação, preços, passageiros, curry e avisos. Distinguir queixas de comerciantes do discurso de proteção dos soldados |
| `0x137092D4..0x137214CC` | Viagem de trem, classes, cassino, Catherine e Gluttony, Dalton Brothers e boneco. Avisos formais, gagueira, voz infantil e ameaça recebem tons distintos |
| `0x1476DA74..0x1476E85C` | Piloto, avião, Sky Demon/B2 Manta Ray e Eagle 1. Conservar as variantes de reação conforme os inimigos derrotados e a história de pai e avô |
| `0x14AA21C4..0x14AB366C` | Dowan, porto e polvos, navio, rumores, trabalhadores, combustível e comércio. Preservar direções, piadas, preços e mudanças de estado das missões |
| `0x1576A20C..0x1576F2AC` | Shaka Khan, Fang, Rouge Rogues e integrantes da gangue. Manter suspense de identidade, provocações e contraste com o zelo pelas três refeições |
| `0x169B6AB4..0x169B8760` | Visita à Catedral Muscular, adesão e confisco de equipamento. Completa o trecho que antecede o sermão já trabalhado na v015 |

As fronteiras são offsets do recorte, não prova automática de início ou fim de
cada cena. Falantes sem associação comprovada continuam inferidos pela sequência
e pelos rótulos disponíveis; não foi feito novo mapeamento de retratos.

Continental Railroad recebe Ferrovia Continental. Preservar Catherine, Gluttony,
Fredrick, Shasta, Marceau e Joe; o brinquedo não pode virar um objeto substituível
na fala da criança. Preservar também Curry Lunch, Curry Guru e Number Hunter.
As variantes de Sky Demon, B2 Manta Ray, Eagle 1 e Krak Cannon mantêm os nomes.

O personagem que procura tanques conserva seu jeito peculiar de falar, coerente
com a v015. A Hunter aposentada usa voz ríspida, e o personagem que tosse mantém
as marcações literais e as insinuações. Os rumores de moradores não viram fatos
confirmados pelo relatório.

Os apelidos «Derringer» Jack, «Berserker» Joe e «Demon» Doc Solomon ficam
preservados como identificadores completos. As provocações de Shaka Khan mantêm
o jogo de palavras musical com sucesso e a expressão dançar conforme a música.
Os miados, risadas e marcações como `*sob*`, `*snore*` e `*cough*` continuam literais.

A política de nomes foi ampliada com identificadores completos, sem tratar
palavras genéricas isoladas como Demon como nomes obrigatórios em qualquer
contexto. Não houve tradução em massa de tabelas de equipamentos ou inimigos.

## Integridade e limitações

Os 757 registros sem alteração incluem 143 adiamentos. Dos 23 novos bloqueios:

- Doze têm controles opacos.
- Oito têm terceira string sem edição liberada.
- Dois reúnem ambas as condições.
- Um tem bytes nativos cuja edição continua bloqueada.

Nenhuma dessas restrições foi relaxada. Os alvos foram reformulados quando
necessário para caber nos slots e conservar comandos, páginas, quebras, escolhas
e spans vazios. Nenhum registro ou extent foi ampliado. A exceção ASCII `nao`
continua restrita ao registro anteriormente autorizado `map.msg.1df8bec0`.

O teste novo reproduz a preparação do recorte, confere preservação integral da
v015 e bloqueios, além de nomes, direções de caça, três refeições e valores de
10G, 100G e 150G. A suíte cobre também extração, fontes, instruções do patch de
espaçamento, reinserção e construção de imagens. Testes de retenção fazem
remoções reais somente em pastas temporárias isoladas.

110 testes passaram na suíte completa. Após os dois últimos ajustes de redação,
o teste de regressão da v016 foi executado novamente e passou. A compilação final
não teve recusas ou violações de terminologia.

A ISO tem 1.704.427.520 bytes. A comparação integral verificou que os 223.663
bytes diferentes correspondem exatamente aos patches previstos, incluindo fontes
e espaçamento. O diretório do disco permanece idêntico. São 772 grupos SSD no
recorte. Há 308 avisos conservadores de largura, sem medição em pixels. A aprovação
binária não equivale a teste de execução ou à aprovação de tipografia.

Não houve execução desta versão no PCSX2 pelo Codex. No próximo teste manual,
observar alguma sequência disponível de trem ou Dowan: escolhas, passagem de
páginas, nomes dinâmicos, acentos e largura. A história de Catherine e o ursinho
é uma boa amostra narrativa; os avisos de destino permitem conferir Alice One
e East Zero. Não é necessário alcançar todos os encontros numa sessão.

## Uso local

- `Preparar-Regiao-Inicial.cmd`: compila e valida a v016 sem gerar outra ISO.
- `Testar-Regiao-Inicial.cmd` ou `Iniciar-Teste.cmd`: abre a ISO atual.
- ISO: `work/regiao-inicial-v016/MetalSaga-ptbr-regiao-inicial-v016.iso`.
- Revisão bilíngue, plano e relatório completo: `work/regiao-inicial-v016/`.
- Metadados próprios: `reports/regiao-inicial-v016-validation.json`.

```powershell
python tools/build_translation_pilot.py --draft translations/regiao-inicial-v016.json --output work/reconstrucao-v016 --build-iso
python -m unittest discover -s tests
```

Preparação reproduzível, sem tradução automática nem ISO:

```powershell
python tools/prepare_translation_lot.py --parent translations/regiao-inicial-v015.json --start-offset 1282f8cc --lot-id regiao-inicial-v016 --output work/preparacao-v016-repro
```

A retenção removeu a ISO experimental v009 para manter dez imagens de trabalho.
A receita e os relatórios históricos continuam preservados. O atalho v009 exige
reconstrução caso volte a ser necessário; a v015 permanece disponível. Originais,
BIOS, saves e configurações não foram alterados.

SHA-256 da ISO:
`0dcbb7a8602c2733b12b369a64aacbf956fabace02bba678dba70bf75da95c65`.
