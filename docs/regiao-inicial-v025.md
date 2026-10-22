# Lote v025 — preços, hospedagem e ônibus

A v025 acrescenta 31 registros traduzidos: preços e opções de pagamento em bares e hospedarias, chegada de ônibus e entrega de dinheiro a MC Hamir. Preserva integralmente as 5.790 traduções da v024 e os nomes protegidos. São **5.821 alterados de 7.231** registros conhecidos do MAP.MCT, aproximadamente 80,50%. Essa proporção não mede palavras, áreas completas ou o jogo inteiro.

Os 1.410 registros intactos incluem 195 adiamentos: 181 com controles opacos, distribuídos em 34 grupos disjuntos, e 14 com bytes nativos. Há ainda 599 registros de controles/pontuação, 458 sugestões conservadoras de nomes/expressões e 158 preservados sujeitos a revisão contextual. Essas categorias não autorizam edição automaticamente.

O controle `%$1` representa um valor numérico variável; a política restrita e a evidência no ELF original estão em [controles-numericos-v007.md](controles-numericos-v007.md). Nenhum preço foi fixado na tradução. A receita herda a v024, retoma explicitamente 31 IDs e mantém o layout v005 aprovado nas falas de Nina.

## Como executar

- `Preparar-Regiao-Inicial.cmd`: recompila e valida localmente, sem criar ISO.
- `Testar-Regiao-Inicial.cmd` ou `Iniciar-Teste.cmd`: abre a ISO consolidada atual.
- Receita: `translations/regiao-inicial-v025.json`.
- Textos, revisão bilíngue e relatório completos: `work/regiao-inicial-v025/`.
- ISO: `work/regiao-inicial-v025/MetalSaga-ptbr-regiao-inicial-v025.iso`.

```powershell
python tools/build_translation_pilot.py --draft translations/regiao-inicial-v025.json --output work/rebuild-v025 --build-iso
python tools/audit_translation_coverage.py --build-dir work/regiao-inicial-v025 --output work/auditoria-v025-nova
python tools/plan_remaining_texts.py --build-dir work/regiao-inicial-v025 --output work/pendencias-v025-novas.json
```

## Conferência posterior no save corrido

Não houve navegação ou execução desta versão no PCSX2 pelo Codex. Por orientação do usuário, a validação visual dessas cenas será acumulada para uma passagem contínua. Não bloquear o avanço pela distância de Dr. Palm no save.

| Contexto textual | Amostra | Observar quando encontrar |
| --- | --- | --- |
| Bar e pagamento de rodada | `map.smsg.038d5388` | Número antes de G; confirmação e recusa com efeito correto |
| Hospedaria | `map.2snm.057cdddc` | Preço variável; opções completas; rótulo original protegido |
| Ônibus | `map.msg.06493814`, `map.msg.06493a84` | Minutos dinâmicos e quebra de linha |
| MC Hamir | `map.msg.12824d2c`, `map.msg.128256fc` | Quantia entregue e nome preservado |
| Hospedaria, resposta sobre gorjeta | `map.2snm.1df4712c` | A resposta negativa e a gorjeta mantêm o sentido e fluxo |
| Construção de tanques, herdada da v024 | `map.smsg.1fd45128`, `map.smsg.1fd46774` | Apelido, páginas, escolhas e aviso de perda de equipamento |

Os contextos acima vêm dos textos e rótulos, não de um vínculo automático comprovado com todas as cidades ou cenas. Não usar savestate antigo como prova de que o conteúdo da nova ISO foi carregado. Preservar os saves existentes.

## Cobertura e próximos passos

São 6.231 segmentos traduzidos no catálogo de 1.595 grupos SSD. Há 656 registros com avisos conservadores de largura; não são medidas em pixels. O lote novo acrescenta um desses avisos, nas opções de `map.2snm.0a6113fc`. A tradução mantém o limite original em bytes, mas o layout exige conferência visual posterior.

Próximo grupo recomendado: `%N$3`, com 19 ocorrências exclusivas; depois `%$15` e `%T$0`, com 18 cada. Investigar cada consumidor e seus argumentos antes de liberar edição. Manter o extrator local, as receitas anteriores e a separação entre evidência binária e teste no jogo.

## Integridade automatizada

A suíte completa passou: 159 testes em 554,645 segundos. Inclui comparação integral dos 7.231 descritores com a v024: somente os 31 IDs retomados mudam de tradução e de bloqueio; todas as 5.790 traduções anteriores permanecem iguais. Foram conferidos controles, bytes, slots, offsets, rótulos e limites por segmento. Evidência de execução em `reports/regiao-inicial-v025-tests.json`. Isso não equivale a execução no PCSX2.

A ISO tem 1,704,427,520 bytes; comparação integral: 483,814 bytes alterados, todos previstos pelos patches. Diretórios e extents preservados. SHA-256: `ae8987c8431813c64fa6b9d92ec9dfce398f6401b9279bcaa7f6a7eb03292e7d`.

Uma releitura independente confirmou que o ELF e as duas GFI são idênticos byte a byte aos recursos da ISO de layout v005 aprovada. Relatórios próprios em `reports/regiao-inicial-v025-validation.json`, `reports/regiao-inicial-v025-coverage.json` e `reports/plano-pendencias-v003.json`.

A retenção removeu somente a ISO gerada v017, a mais antiga elegível, e mantém dez imagens: v018 a v025 e layouts v004/v005. A ISO original, BIOS, saves e configurações foram preservados. Receitas e relatórios históricos continuam disponíveis.
