"""Conservative ELF UI text catalog and fixed-string patches; no relocation."""
import argparse
import hashlib
import json
import re
import struct
from pathlib import Path
from glyph_spacing import ORIGINAL_SHA
from gfi import encode,decode
from reinsertion import ROOT,local

SOURCE=ROOT/'JOGO/Metal Saga/SLUS_212.93'
FORMAT=re.compile(rb'%(?:%|[-+ #0]*\d*(?:\.\d+)?[hlL]*[diuoxXfFeEgGcs])')


def sections(data):
    if data[:6]!=b'\x7fELF\x01\x01':raise ValueError('ELF32 LE required')
    off=struct.unpack_from('<I',data,32)[0];step,count,names_index=struct.unpack_from('<HHH',data,46)
    rows=[struct.unpack_from('<10I',data,off+i*step) for i in range(count)]
    names=data[rows[names_index][4]:rows[names_index][4]+rows[names_index][5]]
    return {names[r[0]:].split(b'\0',1)[0].decode('ascii'):{'va':r[3],'offset':r[4],'size':r[5],'type':r[1]} for r in rows}


def references(data,parts):
    """Conservative address evidence, not a complete control-flow disassembler."""
    refs={}
    def add(va,item):refs.setdefault(va,[]).append(item)
    for name in ('.data','.rodata','.sdata'):
        s=parts[name]
        for at in range(s['offset'],s['offset']+s['size']-3,4):
            add(struct.unpack_from('<I',data,at)[0],{'kind':'data-pointer','offset':at})
    gp=struct.unpack_from('<I',data,parts['.reginfo']['offset']+20)[0]
    text=parts['.text'];end=text['offset']+text['size']
    for at in range(text['offset'],end-3,4):
        w=struct.unpack_from('<I',data,at)[0];op=w>>26;rt=w>>16&31;rs=w>>21&31
        if op==9 and rs==28:
            n=w&65535;n=n if n<32768 else n-65536
            add(gp+n,{'kind':'gp-addiu','offset':at,'word':f'{w:08x}'})
        if op!=15:continue
        stop=end
        for pos in range(at+4,min(at+32,stop),4):
            if pos>=stop:break
            x=struct.unpack_from('<I',data,pos)[0];xo=x>>26;xr=x>>21&31;xt=x>>16&31
            if xr==rt and xo in (9,13):
                lo=x&65535
                va=((w&65535)<<16)+(lo if lo<32768 or xo==13 else lo-65536)
                add(va,{'kind':'lui-immediate-candidate','offset':at,'immediate_offset':pos,
                        'words':[f'{w:08x}',f'{x:08x}']})
            if xo in (1,2,3,4,5,6,7,20,21,22,23):stop=min(stop,pos+8)
            if (xo in (9,13,15,35,32,36) and xt==rt) or (xo==0 and x>>11&31==rt):break
    return refs


def catalog(data,verify=True):
    checksum=hashlib.sha256(data).hexdigest()
    if verify and checksum!=ORIGINAL_SHA:raise ValueError('Original ELF revision mismatch')
    parts=sections(data);refs=references(data,parts);rows=[]
    for name in ('.rodata','.sdata'):
        s=parts[name];raw=data[s['offset']:s['offset']+s['size']]
        for match in re.finditer(rb'(?<=\x00)[\x20-\x7e]{3,}\x00',raw):
            at=s['offset']+match.start();value=match.group()[:-1];va=s['va']+match.start()
            base_refs=refs.get(va,[])
            interior=[{'relative_offset':i,'references':refs[va+i]} for i in range(1,len(value)) if va+i in refs]
            rows.append({'id':f'elf.ui.{at:08x}','offset':at,'va':va,'section':name,'source':value.decode('ascii'),
                'source_hex':value.hex(),'source_sha256':hashlib.sha256(value).hexdigest(),'capacity':len(value),
                'references':base_refs,'interior_references':interior,
                'status':'referenced-candidate' if base_refs and not interior else 'pending'})
    return {'schema':1,'source_sha256':checksum,'reference_limit':'Address evidence only; does not prove runtime screen or completeness',
            'entries':rows}


