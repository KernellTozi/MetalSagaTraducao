"""Opt-in NDATA CRLF tables and fixed DIARY slots; no resource relocation."""
import argparse
import hashlib
import json
import re
import struct
from reinsertion import ROOT
from glyph_spacing import ORIGINAL_SHA
from gfi import encode,decode
from diary import fields
from pathlib import Path

POLICY='ndata-crlf-and-diary-fixed-v003'
NDATA='DATA/NDATA/NDATA.SDA'
DIARY='DATA/FDATA/DIARY.DAT'
TABLES={186:(0x110d800,0x1357,79,0x320b00),200:(0x1344800,0x43b,20,0x348ff0)}
CODE=((0x95b68,0x95bb4,'77cd592d6ba49e60d254e189911898331aab485d4962319973d21f7abdf60b70'),
      (0x95c20,0x95d70,'d158ec9ef69622594bca89d8c4a3d9a97aae614a93469eb42ddb40d19c192a2e'),
      (0xc11e8,0xc1260,'c168129c4e743ddfdc2a006d7d102f3b43a6c428ac8270b72802485e256a9118'),
      (0xcddb0,0xcde08,'6f9a2eb751718e77c4cbb93cdc730f9d85309a5b56491d1646d7325ea0834114'),
      (0x96998,0x96a48,'db3095e55581cd2df8eb18208e80c822a213ea6a17ffe3e269dddac59b9be8ef'))


def sha(raw):return hashlib.sha256(raw).hexdigest()


def original(resource):
    inventory={e['path']:e for e in json.loads((ROOT/'reports/inventory.json').read_text(encoding='utf-8'))}
    raw=(ROOT/'JOGO/Metal Saga'/resource).read_bytes()
    if sha(raw)!=inventory[resource]['sha256']:raise ValueError('Resource source mismatch')
    return raw


def verify(elf):
    if sha(elf)!=ORIGINAL_SHA:raise ValueError('Resource ELF mismatch')
    for a,z,h in CODE:
        if sha(elf[a:z])!=h:raise ValueError('CRLF reader/consumer mismatch')
    return {'elf_sha256':ORIGINAL_SHA,'instruction_windows':[{'offset':a,'size':z-a,'sha256':h} for a,z,h in CODE],
            'scratch_row_limit':511,'line_separator':'CRLF','pipe_becomes_newline_in_memory':True,
            'runtime_visual_status':'pending_user_verification'}


def table_rows(raw,elf,index):
    if index not in TABLES:raise ValueError('Unknown NDATA table')
    start,size,count,descriptor=TABLES[index]
    if raw[:4]!=b'sda\0' or struct.unpack_from('<I',raw,4)[0]!=len(raw):raise ValueError('NDATA header mismatch')
    n=struct.unpack_from('<I',raw,8)[0];offsets=struct.unpack_from('<'+str(n)+'I',raw,12)
    if offsets[index]!=start or start+size>=offsets[index+1]:raise ValueError('NDATA boundary mismatch')
    if struct.unpack_from('<II',elf,descriptor)!=(start,size):raise ValueError('NDATA descriptor mismatch')
    payload=raw[start:start+size]
    if not payload.endswith(b'\r\n') or any(c not in (10,13) and not 32<=c<127 for c in payload):raise ValueError('Unsupported table bytes')
    rows=payload[:-2].split(b'\r\n')
    if len(rows)!=count or any(not r or b'\r' in r or b'\n' in r or len(r)>511 for r in rows):raise ValueError('CRLF row structure mismatch')
    return rows


def tokens(raw,diary=False):
    pattern=rb'%N\d+|\|' if diary else rb'\$[A-Z]+\$|\|'
    result=re.findall(pattern,raw)
    rest=re.sub(pattern,b'',raw)
    if b'%' in rest or b'$' in rest:raise ValueError('Unknown resource control')
    return result


def validate_text(before,text,diary=False):
    after=encode(text)
    if not after or any(c in after for c in (0,9,10,13)):raise ValueError('Empty text or injected table delimiter')
    if tokens(before,diary)!=tokens(after,diary):raise ValueError('Resource controls changed')
    if decode(after)!=text:raise ValueError('Resource glyph round-trip failed')
    from translation_policy import validate,POLICY_PATH
    policy=json.loads(POLICY_PATH.read_text(encoding='utf-8'))
    # Proper-name case distinguishes generic "junkyard" from the city Junkyard.
    # Profession terms and expressions retain the shared policy's matching.
    policy['case_sensitive_names']=policy['protected_names']
    issues=validate(before.decode('ascii').replace('|',' '),text.replace('|',' '),policy)
    if issues:raise ValueError('Resource terminology: '+'; '.join(issues))
    return after


