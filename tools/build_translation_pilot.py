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
import copy
from datetime import datetime

from reinsertion import ROOT,SOURCE,RESOURCE,POLICY,NAMED_POLICY,B15_POLICY,descriptor,source_hash,compile_batch,local
from dialogue_advanced import SsdIndex,LAYOUTS
from dialogue_formats import tokens
from gfi import Gfi,encode,decode
from glyph_spacing import elf_patch
from disc import entries,digest,SECTOR
from build_dialogue_iso import compare_streams,ORIGINAL_ISO_SHA256

DRAFT=ROOT/'translations/piloto-inicial-v001.json'
PROFILE='spacing-v003-assumed-by-user-not-visually-confirmed'
REGION_V2_DRAFT=ROOT/'translations/regiao-inicial-v002.json'
REGION_V3_DRAFT=ROOT/'translations/regiao-inicial-v003.json'
REGION_V4_DRAFT=ROOT/'translations/regiao-inicial-v004.json'
REGION_V5_DRAFT=ROOT/'translations/regiao-inicial-v005.json'
REGION_V6_DRAFT=ROOT/'translations/regiao-inicial-v006.json'
REGION_V7_DRAFT=ROOT/'translations/regiao-inicial-v007.json'
REGION_V8_DRAFT=ROOT/'translations/regiao-inicial-v008.json'
REGION_V9_DRAFT=ROOT/'translations/regiao-inicial-v009.json'
REGION_V10_DRAFT=ROOT/'translations/regiao-inicial-v010.json'
REGION_V11_DRAFT=ROOT/'translations/regiao-inicial-v011.json'
REGION_V12_DRAFT=ROOT/'translations/regiao-inicial-v012.json'
REGION_V13_DRAFT=ROOT/'translations/regiao-inicial-v013.json'
REGION_V14_DRAFT=ROOT/'translations/regiao-inicial-v014.json'
REGION_V15_DRAFT=ROOT/'translations/regiao-inicial-v015.json'
REGION_V16_DRAFT=ROOT/'translations/regiao-inicial-v016.json'
REGION_V17_DRAFT=ROOT/'translations/regiao-inicial-v017.json'
REGION_V18_DRAFT=ROOT/'translations/regiao-inicial-v018.json'
REGION_V19_DRAFT=ROOT/'translations/regiao-inicial-v019.json'
REGION_V20_DRAFT=ROOT/'translations/regiao-inicial-v020.json'
REGION_V21_DRAFT=ROOT/'translations/regiao-inicial-v021.json'
REGION_V22_DRAFT=ROOT/'translations/regiao-inicial-v022.json'
REGION_V23_DRAFT=ROOT/'translations/regiao-inicial-v023.json'
DEFAULT_DRAFT=ROOT/'translations/regiao-inicial-v024.json'


def unique_object(pairs):
    result={}
    for key,value in pairs:
        if key in result:raise ValueError(f'Duplicate authored JSON key: {key}')
        result[key]=value
    return result


def load_draft(path,chain=()):
    path=Path(path).resolve()
    if not path.is_relative_to(ROOT) or path in chain or len(chain)>=64:
        raise ValueError('Draft outside project or circular inheritance')
    raw=path.read_bytes();child=json.loads(raw.decode('utf-8-sig'),object_pairs_hook=unique_object);sources=[]
    if 'extends' in child:
        base,sources=load_draft(path.parent/child['extends'],chain+(path,))
        draft={**base,**child}
        for key in ('translations','deferred','aliases'):
            draft[key]={**base.get(key,{}),**child.get(key,{})}
        resumed=child.get('resume_deferred',[])
        if (not isinstance(resumed,list) or any(not isinstance(key,str) for key in resumed)
                or len(resumed)!=len(set(resumed))):
            raise ValueError('Invalid resumed deferred IDs')
        for key in resumed:
            if (key not in base.get('deferred',{}) or key not in child.get('translations',{})
                    or key in child.get('deferred',{}) or key in child.get('aliases',{})):
                raise ValueError('Resumed record must be deferred in parent and explicitly translated in child')
            draft['deferred'].pop(key)
    else:
        if child.get('resume_deferred'):raise ValueError('Cannot resume without parent')
        draft=child
    draft.pop('extends',None)
    draft.pop('resume_deferred',None)
    sources.append({'path':path.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(raw).hexdigest()})
    return draft,sources


