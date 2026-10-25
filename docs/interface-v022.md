# Interface v022 — equipamentos e proteções

Rodada limitada a **uma frente**, com **20 nomes novos**. Total: **477 registros
de nomes**, 462 rótulos distintos e **2.077 campos/ocorrências de interface**.
Todos os demais recursos da v021 permanecem idênticos: 536 descrições/883 IDs,
MAP v030, fontes/layout v005, arte v014 e mensagens de sistema.

| IDs | Tradução |
|---|---|
| 113, 135, 151, 162 | Capacete CVC, Armadura CVC, Luvas CVC, Botas CVC |
| 127, 128, 133 | Casaco BDU, Camisa carmim, Jaqueta Bio |
| 141, 150, 161, 187 | Biquíni férreo, Braçal de tiro, Geta carmim, Traje isolante |
| 165–173 | Traje canino LV1 até LV9 |

As descrições originais foram consultadas: CVC equipa tripulantes de tanques;
BDU é vestuário de combate; a proteção elétrica justifica Traje isolante.
As siglas CVC/BDU, Bio e os níveis LV1..LV9 permanecem explícitos. Não são
alterados efeitos, números, referências ou preços. Os nomes únicos ainda
incertos permanecem fora do lote; não foram abreviados para aumentar contagens.

Dois adiamentos anteriores foram retomados explicitamente: **141 e 187**.
As outras 18 entradas ainda não haviam sido selecionadas. O ledger passa a
523 selecionados, 477 aceitos, **45 pendentes** e um preservado. As propostas
e evidências dos demais adiamentos permanecem idênticas. Há ainda 43 nomes
nunca selecionados no catálogo, incluindo termos a preservar; não são 43
traduções automaticamente autorizadas.

Mantém-se `spack-reviewed-generic-names-observed-ceiling-v002`, sem mudança no
compilador: máximo de 16 bytes mais NUL no preenchimento zerado do próprio
registro. Não há repack, realocação, crescimento de arquivos ou novas fontes.
Os 457 nomes anteriores e seus patches permanecem integralmente iguais.

## Uso

Abra **Iniciar-Teste.cmd**. Imagem:

`work/interface-v022/MetalSaga-ptbr-interface-v022.iso`

Em partida normal, confira inventário, lojas e equipamentos: nomes inteiros,
acentos, alinhamento e níveis dos trajes caninos. Não é necessário obter todos
os itens para continuar. O agente não executou o PCSX2 nesta rodada; a
validação visual continua pendente do usuário.

Reprodução local, sem IA/APIs:

```powershell
python tools/plan_interface_menus.py
python tools/build_translation_pilot.py --draft translations/regiao-inicial-v030.json --interface-draft translations/interface-v022.json --output work/interface-reproducao-v022 --compact-output --build-iso
python -m unittest discover -s tests -p test_interface_v022.py -v
```

## Verificação

Passaram **26 testes distintos**: cinco novos do lote, sete do teto de nomes,
seis de planejamento, cinco de retenção e três da alpha. Incluem preservação
dos patches anteriores, controles, siglas/níveis, codificação, recusa de
padding inválido, round-trip e atributos intactos em todos os 1.349 registros.

O relatório `reports/interface-v022.json` registra o hash da imagem e a
comparação integral com a v021. Mantêm-se cinco ISOs de trabalho, além da
alpha permanente. Somente uma nova ISO consolidada foi produzida nesta rodada.

Próximas pendências continuam sendo nomes sem representação natural dentro
dos limites atuais, limites do pool de descrições e semântica de TITLE/BACK.
Não liberar novos glifos, nomes protegidos ou controles por semelhança.

Comparação executada: **270 bytes diferentes em 20 intervalos autorizados**;
demais bytes e diretório ISO idênticos. SHA-256:
`f0d33e8574cdbfee95d349d88a66353ee1292e067a3d5d05bedb6aff4a483230`.
Iniciador conferido sem abrir o PCSX2.