def execute_count(elf,raw):
    """Execute only the original CR/LF counting loop in simulated memory.

    File PCs, real branch/likely delay slots, synthetic buffer/count pointer.
    Does not execute allocation, font classification, I/O or the PS2 runtime.
    """
    verify(elf);regs=[0]*32;regs[16]=len(raw);regs[20]=0x2000;regs[21]=0x4000
    memory={0x4000+i:c for i,c in enumerate(raw+b'\0')};pc=0x95b68;pending=None
    for _ in range(max(100,20*len(raw))):
        if pc==0x95bb4:
            return sum(memory.get(0x2000+i,0)<<(8*i) for i in range(4))
        if not 0x95b68<=pc<0x95bb4:raise ValueError('Counter escaped verified code')
        w=struct.unpack_from('<I',elf,pc)[0];op=w>>26;rs=w>>21&31;rt=w>>16&31;rd=w>>11&31;fn=w&63
        n=w&65535;n=n if n<32768 else n-65536;old=pending;pending=None;nextpc=pc+4
        if op==0:
            if fn in (33,45):regs[rd]=regs[rs]+regs[rt]
            elif fn==43:regs[rd]=int(regs[rs]<regs[rt])
            elif fn==10:
                if regs[rt]==0:regs[rd]=regs[rs]
            else:raise ValueError('Unsupported counter arithmetic')
        elif op in (4,5,20,21):
            equal=regs[rs]==regs[rt];taken=equal if op in (4,20) else not equal
            if op in (20,21) and not taken:nextpc=pc+8
            else:pending=pc+4+n*4 if taken else pc+8
        elif op==9:regs[rt]=regs[rs]+n
        elif op==14:regs[rt]=regs[rs]^(w&65535)
        elif op in (32,35):
            a=(regs[rs]+n)&0xffffffff
            if op==32:
                c=memory.get(a,0);regs[rt]=c if c<128 else c-256
            else:regs[rt]=sum(memory.get(a+i,0)<<(8*i) for i in range(4))
        elif op==43:
            a=(regs[rs]+n)&0xffffffff
            for i in range(4):memory[a+i]=(regs[rt]>>(8*i))&255
        else:raise ValueError('Unsupported counter instruction')
        regs=[v&0xffffffff for v in regs];regs[0]=0;pc=old if old is not None else nextpc
    raise ValueError('Counter instruction budget exceeded')


