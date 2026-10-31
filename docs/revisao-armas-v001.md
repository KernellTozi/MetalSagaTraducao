# Revisão completa de nomes de armas

Atualização v058: a revisão humana foi recebida e os 86 ALTERAR foram aplicados;
89 MANTER preservados. Ver docs/interface-v058.md e o relatório local
work/revisao-armas-v001/APLICACAO-ARMAS-APROVADAS.md. O gerador abaixo mantém
a auditoria histórica v055; não representa o estado atual da tradução.

Executar localmente, sem IA, APIs ou internet:

```powershell
python tools/weapon_name_review.py
```

A lista para editar fica em **work/revisao-armas-v001/ARMAS-PARA-REVISAR.md**;
o JSON completo fica ao lado, em **armas-revisao.json**. A ferramenta não
escreve no jogo ou nas ISOs. A coluna “Sua decisão” aceita aprovar, manter
original ou outra redação. Devolver o documento revisado antes de aplicar.

## Abrangência e evidência

Fonte: tabela de itens do S_PACK.SDA, base 0x820, stride 128, 1349 registros,
campo de nome de 24 bytes com NUL. O campo u32 em registro+0x1C separa os
grupos abaixo. A contagem inclui cada ocorrência, sem deduplicar IDs.

| Classe observada | Registros | Grupo de revisão |
|---|---:|---|
| 1 | 100 | Portáteis / personagens e cães |
| 10 | 30 | MAIN |
| 11 | 21 | SUB |
| 12 | 24 | SE |
| 15 | 15 | Munição especial, anexo separado |

São **175 registros das quatro classes de armas identificadas**. A seleção
não usa somente um intervalo: inclui 1042, fora dos IDs 1–99. Os registros
19 e 74 repetem Bare Hands e aparecem separadamente com a mesma proposta.
Isso não afirma que todo objeto ofensivo de outras classes seja uma arma;
acessórios e consumíveis mantêm suas classificações próprias.

Um dos 175 nomes já estava alterado: 1042, Rede elétrica. Os demais 174
estão com os nomes originais na receita atual. O anexo de 15 munições mostra
as traduções já aprovadas, incluindo as revisões das v053/v054.

Há 87 sugestões diferentes do original, incluindo aquela já aplicada, e
88 preservações conservadoras. Gibson, modelos, siglas e identidades
únicas não foram substituídos automaticamente. MAIN/SUB/SE ficam intactos.
Sugestões descritivas são propostas editoriais, sem alegação de aprovação
humana ou de contexto canônico de todas as armas.

## Limites para revisão

- Os bytes são os da codificação do projeto, não UTF-8. Acentos aprovados
  normalmente usam dois bytes. Canivete borboleta tem 18; Facão tem seis.
- O teto global histórico é **16 bytes**; ele não autoriza por si só a
  edição das armas protegidas. O campo físico admite 23 mais NUL, mas os
  consumidores/layouts precisam de prova própria antes de usar esse espaço.
- **18 propostas** ultrapassam o teto histórico e estão marcadas Investigar.
  Foram mantidas completas para o usuário decidir; não houve abreviação,
  remoção de acentos, redução de fonte ou aumento de limite.
- O JSON inclui referências às ações de batalha de mesmo nome original.
  A futura aplicação deve manter esses aliases consistentes; as exceções
  de 18/19 bytes das munições anteriores não liberam estas armas.

Os dados bilíngues e bytes originais ficam somente em work/. O arquivo
versionado `translations/sugestoes-armas-v001.json` contém IDs, hashes e
propostas próprias; preservações usam null em vez de copiar o texto original.
O relatório público é `reports/revisao-armas-v001.json`.

A validação recusa IDs ausentes/duplicados/estranhos, origem diferente,
mudança de calibre/número, controles, Unicode não suportado e divergência
entre propostas de nomes idênticos. `approved_for_application: false` é
obrigatório. Não existe caminho de aplicação destas sugestões no construtor.
