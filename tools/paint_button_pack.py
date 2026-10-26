"""Bounded indexed crops for paint menus, work copies only, no ISO promotion."""
import argparse,json
from pathlib import Path
from reinsertion import ROOT,local
from explore_interface_atlases import inspect,sha
from interface_texture_pack import pillow,unpack_indices,replace_indices
from interface_text import SOURCE
from discover_paint import RESOURCE
from paint_captions import SOURCE_SHA
from glyph_spacing import ORIGINAL_SHA
from speaker_labels import _run

POLICY='paint-menu-indexed-ganm-crops-work-copies-v001'
WINDOWS=((0x5e250,0x5e284),)


def inventory():
    elf=SOURCE.read_bytes();raw=(ROOT/'JOGO/Metal Saga'/RESOURCE).read_bytes()
    if sha(elf)!=ORIGINAL_SHA or sha(raw)!=SOURCE_SHA:raise ValueError('Paint source revision differs')
    records={r['entry']:r for r in inspect(raw) if r['node_offset']==0}
    # Actual component texture/GANM argument forwarding, bounded before callees.
    import struct
    owner=bytearray(0x724);context=bytearray(0x3c)
    struct.pack_into('<I',owner,0x720,0x630000);struct.pack_into('<I',context,0x38,0x600000)
    regs=[0]*32;regs[17]=0x620000
    a=_run(elf,0x5e250,WINDOWS,regs,[(0x620000,owner),(0x630000,context)],0x1acc58)
    if (a[5],a[7])!=(0x600000+records[6]['offset'],records[6]['size']):raise ValueError('Paint component texture forwarding differs')
    a=_run(elf,0x5e274,WINDOWS,a,[],0x19af80)
    if a[5]!=0x600000+records[7]['offset']:raise ValueError('Paint component GANM forwarding differs')
    rows=[]
    for texture,ganm,indices in ((13,14,range(10)),(6,7,(0,)),(8,9,(19,))):
        row=records[texture];geometry=records[ganm]
        for i in indices:
            sprite=geometry['sprites'][i];rect=sprite['rect'];meta=row['texture']
            if not (0<=rect[0]<rect[2]<=meta['width'] and 0<=rect[1]<rect[3]<=meta['height']):raise ValueError('Paint crop bounds differ')
            key=f'paint.button.{texture:02d}.{i:02d}'
            rows.append({'id':key,'texture_entry':texture,'texture_offset':row['offset'],
                'texture_size':row['size'],'texture_sha256':row['sha256'],'texture':meta,
                'ganm_offset':geometry['offset'],'ganm_sha256':geometry['sha256'],
                'sprite_index':i,'rect':rect,'png':key+'.png',
                'editable':not (texture==13 and i in (6,7)),
                'usage_evidence':'component texture and GANM forwarding executed' if texture==6 else 'visual crop plus GANM geometry; dispatch pending'})
    result={'schema':1,'policy':POLICY,'resource':RESOURCE,'source_sha256':SOURCE_SHA,
        'elf_sha256':ORIGINAL_SHA,'instruction_windows':[{'offset':a,'size':z-a,'sha256':sha(elf[a:z])} for a,z in WINDOWS],
        'entries':rows,'scope':'Work copy only. Same-size indexed crops; palette/alpha/GANM immutable. MAIN/SUB/SE preservation required.',
        'iso_integration':False,'pcsx2_executed':False}
    return raw,result


def export(folder):
    folder=local(folder,True);raw,manifest=inventory();Image=pillow();folder.mkdir(parents=True)
    for row in manifest['entries']:
        meta=row['texture'];record=raw[row['texture_offset']:row['texture_offset']+row['texture_size']]
        palette=record[16:meta['pixel_offset']];count=1<<meta['bpp']
        image=Image.frombytes('P',(meta['width'],meta['height']),unpack_indices(record,meta))
        image.putpalette(bytes(c for i in range(count) for c in palette[4*i:4*i+3])+bytes(768-count*3))
        image.crop(row['rect']).save(folder/row['png'],transparency=bytes(palette[4*i+3] for i in range(count)),bits=meta['bpp'])
    with (folder/'manifest.json').open('x',encoding='utf-8') as f:json.dump(manifest,f,indent=2);f.write('\n')
    return manifest


