"""Brazilian card terminology revision; bounded overlays on release v068."""
import copy
import json
from pathlib import Path

import minigames_release as base
from dialogue import ROOT, sha
from gfi import encode

POLICY = 'brazilian-card-terms-fixed-planes-v001'
PARENT = 'translations/interface-v068.json'
CHILD = 'translations/interface-v069.json'
MANIFEST = 'translations/termos-cartas-v001.json'
FOLDER = ROOT/'work/cartas-v069'
STATUS = 'Terminologia brasileira dos jogos de cartas; visual pendente.'
TERMS = {
    'SEQUÊNCIA REAL': 'ROYAL FLUSH',
    'SEQUÊNCIA DE NAIPE': 'STRAIGHT FLUSH',
    'TRINCA E PAR': 'FULL HOUSE',
    'MESMO NAIPE': 'FLUSH',
    'Pôquer': 'Poker',
    'vinte e um natural': 'blackjack',
    'VINTE E UM PAGA 3:2': 'BLACKJACK PAGA 3:2',
}
LITERALS = {0x31fd38:'Blackjack', 0x348e00:'Poker'}


def revised_specs():
    content=json.loads((ROOT/base.CONTENT).read_bytes())
    changes=[]
    def walk(value):
        if isinstance(value,dict):
            return {k:walk(v) for k,v in value.items()}
        if isinstance(value,list):
            return [walk(v) for v in value]
        if isinstance(value,str):
            for old,new in TERMS.items():
                value=value.replace(old,new)
        return value
    for spec in content['textures']:
        revised=walk(spec)
        if revised!=spec:
            changes.append((spec,revised))
    return changes


def derive(elf,parents,previews=False):
    replacements=[]; evidence=[]; images=[]
    for old,spec in revised_specs():
        # These card planes were new in v068, so original is the rendering base.
        patch,proof,current,output=base.render_texture(spec,[])
        prior=next((p for p in parents if p['id']==patch['id']),None)
        if not prior or any(prior[k]!=patch[k] for k in ('resource','offset','before')):
            raise ValueError('Card plane is not an exact v068 plane')
        reproduced,_,_,_=base.render_texture(old,[])
        if reproduced['after']!=prior['after']:
            raise ValueError('Card plane v068 content mismatch')
        if patch['after']==prior['after']:
            raise ValueError('Card revision has no change')
        replacements.append(patch); evidence.append(proof)
        if previews:
            raw=base.original(spec['resource']);at=spec['offset'];meta=proof['texture']
            header=raw[at:at+meta['pixel_offset']]
            images.append((spec,proof,header+prior['after'],output))
    for at,target in LITERALS.items():
        prior=next(p for p in parents if p['id']==f'minigame.elf.{at:08x}')
        if elf[at:at+len(prior['before'])]!=prior['before']:
            raise ValueError('Card literal baseline differs')
        out=encode(target)
        if len(out)>=len(prior['before']):
            raise ValueError('Card literal overflow')
        replacements.append({**prior,'after':out+bytes(len(prior['before'])-len(out))})
    if previews:
        FOLDER.mkdir(parents=True,exist_ok=True)
        # Same reviewed before/after generator, redirected only for this call.
        previous=base.FOLDER
        try:
            base.FOLDER=FOLDER
            base.export_previews(images)
        finally:
            base.FOLDER=previous
    return replacements,evidence


def binding_load(binding):
    if set(binding)!={'recipe','sha256'} or binding['recipe']!=MANIFEST:
        raise ValueError('Unknown card terminology binding')
    raw=(ROOT/MANIFEST).read_bytes();m=json.loads(raw)
    if (sha(raw)!=binding['sha256'] or m['policy']!=POLICY
        or m['parent_sha256']!=sha((ROOT/PARENT).read_bytes())
        or m['source_content_sha256']!=sha((ROOT/base.CONTENT).read_bytes())
        or m['terms']!=TERMS or m['literals']!={str(k):v for k,v in LITERALS.items()}
        or m['fonts']!={k:sha(p.read_bytes()) for k,p in base.FONTS.items()}):
        raise ValueError('Card terminology source/manifest/font drift')
    return m


def validate(recipe):
    m=binding_load(recipe['card_terms_review'])
    parent=json.loads((ROOT/PARENT).read_bytes());expected=copy.deepcopy(parent)
    expected.update(card_terms_review=recipe['card_terms_review'],
                    iso_name='MetalSaga-ptbr-interface-v069.iso',status=STATUS)
    if expected!=recipe:
        raise ValueError('Unrelated card terminology mutation')
    return parent,m


def compile_interface(elf,recipe):
    from interface_text import compile_draft
    parent,m=validate(recipe)
    parents,report=compile_draft(elf,parent)
    revised,evidence=derive(elf,parents)
    if m['revised']!=[base.metadata(p) for p in revised] or m['evidence']!=evidence:
        raise ValueError('Card terminology output drift')
    replacements={p['id']:p for p in revised}
    report=copy.deepcopy(report)
    report['card_terms_review']={'policy':POLICY,'texture_planes':len(evidence),
        'elf_literals':len(LITERALS),'new_units':0,'pcsx2_executed':False,
        'visual_status':'pending_user'}
    return [replacements.get(p['id'],p) for p in parents],report


def prepare():
    from interface_text import compile_draft
    elf=base.ELF.read_bytes();parent=json.loads((ROOT/PARENT).read_bytes())
    parents,_=compile_draft(elf,parent)
    revised,evidence=derive(elf,parents,previews=True)
    m={'schema':1,'policy':POLICY,'parent':PARENT,
       'parent_sha256':sha((ROOT/PARENT).read_bytes()),
       'source_content_sha256':sha((ROOT/base.CONTENT).read_bytes()),
       'terms':TERMS,'literals':LITERALS,
       'fonts':{k:sha(p.read_bytes()) for k,p in base.FONTS.items()},
       'revised':[base.metadata(p) for p in revised],'evidence':evidence}
    raw=(json.dumps(m,ensure_ascii=False,indent=2)+'\n').encode()
    (ROOT/MANIFEST).write_bytes(raw)
    child=copy.deepcopy(parent)
    child.update(card_terms_review={'recipe':MANIFEST,'sha256':sha(raw)},
                 iso_name='MetalSaga-ptbr-interface-v069.iso',status=STATUS)
    (ROOT/CHILD).write_bytes((json.dumps(child,ensure_ascii=False,indent=2)+'\n').encode())
    validate(child)
    print(f'Card terminology: {len(evidence)} planes, {len(LITERALS)} literals')


if __name__=='__main__':
    prepare()
