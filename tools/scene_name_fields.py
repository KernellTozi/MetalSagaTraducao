"""Bounded map scene-tree name catalogue. Read only; no edit permission."""
import argparse,collections,json,mmap,re,struct
from pathlib import Path
from dialogue import ROOT,sha
from reinsertion import SOURCE,RESOURCE
from interface_text import SOURCE as ELF
from glyph_spacing import ORIGINAL_SHA
from disc import entries,SECTOR

SCOPE='map-scene-name-fields-read-only-v007'
PROOF_SCOPE='six-approved-item-names-release-evidence-v007'
BASE=0x800


def parse(data,base=BASE):
    if bytes(data[base:base+4])!=b'maps' or struct.unpack_from('<I',data,base+4)[0]!=14:
        raise ValueError('Scene map bank signature/profile differs')
    header,size=struct.unpack_from('<II',data,base+8)
    if header!=0x12f0 or size>len(data)-base or header>size:
        raise ValueError('Scene bank bounds differ')
    count=(header-48)//16;rows=[];nodes=collections.Counter();trees=[];seen=set()
    for index in range(count):
        tree,tree_size,blob,script=struct.unpack_from('<4I',data,base+48+index*16)
        if not header<=tree<tree+tree_size<=blob<=script<=size or tree_size%16:
            raise ValueError('Scene tree/data ranges invalid')
        stack=[];pending=1;tree_rows=[]
        for at in range(base+tree,base+tree+tree_size,16):
            typ,children,identity,offset,length=struct.unpack_from('<HHIII',data,at)
            if not pending or typ>12:raise ValueError('Scene tree orphan/unknown node')
            while stack and stack[-1][1]==0:stack.pop()
            parent=stack[-1][0] if stack else None
            if stack:stack[-1][1]-=1
            if at==base+tree and typ!=0:raise ValueError('Scene root type differs')
            if offset+length>script-blob:raise ValueError('Scene payload exceeds bank entry')
            pending+=children-1;nodes[typ]+=1
            if typ in (2,3):
                if length<(0x48 if typ==2 else 0x34):raise ValueError('Short named scene payload')
                pos=base+blob+offset;raw=bytes(data[pos:pos+32]);zero=raw.find(0)
                if zero<0 or any(raw[zero:]):raise ValueError('Scene name has no bounded NUL/zero tail')
                if pos in seen:raise ValueError('Scene name payload alias needs separate analysis')
                seen.add(pos);flags=struct.unpack_from('<I',data,pos+32)[0]
                if typ==3 and flags&256 and (parent is None or parent['type']!=2):
                    raise ValueError('Inherited scene name has unexpected parent')
                row={'id':f'map.scene.{index:03d}.{at-base-tree:06x}',
                     'map_index':index,'node_offset':at,'node_type':typ,'node_identity':identity,
                     'node_sha256':sha(data[at:at+16]),'offset':pos,'field_bytes':32,
                     'field_sha256':sha(raw),'source_hex':raw[:zero].hex(),'source_bytes':zero,
                     'payload_prefix_sha256':sha(data[pos:pos+36]),
                     'native':any(b>127 for b in raw[:zero]),'has_item_reference':b'%I' in raw[:zero],
                     'inherits_parent_name':bool(typ==3 and flags&256),
                     'parent_node_offset':parent['offset'] if parent else None}
                rows.append(row);tree_rows.append(row['id'])
            node={'type':typ,'offset':at}
            if children:stack.append([node,children])
            if len(stack)>256:raise ValueError('Scene tree nesting exceeds probe bound')
        if pending:raise ValueError('Scene tree ends before child count')
        trees.append({'map_index':index,'tree_offset':base+tree,'tree_bytes':tree_size,
                      'tree_sha256':sha(data[base+tree:base+tree+tree_size]),'name_count':len(tree_rows)})
    return {'map_count':count,'node_counts':dict(nodes),'name_fields':len(rows),
            'native_fields':sum(r['native'] for r in rows),'item_references':sum(r['has_item_reference'] for r in rows),
            'inherited_names':sum(r['inherits_parent_name'] for r in rows),'rows':rows,'trees':trees}


