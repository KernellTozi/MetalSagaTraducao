# Alpha v001 preservada

**Registro histórico, substituído por nova ordem do usuário:** a antiga ISO
alpha foi removida após a criação e conferência do backup v059. A referência
atual é dist/backup-v059/MetalSaga-ptbr-backup-v059.iso; ver
docs/falantes-lookup-v001.md e reports/backup-v059.json. As instruções abaixo
descrevem a preservação antiga e não autorizam recriá-la automaticamente.

Em 23/10/2026 o usuário pediu que a última versão disponível fosse preservada como alpha. O snapshot é a **interface v001**, com os 88 textos de interface sobre os 5.892 diálogos traduzidos v029 e layout `ptbr-layout-v005`. A v002 é posterior e não substitui esta alpha.

- Arquivo: `dist/alpha-v001/MetalSaga-ptbr-alpha-v001.iso`.
- Tamanho: 1.704.427.520 bytes.
- SHA-256: `f928e0c375db669e16f078d6a0b7a4bd053ab3e933e7732e3772f14beb00bc58`.
- Origem: `work/interface-v001/MetalSaga-ptbr-interface-v001.iso`, código/receita no commit `0ce9b22`.
- Manifesto próprio: `reports/alpha-v001.json`.

`tools/archive_alpha.py` copiou a imagem, comparou o hash completo e marcou a cópia como somente leitura. A cópia é independente, não é hardlink. O programa recusa sobrescrevê-la. A pasta dist/ já é ignorada no Git. Não enviar a ISO ao GitHub.

**Exceção de retenção autorizada pelo usuário:** a alpha fica fora de work/, onde opera `tools/iso_retention.py`. Manter dez ISOs de trabalho, além desta cópia permanente. Não apagar, substituir ou incluir a alpha na fila de retenção. A ferramenta de retenção recusa executar contra dist/. O atributo de somente leitura ajuda contra alterações acidentais; não é backup contra falha do disco.

O snapshot não representa aprovação visual de todo o jogo ou da interface nova. Preserva exatamente o estado escolhido pelo usuário. Para reproduzir, usar a receita `translations/interface-v001.json` sobre a v029, conforme `docs/interface-v001.md`; não usar uma receita futura sob o mesmo nome alpha.
