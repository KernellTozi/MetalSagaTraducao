"""Read-only capacity investigation. No compiler policy or game writes."""
import argparse,json,struct
from functools import lru_cache
from pathlib import Path
from dialogue import ROOT,sha
from glyph_spacing import ORIGINAL_SHA
from interface_text import SOURCE,sections
from item_names import catalog,original,RESOURCE
from gfi import encode

SCOPE='item-name-capacity-read-only-v001'
RECIPE='translations/interface-v050.json'
DECISIONS='translations/revisao-humana-itens-v001.json'
WINDOWS=((0x1977c8,0x197910),(0x3e1f0,0x3e2ac),(0x1cd474,0x1cd498),(0x1b34ec,0x1b3504),
         (0x1b3b0c,0x1b3b6c),(0x1b55e8,0x1b5698),(0x1d5510,0x1d5560))

def census(elf):
    """Exact opcode candidates; not an alias or whole-program proof."""
    if sha(elf)!=ORIGINAL_SHA:raise ValueError('Capacity ELF revision differs')
    section=sections(elf)['.text'];reads=[];writes=[];calls=[];literal_refs=[]
    for at in range(section['offset'],section['offset']+section['size'],4):
        w=struct.unpack_from('<I',elf,at)[0];op=w>>26
        if op in (35,43) and w&65535==0x5ae8:
            (reads if op==35 else writes).append({'offset':at,'word':f'{w:08x}',
                'base_register':w>>21&31,'register':w>>16&31,
                'window_offset':max(section['offset'],at-32),
                'window_sha256':sha(elf[max(section['offset'],at-32):at+100]),
                'status':'low-immediate candidate; base register and pointer use require tracing'})
        va=at+0xff000
        if op==3 and (((va+4)&0xf0000000)|((w&0x3ffffff)<<2))==0x16c938:
            calls.append({'offset':at,'word':f'{w:08x}','window_sha256':sha(elf[at:at+100]),
                'status':'exact direct record-getter call; can access attributes or forward a pointer, not necessarily a name'})
    for name in ('.rodata','.data','.sdata'):
        part=sections(elf)[name]
        for at in range(part['offset'],part['offset']+part['size']-3,4):
            if struct.unpack_from('<I',elf,at)[0]==0x475ae8:literal_refs.append(at)
    return {'raw_low_immediate_load_candidates':reads,'raw_low_immediate_store_candidates':writes,
        'direct_record_getter_calls':calls,'aligned_global_address_literals':literal_refs,
        'limits':'Immediate scan includes unproved bases; direct getter calls do not imply names. Indirect calls, aliases, pointer stores/loads, arithmetic-address materialization and all control flow are not resolved. Never authorizes growth.'}

