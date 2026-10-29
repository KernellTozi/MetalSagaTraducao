"""Read-only original menu formatter, with explicitly modeled copy helpers."""
import argparse
import json
import re
import struct
from pathlib import Path
from dialogue import ROOT,sha
from interface_text import SOURCE
from glyph_spacing import ORIGINAL_SHA
from gfi import encode,decode
from item_names import original,RESOURCE
from item_name_buffers import name_table,RECIPE
from control_b15 import execute_argument
from spack_ui import execute_byte_length
from name_source_paths import run,DELTA

SCOPE='additional-name-formatter-bounds-read-only-v006'
START,END=0x10e0e8,0x10e27c


def evidence(elf):
    if sha(elf)!=ORIGINAL_SHA:raise ValueError('Additional formatter ELF differs')
    expected={0x7ef08:0x26040130,0x74ff0:0x27bdffe0,0x75014:0x24060020,
              0x7f6ac:0x0c0c956d,0x7f6b0:0x24840010,
              0x123ec8:0x27b70040,0x123f48:0x03a0202d,
              0x123f64:0x02e0202d,0x123f6c:0x27a40080}
    for at,w in expected.items():
        if struct.unpack_from('<I',elf,at)[0]!=w:raise ValueError('Formatter evidence instruction differs')
    windows=((START,END),(0x74ff0,0x75034),(0x7f6a0,0x7f6cc),
             (0x123ec8,0x123ee0),(0x123f44,0x123f80))
    return {'windows':[{'offset':a,'size':z-a,'sha256':sha(elf[a:z])} for a,z in windows],
        'actor_name_field':{'bytes_initialized':32,'following_field_offset':32,
            'setter_uses_unbounded_strcpy':True,'runtime_nul_within_field_proven':False,
            'conditional_valid_nul_terminated_content_max_bytes':31},
        'two_observed_scratch_areas':[
            {'call_offset':0x123f50,'destination_sp_offset':0,'next_area_sp_offset':64,'bytes':64},
            {'call_offset':0x123f60,'destination_sp_offset':64,'next_area_sp_offset':128,'bytes':64}],
        'limits':'Static separation of adjacent destinations, not a C array declaration or proof of complete incoming texts. The 32-byte initialized name field alone does not guarantee all callers bound strcpy.'}


def format_text(elf,table,text,name,capacity=64):
    evidence(elf)
    from item_names import ITEM_COUNT,STRIDE
    if len(table)!=ITEM_COUNT*STRIDE or capacity!=64:raise ValueError('Use full item table and witnessed 64-byte separation')
    source=bytearray(encode(text)+b'\0');before=bytes(source)
    rest=re.sub(rb'%(?:I[0-9]+|N0(?![0-9$]))',b'',source[:-1])
    if b'%' in rest or any(b<32 for b in rest):raise ValueError('Only plain text, pipes, literal I and literal N0 in this probe')
    name_raw=encode(name)+b'\0'
    if len(name_raw)>32:raise ValueError('Conditional name exceeds the observed 32-byte field')
    if any(b<32 for b in name_raw[:-1]):raise ValueError('Plain N0 name required')
    dest=bytearray(b'\xa5'*capacity);stack=bytearray(b'\xa5'*0x200)
    globals_=bytearray(0x900)
    struct.pack_into('<I',globals_,0x868,0x640000)
    struct.pack_into('<I',globals_,0x30c,0x680000)
    regions=[(0x600000,source,True),(0x610000,dest,True),(0x640000,table,False),
             (0x680000,name_raw,False),(0x6ffe00,stack,True),(0x475280,globals_,False)]
    regs=[0]*32;regs[4]=0x610000;regs[5]=0x600000;regs[29]=0x700000;regs[31]=0x7ffff0
    initial=regs.copy();items=[];helper_calls=[]
    def cstring(access,at):
        value=bytearray()
        for i in range(4096):
            b=access(at+i,1)
            if not b:return bytes(value)
            value.append(b)
        raise ValueError('CString probe limit exceeded')
    def handlers(pc,r,access):
        if pc==0x296080:
            b=r[4]&255
            if b==0x82:value=-1
            elif 32<=b<=127:value=1
            else:raise ValueError('Unsupported formatter classification')
            r[2]=value&0xffffffff
        elif pc==0x2b4a30:
            pos=r[4]-0x600000
            if not 0<=pos<len(source):raise ValueError('Formatter argument outside source')
            arg=execute_argument(elf,bytes(source[pos:]),[])
            value=arg['value'];kind=source[pos-1:pos]
            if kind==b'I':
                if not 0<=value<ITEM_COUNT or 0 not in table[value*STRIDE:value*STRIDE+24]:raise ValueError('Invalid item name field')
                items.append(value)
            elif kind!=b'N' or value!=0:raise ValueError('Unreviewed formatter token')
            access(r[5],4,value);r[2]=r[4]+arg['consumed']
        elif pc==0x3255b4:
            raw=cstring(access,r[5])
            for i,b in enumerate(raw+b'\0'):access(r[4]+i,1,b)
            r[2]=r[4];helper_calls.append('strcpy-modeled-with-bounded-memory')
        elif pc==0x3256cc:
            raw=cstring(access,r[4]);r[2]=execute_byte_length(elf,raw)
            helper_calls.append('strlen-original-scalar-reader')
        elif pc==0x325b90:
            for i in range(r[6]):access(r[4]+i,1,access(r[5]+i,1))
            r[2]=r[4];helper_calls.append('two-byte-copy-modeled')
        else:return False
        return True
    result=run(elf,START,((START,END),),regs,regions,0x7ffff0,handlers=handlers)
    if any(result['registers'][r]!=initial[r] for r in (*range(16,24),29,31)):raise ValueError('Formatter saved registers differ')
    if bytes(source)!=before.replace(b'|',b'\n'):raise ValueError('Formatter altered unexpected input bytes')
    if 0 not in dest:raise ValueError('Formatter destination NUL missing')
    value=bytes(dest).split(b'\0')[0]
    return {'text':decode(value),'output_hex':value.hex(),'output_bytes':len(value),
            'capacity_bytes':capacity,'nul_written':True,'lookup_item_ids':items,
            'source_pipes_changed_to_lf':before!=bytes(source),'source_other_bytes_unchanged':True,
            'callee_saved':True,'helper_calls':helper_calls,'original_instructions':result['instructions'],
            'copy_helpers_modeled':True,'upstream_inputs_proven':False}


