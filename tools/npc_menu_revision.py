"""Consolidated v060: bound default NPC fields + choice-row measurement."""
import copy
import hashlib
import json
import mmap
from dialogue import ROOT,sha
from reinsertion import SOURCE
from interface_text import SOURCE as ELF
import npc_default_names as npc
import choice_text_metrics as choice

POLICY='npc-default-names-and-native-choice-width-v001'
PARENT='translations/interface-v059.json'
MANIFEST='translations/npc-menus-v001.json'
STATUS='108 nomes padrão de NPCs e largura nativa de opções; visual pendente.'


def template(data,elf):
    inv=next(r for r in json.loads((ROOT/'reports/inventory.json').read_bytes()) if r['path']==npc.RESOURCE)
    if sha(data)!=inv['sha256']:raise ValueError('Default name MCT source differs')
    cases=[]
    for mode in (0,1,2):
        for text in ('Sim','Não','Cancelar','Menino'):
            cases.append({'translation':text,'mode':mode,
                          'before':choice.execute(elf,text,mode=mode,patched=False),
                          'after':choice.execute(elf,text,mode=mode)})
    return {'schema':1,'policy':POLICY,'parent_recipe':PARENT,
            'parent_sha256':sha((ROOT/PARENT).read_bytes()),
            'resource':npc.RESOURCE,'source_sha256':inv['sha256'],
            'model_bank_offset':npc.BASE,'model_records':npc.COUNT,
            'model_directory_sha256':sha(data[npc.BASE:npc.BASE+4+npc.COUNT*npc.STRIDE]),
            'entries':npc.targets(data,elf),'name_instruction_windows':npc.bindings(elf),
            'choice_instruction_windows':choice.bindings(elf),
            'choice_patch_sha256':sha(choice.replacement()),'choice_cases':cases}


def validate_interface(recipe):
    binding=recipe['npc_and_choice_release']
    if set(binding)!={'recipe','sha256'} or binding['recipe']!=MANIFEST:
        raise ValueError('Unknown NPC/choice binding')
    raw=(ROOT/MANIFEST).read_bytes()
    if sha(raw)!=binding['sha256']:raise ValueError('NPC/choice manifest differs')
    manifest=json.loads(raw);parent_raw=(ROOT/PARENT).read_bytes();parent=json.loads(parent_raw)
    if manifest.get('parent_recipe')!=PARENT or manifest.get('parent_sha256')!=sha(parent_raw):
        raise ValueError('NPC/choice parent differs')
    expected=copy.deepcopy(parent)
    expected.update(npc_and_choice_release=binding,iso_name='MetalSaga-ptbr-interface-v060.iso',status=STATUS)
    if recipe!=expected:raise ValueError('Unrelated NPC/choice child mutation')
    return parent,manifest


def compile_additions(data,elf,manifest):
    if manifest!=template(data,elf):raise ValueError('NPC/choice sources, fields or metric proof changed')
    patches,report=npc.compile_names(data,elf,manifest['entries'])
    if report['accepted']!=108:raise ValueError('Expected 108 reviewed default names')
    patches.append(choice.elf_patch(elf))
    return patches,{'policy':POLICY,'accepted':108,'npc_default_names':report,
                    'choice_metrics':{'function_offset':choice.START,'size':choice.END-choice.START,
                        'native_measure_function':choice.MEASURE,'cases':manifest['choice_cases'],
                        'new_storage_or_heap_changes':False,'font_bitmaps_and_layout_v005_unchanged':True},
                    'explicit_13_labels_still_pending':True,'pcsx2_executed':False,
                    'visual_status':'pending_user'}


def compile_interface(elf,recipe):
    from interface_text import compile_draft
    parent,manifest=validate_interface(recipe)
    patches,report=compile_draft(elf,parent)
    with SOURCE.open('rb') as stream,mmap.mmap(stream.fileno(),0,access=mmap.ACCESS_READ) as data:
        additions,evidence=compile_additions(data,elf,manifest)
    for p in additions:
        if any(q['resource']==p['resource'] and max(p['offset'],q['offset'])<min(p['offset']+len(p['before']),q['offset']+len(q['before'])) for q in patches):
            raise ValueError('NPC/choice patch overlaps an older translation')
    report=copy.deepcopy(report);report['accepted']+=evidence['accepted']
    report['npc_and_choice_release']=evidence
    return patches+additions,report


def prepare():
    elf=ELF.read_bytes()
    with SOURCE.open('rb') as stream,mmap.mmap(stream.fileno(),0,access=mmap.ACCESS_READ) as data:
        manifest=template(data,elf);patches,report=compile_additions(data,elf,manifest)
        catalog={r['id']:r for r in npc.catalog(data)}
        review=[{'id':r['id'],'source':catalog[r['id']]['source'],'translation':r['translation'],
                 'capacity':31,'target_bytes':r['target_bytes']} for r in manifest['entries']]
    payload=(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n').encode()
    (ROOT/MANIFEST).write_bytes(payload)
    child=json.loads((ROOT/PARENT).read_bytes())
    child.update(npc_and_choice_release={'recipe':MANIFEST,'sha256':sha(payload)},
                 iso_name='MetalSaga-ptbr-interface-v060.iso',status=STATUS)
    (ROOT/'translations/interface-v060.json').write_bytes((json.dumps(child,ensure_ascii=False,indent=2)+'\n').encode())
    validate_interface(child)
    out=ROOT/'work/npc-menus-v001';out.mkdir(exist_ok=True)
    (out/'revisao-local.json').write_bytes((json.dumps(review,ensure_ascii=False,indent=2)+'\n').encode())
    return {'new_default_names':108,'unique_labels':len({r['translation'] for r in review}),
            'patches':len(patches),'boy_occurrences':sum(r['source']=='Boy' for r in review),
            'explicit_13_labels_still_pending':True}


if __name__=='__main__':print(json.dumps(prepare(),ensure_ascii=True))
