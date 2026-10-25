"""Read-only paint caption table, separate from item names in S_PACK."""
import collections,struct
from dialogue import sha
from glyph_spacing import ORIGINAL_SHA
from speaker_labels import _run
RESOURCE='DATA/S/S_PAINT.SDA'
START,COUNT,STRIDE=0xae6a0,228,36
WINDOWS=((0x1de130,0x1de160),(0x1dfe18,0x1dfe38),(0x1dfe64,0x1dfe9c),(0x1dff00,0x1dff6c))

def analyse(elf,raw):
    if sha(elf)!=ORIGINAL_SHA:raise ValueError('Paint source ELF revision differs')
    if raw[:4]!=b'sda\0' or struct.unpack_from('<I',raw,8)[0]!=28:raise ValueError('Paint SDA header differs')
    offsets=struct.unpack_from('<28I',raw,12)
    if offsets[22:24]!=(START,START+COUNT*STRIDE):raise ValueError('Paint caption table boundaries differ')
    # Execute source table address calculation through the original call delay slot.
    owner=bytearray(0xc0);context=bytearray(0xb94);struct.pack_into('<I',owner,0xbc,0x630000);struct.pack_into('<I',context,0xb90,0x600000)
    regs=[0]*32;regs[16]=0x620000
    result=_run(elf,0x1dfe18,WINDOWS,regs,[(0x620000,owner),(0x630000,context)],0x40998)
    if result[18]!=0x600000+START:raise ValueError('Original paint table base differs')
    rows=[];aliases=collections.defaultdict(list);groups=collections.Counter()
    for i in range(COUNT):
        at=START+i*STRIDE;record=raw[at:at+STRIDE];field=record[1:24];end=field.find(b'\0')
        if end<1 or any(field[end:]) or any(not 32<=v<127 for v in field[:end]):raise ValueError('Paint caption field not canonical ASCII/NUL/zero padding')
        name=field[:end];groups[record[0]]+=1;aliases[name.hex()].append(i)
        regs=[0]*32;regs[17]=0x600000+at+1
        forwarded=_run(elf,0x1dff1c,WINDOWS,regs,[],0x4f810)
        if (forwarded[6],forwarded[7],forwarded[8])!=(0x600000+at+1,22,10):raise ValueError('Paint caption forwarding differs')
        rows.append({'id':f'paint.caption.{i:04d}','index':i,'offset':at,'group_byte':record[0],'name_offset':at+1,'name_field_bytes':23,
            'source_hex':name.hex(),'source_ascii':name.decode('ascii'),'source_sha256':sha(name),'record_sha256':sha(record),
            'source_bytes':len(name),'color_data_offset':at+24,'color_data_bytes':12,'editing_authorized':False})
    if dict(groups)!={i:12 for i in range(19)}:raise ValueError('Paint grouping differs')
    metadata={'resource':RESOURCE,'source_sha256':sha(raw),'sda_entry':22,'table_offset':START,'table_size':COUNT*STRIDE,
        'records':COUNT,'record_stride':STRIDE,'group_values':len(groups),'records_per_group':12,'unique_captions':len(aliases),
        'name_field_relative_offset':1,'name_field_bytes':23,'maximum_original_caption_bytes':max(r['source_bytes'] for r in rows),
        'color_data_relative_offset':24,'color_data_bytes':12,
        'original_table_pointer_and_name_forwarding_executed':True,'name_forwarding_cases':COUNT,
        'instruction_windows':[{'offset':a,'size':z-a,'sha256':sha(elf[a:z])} for a,z in WINDOWS],
        'editing_authorized':False,'pcsx2_executed':False,
        'pending':['Prove text consumer width/capacity before allowing field growth','Preserve group byte, 12 color bytes and every alias','Map raster paint labels separately'],
        'limits':'Table address/name argument snippets executed in synthetic RAM; full category filter, constructor, glyph draw and PS2 not executed. Group identity not canonically established.'}
    return metadata,{'rows':rows,'aliases':[{'source_hex':s,'indices':ids} for s,ids in aliases.items()]}
