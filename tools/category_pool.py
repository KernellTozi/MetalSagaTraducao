"""Same-size category string pool with source-bound pointer consumers."""
import struct
from dialogue import sha
from gfi import encode
from interface_text import references,sections
from glyph_spacing import ORIGINAL_SHA,DELTA

START=0x349248
END=0x349290
NAMES={'Unknown':'Desconhecidos','Bio':'Bio','Cyber':'Cyber','Machine':'Máquinas',
       'Vehicle':'Veículos','Outlaw':'Alvos','Normal':'Normal','Stealth':'Furtivo','Shelter':'Abrigo'}
BANKS=(tuple(range(START,END,8)),tuple(range(0x349818,0x349848,8)),tuple(range(0x349e70,0x349ea0,8)))
# The first table is copied as eleven pointers, the second is indexed by 4.
# The final table is constructed by six immediate pointer loads into stack cells.
WINDOWS=((0xe6478,0xe64dc),(0xe6528,0xe65b0),(0x12b0b0,0x12b120),
         (0x12b600,0x12b660),(0x1d8d50,0x1d8e20))


def derive(elf,parents):
    if sha(elf)!=ORIGINAL_SHA:raise ValueError('Category ELF source differs')
    refs=references(elf,sections(elf));out=bytearray();pointers={};records=[]
    for source,target in NAMES.items():
        pointers[source]=START+DELTA+len(out)
        out.extend(encode(target)+b'\0')
    if len(out)>END-START:raise ValueError('Category pool overflow')
    out.extend(bytes(END-START-len(out)))
    pool={'id':'final.categories.pool','resource':'SLUS_212.93','offset':START,
          'before':elf[START:END],'after':bytes(out)}
    absorbed=[p for p in parents if p['resource']=='SLUS_212.93' and
              max(START,p['offset'])<min(END,p['offset']+len(p['before']))]
    if any(not START<=p['offset']<p['offset']+len(p['before'])<=END for p in absorbed):
        raise ValueError('Category pool partially overlaps inherited patch')
    patches=[pool];seen=set()
    for bank_index,bank in enumerate(BANKS):
        for at in bank:
            source=elf[at:at+8].split(b'\0')[0].decode('ascii')
            if source not in NAMES:raise ValueError('Category bank label differs')
            old=at+DELTA;target=pointers[source]
            uses=refs.get(old,[])
            if not uses:raise ValueError('Category source has no known consumer')
            if bank_index<2 and any(r['kind']!='data-pointer' for r in uses):
                raise ValueError('Category data bank has unexpected direct consumer')
            # Independently census absolute words throughout the entire ELF.
            hits={p for p in range(0,len(elf)-3,4) if struct.unpack_from('<I',elf,p)[0]==old}
            data_uses={r['offset'] for r in uses if r['kind']=='data-pointer'}
            if hits!=data_uses:raise ValueError('Additional absolute category pointer')
            if bank_index==2 and len(uses)!=1:raise ValueError('Stack category consumer count differs')
            for ref in uses:
                if ref['kind']=='data-pointer':
                    pos=ref['offset'];before=elf[pos:pos+4];after=struct.pack('<I',target)
                elif ref['kind']=='lui-immediate-candidate':
                    hi=struct.unpack_from('<I',elf,ref['offset'])[0]
                    pos=ref['immediate_offset'];lo=struct.unpack_from('<I',elf,pos)[0]
                    if hi>>26!=15 or lo>>26!=9 or lo>>21&31!=hi>>16&31:
                        raise ValueError('Category pointer pair instruction differs')
                    if (target+0x8000)>>16!=hi&65535:raise ValueError('Category high half would change')
                    before=elf[pos:pos+4];after=struct.pack('<I',(lo&0xffff0000)|(target&65535))
                    signed=target&65535;signed=signed if signed<32768 else signed-65536
                    if ((hi&65535)<<16)+signed!=target:raise ValueError('Category signed low address differs')
                else:raise ValueError('Unknown category reference kind')
                if pos in seen:raise ValueError('Category duplicate reference')
                seen.add(pos)
                if before!=after:
                    patches.append({'id':f'final.category.reference.{pos:08x}','resource':'SLUS_212.93',
                                    'offset':pos,'before':before,'after':after})
                records.append({'source_offset':at,'source_name':source,'translation':NAMES[source],
                                'consumer':ref,'target_va':target,'changed':before!=after})
    return patches,[p['id'] for p in absorbed],{
        'pool_start':START,'pool_bytes':END-START,'used_bytes':len(bytes(out).rstrip(b'\0'))+1,
        'strings':[{ 'source':s,'translation':NAMES[s],'va':v} for s,v in pointers.items()],
        'references':records,'windows':[{'offset':a,'size':z-a,'sha256':sha(elf[a:z])} for a,z in WINDOWS],
        'no_new_segment_or_heap_allocation':True,'all_other_strings_retained':True}


def normalize(old_patches,new_patches):
    key=('SLUS_212.93',START);pool=new_patches[key];overlay=bytearray(pool['before'])
    keys=[k for k,p in old_patches.items() if k[0]=='SLUS_212.93' and
          max(START,p['offset'])<min(END,p['offset']+len(p['before']))]
    for k in keys:
        p=old_patches.pop(k);at=p['offset']-START
        if p['before']!=pool['before'][at:at+len(p['before'])]:raise ValueError('Category normalization source differs')
        overlay[at:at+len(p['after'])]=p['after']
    old_patches[key]={**pool,'after':bytes(overlay)}
