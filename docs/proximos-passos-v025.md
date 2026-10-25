# Próximos passos e cobertura — base v025

Planejamento sobre interface v025, MAP v030, fontes/layout v005 e arte v014.
Nesta rodada não foram traduzidos textos, construídas ISOs ou executado o
PCSX2. A ISO v025 foi novamente conferida por SHA-256 e corresponde ao relatório.
Medições e hashes: `reports/progresso-v025.json`.

## Porcentagens verificáveis

| Catálogo e base de cálculo | Traduzidos | Cobertura por registros |
|---|---:|---:|
| MAP.MCT conhecido | 5.892 / 7.231 | **81,48%** |
| Descrições conhecidas | 541 / 567 | **95,41%** |
| Nomes fora das categorias atualmente protegidas | 516 / 565 | **91,33%** |

Esses percentuais contam registros/campos, sem ponderação por palavras, tamanho
ou tempo de jogo. Não devem ser somados ou usados como média do jogo inteiro.
Preservação correta pode impedir que uma tabela chegue a 100% de textos alterados.

MAP mantém 1.339 registros intactos, incluindo **123 adiamentos técnicos**.
O restante inclui nomes, expressões, controles e decisões de preservação;
não são 1.339 falas obrigatoriamente sem tradução. Os adiamentos incluem os
109 casos opacos e 14 nativos da base v029/v030, com N3 já decidido como nomes
de tanques preservados. Não repetir essa investigação para aumentar contagens.

A tabela de nomes possui 1.041 entradas não vazias. **476 estão fora do recorte
atual por categoria protegida**; isso é uma exclusão conservadora, não prova
de revisão editorial completa. Nos outros 565, há 516 traduções, **23 propostas
pendentes e 26 nomes não revisados**. Parte desses 49 deve permanecer em inglês.
As 516 ocorrências correspondem a 500 rótulos PT-BR distintos.

As descrições restantes são **24 bloqueadas por espaço**, uma por `80%%` e
um marcador preservado. As restrições dos 24 casos se dividem em oito somente
por bytes, cinco por bytes/quebra/linhas/colunas e onze por bytes/quebra/colunas.
Não somar verificações sobrepostas como textos diferentes. As 541 traduções
atendem 889 referências de itens; essas referências não são 889 descrições únicas.

Há **2.121 campos/ocorrências implementados de interface**, incluindo nomes e
descrições. Não existe denominador completo e aprovado para toda a interface.
As 4.299 strings ELF incluem debug, formatos e dados técnicos: não são 4.299
textos que precisam de tradução. Por isso **a porcentagem do jogo inteiro ainda
é indeterminada**; usar 81,48% apenas como indicador do catálogo MAP conhecido.

## Ordem recomendada

1. **Integridade antes de abrir ou entregar a imagem.** Planejar uma verificação
   automática de tamanho/hash e transações no iniciador, com recusa segura em
   divergências. O incidente de um byte na v024 foi restaurado, mas sua causa
   permanece indeterminada. Não aplicar correções presumidas a outras imagens.
   Esse reforço ainda não foi implementado nesta rodada.
2. **Concluir a revisão nominal dos 49 casos.** Separar definitivamente termos
   preservados, propostas naturais e bloqueios reais. Dos 23 pendentes, a primeira
   guarda atual acusa 17 casos de espaço, um glifo, quatro proteções nominais e
   um caso que passa na guarda individual mas exige revisão/alias protegido.
   Uma guarda pode esconder outras. Não prometer 49 novas traduções ou forçar
   o mínimo de 15 quando o restante exigir preservação. Manter Kevy, Kaiser,
   Saratoga, Ali Baba, AAP e os demais identificadores próprios.
3. **Resolver capacidade das descrições, não apenas encurtar.** Investigar os
   consumidores, referências internas/externas, limites e aliases do pool de
   S_PACK antes de propor reorganização. Preservar o formato histórico. Só
   liberar um perfil separado após round-trip, limites e testes próprios;
   tratar `80%%` por prova do consumidor/formatador, sem inferência por sintaxe.
4. **Fechar as lacunas reais de interface.** Esclarecer Coat e TITLE/BACK pela
   função efetiva, não por adivinhação. Revisar os 17 candidatos ELF com referência
   e 23 sem referência suficiente como candidatos, sem promoção automática.
   Auditar recortes gráficos e telas ainda não catalogadas; não redesenhar a
   arte aprovada nem recomeçar ajuda, diário, correio e procurados já tratados.
5. **Retomar os fragmentos MAP por último.** Agrupar os 123 adiamentos por
   formato/controle e retomar uma família comprovada por vez. %$0 e %$2 têm
   prioridade histórica entre os grupos ainda bloqueados. Não confundir os
   14 registros nativos com o mapeamento PT-BR das fontes.
6. **Revisão contextual e teste corrido.** Consolidar um roteiro de inventário,
   lojas, habilidades, tanques, diário, Satcom, mensagens, batalhas e diálogos.
   O usuário testa em partida normal, sem precisar obter cada item ou alcançar
   Dr. Palm imediatamente. Conferir tom, nomes, efeitos, cortes, acentos e
   escolhas; depois preparar um patch reproduzível de distribuição.

Nas próximas rodadas, reunir 15 ou mais nomes quando houver conteúdo seguro,
preservando lotes anteriores e uma única versão consolidada. Se o bloqueio
for estrutural, avançar na ferramenta ou evidência necessária em vez de repetir
tentativas de redação que percam fatos. Manter cinco ISOs e a alpha protegida;
OneDrive e desligamento somente mediante novo pedido.

## O que falta descobrir ou comprovar

- Inventário completo dos recursos visíveis fora dos catálogos atuais; não há
  comprovação de cobertura de todas as telas/cenas ou regiões do jogo.
- Limites reais de todos os consumidores antes de expandir nomes/descrições.
- Semântica dos controles e bytes nativos ainda bloqueados.
- Apresentação e contexto em todo o jogo: testes binários não equivalem a uma
  passagem funcional completa. O layout aprovado em Nina não valida toda fonte.
- Decisões editoriais finais para nomes/expressões preservados e casos ambíguos.

As ferramentas atuais continuam locais: `python tools/plan_interface_menus.py`
atualiza `work/planejamento-interface.json`. A receita e a ISO continuam v025;
este documento não libera formatos nem altera a tradução.
