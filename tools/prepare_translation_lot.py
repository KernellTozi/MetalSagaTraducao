"""Prepare a larger local authoring lot with conservative exact-source reuse.

No translation/API calls. Blank targets deliberately block compilation until
reviewed. Original text/context is exported exclusively below ignored work/.
"""
import argparse
import json
import mmap
from pathlib import Path
import re
import shutil

from build_translation_pilot import DEFAULT_DRAFT,load_draft,compile_draft,write_json
from reinsertion import ROOT,SOURCE,descriptor,local
from dialogue_advanced import SsdIndex,LAYOUTS


def signature(entry):
    return tuple((s['key'],s['source_hex']) for s in entry['segments'])


def prepare(data,parent,end=None,*,start=None):
    document,_,validation=compile_draft(data,parent)
    if not validation['valid']:raise ValueError('Parent lot must compile before reuse')
    index=SsdIndex(data);previous_start=int(parent['scope']['first_offset'],16)
    previous_end=int(parent['scope']['last_offset'],16)
    if (start is None)==(end is None):raise ValueError('Choose exactly one interval boundary to extend')
    if start is not None:
        if not 0<=start<previous_start:raise ValueError('New start must precede the previous interval')
        end=previous_end
    else:
        if end<=previous_end:raise ValueError('New lot must extend the previous interval')
        start=previous_start
    excluded=set(parent.get('deferred',{}))
    exception=parent.get('ascii_exception',{})
    if exception:excluded.add(exception['id'])
    pool={signature(e):e['id'] for e in document['entries']
          if not e['blocked_reasons'] and e['id'] not in excluded}
    aliases={};targets={};deferred={};pending=[];count=len(document['entries'])
    for at in sorted(index.records):
        if not (start<=at<previous_start or previous_end<at<=end):continue
        if bytes(data[at:at+4]) not in set(LAYOUTS)|{b'msg\0',b'msgn'}:continue
        entry=descriptor(data,at,index);count+=1;key=entry['id'];sig=signature(entry)
        if entry['blocked_reasons']:
            deferred[key]='; '.join(entry['blocked_reasons']);continue
        if sig in pool:
            aliases[key]=pool[sig];continue
        pool[sig]=key
        editable=[s for s in entry['segments'] if s['editable']]
        targets[key]='' if len(editable)==1 else {s['key']:'' for s in editable}
        pending.append(entry)
    return {'scope':{'first_offset':f'{start:08x}','last_offset':f'{end:08x}','records':count},
            'translations':targets,'aliases':aliases,'deferred':deferred},pending


def main():
    parser=argparse.ArgumentParser(description='Preparar lote maior sem traduzir nem gerar ISO')
    parser.add_argument('--parent',type=Path,default=DEFAULT_DRAFT)
    boundary=parser.add_mutually_exclusive_group(required=True)
    boundary.add_argument('--end-offset',type=lambda s:int(s,16))
    boundary.add_argument('--start-offset',type=lambda s:int(s,16))
    parser.add_argument('--lot-id',required=True)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    if not re.fullmatch(r'[a-z0-9-]+',args.lot_id):raise ValueError('Invalid lot ID')
    output=local(args.output,True);parent,sources=load_draft(args.parent)
    with SOURCE.open('rb') as stream,mmap.mmap(stream.fileno(),0,access=mmap.ACCESS_READ) as data:
        planned,pending=prepare(data,parent,args.end_offset,start=args.start_offset)
    names=[Path(s['path']).name for s in sources]
    if len(names)!=len(set(names)) or args.lot_id+'.json' in names:raise ValueError('Draft filename collision')
    output.mkdir(parents=True)
    for source in sources:shutil.copyfile(ROOT/source['path'],output/Path(source['path']).name)
    draft={'schema':1,'extends':args.parent.name,'name':args.lot_id,
           'status':'rascunho pendente; alvos vazios bloqueiam compilação',
           'font_profile':parent['font_profile'],'terminology_policy':'translations/politica.json',
           'iso_name':f'MetalSaga-ptbr-{args.lot_id}.iso',**planned}
    write_json(output/(args.lot_id+'.json'),draft)
    with (output/'contexto-pendente.jsonl').open('x',encoding='utf-8') as stream:
        for entry in pending:stream.write(json.dumps(entry,ensure_ascii=False)+'\n')
    report={'parent_sources':sources,'parent_records':parent['scope']['records'],
            'total_records':planned['scope']['records'],'unique_targets_pending':len(pending),
            'exact_source_reuse_proposals':len(planned['aliases']),'new_deferred':len(planned['deferred']),
            'runtime_validated':False,'context_review_required':True}
    write_json(output/'preparacao.json',report)
    print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':main()
