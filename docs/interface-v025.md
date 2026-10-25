# Interface v025 — dezessete nomes revisados

Rodada com **17 nomes novos**, sem ampliar o teto de 16 bytes, mudar fontes
ou alterar traduções anteriores. Total: **516 registros de nomes**, 500 rótulos
distintos e **2.121 campos/ocorrências de interface**. Mantêm-se 541 descrições
referenciadas por 889 IDs, MAP v030, layout/fontes v005 e arte v014.

| IDs | Traduções |
|---|---|
| 111, 123, 140, 177 | Peruca Kevy, Camisa Kevy, Vestido Kevy, Colete Kevy |
| 116, 134, 138, 183 | Coroa Kaiser, Traje Saratoga, Colete Ali Baba, Colete AAP |
| 179 | Traje cerâmico |
| 441, 460 | Pin de platina, Imagem de barro |
| 646, 647 | Aro de óculos, Trapo de jaqueta |
| 870–873 | Barril vital 1 até Barril vital 4 |

## Contexto e consistência

Nos equipamentos nomeados, **Kevy, Kaiser, Saratoga, Ali Baba e AAP** mantêm
grafia e caixa; só a designação genérica foi traduzida. Os nomes de personagens,
cidades, tanques, armas e motores não foram alterados. As descrições originais
confirmam as peças de vestuário, a coroa, o colete e as proteções. Materiais,
efeitos, preços e atributos continuam intactos.

Pin de platina preserva o acessório e o material, com o mesmo uso de Pin já
adotado para as recompensas. Imagem de barro traduz a peça decorativa e fica
distinta da **Figura de barro** (459), já traduzida. Os componentes 646/647
têm designações genéricas de aro e retalho de roupa; componentes e referências
com identificadores únicos continuam protegidos.

A série Revival Keg recebe **Barril vital**, distinta de **Barril de cura**
(Medicine Keg, 866–869). Preservam-se os números 1..4 e as descrições; as duas
descrições disponíveis para Revival informam restauração de HP de cada membro
do grupo. Não se acrescenta alegação de ressurreição ou valores não presentes
nas descrições dos níveis 3/4. Nomes não são prova adicional do efeito.

Nove pendências retomadas explicitamente: **179, 441, 460, 646, 647 e 870–873**.
Oito seleções novas: **111, 116, 123, 134, 138, 140, 177 e 183**. O ledger passa
a 540 selecionados, 516 aceitos, **23 pendentes** e um preservado. Os demais
adiamentos conservam propostas e evidências históricas. Restam também 26
nomes não selecionados, incluindo termos a preservar; isso não autoriza
traduzir todos. As 25 descrições pendentes continuam com a situação anterior.

## Uso e reprodução local

Abra **Iniciar-Teste.cmd**, que aponta para:

`work/interface-v025/MetalSaga-ptbr-interface-v025.iso`

Em partida normal, conferir listas de equipamentos, acessórios e habilidades:
nomes inteiros, acentos, números, seleção e distinção entre as duas séries de
barris. Não é preciso obter cada item para continuar. Não houve execução do
PCSX2 pelo agente; a conferência visual permanece pendente.

```powershell
python tools/plan_interface_menus.py
python tools/build_translation_pilot.py --draft translations/regiao-inicial-v030.json --interface-draft translations/interface-v025.json --output work/interface-reproducao-v025 --compact-output --build-iso
python -m unittest discover -s tests -p test_interface_v025.py -v
```

Passaram **26 testes distintos**: cinco do lote, sete do teto, seis de
planejamento, cinco de retenção e três da alpha. Verificam nomes próprios,
distinção entre objetos/séries, preservação dos alvos e patches anteriores,
apenas nove retomadas, limites, codificação, intervalos disjuntos, round-trip
e atributos/referências intactos em todos os 1.349 registros.

Hash e comparação integral ficam em **reports/interface-v025.json**. Uma única
versão nova; cinco imagens de trabalho e alpha permanente preservada. Nenhuma
cópia ao OneDrive ou mudança do emulador. As ferramentas continuam locais e
reutilizam o catálogo em work/, sem IA/APIs para as operações binárias.


## Integridade da imagem histórica

Na comparação, a v024 anterior deixou de conferir com o hash histórico:
ISO **0x1231E377**, dentro de MAP.MCT relativo **0x0EFD5377**, continha **1E**
em vez de **3E**. A correção virtual desse único byte reproduziu o hash esperado.
As imagens v021/v022/v023/v025 conferiram com seus relatórios. Não há evidência
suficiente para atribuir a causa ao hardware, software ou ao jogo.

A imagem inválida foi removida após registrar a divergência; o relatório antigo
foi preservado em work/interface-v024-invalida/relatorio.json. O construtor
existente reconstruiu a v024 inteira dos originais imutáveis, no caminho anterior,
reproduzindo exatamente seu hash histórico. Não houve alteração de bytes in-place.
A reconstrução não muda a versão de desenvolvimento: o iniciador continua na v025.

Após a restauração, a comparação integral v024→v025 passou: **217 bytes diferentes
em 17 intervalos autorizados**; demais bytes e diretório idênticos. SHA-256 v025:
`308fe9abbdb111f2df16975eecbb96bfb5c74e25f157bbb781913eec1e2d4b87`.
Evidências antes/depois e hashes ficam no relatório v025. Iniciador conferido
sem abrir o PCSX2.
