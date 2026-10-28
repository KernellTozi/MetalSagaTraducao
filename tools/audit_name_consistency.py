"""Offline concordance of item origins/previous labels against runtime texts.

Findings require contextual decisions. Never replaces text or writes a recipe.
Full game text stays under work/.
"""
import argparse,collections,json,re
from pathlib import Path
from reinsertion import ROOT,local
from dialogue import sha
from item_names import catalog,original,RESOURCE
from item_name_user_review import load_manifest
from build_translation_pilot import load_draft

def normalize(text):
    return re.sub(r'\s+',' ',re.sub(r'<[^>]*>',' ',text).replace('|',' ')).strip()

def fields(recipe):
    result=[]
    def walk(value,path):
        if isinstance(value,dict):
            for key,child in value.items():
                if key=='translation' and isinstance(child,str):
                    result.append({'field':path,'id':value.get('id',path),'text':child,'text_sha256':sha(child.encode('utf-8'))})
                elif key not in ('item_names','item_name_review','description_review'):
                    walk(child,path+'.'+key)
        elif isinstance(value,list):
            for i,child in enumerate(value):walk(child,path+'['+str(i)+']')
    walk(recipe,'interface')
    draft,_=load_draft(ROOT/recipe['base_dialogue_draft'])
    targets=dict(draft['translations']);todo=dict(draft.get('aliases',{}))
    while todo:
        ready=[k for k,parent in todo.items() if parent in targets]
        if not ready:raise ValueError('Unresolved narrative alias')
        for key in ready:targets[key]=targets[todo.pop(key)]
    for key,value in targets.items():
        if key in draft.get('deferred',{}):continue
        for segment,text in (value.items() if isinstance(value,dict) else [('',value)]):
            field=key+('.'+segment if segment else '')
            result.append({'field':field,'id':key,'text':text,'text_sha256':sha(text.encode('utf-8'))})
    return result

def terms(recipe):
    raw=original(RESOURCE)
    if sha(raw)!=recipe['item_names']['source_sha256']:raise ValueError('Name source differs')
    rows={r['id']:r for r in catalog(raw)};applied={r['id']:r['translation'] for r in recipe['item_names']['entries']}
    table=collections.defaultdict(dict)
    def add(text,key,kind):
        target=applied.get(key)
        if not target or normalize(text).casefold()==normalize(target).casefold():return
        if len(text)<4:return
        table[text][(key,kind)]={'item_id':key,'canonical':target,'kind':kind}
    for key,text in applied.items():add(bytes.fromhex(rows[key]['source_hex']).decode('ascii'),key,'original-english')
    m=load_manifest(recipe['item_names']['user_review'])
    for r in m['approved']:add(r['audited_translation'],r['id'],'previous-translation')
    if 'approved_extension' in recipe['item_names']:
        from item_name_approved_batch import load
        _,parent=load(recipe['item_names']['approved_extension'])
        before={r['id']:r['translation'] for r in parent['item_names']['entries']}
        for key,target in applied.items():
            if key in before:add(before[key],key,'previous-translation')
    return {text:list(decisions.values()) for text,decisions in sorted(table.items())}

def scan(recipe):
    labels=terms(recipe);texts=fields(recipe);matches=[]
    patterns=[(term,choices,re.compile(r'(?<!\w)'+re.escape(normalize(term))+r'(?!\w)',re.I),
        [re.compile(re.escape(normalize(c['canonical'])),re.I) for c in choices]) for term,choices in labels.items()]
    for field in texts:
        text=normalize(field['text'])
        for term,choices,pattern,canonical_patterns in patterns:
            spans=list(pattern.finditer(text))
            if not spans:continue
            canonical_spans=[m.span() for p in canonical_patterns for m in p.finditer(text)]
            overlap=all(any(a<=m.start() and m.end()<=b for a,b in canonical_spans) for m in spans)
            matches.append({**field,'matched_term':term,'candidates':choices,
                'inside_canonical_name':overlap,'auto_edit_allowed':False})
    return {'schema':1,'fields_scanned':len(texts),'terms_scanned':len(labels),'name_fields':len(recipe['item_names']['entries']),
        'matches':matches,'possible_references':len(matches),'limits':'Literal/HTML-whitespace concordance only, no semantic identity proof. Canonical overlaps and ordinary nouns may be correct; no global replacement.'}

def signature(row):
    return (row['field'],sha(row['matched_term'].encode('utf-8')),row['text_sha256'])

def reviewed_findings(result,recipe_sha,decisions_path):
    decisions_path=decisions_path.resolve()
    if not decisions_path.is_relative_to(ROOT/'translations'):raise ValueError('Decisions outside translations')
    document=json.loads(decisions_path.read_text(encoding='utf-8'))
    if document.get('policy')!='context-classified-name-concordance-v001' or document['output_recipe_sha256']!=recipe_sha:
        raise ValueError('Decisions do not bind this exact recipe')
    decisions={(r['field'],r['term_sha256'],r['text_sha256']):r for r in document['decisions']}
    if len(decisions)!=len(document['decisions']):raise ValueError('Duplicate name consistency decision')
    unresolved=[]
    for row in result['matches']:
        decision=decisions.get(signature(row))
        if not decision or decision['action']!='preserve':unresolved.append(row['field'])
        else:row['reviewed_classification']=decision['reason']
    return {'preserved_reviewed_matches':len(result['matches'])-len(unresolved),'unresolved_matches':unresolved}

def run(recipe_path,output,decisions_path=None):
    recipe_path=recipe_path.resolve();output=local(output,True)
    if not recipe_path.is_relative_to(ROOT/'translations'):raise ValueError('Recipe outside translations')
    result=scan(json.loads(recipe_path.read_text(encoding='utf-8')))
    result.update(recipe=recipe_path.relative_to(ROOT).as_posix(),recipe_sha256=sha(recipe_path.read_bytes()),iso_modified=False)
    if decisions_path is not None:result['review']=reviewed_findings(result,result['recipe_sha256'],decisions_path)
    output.parent.mkdir(parents=True,exist_ok=True);output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    return {k:result[k] for k in ('fields_scanned','terms_scanned','name_fields','possible_references','iso_modified','review') if k in result}

if __name__=='__main__':
    p=argparse.ArgumentParser(description='Conferir nomes em textos locais, sem substituir ou acessar APIs')
    p.add_argument('--recipe',type=Path,default=ROOT/'translations/interface-v044.json')
    p.add_argument('--decisions',type=Path)
    p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    print(json.dumps(run(a.recipe,a.output,a.decisions),ensure_ascii=False))
