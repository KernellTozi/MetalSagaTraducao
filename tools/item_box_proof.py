"""Bounded execution of original window geometry and shop column arithmetic.

Original scalar MIPS instructions, synthetic RAM, refresh callback intercepted.
No GPU, allocator, save loading or complete game execution is modeled.
"""
import argparse,json,struct,mmap
from pathlib import Path
from dialogue import ROOT,sha
from interface_text import SOURCE
from glyph_spacing import ORIGINAL_SHA
from item_name_boxes import IDS, investigate as measurements
from name_source_paths import DELTA

WINDOWS=((0x1b6268,0x1b62d8),(0x1b6170,0x1b6224),(0x43720,0x43734),
         (0x1b63f8,0x1b6448),(0x1b62d8,0x1b6390),
         (0x4f898,0x4f8d0),(0x4fa98,0x4fb1c))


def scalar(elf,start,regs,regions,stop,handlers=None):
    if sha(elf)!=ORIGINAL_SHA:raise ValueError('Geometry ELF differs')
    pc=start+DELTA;pending=None;visited=set();fp={}
    def access(at,size,value=None):
        for base,data,writable in regions:
            if base<=at and at+size<=base+len(data):
                off=at-base
                if value is None:return int.from_bytes(data[off:off+size],'little')
                if not writable:raise ValueError('Geometry write to immutable region')
                data[off:off+size]=(value&((1<<(8*size))-1)).to_bytes(size,'little');return
        raise ValueError(f'Geometry access outside bounded RAM {at:x}/{size}')
    for steps in range(10000):
        if pc==stop:return {'registers':regs,'instructions':steps,'offsets':sorted(visited)}
        if handlers and handlers(pc,regs,access):pc=regs[31];continue
        at=pc-DELTA
        if not any(a<=at<z for a,z in WINDOWS):raise ValueError(f'Geometry escaped code {at:x}')
        visited.add(at);w=struct.unpack_from('<I',elf,at)[0]
        op,rs,rt,rd,fn=w>>26,w>>21&31,w>>16&31,w>>11&31,w&63
        u=w&65535;n=u if u<32768 else u-65536
        old,pending,nextpc=pending,None,pc+4
        signed=lambda v:v if v<0x80000000 else v-0x100000000
        if op==0:
            if fn in (33,45):regs[rd]=regs[rs]+regs[rt]
            elif fn in (35,47):regs[rd]=regs[rs]-regs[rt]
            elif fn==37:regs[rd]=regs[rs]|regs[rt]
            elif fn==36:regs[rd]=regs[rs]&regs[rt]
            elif fn==42:regs[rd]=int(signed(regs[rs])<signed(regs[rt]))
            elif fn==24:regs[rd]=regs[rs]*regs[rt] # R5900 MULT rd,rs,rt
            elif fn==0:regs[rd]=regs[rt]<<(w>>6&31)
            elif fn==3:regs[rd]=signed(regs[rt])>>(w>>6&31)
            elif fn in (8,9):
                target=regs[rs]
                if fn==9:regs[rd]=pc+8
                pending=target
            else:raise ValueError(f'Geometry unsupported SPECIAL {w:08x}')
        elif op==9:regs[rt]=regs[rs]+n
        elif op==12:regs[rt]=regs[rs]&u
        elif op==13:regs[rt]=regs[rs]|u
        elif op==15:regs[rt]=u<<16
        elif op in (30,33,35,55):
            value=access((regs[rs]+n)&0xffffffff,{30:16,33:2,35:4,55:8}[op])
            regs[rt]=value-65536 if op==33 and value>=32768 else value
        elif op in (31,41,43,63):access((regs[rs]+n)&0xffffffff,{31:16,41:2,43:4,63:8}[op],regs[rt])
        elif op==17 and rs==4:fp[rd]=regs[rt] # bit transfer only, no floating arithmetic
        elif op==57:access((regs[rs]+n)&0xffffffff,4,fp[rt])
        elif op in (4,5,20,21):
            take=regs[rs]==regs[rt] if op in (4,20) else regs[rs]!=regs[rt]
            if op in (20,21) and not take:nextpc=pc+8
            else:pending=pc+4+n*4 if take else pc+8
        elif op==1 and rt==0:pending=pc+4+n*4 if signed(regs[rs])<0 else pc+8
        elif op==3:regs[31]=pc+8;pending=(w&0x3ffffff)<<2
        else:raise ValueError(f'Geometry unsupported instruction {w:08x}')
        regs=[v&0xffffffff for v in regs];regs[0]=0;pc=old if old is not None else nextpc
    raise ValueError('Geometry instruction budget exceeded')


