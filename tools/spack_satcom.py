"""Exact Satcom mail and wanted profiles; no parent offsets or named fields edited."""
import hashlib,json,re,struct
from interface_resources import original
from reinsertion import ROOT
from glyph_spacing import ORIGINAL_SHA
from gfi import encode,decode
from spack_ui import execute_sda_pointer,execute_byte_length

RESOURCE='DATA/S/S_PACK.SDA'
POLICY='spack-satcom-mail-wanted-bounded-v001'
TABLES={'mail':(13,0x86700,0x1f10,41),'wanted':(14,0x88610,0x1960,40)}
# Standard integer instructions checked separately from R5900 register saves.
WINDOWS=((0x6cef4,0x6cf14),(0x71ae0,0x71b70),
 (0x124128,0x124138),(0x124244,0x124268),(0x12430c,0x124328),
 (0x123f44,0x123f80),(0x10e0e8,0x10e254),
 (0x12c1f4,0x12c210),(0x12c138,0x12c154),(0x1d7a08,0x1d7a44),
 (0x2266cc,0x2266d8),(0x2267f0,0x226810))

def sha(raw):return hashlib.sha256(raw).hexdigest()

def bindings(elf):return [{'offset':a,'size':z-a,'sha256':sha(elf[a:z])} for a,z in WINDOWS]

def parse_table(raw,kind,translated=False):
    _,base,size,count=TABLES[kind]
    block=bytes(raw[base:base+size])
    if len(block)!=size or struct.unpack_from('<I',block)[0]!=count:raise ValueError('Satcom table count/size mismatch')
    offsets=list(struct.unpack_from('<'+str(count)+'I',block,4))
    if offsets[0]!=4+count*4 or any(a>=b or a%4 for a,b in zip(offsets,offsets[1:]+[size])):
        raise ValueError('Satcom record boundaries mismatch')
    result=[]
    for index,(a,z) in enumerate(zip(offsets,offsets[1:]+[size])):
        record=block[a:z];fields={}
        if kind=='mail':
            if len(record)<8 or struct.unpack_from('<I',record)[0] not in (0,1,2,3):raise ValueError('Mail header mismatch')
            cursor=4
            for name in ('sender','subject','body'):
                end=record.find(b'\0',cursor)
                if end<=cursor:raise ValueError('Mail string missing/empty')
                fields[name]={'relative':cursor,'raw':record[cursor:end]};cursor=end+1
        else:
            if len(record)<=44:raise ValueError('Wanted record too small')
            name_end=record.find(b'\0',16,44)
            if name_end<17 or any(record[name_end:44]):raise ValueError('Wanted name slot mismatch')
            end=record.find(b'\0',44)
            if end<45:raise ValueError('Wanted body terminator missing')
            fields={'name':{'relative':16,'raw':record[16:name_end]},'body':{'relative':44,'raw':record[44:end]}}
            cursor=end+1
        tail=record[cursor:]
        known_tail=kind=='mail' and index==40 and (tail==b'\0\0\0\xc1' or
            (translated and tail.endswith(b'\xc1') and not any(tail[:-1])))
        if any(tail) and not known_tail:
            raise ValueError('Unknown Satcom trailing bytes')
        for field in fields.values():
            # Source ASCII is a verified repertoire here; no native promotion.
            if translated:decode(field['raw'])
            elif any(c<32 or c>126 for c in field['raw']):raise ValueError('Native Satcom text blocked')
        result.append({'id':index,'offset':base+a,'size':z-a,'raw':record,'fields':fields,'used_bytes':cursor})
    return result

def tokens(value):
    found=re.findall(rb'%[NB]0|\|',value)
    if b'%' in re.sub(rb'%[NB]0',b'',value):raise ValueError('Unknown Satcom token')
    return found