def compile_draft(data,draft):
    if draft.get('schema')!=1 or draft.get('font_profile')!=PROFILE:
        raise ValueError('Unsupported pilot schema/font profile')
    policy=draft.get('reinsertion_policy',POLICY)
    if policy not in (POLICY,NAMED_POLICY,B15_POLICY):raise ValueError('Unknown reinsertion policy')
    named_choices=policy in (NAMED_POLICY,B15_POLICY)
    b15=policy==B15_POLICY
    targets=copy.deepcopy(draft['translations']);deferred=draft.get('deferred',{})
    if not isinstance(targets,dict) or not targets:raise ValueError('Empty draft')
    index=SsdIndex(data);selected=[]
    lo=int(draft['scope']['first_offset'],16);hi=int(draft['scope']['last_offset'],16)
    for at in sorted(index.records):
        if lo<=at<=hi and bytes(data[at:at+4]) in set(LAYOUTS)|{b'msg\0',b'msgn'}:
            selected.append(descriptor(data,at,index,named_choices=named_choices,b15=b15))
    by_id={e['id']:e for e in selected}
    aliases=dict(draft.get('aliases',{}))
    while aliases:
        ready=[key for key,value in aliases.items() if value in targets]
        if not ready:raise ValueError('Unresolved/circular translation alias')
        for key in ready:
            parent=aliases.pop(key)
            if key in targets or key not in by_id or parent not in by_id:
                raise ValueError('Invalid alias identity')
            if [(s['key'],s['source']) for s in by_id[key]['segments']]!=[(s['key'],s['source']) for s in by_id[parent]['segments']]:
                raise ValueError('Translation reuse requires identical source segments')
            targets[key]=copy.deepcopy(targets[parent])
    if set(targets)&set(deferred) or any(not isinstance(v,str) or not v.strip() for v in deferred.values()):
        raise ValueError('Invalid deferred record/reason')
    if len(selected)!=draft['scope']['records'] or set(by_id)!=set(targets)|set(deferred):
        raise ValueError('Draft does not exactly cover the declared scene interval')
    terminology=[]
    for entry in selected:
        if entry['id'] in deferred:continue
        value=targets[entry['id']]
        editable=[s for s in entry['segments'] if s['editable']]
        if isinstance(value,str):
            if len(editable)!=1:raise ValueError('Multi-segment target requires explicit keys')
            value={editable[0]['key']:value}
        if not isinstance(value,dict) or set(value)!={s['key'] for s in editable}:
            raise ValueError('Missing segment or attempted protected-label edit')
        for segment in editable:
            segment['translation']=value[segment['key']]
            if not isinstance(segment['translation'],str) or (segment['source'].strip() and not segment['translation'].strip()):
                raise ValueError('Empty or invalid authored translation')
            if draft.get('terminology_policy'):
                if draft['terminology_policy']!='translations/politica.json':raise ValueError('Unknown terminology policy')
                from translation_policy import validate
                if not isinstance(segment['translation'],str):raise ValueError('Invalid translation')
                if segment['translation']!=segment['source']:
                    terminology.extend({'id':entry['id'],'segment':segment['key'],'reason':reason}
                                       for reason in validate(segment['source'],segment['translation']))
    document={'schema':1,'policy':policy,'resource':RESOURCE,'source_sha256':source_hash(data),
              'catalog_version':'v003','entries':selected}
    patches,report=compile_batch(data,document,index)
    # Read back actual translated spans independently; the existing compiler
    # validates headers, controls, lengths and structural shadow parsers.
    for patch in patches:
        entry=by_id[patch['id']]
        for segment in entry['segments']:
            start=segment['offset']-entry['offset']
            target=patch['after'][start:].split(b'\0',1)[0]
            if target!=(bytes.fromhex(segment['source_hex']) if segment['translation']==segment['source'] else encode(segment['translation'])):
                raise ValueError('Pilot readback differs')
    report['deferred']=[{'id':key,'reason':value} for key,value in deferred.items()]
    report['terminology_issues']=terminology
    report['terminology_refused_records']=len({issue['id'] for issue in terminology})
    if terminology:report['valid']=False;patches=[]
    return document,patches,report


def write_json(path,value):
    with path.open('x',encoding='utf-8',newline='\n') as stream:
        json.dump(value,stream,ensure_ascii=False,indent=2);stream.write('\n')