def investigate():
    elf=SOURCE.read_bytes();recipe=json.loads((ROOT/RECIPE).read_bytes())
    decisions=json.loads((ROOT/'translations/revisao-humana-itens-v001.json').read_bytes())
    table,targets=name_table(elf,original(RESOURCE),recipe,decisions);cases=[]
    for index,target in targets.items():
        for name in ('Nina','A'*31,'é'*15):
            text=f'Achou %I{index}|%N0!';r=format_text(elf,table,text,name)
            if r['text']!='Achou '+target+'\n'+name+'!':raise ValueError('Additional formatter output differs')
            cases.append({'item_id':index,'name_bytes':len(encode(name)),**r})
    return {'schema':1,'scope':SCOPE,'evidence':evidence(elf),'cases':cases,'case_count':len(cases),
        'mail_dependency_audit':audit_mail_dependencies(elf),
        'consumer_input_audit':audit_consumer_inputs(elf),
        'editing_authorized':False,'new_translations':0,'iso_created':False,'pcsx2_executed':False,
        'limits':'Original formatter with modeled classification, strcpy and two-byte copy. strlen and numeric argument reader execute original scalar instructions. Three supplied names are conditional, not recovered scene identities. The observed-corpus dependency audit is separate from runtime name lifecycle, arbitrary mutations, indirect aliases and universal memory safety.'}


def audit_mail_dependencies(elf):
    """Resolve the first two call inputs through the existing original getter."""
    from spack_satcom import compile_satcom,parse_table,execute_mail_getter,TABLES
    recipe_path=ROOT/'translations/interface-v052.json';recipe=json.loads(recipe_path.read_bytes())
    raw=original(RESOURCE);patches,_=compile_satcom(elf,recipe['satcom_records'])
    current=bytearray(raw)
    for p in patches:current[p['offset']:p['offset']+len(p['after'])]=p['after']
    original_rows=parse_table(raw,'mail');current_rows=parse_table(current,'mail',translated=True)
    _,base,size,count=TABLES['mail'];rows=[]
    for index in range(count):
        for data,parsed in ((raw,original_rows),(current,current_rows)):
            ptrs=execute_mail_getter(elf,bytes(data[base:base+size]),index)
            for field in ('sender','subject'):
                expected=parsed[index]['offset']-base+parsed[index]['fields'][field]['relative']
                if ptrs[field]!=expected:raise ValueError('Mail dependency getter disagrees with parsed field')
        for field in ('sender','subject'):
            a=original_rows[index]['fields'][field]['raw'];b=current_rows[index]['fields'][field]['raw']
            if b'%I' in a or b'%I' in b:raise ValueError('Unexpected item reference in resolved mail header')
            rows.append({'mail_id':index,'field':field,'original_sha256':sha(a),'current_sha256':sha(b),
                         'original_bytes':len(a),'current_bytes':len(b),'item_references':0})
    windows=((0x123ecc,0x123ed8),(0x123f44,0x123f68),(0x71ae0,0x71b70))
    return {'recipe':'translations/interface-v052.json','recipe_sha256':sha(recipe_path.read_bytes()),
        'resolved_direct_calls':[0x123f50,0x123f60],'mail_records':count,'fields':len(rows),
        'original_getter_executions':count*2,'rows':rows,
        'instruction_windows':[{'offset':a,'size':z-a,'sha256':sha(elf[a:z])} for a,z in windows],
        'item_name_growth_affects_these_two_inputs':False,'all_other_formatting_capacity_proven':False,
        'remaining_direct_calls_to_trace':7,
        'limits':'Sender and subject only, original and current bounded mail catalogue. Zero I dependencies removes these paths from this six-item growth question; it is not a universal buffer safety claim or exclusion of computed calls.'}


