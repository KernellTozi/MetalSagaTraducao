"""Compile the contextual opening pilot locally, optionally build a fixed ISO.

Original text stays in ignored work/, while the authored PT-BR draft is tracked.
The v004 compiler and legacy development ISO policy remain unchanged.
"""
import argparse
import hashlib
import json
import mmap
import os
from pathlib import Path
import shutil
import sys
from datetime import datetime

from reinsertion import ROOT,SOURCE,RESOURCE,POLICY,descriptor,source_hash,compile_batch,local
from dialogue_advanced import SsdIndex,LAYOUTS
from dialogue_formats import tokens
from gfi import Gfi,encode,decode
from glyph_spacing import elf_patch
from disc import entries,digest,SECTOR
from build_dialogue_iso import compare_streams,ORIGINAL_ISO_SHA256

DRAFT=ROOT/'translations/piloto-inicial-v001.json'
PROFILE='spacing-v003-assumed-by-user-not-visually-confirmed'


def compile_draft(data,draft):
    if draft.get('schema')!=1 or draft.get('font_profile')!=PROFILE:
        raise ValueError('Unsupported pilot schema/font profile')
    targets=draft['translations']
    if not isinstance(targets,dict) or not targets:raise ValueError('Empty draft')
    index=SsdIndex(data);selected=[]
    lo=int(draft['scope']['first_offset'],16);hi=int(draft['scope']['last_offset'],16)
    for at in sorted(index.records):
        if lo<=at<=hi and bytes(data[at:at+4]) in set(LAYOUTS)|{b'msg\0',b'msgn'}:
            selected.append(descriptor(data,at,index))
    if len(selected)!=draft['scope']['records'] or {e['id'] for e in selected}!=set(targets):
        raise ValueError('Draft does not exactly cover the declared scene interval')
    for entry in selected:
        if len(entry['segments'])!=1:raise ValueError('Pilot expects single-segment records')
        entry['segments'][0]['translation']=targets[entry['id']]
    document={'schema':1,'policy':POLICY,'resource':RESOURCE,'source_sha256':source_hash(data),
              'catalog_version':'v003','entries':selected}
    patches,report=compile_batch(data,document,index)
    # Read back actual translated spans independently; the existing compiler
    # validates headers, controls, lengths and structural shadow parsers.
    for patch in patches:
        entry=next(e for e in selected if e['id']==patch['id'])
        start=entry['segments'][0]['offset']-entry['offset']
        target=patch['after'][start:].split(b'\0',1)[0]
        if decode(target)!=targets[entry['id']]:raise ValueError('Pilot readback differs')
    return document,patches,report


def write_json(path,value):
    with path.open('x',encoding='utf-8',newline='\n') as stream:
        json.dump(value,stream,ensure_ascii=False,indent=2);stream.write('\n')