def panel(elf,x=80,y=144,width=272,height=208,style=0):
    if sha(elf)!=ORIGINAL_SHA:raise ValueError('Panel ELF differs')
    obj=bytearray(0x280);stack=bytearray(0x400);out=bytearray(16)
    struct.pack_into('<I',obj,0x10,0x409680)
    # Constructor with style -1: concrete skin pointer and style index from 2b5448.
    if style not in (0,1):raise ValueError('Unknown original panel style')
    struct.pack_into('<I',obj,0x238,0x43ced0 if style==0 else 0x43cf60);struct.pack_into('<h',obj,0x25e,style)
    if struct.unpack_from('<hI',elf,0x409680-DELTA+0x58)[0]!=0:raise ValueError('Panel adjustment differs')
    target=struct.unpack_from('<I',elf,0x409680-DELTA+0x5c)[0]
    if target!=0x2b5268:raise ValueError('Panel method differs')
    refresh=struct.unpack_from('<I',elf,0x409680-DELTA+0x8c)[0];calls=[]
    def handler(pc,regs,access):
        if pc!=refresh:return False
        calls.append(pc);return True
    regions=[(DELTA,elf,False),(0x600000,obj,True),(0x700000,stack,True),(0x710000,out,True)]
    regs=[0]*32;regs[4:9]=[0x600000,x,y,width,height];regs[29]=0x700200;regs[31]=0x7ffff0
    a=scalar(elf,target-DELTA,regs,regions,0x7ffff0,handler)
    regs=[0]*32;regs[4:9]=[0x600000,0x710000,0x710004,0x710008,0x71000c];regs[31]=0x7ffff0
    b=scalar(elf,0x1b62d8,regs,regions,0x7ffff0)
    result=list(struct.unpack('<4i',out))
    if result!=[x,y,width,height] or len(calls)!=1:raise ValueError('Panel geometry roundtrip differs')
    return {'requested_and_returned':result,'style':style,'stored_rectangle':list(struct.unpack_from('<4i',obj,0x14)),
            'setter_instructions':a['instructions'],'getter_instructions':b['instructions'],
            'refresh_callback_intercepted':hex(refresh),'final_draw_origin_route':[0x40060,0x40078,0x400c8,0x400d8],
            'gpu_clipping_executed':False}


def shop(elf):
    obj=bytearray(0xa0);base=0x600000
    struct.pack_into('<II',obj,0x58,22,17)
    regs=[0]*32;regs[4]=base;regs[31]=0x7ffff0
    regions=[(DELTA,elf,False),(base,obj,True)]
    a=scalar(elf,0x4f898,regs,regions,0x7ffff0)
    regs=[0]*32;regs[4:9]=[base,99999999,1,1,0xffffffff];regs[31]=0x7ffff0
    b=scalar(elf,0x4fa98,regs,regions,0x7ffff0)
    width=struct.unpack_from('<I',obj,0x2c)[0];price=struct.unpack_from('<I',obj,0x8c)[0]
    if (width,price)!=(374,264):raise ValueError('Shop row/price columns differ')
    return {'font_size':22,'width_parameter':17,'logical_row_width':width,'name_origin':22,
            'eight_digit_price_origin':price,'name_budget_before_price':price-22,
            'width_instructions':a['instructions'],'column_instructions':b['instructions'],
            'price_value_used':99999999,'R5900_mult_destination_executed':True}


