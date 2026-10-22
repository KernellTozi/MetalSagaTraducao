"""Conservative MAP.MCT msg\0 editor. Fixed-size ASCII bodies, no pointer rewriting.

Discovery is heuristic; insertion additionally verifies source/record hashes, exact
headers, zero padding and three framed neighboring instructions. Unknown variants,
percent commands, non-ASCII glyphs, TAB pages and msgn are deliberately excluded.
"""
from pathlib import Path
import argparse, hashlib, json, mmap, re, struct

ROOT=Path(__file__).resolve().parents[1]
TAG=re.compile(rb'[A-Za-z0-9_]{1,4}\x00{0,3}\Z')
PILOT_OFFSET=0x1DF47F0C
PILOT_SOURCE='You want to become\na hunter?'
PILOT_TRANSLATION='Quer ser um\nHunter?'

def sha(data):return hashlib.sha256(data).hexdigest()

def instruction(data,at):
    if at<0 or at%4 or at+8>len(data):raise ValueError('Invalid instruction location')
    tag=data[at:at+4]
    if not TAG.fullmatch(tag):raise ValueError('Invalid instruction tag')
    index,size=struct.unpack_from('<HH',data,at+4)
    if size<8 or size%4 or at+size>len(data):raise ValueError('Invalid instruction size')
    return {'offset':at,'tag':tag.hex(),'index':index,'size':size}

def neighbors(data,at,count=3):
    prev=[];current=at
    for _ in range(count):
        candidates=[]
        for size in range(8,min(4096,current)+1,4):
            pos=current-size
            if data[pos:pos+4].strip(b'\0') and TAG.fullmatch(data[pos:pos+4]) and struct.unpack_from('<H',data,pos+6)[0]==size:
                candidates.append(instruction(data,pos))
        if len(candidates)!=1:raise ValueError('Ambiguous previous record boundary')
        prev.append(candidates[0]);current=candidates[0]['offset']
    following=[];current=at
    for _ in range(count):
        record=instruction(data,current);current+=record['size']
        following.append(instruction(data,current))
    return {'previous':list(reversed(prev)),'following':following}

def record(data,at,context=True):
    info=instruction(data,at);size=info['size']
    if data[at:at+4]!=b'msg\0' or size<36:raise ValueError('Unsupported message variant')
    body=data[at+32:at+size];zero=body.find(b'\0')
    if zero<=0 or any(body[zero:]):raise ValueError('Missing terminator or nonzero trailing data')
    raw=body[:zero]
    if b'%' in raw or any(c!=10 and not 32<=c<=126 for c in raw):
        raise ValueError('Unsupported control code or encoding')
    info.update({'id':f'map.msg.{at:08x}','text_offset':at+32,'capacity':size-33,
                 'header_hex':data[at:at+32].hex(),'record_sha256':sha(data[at:at+size]),
                 'source':raw.decode('ascii'),'translation':raw.decode('ascii')})
    if context:info['neighbors']=neighbors(data,at)
    return info

def plan(data,offsets):
    return {'schema':1,'resource':'DATA/MAP/MAP.MCT','source_sha256':sha(data),
            'policy':'msg-null-fixed-size-ascii-lf-v1','entries':[record(data,at) for at in offsets]}

def changes(data,document):
    if document.get('schema')!=1 or document.get('resource')!='DATA/MAP/MAP.MCT' or document.get('policy')!='msg-null-fixed-size-ascii-lf-v1':
        raise ValueError('Unsupported patch schema')
    if document['source_sha256']!=sha(data):raise ValueError('Source hash mismatch')
    patches=[];seen=set()
    for entry in document['entries']:
        at=entry['offset'];old=record(data,at)
        if at in seen:raise ValueError('Duplicate message')
        seen.add(at)
        if {k:v for k,v in entry.items() if k!='translation'}!={k:v for k,v in old.items() if k!='translation'}:
            raise ValueError('Source text or structural metadata changed')
        if entry['translation']==old['source']:
            continue
        text=entry['translation'];raw=text.encode('ascii')
        if not raw or any(c!=10 and not 32<=c<=126 for c in raw) or b'%' in raw:
            raise ValueError('Unsupported replacement control/encoding')
        if text.count('\n')!=old['source'].count('\n'):raise ValueError('Line-break count changed')
        if any(not line for line in text.split('\n')):raise ValueError('Empty lines require separate validation')
        if len(raw)>old['capacity']:raise ValueError('Message exceeds fixed slot')
        # Until GFI metrics are identified, never lengthen any visual line.
        if any(len(new)>len(src) for new,src in zip(text.split('\n'),old['source'].split('\n'))):
            raise ValueError('Line exceeds source character count; pixel width still unverified')
        payload=raw+bytes(old['capacity']+1-len(raw))
        if raw.decode('ascii')!=old['source']:
            patches.append({'offset':old['text_offset'],'before':data[old['text_offset']:at+old['size']],
                            'after':payload,'id':old['id']})
    patches.sort(key=lambda x:x['offset'])
    if any(a['offset']+len(a['before'])>b['offset'] for a,b in zip(patches,patches[1:])):
        raise ValueError('Overlapping edits')
    return patches

def main():
    p=argparse.ArgumentParser();p.add_argument('mode',choices=['pilot','scan']);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();target=a.output.resolve()
    if not target.is_relative_to(ROOT/'work') or target.exists():raise ValueError('Use a new output under work/')
    source=ROOT/'JOGO/Metal Saga/DATA/MAP/MAP.MCT'
    with source.open('rb') as f,mmap.mmap(f.fileno(),0,access=mmap.ACCESS_READ) as data:
        if a.mode=='pilot':
            document=plan(data,[PILOT_OFFSET])
            if document['entries'][0]['source']!=PILOT_SOURCE:raise ValueError('Pilot text mismatch')
            document['entries'][0]['translation']=PILOT_TRANSLATION
            changes(data,document)
        else:
            offsets=[];rejected=0
            for match in re.finditer(rb'msg\0',data):
                try:record(data,match.start());offsets.append(match.start())
                except ValueError:rejected+=1
            document=plan(data,offsets);document['scan_rejected']=rejected
        target.parent.mkdir(parents=True,exist_ok=True)
        target.write_text(json.dumps(document,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
        print(f'{len(document["entries"])} eligible records written to {target}')

if __name__=='__main__':main()
