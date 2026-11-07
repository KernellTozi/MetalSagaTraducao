# Metal Saga — Tradução PT-BR

Tradução independente de **Metal Saga para PlayStation 2**, por **Kernell Tozi**.
O projeto adapta textos, menus e recursos gráficos para português brasileiro,
preservando nomes próprios e a identidade do jogo.

**Versão atual: v071 — candidata para revisão em partida.**
Testada em amostras no PCSX2, com verificações automatizadas de integridade.
A tradução ainda pode apresentar lacunas e ajustes de contexto; não afirmamos
cobertura de 100% nem aprovação visual de todas as telas.

## Aplicar a tradução

O projeto distribui um **patch de diferenças**, sem ISO, BIOS ou emulador.
Você precisa fornecer sua própria ISO original compatível.

1. Obtenha o pacote `MetalSaga-PTBR-v071-Patch.zip`, quando disponibilizado
   pelo autor. Não há download do ZIP versionado neste repositório.
2. Extraia todos os arquivos e abra **Aplicar-Patch.cmd** no Windows 11 x64.
3. Selecione a ISO original americana e aguarde a criação de uma nova ISO.
4. Abra a imagem traduzida no PCSX2.

O aplicador funciona offline, preserva a original e confere a imagem gerada.
Não aplique sobre outra tradução, uma ISO modificada ou um CHD.

| Origem exigida | Valor |
|---|---|
| Edição | USA / NTSC-U |
| Serial | SLUS-21293 |
| Tamanho | 1.704.427.520 bytes |
| SHA-256 | `ef8405bf9e34bffd7846bcf3386a73464864823e20cd46ee9dacec514028b403` |

[Instruções completas, hashes e conteúdo do pacote v071](docs/publicacao-patch-v071.md).

## O que foi trabalhado

- Diálogos e referências de falantes identificados no catálogo técnico.
- Menus, Satcom, diário, ajuda, lojas e mensagens de sistema.
- Itens, equipamentos, habilidades e mensagens de uso de itens.
- Fontes com caracteres PT-BR e recursos gráficos de interface/minigames.

A v071 acrescenta mensagens de cura, ração, reparo e outros efeitos de itens,
além dos avisos de Montanha de Sucata/Monte Macaco e uma pergunta da ajuda.
Treze rótulos curtos de falantes continuam bloqueados por limitações técnicas.
Dummy, UP, DOWN e Damage Override foram preservados por decisão contextual.
Nomes próprios e termos como Hunter, Soldier, MAIN, SUB e SE são intencionais.

[Correções v071](docs/interface-v071.md) ·
[Pendências e validação](docs/pendencias-atuais.md) ·
[Glossário](docs/glossario.md)

## Encontrou um problema?

Abra um [relato no GitHub](https://github.com/KernellTozi/MetalSagaTraducao/issues/new/choose)
com a versão da tradução, local da cena, texto observado e uma captura de tela.
Informe se iniciou pelo memory card ou restaurou um save state.
Não envie ISO, BIOS, dados pessoais ou arquivos proprietários.

## Ferramentas e documentação

Este repositório reúne ferramentas próprias em Python, receitas de tradução,
testes e evidências técnicas. A extração e a reinserção funcionam localmente,
sem IA ou APIs. Construir a ISO exige os recursos originais locais, que não
acompanham o repositório. O projeto é independente de recompilação nativa.

| Pasta | Conteúdo |
|---|---|
| `tools/` | Extração, análise, reinserção, construção e verificação |
| `tests/` | Testes automatizados |
| `translations/` | Receitas e decisões de tradução |
| `docs/` | Manuais, descobertas e histórico |
| `reports/` | Evidências e relatórios reproduzíveis |
| `release/` | Aplicadores do patch |

[Índice da documentação](docs/README.md) ·
[Guia local e atalhos](docs/guia-projeto.md) ·
[Como contribuir](CONTRIBUTING.md) ·
[Autoria e distribuição](AVISOS.md)

ISO, BIOS, emulador, saves, anexos privados e recursos extraídos ficam fora
do Git. Não solicite ou publique esses arquivos nas issues.
