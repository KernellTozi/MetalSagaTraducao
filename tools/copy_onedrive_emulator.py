"""Explicit private delivery of the existing portable PCSX2, with verified copies."""
import configparser
from datetime import datetime
import io
import json
import os
from pathlib import Path
import shutil
import tempfile
from copy_onedrive import ROOT,DESTINATION,checksum


def deliver():
    source=(ROOT/'PCSX2').resolve()
    destination=DESTINATION.resolve()
    final=destination/'PCSX2'
    if final.exists():raise ValueError('PCSX2 de destino já existe; preservar essa cópia antes de nova entrega')
    paths=[]
    for base,dirs,files in os.walk(source,followlinks=False):
        parent=Path(base)
        for name in list(dirs):
            path=parent/name
            if path.is_symlink() or path.is_junction():raise ValueError('Links não permitidos no pacote')
            if parent==source and name.lower() in ('cache','logs'):dirs.remove(name)
        for name in files:
            path=parent/name
            if path.is_symlink() or not path.resolve().is_relative_to(source):raise ValueError('Arquivo externo bloqueado')
            paths.append(path)
    paths.sort()
    hashes={p.relative_to(source).as_posix():checksum(p) for p in paths}
    cfg=configparser.ConfigParser(interpolation=None,strict=False);cfg.optionxform=str
    cfg.read(source/'inis/PCSX2.ini',encoding='utf-8')
    bios=cfg.get('Filenames','BIOS')
    if Path(bios).name!=bios or not (source/'BIOS'/bios).is_file():raise ValueError('BIOS não está contida no pacote')
    if not (source/'portable.txt').is_file():raise ValueError('Instalação original não é portátil')
    # Only the delivered INI changes. Do not traverse the original game list.
    cfg['GameList']={}
    for key,value in {'Bios':'BIOS','Snapshots':'snaps','Savestates':'sstates','MemoryCards':'memcards',
        'Logs':'logs','Cheats':'cheats','Patches':'patches','UserResources':'resources','Cache':'cache',
        'Textures':'textures','InputProfiles':'inputprofiles','Videos':'videos',
        'DebuggerLayouts':'debuggerlayouts','DebuggerSettings':'debuggersettings'}.items():
        cfg.set('Folders',key,value)
    output=io.StringIO();cfg.write(output);ini=output.getvalue().encode('utf-8')
    destination.mkdir(parents=True,exist_ok=True)
    partial=Path(tempfile.mkdtemp(prefix='.PCSX2-copy-',dir=destination))
    verified=[]
    for path in paths:
        rel=path.relative_to(source);target=partial/rel;target.parent.mkdir(parents=True,exist_ok=True)
        if rel.as_posix()=='inis/PCSX2.ini':target.write_bytes(ini)
        else:shutil.copy2(path,target)
        expected=__import__('hashlib').sha256(ini).hexdigest() if rel.as_posix()=='inis/PCSX2.ini' else hashes[rel.as_posix()]
        if checksum(target)!=expected:raise ValueError('Cópia do emulador não confere: '+str(rel))
        verified.append({'path':rel.as_posix(),'sha256':expected,'size':target.stat().st_size})
    for path in paths:
        if checksum(path)!=hashes[path.relative_to(source).as_posix()]:raise ValueError('Origem mudou durante a cópia')
    for name in ('cache','logs'):(partial/name).mkdir(exist_ok=True)
    if not (partial/'pcsx2-qt.exe').is_file():raise ValueError('Executável ausente')
    for key in ('Slot1','Slot2'):
        if cfg.getboolean('MemoryCards',key+'_Enable',fallback=False):
            name=cfg.get('MemoryCards',key+'_Filename')
            if Path(name).name!=name or not (partial/'memcards'/name).is_file():raise ValueError('Cartão selecionado ausente')
    os.rename(partial,final)
    for item in verified:
        if checksum(final/item['path'])!=item['sha256']:raise ValueError('Verificação final do emulador falhou')
    launcher=destination/'Iniciar-MetalSaga.cmd'
    with launcher.open('x',encoding='ascii',newline='') as f:
        f.write('@echo off\r\ncd /d "%~dp0PCSX2"\r\nstart "Metal Saga PT-BR" "%~dp0PCSX2\\pcsx2-qt.exe" -portable -fastboot "%~dp0MetalSaga-PTBR.iso"\r\n')
    with (destination/'COMO-JOGAR.txt').open('x',encoding='utf-8') as f:
        f.write('METAL SAGA PT-BR — pacote pessoal\n\n'
            '1. Aguarde o OneDrive concluir a sincronização no computador de origem.\n'
            '2. No outro computador, baixe integralmente a pasta METAL SAGA (manter sempre neste dispositivo).\n'
            '3. Abra Iniciar-MetalSaga.cmd. O PCSX2 e a ISO devem permanecer nesta estrutura de pastas.\n\n'
            'A cópia inclui BIOS, cartões e configurações do PCSX2 do projeto. Os originais foram preservados.\n'
            'Ajuste os controles e o renderizador no PCSX2 se o hardware do outro computador exigir.\n'
            'O jogo começa pela inicialização normal: carregue seu progresso pelo menu do jogo.\n'
            'O conteúdo é para seu uso pessoal; não publique a ISO, BIOS ou cartões no GitHub.\n')
    report={'source':'PCSX2','destination':str(final),'files':verified,'file_count':len(verified),
        'bytes':sum(r['size'] for r in verified),'source_preserved':True,'local_copy_verified':True,
        'included':'emulator, BIOS, memory cards, settings and existing runtime resources',
        'copy_only_changes':['INI folder paths portable and original external game list cleared'],
        'excluded':['cache','logs'],'launcher':str(launcher),'emulator_executed':False,'cloud_sync_confirmed':False}
    report_path=ROOT/'reports'/f'onedrive-pcsx2-{datetime.now():%Y%m%d-%H%M%S}.json'
    with report_path.open('x',encoding='utf-8') as f:json.dump(report,f,ensure_ascii=False,indent=2);f.write('\n')
    print(f'PCSX2 copiado e verificado: {len(verified)} arquivos; {report_path.name}')


if __name__=='__main__':deliver()