def import_pack(folder,output):
    folder=local(folder);output=local(output,True);raw,expected=inventory()
    if (folder/'manifest.json').is_symlink():raise ValueError('Linked manifest blocked')
    if json.loads((folder/'manifest.json').read_text(encoding='utf-8'))!=expected:raise ValueError('Paint crop bindings differ')
    Image=pillow();buffers={};results=[]
    for row in expected['entries']:
        meta=row['texture'];at=row['texture_offset'];before=raw[at:at+row['texture_size']]
        if at not in buffers:buffers[at]=bytearray(unpack_indices(before,meta))
        palette=before[16:meta['pixel_offset']];count=1<<meta['bpp'];x,y,z,w=row['rect'];path=folder/row['png']
        if path.is_symlink():raise ValueError('Linked crop blocked')
        with Image.open(path) as im:
            if im.mode!='P' or im.size!=(z-x,w-y):raise ValueError('Paint crop dimensions/mode changed')
            rgb=bytes(c for i in range(count) for c in palette[4*i:4*i+3])
            if bytes(im.getpalette()[:count*3])!=rgb or im.info.get('transparency')!=bytes(palette[4*i+3] for i in range(count)):
                raise ValueError('Paint crop palette/alpha changed')
            value=im.tobytes()
        if any(c>=count for c in value):raise ValueError('Paint crop palette index outside range')
        old=unpack_indices(before,meta);changed=0
        for yy in range(w-y):
            low=(y+yy)*meta['width']+x;part=value[yy*(z-x):(yy+1)*(z-x)]
            changed+=sum(a!=b for a,b in zip(old[low:low+z-x],part))
            buffers[at][low:low+z-x]=part
        if changed and not row['editable']:raise ValueError('Protected SUB/SE paint caption modified')
        results.append({'id':row['id'],'changed_pixels':changed})
    rebuilt=bytearray(raw)
    for at,indices in buffers.items():
        row=next(r for r in expected['entries'] if r['texture_offset']==at)
        before=raw[at:at+row['texture_size']];after=replace_indices(before,indices)
        if replace_indices(after,unpack_indices(before,row['texture']))!=before:raise ValueError('Paint crop reverse round-trip differs')
        rebuilt[at:at+len(after)]=after
    reverse=bytearray(rebuilt)
    for at in buffers:
        row=next(r for r in expected['entries'] if r['texture_offset']==at)
        reverse[at:at+row['texture_size']]=raw[at:at+row['texture_size']]
    if reverse!=raw or len(rebuilt)!=len(raw):raise ValueError('Paint resource bounds changed')
    output.mkdir(parents=True)
    with (output/'S_PAINT.SDA').open('xb') as f:f.write(rebuilt)
    if sha((output/'S_PAINT.SDA').read_bytes())!=sha(rebuilt):raise ValueError('Paint copy readback failed')
    report={'policy':POLICY,'entries':results,'source_sha256':sha(raw),'output_sha256':sha(rebuilt),
        'resource_size':len(rebuilt),'originals_modified':False,'iso_modified':False,'reverse_roundtrip':True,
        'iso_usage_approval':False,'runtime_visual_status':'not_tested'}
    with (output/'relatorio.json').open('x',encoding='utf-8') as f:json.dump(report,f,indent=2);f.write('\n')
    return report


if __name__=='__main__':
    p=argparse.ArgumentParser(description='Preparar/importar recortes da pintura em cópias, sem alterar ISO')
    sub=p.add_subparsers(dest='action',required=True)
    e=sub.add_parser('export');e.add_argument('--output',type=Path,required=True)
    i=sub.add_parser('import');i.add_argument('--pack',type=Path,required=True);i.add_argument('--output',type=Path,required=True)
    a=p.parse_args();r=export(a.output) if a.action=='export' else import_pack(a.pack,a.output)
    print('Recortes de pintura processados; ISO inalterada.')
