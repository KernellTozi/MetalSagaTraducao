# Ambiente isolado e roteiro de teste

Atualizado em 21/10/2026. O usuário faz navegação e verificações visuais pontuais;
o desenvolvimento técnico continua independentemente desses testes.

## Caminhos completos

| Finalidade | Caminho |
| --- | --- |
| Instalação original preservada | `C:\Projetos\MetalSagaTraducao\PCSX2` |
| Cópia portátil de teste | `C:\Projetos\MetalSagaTraducao\work\pcsx2-functional` |
| Executável de teste, versão 2.8.2 | `C:\Projetos\MetalSagaTraducao\work\pcsx2-functional\pcsx2-qt.exe` |
| Configuração isolada | `C:\Projetos\MetalSagaTraducao\work\pcsx2-functional\inis\PCSX2.ini` |
| Memory cards de teste | `C:\Projetos\MetalSagaTraducao\work\pcsx2-functional\memcards` |
| Save states de teste | `C:\Projetos\MetalSagaTraducao\work\pcsx2-functional\sstates` |
| Capturas nativas | `C:\Projetos\MetalSagaTraducao\work\pcsx2-functional\snaps` |
| Logs locais | `C:\Projetos\MetalSagaTraducao\work\pcsx2-functional\logs` |
| ISO original, nunca modificar | `C:\Projetos\MetalSagaTraducao\JOGO\Metal Saga.iso` |
| ISO do diário | `C:\Projetos\MetalSagaTraducao\work\MetalSaga-ptbr-experimento.iso` |
| ISO do diálogo inicial v001 | `C:\Projetos\MetalSagaTraducao\work\MetalSaga-ptbr-dialogo-inicial-v001.iso` |
| Iniciador | `C:\Projetos\MetalSagaTraducao\Iniciar-Teste.cmd` |

Não há cartões pessoais ou savestates copiados. Os diretórios de cartões e states
estão vazios nesta entrega e os dois slots de cartão estão desativados. A BIOS é
uma cópia local; os arquivos de referência permanecem fora do Git.

## Iniciar sem localizar o executável

Fechar a cópia de teste antes de iniciar outra sessão. O iniciador recusa duplicar
processos usando a mesma configuração isolada. Um duplo clique em
`Iniciar-Teste.cmd` abre a ISO do diálogo v001. A partir do PowerShell na raiz:

```powershell
.\Iniciar-Teste.cmd dialogue
.\Iniciar-Teste.cmd diary
```

Executar somente uma das opções por vez. O iniciador passa `-portable -fastboot` ao
executável da cópia, com diretório de trabalho dentro dela. Não passa `-state` ou
`-statefile`. Fast boot pula a animação da BIOS, mas inicia RAM nova; não restaura state.

Para outra ISO experimental, ela deve estar dentro de `work/`:

```powershell
python tools/start_test.py --iso 'C:\Projetos\MetalSagaTraducao\work\nome-da-versao.iso'
```

O script valida os diretórios de BIOS, cartões, states, capturas, logs e cache antes
de executar. Também pode ser inspecionado sem abrir o programa:

```powershell
python tools/start_test.py --iso dialogue --dry-run
```

Alternativa manual: abrir o executável de teste indicado na tabela; usar
**Sistema → Iniciar Arquivo** e selecionar a ISO experimental. Ao mudar de build,
desligar o jogo e iniciar de novo. Apenas trocar o disco com o jogo rodando ou
carregar um state antigo pode manter textos da outra ISO na RAM.

## Controles manuais preparados

As macros persistentes usadas no diagnóstico foram removidas da cópia existente.
Uma cópia da configuração anterior ficou em `inis/PCSX2.before-manual.ini`.

| PS2 / função | Tecla |
| --- | --- |
| Direcional | setas |
| X / confirmar | X |
| Círculo / voltar | C |
| Triângulo / menu | T |
| Quadrado | S |
| Start | Enter |
| Select | Backspace |
| Analógico esquerdo | W / Z / A / D |
| L1 / R1 | Q / E |
| L2 / R2 | 1 / 3 |
| Pausar emulação | Espaço |
| Captura nativa | F8 |
| Salvar / carregar state de teste | F1 / F3 |
| Próximo slot de state | F2 |

