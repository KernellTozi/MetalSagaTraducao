"""Exclusive development ISO transactions with persistent undo and recovery."""
from contextlib import contextmanager
from pathlib import Path
import hashlib
import json
import os
import shutil
import sys
import uuid

from dialogue import ROOT, sha
from disc import entries, SECTOR, digest
from build_dialogue_iso import compare_streams, ORIGINAL_ISO_SHA256
from reinsertion import local

ORIGINAL=ROOT/'JOGO/Metal Saga.iso'
SESSION=ROOT/'work/desenvolvimento'
IMAGE=SESSION/'MetalSaga-ptbr-desenvolvimento.iso'


def atomic_json(path,data):
    path=local(path);path.parent.mkdir(parents=True,exist_ok=True)
    temporary=path.with_name(path.name+'.'+uuid.uuid4().hex+'.tmp')
    with temporary.open('x',encoding='utf-8',newline='\n') as stream:
        json.dump(data,stream,ensure_ascii=False,indent=2);stream.write('\n');stream.flush();os.fsync(stream.fileno())
    os.replace(temporary,path)


@contextmanager
def exclusive(path):
    """Windows share=0 rejects existing readers and blocks new PCSX2 readers."""
    path=local(path)
    if ORIGINAL.exists() and path.exists() and os.path.samefile(path,ORIGINAL):
        raise ValueError('A ISO de trabalho não pode ser hardlink do original')
    if os.name=='nt':
        import ctypes,msvcrt
        from ctypes import wintypes
        create=ctypes.windll.kernel32.CreateFileW
        create.argtypes=[wintypes.LPCWSTR,wintypes.DWORD,wintypes.DWORD,ctypes.c_void_p,wintypes.DWORD,wintypes.DWORD,wintypes.HANDLE]
        create.restype=wintypes.HANDLE
        handle=create(str(path),0xc0000000,0,None,3,0x80,None)
        if handle==ctypes.c_void_p(-1).value:
            raise OSError('ISO ocupada ou inacessível. Feche o jogo/PCSX2 antes de atualizar.')
        try:fd=msvcrt.open_osfhandle(handle,os.O_RDWR|os.O_BINARY)
        except BaseException:
            ctypes.windll.kernel32.CloseHandle(handle);raise
        with os.fdopen(fd,'r+b') as stream:yield stream
    else:
        import fcntl
        with path.open('r+b') as stream:
            fcntl.flock(stream,fcntl.LOCK_EX|fcntl.LOCK_NB)
            try:yield stream
            finally:fcntl.flock(stream,fcntl.LOCK_UN)


def serialize(patches):
    return [{k:(v.hex() if k in ('before','after') else v) for k,v in p.items()} for p in patches]


def deserialize(patches):
    return [{**p,'before':bytes.fromhex(p['before']),'after':bytes.fromhex(p['after'])} for p in patches]


def validated_patches(source,patches):
    directory=entries(source);extents={e['path']:e for e in directory}
    previous=0
    for p in sorted(patches,key=lambda p:p['offset']):
        resource=extents.get(p['resource'])
        if p['resource'] not in ('DATA/MAP/MAP.MCT','DATA/SYS/SUC20I22.GFI','DATA/SYS/SUC24I26.GFI') or resource is None:
            raise ValueError('Recurso não aprovado para atualização')
        start=resource['lba']*SECTOR;end=start+resource['size'];at=p['offset']
        if len(p['before'])!=len(p['after']) or not start<=at<at+len(p['before'])<=end or at<previous:
            raise ValueError('Patch fora do extent, sobreposto ou de tamanho variável')
        source.seek(at)
        if source.read(len(p['before']))!=p['before']:raise ValueError('Bytes de origem do patch não coincidem com a ISO')
        previous=at+len(p['before'])
    return directory


def verify(source,target,patches):
    source.seek(0);target.seek(0)
    result=compare_streams(source,target,patches)
    if result['source_iso_sha256']!=ORIGINAL_ISO_SHA256:raise ValueError('Hash da ISO original divergente')
    return result


