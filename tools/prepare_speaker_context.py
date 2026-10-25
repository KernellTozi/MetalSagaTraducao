"""Prepare the explicitly reviewed role captions and bounded leftover choices."""
import argparse,collections,copy,json,mmap
from pathlib import Path
from build_translation_pilot import ROOT,SOURCE,compile_draft,load_draft
from interface_text import SOURCE as ELF
from speaker_label_review import POLICY,EXTRA,construct,bindings
from speaker_labels import ROLES
from dialogue import sha
from gfi import encode

def prepare(data,parent,elf):
    document,patches,report=compile_draft(data,parent)
    if not report['valid']:raise ValueError('Invalid reviewed-role parent')
    patches={p['id']:p for p in patches};items=copy.deepcopy(parent.get('speaker_context_review',{}).get('entries',[]));inherited=len(items)
    deferred=[];layouts=collections.Counter();reviewed=legacy=0
    for e in document['entries']:
        label=next((s for s in e['segments'] if s['key']=='label'),None)
        if not label or label['translation']!=label['source']:continue
        source=label['source'];target=EXTRA.get(source,ROLES.get(source))
        if target is None or source not in EXTRA and len(encode(target))<=label['capacity']:continue
        original=bytes(data[e['offset']:e['offset']+e['size']]);base=patches[e['id']]['after'] if e['id'] in patches else original
        try:
            if e['id'] in parent.get('preservation_decisions',{}):raise ValueError('Explicit preservation decision')
            _,positions,layout=construct(base,e,target)
        except ValueError as error:
            deferred.append({'id':e['id'],'label_sha256':sha(bytes.fromhex(label['source_hex'])),'reason':str(error)});continue
        layouts[layout]+=1;reviewed+=source in EXTRA;legacy+=source not in EXTRA
        items.append({'id':e['id'],'record_sha256':e['record_sha256'],'label_sha256':sha(bytes.fromhex(label['source_hex'])),
            'base_record_sha256':sha(base),'translation':target,'layout':layout,'target_offsets':[e['offset']+at for at in positions]})
    return {'policy':POLICY,'instruction_windows':bindings(elf),'entries':items},{
        'new_label_fields':len(items)-inherited,'total_reviewed_label_fields':len(items),
        'newly_reviewed_role_references':reviewed,'recovered_legacy_references':legacy,
        'new_layout_counts':dict(layouts),'remaining_role_references':len(deferred),'deferred':deferred,'pcsx2_executed':False}

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--parent',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True);p.add_argument('--report',type=Path,required=True);a=p.parse_args()
    parent=a.parent.resolve();output=a.output.resolve();summary=a.report.resolve()
    if not parent.is_relative_to(ROOT/'translations') or not output.is_relative_to(ROOT/'translations') or not summary.is_relative_to(ROOT/'reports') or output.exists() or summary.exists():raise ValueError('Use new recipe/report inside translations/ and reports/')
    draft,_=load_draft(parent)
    with SOURCE.open('rb') as stream,mmap.mmap(stream.fileno(),0,access=mmap.ACCESS_READ) as data:
        config,report=prepare(data,draft,ELF.read_bytes())
    child={'schema':1,'extends':parent.name,'name':output.stem,'status':'Funções revistas por contexto e escolhas nomeadas com folga interna; visual pendente','translations':{},'speaker_context_review':config}
    for path,value in ((output,child),(summary,report)):
        with path.open('x',encoding='utf-8') as stream:json.dump(value,stream,ensure_ascii=False,indent=2);stream.write('\n')
    print(f"Novos rótulos: {report['new_label_fields']}; pendentes: {report['remaining_role_references']}")
