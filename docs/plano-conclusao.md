# Plano para concluir a tradução

## Base e método

Manter a tradução consolidada e o perfil de layout v005 aprovado nas falas de Nina. Cada etapa produz ferramentas locais reutilizáveis, evidência por formato e um lote contextual. Separar extração, edição binária e teste visual. Não trocar confiabilidade por contagem.

A primeira triagem reproduzível está em `reports/plano-pendencias-v001.json`, obtida por `tools/plan_remaining_texts.py`. Na base v023, os 244 opacos formam 39 grupos disjuntos de spans; os 158 preservados a revisar têm 112 combinações textuais distintas. Contagens por token isolado podem se sobrepor e não devem ser somadas.

## 1 — Fechar o MAP.MCT conhecido

**Em execução:** liberar uma família de controle por vez, começando por grupos grandes com contexto coerente. Primeiro grupo: 32 registros cujo único opaco é `%B$15`, tratados na v024 com política própria e limite de tamanho mais estrito.

**Segundo grupo:** 31 registros exclusivos `%$1`, tratados na v025 com política v007. O leitor e o handler em `0x1B5DEC..0x1B5E83` confirmam a variável 1 e o formato inteiro `%d`. O caminho com f minúsculo continua bloqueado; a tradução preserva G e não fixa os números. Ver `docs/controles-numericos-v007.md`.

Depois: grupos `%N$3` (19), `%$15` (18), `%T$0` (18), `%I$0` (14) e combinações. Esses números são grupos disjuntos da base inicial, não metas garantidas. Para cada família: provar consumo/argumentos no ELF, preservação dos valores, limites dos buffers e testes negativos; só então acrescentar uma política opt-in. Não liberar sintaxe apenas ampliando regex.

Em paralelo, revisar os 14 registros com bytes nativos e os 112 conjuntos distintos de preservados: nomes, risadas e expressões podem permanecer; descrições de ação ou outros textos só recebem decisão após contexto. Registrar a justificativa por ID, sem inflar o total traduzido por mudanças cosméticas.

**Critério de saída:** cada registro conhecido traduzido, preservado por decisão explícita ou bloqueado com motivo e próximo experimento definido. Isso não prova que todo o MAP foi descoberto.

## 2 — Diário, menus e dados de itens

1. DIARY.DAT: reutilizar os 68 registros/136 campos e a ferramenta existente; rastrear controles, confirmar de onde vem o título exibido, provar acentos nessa interface e só então traduzir o conjunto. Não atribuir o antigo teste negativo a saves sem evidência.
2. S_PACK.SDA: modelar as tabelas internas de equipamentos já localizadas; separar nomes próprios de descrições genéricas, extrair IDs/referências/capacidades e criar round-trip antes da tradução.
3. SLUS_212.93: catalogar mensagens de interface com referências de código; excluir strings técnicas/debug antes de preparar lotes.
4. Investigar MMBATTLE.BIN, BTITEM.DAT, HWEAPON.DAT e TANK.DAT por evidências. Não presumir texto só pelo nome do arquivo.

**Critério de saída:** catálogo por tela/recurso, extrator/reinseridor com testes e amostra visual de cada mecanismo. Ampliar maiúsculas PT-BR faltantes quando necessárias ao conteúdo real, preservando os glifos já aprovados.

## 3 — Imagens e vídeo

Inspecionar F_COMMON.SDA, RTITLE.SDA, PASSWORD.SDA e candidatos adicionais para identificar texto realmente rasterizado. Desenvolver exportação/importação de textura preservando dimensões, paleta e metadados. Conferir DEMO.STM para saber se há texto a localizar; não presumir necessidade de edição ou dublagem.

**Critério de saída:** lista de recursos com e sem texto confirmada visualmente, assets editáveis e round-trip por formato identificado.

## 4 — Revisão contextual por cenas

Relacionar os blocos SSD a cenas/áreas/personagens apenas com evidência. Revisar a tradução por conversa, mantendo ordem de opções, humor, pistas de missões, termos técnicos e nomes protegidos. Não chamar uma cidade de completa somente porque existem textos dela no catálogo.

Gerar um checklist de cobertura por local com status confirmado/provável/desconhecido e revisão de nomes. Ajustar layout e texto com métricas, sem omitir artigos ou remover acentos para caber. Caso um texto realmente precise crescer, tratar realocação como uma investigação independente de ponteiros e extents.

## 5 — Passagem funcional e entrega

O usuário faz navegação e testes periódicos de imagens consolidadas. Cobrir progressão, escolhas, lojas, batalha, diário, salvamento/carregamento e cenas opcionais. Registrar local, ID quando conhecido, versão e defeito. A suíte binária acompanha cada mudança de parser/compilador; não repetir toda a campanha a cada frase.

Na conclusão: uma versão identificada, receitas e ferramentas reproduzíveis, glossário consolidado, lista de limitações e patch de distribuição aplicável à revisão exata da ISO original. Não distribuir ISO, BIOS, saves ou arquivos proprietários.

## Limites para evitar trabalho improdutivo

Se uma família não avançar após investigar o leitor, consumidores e amostras representativas, documentar o bloqueio e passar ao próximo recurso independente. Não inventar compatibilidade entre formatos. Construir apenas uma ISO por lote aprovado; manter no máximo dez. Preservar o histórico de receitas e relatórios.


## Estado após o primeiro passo — v024

Primeiro grupo concluído binariamente: 32 registros B15 traduzidos. Permanecem 212 opacos em 35 grupos disjuntos e 14 nativos. A triagem atual está em `reports/plano-pendencias-v002.json`. Próxima investigação: `%$1`, ainda com 31 registros exclusivos. A revisão dos preservados e a validação visual da cena continuam pendentes.

## Estado após o segundo passo — v025

São 5.821 registros traduzidos, com 31 acréscimos de preços, hospedagem, ônibus e MC Hamir. Permanecem 181 opacos em 34 grupos disjuntos e 14 nativos. Triagem em `reports/plano-pendencias-v003.json`; próximo grupo exclusivo: `%N$3` (19). Preservar os 158 registros a revisar / 112 combinações distintas.

O usuário informou que Dr. Palm está distante no save e pediu teste conjunto em uma passagem contínua. Registrar a pendência visual e continuar o trabalho técnico e a tradução compatível sem exigir acesso imediato à cena. O roteiro cumulativo da v025 inclui preços, ônibus e construção de tanques.
