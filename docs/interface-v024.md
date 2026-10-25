# Interface v024 — continuação regular

Rodada de **11 campos novos**, preservando todos os textos anteriores:

- Seis nomes: **Sentidos finos** (861), **Sucateiro** (899), **Mapa do tesouro**
  (1015) e **Pin 10/20/30 vitórias** (1043–1045).
- Cinco descrições retomadas explicitamente: **003bb, 0049e, 0310c, 04e00,
  04e5a**. São uma arma branca que paralisa alvos orgânicos, lente elétrica
  corpo a corpo, efeito de descida de inimigos mecânicos em voo alto, botas
  enormes que impedem andar e armadura enorme de metal em que cabe o usuário.

Os textos de nome e descrição são contados separadamente. São **499 registros
de nomes** (483 rótulos distintos), **541/567 descrições** referenciadas por
**889 IDs**, e **2.104 campos/ocorrências de interface**. Isso não mede a
porcentagem de todo o jogo.

## Revisão e limitações

A descrição 003bb mantém paralisa, coerente com a proposta anterior; o alvo
orgânico continua explícito. Seu ponto final foi dispensado para respeitar os
32 bytes originais. A lente mantém o ataque corpo a corpo e usa choque para
indicar eletricidade; feixe continua sendo um efeito distinto. O efeito de
descida mantém todo inimigo mecânico em voo alto, sem reduzi-lo a robôs.
As descrições de botas/armadura conservam material, tamanho e efeito descrito.

A referência compartilhada das descrições foi preservada. O mapa tem descrição
original sobre tesouro escondido; os pins mantêm 10/20/30, com descrições de
sequência de vitórias intactas. Sucateiro traduz a habilidade Junker conforme
o glossário de sucata; não se infere seu efeito a partir do nome.

Hawk Eye continua em inglês: IDs 590 e 877 compartilham esse rótulo e o primeiro
é um componente protegido. Não se traduz somente a habilidade para quebrar
a igualdade entre aliases, nem se libera o componente por conveniência.

O ledger de nomes tem 532 selecionados, 499 aceitos, **32 pendentes** e um
preservado; somente o adiamento 861 foi retomado, com cinco novas seleções.
Descrições: cinco retomadas e **25 pendentes** (24 por espaço e um `80%%`
bloqueado), além do marcador original preservado. Os dados históricos de
todos os demais adiamentos permanecem iguais.

Mantêm-se os perfis atuais: descrições nos slots originais, nomes com teto
observado de 16 bytes no próprio preenchimento zerado, fontes/layout v005,
MAP v030 e arte v014. Nenhum novo controle, glifo, repack ou realocação.

## Uso e validação

Abra **Iniciar-Teste.cmd**, que aponta para:

`work/interface-v024/MetalSaga-ptbr-interface-v024.iso`

O usuário confere nomes e descrições no inventário/lojas e nas habilidades
durante uma partida normal. Não é necessário obter cada item para continuar.
Não houve execução do PCSX2 pelo agente; validação visual permanece pendente.

```powershell
python tools/plan_interface_menus.py
python tools/build_translation_pilot.py --draft translations/regiao-inicial-v030.json --interface-draft translations/interface-v024.json --output work/interface-reproducao-v024 --compact-output --build-iso
python -m unittest discover -s tests -p test_interface_v024.py -v
```

Passaram **41 testes distintos**: cinco do lote, 21 de descrições/preparação,
sete do teto de nomes, cinco de retenção e três da alpha. Cobrem preservação
dos alvos/patches anteriores, ledger, aliases protegidos, números, fontes e
controles aceitos, intervalos disjuntos e round-trip de recursos. Todos os
1.349 registros mantêm os atributos e referências originais.

Hash e comparação integral estão em **reports/interface-v024.json**. Uma única
ISO nova, cinco imagens de trabalho e alpha permanente preservada. Não houve
cópia ao OneDrive. O planejador local reutiliza o mesmo JSON em work/.

Comparação executada: **261 bytes diferentes em 11 intervalos autorizados**;
demais bytes e diretório ISO idênticos. SHA-256:
`7d54ad51ab381a03d3fa8a4a3e42c1ac92914919d8854806876e1019b1213a3e`.
Iniciador conferido sem abrir o PCSX2.
