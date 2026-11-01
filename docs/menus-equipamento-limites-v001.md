# Equipamento e categorias de caça — pesquisa sem aplicação

Data: 01/11/2026. Base jogável preservada: interface v060, MAP v044/layout
v005. O usuário está testando essa versão e pediu pesquisa e registro,
**sem modificar o jogo ainda**. Nenhuma receita, ferramenta de construção,
fonte, iniciador ou ISO é alterada nesta rodada.

## Capturas recebidas

- Equipamento: Status/Equip, MEMBER LIST, VEHICLE LIST e Compare parts ainda
  em inglês. Sugestões para revisão futura: Status/Equipamento, Personagens,
  Veículos e Comparar peças. São propostas, não textos aplicados.
- Satcom/Caça: Bio, Cyber, Máq., Veíc., Descon. e Alvos. O usuário considera
  as abreviações inadequadas e solicita investigar nomes completos.
  Máquinas, Veículos e Desconhecidos são propostas iniciais. Bio e Cyber
  também precisam de revisão contextual; não decidir por uma expansão
  automática nem confundir Alvos com uma categoria desconhecida.

Evidências fornecidas: codex-clipboard-1c315ac1-70c9-4d11-b283-d60700a2a03f.png
e codex-clipboard-a4c018cd-9514-4d8d-b951-142529c83fab.png. A versão exata usada
nessas duas capturas não foi confirmada; o usuário ainda pretende testar v060.

## Evidência local, somente leitura

A consulta ao ELF original e à receita v060 encontrou:

| Texto | Offset de arquivo ELF | Situação |
|---|---|---|
| Compare parts | 0x32B250 | Literal encontrado, fora do catálogo conservador de strings isoladas; referência candidata LUI/ADDIU |
| Status/Equip | 0x32B110 | String de 12 bytes, duas referências candidatas LUI/ADDIU |
| Status/Equip | 0x32CE80 | Outra ocorrência, fora daquele catálogo, com referência em tabela |
| MEMBER LIST / VEHICLE LIST | — | Não encontrados como literais ASCII exatos no ELF; origem ainda não identificada |

A ausência dos dois cabeçalhos no ELF não prova que sejam imagens. Podem
estar em outro recurso, outra codificação ou composição de texto. Investigar
os atlas conhecidos somente depois de identificar os seletores da tela.

A receita contém Status/Equip. em outro recurso (campo 46). Isso não traduz
automaticamente todas as ocorrências do mesmo título. Compare parts requer
analisar os bytes anteriores, a chamada consumidora e o terminador; não
liberar o catálogo inteiro só porque um literal foi localizado.

As categorias abreviadas são strings fixas do ELF. O limite abaixo é o
texto original antes do NUL, imposto pelo compilador atual; não é uma prova
de limite universal do motor ou de quantidade máxima de caracteres.

| Atual | Proposta | Capacidade atual, sem NUL | Bytes da proposta, sem NUL |
|---|---|---:|---:|
| Máq. | Máquinas | 7 | 9 |
| Veíc. | Veículos | 7 | 9 |
| Descon. | Desconhecidos | 7 | 13 |

Contagem executada com tools/gfi.py: o acento usa dois bytes no mapeamento
do projeto. Os valores não são UTF-8 nem Windows-1252. A capacidade física
de um novo destino também precisaria incluir um byte de NUL.

Há dez ocorrências relacionadas na receita, que exigem revisão de aliases:

- 0x349248, 0x349260 e 0x349268: Descon., Máq. e Veíc.; as referências
  detectadas são ponteiros em dados. O primeiro tem três referências.
- 0x349828, 0x349830 e 0x349838: Máq., Veíc. e Descon.; ponteiros em dados.
- 0x3498D0: outra Veíc.; ponteiro em dados.
- 0x349E80, 0x349E88 e 0x349E90: Máq., Veíc. e Descon.; candidatos
  de endereço construído por LUI/ADDIU.

