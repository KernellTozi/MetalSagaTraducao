"""Bounded FD_END editing in work copies; no ISO integration or staff-name edits."""
import argparse,json,struct
from pathlib import Path
from reinsertion import ROOT,local
from interface_text import SOURCE
from discover_credits import analyse,decode,execute_decoder_loop,RESOURCE,sha
from gfi import encode

POLICY='credits-role-lines-same-extent-lzss-v001'


def compress(data,maximum=16*1024*1024):
    if len(data)>maximum:raise ValueError('Compression input exceeds bound')
    dictionary=bytearray(1024);position=1006;at=0;out=bytearray(struct.pack('<I',len(data)))
    while at<len(data):
        flag_at=len(out);out.append(0);flags=0
        for bit in range(8):
            if at==len(data):break
            best=0;best_start=0;limit=min(18,len(data)-at)
            for start in range(1024):
                if dictionary[start]!=data[at]:continue
                length=0
                while length<limit:
                    index=(start+length)&1023;written=(index-position)&1023
                    value=data[at+written] if written<length else dictionary[index]
                    if value!=data[at+length]:break
                    length+=1
                if length>best:best,best_start=length,start
                if best==limit:break
            if best>=3:
                out.extend((best_start&255,((best_start>>8)<<4)|(best-3)));length=best
            else:
                flags|=1<<bit;out.append(data[at]);length=1
            for value in data[at:at+length]:dictionary[position]=value;position=(position+1)&1023
            at+=length
        out[flag_at]=flags
    return bytes(out)


def original():
    raw=(ROOT/'JOGO/Metal Saga'/RESOURCE).read_bytes();elf=SOURCE.read_bytes()
    expected=next(r for r in json.loads((ROOT/'reports/inventory.json').read_text(encoding='utf-8')) if r['path']==RESOURCE)
    if sha(raw)!=expected['sha256']:raise ValueError('Credits original revision differs')
    metadata,catalogue=analyse(elf,raw)
    return elf,raw,metadata,catalogue


def template(elf,raw,metadata,catalogue):
    rows=[]
    for row in catalogue['rows']:
        value=bytes.fromhex(row['source_hex'])
        kind='role-heading' if value.startswith(b'\x81\x9f') else 'closing-phrase' if row['row'] in (286,291) else 'preserved-name-company-or-layout'
        prefix=value[:2] if kind=='role-heading' else b''
        rows.append({**row,'kind':kind,'immutable_prefix_hex':prefix.hex(),
            'editable_payload':value[len(prefix):].decode('ascii') if kind!='preserved-name-company-or-layout' else None,
            'translation':None})
    windows=((0x1390a8,0x1390f0),(0x1399e4,0x139a50),(0x139d40,0x139e98))
    return {'schema':1,'policy':POLICY,'resource':RESOURCE,'source_sha256':sha(raw),
        'decoded_sha256':metadata['decoded_sha256'],'elf_sha256':sha(elf),
        'reader_windows':[{'offset':a,'size':z-a,'sha256':sha(elf[a:z])} for a,z in windows],
        'maximum_line_bytes':35,'maximum_decoded_bytes':metadata['decoded_size'],
        'iso_integration':False,'rows':rows}


