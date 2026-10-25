"""Prepare only the manually authored role map; no machine translation or APIs."""
import argparse,json,mmap,collections,copy
from pathlib import Path
from build_translation_pilot import load_draft,compile_draft,ROOT,SOURCE
from speaker_labels import ROLES,POLICY,bindings,validate_label
from dialogue import sha
from gfi import encode
from interface_text import SOURCE as ELF

def prepare(data,parent,elf):
    document,_,report=compile_draft(data,parent)
    if not report['valid']:raise ValueError('Invalid parent')
    entries=[];deferred=[];excluded=collections.Counter();roles=set()
    for e in document['entries']:
        for s in e['segments']:
            if s['key']!='label':continue
            source=s['source']
            if source not in ROLES:excluded[source]+=1;continue
            target=ROLES[source];reason=None
            if e['id'] in parent.get('preservation_decisions',{}) or e['blocked_reasons']:reason='record_blocked_or_preserved'
            elif len(encode(target))>s['capacity']:reason='natural_target_exceeds_original_slot'
            if reason:
                deferred.append({'id':e['id'],'label_sha256':sha(bytes.fromhex(s['source_hex'])),
                    'capacity':s['capacity'],'target_bytes':len(encode(target)),'reason':reason});continue
            validate_label(source,target,s['capacity']);roles.add(source)
            entries.append({'id':e['id'],'record_sha256':e['record_sha256'],
                'label_sha256':sha(bytes.fromhex(s['source_hex'])),'translation':target})
    return {'policy':POLICY,'instruction_windows':bindings(elf),'entries':entries},{
        'accepted_label_fields':len(entries),'distinct_source_roles':len(roles),
        'deferred_reviewed_role_references':len(deferred),'deferred':deferred,
        'excluded_unreviewed_or_protected_references':sum(excluded.values()),
        'excluded_unique_labels':len(excluded),'automatic_generic_role_detection':False,
        'source_body_translations_preserved':report['accepted'],'pcsx2_executed':False}

def prepare_relocations(data,parent,elf,*,byte_packed=False):
    from speaker_label_space import POLICY,BYTE_POLICY,bindings,placement
    if byte_packed:POLICY=BYTE_POLICY
    document,patches,report=compile_draft(data,parent)
    if not report['valid']:raise ValueError('Invalid relocation parent')
    compiled={p['id']:p for p in patches}
    key='speaker_label_byte_packing' if byte_packed else 'speaker_label_relocations'
    entries=copy.deepcopy(parent.get(key,{}).get('entries',[]));inherited=len(entries)
    deferred=[];roles=set()
    for e in document['entries']:
        for s in e['segments']:
            if s['key']!='label' or s['source'] not in ROLES or s['translation']!=s['source']:continue
            target=ROLES[s['source']]
            if len(encode(target))<=s['capacity']:continue
            original=bytes(data[e['offset']:e['offset']+e['size']]);base=compiled[e['id']]['after'] if e['id'] in compiled else original
            try:
                if e['id'] in parent.get('preservation_decisions',{}):raise ValueError('Explicit preservation decision')
                start,_,_=placement(base,e,target,alignment=1 if byte_packed else 4)
            except ValueError as error:
                deferred.append({'id':e['id'],'label_sha256':sha(bytes.fromhex(s['source_hex'])),
                    'capacity':s['capacity'],'target_bytes':len(encode(target)),'reason':str(error)});continue
            roles.add(s['source']);entries.append({'id':e['id'],'record_sha256':e['record_sha256'],
                'label_sha256':sha(bytes.fromhex(s['source_hex'])),'translation':target,
                'base_record_sha256':sha(base),'target_offset':e['offset']+start})
    return {'policy':POLICY,'instruction_windows':bindings(elf),'entries':entries},{
        'new_label_fields':len(entries)-inherited,'total_relocated_label_fields':len(entries),'distinct_source_roles':len(roles),
        'remaining_reviewed_role_references':len(deferred),'deferred':deferred,
        'source_body_translations_preserved':sum(any(s['key']!='label' and s['translation']!=s['source'] for s in e['segments']) for e in document['entries']),
        'pcsx2_executed':False}

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--parent',type=Path,required=True)
    mode=p.add_mutually_exclusive_group()
    mode.add_argument('--relocate',action='store_true',help='Borrow proven separator zeros after parent compilation')
    mode.add_argument('--byte-packed',action='store_true',help='Allow byte-positioned label tails under the separate v003 policy')
    p.add_argument('--output',type=Path,required=True);p.add_argument('--report',type=Path,required=True);a=p.parse_args()
    parent=a.parent.resolve();output=a.output.resolve();summary=a.report.resolve()
    if not parent.is_relative_to(ROOT/'translations') or not output.is_relative_to(ROOT/'translations') or not summary.is_relative_to(ROOT/'reports') or output.exists() or summary.exists():raise ValueError('Use new authored recipe/report inside project')
    draft,_=load_draft(parent)
    with SOURCE.open('rb') as stream,mmap.mmap(stream.fileno(),0,access=mmap.ACCESS_READ) as data:
        config,report=(prepare_relocations(data,draft,ELF.read_bytes(),byte_packed=a.byte_packed) if a.relocate or a.byte_packed else prepare(data,draft,ELF.read_bytes()))
    child={'schema':1,'extends':parent.name,'name':output.stem,
        'status':('Rótulos genéricos com folga interna; falas herdadas; visual pendente' if a.relocate or a.byte_packed else 'Rótulos genéricos de falantes em slots fixos; falas herdadas; visual pendente'),
        'translations':{},'speaker_label_byte_packing' if a.byte_packed else 'speaker_label_relocations' if a.relocate else 'speaker_labels':config}
    for path,value in ((output,child),(summary,report)):
        with path.open('x',encoding='utf-8') as stream:json.dump(value,stream,ensure_ascii=False,indent=2);stream.write('\n')
    pending=report.get('remaining_reviewed_role_references',report.get('deferred_reviewed_role_references'))
    print(f"Rótulos: {len(config['entries'])}; adiados: {pending}")
