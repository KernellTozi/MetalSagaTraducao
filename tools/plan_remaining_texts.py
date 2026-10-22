"""Read-only remaining-work inventory; emits metadata, never source dialogue."""
import argparse
from collections import Counter,defaultdict
import hashlib
import json
from pathlib import Path
from dialogue_formats import tokens,native_text
from reinsertion import ROOT,local


def inventory(folder):
    plan_raw=(folder/'plano.json').read_bytes();report_raw=(folder/'relatorio.json').read_bytes()
    plan=json.loads(plan_raw);report=json.loads(report_raw)
    if not report['valid'] or report['refused']:raise ValueError('Use valid compiled data')
    if plan['source_sha256']!=report['source_sha256']:raise ValueError('Source bindings differ')
    deferred={x['id'] for x in report['deferred']};rows={e['id']:e for e in plan['entries']}
    if len(rows)!=len(plan['entries']) or not deferred.issubset(rows):raise ValueError('Invalid record IDs')
    tokenizer=tokens
    from reinsertion import B15_POLICY,NUMERIC1_POLICY,NUMERIC15_POLICY
    if plan.get('policy')==NUMERIC15_POLICY:
        from control_numeric15 import tokenize as tokenizer
    elif plan.get('policy')==NUMERIC1_POLICY:
        from control_numeric1 import tokenize as tokenizer
    elif plan.get('policy')==B15_POLICY:
        from control_b15 import tokenize as tokenizer
    groups=defaultdict(list);families=defaultdict(set);native=[]
    for key in sorted(deferred):
        e=rows[key];opaque=set();native_pairs=Counter()
        for s in e['segments']:
            raw=bytes.fromhex(s['source_hex']);parts,_=tokenizer(raw)
            opaque.update(bytes.fromhex(t['hex']).decode('ascii') for t in parts if t['kind']=='opaque-percent')
            _,spans=native_text(raw)
            native_pairs.update(s['hex'] for s in spans)
        if opaque:
            groups[tuple(sorted(opaque))].append(key)
            for token in opaque:families[token].add(key)
        if native_pairs:native.append({'id':key,'native_sequences':dict(sorted(native_pairs.items()))})
    from audit_translation_coverage import audit
    from translation_policy import POLICY_PATH
    coverage,classified=audit(plan,report,json.loads(POLICY_PATH.read_text(encoding='utf-8')))
    review=[r['entry'] for r in classified if r['class']=='review_unchanged']
    combos={tuple(s['source_hex'] for s in e['segments'] if s['editable']) for e in review}
    assert sum(map(len,groups.values()))==coverage['deferred_by_reason'].get('Controle opaco: edição bloqueada',0)
    assert len(deferred)==coverage['classes']['deferred']
    assert len(native)==coverage['deferred_by_reason'].get('Origem com bytes nativos: preservação permitida, edição bloqueada',0)
    return {'schema':1,'source':'compiled text plan; read-only planning, not edit approval',
        'plan_sha256':hashlib.sha256(plan_raw).hexdigest(),'coverage':coverage['classes'],
        'opaque_records':sum(map(len,groups.values())), 'opaque_group_count':len(groups),
        'disjoint_opaque_groups':[{'parser_spans':list(k),'records':len(v),'example_ids':v[:3]} for k,v in sorted(groups.items(),key=lambda p:(-len(p[1]),p[0]))],
        'overlapping_syntax_counts':[{'syntax':k,'records':len(v),'exclusive_records':len(groups.get((k,),[]))} for k,v in sorted(families.items(),key=lambda p:(-len(p[1]),p[0]))],
        'native_records':native,'review_records':len(review),'review_distinct_source_combinations':len(combos),
        'editing_enabled':False,'limitations':['Parser spans are not complete command grammar','Categories do not establish runtime semantics','Native bytes do not imply Portuguese glyph slots']}


def main():
    parser=argparse.ArgumentParser(description='Planejar pendências com metadados locais')
    from build_translation_pilot import DEFAULT_DRAFT
    parser.add_argument('--build-dir',type=Path,default=ROOT/'work'/DEFAULT_DRAFT.stem)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args();folder=local(args.build_dir);output=args.output.resolve()
    if output.exists() or not any(output.is_relative_to(ROOT/d) for d in ('reports','work')):raise ValueError('Use new report under reports/ or work/')
    result=inventory(folder);output.parent.mkdir(parents=True,exist_ok=True)
    output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(f"{result['opaque_records']} opacos em {result['opaque_group_count']} grupos; {len(result['native_records'])} nativos; {result['review_records']} a revisar / {result['review_distinct_source_combinations']} combinações distintas")
    for group in result['disjoint_opaque_groups'][:8]:print(group['records'],group['parser_spans'])

if __name__=='__main__':main()