def probe(elf,raw,*,copy=False,direct=False,classification=None):
    """Original scalar loops with bounded RAM and declared draw/table models.

    Drawing is a stub; classification-table contents are modeled from the same
    ranges as existing layout probes, not claimed to execute initialization.
    Copy destination has 32 synthetic bytes, not a proven real buffer size.
    """
    if sha(elf)!=ORIGINAL_SHA:raise ValueError('Capacity probe ELF differs')
    if not raw or b'\0' in raw or copy and direct:raise ValueError('Capacity probe requires nonempty terminated-by-harness bytes and one mode')
    regs=[0]*32;regs[29]=0x700000;regs[31]=0x7ffff0;regs[4]=0x650000;regs[5]=0x600000
    if copy:regs[5]=0x600000;regs[18]=0x610000
    start,end=(0x1cd474,0x1cd498) if copy else (0x197858,0x197910)
    if direct:
        start,end=0x3e1f0,0x3e2ac;regs[16]=0x600000;regs[17]=10;regs[18]=20
        regs[19]=22;regs[20]=11;regs[21]=22;regs[23]=0
    pc=start;pending=None;mem={};glyphs=[];reads=[];writes=[];code_pcs=[]
    source=raw+b'\0';destination=bytearray(b'\xa5'*32+b'GUARD')
    saved={r:regs[r] for r in (16,17,29,31)}
    def get(at,size,signed=False):
        if 0x600000<=at and at+size<=0x600000+len(source):
            reads.append((at,size));data=source[at-0x600000:at-0x600000+size]
        elif 0x610000<=at and at+size<=0x610000+len(destination):data=destination[at-0x610000:at-0x610000+size]
        elif 0x484660<=at<0x484760 and size==1:
            b=at-0x484660
            val=classification(b) if classification else 0 if b<32 else 1 if b<=127 else 2 if 0xa0<=b<=0xdf else -2 if 0xf0<=b<=0xf9 else -1
            data=bytes((val&255,))
        elif all(at+i in mem for i in range(size)):data=bytes(mem[at+i] for i in range(size))
        elif 0xff000<=at and at+size<=0xff000+len(elf):data=elf[at-0xff000:at-0xff000+size]
        else:raise ValueError(f'Capacity probe unmapped read {at:x}/{size}')
        return int.from_bytes(data,'little',signed=signed)
    def put(at,value,size):
        if 0x610000<=at and at+size<=0x610000+len(destination):
            destination[at-0x610000:at-0x610000+size]=(value&((1<<(size*8))-1)).to_bytes(size,'little');writes.append((at,size))
        elif 0x6ffe00<=at and at+size<=0x700100:
            for i in range(size):mem[at+i]=value>>(8*i)&255
        else:raise ValueError(f'Capacity probe unmapped write {at:x}/{size}')
    if direct:put(0x700000,10,4);put(0x7000b0,0,4)
    for _ in range(10000):
        if pc==(end if copy or direct else 0x7ffff0):
            if copy:
                if destination[:len(raw)]!=raw or destination[len(raw):]!=b'\xa5'*(32-len(raw))+b'GUARD':
                    raise ValueError('Capacity scalar copy/guards differ')
                return {'copied_bytes':len(writes),'source_bytes':len(raw),'source_terminator_read':max(a+s for a,s in reads)==0x600000+len(source),
                    'destination_nul_written':False,'synthetic_destination_bytes':32,'guard_unchanged':True,
                    'real_destination_capacity_proven':False,'executed_instruction_count':len(code_pcs)}
            if not direct and any(regs[r]!=value for r,value in saved.items()):raise ValueError('Capacity renderer callee-saved register changed')
            return {'source_bytes':len(raw),'glyph_codes':glyphs,'consumed_bytes':max(a+s for a,s in reads)-0x600000,
                'source_terminator_read':True,'callee_saved':True if not direct else None,'draw_stub_calls':len(glyphs),
                'classification_table_modeled':True,'executed_instruction_count':len(code_pcs),
                'loop_offset':start,'draw_and_escape_compare_modeled':direct}
        if pc in (0x197910,0x3e2e0):
            glyphs.append(regs[5]&65535);regs[2]=regs[6]+1 if direct else 1;pc=regs[31];continue
        if direct and pc==0x197080:
            b=regs[4]&255;regs[2]=(-1 if b==0x82 else 1)&((1<<128)-1);pc=regs[31];continue
        if direct and pc==0x2269c8:
            result=0
            for i in range(regs[6]):
                a=get(regs[4]+i,1);b=get(regs[5]+i,1)
                if a!=b:result=1;break
                if a==0:break
            regs[2]=result;pc=regs[31];continue
        if not start<=pc<end:raise ValueError(f'Capacity probe escaped original code {pc:x}')
        code_pcs.append(pc);w=struct.unpack_from('<I',elf,pc)[0];op=w>>26;rs=w>>21&31;rt=w>>16&31;rd=w>>11&31;fn=w&63
        u=w&65535;n=u if u<32768 else u-65536;old=pending;pending=None;nextpc=pc+4
        if op==0:
            if fn==0:regs[rd]=regs[rt]<<((w>>6)&31)
            elif fn==3:
                value=regs[rt]&0xffffffff;value=value if value<0x80000000 else value-0x100000000
                regs[rd]=value>>((w>>6)&31)
            elif fn in (33,45):regs[rd]=regs[rs]+regs[rt]
            elif fn==37:regs[rd]=regs[rs]|regs[rt]
            elif fn==8:
                target=regs[rs];pending=target-0xff000 if 0xff000<=target<0xff000+len(elf) else target
            else:raise ValueError(f'Capacity unsupported R opcode {w:08x}')
        elif op==9:regs[rt]=regs[rs]+n
        elif op==11:regs[rt]=int((regs[rs]&0xffffffff)<(n&0xffffffff))
        elif op==15:regs[rt]=u<<16
        elif op in (30,32,33,35,36,55):
            size={30:16,32:1,33:2,35:4,36:1,55:8}[op]
            regs[rt]=get((regs[rs]+n)&0xffffffff,size,signed=op in (32,33))
        elif op in (31,40,43,63):put((regs[rs]+n)&0xffffffff,regs[rt],{31:16,40:1,43:4,63:8}[op])
        elif op in (4,5,20,21):
            take=regs[rs]==regs[rt] if op in (4,20) else regs[rs]!=regs[rt]
            if op in (20,21) and not take:nextpc=pc+8
            else:pending=pc+4+n*4 if take else pc+8
        elif op==1 and rt==1:
            take=(regs[rs]&0x80000000)==0;pending=pc+4+n*4 if take else pc+8
        elif op==3:regs[31]=pc+8;pending=((w&0x3ffffff)<<2)-0xff000
        else:raise ValueError(f'Capacity unsupported opcode {w:08x}')
        regs=[v&((1<<128)-1) for v in regs];regs[0]=0;pc=old if old is not None else nextpc
    raise ValueError('Capacity probe step limit')

