"""Real-source binary tests in memory; never applies mass changes to an ISO."""
import argparse
import collections
import copy
import json
import mmap
from pathlib import Path
import time

from reinsertion import SOURCE,ROOT,export,compile_batch,descriptor,POLICY,RESOURCE
from dialogue import sha
from dialogue_formats import tokens
from dialogue_advanced import SsdIndex


def validate():
    start=time.perf_counter()
    with SOURCE.open('rb') as stream,mmap.mmap(stream.fileno(),0,access=mmap.ACCESS_READ) as data:
        index=SsdIndex(data);document=export(data,index);baseline=sha(data)
        noops,no_report=compile_batch(data,document,index)
        if not no_report['valid'] or noops:raise ValueError('Round-trip do catálogo produziu mudanças')
        coverage=collections.Counter();blocked=collections.Counter();mutated=collections.Counter();no_literals=[];padding=collections.Counter()
        for entry in document['entries']:
            tag=bytes.fromhex(entry['tag']).rstrip(b'\0').decode('ascii')
            if entry['blocked_reasons']:
                blocked[tag]+=1;continue
            coverage[tag]+=1;done=False
            for field in entry['segments']:
                if not field['editable']:continue
                raw=bytes.fromhex(field['source_hex']);parts,_=tokens(raw)
                excluded={i for t in parts for i in range(t['relative_offset'],t['relative_offset']+len(bytes.fromhex(t['hex'])))}
                padding[field['capacity']-len(raw)]+=1
                for i,value in enumerate(raw):
                    if i in excluded:continue
                    new=chr(value).swapcase() if chr(value).isalpha() else ',' if value==46 else '.'
                    text=field['source'];field['translation']=text[:i]+new+text[i+1:]
                    mutated[tag]+=1;done=True;break
                if done:break
            if not done:no_literals.append(entry['id'])
        patches,result=compile_batch(data,document,index)
        if not result['valid']:
            raise ValueError(json.dumps([r for r in result['results'] if r['status']=='refused'],ensure_ascii=False))
        by_block=collections.defaultdict(list)
        for p in patches:by_block[index.records[p['offset']]['block_offset']].append(p)
        for block_at,items in by_block.items():
            end=index.records[items[0]['offset']]['block_end'];before=bytes(data[block_at:end]);after=bytearray(before)
            for p in items:
                a=p['offset']-block_at
                if after[a:a+len(p['before'])]!=p['before']:raise ValueError('Patch baseline incorreto')
                after[a:a+len(p['after'])]=p['after']
            if SsdIndex(bytes(after)).records!=SsdIndex(before).records:
                raise ValueError('Índices/fronteiras SSD mudaram')
        def one(entry):
            return {'schema':1,'policy':POLICY,'resource':RESOURCE,'source_sha256':baseline,
                    'catalog_version':'v003','entries':[entry]}
        e=descriptor(data,0x11620,index)
        e['segments'][0]['translation']=e['segments'][0]['source'].replace('?',' now?',1)
        e['segments'][1]['translation']='Yes\tNo'
        _,slot_report=compile_batch(data,one(e),index)
        if slot_report['valid']:raise ValueError('Caso de expansão escolhido não excede slot original')
        e['mode']='repack';repack,repack_report=compile_batch(data,one(e),index)
        if not repack_report['valid']:raise ValueError('Repack real falhou')
        expanded=repack_report['results'][0]
        if expanded['target_lengths'][0]<=expanded['source_capacities'][0]:raise ValueError('Não houve expansão real além do slot')
        old=descriptor(data,0x1139c,index);name=old['segments'][1]['source']
        old['mode']='repack';old['segments'][0]['translation']='Teste\n'+old['segments'][0]['source'].split('\n',1)[1]
        named,named_report=compile_batch(data,one(old),index)
        if not named_report['valid'] or name.encode('ascii') not in named[0]['after']:raise ValueError('Rótulo ms gn não preservado')
        huge=descriptor(data,0x1df47f0c,index)
        huge['segments'][0]['translation']='X'*40+'\n'+'Y'*40
        oversized,oversized_report=compile_batch(data,one(huge),index)
        if oversized_report['valid'] or oversized:raise ValueError('Crescimento externo deveria ser bloqueado')
        if sha(data)!=baseline:raise ValueError('Arquivo original foi alterado')
    return {'schema':1,'source_sha256':baseline,'source_unchanged':True,'catalog_noop_roundtrip':True,
            'records':len(document['entries']),'eligible':sum(coverage.values()),'blocked':sum(blocked.values()),
            'eligible_by_family':dict(coverage),'blocked_by_family':dict(blocked),
            'binary_edits_tested':len(patches),'tested_by_family':dict(mutated),
            'eligible_without_editable_literal':no_literals,'verified_affected_ssd_blocks':len(by_block),
            'padding_free_bytes_histogram':dict(padding),
            'real_repack_expansion':expanded,'real_named_repack':named_report['results'][0],
            'external_record_growth_refused':oversized_report['results'][0],
            'test_method':'Deterministic one-byte case/punctuation changes in memory, not linguistic translation; no ISO update',
            'runtime_visual_validation':False,'elapsed_seconds':round(time.perf_counter()-start,3)}


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--report',type=Path,required=True);args=parser.parse_args()
    path=args.report.resolve()
    if not (path.is_relative_to(ROOT/'reports') or path.is_relative_to(ROOT/'work')) or path.exists():parser.error('Use um relatório novo em reports/ ou work/')
    result=validate();path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('x',encoding='utf-8') as stream:json.dump(result,stream,indent=2,ensure_ascii=False);stream.write('\n')
    print(f'Politica: {result["eligible"]} elegiveis; {result["binary_edits_tested"]} edicoes binarias verificadas. Sem ISO nova.')


if __name__=='__main__':main()
