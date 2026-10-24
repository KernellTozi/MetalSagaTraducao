"""Exact NDATA entry 12: 17 installer messages, immutable descriptor and token."""
import re,struct
from interface_resources import original,NDATA,execute_count,sha,verify
from glyph_spacing import ORIGINAL_SHA
from gfi import encode,decode
POLICY='ndata-install-crlf-original-loaded-region-v001'
START,SIZE,COUNT,DESCRIPTOR=0x96800,0x36b,17,0x348ed0
WINDOWS=((0xbd8b4,0xbd914),(0xbeec4,0xbeeec),(0x95e50,0x95fd8),
         (DESCRIPTOR,DESCRIPTOR+8),(0x3208a0,0x3208ae))

def binding(elf):return [{'offset':a,'size':z-a,'sha256':sha(elf[a:z])} for a,z in WINDOWS]

def rows(raw,elf):
    if struct.unpack_from('<II',elf,DESCRIPTOR)!=(START,SIZE):raise ValueError('Installer descriptor changed')
    count=struct.unpack_from('<I',raw,8)[0];offsets=struct.unpack_from('<'+str(count)+'I',raw,12)
    if raw[:4]!=b'sda\0' or offsets[12]!=START or START+SIZE>=offsets[13]:raise ValueError('Installer SDA bounds mismatch')
    block=raw[START:START+SIZE]
    if not block.endswith(b'\r\n'):raise ValueError('Installer final CRLF missing')
    values=block[:-2].split(b'\r\n')
    if len(values)!=COUNT or any(not v or any(c<32 or c>126 for c in v) for v in values):raise ValueError('Installer ASCII/line topology mismatch')
    return values

def tokens(value):
    found=re.findall(rb'%INSTALLSIZE%|\|',value)
    rest=re.sub(rb'%INSTALLSIZE%|\|',b'',value)
    if b'%' in rest or b'$' in rest:raise ValueError('Unproved installer variable')
    return found

def compile_install(elf,config):
    verify(elf)
    if sha(elf)!=ORIGINAL_SHA or config.get('policy')!=POLICY or config.get('instruction_windows')!=binding(elf):
        raise ValueError('Installer reader/token binding mismatch')
    raw=original(NDATA);before=raw[START:START+SIZE];source=rows(raw,elf)
    if config.get('source_sha256')!=sha(raw) or config.get('table_sha256')!=sha(before):raise ValueError('Installer source mismatch')
    if len(config['rows'])!=COUNT:raise ValueError('Installer row count changed')
    outputs=[];results=[]
    column_ceiling=max(len(line) for row in source for line in row.decode('ascii').split('|'))
    for i,(old,target) in enumerate(zip(source,config['rows'])):
        if set(target)!={'id','source_sha256','translation'} or target['id']!=f'install.{i:03d}' or target['source_sha256']!=sha(old):
            raise ValueError('Installer row ID/hash/order mismatch')
        text=target['translation'];value=encode(text)
        if not value or len(value)>511 or any(c in value for c in (0,9,10,13)):raise ValueError('Installer scratch/delimiter overflow')
        if decode(value)!=text or tokens(old)!=tokens(value):raise ValueError('Installer tokens/glyphs changed')
        if re.findall(rb'\d+',old)!=re.findall(rb'\d+',value):raise ValueError('Installer numbers changed')
        # These are variable CRLF records, not fixed per-label slots. Bound
        # columns by this table's observed maximum, including Sim/Não choices.
        # This is a conservative count, not measured pixels or a buffer proof.
        if max(map(len,text.split('|')))>column_ceiling:raise ValueError(f'Installer column guard exceeded at row {i}')
        from translation_policy import validate
        issues=validate(old.decode('ascii').replace('|',' '),text.replace('|',' '))
        if issues:raise ValueError('; '.join(issues))
        outputs.append(value)
        if value!=old:results.append({'id':target['id'],'source_bytes':len(old),'target_bytes':len(value)})
    payload=b'\r\n'.join(outputs)+b'\r\n'
    if len(payload)>SIZE:raise ValueError('Installer original loaded region exceeded')
    after=payload+bytes(SIZE-len(payload))
    if execute_count(elf,after)!=COUNT:raise ValueError('Original installer row counter disagrees')
    if after[:len(payload)].split(b'\r\n')[:-1]!=outputs or any(after[len(payload):]):raise ValueError('Installer readback mismatch')
    return [{'id':'ndata.install.12','resource':NDATA,'offset':START,'before':before,'after':after}],{
        'policy':POLICY,'accepted':len(results),'results':results,'loaded_bytes':SIZE,'used_bytes':len(payload),
        'row_count':COUNT,'column_ceiling':column_ceiling,'instruction_windows':binding(elf),'descriptor_and_external_padding_unchanged':True,
        'token':'%INSTALLSIZE%','original_counter_verified':True,'runtime_visual_status':'pending_user_verification',
        'limits':'No HDD installation, file I/O, token replacer or PCSX2 execution performed'}
