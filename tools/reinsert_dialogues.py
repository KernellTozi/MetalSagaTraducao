"""Local Windows-friendly batch export, simulation, ISO update and recovery."""
from datetime import datetime
from pathlib import Path
import argparse
import json
import mmap

from reinsertion import SOURCE, ROOT, export, compile_batch, local, merge
from dialogue import sha
from dialogue_advanced import SsdIndex
import development_iso as dev


def report_path(command):
    return ROOT/'work/relatorios-reinsercao'/f'{datetime.now():%Y%m%d-%H%M%S-%f}-{command}.json'


def menu():
    print('Metal Saga - reinsercao local v004')
    print('1 Exportar catalogo editavel\n2 Simular lotes\n3 Aplicar lotes na ISO de desenvolvimento\n4 Criar ISO base (uma vez)\n5 Restaurar ISO de desenvolvimento\n6 Recuperar transacao interrompida\n0 Sair')
    command={'1':'export','2':'dry-run','3':'apply','4':'init','5':'restore','6':'recover'}.get(input('Opcao: ').strip())
    if command is None:return None
    if command=='export':return [command,'--output',input('Novo arquivo JSON [work/traducoes/lote-v004.json]: ').strip() or 'work/traducoes/lote-v004.json']
    if command in ('dry-run','apply'):
        paths=input('Arquivos JSON separados por ponto e virgula [work/traducoes/lote-v004.json]: ').strip() or 'work/traducoes/lote-v004.json'
        return [command,'--plan',*[p.strip().strip('"') for p in paths.split(';')]]
    return [command]


def main(argv=None):
    import sys
    argv=list(sys.argv[1:] if argv is None else argv)
    if not argv:
        argv=menu()
        if argv is None:return
    parser=argparse.ArgumentParser(description='Reinserção offline em lotes Metal Saga')
    sub=parser.add_subparsers(dest='command',required=True)
    p=sub.add_parser('export');p.add_argument('--output',type=Path,required=True)
    for name in ('dry-run','apply'):
        p=sub.add_parser(name);p.add_argument('--plan',type=Path,nargs='+',required=True);p.add_argument('--report',type=Path)
    for name in ('init','restore','recover'):
        p=sub.add_parser(name);p.add_argument('--report',type=Path)
    a=parser.parse_args(argv)
    try:
        if a.command=='export':
            path=local(a.output,True)
            with SOURCE.open('rb') as stream,mmap.mmap(stream.fileno(),0,access=mmap.ACCESS_READ) as data:
                document=export(data,SsdIndex(data))
            dev.atomic_json(path,document)
            available=sum(not e['blocked_reasons'] for e in document['entries'])
            print(f'{len(document["entries"])} registros exportados; {available} elegiveis pela politica binaria. Arquivo: {path}')
            return
        path=local(a.report or report_path(a.command),True)
        if a.command=='init':result=dev.initialize()
        elif a.command=='recover':result=dev.recover()
        elif a.command=='restore':result=dev.transact([],'restore-original')
        else:
            inputs=[(local(p),local(p).read_bytes()) for p in a.plan]
            documents=[json.loads(raw.decode('utf-8-sig')) for _,raw in inputs]
            document=merge(documents)
            with SOURCE.open('rb') as stream,mmap.mmap(stream.fileno(),0,access=mmap.ACCESS_READ) as data:
                patches,result=compile_batch(data,document)
            result['command']=a.command
            result['plan_sha256']=sha(json.dumps(document,sort_keys=True,ensure_ascii=False).encode('utf-8'))
            result['plans']=[{'path':p.relative_to(ROOT).as_posix(),'sha256':sha(raw)} for p,raw in inputs]
            state_file=dev.SESSION/'estado.json'
            if state_file.exists():
                old=json.loads(state_file.read_text(encoding='utf-8'));new_ids={p['id'] for p in patches}
                result['previous_entries_restored_to_original']=sorted({p['id'] for p in old['patches'] if 'id' in p}-new_ids)
            if result['valid']:
                if result['requires_ptbr_fonts']:
                    patches+=dev.font_patches()
                    result['fonts_version']='preliminary-validated-acentos-v001'
                # Extent/baseline validation is also performed during dry-run.
                dev.absolute_patches(patches)
                if a.command=='apply':
                    recipe={**document,'entries':[e for e in document['entries'] if any(s['translation']!=s['source'] for s in e['segments'])]}
                    recipe_sha=sha(json.dumps(recipe,sort_keys=True,ensure_ascii=False).encode('utf-8'))
                    archive=dev.SESSION/'lotes'/f'{recipe_sha}.json'
                    if archive.exists():
                        prior=json.loads(archive.read_text(encoding='utf-8'))
                        if prior!=recipe:raise ValueError('Snapshot arquivado foi alterado')
                    else:dev.atomic_json(archive,recipe)
                    result['recipe']={'path':archive.relative_to(ROOT).as_posix(),'sha256':recipe_sha}
                    result['apply_state']='validated_prepared';dev.atomic_json(path,result)
                    result['iso_update']=dev.transact(patches,recipe_sha)
                    result['iso']=dev.IMAGE.relative_to(ROOT).as_posix()
                    result['apply_state']='committed'
            dev.atomic_json(path,result)
            print(f'Aceitos: {result["accepted"]}; recusados: {result["refused"]}; sem mudanca: {result["unchanged"]}. Relatorio: {path}')
            if not result['valid']:raise SystemExit(2)
            if a.command=='dry-run':print('Simulacao concluida: nenhum binario foi gravado.')
            else:print(f'ISO validada sem regravar: {dev.IMAGE}' if result['iso_update'].get('idempotent_no_write') else f'ISO atualizada: {dev.IMAGE}')
            return
        dev.atomic_json(path,result);print(f'Concluido. Relatorio: {path}\nISO: {dev.IMAGE}')
    except (ValueError,OSError,KeyError,TypeError,ImportError) as error:
        parser.exit(2,f'Erro: {error}\nSe existir transacao.json, execute recover antes de usar a ISO.\n')


if __name__=='__main__':main()