def build_iso(output,patches):
    output=local(output,True)
    sys.path.insert(0,str(ROOT/'work/python-deps'))
    from gfi_refined import font_patches
    reference=ROOT/'JOGO/Metal Saga'
    inventory={v['path']:v for v in json.loads((ROOT/'reports/inventory.json').read_text(encoding='utf-8'))}
    fonts=[]
    golden=json.loads((ROOT/'reports/fontes-v002-validation.json').read_text(encoding='utf-8'))
    expected={v['path']:v['patched_sha256'] for v in golden['fonts']}
    for name in ('DATA/SYS/SUC20I22.GFI','DATA/SYS/SUC24I26.GFI'):
        data=(reference/name).read_bytes()
        if hashlib.sha256(data).hexdigest()!=inventory[name]['sha256']:raise ValueError('Original font differs')
        modified=bytearray(data);font=Gfi(data)
        for p in font_patches(data):
            modified[p['offset']:p['offset']+len(p['after'])]=p['after']
            patches.append({'resource':name,**p})
        checksum=hashlib.sha256(modified).hexdigest()
        if checksum!=expected[name]:raise ValueError('Font differs from v002 profile')
        fonts.append({'path':name,'sha256':checksum,'side':font.side})
    elf=(reference/'SLUS_212.93').read_bytes()
    patches.append({'resource':'SLUS_212.93',**elf_patch(elf)})
    original=ROOT/'JOGO/Metal Saga.iso';absolute=[]
    with original.open('rb') as src:
        directory=entries(src)
        for name in sorted({p['resource'] for p in patches}):
            matching=[v for v in directory if v['path']==name]
            if len(matching)!=1:raise ValueError('Resource extent not unique')
            extent=matching[0];src.seek(extent['lba']*SECTOR)
            if extent['size']!=inventory[name]['size'] or digest(src,extent['size'])!=inventory[name]['sha256']:
                raise ValueError('ISO/extracted resource mismatch')
            for p in patches:
                if p['resource']!=name:continue
                if len(p['before'])!=len(p['after']) or not 0<=p['offset']<p['offset']+len(p['before'])<=extent['size']:
                    raise ValueError('Patch outside resource or resized')
                absolute.append({**p,'offset':extent['lba']*SECTOR+p['offset']})
    absolute.sort(key=lambda p:p['offset'])
    if any(a['offset']+len(a['before'])>b['offset'] for a,b in zip(absolute,absolute[1:])):
        raise ValueError('Overlapping patches')
    partial=output.with_suffix('.iso.partial')
    with original.open('rb') as src,partial.open('xb') as dst:
        shutil.copyfileobj(src,dst,1024*1024)
    with partial.open('r+b') as dst:
        for p in absolute:
            dst.seek(p['offset'])
            if dst.read(len(p['before']))!=p['before']:raise ValueError('Patch baseline mismatch')
            dst.seek(p['offset']);dst.write(p['after'])
        dst.flush();os.fsync(dst.fileno())
    with original.open('rb') as src,partial.open('rb') as dst:
        validation=compare_streams(src,dst,absolute)
        dst.seek(0)
        if entries(dst)!=directory:raise ValueError('ISO directory changed')
    if validation['source_iso_sha256']!=ORIGINAL_ISO_SHA256:raise ValueError('Original ISO hash differs')
    partial.rename(output)
    return {**validation,'iso_directory_identical':True,'fonts':fonts,
            'elf_profile':'spacing-v003','visual_status':'assumed_by_user_pending_actual_test'}


def main():
    parser=argparse.ArgumentParser(description='Piloto local da cena inicial, sem APIs')
    parser.add_argument('--draft',type=Path,default=DRAFT)
    parser.add_argument('--output',type=Path,default=ROOT/'work/pilotos'/f'{datetime.now():%Y%m%d-%H%M%S-%f}')
    parser.add_argument('--build-iso',action='store_true')
    args=parser.parse_args();output=local(args.output,True)
    draft_path=args.draft.resolve()
    if not draft_path.is_relative_to(ROOT):raise ValueError('Draft must be inside workspace')
    raw=draft_path.read_bytes();draft=json.loads(raw.decode('utf-8-sig'))
    with SOURCE.open('rb') as stream,mmap.mmap(stream.fileno(),0,access=mmap.ACCESS_READ) as data:
        document,patches,report=compile_draft(data,draft)
    output.mkdir(parents=True)
    write_json(output/'plano.json',document)
    write_json(output/'rascunho.json',draft)
    report.update({'draft_sha256':hashlib.sha256(raw).hexdigest(),
                   'font_profile':PROFILE,'narrative_status':draft['status'],
                   'visual_status':'assumed_by_user_pending_actual_test'})
    if report['valid'] and args.build_iso:
        report['iso']=build_iso(output/'MetalSaga-ptbr-piloto-inicial-v001.iso',patches)
    write_json(output/'relatorio.json',report)
    with (output/'revisao.jsonl').open('x',encoding='utf-8') as stream:
        for e,r in zip(document['entries'],report['results']):
            source=e['segments'][0]['source'];target=e['segments'][0]['translation']
            stream.write(json.dumps({'id':e['id'],'block_offset':e['block_offset'],
                'source':source,'translation':target,'validation':r,
                'speaker':'unresolved; infer from scene, not proven header mapping'},ensure_ascii=False)+'\n')
    print(f"{report['accepted']} translated, {report['unchanged']} unchanged, {report['refused']} refused. {output}")
    if not report['valid']:raise SystemExit(2)


if __name__=='__main__':main()