def validate_text(before,text,kind,field):
    value=encode(text)
    if not value or value!=value.strip() or any(c in value for c in (0,9,10,13)):
        raise ValueError('Invalid Satcom text/delimiter')
    if decode(value)!=text:raise ValueError('Satcom Unicode round-trip mismatch')
    if tokens(before)!=tokens(value):raise ValueError('Satcom controls/order changed')
    if kind=='wanted' and b'%' in value:raise ValueError('Wanted variables blocked')
    # Existing stack-based expansion has no general capacity proof. Do not grow
    # any source field or increase line count or the original maximum columns.
    if len(value)>len(before):raise ValueError('Satcom original field budget exceeded')
    source=before.decode('ascii');plain_source=source.replace('|',' ');plain_target=text.replace('|',' ')
    if max(map(len,text.split('|')))>max(map(len,source.split('|'))):raise ValueError('Satcom line width guard exceeded')
    if re.findall(r'\d+',re.sub(r'%[NB]0','',source))!=re.findall(r'\d+',re.sub(r'%[NB]0','',text)):
        raise ValueError('Satcom fixed numbers changed')
    from translation_policy import validate
    from weapon_terms import validate as weapons
    policy=json.loads((ROOT/'translations/politica.json').read_text(encoding='utf-8'))
    # junkyard in this mail corpus denotes the first city, including lowercase
    # occurrences. It must never trigger the material rule for generic junk.
    plain_source=re.sub(r'\bjunkyard\b','Junkyard',plain_source,flags=re.I)
    policy['case_sensitive_names']=policy['protected_names']
    issues=validate(plain_source,plain_target,policy)+weapons(plain_source,plain_target)
    # Names specific to these descriptions are locked even if not in the global glossary.
    for name in ('Suicide Bomber','Blueberry Army','Chimpone Family','Arachnomad',
                 'Lloyd','Duke','Guermo','Roberto','Lake Bridge'):
        if name in plain_source and name not in plain_target:issues.append('Satcom proper name missing: '+name)
    if issues:raise ValueError('; '.join(issues))
    return value

def rebuild(row,kind,values):
    fields=row['fields'];before=row['raw']
    if kind=='mail':
        # The getter walks sender and subject NULs. Only subject/body move inside
        # the same record. Sender, metadata and every outer pointer are immutable.
        start=fields['subject']['relative'];out=bytearray(before)
        text=values.get('subject',fields['subject']['raw'])+b'\0'+values.get('body',fields['body']['raw'])+b'\0'
        if len(text)>row['used_bytes']-start:raise ValueError('Mail record overflow')
        out[start:row['used_bytes']]=text+bytes(row['used_bytes']-start-len(text))
    else:
        out=bytearray(before);raw=fields['body']['raw'];value=values.get('body',raw)
        if len(value)>len(raw):raise ValueError('Wanted fixed body overflow')
        out[44:44+len(raw)+1]=value+bytes(len(raw)+1-len(value))
    return bytes(out)

def compile_satcom(elf,config):
    if sha(elf)!=ORIGINAL_SHA or config.get('policy')!=POLICY or config.get('instruction_windows')!=bindings(elf):
        raise ValueError('Satcom policy/instruction binding mismatch')
    raw=original(RESOURCE)
    if config.get('source_sha256')!=sha(raw):raise ValueError('Satcom source mismatch')
    tables={kind:parse_table(raw,kind) for kind in TABLES};patches=[];results=[];seen=set()
    for kind,(entry,base,size,count) in TABLES.items():
        if execute_sda_pointer(elf,raw,1)!=0x35000 or execute_sda_pointer(elf,raw[0x35000:],entry)!=base-0x35000:
            raise ValueError('Satcom SDA entry mismatch')
        if config['table_sha256'].get(kind)!=sha(raw[base:base+size]):raise ValueError('Satcom table source mismatch')
        for row in tables[kind]:
            if rebuild(row,kind,{})!=row['raw']:raise ValueError('Satcom identity round-trip failed')
    byid={(kind,row['id']):row for kind,rows in tables.items() for row in rows}
    grouped={}
    for target in config['entries']:
        key=target['id'];match=re.fullmatch(r'spack\.(mail|wanted)\.(\d{3})\.(subject|body)',key)
        if not match or key in seen:raise ValueError('Duplicate/unknown Satcom field')
        seen.add(key);kind,index,field=match.groups()
        if (kind,int(index)) not in byid:raise ValueError('Unknown Satcom record ID')
        row=byid[(kind,int(index))]
        if field not in row['fields'] or (kind=='wanted' and field!='body'):raise ValueError('Satcom immutable field')
        before=row['fields'][field]['raw']
        if target['source_sha256']!=sha(before) or target['record_sha256']!=sha(row['raw']):raise ValueError('Satcom field/record binding mismatch')
        value=validate_text(before,target['translation'],kind,field)
        if value==before:raise ValueError('Unchanged Satcom field must be omitted')
        grouped.setdefault((kind,int(index)),{})[field]=value
        results.append({'id':key,'offset':row['offset']+row['fields'][field]['relative'],
            'source_bytes':len(before),'target_bytes':len(value),'controls_hex':[t.hex() for t in tokens(before)]})
    for (kind,index),values in sorted(grouped.items()):
        row=byid[kind,index];after=rebuild(row,kind,values)
        if len(after)!=row['size']:raise ValueError('Satcom record resized')
        probe=bytearray(raw);probe[row['offset']:row['offset']+row['size']]=after
        check=parse_table(probe,kind,translated=True)[index]
        for field,old in row['fields'].items():
            if check['fields'][field]['raw']!=values.get(field,old['raw']):raise ValueError('Satcom field readback mismatch')
        if kind=='mail':
            pointers=execute_mail_getter(elf,bytes(probe[TABLES[kind][1]:TABLES[kind][1]+TABLES[kind][2]]),index)
            for field in ('sender','subject','body'):
                if pointers[field]!=row['offset']-TABLES[kind][1]+check['fields'][field]['relative']:
                    raise ValueError('Original mail getter pointer mismatch')
        patches.append({'resource':RESOURCE,'id':f'spack.{kind}.{index:03d}','offset':row['offset'],'before':row['raw'],'after':after})
    return patches,{'policy':POLICY,'accepted':len(results),'mail_records':sum(k=='mail' for k,i in grouped),
        'wanted_records':sum(k=='wanted' for k,i in grouped),'original_offsets_and_names_unchanged':True,
        'same_record_mail_repack':True,'per_field_growth':False,'reverse_roundtrip':True,
        'source_sha256':sha(raw),'instruction_windows':bindings(elf),'results':results,
        'runtime_visual_status':'pending_user_verification',
        'limits':'Byte/line guards preserve original budgets; no general expansion buffer capacity or full PS2 execution claimed'}