def font_patches():
    """Reuse exactly the preliminary-tested v001 fonts; no typeface redesign."""
    golden=json.loads((ROOT/'reports/acentos-v001-validation.json').read_text(encoding='utf-8'))
    experiment=ROOT/'work/MetalSaga-ptbr-acentos-v001.iso'
    result=[]
    cached=None
    if experiment.is_file():
        with experiment.open('rb') as stream:
            table={e['path']:e for e in entries(stream)};cached={}
            for item in golden['fonts']:
                e=table[item['path']];stream.seek(e['lba']*SECTOR);cached[item['path']]=stream.read(e['size'])
    for item in golden['fonts']:
        original=(ROOT/'JOGO/Metal Saga'/item['path']).read_bytes()
        if sha(original)!=item['source_sha256']:raise ValueError('Fonte original divergente')
        if cached is not None:modified=cached[item['path']]
        else:
            sys.path.insert(0,str(ROOT/'work/python-deps'))
            from gfi import font_patches as compose
            modified=bytearray(original)
            for p in compose(original):modified[p['offset']:p['offset']+len(p['after'])]=p['after']
            modified=bytes(modified)
        if len(original)!=len(modified) or sha(modified)!=item['patched_sha256']:
            raise ValueError('Fonte compilada difere da versão visualmente testada')
        # Each changed glyph is represented as a fixed slot, anchored in original.
        stride=item['glyph_stride']
        for glyph in item['glyph_edits']:
            at=glyph['offset'];result.append({'resource':item['path'],'offset':at,
                                              'before':original[at:at+stride],'after':modified[at:at+stride]})
    return result


def absolute_patches(relative):
    inventory={e['path']:e for e in json.loads((ROOT/'reports/inventory.json').read_text(encoding='utf-8'))}
    with ORIGINAL.open('rb') as stream:
        table={e['path']:e for e in entries(stream)}
        for name in set(p['resource'] for p in relative):
            e=table[name];stream.seek(e['lba']*SECTOR)
            if e['size']!=inventory[name]['size'] or digest(stream,e['size'])!=inventory[name]['sha256']:
                raise ValueError('Extent de origem não corresponde ao inventário')
        patches=sorted([{**p,'offset':table[p['resource']]['lba']*SECTOR+p['offset']} for p in relative],key=lambda p:p['offset'])
        validated_patches(stream,patches)
    return patches


def initialize():
    local(SESSION);local(IMAGE)
    SESSION.mkdir(parents=True,exist_ok=True)
    if IMAGE.exists():raise ValueError('Ambiente de desenvolvimento já existe')
    state_path=SESSION/'estado.json'
    if (SESSION/'transacao.json').exists():raise ValueError('Transação pendente; inicialização não pode sobrescrever recuperação')
    if state_path.exists():
        prior=json.loads(state_path.read_text(encoding='utf-8'))
        if prior.get('generation')!=0 or prior.get('patches') or (ROOT/prior['image']).resolve()!=IMAGE.resolve():
            raise ValueError('Estado pré-existente não é uma inicialização interrompida')
    partial=IMAGE.with_suffix('.iso.partial')
    if partial.exists():
        # Resume only after every existing prefix byte matches the immutable ISO.
        with exclusive(partial) as dst,ORIGINAL.open('rb') as src:
            remaining=partial.stat().st_size
            if remaining>ORIGINAL.stat().st_size:raise ValueError('Cópia parcial maior que o original')
            while remaining:
                size=min(remaining,1024*1024)
                if dst.read(size)!=src.read(size):raise ValueError('Prefixo parcial diverge; inicialização não retomada')
                remaining-=size
            shutil.copyfileobj(src,dst,1024*1024);dst.flush();os.fsync(dst.fileno())
    else:
        with ORIGINAL.open('rb') as src,partial.open('xb') as dst:
            shutil.copyfileobj(src,dst,1024*1024);dst.flush();os.fsync(dst.fileno())
    with ORIGINAL.open('rb') as src,partial.open('rb') as dst:validation=verify(src,dst,[])
    state={'schema':1,'image':IMAGE.relative_to(ROOT).as_posix(),'patches':[],
           'output_iso_sha256':validation['output_iso_sha256'],'generation':0}
    # A failure before the state commit leaves a partial ISO, never a published image.
    atomic_json(SESSION/'estado.json',state);partial.rename(IMAGE)
    return state


def write_state(stream,old,new):
    """Restore the union to baseline, then apply target state; size never changes."""
    for p in old+new:
        stream.seek(p['offset']);stream.write(p['before'])
    for p in new:
        stream.seek(p['offset']);stream.write(p['after'])
    stream.flush();os.fsync(stream.fileno())