def inspect_current_iso(result,image):
    from verify_test_iso import verify_image
    proof=verify_image(image)
    with Path(image).open('rb') as f:
        extent=next(r for r in entries(f) if r['path']==RESOURCE)
        for row in result['rows']:
            f.seek(extent['lba']*SECTOR+row['offset']);raw=f.read(36)
            if sha(raw)!=row['payload_prefix_sha256']:raise ValueError('Current ISO scene name/flags differ from reference')
        for row in result['trees']:
            f.seek(extent['lba']*SECTOR+row['tree_offset'])
            if sha(f.read(row['tree_bytes']))!=row['tree_sha256']:raise ValueError('Current ISO scene tree differs from reference')
    return {'image':proof,'fields_identical':len(result['rows'])}


def investigate(image=None):
    inventory=json.loads((ROOT/'reports/inventory.json').read_bytes())
    expected=next(r for r in inventory if r['path']==RESOURCE)
    elf=ELF.read_bytes()
    if sha(elf)!=ORIGINAL_SHA:raise ValueError('Scene loader ELF differs')
    with SOURCE.open('rb') as f,mmap.mmap(f.fileno(),0,access=mmap.ACCESS_READ) as data:
        if sha(data)!=expected['sha256']:raise ValueError('Reference scene resource differs')
        result=parse(data)
    if (result['map_count'],result['name_fields'],result['inherited_names'],result['item_references'])!=(300,839,400,0):
        raise ValueError('Observed scene catalogue changed')
    windows=((0x444c8,0x446b8),(0x447a8,0x44814),(0x44950,0x44998),
             (0x44ab8,0x44afc),(0x47328,0x473a8),(0x792fc,0x79314))
    result.update(schema=1,scope=SCOPE,source_sha256=expected['sha256'],elf_sha256=sha(elf),
                  loader_windows=[{'offset':a,'size':z-a,'sha256':sha(elf[a:z])} for a,z in windows],
                  editing_authorized=False,new_translations=0,iso_created=False,
                  limits='Exact 300-tree bank and typed name payloads linked to original loader. Does not enumerate arbitrary mutated trees, other class instances, computed calls or malformed saves. Native fields are preserved bytes, not decoded.')
    if image is not None:result['current_iso']=inspect_current_iso(result,image)
    return result


def message_budgets(document,item_bytes=18,name_bytes=31):
    from gfi import encode
    if item_bytes not in (18,19) or name_bytes!=31:raise ValueError('Only bound 18/19-byte item envelopes and valid N0 field')
    pattern=re.compile(r'%I(?:\$[0-9]+|[0-9]+)|%N0')
    fields=[];pages=[]
    for entry in document['entries']:
        for segment in entry['segments']:
            text=segment['translation']
            if '%I' not in text:continue
            if segment['key']!='body':raise ValueError('Unexpected item reference outside proven body set')
            rest=pattern.sub('',text).replace('%W5','')
            if '%' in rest:raise ValueError('Unreviewed control in item-bearing body')
            def upper(value,byte_count):
                total=len(encode(value)) if byte_count else len(value)
                for token in pattern.finditer(value):
                    total+=(name_bytes if token.group()=='%N0' else item_bytes)-len(token.group())
                return total
            bound=upper(text,True)
            if bound+1>1024:raise ValueError('Item-bearing full body exceeds large scratch bound')
            fields.append({'id':entry['id'],'segment':segment['key'],'text_sha256':sha(encode(text)),
                           'maximum_expanded_bytes':bound})
            for number,page in enumerate(text.split('\t')):
                if '%I' not in page:continue
                if '%' in pattern.sub('',page):raise ValueError('Unreviewed control in item-bearing page')
                cells=upper(page,False)
                if cells>99:raise ValueError('Item-bearing page exceeds cell stream bound')
                pages.append({'id':entry['id'],'page':number,'maximum_content_cells':cells,
                              'text_sha256':sha(encode(page))})
    if (len(fields),len(pages))!=(34,35):raise ValueError('Known item-message coverage differs')
    return {'item_byte_bound':item_bytes,'N0_byte_bound_for_valid_field':name_bytes,
            'name_field_precondition':'NUL within the existing 32-byte actor-name field; malformed/overflowed saves are not made valid by this release.',
            'fields':fields,'pages':pages,'field_count':len(fields),'page_count':len(pages),
            'maximum_body_bytes':max(r['maximum_expanded_bytes'] for r in fields),
            'maximum_page_content_cells':max(r['maximum_content_cells'] for r in pages),
            'independent_variable_values_bounded':True,
            'method':'Each I output is bounded by the longest encoded item name after the exact six proposals; byte count is also a conservative glyph-cell bound. Each N0 is bounded independently by a valid existing name field. W5 is unchanged and the string scratch routine has no expanding W handler.'}


