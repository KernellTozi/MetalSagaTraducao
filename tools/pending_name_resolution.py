"""Exact fourteen-name continuation requested by the user; unchanged ceilings."""
import copy,json
from reinsertion import ROOT
from dialogue import sha
from gfi import encode

POLICY='pending-generic-names-exact-fourteen-fixed-slots-v001'
NAMES={625:'Presa',631:'Presa grande',635:'Peça cilíndr.',650:'Lâm. de espada',
       695:'Placa de ônibus',701:'Sucata cibern.',741:'Jarro de porcel.',
       753:'Guaxinim',762:'Máq. de vendas',765:'Roupeiro orient.',
       768:'Geladeira comum',781:'Vest. garçonete',786:'Mira infraverm.',1037:'Cinturão'}
FRIDGE='Geladeira compacta|de uma porta.'
BUS_IDS=('map.msg.0e551d94','map.msgn.0e76fcc4','map.smsg.06493b00','map.smsg.0e5517d4')

def load(binding):
    if set(binding)!={'recipe','sha256'}:raise ValueError('Unknown pending-name binding')
    path=(ROOT/binding['recipe']).resolve()
    if not path.is_relative_to(ROOT/'translations'):raise ValueError('Pending-name manifest outside translations')
    raw=path.read_bytes()
    if sha(raw)!=binding['sha256']:raise ValueError('Pending-name manifest changed')
    m=json.loads(raw)
    if m.get('schema')!=1 or m.get('policy')!=POLICY or m.get('parent_recipe')!='translations/interface-v044.json':
        raise ValueError('Pending-name parent/policy differs')
    raw=(ROOT/m['parent_recipe']).read_bytes()
    if sha(raw)!=m['parent_recipe_sha256']:raise ValueError('Pending-name parent changed')
    if [(r['index'],r['translation']) for r in m['approved']]!=list(NAMES.items()):
        raise ValueError('Pending-name exact scope/wording differs')
    if tuple(r['id'] for r in m['bus_stop_references'])!=BUS_IDS:raise ValueError('Bus Stop Sign exact reference scope differs')
    return m,json.loads(raw)

def expected_names(binding,rows):
    from item_name_user_review import validate_config
    m,parent=load(binding);validate_config(parent['item_names'],rows)
    expected=copy.deepcopy(parent['item_names']);byid={r['id']:r for r in rows}
    pending={r['id'] for r in parent['item_name_review']['pending']}
    if pending!={r['id'] for r in m['approved']}:raise ValueError('Pending-name parent selection differs')
    for target in m['approved']:
        row=byid[target['id']]
        if row['index']!=target['index'] or any(row[k]!=target[k] for k in ('source_sha256','record_sha256')):
            raise ValueError('Pending-name record binding differs')
        value=encode(target['translation'])
        if not 1<=len(value)<=16:raise ValueError('Pending-name ceiling exceeded')
        if target['encoded_hex']!=value.hex() or target['encoded_bytes']!=len(value):
            raise ValueError('Pending-name codec binding differs')
        group='generic-equipment' if row['index'] in (781,786) else 'consumables-materials' if row['index']<710 else 'furniture-accessories' if row['index']<800 else 'generic-key-items'
        expected['entries'].append({'id':row['id'],'source_sha256':row['source_sha256'],
            'record_sha256':row['record_sha256'],'translation':target['translation'],'group':group})
    expected['pending_resolution']=binding
    return expected

def validate_names(config,rows):
    binding=config['pending_resolution'];_,parent=load(binding)
    if config!=expected_names(binding,rows):raise ValueError('Non-authorized pending-name/config change')
    return parent['item_names']

def expected_descriptions(binding):
    m,parent=load(binding);expected=copy.deepcopy(parent['item_descriptions']);change=m['fridge_description']
    row=next(r for r in expected['entries'] if r['id']==change['id'])
    if (row['source_sha256']!=change['source_sha256'] or row['item_records']!=change['item_records']
        or len(row['item_records'])!=1 or row['item_records'][0]['id']!=768
        or sha(row['translation'].encode('utf-8'))!=change['parent_text_sha256']
        or change['translation']!=FRIDGE):raise ValueError('One-door fridge description identity differs')
    row['translation']=FRIDGE;expected['pending_name_resolution']=binding
    return expected