def investigate():
    from build_translation_pilot import load_draft,compile_draft
    from reinsertion import SOURCE as MAP
    from scene_name_fields import message_budgets
    elf=SOURCE.read_bytes();r=measurements(elf)
    # Bind caller constants and class construction, not only synthetic inputs.
    words={0x1b3354:0x0c000000|(0x2b4f98>>2),0x1b3358:0x2405ffff,
           0x1b5fbc:0x24639680,0x1b5fc4:0xae030010,
           0x1b645c:0x2442ced0,0x1b6470:0x2442cf60,
           0x118b30:0x24070140,0x11d090:0x24070120,
           0x1d5298:0x24070016,0x1d52a0:0x24080011,
           0x11d378:0x0c000000|(0x326a28>>2),0x11d3ac:0x0c000000|(0x20f198>>2),
           0x118808:0x0c000000|(0x20f198>>2)}
    for at,w in words.items():
        if struct.unpack_from('<I',elf,at)[0]!=w:raise ValueError(f'UI caller differs at {at:x}')
    recipe=json.loads((ROOT/'translations/interface-v053.json').read_bytes())
    draft,bindings=load_draft(ROOT/recipe['base_dialogue_draft'])
    with MAP.open('rb') as f,mmap.mmap(f.fileno(),0,access=mmap.ACCESS_READ) as data:
        doc,_,report=compile_draft(data,draft)
    if not report['valid']:raise ValueError('Dialogue base invalid')
    budgets=message_budgets(doc,item_bytes=19)
    budgets['method']='Independent item outputs conservatively bounded at 19 bytes/cells; N0 conditional valid field bound remains 31. No template or token changes.'
    panel_cases=[panel(elf),panel(elf,0,0),panel(elf,120,80,320,240,1),panel(elf,336,144,288,68)]
    s=shop(elf)
    for row in r['items']:
        row['shop_name_margin_before_price']=s['name_budget_before_price']-max(row['logical_advances_size22_modes012'])
        if row['shop_name_margin_before_price']<22:raise ValueError('Name reaches shop price guard')
    return {'schema':1,'scope':'nine-approved-item-names-ui-evidence-v002',
            'elf_sha256':sha(elf),'parent_recipe':'translations/interface-v053.json',
            'parent_sha256':sha((ROOT/'translations/interface-v053.json').read_bytes()),
            'windows':[{'offset':a,'size':z-a,'sha256':sha(elf[a:z])} for a,z in WINDOWS],
            'caller_instruction_words':[{'offset':a,'word':f'{w:08x}'} for a,w in words.items()],
            'panel_cases':panel_cases,'shop':s,'items':r['items'],'budgets':budgets,
            'observed_list_rectangles':[
                {'context':'inventory item list','width':320,'offset':0x118b30,'name_widget_calls':[0x1187f0,0x118808]},
                {'context':'battle action list','width':288,'offset':0x11d090,'name_widget_calls':[0x11d378,0x11d3ac]}],
            'legacy_scene_dependency_proof':'reports/prova-seis-nomes-v007.json',
            'legacy_scene_dependency_sha256':sha((ROOT/'reports/prova-seis-nomes-v007.json').read_bytes()),
            'limits':'Source-bound original scalar geometry plus compiled message budgets. Refresh/GPU/printf and complete list rendering are not executed. Representative known menu paths support an exact opt-in test build, not universal visual approval or safety for malformed game state.'}


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,default=ROOT/'work/prova-nove-nomes-v002.json');a=p.parse_args()
    out=a.output.resolve()
    if not out.is_relative_to(ROOT/'work'):raise ValueError('Use work output')
    if out.exists() and json.loads(out.read_bytes()).get('scope')!='nine-approved-item-names-ui-evidence-v002':raise ValueError('Unrelated output')
    r=investigate();out.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'names':len(r['items']),'page_max':r['budgets']['maximum_page_content_cells'],'body_max':r['budgets']['maximum_body_bytes'],'shop_margin_min':min(x['shop_name_margin_before_price'] for x in r['items'])}))