def rebuild(elf,raw,metadata,catalogue,draft):
    expected=template(elf,raw,metadata,catalogue)
    binding={k:v for k,v in draft.items() if k!='rows'}
    if binding!={k:v for k,v in expected.items() if k!='rows'}:raise ValueError('Credits draft bindings differ')
    if len(draft['rows'])!=len(expected['rows']):raise ValueError('Credits row count changed')
    rows=[];changed=[]
    for target,old in zip(draft['rows'],expected['rows']):
        if {k:v for k,v in target.items() if k!='translation'}!={k:v for k,v in old.items() if k!='translation'}:
            raise ValueError('Credits row/source/ordering metadata changed')
        value=bytes.fromhex(old['source_hex']);text=target['translation']
        if text is not None:
            if old['kind']=='preserved-name-company-or-layout':raise ValueError('Staff/company/layout row is immutable')
            if not isinstance(text,str) or not text or text!=text.strip() or any(c in text for c in '\0\r\n\t%|#'):
                raise ValueError('Credits line contains controls or invalid spacing')
            if old['row']==286 and text.count('Atlus')!=1:raise ValueError('Preserve Atlus company name')
            value=bytes.fromhex(old['immutable_prefix_hex'])+encode(text)
            if len(value)>35:raise ValueError('Credits line exceeds observed 35-byte ceiling')
            if value!=bytes.fromhex(old['source_hex']):changed.append(old['id'])
        rows.append(value)
    decoded=struct.pack('<I',len(rows))+b'\r\n'.join(rows)+b'\r\n'
    if len(decoded)>metadata['decoded_size']:raise ValueError('Credits total decompressed budget exceeded')
    if not changed:
        after=raw;compressed=raw[0x800:0x1800]
    else:
        compressed=compress(decoded)
        if len(compressed)>4096:raise ValueError('Credits compressed slot overflow')
        compressed+=bytes(4096-len(compressed));after=raw[:0x800]+compressed+raw[0x1800:]
    python,consumed,_=decode(compressed)
    executed,executed_consumed,steps=execute_decoder_loop(elf,compressed)
    if python!=decoded or executed!=decoded or consumed!=executed_consumed:
        raise ValueError('Credits recompression original decoder/readback differs')
    if len(after)!=len(raw) or after[:0x800]!=raw[:0x800] or after[0x1800:]!=raw[0x1800:]:
        raise ValueError('Credits outer SDA/extent changed')
    return after,{'policy':POLICY,'changed_rows':changed,'changed_line_count':len(changed),
        'editable_line_count':sum(r['kind']!='preserved-name-company-or-layout' for r in expected['rows']),
        'line_count':len(rows),'decoded_size':len(decoded),'compressed_bytes_consumed':consumed,
        'original_decoder_steps':steps,'original_decoder_matches':True,'source_sha256':sha(raw),
        'output_sha256':sha(after),'decoded_sha256':sha(decoded),'resource_size':len(after),
        'outside_compressed_slot_identical':True,'staff_names_companies_layout_preserved':True,
        'iso_modified':False,'font_and_runtime_visual_validation':'pending; no renderer or PCSX2 execution'}


def export(path):
    path=local(path,True);elf,raw,meta,cat=original();draft=template(elf,raw,meta,cat)
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('x',encoding='utf-8') as stream:json.dump(draft,stream,ensure_ascii=False,indent=2);stream.write('\n')
    return draft


def import_pack(path,output):
    path=local(path);output=local(output,True);elf,raw,meta,cat=original()
    draft=json.loads(path.read_text(encoding='utf-8'));after,report=rebuild(elf,raw,meta,cat,draft)
    output.mkdir(parents=True)
    target=output/'FD_END.SDA'
    with target.open('xb') as stream:stream.write(after)
    if sha(target.read_bytes())!=report['output_sha256']:raise ValueError('Credits copy readback differs')
    with (output/'relatorio.json').open('x',encoding='utf-8') as stream:json.dump(report,stream,indent=2);stream.write('\n')
    return report


if __name__=='__main__':
    p=argparse.ArgumentParser(description='Preparar/recomprimir créditos em cópias locais, sem ISO')
    sub=p.add_subparsers(dest='action',required=True)
    e=sub.add_parser('export');e.add_argument('--output',type=Path,required=True)
    i=sub.add_parser('import');i.add_argument('--pack',type=Path,required=True);i.add_argument('--output',type=Path,required=True)
    args=p.parse_args();result=export(args.output) if args.action=='export' else import_pack(args.pack,args.output)
    print('Créditos preparados em cópia local; nenhuma ISO alterada.')
