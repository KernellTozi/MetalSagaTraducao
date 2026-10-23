"""Lossless indexed-PNG transport for six pinned texture records; no quantization."""
import argparse
import hashlib
import json
from pathlib import Path
import sys
from reinsertion import ROOT,local
from interface_textures import SOURCES,inspect_texture
from probe_resources import nested

POLICY='six-textures-original-palette-v002'


def sha(raw):return hashlib.sha256(raw).hexdigest()


def pillow():
    sys.path.insert(0,str(ROOT/'work/python-deps'))
    from PIL import Image
    return Image


def records():
    inventory={e['path']:e for e in json.loads((ROOT/'reports/inventory.json').read_text(encoding='utf-8'))}
    result=[]
    for name in SOURCES:
        resource='DATA/FDATA/'+name;raw=(ROOT/'JOGO/Metal Saga'/resource).read_bytes()
        if sha(raw)!=inventory[resource]['sha256']:raise ValueError('Texture resource source mismatch')
        root=nested(raw)[0]
        for index in range(3):
            a,b=root['offsets'][index:index+2];record=raw[a:b];meta,_=inspect_texture(record)
            result.append(({'id':f'{name}.{index}','resource':resource,'entry':index,'offset':a,
                'record_size':b-a,'record_sha256':sha(record),'source_sha256':sha(raw),'texture':meta,
                'png':f'{name}-{index}.png'},record))
    return result


def unpack_indices(record,meta):
    start=meta['pixel_offset'];encoded=record[start:start+meta['pixel_bytes']]
    return encoded if meta['bpp']==8 else bytes(v for c in encoded for v in (c&15,c>>4))[:meta['width']*meta['height']]


def replace_indices(record,indices):
    meta,_=inspect_texture(record);count=meta['width']*meta['height'];limit=1<<meta['bpp']
    if len(indices)!=count or any(c>=limit for c in indices):raise ValueError('Invalid texture indices')
    at=meta['pixel_offset'];out=bytearray(record)
    if meta['bpp']==8:out[at:at+count]=indices
    else:
        for i,value in enumerate(indices):
            pos=at+i//2
            out[pos]=(out[pos]&0x0f)|(value<<4) if i%2 else (out[pos]&0xf0)|value
    return bytes(out)


def export(folder):
    folder=local(folder,True);rows=records();Image=pillow();folder.mkdir(parents=True)
    for row,raw in rows:
        meta=row['texture'];count=1<<meta['bpp'];palette=raw[16:meta['pixel_offset']]
        rgb=bytes(c for i in range(count) for c in palette[i*4:i*4+3]);alpha=bytes(palette[i*4+3] for i in range(count))
        image=Image.frombytes('P',(meta['width'],meta['height']),unpack_indices(raw,meta))
        image.putpalette(rgb+bytes(768-len(rgb)))
        image.save(folder/row['png'],transparency=alpha,bits=meta['bpp'])
    manifest={'schema':1,'policy':POLICY,'entries':[row for row,_ in rows],
        'alpha':'raw original palette bytes, not normalized PS2 opacity; do not edit palette/transparency',
        'allowed_changes':'pixel indices only; no palette, size, header, offsets, tail or other records'}
    (folder/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')
    return manifest


def import_pack(folder,output):
    folder=local(folder);output=local(output,True)
    manifest=json.loads((folder/'manifest.json').read_text(encoding='utf-8'))
    expected=records();known=[row for row,_ in expected]
    if manifest.get('schema')!=1 or manifest.get('policy')!=POLICY or manifest.get('entries')!=known:
        raise ValueError('Texture manifest binding mismatch')
    Image=pillow();rebuilt={};report=[]
    # Validate the entire pack before producing any output resource.
    for row,before in expected:
        meta=row['texture'];path=folder/row['png'];count=1<<meta['bpp'];palette=before[16:meta['pixel_offset']]
        if path.is_symlink():raise ValueError('Linked PNG blocked')
        with Image.open(path) as image:
            if image.mode!='P' or image.size!=(meta['width'],meta['height']):raise ValueError('Keep indexed PNG mode and original dimensions')
            rgb=bytes(c for i in range(count) for c in palette[i*4:i*4+3])
            if bytes(image.getpalette()[:count*3])!=rgb:raise ValueError('Palette RGB changed; no quantization allowed')
            alpha=bytes(palette[i*4+3] for i in range(count))
            if image.info.get('transparency')!=alpha:raise ValueError('Original palette alpha changed')
            indices=image.tobytes()
        after=replace_indices(before,indices)
        if unpack_indices(after,meta)!=indices:raise ValueError('Texture index readback failed')
        reverse=replace_indices(after,unpack_indices(before,meta))
        if reverse!=before:raise ValueError('Texture reverse round-trip failed')
        resource=row['resource']
        if resource not in rebuilt:rebuilt[resource]=bytearray((ROOT/'JOGO/Metal Saga'/resource).read_bytes())
        rebuilt[resource][row['offset']:row['offset']+len(after)]=after
        report.append({'id':row['id'],'changed_bytes':sum(a!=b for a,b in zip(before,after)),
                       'record_sha256':sha(after),'reverse_roundtrip':True})
    output.mkdir(parents=True)
    resources=[]
    for resource,data in rebuilt.items():
        name=Path(resource).name
        with (output/name).open('xb') as f:f.write(data)
        if sha((output/name).read_bytes())!=sha(data):raise ValueError('Rebuilt resource readback failed')
        resources.append({'resource':resource,'size':len(data),'sha256':sha(data)})
    result={'policy':POLICY,'records':report,'resources':resources,'originals_unchanged':True,
            'iso_modified':False,'visual_status':'not_tested'}
    (output/'roundtrip.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    return result


def main():
    p=argparse.ArgumentParser(description='Exportar/importar seis texturas com paleta original, em cópias locais')
    sub=p.add_subparsers(dest='action',required=True)
    e=sub.add_parser('export');e.add_argument('--output',type=Path,required=True)
    i=sub.add_parser('import');i.add_argument('--pack',type=Path,required=True);i.add_argument('--output',type=Path,required=True)
    a=p.parse_args()
    result=export(a.output) if a.action=='export' else import_pack(a.pack,a.output)
    print('Pacote de seis texturas exportado' if a.action=='export' else 'Cópias reconstruídas e verificadas; ISO não alterada')


if __name__=='__main__':main()
