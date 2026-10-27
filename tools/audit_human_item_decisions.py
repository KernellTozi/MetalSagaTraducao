"""Read-only reconciliation of the human Markdown with the reviewed recipe.

Writes private diffs and possible stale literal references, never substitutes
text globally. Human file and game texts stay under work/ only.
"""
import argparse,collections,json,re
from pathlib import Path
from reinsertion import ROOT,local
from dialogue import sha
from gfi import encode
from item_names import catalog,original,RESOURCE
from item_name_user_review import load_manifest
from build_translation_pilot import load_draft


def parse(text):
    section='';tables=collections.defaultdict(list);protected={}
    for line in text.splitlines():
        if line.startswith('## '):section=line[3:].split(' — ')[0]
        elif line.startswith('|'):
            cells=[c.strip().replace('**','') for c in line.strip().strip('|').split('|')]
            if cells[0].isdigit():tables[section].append(cells)
            elif section=='C' and re.fullmatch(r'\d+(?:,\s*\d+)*',cells[0]):
                ids=[int(x.strip()) for x in cells[0].split(',')];names=re.findall(r'`([^`]+)`',cells[1])
                if len(ids)!=len(names):raise ValueError('Protected human name table column mismatch')
                protected.update(zip(ids,names))
    if {s:len(tables[s]) for s in ('A','B','D','E')}!={'A':72,'B':16,'D':35,'E':134}:
        raise ValueError('Human decision table counts differ')
    if len({int(r[0]) for r in tables['A']})!=72 or len(protected)!=18:
        raise ValueError('Human decision IDs duplicate or protected table incomplete')
    return dict(tables),protected


def current_names(recipe,rows):
    applied={r['id']:r['translation'] for r in recipe['item_names']['entries']}
    return {r['id']:applied.get(r['id'],bytes.fromhex(r['source_hex']).decode('ascii')) for r in rows}


def concordance(recipe,manifest):
    old_names=collections.defaultdict(list)
    for row in manifest['approved']:
        old_names[row['audited_translation']].append({'id':row['id'],'new':row['translation']})
    fields=[]
    def walk(value,path):
        if isinstance(value,dict):
            for key,child in value.items():
                if key=='translation' and isinstance(child,str):fields.append((path,child))
                elif key not in ('item_names','item_name_review'):walk(child,path+'.'+key)
        elif isinstance(value,list):
            for i,child in enumerate(value):walk(child,path+'['+str(i)+']')
    walk(recipe,'interface')
    draft,_=load_draft(ROOT/recipe['base_dialogue_draft']);targets=dict(draft['translations']);todo=dict(draft.get('aliases',{}))
    while todo:
        ready=[k for k,parent in todo.items() if parent in targets]
        if not ready:raise ValueError('Unresolved alias while auditing literal references')
        for k in ready:targets[k]=targets[todo.pop(k)]
    for key,value in targets.items():
        if key in draft.get('deferred',{}):continue
        if isinstance(value,str):fields.append((key,value))
        else:fields.extend((key+'.'+segment,text) for segment,text in value.items())
    matches=[]
    for path,text in fields:
        normalized=re.sub(r'\s+',' ',text.replace('|',' '))
        for old,decisions in old_names.items():
            pattern=r'(?<!\w)'+re.escape(old)+r'(?!\w)'
            if len(old)<4 or not re.search(pattern,normalized,re.I):continue
            matches.append({'field':path,'previous_wording':old,'candidate_decisions':decisions,
                'current_text':text,'classification':'possible-literal-reference-needs-context',
                'auto_edit_allowed':False})
    return {'fields_scanned':len(fields),'possible_references':len(matches),
        'limits':'Literal matching only. Ordinary words, dialogue and the still-preserved item 142 may legitimately keep old wording; not a list of proven errors.',
        'matches':matches}