def execute_mail_getter(elf,table,index):
    """Run original getter with synthetic RAM; strlen calls use the original bounded probe.

    Models R5900 LQ/SQ and LD/SD solely as register saves. No I/O, GPU, message
    expansion, scheduler or complete emulator is executed.
    """
    count=struct.unpack_from('<I',table)[0]
    if not 0<=index<count:raise ValueError('Mail probe index outside table')
    regs=[0]*32;regs[4]=index;regs[5]=0x620000;regs[29]=0x700000;regs[31]=0x710000
    mem={0x600000+i:b for i,b in enumerate(table)}
    def put(at,value,size):
        for i in range(size):mem[at+i]=(value>>(8*i))&255
    def get(at,size):
        if any(at+i not in mem for i in range(size)):raise ValueError('Mail probe read outside supplied RAM')
        return sum(mem[at+i]<<(8*i) for i in range(size))
    put(0x475b2c,0x600000,4);put(0x47597c+index,3,1)
    pc=0x71ae0;pending=None;calls=0
    for _ in range(150):
        if pc==0x710000:
            if calls!=2 or regs[29]!=0x700000:raise ValueError('Mail getter ABI/strlen probe mismatch')
            return {name:get(0x620000+at,4)-0x600000 for name,at in [('sender',8),('subject',12),('body',16)]}
        if pc==0x2266cc:
            pointer=regs[4];data=[]
            for n in range(len(table)):
                b=get(pointer+n,1)
                if not b:break
                data.append(b)
            else:raise ValueError('Mail strlen unterminated')
            regs[2]=execute_byte_length(elf,bytes(data));calls+=1;pc=regs[31];continue
        if not 0x71ae0<=pc<0x71b70:raise ValueError('Mail getter probe escaped')
        w=struct.unpack_from('<I',elf,pc)[0];op=w>>26;rs=w>>21&31;rt=w>>16&31;rd=w>>11&31;fn=w&63
        n=w&65535;n=n if n<32768 else n-65536;old=pending;pending=None
        if op==0:
            if fn==0:regs[rd]=regs[rt]<<((w>>6)&31)
            elif fn in (33,45):regs[rd]=regs[rs]+regs[rt]
            elif fn==8:pending=regs[rs]
            else:raise ValueError('Unsupported mail probe integer op')
        elif op==9:regs[rt]=regs[rs]+n
        elif op==15:regs[rt]=(w&65535)<<16
        elif op in (30,35,36,55):regs[rt]=get((regs[rs]+n)&0xffffffff,{30:16,35:4,36:1,55:8}[op])
        elif op in (31,43,63):put((regs[rs]+n)&0xffffffff,regs[rt],{31:16,43:4,63:8}[op])
        elif op==3:regs[31]=pc+8;pending=((w&0x3ffffff)<<2)-0xff000
        else:raise ValueError('Unsupported mail probe opcode')
        regs=[r&((1<<128)-1) for r in regs];regs[0]=0;pc=old if old is not None else pc+4
    raise ValueError('Mail getter step limit')