def investigate(elf,raw,recipe,decisions):
    if sha(elf)!=ORIGINAL_SHA:raise ValueError('Capacity source ELF differs')
    if sha(raw)!=recipe['item_names']['source_sha256']:raise ValueError('Capacity S_PACK differs')
    rows=catalog(raw);by={r['id']:r for r in rows};blocked=decisions['blocked'];targets={r['id']:r['translation'] for r in recipe['item_names']['entries']}
    if len(blocked)!=16 or len({r['id'] for r in blocked})!=16:raise ValueError('Capacity decisions scope differs')
    from spack_battle import catalog as battle_catalog
    battle=battle_catalog(raw);actions={r['id']:r['translation'] for r in recipe['spack_battle']['entries']}
    from glyph_layout import elf_patch
    from layout_probe import execute
    layout=elf_patch(elf)
    @lru_cache(None)
    def advance(char,side,mode):
        value=encode(char);r=execute(elf,layout['after'],value,side,mode)
        if r['consumed']!=len(value) or not r['callee_saved']:raise ValueError('Capacity metric probe differs')
        return r['metrics'][3]
    profiles=[];measurements={r['id']:[] for r in blocked}
    for side in (22,26):
        for mode in (0,1,2):
            width=lambda text:sum(advance(c,side,mode) for c in text)
            widths={r['index']:width(bytes.fromhex(r['source_hex']).decode('ascii')) for r in rows if not r['empty'] and not r['native']}
            maximum=max(widths.values());profiles.append({'side':side,'mode':mode,'original_maximum_advance':maximum,'witness_ids':[i for i,v in widths.items() if v==maximum]})
            for b in blocked:
                try:value=width(b['desired_not_applied'])
                except ValueError as e:
                    if 'Unsupported project glyph' not in str(e):raise
                    continue
                measurements[b['id']].append({'side':side,'mode':mode,'advance':value,'within_observed_envelope':value<=maximum})
    results=[]
    for b in blocked:
        row=by[b['id']];target=b['desired_not_applied'];error=None
        try:value=encode(target)
        except ValueError as e:value=None;error=str(e)
        counterparts=[{'id':r['id'],'record_sha256':r['record_sha256'],'source_sha256':r['source_sha256'],
            'current_translation':actions.get(r['id']),'physical_field_bytes':r['field_bytes'],
            'observed_policy_ceiling':18,'desired_exceeds_action_ceiling':len(value)>18 if value else None}
            for r in battle if r['kind']=='action' and r['source_hex']==row['source_hex']]
        if value is not None:
            if len(value)!=b['encoded_bytes']:raise ValueError('Capacity approved byte count differs')
            at=row['offset'];candidate=value+b'\0'
            if len(candidate)>24 or any(raw[at+row['source_bytes']:at+24]):raise ValueError('Capacity physical tail differs')
            renderer=probe(elf,value);copier=probe(elf,value,copy=True);direct_scan=probe(elf,value,direct=True)
            if renderer['draw_stub_calls']!=len(target) or renderer['consumed_bytes']!=len(value)+1:raise ValueError('Capacity renderer scan length differs')
            if direct_scan['glyph_codes']!=[int.from_bytes(encode(c),'big') for c in target if c!=' ']:raise ValueError('Capacity direct scan glyph sequence differs')
        else:renderer=copier=direct_scan=None
        results.append({'id':b['id'],'record_sha256':row['record_sha256'],'source_name_sha256':row['source_sha256'],
            'current_translation':targets.get(b['id']),'desired_translation':target,'encoded_bytes':len(value) if value else None,
            'unicode_characters':len(target),'codec_error':error,'physical_field_bytes':24,'fits_physical_name_field':len(value)+1<=24 if value else None,
            'original_byte_budget':row['source_bytes'],'current_policy_ceiling':16,'profiles':measurements[b['id']],
            'within_all_observed_width_profiles':all(r['within_observed_envelope'] for r in measurements[b['id']]) if value else None,
            'renderer_scan_probe':renderer,'direct_draw_loop_probe':direct_scan,'scalar_expansion_copy_probe':copier,'battle_counterparts':counterparts,
            'editing_authorized':False,'unresolved':'Missing full consumer/buffer and actual-box proof; unsupported glyph also blocks item 460.'})
    roots=census(elf)
    return {'schema':1,'scope':SCOPE,'elf_sha256':sha(elf),'spack_sha256':sha(raw),
        'instruction_windows':[{'offset':a,'size':z-a,'sha256':sha(elf[a:z])} for a,z in WINDOWS],
        'items':results,'metric_profiles':profiles,'pointer_candidates':roots,
        'counts':{'blocked':len(results),'codec_supported':sum(r['codec_error'] is None for r in results),
        'within_all_observed_width_profiles':sum(r['within_all_observed_width_profiles'] is True for r in results),
        'above_observed_width_in_some_profile':sum(r['within_all_observed_width_profiles'] is False for r in results),
        'unique_related_battle_actions':len({b['id'] for r in results for b in r['battle_counterparts']}),
        'raw_pointer_load_candidates':len(roots['raw_low_immediate_load_candidates']),
        'raw_pointer_store_candidates':len(roots['raw_low_immediate_store_candidates']),
        'direct_record_getter_calls':len(roots['direct_record_getter_calls'])},
        'editing_authorized':False,'originals_modified':False,'iso_created':False,'pcsx2_executed':False,
        'limits':'Original scalar scan/copy instructions in bounded synthetic RAM. Classification-table contents and drawing are modeled; real copy destination extent and full formatter are not executed/proven. Width sums compare to original names, not actual UI boxes. Census is not full data-flow proof; no ceiling increase authorized.'}