def audit_consumer_inputs(elf):
    """Source-bound dependency exclusion for observed direct caller corpora.

    This is not a general input-size/whole-call-graph proof. No input strings
    are translated, filtered or shortened by this dependency audit.
    """
    from spack_satcom import compile_satcom,parse_table
    from interface_resources import compile_resources,DIARY,original as read_resource
    from diary import fields
    recipe_path=ROOT/'translations/interface-v052.json';recipe=json.loads(recipe_path.read_bytes())
    raw=original(RESOURCE);sat=bytearray(raw)
    patches,_=compile_satcom(elf,recipe['satcom_records'])
    for p in patches:sat[p['offset']:p['offset']+len(p['after'])]=p['after']
    rows=[]
    for kind in ('mail','wanted'):
        old=parse_table(raw,kind);new=parse_table(sat,kind,translated=True)
        for a,b in zip(old,new):
            for field in (('sender','subject','body') if kind=='mail' else ('body',)):
                before=a['fields'][field]['raw'];after=b['fields'][field]['raw']
                if b'%I' in before or b'%I' in after:raise ValueError('Item dependency found in resolved Satcom corpus')
                rows.append({'id':f'spack.{kind}.{a["id"]:03d}.{field}',
                             'source_sha256':sha(before),'current_sha256':sha(after),'item_references':0})
    original_diary=read_resource(DIARY);current_diary=bytearray(original_diary)
    resource_patches,_=compile_resources(elf,recipe)
    for p in resource_patches:
        if p['resource']==DIARY:current_diary[p['offset']:p['offset']+len(p['after'])]=p['after']
    old_fields=fields(original_diary);new_fields=fields(current_diary)
    for a,b in zip(old_fields,new_fields):
        before=original_diary[a['offset']:a['offset']+a['capacity']+1].split(b'\0')[0]
        after=bytes(current_diary[b['offset']:b['offset']+b['capacity']+1]).split(b'\0')[0]
        if b'%I' in before or b'%I' in after:raise ValueError('Item dependency found in resolved diary corpus')
        rows.append({'id':f'diary.{a["record"]:03d}.{a["field"]}',
                     'source_sha256':sha(before),'current_sha256':sha(after),'item_references':0})
    if len(rows)!=299 or len({r['id'] for r in rows})!=299:raise ValueError('Additional formatter corpus coverage differs')
    call_map={0x123f50:'mail.sender',0x123f60:'mail.subject',0x124310:'mail.body',
              0x1243bc:'mail.sender',0x1243dc:'mail.subject',0x129474:'diary.title',
              0x129684:'diary.title',0x129754:'diary.body',0x12c1f8:'wanted.body'}
    # Exact direct-only helper chain: mail compositor receives the descriptor
    # produced by the getter, with sender at +8 and subject at +12.
    from interface_text import sections
    part=sections(elf)['.text'];word=0x0c000000|((0x124358+DELTA)>>2)
    calls=[at for at in range(part['offset'],part['offset']+part['size'],4)
           if struct.unpack_from('<I',elf,at)[0]==word]
    if calls!=[0x124250] or elf[0x32d150:0x32d15a]!=b'diary.dat\0':
        raise ValueError('Mail compositor or diary resource chain differs')
    windows=((0x123eb4,0x123ed8),(0x124128,0x124138),(0x124244,0x124268),
             (0x12430c,0x124328),(0x124358,0x1243e4),(0x128990,0x1289b0),
             (0x129420,0x129478),(0x12967c,0x12968c),(0x129750,0x12975c),
             (0x129580,0x1295bc),(0x129a68,0x129acc),
             (0x12c138,0x12c154),(0x12c1f4,0x12c210))
    return {'recipe_sha256':sha(recipe_path.read_bytes()),'unique_fields':299,
        'mail_fields':123,'wanted_bodies':40,'diary_fields':136,'rows':rows,
        'direct_call_input_classes':[{'call_offset':k,'input_class':v} for k,v in call_map.items()],
        'instruction_windows':[{'offset':a,'size':z-a,'sha256':sha(elf[a:z])} for a,z in windows],
        'item_name_growth_affects_observed_corpora':False,'unresolved_direct_input_classes':0,
        'all_runtime_mutations_or_indirect_calls_proven':False,
        'limits':'Original/current compiled bounded mail, wanted body and diary fields have no I token. This excludes these observed corpus paths from the six-item growth dependency; it is not a universal memory safety or future runtime-text mutation proof. Native diary bytes are scanned and preserved, not decoded or edited.'}


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,default=ROOT/'work/limites-formatador-atual.json')
    out=p.parse_args().output.resolve()
    if not out.is_relative_to(ROOT/'work'):raise ValueError('Keep formatter details under work/')
    if out.exists() and json.loads(out.read_bytes()).get('scope')!=SCOPE:raise ValueError('Refuse unrelated formatter output')
    r=investigate();out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'cases':r['case_count'],'editing_authorized':False}))