def validate_descriptions(config):
    binding=config['pending_name_resolution'];m,parent=load(binding)
    if config!=expected_descriptions(binding):raise ValueError('Non-authorized pending description change')
    return parent['item_descriptions'],{m['fridge_description']['id']}

def expected_interface(binding):
    from item_names import catalog,original,RESOURCE
    m,parent=load(binding);expected=copy.deepcopy(parent)
    expected['item_names']=expected_names(binding,catalog(original(RESOURCE)))
    expected['item_name_review']['pending']=[];expected['item_name_review']['accepted']=len(expected['item_names']['entries'])
    expected['item_descriptions']=expected_descriptions(binding)
    expected.update(pending_name_resolution=binding,base_dialogue_draft='translations/regiao-inicial-v040.json',
                    iso_name='MetalSaga-ptbr-interface-v045.iso',
                    status='Quatorze nomes genéricos restantes resolvidos; abreviações explícitas, teto de 16 bytes e acentos preservados.')
    return expected

def validate_interface(recipe):
    if 'interface_gap_review' in recipe:
        from interface_gaps import validate_interface as validate_gaps
        return validate_gaps(recipe)
    if recipe!=expected_interface(recipe['pending_name_resolution']):raise ValueError('Non-authorized interface change in pending resolution')

def term_exception(row,text):
    expected={625:(b'Fang','Presa','Fang'),631:(b'Large Fang','Presa grande','Fang'),
              695:(b'Bus Stop Sign','Placa de ônibus','Bus Stop Sign')}.get(row['index'])
    if expected and (bytes.fromhex(row['source_hex']),text)==expected[:2]:return expected[2]
    return None

def validate_narrative(draft):
    from build_translation_pilot import load_draft
    binding=draft['pending_name_resolution'];m,parent=load(binding)
    p=ROOT/parent['base_dialogue_draft']
    if sha(p.read_bytes())!=m['parent_dialogue_sha256']:raise ValueError('Pending-name narrative parent changed')
    expected,_=load_draft(p)
    for change in m['bus_stop_references']:
        key=change['id']
        if sha(json.dumps(expected['translations'][key],ensure_ascii=False,sort_keys=True).encode('utf-8'))!=change['parent_value_sha256']:
            raise ValueError('Bus Stop Sign prior narrative differs')
        expected['translations'][key]=change['translation']
    rebinding=m['speaker_rebinding']
    row=next(r for r in expected['speaker_label_relocations']['entries'] if r['id']==rebinding['id'])
    if (row['id']!='map.msgn.0e76fcc4' or row['target_offset']!=rebinding['target_offset']
        or sha(json.dumps(row,ensure_ascii=False,sort_keys=True).encode('utf-8'))!=rebinding['parent_binding_sha256']):
        raise ValueError('Pending-name speaker binding differs')
    row['base_record_sha256']=rebinding['base_record_sha256']
    expected.update(pending_name_resolution=binding,name='regiao-inicial-v040',
        status='Referências a Placa de ônibus acompanham o item; demais diálogos preservados.',
        reviewed_changes=[r['id'] for r in m['bus_stop_references']])
    if draft!=expected:raise ValueError('Non-authorized pending-name narrative change')

def filter_terminology(binding,key,segment,source,target,issues):
    if key not in BUS_IDS or segment!='body':return issues
    m,_=load(binding);changes={r['id']:r for r in m['bus_stop_references']}
    change=changes[key];value=change['translation'];expected=value['body'] if isinstance(value,dict) else value
    if segment!='body' or target!=expected or sha(source.encode('utf-8'))!=change['source_body_sha256']:
        raise ValueError('Bus Stop Sign reference identity differs')
    from translation_policy import occurrences
    if occurrences(source,'Bus Stop Sign')!=1 or occurrences(target,'Placa de ônibus')!=1:
        raise ValueError('Bus Stop Sign reference naming differs')
    return [i for i in issues if i!='Termo/nome protegido ausente: Bus Stop Sign']