def apply_authorized_fallback(result,current_recipe):
    """Keep the historical investigation, exclude only a bound resolved name."""
    from item_accent_fallback import validate_interface,parent_names,TARGET
    recipe_path=Path(current_recipe).resolve()
    if not recipe_path.is_relative_to(ROOT/'translations'):raise ValueError('Current recipe must be under translations/')
    recipe=json.loads(recipe_path.read_bytes());released=[]
    if 'all_minigames_release' in recipe:
        from minigames_release import validate,PARENT
        validate(recipe)
        result=apply_authorized_fallback(result,ROOT/PARENT)
        result['effective_recipe']=recipe_path.relative_to(ROOT).as_posix()
        result['effective_recipe_sha256']=sha(recipe_path.read_bytes())
        return result
    if 'screenshot_backlog_release' in recipe:
        from screenshot_backlog import validate,PARENT
        validate(recipe)
        result=apply_authorized_fallback(result,ROOT/PARENT)
        result['effective_recipe']=recipe_path.relative_to(ROOT).as_posix()
        result['effective_recipe_sha256']=sha(recipe_path.read_bytes())
        return result
    if 'tank_drinking_release' in recipe:
        from tank_drinking_gaps import validate,PARENT
        validate(recipe)
        result=apply_authorized_fallback(result,ROOT/PARENT)
        result['effective_recipe']=recipe_path.relative_to(ROOT).as_posix()
        result['effective_recipe_sha256']=sha(recipe_path.read_bytes())
        return result
    if 'credit_readability_release' in recipe:
        from credit_readability import validate,PARENT
        validate(recipe)
        result=apply_authorized_fallback(result,ROOT/PARENT)
        result['effective_recipe']=recipe_path.relative_to(ROOT).as_posix()
        result['effective_recipe_sha256']=sha(recipe_path.read_bytes())
        return result
    if 'title_menu_release' in recipe:
        from title_menu_revision import validate,PARENT
        validate(recipe)
        result=apply_authorized_fallback(result,ROOT/PARENT)
        result['effective_recipe']=recipe_path.relative_to(ROOT).as_posix()
        result['effective_recipe_sha256']=sha(recipe_path.read_bytes())
        return result
    if 'capture_release' in recipe:
        from capture_release import validate_interface as validate_capture,PARENT_UI as CAPTURE_PARENT
        validate_capture(recipe)
        result=apply_authorized_fallback(result,ROOT/CAPTURE_PARENT)
        result['effective_recipe']=recipe_path.relative_to(ROOT).as_posix()
        result['effective_recipe_sha256']=sha(recipe_path.read_bytes())
        return result
    if 'screen_followup_release' in recipe:
        from screen_followup import validate_interface as validate_followup,PARENT as FOLLOWUP_PARENT
        validate_followup(recipe)
        result=apply_authorized_fallback(result,ROOT/FOLLOWUP_PARENT)
        result['effective_recipe']=recipe_path.relative_to(ROOT).as_posix()
        result['effective_recipe_sha256']=sha(recipe_path.read_bytes())
        return result
    if 'observed_menu_release' in recipe:
        from observed_menu_translation import validate_interface as validate_observed,PARENT as OBSERVED_PARENT
        validate_observed(recipe)
        result=apply_authorized_fallback(result,ROOT/OBSERVED_PARENT)
        result['effective_recipe']=recipe_path.relative_to(ROOT).as_posix()
        result['effective_recipe_sha256']=sha(recipe_path.read_bytes())
        return result
    if 'npc_and_choice_release' in recipe:
        from npc_menu_revision import validate_interface as validate_npc,PARENT as NPC_PARENT
        validate_npc(recipe)
        result=apply_authorized_fallback(result,ROOT/NPC_PARENT)
        result['effective_recipe']=recipe_path.relative_to(ROOT).as_posix()
        result['effective_recipe_sha256']=sha(recipe_path.read_bytes())
        return result
    if 'battle_effect_release' in recipe:
        from battle_effect_atlas import validate_interface as validate_effects,PARENT as EFFECT_PARENT
        validate_effects(recipe)
        result=apply_authorized_fallback(result,ROOT/EFFECT_PARENT)
        result['effective_recipe']=recipe_path.relative_to(ROOT).as_posix()
        result['effective_recipe_sha256']=sha(recipe_path.read_bytes())
        return result
    if 'approved_weapons' in recipe:
        from approved_weapon_names import validate_interface as validate_weapons,PARENT as WEAPON_PARENT
        validate_weapons(recipe)
        result=apply_authorized_fallback(result,ROOT/WEAPON_PARENT)
        result['effective_recipe']=recipe_path.relative_to(ROOT).as_posix()
        result['effective_recipe_sha256']=sha(recipe_path.read_bytes())
        return result
    if 'exit_wording_revision' in recipe:
        from exit_wording_revision import validate_interface as validate_wording,PARENT as WORDING_PARENT
        validate_wording(recipe)
        result=apply_authorized_fallback(result,ROOT/WORDING_PARENT)
        result['effective_recipe']=recipe_path.relative_to(ROOT).as_posix()
        result['effective_recipe_sha256']=sha(recipe_path.read_bytes())
        return result
    if 'satcom_gap_release' in recipe:
        from satcom_observed_gaps import validate_interface as validate_gaps,PARENT as GAPS_PARENT
        validate_gaps(recipe)
        result=apply_authorized_fallback(result,ROOT/GAPS_PARENT)
        result['effective_recipe']=recipe_path.relative_to(ROOT).as_posix()
        result['effective_recipe_sha256']=sha(recipe_path.read_bytes())
        result['unchanged_names_overlay']='satcom-observed-gaps-and-fixed-exit-labels-v001'
        return result
    if 'battle_atlas_release' in recipe:
        from battle_menu_atlas import validate_interface as validate_combat,PARENT as COMBAT_PARENT
        parent,_=validate_combat(recipe)
        result=apply_authorized_fallback(result,ROOT/COMBAT_PARENT)
        result['effective_recipe']=recipe_path.relative_to(ROOT).as_posix()
        result['effective_recipe_sha256']=sha(recipe_path.read_bytes())
        result['unchanged_names_overlay']='battle-compressed-tim2-fixed-labels-v001'
        return result
    if 'remaining_name_release' in recipe:
        from remaining_item_name_release import validate_interface as validate_remaining,load as load_remaining
        parent=validate_remaining(recipe);manifest,_=load_remaining(recipe['remaining_name_release'])
        result=apply_authorized_fallback(result,ROOT/'translations/interface-v053.json')
        from item_names import compile_names
        compiled={p['id']:p for p in compile_names(SOURCE.read_bytes(),recipe['item_names'])[0]}
        for row in manifest['items']:
            if compiled[row['id']]['after'].split(b'\0')[0]!=encode(row['translation']):raise ValueError('Remaining name not compiled')
        resolved={r['id'] for r in manifest['items']}
        if resolved!={r['id'] for r in result['items']}:raise ValueError('Remaining ledger IDs differ')
        result['items']=[]
        for key in ('blocked','codec_supported','within_all_observed_width_profiles','above_observed_width_in_some_profile','unique_related_battle_actions'):result['counts'][key]=0
        result['effective_recipe']=recipe_path.relative_to(ROOT).as_posix();result['effective_recipe_sha256']=sha(recipe_path.read_bytes())
        result['resolved_remaining_name_revisions']=[{'id':r['id'],'translation':r['translation'],'encoded_bytes':len(encode(r['translation'])),'compiled':True} for r in manifest['items']]
        return result
    if 'large_name_release' in recipe:
        from large_item_name_release import validate_interface as validate_release,parent_names as release_parent,load
        parent=validate_release(recipe);validate_interface(parent)
        names_parent=parent_names(release_parent(recipe['item_names']))
        manifest,_=load(recipe['large_name_release']);released=manifest['items']
    else:
        validate_interface(recipe);names_parent=parent_names(recipe['item_names'])
    baseline=json.loads((ROOT/RECIPE).read_bytes())
    if names_parent!=baseline['item_names']:raise ValueError('Other current names differ from diagnostic baseline')
    from item_names import compile_names
    patches,_=compile_names(SOURCE.read_bytes(),recipe['item_names'])
    resolved=next(p for p in patches if p['id']=='item.name.0460')
    if resolved['after']!=encode(TARGET)+b'\0\0':raise ValueError('Authorized fallback not compiled')
    result=json.loads(json.dumps(result))
    byid={p['id']:p for p in patches}
    for row in released:
        if byid[row['id']]['after'].split(b'\0')[0]!=encode(row['translation']):raise ValueError('Large-name revision not compiled')
    excluded={'item.name.0460'}|{r['id'] for r in released}
    result['items']=[r for r in result['items'] if r['id'] not in excluded]
    result['counts'].update(blocked=len(result['items']),codec_supported=sum(r['codec_error'] is None for r in result['items']),
        within_all_observed_width_profiles=sum(r['within_all_observed_width_profiles'] is True for r in result['items']),
        above_observed_width_in_some_profile=sum(r['within_all_observed_width_profiles'] is False for r in result['items']),
        unique_related_battle_actions=len({b['id'] for r in result['items'] for b in r['battle_counterparts']}))
    result['effective_recipe']=recipe_path.relative_to(ROOT).as_posix()
    result['effective_recipe_sha256']=sha(recipe_path.read_bytes())
    result['resolved_authorized_fallbacks']=[{'id':'item.name.0460','translation':TARGET,'encoded_bytes':14,'compiled':True}]
    result['resolved_large_name_revisions']=[{'id':r['id'],'translation':r['translation'],'encoded_bytes':len(encode(r['translation'])),'compiled':True} for r in released]
    return result