def controls(raw):
    out=[];cursor=0
    while cursor<len(raw):
        if raw[cursor]==37:
            m=FORMAT.match(raw,cursor)
            if not m:raise ValueError('Unknown percent syntax in UI string')
            out.append(m.group());cursor=m.end();continue
        if raw[cursor] in b'|;\n\t':out.append(raw[cursor:cursor+1])
        cursor+=1
    return out


def embedded_catalog(data):
    """Two exact format-string consumers; no general scan/boundary relaxation."""
    windows=((0x122304,0x122330,'bef0d1ab5e1f69dcd3513b612f3afaf39652434b1c34159d5d00904002d9a4aa'),
             (0x122558,0x122568,'d3cdb49cc41b853c133476ee8b64c3d011d31a207327f33bd728c9456cf4c170'))
    for a,z,h in windows:
        if hashlib.sha256(data[a:z]).hexdigest()!=h:raise ValueError('Embedded UI consumer changed')
    refs=references(data,sections(data));result=[]
    for at in (0x32c6c0,0x32c810):
        end=data.find(b'\0',at);value=data[at:end];va=at+0xff000
        if not value or any(c!=10 and not 32<=c<127 for c in value):raise ValueError('Embedded literal structure changed')
        interior=[{'relative_offset':i,'references':refs[va+i]} for i in range(1,len(value)) if va+i in refs]
        result.append({'id':f'elf.ui.{at:08x}','offset':at,'source_hex':value.hex(),'source_sha256':hashlib.sha256(value).hexdigest(),
            'references':refs.get(va,[]),'interior_references':interior,'status':'referenced-candidate' if refs.get(va) and not interior else 'pending'})
    return result