def release_proof(image):
    from build_translation_pilot import load_draft,compile_draft
    from item_name_buffers import name_table
    from item_names import original,RESOURCE as S_PACK,ITEM_COUNT,STRIDE
    ui_path=ROOT/'translations/interface-v052.json';ui=json.loads(ui_path.read_bytes())
    elf=ELF.read_bytes();scenes=investigate(image)
    decisions=json.loads((ROOT/'translations/revisao-humana-itens-v001.json').read_bytes())
    table,_=name_table(elf,original(S_PACK),ui,decisions)
    lengths=[]
    for index in range(ITEM_COUNT):
        raw=table[index*STRIDE:index*STRIDE+24];end=raw.find(0)
        if end<0:raise ValueError('Proposed name table is unterminated')
        lengths.append(end)
    if max(lengths)!=18:raise ValueError('Proposed item byte envelope differs')
    draft,bindings=load_draft(ROOT/ui['base_dialogue_draft'])
    with SOURCE.open('rb') as f,mmap.mmap(f.fileno(),0,access=mmap.ACCESS_READ) as data:
        document,_,report=compile_draft(data,draft)
    if not report['valid']:raise ValueError('Invalid current dialogue base')
    return {'schema':1,'scope':PROOF_SCOPE,
            'parent_recipe':'translations/interface-v052.json','parent_sha256':sha(ui_path.read_bytes()),
            'dialogue_bindings':bindings,'scene_source_sha256':scenes['source_sha256'],
            'scene_fields':scenes['name_fields'],'scene_trees':scenes['map_count'],
            'scene_I_references':scenes['item_references'],'inherited_scene_names':scenes['inherited_names'],
            'scene_field_metadata_sha256':sha(json.dumps([{k:v for k,v in r.items() if k!='source_hex'} for r in scenes['rows']],sort_keys=True).encode()),
            'scene_iso_verification':scenes['current_iso'],'loader_windows':scenes['loader_windows'],
            'budgets':message_budgets(document),'item_table_maximum_bytes':max(lengths),
            'new_consumer_dependency_report':'reports/limites-nomes-v006.json',
            'new_consumer_dependency_sha256':sha((ROOT/'reports/limites-nomes-v006.json').read_bytes()),
            'assumptions':['Original resource revision and exact archived recipes.',
                'Valid game state: item indices address the existing table and actor-name fields retain a NUL within 32 bytes, as already required by the original game.'],
            'limits':'Source-bound known resource and direct-path evidence, not a universal safety proof for arbitrary code, malformed saves, indirect aliases or runtime-generated new templates. No names applied by this evidence generator.'}


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,default=ROOT/'work/nomes-cena-atual.json')
    p.add_argument('--current-iso',type=Path)
    p.add_argument('--release-proof',action='store_true')
    args=p.parse_args();out=args.output.resolve()
    if not out.is_relative_to(ROOT/'work'):raise ValueError('Keep scene name text and bytes in work/')
    expected_scope=PROOF_SCOPE if args.release_proof else SCOPE
    if out.exists() and json.loads(out.read_bytes()).get('scope')!=expected_scope:raise ValueError('Refuse unrelated scene catalogue')
    if args.release_proof:
        if args.current_iso is None:raise ValueError('Release evidence requires current ISO verification')
        r=release_proof(args.current_iso)
    else:r=investigate(args.current_iso)
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:r[k] for k in (('scene_trees','scene_fields','item_table_maximum_bytes') if args.release_proof else ('map_count','name_fields','native_fields','inherited_names','item_references'))}))