def compile_resources(elf,draft):
    config=draft.get('resource_texts')
    if config is None:return [],{'accepted':0,'results':[]}
    if config.get('policy')!=POLICY:raise ValueError('Unknown resource policy')
    evidence=verify(elf);patches=[];results=[];seen=set()
    bindings=config['source_bindings']
    for resource in (NDATA,DIARY):
        if bindings.get(resource)!=sha(original(resource)):raise ValueError('Resource recipe source mismatch')
    ndata=original(NDATA)
    for table in config.get('tables',[]):
        index=table['index']
        if index in seen:raise ValueError('Duplicate NDATA table')
        seen.add(index);rows=table_rows(ndata,elf,index);start,size,count,_=TABLES[index]
        if table['source_sha256']!=sha(ndata[start:start+size]):raise ValueError('NDATA table binding mismatch')
        if len(table['rows'])!=len(rows):raise ValueError('NDATA row count changed')
        output=[]
        for i,(before,target) in enumerate(zip(rows,table['rows'])):
            if target['id']!=f'ndata.{index:03d}.{i:03d}' or target['source_sha256']!=sha(before):raise ValueError('NDATA row identity mismatch')
            after=validate_text(before,target['translation'])
            if len(after)>511:raise ValueError('CRLF scratch row overflow')
            output.append(after)
            if after!=before:results.append({'id':target['id'],'resource':NDATA,'table':index,'row':i,'source_bytes':len(before),'target_bytes':len(after)})
        payload=b'\r\n'.join(output)+b'\r\n'
        if len(payload)>size:raise ValueError('NDATA fixed loaded region overflow')
        # Runtime loader still reads its original length. NUL padding adds no
        # CR/LF records; all line indices and the loaded allocation are retained.
        after=payload+bytes(size-len(payload));before=ndata[start:start+size]
        if execute_count(elf,after)!=count:raise ValueError('Original counter disagrees with compiled row count')
        if after!=before:patches.append({'resource':NDATA,'id':f'ndata.table.{index}','offset':start,'before':before,'after':after})
    raw=original(DIARY);known={f"diary.{e['record']:03d}.{e['field']}":e for e in fields(raw)}
    seen=set()
    for target in config.get('diary',[]):
        key=target['id']
        if key in seen:raise ValueError('Duplicate diary field')
        seen.add(key);entry=known[key];a=entry['offset'];capacity=entry['capacity'];before=raw[a:a+capacity+1];old=before.split(b'\0',1)[0]
        if any(c>=128 for c in old):raise ValueError('Native diary bytes remain blocked')
        if target['source_sha256']!=sha(old):raise ValueError('Diary field binding mismatch')
        after=validate_text(old,target['translation'],True)
        if len(after)>capacity:raise ValueError(f'Diary slot overflow: {key}')
        if old==after:raise ValueError('Unchanged diary field must be omitted')
        patches.append({'resource':DIARY,'id':key,'offset':a,'before':before,'after':after+bytes(len(before)-len(after))})
        results.append({'id':key,'resource':DIARY,'offset':a,'capacity':capacity,'source_bytes':len(old),'target_bytes':len(after)})
    # Independent per-resource readback/reversal; no original bytes are written.
    for resource in (NDATA,DIARY):
        source=original(resource);out=bytearray(source);spans=sorted((p for p in patches if p['resource']==resource),key=lambda p:p['offset'])
        if any(a['offset']+len(a['after'])>b['offset'] for a,b in zip(spans,spans[1:])):raise ValueError('Resource patches overlap')
        for p in spans:
            if len(p['before'])!=len(p['after']):raise ValueError('Resource resized')
            out[p['offset']:p['offset']+len(p['after'])]=p['after']
        for p in spans:
            if out[p['offset']:p['offset']+len(p['after'])]!=p['after']:raise ValueError('Resource readback failed')
            out[p['offset']:p['offset']+len(p['before'])]=p['before']
        if out!=source:raise ValueError('Resource reverse round-trip failed')
    return patches,{'accepted':len(results),'patches':len(patches),'evidence':evidence,'results':results,'reverse_roundtrip':True}


def main():
    parser=argparse.ArgumentParser(description='Exportar tabelas comprovadas de interface e slots do diário, sem APIs')
    parser.add_argument('--output',type=Path,required=True);args=parser.parse_args()
    from reinsertion import local
    from interface_text import SOURCE
    output=local(args.output,True);elf=SOURCE.read_bytes();evidence=verify(elf);ndata=original(NDATA)
    tables=[]
    for index in TABLES:
        at,size,_,_=TABLES[index];rows=table_rows(ndata,elf,index);cursor=at;items=[]
        for i,row in enumerate(rows):
            items.append({'id':f'ndata.{index:03d}.{i:03d}','offset':cursor,'source':row.decode('ascii'),
                'source_hex':row.hex(),'source_sha256':sha(row),'controls_hex':[t.hex() for t in tokens(row)]})
            cursor+=len(row)+2
        tables.append({'index':index,'offset':at,'loaded_bytes':size,'rows':items})
    raw=original(DIARY);diary=[]
    for e in fields(raw):
        row=raw[e['offset']:e['offset']+e['capacity']+1].split(b'\0',1)[0]
        diary.append({**e,'id':f"diary.{e['record']:03d}.{e['field']}",'source_hex':row.hex(),
            'source_sha256':sha(row),'editable':all(c<128 for c in row)})
    document={'schema':1,'policy':POLICY,'evidence':evidence,'tables':tables,'diary':diary,
        'source_bindings':{r:sha(original(r)) for r in (NDATA,DIARY)}}
    output.parent.mkdir(parents=True,exist_ok=True)
    with output.open('x',encoding='utf-8') as stream:json.dump(document,stream,ensure_ascii=False,indent=2);stream.write('\n')
    print('99 mensagens do sistema e 136 campos do diário exportados; 2 corpos nativos bloqueados')


if __name__=='__main__':main()
