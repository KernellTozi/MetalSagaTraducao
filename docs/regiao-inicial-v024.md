# Lote v024 — construção e reforma de tanques

A v024 retoma 32 registros antes bloqueados por `%B$15`, sem ampliar o catálogo de 7.231 registros. São 5.790 registros alterados, contra 5.758 na v023; 1.441 permanecem intactos, incluindo 226 adiamentos. Aproximadamente 80,07% dos registros catalogados estão alterados; essa proporção não mede palavras ou o jogo inteiro.

O contexto textual retoma Dr. Palm e seu assistente Thursday, seguindo a revisão anterior do glossário; isso não deriva de um mapeamento automático de retratos. O lote cobre conversa sobre apelido, projeto, escolha de chassi/armas, coleta de sucata, desmontagem do tanque existente e fabricação de C Unit a partir de um chip. Preserva nomes de tanques, armas, Thursday, C Unit e risadas. Os riscos e escolhas da reforma, inclusive perda dos equipamentos, continuam explícitos na tradução.

A política `fixed-record-b15-preserved-slots-v006` é restrita ao comando exato e está em `docs/controles-b15-v006.md`. A receita declara `layout_profile: ptbr-layout-v005`; o construtor respeita esse vínculo e recusa override incompatível. Receitas antigas sem esse campo mantêm o fallback histórico, e o extrator não muda.

## Uso

- `Preparar-Regiao-Inicial.cmd`: recompila e valida a receita atual, sem criar ISO.
- `Testar-Regiao-Inicial.cmd` / `Iniciar-Teste.cmd`: abre a imagem consolidada atual.
- Receita: `translations/regiao-inicial-v024.json`.
- Plano, revisão bilíngue e relatório completos: `work/regiao-inicial-v024/`.
- ISO: `work/regiao-inicial-v024/MetalSaga-ptbr-regiao-inicial-v024.iso`.

```powershell
python tools/build_translation_pilot.py --draft translations/regiao-inicial-v024.json --output work/rebuild-v024 --build-iso
python tools/audit_translation_coverage.py --build-dir work/regiao-inicial-v024 --output work/auditoria-v024-nova
python tools/plan_remaining_texts.py --build-dir work/regiao-inicial-v024 --output work/pendencias-v024-novas.json
```

## Teste visual pendente

O Codex não navegou nem executou esta versão no PCSX2. A aprovação anterior dos acentos permanece restrita ao contexto de Nina. Quando alcançar o personagem responsável por construir tanques, conferir o apelido inserido em `%B$15`, as páginas, escolhas e os avisos de desmontagem/perda de equipamento. Thursday deve continuar em inglês; não há necessidade de jogar autonomamente até essa cena.

Amostras: `map.smsg.1fd45128` (atendimento e opções), `map.smsg.1fd46774` (alerta de desmontagem), `map.smsg.1fd46e88` (chassis), `map.msg.1fd4a7dc` (chip para C Unit). Os comandos são preservados integralmente, sem gravar um apelido fixo na tradução.

## Integridade executada

A suíte completa passou: 152 testes em 504,436 segundos. A regressão da v024 compara integralmente as 5.758 traduções anteriores, os 7.231 descritores e os 32 IDs retomados. A exceção de bloqueio muda somente nesses 32 descritores; os demais permanecem iguais. As opções de chassis e equipamentos com nomes próprios não foram traduzidas.

São 6,173 segmentos traduzidos em 1,595 grupos SSD. Há 655 avisos conservadores de largura, sem medição em pixels ou aprovação visual automática.

A ISO tem 1,704,427,520 bytes. A comparação integral encontrou 482,019 bytes diferentes do original, todos previstos pelos patches. Diretórios, tamanhos e extents foram preservados. O perfil efetivo do executável é `ptbr-layout-v005`.

SHA-256: `a9ca31b231dc209f1ed0c3a52adb36cd12d63751c6db4bf9b2ac60dd70152f38`.

A auditoria confirma 226 adiamentos: 212 opacos em 35 grupos disjuntos e 14 com bytes nativos. O próximo maior grupo exclusivo é `%$1`, com 31 registros; não foi liberado nesta versão. Os 158 preservados continuam sujeitos a revisão contextual. Relatórios próprios em `reports/regiao-inicial-v024-validation.json`, `reports/regiao-inicial-v024-coverage.json` e `reports/plano-pendencias-v002.json`.

A retenção removeu a ISO v016 mais antiga e mantém dez imagens de trabalho: v017 a v024 e layouts v004/v005. A ISO original fica fora da contagem. Receitas e relatórios foram preservados; BIOS, saves e configurações não foram alterados.

Uma releitura independente comparou o ELF e as duas GFI com a ISO de layout v005 aprovada: os três recursos são idênticos byte a byte. A prova e os hashes ficam em `validated_font_profile_inheritance` no relatório de validação.