def run(output,summary=None,*,current_recipe=None):
    output=Path(output).resolve()
    if not output.is_relative_to(ROOT/'work'):raise ValueError('Capacity detailed output must be under work/')
    if output.exists() and json.loads(output.read_bytes()).get('scope')!=SCOPE:raise ValueError('Refuse unrelated capacity output')
    if summary is not None:
        summary=Path(summary).resolve()
        if not summary.is_relative_to(ROOT/'reports') or summary.exists():raise ValueError('Use new capacity metadata summary under reports/')
    recipe=json.loads((ROOT/RECIPE).read_bytes());decisions=json.loads((ROOT/DECISIONS).read_bytes())
    result=investigate(SOURCE.read_bytes(),original(RESOURCE),recipe,decisions)
    result.update(recipe=RECIPE,recipe_sha256=sha((ROOT/RECIPE).read_bytes()),decisions=DECISIONS,decisions_sha256=sha((ROOT/DECISIONS).read_bytes()))
    if current_recipe is not None:result=apply_authorized_fallback(result,current_recipe)
    output.parent.mkdir(parents=True,exist_ok=True);output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    if summary is not None:
        compact={k:v for k,v in result.items() if k!='pointer_candidates'}
        for row in compact['items']:
            row['renderer_scan_probe']={k:v for k,v in row['renderer_scan_probe'].items() if k!='glyph_codes'} if row['renderer_scan_probe'] else None
            row['direct_draw_loop_probe']={k:v for k,v in row['direct_draw_loop_probe'].items() if k!='glyph_codes'} if row['direct_draw_loop_probe'] else None
        summary.write_text(json.dumps(compact,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    return result['counts']

if __name__=='__main__':
    p=argparse.ArgumentParser(description='Investigar os 16 nomes bloqueados sem alterar jogo ou liberar edição')
    p.add_argument('--output',type=Path,default=ROOT/'work/capacidade-nomes-atual.json');p.add_argument('--summary',type=Path)
    p.add_argument('--current-recipe',type=Path,help='Excluir a exceção de acento já compilada por receita vinculada')
    a=p.parse_args();print(json.dumps(run(a.output,a.summary,current_recipe=a.current_recipe)))
