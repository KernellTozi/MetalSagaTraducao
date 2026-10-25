"""Prepare only the manually authored role map; no machine translation or APIs."""
import argparse,json,mmap,collections
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

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--parent',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True);p.add_argument('--report',type=Path,required=True);a=p.parse_args()
    parent=a.parent.resolve();output=a.output.resolve();summary=a.report.resolve()
    if not parent.is_relative_to(ROOT/'translations') or not output.is_relative_to(ROOT/'translations') or not summary.is_relative_to(ROOT/'reports') or output.exists() or summary.exists():raise ValueError('Use new authored recipe/report inside project')
    draft,_=load_draft(parent)
    with SOURCE.open('rb') as stream,mmap.mmap(stream.fileno(),0,access=mmap.ACCESS_READ) as data:
        config,report=prepare(data,draft,ELF.read_bytes())
    child={'schema':1,'extends':parent.name,'name':output.stem,
        'status':'Rótulos genéricos de falantes em slots fixos; falas herdadas; visual pendente',
        'translations':{},'speaker_labels':config}
    for path,value in ((output,child),(summary,report)):
        with path.open('x',encoding='utf-8') as stream:json.dump(value,stream,ensure_ascii=False,indent=2);stream.write('\n')
    print(f"Rótulos: {len(config['entries'])}; adiados: {report['deferred_reviewed_role_references']}")
