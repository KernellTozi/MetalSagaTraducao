# Consistência contextual dos nomes — interface v044

Rodada solicitada para conferir referências aos nomes aprovados, partindo da
interface v043/MAP v038. Não é um novo lote de nomes nem autorização para as
14 propostas pendentes ou as 16 revisões bloqueadas.

## Cobertura e resultado

Varredura local de **10.682 campos**, abrangendo **527 nomes aplicados** e
**580 termos distintos**: nomes ingleses originais e traduções anteriores
substituídas pelas revisões aprovadas. O scanner considera limites de palavras,
quebras, pipes e tags HTML, mantendo a origem de cada ocorrência.
Termos com menos de quatro caracteres ficam fora da busca literal para evitar
coincidências com siglas e fragmentos; não se deduz cobertura desses termos.

Encontradas **81 ocorrências**, incluindo integralmente as **69** do relatório
anterior. Todas receberam uma decisão vinculada ao hash do texto e do termo:

- **25 ocorrências corrigidas**, em **24 campos**; uma página de ajuda contém
  dois ingredientes. São 16 campos de interface e oito registros MAP.
- **56 ocorrências preservadas**, pois o contexto não corresponde ao item
  renomeado, ou o nome já está correto.
- **Zero ocorrências sem decisão** na nova conferência deste recorte.

Não interpretar a contagem como prova de que todas as referências semânticas,
flexões, imagens ou textos ainda desconhecidos do jogo foram encontrados.
As correspondências são candidatos de uma concordância literal; a decisão
contextual, não a busca, autoriza a correção.

## Correções aplicadas

| Conjunto | Correção | Campos |
| --- | --- | ---: |
| Aviso de equipamento | Falta um Teleportador | 1 |
| Aviso de detector | Requer detector de metais | 1 |
| Receita de curry na ajuda | Secreção doce e Massa gelatinosa | 1 |
| Descrições de munição auxiliar | Projétil extra, com efeitos preservados | 11 |
| Descrição da unidade da Alpha Series | Unidade de dados | 1 |
| Lista de nomes de mapa | Metade do mapa | 1 |
| Conversa de extração/entrega da unidade | unidade de dados | 6 |
| Pedidos de reparo do caminhão | Kit de reparo | 2 |

O aviso original de detector tem 26 bytes. Os nomes completos Detector básico
e Busca-metais não cabem juntos nesse literal; a frase de categoria identifica
a necessidade sem privilegiar somente um dos dois aparelhos ou inventar um
novo nome de item. Não se alterou o comportamento da verificação.

Os seis diálogos de unidade de memória dizem memory unit no original. A
descrição do item 1012 o identifica como unidade da Alpha Series. A referência
ao objeto acompanha Unidade de dados; lembranças e memórias da personagem
continuam palavras naturais, sem troca automática do substantivo.

Os dois pedidos de Repair Kit foram conferidos na fonte original e permanecem
distintos de Mechanic Kit. O opt-in remove só o aviso de proteção de Repair Kit
nesses dois corpos exatos, com hash da origem e do destino vinculado.

## O que foi preservado e por quê

- 19 avisos de cartão de memória e 17 referências ao Centro de Memória.
- Memória da personagem e inscrição em memória de uma vitória.
- Chip de memória para C Unit: origem e contexto distintos da unidade 1012.
- Teleporte como ação, distinto do aparelho Teleportador.
- Armário como categoria de mobília ou objeto comum de uma cena.
- Bloqueio militar e o verbo regenerar, distintos de nomes de habilidades.
- Treasure Map na loja e em descrição compartilhada de fragmentos, distinto
  de Cache Map/Pista secreta. Não renomear mapas diferentes pelo tema.
- Nomes/qualificadores de outros inimigos, Junk Zombies e instalações CS Plant.
- Atirador dentro de Franco-atirador: o rótulo já estava correto.

