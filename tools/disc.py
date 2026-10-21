"""Minimal ISO9660 extent audit and same-size replacement into a new image."""
from pathlib import Path
import argparse, hashlib, json, shutil, struct

SECTOR=2048

def entries(f):
    f.seek(16*SECTOR);pvd=f.read(SECTOR)
    if pvd[:7]!=b'\x01CD001\x01' or struct.unpack_from('<H',pvd,128)[0]!=SECTOR:
        raise ValueError('Unsupported ISO9660 primary descriptor')
    def walk(record,prefix):
        extent=struct.unpack_from('<I',record,2)[0];size=struct.unpack_from('<I',record,10)[0]
        f.seek(extent*SECTOR);data=f.read(size);pos=0
        while pos<len(data):
            length=data[pos]
            if length==0:
                pos=(pos//SECTOR+1)*SECTOR;continue
            r=data[pos:pos+length];pos+=length
            if len(r)<34:raise ValueError('Invalid directory record')
            name=r[33:33+r[32]]
            if name in (b'\0',b'\1'):continue
            name=name.decode('ascii').split(';')[0]
            path=f'{prefix}/{name}'.lstrip('/')
            if r[25]&128:raise ValueError('Multi-extent file unsupported')
            if r[25]&2:yield from walk(r,path)
            else:yield {'path':path,'lba':struct.unpack_from('<I',r,2)[0],'size':struct.unpack_from('<I',r,10)[0]}
    return list(walk(pvd[156:190],''))

def digest(f,size):
    h=hashlib.sha256()
    while size:
        b=f.read(min(size,1024*1024))
        if not b:raise ValueError('Unexpected EOF')
        h.update(b);size-=len(b)
    return h.hexdigest()

def main():
    p=argparse.ArgumentParser();p.add_argument('iso',type=Path);p.add_argument('--source',type=Path);p.add_argument('--report',type=Path);p.add_argument('--replace');p.add_argument('--payload',type=Path);p.add_argument('--output',type=Path)
    a=p.parse_args()
    with a.iso.open('rb') as f:
        rows=entries(f)
        for r in rows:
            f.seek(r['lba']*SECTOR);r['sha256']=digest(f,r['size'])
            if a.source:
                source=a.source/r['path']
                r['extracted_matches']=source.is_file() and source.stat().st_size==r['size'] and hashlib.sha256(source.read_bytes()).hexdigest()==r['sha256']
    if a.report:
        a.report.parent.mkdir(parents=True,exist_ok=True);a.report.write_text(json.dumps(rows,indent=2)+'\n',encoding='utf-8')
    if a.replace:
        if not a.payload or not a.output:p.error('replacement requires --payload and --output')
        root=Path(__file__).resolve().parents[1];target=a.output.resolve()
        if not target.is_relative_to(root/'work') or target.exists():raise ValueError('Use a new output under work/')
        matches=[r for r in rows if r['path']==a.replace]
        if len(matches)!=1:raise ValueError('File not uniquely found')
        r=matches[0];payload=a.payload.read_bytes()
        if len(payload)!=r['size']:raise ValueError('Replacement must have identical size')
        target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(a.iso,target)
        with target.open('r+b') as f:f.seek(r['lba']*SECTOR);f.write(payload)
        # Compare every byte outside the replacement, not just directory entries.
        with a.iso.open('rb') as src,target.open('rb') as dst:
            start=r['lba']*SECTOR;end=start+r['size'];pos=0
            while original:=src.read(1024*1024):
                changed=dst.read(len(original));lo=max(0,start-pos);hi=min(len(original),end-pos)
                if hi>lo:
                    assert original[:lo]==changed[:lo] and original[hi:]==changed[hi:]
                else:assert original==changed
                pos+=len(original)
            assert dst.read(1)==b''
        print('Created ISO; all bytes outside replacement verified identical')
    print(f'{len(rows)} ISO files; matches: {sum(r.get("extracted_matches",False) for r in rows)}')

if __name__=='__main__':main()