def build_iso(output,patches,layout_profile='spacing-v003'):
    if layout_profile not in ('spacing-v003','ptbr-layout-v004','ptbr-layout-v005'):raise ValueError('Unknown layout profile')
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
    layout_evidence=None
    if layout_profile in ('ptbr-layout-v004','ptbr-layout-v005'):
        from glyph_layout import elf_patch as layout_patch
        p=layout_patch(elf)
        patches.append({'resource':'SLUS_212.93',**p})
        layout_evidence={'offset':p['offset'],'size':len(p['after']),
            'source_sha256':hashlib.sha256(p['before']).hexdigest(),
            'patched_sha256':hashlib.sha256(p['after']).hexdigest(),
            'scope':'18 PT-BR codes inherit ASCII base draw width, width margin, bearing and advance',
            'bitmaps':'unchanged v002','runtime_validated':False}
    if layout_profile=='ptbr-layout-v005':
        from glyph_single import elf_patch as single_patch
        p=single_patch(elf)
        patches.append({'resource':'SLUS_212.93',**p})
        layout_evidence['single_glyph']={'offset':p['offset'],'size':len(p['after']),
            'source_sha256':hashlib.sha256(p['before']).hexdigest(),
            'patched_sha256':hashlib.sha256(p['after']).hexdigest(),
            'cache_code_retained':True,'runtime_validated':False}
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
    from iso_retention import prune
    retention=prune(reserve=1)
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
    return {**validation,'iso_directory_identical':True,'fonts':fonts,'retention':retention,
            'elf_profile':layout_profile,'layout_patch':layout_evidence,'visual_status':'pending_user_verification' if layout_evidence else 'assumed_by_user_pending_actual_test'}


def select_layout_profile(draft,override=None):
    selected=override or draft.get('layout_profile','spacing-v003')
    if selected not in ('spacing-v003','ptbr-layout-v004','ptbr-layout-v005'):raise ValueError('Unknown recipe layout profile')
    if override and draft.get('layout_profile') and override!=draft['layout_profile']:raise ValueError('Layout override conflicts with bound recipe profile')
    return selected


def main():
    parser=argparse.ArgumentParser(description='Compilação local de lotes contextuais, sem APIs')
    parser.add_argument('--draft',type=Path,default=DEFAULT_DRAFT)
    parser.add_argument('--output',type=Path,default=ROOT/'work/pilotos'/f'{datetime.now():%Y%m%d-%H%M%S-%f}')
    parser.add_argument('--build-iso',action='store_true')
    parser.add_argument('--layout-profile',choices=('spacing-v003','ptbr-layout-v004','ptbr-layout-v005'),default=None)
    parser.add_argument('--iso-name',help='Optional experimental image name; never changes the saved recipe')
    args=parser.parse_args();output=local(args.output,True)
    draft_path=args.draft.resolve()
    if not draft_path.is_relative_to(ROOT):raise ValueError('Draft must be inside workspace')
    raw=draft_path.read_bytes();draft,sources=load_draft(draft_path)
    layout_profile=select_layout_profile(draft,args.layout_profile)
    with SOURCE.open('rb') as stream,mmap.mmap(stream.fileno(),0,access=mmap.ACCESS_READ) as data:
        document,patches,report=compile_draft(data,draft)
    output.mkdir(parents=True)
    write_json(output/'plano.json',document)
    write_json(output/'rascunho.json',draft)
    report.update({'draft_sha256':hashlib.sha256(raw).hexdigest(),
                   'draft_sources':sources,
                   'font_profile':PROFILE,'layout_profile':layout_profile,'narrative_status':draft['status'],
                   'visual_status':'assumed_by_user_pending_actual_test'})
    if draft.get('terminology_policy'):
        policy_path=ROOT/draft['terminology_policy']
        report['terminology_policy_sha256']=hashlib.sha256(policy_path.read_bytes()).hexdigest()
    if report['valid'] and args.build_iso:
        name=args.iso_name or draft.get('iso_name','MetalSaga-ptbr-piloto-inicial-v001.iso')
        if Path(name).name!=name or not name.startswith('MetalSaga-ptbr-') or not name.endswith('.iso'):
            raise ValueError('Invalid ISO name')
        report['iso']=build_iso(output/name,patches,layout_profile)
        report['iso']['image_name']=name
        report['visual_status']=report['iso']['visual_status']
    write_json(output/'relatorio.json',report)
    with (output/'revisao.jsonl').open('x',encoding='utf-8') as stream:
        for e,r in zip(document['entries'],report['results']):
            source=e['segments'][0]['source'];target=e['segments'][0]['translation']
            stream.write(json.dumps({'id':e['id'],'block_offset':e['block_offset'],
                'source':source,'translation':target,'validation':r,
                'segments':e['segments'],
                'speaker':'unresolved; infer from scene, not proven header mapping'},ensure_ascii=False)+'\n')
    print(f"Traduzidos: {report['accepted']}; preservados: {report['unchanged']}; recusados: {report['refused']}. {output}")
    if report['terminology_issues']:print('Lote bloqueado por violações de terminologia; consulte o relatório.')
    if not report['valid']:raise SystemExit(2)


if __name__=='__main__':main()
