# Interface v052 — exceção autorizada e avanço dos nomes dinâmicos

Base: interface v051/MAP v044, fonte e layout v005. Receita nova:
`translations/interface-v052.json`. A receita v051 e as escolhas humanas
originais permanecem intactas.

## Alteração aplicada

Somente o item **460** muda de **Imagem de barro** para **Idolo de barro**.
A escolha humana era Ídolo de barro; o usuário autorizou omitir esse acento
se a solução na fonte não fosse simples. A exceção é exclusiva deste nome.

O mapeamento atual não contém Í. Acrescentá-lo envolve bitmap e os três
caminhos de largura/desenho, com intervalos de 18 códigos e tabelas vinculadas.
Não é uma alteração isolada de desenho. Optou-se pelo fallback autorizado de
**14 bytes ASCII**, dentro do teto existente de 16, sem fonte ou ELF novos.

A política `single-item-authorized-ascii-accent-fallback-v001` vincula o pai,
manifesto, origem e registro. Aceita somente o texto exato no ID 460. Preserva
o prefixo editado anterior de 16 bytes, com novo nome e dois zeros finais.
Não há outro alias nem ação de batalha com o mesmo nome original neste
levantamento; a ferramenta recusa uma mudança nessa condição.

Os compiladores históricos continuam recusando o glifo Í e nomes fora de seus
limites. A extensão usa uma configuração explícita e vinculada, não libera
outros nomes sem acento, e mantém todas as demais escolhas da receita-pai.
A quantidade de nomes de itens permanece **541**: é uma revisão, não item novo.
As propostas ainda bloqueadas passam de **16 para 15** — seis por capacidade
dos consumidores e nove com alertas de largura. A escolha acentuada histórica
continua documentada; não foi apagada do manifesto da revisão humana.

## Mensagens que combinam nome e item

`tools/item_name_stream.py` ganhou a opção explícita de executar `%N0` literal
no emissor completo. O handler N, seu lookup de ponteiro, o leitor de argumento,
a emissão do nome e o retorno ao texto original são executados. Tabela de
ponteiros, nome fornecido, classificação e registro de glifos são modelados.
Isso não identifica o personagem canônico nem executa GPU/PCSX2.

**N0 é literal zero, não N$0.** O novo caminho recusa variantes não habilitadas.
O nome e os valores das variáveis I são entradas independentes. Testes conferem
ordens N0→I e I→N0, caracteres acentuados, nome vazio e limite de células.

Nas dez páginas reais que a sonda anterior separava, foram executados **60
casos condicionais**, seis itens por página, em **360 cenários de instruções**:
nome vazio, dois nomes de amostra, limite exato com ASCII, limite exato com
acentos e uma tentativa acima do limite, que deve ser recusada pelo harness.
Os nomes de amostra não são atribuídos a personagens dessas cenas.

O menor orçamento restante observado foi de **41 células para o nome**, entre
essas páginas e contextos. Esse número é um orçamento condicional, **não o
tamanho máximo comprovado da fonte real do nome**. Não basta para liberar os
seis itens maiores. O resultado anterior das outras 25 páginas continua igual.
As dez páginas já não dependem de descobrir outro controle para este ensaio;
falta fechar os limites das fontes dinâmicas e a chamada virtual 0x473C8.

Reproduzir sem internet/IA/APIs:

```powershell
python tools/item_name_stream.py --audit-mixed-names --output work/fluxo-nomes-v004.json
```

O relatório mantém os dez bloqueios do modo estrito v003 e acrescenta
`map_audit.mixed_names` com seus resultados no modo N0 habilitado. Não confundir
a preservação dessa classificação histórica com falha do novo diagnóstico.

## ISO e verificação

Abrir **Iniciar-Teste.cmd** para usar:
`work/interface-v052/MetalSaga-ptbr-interface-v052.iso`.
`Preparar-Interface.cmd` valida a receita v052, sem gerar outra imagem.
`Auditar-Traducao.cmd` usa o build v052 e exclui do diagnóstico de pendências
somente o fallback efetivamente compilado, mantendo as outras 15 propostas.
Sem argumento de receita atual, o diagnóstico de capacidade ainda reproduz
a investigação histórica de 16 propostas contra v050.

A comparação integral v051→v052 confirmou **13 bytes diferentes em um único
prefixo de 16 bytes**, do item 460 em S_PACK.SDA. Todos os outros bytes e o
diretório ISO permaneceram iguais. Fonte/layout v005 e todos os diálogos
permanecem idênticos. O comparador exige o pai exato e não normaliza spans
arbitrários para aceitar esta mudança.

SHA-256 v052: `26a23155f5fe8e7aa994871c7100e35929f90b59ecd96e1d9a542b8d7079b449`.
Tamanho: 1.704.427.520 bytes. Preflight de tamanho/hash/transações e preparação
do comando do iniciador conferidos, **sem iniciar o emulador**.
Mantidas cinco ISOs de trabalho e a alpha separada. Sem OneDrive ou desligamento.

Teste visual futuro: ao encontrar esse objeto na lista de itens/decoração,
conferir Idolo de barro completo, sem texto residual. O usuário segue a partida
normal; não é necessário alcançar o objeto agora para continuar o trabalho.

## Próximo passo

Investigar as fontes concretas dos nomes e os retornos virtuais que chegam a
0x473C8. Os testes agora permitem exercitar N0 e I juntos, inclusive no limite;
não repetir a busca bruta nem abreviar os seis nomes para aumentar contagens.
Com as provas restantes, criar política por ID para esses seis nomes e suas
cinco ações. Os nove casos de largura permanecem separados.

## Testes concluídos

**103 testes unitários distintos passaram**, zero falhas, erros ou ignorados
na execução final. Incluem oito testes do fallback e cinco novos do modo N0,
além das regressões de itens, controles, contexto, retenção e preflight de ISO.
Os cenários internos e as reexecuções durante o desenvolvimento não são
somados à contagem de unittest. A comparação integral da ISO e o preflight
também foram executados, separadamente dos testes unitários.

Relatórios próprios: reports/interface-v052.json, reports/interface-v052-delta.json
e reports/fluxo-nomes-v004.json. Saídas detalhadas e logs somente em work/.