O catálogo não detectou referências interiores nesses dez literais. Sua
varredura conservadora não prova ausência de chamadas indiretas, aliases
calculados ou consumidores desconhecidos. Não substituir os dez rótulos
indiscriminadamente antes de confirmar quais telas os utilizam.

## Pesquisa pública: é possível ampliar?

Sim, há técnicas usadas em traduções de PS2. O projeto
[Busin0Translation](https://github.com/Fabulu/Busin0Translation/blob/master/README.md)
documenta recálculo de referências de texto em scripts, ajustes de métricas,
reconstrução/realocação de arquivo na ISO e ampliação de uma caixa de nomes.
O mesmo histórico registra uma tentativa de extensão do executável rejeitada
pelo carregador. A caixa ampliada ainda era indicada como pendente de inspeção
visual nessa documentação. Isso distingue implementação de confirmação em tela.

Essa referência sustenta a possibilidade técnica, não compatibilidade com
Metal Saga. O formato de scripts e o armazenamento de Busin 0 diferem dos
nossos. O README foi consultado; tentativas de abrir os scripts específicos
patch_pill_widen.py e patch_section1_offsets.py não retornaram conteúdo pelo
navegador. Não houve auditoria desses scripts, incorporação de código,
instalação de dependências ou avaliação de licença para reutilização.

## Estratégia recomendada para a próxima implementação autorizada

1. Separar tamanho de armazenamento, cópia em RAM e largura visível. Cada um
   pode impor um limite distinto. Espaço aparente na captura é indício de
   margem visual, não autorização para sobrescrever os próximos bytes.
2. Começar pelas três categorias da tabela: confirmar tabelas consumidoras,
   seletores e ciclo de vida, aproveitando as referências já encontradas.
   As provas anteriores de buffers de nomes de itens não se transferem a elas.
3. Buscar primeiro espaço carregado e comprovadamente disponível no mesmo
   recurso. Se houver, criar um pequeno banco de textos maiores e redirecionar
   apenas referências comprovadas. Atualizar endereços MIPS exige distinguir
   LUI/ADDIU com sinal de LUI/ORI; não trocar palavras isoladas por coincidência.
4. Se não existir espaço seguro, estudar reserva explícita e carregamento de
   outro banco. O fim do ELF/heap permanece um bloqueio conhecido na pesquisa
   dos 13 falantes; não presumir que padding ou BSS estejam livres. Ampliar
   segmento/arquivo exigiria prova do carregador, alocador e reconstrução ISO.
5. Verificar terminador, cópias temporárias, limites de listas e todas as
   referências afetadas. Medir Máquinas/Veículos/Desconhecidos com os avanços
   existentes do layout v005 e reservar margem antes da coluna numérica.
   Não reduzir a fonte como primeira solução para uma limitação de bytes.
6. Tratar os cabeçalhos e Compare parts pelo recurso efetivamente identificado.
   Se forem imagens, o limite será a célula/UV e o desenho, não a string ELF.
7. Somente após nova ordem, implementar política opt-in com hashes, aliases,
   testes de limites e comparação integral. Entregar uma versão consolidada
   para teste dessas telas; preservar a v060 enquanto estiver em avaliação.

Leituras locais: docs/interface-v001.md, docs/capacidade-nomes-v001.md,
docs/buffers-nomes-v002.md e docs/falantes-lookup-v001.md. As duas primeiras
investigações de nomes são históricas; não reabrir revisões de itens já
aplicadas como se continuassem pendentes.

## Resultado desta rodada

Pesquisa e consultas somente leitura concluídas. Nenhum aumento de limite
implementado ou comprovado no jogo. Nenhuma nova ISO, execução de PCSX2,
cópia para OneDrive ou desligamento. Iniciar-Teste.cmd e o atalho de pasta
continuam apontando para v060. O aviso do tanque imobilizado segue separado,
também aguardando autorização para aplicação.
