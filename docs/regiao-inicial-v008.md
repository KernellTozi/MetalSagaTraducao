# Região inicial — lote consolidado v008

O intervalo `0x1DF47F0C..0x1DF6F6C8` contém 577 registros: 503 traduzidos
e 74 preservados, incluindo os mesmos quatorze bloqueios. São 539 segmentos
traduzidos em 114 grupos SSD. A v007 tinha 511 registros e 442 traduzidos;
o acréscimo é de 66 ocorrências e 61 traduções. O teste compara integralmente
os 511 registros anteriores, sem alteração de seus alvos ou metadados.

## Conteúdo e limites

O novo recorte inclui o Disassembler e a fotografia, cenas e alternativas de
Scarlet, comentários sobre roupas e reações familiares às conquistas de Hunter.
Foram preparados 60 alvos únicos e seis aliases baseados na identidade de todos
os segmentos originais. Os caminhos dependem de eventos e não formam uma única
sequência de jogo. Não representam a tradução completa de uma região.

Nomes próprios, risadas, Hunter e Soldier permanecem preservados. Os títulos
Veteran Hunter, Elite Hunter, Ace Hunter e Invincible Hunter ficam em inglês.
As menções a dez, vinte e trinta procurados mantêm as quantidades originais.
Não houve alteração de tabelas de itens, inimigos ou equipamentos.

As recusas iniciais identificaram excesso de bytes, uma maiúscula não disponível
no codec atual e posições incompatíveis de nomes dinâmicos em relação às
quebras. As frases foram reformuladas sem relaxar verificações, remover acentos
ou mudar controles. Todos os registros modificados usam slots existentes.

## Verificação e teste manual

91 testes passaram após os ajustes finais. A construção verifica hashes,
leitura de retorno, limites SSD, diretórios e diferenças integrais da ISO.
Não há realocação. Avisos conservadores de largura permanecem no relatório.
O teste novo também exige a presença dos títulos e nomes relevantes nos alvos.

Não houve execução desta versão no PCSX2. A tipografia mantém o perfil
provisoriamente autorizado, sem nova comprovação visual. No próximo teste,
observar as cenas de Scarlet, mensagens de classificação e opções: largura,
acentos, nomes dinâmicos e passagem de páginas. Não é necessário alcançar todos
esses eventos em uma sessão.

- `Preparar-Regiao-Inicial.cmd`: compila e valida a v008 sem nova ISO.
- `Testar-Regiao-Inicial.cmd` ou `Iniciar-Teste.cmd`: abre a ISO consolidada atual.
- ISO: `work/regiao-inicial-v008/MetalSaga-ptbr-regiao-inicial-v008.iso`.
- Plano, revisão bilíngue e relatório: `work/regiao-inicial-v008/`.
- Evidências publicáveis: `reports/regiao-inicial-v008-validation.json`.

```powershell
python tools/build_translation_pilot.py --output work/reconstrucao-v008 --build-iso
python -m unittest discover -s tests
```

A retenção removeu a ISO do piloto inicial v001 para manter dez imagens de
trabalho. Receita, traduções e relatórios foram preservados; esse conteúdo está
incluído nas versões consolidadas. O atalho histórico `--iso pilot` exige
reconstrução. A v007 permanece disponível; o iniciador padrão abre a v008.
A ISO original, BIOS, saves e configurações não foram modificados.
