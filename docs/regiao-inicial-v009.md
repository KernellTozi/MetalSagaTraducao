# Região inicial — lote ampliado v009

## Cobertura

O intervalo `0x1DF47F0C..0x1DF7ADCC` contém 777 registros: 666 traduzidos
e 111 preservados, incluindo dezesseis bloqueados. São 706 segmentos traduzidos
em 138 grupos SSD. O teste compara integralmente os 577 registros da v008:
seus alvos, bytes de origem, controles e metadados não mudaram.

| Lote | Registros | Traduzidos | Segmentos traduzidos |
| --- | ---: | ---: | ---: |
| v008 | 577 | 503 | 539 |
| v009 | 777 | 666 | 706 |

O acréscimo de 200 ocorrências é cerca de três vezes o acréscimo anterior de
66. Foram revisados 159 alvos únicos, 39 ocorrências reutilizadas por identidade
dos segmentos de origem e dois novos bloqueios. Há 163 registros traduzidos
adicionais; pausas e outras ocorrências sem alteração não inflacionam essa conta.
O recorte binário não comprova a tradução completa de uma cidade ou capítulo.

## Revisão contextual

As falas foram lidas em sequência, incluindo as respostas alternativas e as
repetições propostas. As atribuições abaixo são inferências do diálogo; não
existe identificação automática comprovada de retratos para todos os registros.

| Trecho aproximado | Conteúdo e decisões |
| --- | --- |
| `0x1DF7037C..0x1DF72564` | Visita, café e passeio com Rosa; formalidade de Sebastian, entusiasmo de Carl e conversa familiar |
| `0x1DF728A4..0x1DF74534` | Brincadeira do transportador, constrangimento no bar, aproximação e ciúme entre Rosa e Rachel; insinuações preservadas sem explicitá-las |
| `0x1DF74834..0x1DF767F8` | Despedida, amizade, retorno com Eddy e reunião familiar; mudança do humor para o afeto e a cobrança por notícias |
| `0x1DF76B2C..0x1DF777C8` | Ressurreição, Fang, Helga e aposentadoria; humor do procedimento separado do pesar e da perda |
| `0x1DF77A8C..0x1DF7ADCC` | Crossfire, conselhos de um Hunter, sucata e transporte; orientações práticas preservam rumos e necessidade de veículo/equipamento |

Quando a identidade do falante não estava suficientemente clara, agradecimentos
foram formulados sem flexão de gênero. Expressões como `Aheh`, `Mmm`, risadas e
marcações entre asteriscos foram preservadas. Os alvos continuam sujeitos à
revisão narrativa e visual; equivalência binária não comprova qualidade literária.

Foram acrescentados à política Rosa, Carl, Sebastian, Arthur, Leon, Fang, Helga,
Crossfire, Iron Slugs e Magnum Cycles. Os nomes de inimigos citados nas falas
permanecem em inglês; suas tabelas não foram editadas. O verificador agora
reconhece nomes de várias palavras mesmo quando passam de uma linha para outra.
Isso é uma checagem de nomes conhecidos, não reconhecimento geral de entidades.

## Bloqueios e infraestrutura

`map.smnn.1df78f48` e `map.smnn.1df7ac40` permanecem inteiros: o papel da terceira
string ainda não foi liberado para edição. Os quatorze bloqueios anteriores
também foram preservados. Não houve relaxamento de formatos, controles ou slots.

O carregador de receitas tinha limite de oito versões herdadas, alcançado pela
v008. O limite de proteção passou para 64, mantendo a rejeição de ciclos,
caminhos externos e chaves duplicadas. Um teste carrega dez receitas sintéticas
e verifica a recusa de um ciclo. Essa mudança afeta somente os JSON próprios,
sem alterar qualquer estrutura binária do jogo.

## Verificação

94 testes passaram. Incluem preservação do prefixo, bloqueios, segmentos
protegidos, nomes, herança e integridade de extração/reinserção. A construção
verificou hashes, leitura de retorno, limites SSD, diretórios e diferenças
integrais da ISO. Todos os registros modificados usam slots sem realocação.
As recusas das revisões intermediárias foram resolvidas nos alvos, reformulando
frases para caber e mantendo posições de controles e quebras.

O relatório conserva 88 avisos de largura no lote completo. São estimativas
conservadoras; não há medição de pixels nem aprovação visual desta versão.
Não foi executado teste no PCSX2. O perfil de fontes v002 e espaçamento v003
segue a premissa provisória autorizada pelo usuário.

## Como executar

- `Preparar-Regiao-Inicial.cmd`: compila e valida localmente, sem outra ISO.
- `Testar-Regiao-Inicial.cmd` ou `Iniciar-Teste.cmd`: abre a v009 consolidada.
- ISO: `work/regiao-inicial-v009/MetalSaga-ptbr-regiao-inicial-v009.iso`.
- Plano, revisão bilíngue e relatório completo: `work/regiao-inicial-v009/`.
- Metadados publicáveis: `reports/regiao-inicial-v009-validation.json`.

```powershell
python tools/build_translation_pilot.py --output work/reconstrucao-v009 --build-iso
python -m unittest discover -s tests
```

SHA-256 da ISO: `4e07b63b7e55bebbe1344702c3a982d557a4daaa570ea88697bb30e4bc9ea467`.

Para o teste manual, priorizar uma conversa da visita de Rosa e uma amostra dos
conselhos do Hunter/transportador. Observar naturalidade, tom, identificação de
falante, largura, nomes dinâmicos, páginas e opções. Não é preciso alcançar
todos os eventos em uma sessão.

A retenção removeu a ISO antiga da região v002 para manter dez imagens de
trabalho. Receita e relatórios permanecem; o atalho histórico `--iso region-v002`
exige reconstrução. A v008 continua disponível e a ISO original, BIOS, saves e
configurações não foram alterados.