O ledger completo, só com metadados e decisões, fica em
`translations/consistencia-nomes-decisoes-v001.json`. As fontes, contextos
completos e concordâncias antes/depois permanecem em
`work/consistencia-nomes-v001/`, fora do Git. Não foi necessária nova decisão
do usuário para os casos deste recorte.

## Segurança e reprodução

`translations/consistencia-nomes-v001.json` vincula a interface v043 por hash,
16 caminhos de campos e oito traduções narrativas exatas. Compilar por
`translations/interface-v044.json` e `translations/regiao-inicial-v039.json`.
`tools/name_reference_review.py` recusa alterações adicionais em ambos.
O compilador histórico e a política terminológica global permanecem estritos.

As 12 descrições usam o repack já comprovado do mesmo pool, com revisão opt-in
dos alvos exatos. Todos os aliases lógicos são mantidos. Permanecem 566
descrições; pool com 18.493 bytes usados e 1.667 livres. Somente os ponteiros
de descrição já previstos pelo mecanismo acompanham o novo empacotamento;
nomes e atributos não mudam. Nada foi realocado para fora do pool original.

Não houve novo nome aplicado: continuam **527 nomes, 14 pendentes, 3.822 campos
de interface e 6.024 registros MAP alterados**. Revisões não contam como nova
cobertura. Fontes/layout v005 e arte aprovados permanecem.

Conferência local reproduzível, sem IA/APIs/rede:

```powershell
python tools/audit_name_consistency.py --recipe translations/interface-v044.json --decisions translations/consistencia-nomes-decisoes-v001.json --output work/minha-conferencia-nomes.json
python -m unittest discover -s tests -p test_name_consistency.py
```

Usar um arquivo de saída novo. O auditor exporta candidatos e verifica as
decisões vinculadas; não modifica textos, receitas ou ISO. Termos novos ou
textos alterados deixam de ser considerados revisados automaticamente.

**105 testes passaram**, oito novos, incluindo escopo exato, preservação dos
nomes, rejeição de alterações extras, identidade dos dois Repair Kit, tags,
classificação dos 81 casos, detecção de novos casos e round-trip completo do
pool com leitura de todas as referências de descrição. Não houve execução do
PCSX2 nesta rodada: revisão visual/contextual em partida contínua segue com o
usuário. Sem OneDrive ou desligamento automático.

O verificador de versões também foi corrigido: configurações de nomes
inteiramente iguais são preservação, não uma nova aplicação da transição
v042 → v043. Ele continua validando integralmente os patches e a imagem;
o retorno antecipado só dispensa a normalização de prefixos desnecessária.

## Entrega consolidada e integridade

`Iniciar-Teste.cmd` usa
`work/interface-v044/MetalSaga-ptbr-interface-v044.iso`.
`Preparar-Interface.cmd` valida interface v044/MAP v039.
Tamanho: 1.704.427.520 bytes. SHA-256:
`d139161f28152b90d50537c86195908be367cfc37fab597784fe7f570d97c763`.

A comparação integral com v043 confirmou **4.110 bytes diferentes em 136
patches**, incluindo os transportes de pool/ponteiros necessários às revisões.
São oito registros MAP, uma página NDATA, dois literais ELF e 125 patches
S_PACK. Não confundir patches físicos com os 24 campos lógicos revistos.
Diretório da imagem, nomes de itens e fontes/layout preservados; diferenças
inteiramente explicadas pelo lote. Preflight integral aprovado, sem journal
pendente. Cinco ISOs de trabalho e SHA-256 da alpha conferidos.

Relatórios em `reports/interface-v044.json` e
`reports/interface-v044-delta.json`. Das 69 ocorrências antigas, 19 receberam
correção e 50 foram preservadas por contexto; as 12 descobertas adicionais
completam o total de 81. Os oito testes específicos foram repetidos e passaram
após a correção do normalizador. Isso não constitui validação no PCSX2.
