"""Exact opt-in continuation of the v042 human review, with one glyph fallback."""
import copy,json
from reinsertion import ROOT
from dialogue import sha
from gfi import encode,CHAR_TO_BYTES

POLICY='item-approved-continuation-fixed-names-v001'
APPROVED={103:'Óculos',109:'Máscara hóquei',112:'Turbante aramida',
          118:'Orelha de coelho',130:'Casaco polímero',178:'Placas polímero',
          342:'Kit de reparo',425:'Orelha de coelho',861:'Superpercepção'}

def selected(index):
    text=APPROVED[index]
    missing={c for c in text if not 32<=ord(c)<=126 and c not in CHAR_TO_BYTES}
    if missing:
        if index!=103 or missing!={'Ó'}:raise ValueError('Unapproved glyph fallback')
        text='Oculos'
    if len(encode(text))>16:raise ValueError('Approved name exceeds unchanged 16-byte ceiling')
    return text

def load(binding):
    if set(binding)!={'recipe','sha256'}:raise ValueError('Unknown approved batch binding')
    path=(ROOT/binding['recipe']).resolve()
    if not path.is_relative_to(ROOT/'translations'):raise ValueError('Approved batch outside translations')
    raw=path.read_bytes()
    if sha(raw)!=binding['sha256']:raise ValueError('Approved batch hash differs')
    m=json.loads(raw)
    if m.get('policy')!=POLICY or m.get('schema')!=1:raise ValueError('Unknown approved batch policy')
    if m.get('parent_recipe')!='translations/interface-v042.json':raise ValueError('Approved batch parent differs')
    parent_raw=(ROOT/m['parent_recipe']).read_bytes()
    if sha(parent_raw)!=m['parent_recipe_sha256']:raise ValueError('Approved batch parent hash differs')
    return m,json.loads(parent_raw)

def prepare(parent,m,rows,binding):
    from item_name_user_review import validate_config
    validate_config(parent['item_names'],rows)
    byid={r['id']:r for r in rows};expected=copy.deepcopy(parent['item_names'])
    entries={r['id']:r for r in expected['entries']}
    if [r['index'] for r in m['approved']]!=list(APPROVED):raise ValueError('Approved batch ID scope differs')
    for t in m['approved']:
        row=byid[t['id']];idx=row['index']
        if idx!=t['index'] or t['translation']!=selected(idx):raise ValueError('Approved batch wording differs')
        if any(t[k]!=row[k] for k in ('source_sha256','record_sha256')):raise ValueError('Approved batch source differs')
        old=entries.get(row['id']);effective=encode(old['translation']) if old else bytes.fromhex(row['source_hex'])
        if sha(effective)!=t['parent_effective_name_sha256']:raise ValueError('Approved batch old name differs')
        if idx==861:
            if bytes.fromhex(row['source_hex'])!=b'Keen Senses':raise ValueError('Perception skill identity differs')
            from item_descriptions import catalog,original,RESOURCE
            matches=[d for d in catalog(original(RESOURCE)) if any(i['id']==861 for i in d['items'])]
            if len(matches)!=1 or matches[0]['source_sha256']!=m['perception_description_sha256']:
                raise ValueError('Perception skill description binding differs')
        if old:old['translation']=t['translation']
        else:
            if t['id'] not in {r['id'] for r in parent['item_name_review']['pending']}:
                raise ValueError('Approved batch name was not pending')
            expected['entries'].append({'id':row['id'],'source_sha256':row['source_sha256'],
                'record_sha256':row['record_sha256'],'translation':t['translation'],
                'group':'consumables-materials' if idx==342 else 'generic-equipment'})
    expected['approved_extension']=binding
    return expected

def validate(config,rows):
    m,parent=load(config['approved_extension'])
    if config!=prepare(parent,m,rows,config['approved_extension']):
        raise ValueError('Non-authorized name/config change in approved continuation')
    return parent['item_names']

def repair_exception(row,text):
    return row['index']==342 and bytes.fromhex(row['source_hex'])==b'Repair Kit' and text=='Kit de reparo'
