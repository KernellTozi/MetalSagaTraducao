"""Conservative DIARY.DAT editor. Fixed slots; no relocation or encoding guesses."""
from pathlib import Path
import argparse, hashlib, json, re, struct

def fields(data):
    if len(data) < 4:
        raise ValueError('Missing count')
    n, = struct.unpack_from('<I',data)
    if not 0 < n <= (len(data)-4)//4:
        raise ValueError('Invalid count')
    offsets = list(struct.unpack_from(f'<{n}I',data,4))
    if offsets[0] != 4+4*n or any(a >= b for a,b in zip(offsets,offsets[1:]+[len(data)])):
        raise ValueError('Invalid record boundaries')
    result=[]
    for i,(a,b) in enumerate(zip(offsets,offsets[1:]+[len(data)])):
        if b-a < 50:
            raise ValueError('Short record')
        for name,start,end in [('title',a+8,a+48),('body',a+48,b)]:
            raw=data[start:end]
            zero=raw.find(b'\0')
            if zero < 0 or any(raw[zero:]):
                raise ValueError('Unexpected nonzero padding')
            text=raw[:zero].decode('ascii', errors='backslashreplace')
            result.append({'record':i,'field':name,'offset':start,'capacity':end-start-1,'text':text})
    return result

def extract(data):
    return {'source_sha256':hashlib.sha256(data).hexdigest(),'fields':fields(data)}

def rebuild(data,document):
    if document['source_sha256'] != hashlib.sha256(data).hexdigest():
        raise ValueError('Source hash mismatch')
    original=fields(data)
    if len(original)!=len(document['fields']):
        raise ValueError('Field count mismatch')
    out=bytearray(data)
    for old,new in zip(original,document['fields']):
        if any(old[k]!=new[k] for k in ('record','field','offset','capacity')):
            raise ValueError('Metadata changed')
        parts=re.split(r'(\\x[0-9a-fA-F]{2})',new['text'])
        encoded=b''.join(bytes([int(part[2:],16)]) if re.fullmatch(r'\\x[0-9a-fA-F]{2}',part) else part.encode('ascii') for part in parts)
        if [v for v in encoded if v>=128] != [v for v in data[old['offset']:old['offset']+old['capacity']+1] if v>=128]:
            raise ValueError('Non-ASCII bytes changed')
        if b'\0' in encoded or len(encoded)>old['capacity']:
            raise ValueError('Text exceeds slot or contains NUL')
        if re.findall(r'%[A-Za-z]\d*',old['text']) != re.findall(r'%[A-Za-z]\d*',new['text']):
            raise ValueError('Control tokens changed')
        a=old['offset']; end=a+old['capacity']+1
        # Preserve exact bytes for untouched fields (round-trip identity).
        if old['text']!=new['text']:
            out[a:end]=encoded+b'\0'*(end-a-len(encoded))
    fields(out)
    return bytes(out)

def main():
    p=argparse.ArgumentParser();p.add_argument('mode',choices=['extract','insert']);p.add_argument('source',type=Path);p.add_argument('json',type=Path);p.add_argument('--output',type=Path)
    a=p.parse_args();data=a.source.read_bytes()
    if a.mode=='extract':
        target=a.json; payload=(json.dumps(extract(data),ensure_ascii=False,indent=2)+'\n').encode('utf-8')
    else:
        if a.output is None: p.error('--output required')
        target=a.output;payload=rebuild(data,json.loads(a.json.read_text(encoding='utf-8')))
    root=Path(__file__).resolve().parents[1]
    if target.resolve().is_relative_to(root/'JOGO') or target.resolve().is_relative_to(root/'PCSX2'):
        raise ValueError('Protected output directory')
    if target.exists(): raise ValueError('Output already exists')
    target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(payload)
    print(target)

if __name__=='__main__':main()