def run(source,recipe_path,output):
    source=local(source);output=local(output,True);recipe_path=Path(recipe_path).resolve()
    if not recipe_path.is_relative_to(ROOT/'translations'):raise ValueError('Review recipe outside translations')
    recipe=json.loads(recipe_path.read_text(encoding='utf-8'));m=load_manifest(recipe['item_names']['user_review'])
    document=source.read_bytes()
    if sha(document)!=m['source_document_sha256']:raise ValueError('Human source document changed')
    tables,protected=parse(document.decode('utf-8-sig'));rows=catalog(original(RESOURCE));byindex={r['index']:r for r in rows}
    parent=json.loads((ROOT/m['parent_recipe']).read_text(encoding='utf-8'))
    before=current_names(parent,rows);after=current_names(recipe,rows);approved={r['id']:r for r in m['approved']}
    conflicts=[];changes=[]
    for cells in tables['A']:
        i=int(cells[0]);row=byindex[i];key=row['id'];target=approved[key]
        if bytes.fromhex(row['source_hex']).decode('ascii')!=cells[1] or target['audited_translation']!=cells[2] or target['translation']!=cells[3] or after[key]!=cells[3]:
            conflicts.append(key);continue
        changes.append({'id':key,'original':cells[1],'audited':cells[2],'before_applied':before[key],'after':after[key],'bytes':len(encode(after[key]))})
    changed={key for key in before if before[key]!=after[key]}
    if changed!=set(approved):raise ValueError('Item fields outside human section A changed')
    for section in ('B','D','E'):
        for cells in tables[section]:
            row=byindex[int(cells[0])];key=row['id']
            if bytes.fromhex(row['source_hex']).decode('ascii')!=cells[1] or before[key]!=after[key]:conflicts.append(key)
            if section in ('D','E') and after[key]!=cells[2]:conflicts.append(key)
    for i,name in protected.items():
        row=byindex[i]
        if before[row['id']]!=name or after[row['id']]!=name:conflicts.append(row['id'])
    if after['item.name.0861']!='Sentidos finos':conflicts.append('item.name.0861')
    findings=concordance(recipe,m)
    summary={'schema':1,'source_document_sha256':sha(document),'candidate_recipe':recipe_path.relative_to(ROOT).as_posix(),
        'candidate_changed_ids':len(changes),'ratified_unchanged_ids':35,'additional_unchanged_ids':134,
        'protected_names_checked':len(protected),'blocked_choices':16,'unconfirmed_alternatives':1,
        'conflicts':sorted(set(conflicts)),'all_other_item_fields_unchanged':True,
        'possible_literal_references':findings['possible_references'],'texts_auto_replaced':False,
        'iso_modified':False,'pcsx2_executed':False}
    if conflicts:raise ValueError('Human input conflicts: '+repr(sorted(set(conflicts))))
    output.mkdir(parents=True)
    lines=['# Revisão humana — diff dos nomes','',
        '72 IDs revisados; 35 escolhas ratificadas sem alteração; zero conflitos; 16 bloqueadas e uma alternativa não confirmada preservadas.','',
        '| ID | Original | Antes no jogo | Novo nome | Bytes |','| --- | --- | --- | --- | ---: |']
    for r in changes:lines.append('| '+' | '.join(str(v) for v in (int(r['id'].split('.')[-1]),r['original'],r['before_applied'],r['after'],r['bytes']))+' |')
    lines+=['','## Escolhas bloqueadas — não aplicadas','','| ID | Nome desejado | Bytes | Impedimento |','| --- | --- | ---: | --- |']
    for r in m['blocked']:lines.append('| '+' | '.join(str(v) for v in (int(r['id'].split('.')[-1]),r['desired_not_applied'],r['encoded_bytes'] if r['encoded_bytes'] is not None else '—',r['reason']))+' |')
    lines+=['','ID 861 continua Sentidos finos; Hipersentidos não foi confirmado.','',
        'Os 30 rótulos de batalha correspondentes foram sincronizados por nome de origem/ID explícito, sem mudar descrições, atributos ou efeitos.','',
        'Sucatas leve/média/pesada (822–824) e Detector básico (710) seguem escolhas provisórias do usuário; pesos/alcances precisam de confirmação jogando.','',
        'Concordância literal está em concordancia.json. São candidatos para leitura contextual, não erros comprovados e não receberam substituições automáticas.']
    (output/'diff-nomes.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    (output/'concordancia.json').write_text(json.dumps(findings,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    (output/'resumo.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    return summary


if __name__=='__main__':
    p=argparse.ArgumentParser(description='Conferir decisões humanas e referências textuais, sem aplicar substituições')
    p.add_argument('--input',type=Path,default=ROOT/'work/revisao-humana-itens-v001/decisoes-originais.md')
    p.add_argument('--recipe',type=Path,default=ROOT/'translations/interface-v042.json')
    p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    print(json.dumps(run(a.input,a.recipe,a.output),ensure_ascii=False,indent=2))