def transact(relative,plan_sha256,session=SESSION,image=IMAGE,original=ORIGINAL,failure_hook=None):
    session=local(session);image=local(image)
    journal=session/'transacao.json';state_path=session/'estado.json'
    if journal.exists():raise ValueError('Transação pendente: execute recover antes de qualquer atualização')
    state=json.loads(state_path.read_text(encoding='utf-8'))
    if (ROOT/state['image']).resolve()!=image.resolve():raise ValueError('Estado pertence a outra ISO')
    old=deserialize(state['patches']);new=absolute_patches(relative)
    with exclusive(image) as target,original.open('rb') as source:
        if journal.exists():raise ValueError('Transação pendente; execute recover')
        state=json.loads(state_path.read_text(encoding='utf-8'))
        if (ROOT/state['image']).resolve()!=image.resolve():raise ValueError('Estado pertence a outra ISO')
        old=deserialize(state['patches'])
        directory=validated_patches(source,old);validated_patches(source,new)
        before=verify(source,target,old)
        if before['output_iso_sha256']!=state['output_iso_sha256']:raise ValueError('Estado e hash da ISO divergentes')
        if old==new:
            return {**before,'generation':state['generation'],'iso_directory_identical':True,'idempotent_no_write':True}
        transaction={'schema':1,'image':state['image'],'old_state':state,'new_patches':serialize(new),
                     'plan_sha256':plan_sha256,'status':'prepared'}
        atomic_json(journal,transaction)
        try:
            write_state(target,old,new)
            if failure_hook:failure_hook()
            validation=verify(source,target,new)
            if entries(target)!=directory:raise ValueError('Diretório ISO alterado')
            state={'schema':1,'image':state['image'],'patches':serialize(new),
                   'output_iso_sha256':validation['output_iso_sha256'],
                   'generation':state['generation']+1,'plan_sha256':plan_sha256}
            atomic_json(state_path,state)
            transaction['status']='committed';atomic_json(session/'ultima-transacao.json',transaction)
            journal.unlink()
            return {**validation,'generation':state['generation'],'iso_directory_identical':True}
        except BaseException:
            # Persist prepared journal on failures, including an interrupted process.
            # Recovery always returns to old state, even if the state commit happened.
            raise


def recover(session=SESSION,image=IMAGE,original=ORIGINAL):
    session=local(session);image=local(image);journal=session/'transacao.json'
    tx=json.loads(journal.read_text(encoding='utf-8'));old_state=tx['old_state']
    if (ROOT/tx['image']).resolve()!=image.resolve():raise ValueError('Journal pertence a outra ISO')
    old=deserialize(old_state['patches']);new=deserialize(tx['new_patches'])
    with exclusive(image) as target,original.open('rb') as source:
        validated_patches(source,old);validated_patches(source,new)
        # Only expected mutation ranges may differ during interrupted recovery.
        ranges=sorted((p['offset'],p['offset']+len(p['before'])) for p in old+new)
        source.seek(0);target.seek(0);pos=0;source_hash=hashlib.sha256()
        while block:=source.read(1024*1024):
            source_hash.update(block)
            actual=bytearray(target.read(len(block)));expected=bytearray(block)
            if len(actual)!=len(expected):raise ValueError('Tamanho da ISO divergente na recuperação')
            for a,b in ranges:
                lo=max(a,pos)-pos;hi=min(b,pos+len(block))-pos
                if hi>lo:actual[lo:hi]=expected[lo:hi]
            if actual!=expected:raise ValueError('Alteração fora da transação; recuperação automática recusada')
            pos+=len(block)
        if target.read(1):raise ValueError('ISO tem bytes adicionais')
        if source_hash.hexdigest()!=ORIGINAL_ISO_SHA256:raise ValueError('ISO original divergente; nenhuma recuperação gravada')
        write_state(target,new,old);validation=verify(source,target,old)
        if validation['output_iso_sha256']!=old_state['output_iso_sha256']:raise ValueError('Rollback diverge do estado anterior')
        atomic_json(session/'estado.json',old_state)
        tx['status']='rolled_back';atomic_json(session/'ultima-recuperacao.json',tx);journal.unlink()
        return validation
