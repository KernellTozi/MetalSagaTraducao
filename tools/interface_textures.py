"""Read-only previews for six inspected FDATA texture entries. No PNG import."""
import argparse
import hashlib
import json
import struct
import sys
from pathlib import Path
from reinsertion import ROOT,local
from probe_resources import nested

SOURCES=('FBS_DATA.SDA','F_COMMON.SDA')


def inspect_texture(raw):
    if len(raw)<16:raise ValueError('Truncated texture header')
    width,height,bpp,palette,pixels=struct.unpack_from('<HHIII',raw)
    if bpp not in (4,8) or not 1<=width<=1024 or not 1<=height<=1024:
        raise ValueError('Unsupported dimensions or index depth')
    count=1<<bpp
    if palette!=16 or pixels!=16+count*4:raise ValueError('Unsupported palette/pixel layout')
    size=(width*height*bpp+7)//8
    if pixels+size>len(raw):raise ValueError('Texture outside record')
    encoded=raw[pixels:pixels+size]
    indices=encoded if bpp==8 else bytes(v for byte in encoded for v in (byte&15,byte>>4))[:width*height]
    rgba=raw[palette:pixels]
    rgb=bytes(v for index in indices for v in rgba[index*4:index*4+3])
    return {'width':width,'height':height,'bpp':bpp,'palette_offset':palette,
            'pixel_offset':pixels,'pixel_bytes':size,'trailing_bytes':len(raw)-pixels-size},rgb


def export(output):
    output=local(output,True)
    if output.exists():raise ValueError('Use a new output directory')
    inventory={e['path']:e for e in json.loads((ROOT/'reports/inventory.json').read_text(encoding='utf-8'))}
    previews=[]
    for name in SOURCES:
        path='DATA/FDATA/'+name;raw=(ROOT/'JOGO/Metal Saga'/path).read_bytes()
        if hashlib.sha256(raw).hexdigest()!=inventory[path]['sha256']:raise ValueError('Original resource mismatch')
        root=nested(raw)[0]
        for index in range(3):
            start=root['offsets'][index];end=root['offsets'][index+1]
            record=raw[start:end];meta,rgb=inspect_texture(record)
            previews.append((name,index,meta,rgb,{'resource':path,'source_sha256':inventory[path]['sha256'],
                'entry':index,'offset':start,'record_size':end-start,'record_sha256':hashlib.sha256(record).hexdigest(),
                'texture':meta,'png':f'{name}-{index}.png'}))
    sys.path.insert(0,str(ROOT/'work/python-deps'))
    from PIL import Image
    output.mkdir(parents=True)
    for name,index,meta,rgb,row in previews:
        Image.frombytes('RGB',(meta['width'],meta['height']),rgb).save(output/row['png'])
    report={'schema':1,'scope':'Six inspected entries only; RGB preview, not editable round-trip assets',
        'alpha':'Original palette alpha omitted in previews; no original bytes changed',
        'import_supported':False,'entries':[row for *_,row in previews]}
    (output/'manifest.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    return report


def main():
    parser=argparse.ArgumentParser(description='Exportar seis previews de interface; originais imutáveis')
    parser.add_argument('--output',type=Path,required=True);args=parser.parse_args()
    report=export(args.output)
    print(f"{len(report['entries'])} previews RGB exportados; importação ainda não implementada")


if __name__=='__main__':main()
