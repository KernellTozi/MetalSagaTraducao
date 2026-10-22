"""Read-only local coverage triage; suggestions never approve translation edits."""
import argparse
from datetime import datetime
from build_translation_pilot import DEFAULT_DRAFT
from collections import Counter
import hashlib
import json
from pathlib import Path
import re
from dialogue_formats import tokens
from gfi import decode
from reinsertion import ROOT,local
from translation_policy import POLICY_PATH

CLASSES=('modified','deferred','controls_or_punctuation','name_or_expression_candidate','review_unchanged')


def visible(segment,tokenizer=tokens):
    raw=bytearray.fromhex(segment['source_hex'])
    controls,opaque=tokenizer(raw)
    if opaque:raise ValueError('Opaque controls require explicit deferral')
    for token in controls:
        at=token['relative_offset'];size=len(bytes.fromhex(token['hex']))
        raw[at:at+size]=b' '*size
    return re.sub(r'\s+',' ',decode(bytes(raw))).strip()


def classify(entry,deferred,policy,tokenizer=tokens):
    if entry['id'] in deferred:return 'deferred'
    if any(s['source']!=s['translation'] for s in entry['segments']):return 'modified'
    parts=[visible(s,tokenizer) for s in entry['segments'] if s['editable']]
    if not parts: return 'review_unchanged'
    if not any(any(c.isalpha() for c in p) for p in parts):return 'controls_or_punctuation'
    sensitive=set(policy.get('case_sensitive_names',[]))
    names=policy['protected_names']+policy['protected_terms']+policy['preserve_expressions']
    def recognized(text):
        text=text.strip(' -.!?,:;*"\'()[]')
        if not text or not any(c.isalpha() for c in text):return True
        return any(text==n if n in sensitive else text.casefold()==n.casefold() for n in names)
    if all(recognized(p) for p in parts):return 'name_or_expression_candidate'
    return 'review_unchanged'


def audit(document,report,policy):
    if not report.get('valid') or report.get('refused')!=0:raise ValueError('Use a valid compiled lot')
    if document['source_sha256']!=report['source_sha256']:raise ValueError('Source hash mismatch')
    tokenizer=tokens
    from reinsertion import B15_POLICY,NUMERIC1_POLICY,NUMERIC15_POLICY
    if document.get('policy')==NUMERIC15_POLICY:
        from control_numeric15 import tokenize as tokenizer
    elif document.get('policy')==NUMERIC1_POLICY:
        from control_numeric1 import tokenize as tokenizer
    elif document.get('policy')==B15_POLICY:
        from control_b15 import tokenize as tokenizer
    entries=document['entries'];ids=[e['id'] for e in entries]
    if len(ids)!=len(set(ids)):raise ValueError('Duplicate record ID')
    deferred={e['id'] for e in report['deferred']}
    if len(deferred)!=len(report['deferred']) or not deferred.issubset(ids):raise ValueError('Invalid deferral IDs')
    counts=Counter({c:0 for c in CLASSES});rows=[]
    by_tag=Counter();by_reason=Counter();syntax=Counter();syntax_records={}
    for e in entries:
        status=classify(e,deferred,policy,tokenizer);counts[status]+=1
        rows.append({'class':status,'entry':e})
        if status=='deferred':
            parts=e['id'].split('.')
            by_tag[parts[1] if len(parts)>1 else 'unknown']+=1
            by_reason.update(e.get('blocked_reasons',[]))
            for segment in e['segments']:
                controls,_=tokenizer(bytes.fromhex(segment['source_hex']))
                for token in controls:
                    if token['kind']!='opaque-percent':continue
                    text=bytes.fromhex(token['hex']).decode('ascii')
                    syntax[text]+=1
                    syntax_records.setdefault(text,set()).add(e['id'])
    if counts['modified']!=report['accepted'] or len(ids)-counts['modified']!=report['unchanged']:
        raise ValueError('Compiled counts mismatch')
    return {'schema':1,'records':len(ids),'source_sha256':document['source_sha256'],
            'classes':dict(counts),'automatic_edit_approval':False,
            'deferred_by_tag':dict(sorted(by_tag.items())),
            'deferred_by_reason':dict(sorted(by_reason.items())),
            'opaque_parser_spans':[{'syntax':text,'occurrences':count,
                                    'records':len(syntax_records[text])}
                                   for text,count in sorted(syntax.items(),key=lambda x:(-x[1],x[0]))],
            'opaque_span_limit':'Parser spans are not proof of complete command grammar or semantics',
            'pcsx2_validation':False,'classification':'conservative triage; names/expressions are suggestions'},rows


def main():
    parser=argparse.ArgumentParser(description='Auditar cobertura local sem IA ou alteração binária')
    parser.add_argument('--build-dir',type=Path,default=ROOT/'work'/DEFAULT_DRAFT.stem)
    parser.add_argument('--output',type=Path,default=ROOT/'work/auditorias'/f'{datetime.now():%Y%m%d-%H%M%S-%f}')
    args=parser.parse_args();folder=local(args.build_dir);output=local(args.output,True)
    plan_raw=(folder/'plano.json').read_bytes();report_raw=(folder/'relatorio.json').read_bytes()
    policy_raw=POLICY_PATH.read_bytes()
    summary,rows=audit(json.loads(plan_raw),json.loads(report_raw),json.loads(policy_raw))
    summary.update({'plan_sha256':hashlib.sha256(plan_raw).hexdigest(),
                    'report_sha256':hashlib.sha256(report_raw).hexdigest(),
                    'policy_sha256':hashlib.sha256(policy_raw).hexdigest()})
    output.mkdir(parents=True)
    (output/'resumo.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    for status in CLASSES:
        if status=='modified':continue
        with (output/(status+'.jsonl')).open('x',encoding='utf-8') as stream:
            for row in rows:
                if row['class']==status:stream.write(json.dumps(row,ensure_ascii=False)+'\n')
    print(json.dumps(summary['classes'],ensure_ascii=False));print(output)


if __name__=='__main__':main()