def compile_draft(data,draft):
    if hashlib.sha256(data).hexdigest()!=ORIGINAL_SHA:raise ValueError('Original ELF revision mismatch')
    if draft.get('schema')!=1 or draft.get('policy')!='elf-ui-fixed-original-string-v001':raise ValueError('Unknown UI policy')
    if draft.get('source_sha256')!=ORIGINAL_SHA:raise ValueError('UI source binding mismatch')
    cat=catalog(data);by_id={e['id']:e for e in cat['entries']};seen=set();patches=[];metadata=[]
    if draft.get('embedded_literal_profile'):
        if draft['embedded_literal_profile']!='two-proven-format-literals-v003':raise ValueError('Unknown embedded UI profile')
        by_id.update({e['id']:e for e in embedded_catalog(data)})
    for target in draft['entries']:
        key=target['id']
        if key in seen:raise ValueError('Duplicate UI ID')
        seen.add(key);old=by_id[key]
        if old['status']!='referenced-candidate':raise ValueError(f'UI string lacks safe reference evidence: {key}')
        if target['source_sha256']!=old['source_sha256']:raise ValueError('UI string binding mismatch')
        if not target.get('group'):raise ValueError('UI context group required')
        before=bytes.fromhex(old['source_hex']);after=encode(target['translation'])
        if draft.get('weapon_terms_policy'):
            from weapon_terms import validate as validate_weapon,POLICY as WEAPON_POLICY
            if draft['weapon_terms_policy']!=WEAPON_POLICY:raise ValueError('Unknown weapon terminology policy')
            issues=validate_weapon(before.decode('ascii'),target['translation'])
            if issues:raise ValueError('UI weapon terminology: '+'; '.join(issues))
        if not after or len(after)>len(before):raise ValueError(f'UI overflow: {key}: {len(after)} > {len(before)}')
        if decode(after)!=target['translation']:raise ValueError('UI Unicode round-trip failed')
        if controls(before)!=controls(after):raise ValueError('UI format/control sequence changed')
        if re.match(rb' *',before).group()!=re.match(rb' *',after).group():raise ValueError('UI leading alignment spaces changed')
        if re.search(rb' *$',before).group()!=re.search(rb' *$',after).group():raise ValueError('UI trailing alignment spaces changed')
        if before==after:raise ValueError('UI draft must contain actual changes')
        # Keep both the original address and original terminating NUL. Do not
        # claim padding, modify pointer tables, expand literals or move strings.
        patch={'resource':'SLUS_212.93','id':key,'offset':old['offset'],'before':before+b'\0',
               'after':after+bytes(len(before)+1-len(after))}
        patches.append(patch);metadata.append({'id':key,'offset':old['offset'],'source_sha256':old['source_sha256'],
            'target_sha256':hashlib.sha256(after).hexdigest(),'source_bytes':len(before),'target_bytes':len(after),
            'group':target['group'],'references':old['references'],'controls_hex':[c.hex() for c in controls(before)]})
    if not patches:raise ValueError('Empty UI draft')
    patches.sort(key=lambda p:p['offset'])
    if any(a['offset']+len(a['before'])>b['offset'] for a,b in zip(patches,patches[1:])):raise ValueError('UI patches overlap')
    result=bytearray(data)
    for p in patches:result[p['offset']:p['offset']+len(p['after'])]=p['after']
    if len(result)!=len(data) or sections(result)!=sections(data):raise ValueError('ELF structure changed')
    for p in patches:
        if result[p['offset']:p['offset']+len(p['after'])]!=p['after']:raise ValueError('UI readback failed')
        result[p['offset']:p['offset']+len(p['before'])]=p['before']
    if result!=data:raise ValueError('UI reverse round-trip failed')
    from interface_resources import compile_resources
    resource_patches,resource_report=compile_resources(data,draft)
    patches.extend(resource_patches)
    install_report={'accepted':0}
    if draft.get('install_texts'):
        from install_texts import compile_install
        extra,install_report=compile_install(data,draft['install_texts']);patches.extend(extra)
    spack_report={'accepted':0};status_report={'accepted':0}
    if draft.get('spack_ui'):
        from spack_ui import compile_ui as compile_spack
        added,spack_report=compile_spack(data,draft['spack_ui']);patches.extend(added)
    if draft.get('character_status'):
        from spack_ui import compile_status
        added,status_report=compile_status(data,draft['character_status']);patches.extend(added)
    satcom_report={'accepted':0}
    if draft.get('satcom_records'):
        from spack_satcom import compile_satcom
        added,satcom_report=compile_satcom(data,draft['satcom_records']);patches.extend(added)
    item_report={'accepted':0}
    if draft.get('item_descriptions'):
        from item_descriptions import compile_descriptions
        if draft.get('description_review',{}).get('policy'):
            from prepare_item_batch import validate_review
            from item_descriptions import catalog as item_catalog,RESOURCE as ITEM_RESOURCE
            from interface_resources import original
            validate_review(draft['description_review'],draft['item_descriptions'],item_catalog(original(ITEM_RESOURCE)))
        added,item_report=compile_descriptions(data,draft['item_descriptions']);patches.extend(added)
    item_name_report={'accepted':0}
    if draft.get('item_names'):
        from item_names import compile_names,validate_review,catalog as name_catalog,original,RESOURCE as NAME_RESOURCE
        validate_review(draft['item_name_review'],draft['item_names'],name_catalog(original(NAME_RESOURCE)))
        added,item_name_report=compile_names(data,draft['item_names']);patches.extend(added)
        if draft.get('item_descriptions'):
            if 'names_and_item_records_unchanged' in item_report:
                item_report['names_and_item_records_unchanged_by_description_patches']=item_report.pop('names_and_item_records_unchanged')
            item_report['generic_names_modified_under_separate_policy']=True
    battle_report={'accepted':0}
    if draft.get('spack_battle'):
        from spack_battle import compile_battle
        added,battle_report=compile_battle(data,draft['spack_battle'],draft['item_names']);patches.extend(added)
    interaction_report={'accepted':0}
    if draft.get('spack_interactions'):
        from spack_interactions import compile_interactions
        added,interaction_report=compile_interactions(data,draft['spack_interactions']);patches.extend(added)
    name_report={'accepted':0}
    if draft.get('name_entry'):
        from name_entry_text import compile_name_entry
        name_patches,name_report=compile_name_entry(data,draft['name_entry'])
        for p in name_patches:
            if any(q['resource']==p['resource'] and max(p['offset'],q['offset'])<min(p['offset']+len(p['before']),q['offset']+len(q['before'])) for q in patches):
                raise ValueError('Name entry patches overlap prior interface fields')
            patches.append(p)
    if draft.get('battle_spacing'):
        from battle_font_advance import elf_patch
        patches.append(elf_patch(data,draft['battle_spacing']))
    graphics_report={'accepted':0}
    context_report=None
    if draft.get('canine_status_context'):
        from character_status_context import proof as context_proof
        context_report=context_proof(data,draft['canine_status_context'])
        target=next((e for e in draft['entries'] if e['id']=='elf.ui.0032b690'),None)
        if not target or target['translation']!='Pelo: %4d':raise ValueError('Canine status evidence requires the reviewed Pelo label')
    if draft.get('graphics'):
        binding=draft['graphics'];path=(ROOT/binding['recipe']).resolve()
        if not path.is_relative_to(ROOT/'translations'):raise ValueError('Graphic recipe outside translations/')
        raw=path.read_bytes()
        if hashlib.sha256(raw).hexdigest()!=binding['sha256']:raise ValueError('Graphic recipe binding mismatch')
        from interface_graphics import compile_graphics
        graphics_patches,graphics_report=compile_graphics(json.loads(raw))
        patches.extend(graphics_patches)
    return patches,{'schema':1,'policy':draft['policy'],'source_sha256':ORIGINAL_SHA,'accepted':len(metadata)+resource_report['accepted']+graphics_report['accepted']+name_report['accepted']+spack_report['accepted']+status_report['accepted']+satcom_report['accepted']+item_report['accepted']+item_name_report['accepted']+install_report['accepted']+battle_report['accepted']+interaction_report['accepted'],
        'elf_strings':len(metadata),'resource_texts':resource_report,'patch_count':len(patches),
        **({'install_texts':install_report} if draft.get('install_texts') else {}),
        'graphic_labels':graphics_report,
        **({'spack_ui':spack_report} if draft.get('spack_ui') else {}),
        **({'character_status':status_report} if draft.get('character_status') else {}),
        **({'satcom_records':satcom_report} if draft.get('satcom_records') else {}),
        **({'item_descriptions':item_report} if draft.get('item_descriptions') else {}),
        **({'item_names':item_name_report} if draft.get('item_names') else {}),
        **({'spack_battle':battle_report} if draft.get('spack_battle') else {}),
        **({'spack_interactions':interaction_report} if draft.get('spack_interactions') else {}),
        **({'name_entry':name_report} if draft.get('name_entry') else {}),
        **({'canine_status_context':context_report} if context_report else {}),
        **({'battle_spacing':{'policy':draft['battle_spacing']['policy'], 'codes':18,
            'advance':'Existing ASCII half-cell; glyph dispatch and input bytes preserved',
            'runtime_visual_status':'pending_user_verification'}} if draft.get('battle_spacing') else {}),
        'elf_size_unchanged':True,'addresses_and_pointers_unchanged':not bool(draft.get('spack_ui')),
        'elf_addresses_and_pointers_unchanged':True,'reverse_roundtrip':True,
        'runtime_visual_status':'pending_user_verification','results':metadata}


def main():
    parser=argparse.ArgumentParser(description='Catalogar candidatos de interface do ELF original, sem APIs')
    parser.add_argument('--output',type=Path,required=True);args=parser.parse_args()
    output=local(args.output,True);output.parent.mkdir(parents=True,exist_ok=True)
    result=catalog(SOURCE.read_bytes());output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(f"{len(result['entries'])} strings ASCII catalogadas; referencias nao comprovam interface visivel")

if __name__=='__main__':main()