F1/F3 são opcionais para repetir uma cena na **mesma build**. Não carregar states
de outra build para julgar a tradução. Um controle físico pode ser configurado em
Configurações → Controles dentro desta cópia, sem usar a instalação original.
Se desejar saves normais, criar e habilitar cartões novos somente na pasta de teste.

## Teste prioritário: pergunta sobre ser Hunter

ISO: `MetalSaga-ptbr-dialogo-inicial-v001.iso`. Esta versão parte da ISO original
e modifica apenas o diálogo; **não inclui a alteração do diário**.

1. Iniciar com o iniciador padrão e escolher continuar sem cartão se perguntado.
2. Começar **New Game**, sem restaurar state de outra versão.
3. Acessar a conversa inicial que o usuário identificou como
   “You want to become a Hunter?”. O texto real no recurso é dividido em duas linhas
   e contém “hunter” em minúscula.
4. Esperado nesta build:

   ```text
   Quer ser um
   Hunter?
   ```

Observar se as duas linhas aparecem completas, sem caracteres errados, corte,
sobreposição ou espaços indevidos. Avançar a fala e conferir se o diálogo seguinte
continua normalmente. Enviar uma captura, o nome da ISO e informar se a navegação
prosseguiu ou houve erro. Não é necessário verificar cada registro do catálogo.

A tradução final desejada é “Você quer se tornar um caçador?”. Ela ainda não foi
codificada: acentos, métricas GFI e expansão deste registro não estão comprovados.

## Experimento preservado: diário

ISO: `MetalSaga-ptbr-experimento.iso`. Altera **To Do List → Tarefas**, registro 0
(primeiro registro, não índice 1) de DIARY.DAT. O título começa em `0x11C` dentro
do arquivo. O restante do diário foi preservado.

O corpo desse registro contém a lista de objetivos iniciais em Junkyard. Isso
indica ligação com o começo da campanha, mas **o gatilho exato de desbloqueio não foi
confirmado**. No teste curto o jogo chegou a Junkyard e ao menu com Satcom; o diário
não foi aberto. Não se afirma que o registro já está disponível assim que New Game começa.

Quando conveniente, iniciar a ISO do diário e procurar o diário nas funções de
Satcom. Conferir se o título aparece como “Tarefas” e se o corpo abre normalmente.
Se não houver entrada disponível, informar a tela e o ponto da campanha, sem
necessidade de jogar longamente apenas por esse teste. O experimento fica preservado.

## Evidência já obtida e preservação

Na sessão de diagnóstico, a ISO **do diário** inicializou em PCSX2 2.8.2, passou
pela tela de título, opções e nome de personagem, e chegou a Junkyard. Houve
captura nativa local em `snaps/Metal Saga_SLUS-21293_20261021113827.png`.
Esse quadro registra a área Memory Center, não a tradução do diário. O novo
diálogo ainda não foi observado no emulador. Ambos os resultados visuais seguem pendentes.
O iniciador foi executado com a ISO do diálogo: o log confirmou a imagem correta,
o executável isolado e o CRC ELF `269F5DF5`; a captura da janela mostrou o aviso
inicial de ausência de cartão. A sessão ficou aberta nesse aviso para o teste manual.
Isso confirma boot curto da nova ISO, sem comprovar a fala traduzida.

O manifesto `work/pcsx2-protected-before.json` detectou mudança no hash de
`PCSX2/inis/PCSX2.ini` durante a sessão anterior. As observações capturadas mostram
geometria de janela diferente, mas não há backup integral inicial para atribuir
toda a divergência ou restaurá-la com segurança. A origem da alteração não foi
comprovada. Não houve restauração cega nem escrita nesse arquivo pelas ferramentas
criadas nesta fase. Os hashes de BIOS, cartões e savestates originais coincidem
com o manifesto; a preparação dos controles manuais confirmou que não alterou
nenhum dos recursos originais monitorados.

Logs completos, capturas, estados, configurações, BIOS e ISOs permanecem locais,
ignorados pelo Git. A documentação e os scripts são os artefatos versionáveis.
