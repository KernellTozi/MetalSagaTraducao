"""Prepare reviewed Unicode proposals locally; never translate, call AI or edit binaries."""
import argparse,copy,json,functools,re
from pathlib import Path
from item_descriptions import catalog,original,RESOURCE,validate_value,sha
from reinsertion import ROOT,local

def wrap_words(text,source):
    if '|' in text:return text
    words=text.split();lines=source.count('|')+1;width=max(map(len,source.split('|')))
    @functools.lru_cache(None)
    def solve(start,left):
        if not left:return (0,[]) if start==len(words) else None
        best=None
        for stop in range(start+1,len(words)+1):
            line=' '.join(words[start:stop])
            if len(line)>width:break
            tail=solve(stop,left-1)
            if tail:
                candidate=(tail[0]+(width-len(line))**2,[line]+tail[1])
                if best is None or candidate[0]<best[0]:best=candidate
        return best
    result=solve(0,lines)
    if not result:raise ValueError('No safe word-boundary wrapping under source line budget')
    return '|'.join(result[1])

def prepare(parent,proposals,version,*,resume_deferred=False):
    if not re.fullmatch(r'interface-v\d{3}',version):raise ValueError('Invalid interface version')
    raw=original(RESOURCE);rows=catalog(raw);known={r['id']:r for r in rows}
    draft=copy.deepcopy(parent);config=draft['item_descriptions'];review=draft['description_review']
    existing={r['id'] for r in config['entries']};pending={r['id']:r for r in review['pending']}
    preserved={r['id']:r for r in review.get('preserved',[])}
    used=existing|set(pending)|set(preserved)
    allowed=set(pending) if resume_deferred else set()
    if (not isinstance(proposals,dict) or not proposals or any(not isinstance(t,str) or not t.strip() for t in proposals.values())
        or set(proposals)&(used-allowed) or set(proposals)-known.keys()):raise ValueError('Unknown or already reviewed proposal ID / invalid text')
    if len(used)!=review['reviewed']:raise ValueError('Parent review accounting mismatch')
    from item_descriptions import validate_names
    for key,text in proposals.items():
        row=known[key];before=bytes.fromhex(row['source_hex']);source=before.decode('ascii')
        if key in pending:
            if pending[key]['source_sha256']!=row['source_sha256']:raise ValueError('Deferred proposal source binding mismatch')
            del pending[key]
        if text==source:
            preserved[key]={'id':key,'source_sha256':row['source_sha256'],'reason':'Reviewed; original marker or term intentionally retained'}
            continue
        reason=None;kind=None;target=text
        if row['native'] or b'%' in before:reason='Original profile blocks native bytes or percent syntax';kind='technical-control'
        else:
            try:
                validate_names(source,text)
                target=wrap_words(text,source);validate_value(before,target)
            except ValueError as exc:
                reason=str(exc)
                kind='technical-glyph' if 'glyph' in reason.lower() else ('terminology' if 'reference missing' in reason else 'space-or-policy')
        if reason:
            pending[key]={'id':key,'source_sha256':row['source_sha256'],'reason':reason,'kind':kind,'proposed':text}
        else:
            config['entries'].append({'id':key,'source_sha256':row['source_sha256'],'item_records':row['items'],'translation':target})
    config['name_reference_policy']='item-description-unique-name-references-v002'
    order={r['id']:i for i,r in enumerate(rows)};config['entries'].sort(key=lambda r:order[r['id']])
    reviewed=len(config['entries'])+len(pending)+len(preserved)
    draft['description_review']={'policy':'item-review-ledger-v002','reviewed':reviewed,'accepted':len(config['entries']),
        'pending':sorted(pending.values(),key=lambda r:order[r['id']]),
        'preserved':sorted(preserved.values(),key=lambda r:order[r['id']]),'not_reviewed':len(rows)-reviewed}
    draft['status']='Broad item descriptions, original slots and names preserved; visual verification pending'
    draft['iso_name']=f'MetalSaga-ptbr-{version}.iso'
    return draft

def validate_review(review,config,rows):
    if 'policy' not in review:return # Historical v017 remains reproducible.
    if review['policy']!='item-review-ledger-v002':raise ValueError('Unknown item review ledger')
    known={r['id']:r for r in rows};accepted=[r['id'] for r in config['entries']]
    deferred=[r['id'] for r in review['pending']];preserved=[r['id'] for r in review.get('preserved',[])]
    used=accepted+deferred+preserved
    if (len(used)!=len(set(used)) or set(used)-known.keys() or review['accepted']!=len(accepted)
        or review['reviewed']!=len(used) or review['not_reviewed']!=len(known)-len(used)):
        raise ValueError('Item review class/count mismatch')
    for row in review['pending']+review.get('preserved',[]):
        if row['source_sha256']!=known[row['id']]['source_sha256']:raise ValueError('Item review source binding mismatch')

if __name__=='__main__':
    p=argparse.ArgumentParser(description='Prepare explicit reviewed item proposals without APIs or game changes')
    p.add_argument('--parent',type=Path,required=True);p.add_argument('--proposals',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True);p.add_argument('--version',required=True)
    p.add_argument('--resume-deferred',action='store_true',help='Explicitly permit selected deferred IDs; never overwrite accepted fields');a=p.parse_args()
    parent=a.parent.resolve();proposals=local(a.proposals);output=a.output.resolve()
    if not parent.is_relative_to(ROOT/'translations') or not output.is_relative_to(ROOT/'translations') or output.exists():
        raise ValueError('Use an existing translations parent and a new translations output')
    def unique(pairs):
        out={}
        for k,v in pairs:
            if k in out:raise ValueError('Duplicate proposal key')
            out[k]=v
        return out
    draft=prepare(json.loads(parent.read_text(encoding='utf-8')),json.loads(proposals.read_text(encoding='utf-8-sig'),object_pairs_hook=unique),a.version,resume_deferred=a.resume_deferred)
    output.write_text(json.dumps(draft,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    r=draft['description_review'];print(json.dumps({k:r[k] for k in ('reviewed','accepted','not_reviewed')}))
    print('Pending:',len(r['pending']),'Preserved:',len(r['preserved']))
