"""Repack the six static title sprites, correcting R and adding a credit line.

No extra draw call or executable change: the transparent Continue sprite carries
the credit below the menu. It inherits that sprite's existing tint/visibility.
"""
import argparse
import json
from pathlib import Path
import struct

from reinsertion import ROOT,local
from interface_graphics import original,sha,mask
from interface_textures import inspect_texture
from interface_texture_pack import pillow,unpack_indices,replace_indices
from title_native_font import RESOURCE,render as render_labels
from title_graphics import evidence

POLICY='title-credit-and-raster-v007'
TEXT='Traduzido por: Kernell Tozi'
# Same six frames, same order. Only Continue expands; its text anchor is unchanged.
FRAMES=((0,0,180,24,90,12,0,0),(0,128,256,256,128,12,0,0),
        (0,24,180,48,90,12,0,0),(240,0,245,4,1,1,0,0),
        (0,48,228,88,114,22,0,0),(0,88,228,128,114,22,0,0))


def artwork():
    Image=pillow()
    from PIL import ImageFilter
    source=original(RESOURCE);before=source[32:66608]
    meta,_=inspect_texture(before)
    atlas=Image.frombytes('L',(256,256),unpack_indices(before,meta))
    label_record,labels=render_labels(revised=True)
    label_image=Image.frombytes('L',(256,256),unpack_indices(label_record,meta))
    output=Image.new('L',(256,256))
    # Preserve frame images independently of their atlas placement.
    output.paste(label_image.crop((0,0,180,24)),(0,0))
    output.paste(label_image.crop((0,24,180,48)),(38,128))
    output.paste(label_image.crop((0,48,180,72)),(0,24))
    output.paste(atlas.crop((1,74,6,78)),(240,0))
    output.paste(atlas.crop((0,96,228,136)),(0,48))
    output.paste(atlas.crop((0,136,228,176)),(0,88))
    glyph,layout=mask(TEXT,12,250)
    # Credit is a separate small-print context: use the existing GFI font here,
    # never for the title buttons. Add a black outline to survive the map backdrop.
    ink=Image.new('L',(glyph.width+2,14));ink.paste(glyph,(1,1))
    outline=ink.filter(ImageFilter.MaxFilter(3))
    palette=[tuple(before[16+i*4:20+i*4]) for i in range(256)]
    opaque=[i for i,c in enumerate(palette) if c[3]==127]
    colors=[min(opaque,key=lambda i:sum((palette[i][k]-v)**2 for k in range(3))) for v in range(256)]
    x0=(256-ink.width)//2;y0=128+112
    if x0<0 or y0+ink.height>256:raise ValueError('Title credit exceeds texture/screen bounds')
    for y in range(ink.height):
        for x in range(ink.width):
            if outline.getpixel((x,y))>=16:
                output.putpixel((x0+x,y0+y),colors[ink.getpixel((x,y))])
    data=bytearray(source)
    data[32:66608]=replace_indices(before,output.tobytes())
    for index,frame in enumerate(FRAMES):struct.pack_into('<8h',data,66624+index*16,*frame)
    credit={'text':TEXT,'texture_rect':[x0,y0,x0+ink.width,y0+14],
            'screen_rect':[320-128+x0,330-12+112,320-128+x0+ink.width,330-12+126],
            'mask_sha256':sha(ink.tobytes()),'height':14,'layout':layout,
            'inherits_continue_tint_and_visibility':True}
    return bytes(data),{'labels':labels,'frames':[list(f) for f in FRAMES],'credit':credit}


def compile_credit(config):
    if config.get('policy')!=POLICY:raise ValueError('Unknown credit graphic policy')
    binding=config['parent']
    if binding.get('recipe')!='translations/interface-graphics-v006.json':raise ValueError('Unexpected credit parent')
    path=ROOT/binding['recipe'];payload=path.read_bytes()
    if sha(payload)!=binding['sha256']:raise ValueError('Credit parent binding mismatch')
    before=original(RESOURCE)
    if config.get('source_sha256')!=sha(before):raise ValueError('Credit resource binding mismatch')
    proof=evidence(original('SLUS_212.93'),before)
    after,review=artwork()
    if config.get('reviewed_artwork')!=review:raise ValueError('Credit labels, frames or artwork drift')
    if len(after)!=len(before) or after[:32+1040]!=before[:32+1040] or after[66608:66624]!=before[66608:66624]:
        raise ValueError('Title SDA, palette or GANM header changed')
    from interface_graphics import compile_graphics
    parent_patches,parent=compile_graphics(json.loads(payload))
    patches=[p for p in parent_patches if p['resource']!=RESOURCE]
    patches.extend([
        {'resource':RESOURCE,'id':'title.texture.0','offset':1072,'before':before[1072:66608],'after':after[1072:66608]},
        {'resource':RESOURCE,'id':'title.frames','offset':66624,'before':before[66624:66720],'after':after[66624:66720]}])
    restore=bytearray(after)
    for p in patches:
        if p['resource']==RESOURCE:restore[p['offset']:p['offset']+len(p['before'])]=p['before']
    if restore!=before:raise ValueError('Title credit reverse round-trip failed')
    results=[r for r in parent['results'] if r.get('resource')!=RESOURCE]
    results += [{'id':f'title.label.{r["index"]}','resource':RESOURCE,'texture':0,'family':'title',**r} for r in review['labels']]
    results.append({'id':'title.translation-credit','resource':RESOURCE,'texture':0,'family':'credit',**review['credit']})
    return patches,{'policy':POLICY,'accepted':parent['accepted']+1,'patches':len(patches),
                    'source_sha256':sha(before),'reverse_roundtrip':True,
                    'sda_palette_and_static_frame_count_unchanged':True,
                    'original_credits_untouched':True,'executable_unchanged':True,
                    'title_evidence':proof,'reviewed_artwork':review,'results':results,
                    'runtime_visual_status':'pending_user_verification'}


def main():
    parser=argparse.ArgumentParser(description='Conferir título corrigido e crédito de tradução, sem ISO')
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args();output=local(args.output,True)
    config=json.loads((ROOT/'translations/interface-graphics-v007.json').read_text(encoding='utf-8'))
    _,report=compile_credit(config);source=original(RESOURCE);after,_=artwork();Image=pillow()
    output.mkdir(parents=True)
    for name,data in (('original',source),('ptbr',after)):
        _,rgb=inspect_texture(data[32:66608]);Image.frombytes('RGB',(256,256),rgb).save(output/f'atlas-{name}.png')
    # Geometry preview, not a PCSX2 screenshot. Existing video credits are absent.
    canvas=Image.new('RGBA',(640,448),(88,88,66,255))
    record=after[32:66608];pixels=unpack_indices(record,inspect_texture(record)[0])
    rgba=bytes(v for i in pixels for v in (*record[16+i*4:19+i*4],min(255,record[19+i*4]*2)))
    atlas=Image.frombytes('RGBA',(256,256),rgba)
    for index,cy in ((0,296),(1,330)):
        x,y,z,w,hx,hy,*_=FRAMES[index];canvas.alpha_composite(atlas.crop((x,y,z,w)),(320-hx,cy-hy))
    canvas.convert('RGB').save(output/'posicionamento-menu-credito.png')
    (output/'relatorio.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print('Menu e crédito conferidos; preview geométrico não é teste no PCSX2')


if __name__=='__main__':main()
