"""Recover the Satcom button typeface from its original raster labels, without scaling."""
from functools import lru_cache
import json
import struct
import sys
from pathlib import Path
from interface_graphics import original,RESOURCE,sha
from interface_texture_pack import unpack_indices,replace_indices
from interface_textures import inspect_texture
from reinsertion import ROOT

POLICY='satcom-original-raster-typeface-v004'
ALIGNED_POLICY='satcom-native-baseline-v005'
# Boxed word origins differ from their plain counterparts. In v004 these
# original offsets were incorrectly reused across both variants.
BOXED_CAPITAL_TOP_ADJUSTMENTS={19:1,21:-1,22:1}
# Original plain labels: GANM slot, glyph x bounds within the cell, capital top.
SAMPLES={'R':(13,17,24,6),'e':(13,58,65,6),'m':(13,34,43,6),'o':(14,45,52,6),
 't':(13,52,57,6),'n':(14,31,38,6),'f':(21,44,49,6),'u':(19,34,40,5),
 'a':(22,36,43,4),'i':(17,48,50,6),'l':(17,51,53,6),'s':(19,42,48,5),
 'c':(19,53,59,5),'r':(22,44,50,4),'d':(16,58,64,6),'g':(21,53,60,6),
 'M':(17,27,38,6),'A':(18,24,32,6),'C':(21,21,27,6),'D':(22,24,31,4),'H':(15,26,33,6)}


@lru_cache(maxsize=4)
def alphabet(boxed=False,aligned=False):
    sys.path.insert(0,str(ROOT/'work/python-deps'))
    from PIL import Image,ImageFilter
    raw=original(RESOURCE)[0x30c70:0x38cc0];meta,_=inspect_texture(raw);indices=unpack_indices(raw,meta)
    palette=[tuple(raw[16+i*4:19+i*4]) for i in range(16)];bg,fg=(palette[5],palette[4]) if boxed else (palette[4],palette[7])
    vector=[fg[k]-bg[k] for k in range(3)];norm=sum(v*v for v in vector)
    coverage=[max(0,min(255,round(255*sum((p[k]-bg[k])*vector[k] for k in range(3))/norm))) for p in palette]
    glyphs={}
    for char,(slot,left,right,cap) in SAMPLES.items():
        if boxed:
            if aligned:cap+=BOXED_CAPITAL_TOP_ADJUSTMENTS.get(slot,0)
            if slot in (13,15,22):left-=1;right-=1
            if char=='d':right+=1
            slot={13:1,14:2,15:3,16:4,17:5,18:6,19:7,21:9,22:10}[slot]
            x=0 if slot<10 else 80;y=slot*24 if slot<10 else (slot-10)*24
        else:x=80 if slot<20 else 160;y=(slot-10)*24 if slot<20 else (slot-20)*24
        im=Image.new('L',(right-left,18))
        im.putdata([coverage[indices[(y+cap-3+yy)*256+x+left+xx]] for yy in range(18) for xx in range(right-left)])
        if boxed:
            # Do not mistake the boxed background grain for a glyph halo.
            # Strong native ink stays exact; weaker edge tones require support
            # from the corresponding original normal glyph (one-pixel margin).
            support=alphabet(False,aligned)[char].point(lambda v:255 if v>=24 else 0).filter(ImageFilter.MaxFilter(3))
            for yy in range(18):
                for xx in range(im.width):
                    if im.getpixel((xx,yy))<190 and (xx>=support.width or not support.getpixel((xx,yy))):im.putpixel((xx,yy),0)
        glyphs[char]=im
    # Missing capitals reuse original stems/crossbars; no dialogue glyph is used.
    p=glyphs['R'].copy()
    for y in range(10,18):
        for x in range(2,p.width):p.putpixel((x,y),0)
    glyphs['P']=p
    l=Image.new('L',(7,18));l.paste(glyphs['H'].crop((0,0,2,18)),(0,0))
    l.paste(glyphs['H'].crop((0,8,7,9)),(0,14));glyphs['L']=l
    j=Image.new('L',(6,18));j.paste(glyphs['D'].crop((5,0,7,18)),(4,0))
    j.paste(glyphs['u'].crop((0,12,6,16)),(0,12));glyphs['J']=j
    j=Image.new('L',(5,18));j.paste(glyphs['i'],(3,0))
    j.paste(glyphs['g'].crop((2,15,7,18)),(0,15));glyphs['j']=j
    for char,base in (('á','a'),('ú','u')):
        accented=glyphs[base].copy();center=accented.width//2
        for x,y in ((center+1,2),(center+2,2),(center,3),(center+1,3),(center-1,4),(center,4)):
            accented.putpixel((x,y),255)
        glyphs[char]=accented
    cedilla=glyphs['c'].copy()
    for point in ((3,14),(3,15),(4,15),(3,16),(4,16),(2,17),(3,17)):cedilla.putpixel(point,255)
    glyphs['ç']=cedilla
    return glyphs


def mask(text,max_width,boxed=False,aligned=False):
    glyphs=alphabet(boxed,aligned)
    from PIL import Image
    if not text or any(c not in glyphs for c in text):raise ValueError('Character not recovered for native Satcom typeface')
    width=sum(glyphs[c].width for c in text)+len(text)-1
    if width>max_width:raise ValueError('Native raster label overflow; scaling forbidden')
    out=Image.new('L',(width,18));x=0
    for char in text:out.paste(glyphs[char],(x,0));x+=glyphs[char].width+1
    return out,{'height':18,'capital_body_pixels':12,'rendered_width':width,'horizontal_scale':1,
                'mask_sha256':sha(out.tobytes()),'font_source':'original Satcom raster letters; no GFI'}


def render(record,row,aligned=False):
    meta,_=inspect_texture(record);indices=bytearray(unpack_indices(record,meta));palette=[tuple(record[16+i*4:20+i*4]) for i in range(16)]
    x,y,z,w=row['rect'];a,b,c,d=x+3,y+3,z-3,w-3
    boxed=row['ganm_index']<12 or row['ganm_index'] in (24,26);bg,fg=(5,4) if boxed else (4,7)
    glyph,layout=mask(row['translation'],c-a,boxed,aligned)
    if glyph.height>d-b:raise ValueError('Native raster label vertical overflow')
    colors=[]
    for v in range(256):
        rgb=[round(palette[bg][k]+(palette[fg][k]-palette[bg][k])*v/255) for k in range(3)]
        colors.append(min((i for i,p in enumerate(palette) if p[3]==palette[bg][3]),key=lambda i:sum((palette[i][k]-rgb[k])**2 for k in range(3))))
    for yy in range(b,d):indices[yy*meta['width']+a:yy*meta['width']+c]=bytes([bg])*(c-a)
    ox=a+(c-a-glyph.width)//2
    for yy in range(18):
        for xx in range(glyph.width):indices[(b+yy)*meta['width']+ox+xx]=colors[glyph.getpixel((xx,yy))]
    return replace_indices(record,indices),{**layout,'inner_rect':[a,b,c,d],'background_index':bg,'foreground_index':fg}


def compile_native(config):
    from interface_graphics import compile_graphics,catalog
    if config.get('policy') not in (POLICY,ALIGNED_POLICY):raise ValueError('Unknown native raster policy')
    aligned=config['policy']==ALIGNED_POLICY
    base=ROOT/'translations/interface-graphics-v003.json';raw_base=base.read_bytes()
    if sha(raw_base)!=config['base_recipe_sha256']:raise ValueError('Historical graphic recipe changed')
    if config['source_sha256']!=json.loads(raw_base)['source_sha256']:raise ValueError('Native source binding mismatch')
    patches,report=compile_graphics(json.loads(raw_base))
    raw=original(RESOURCE);before=raw[0x30c70:0x38cc0];after=before;rows={r['id']:r for r in catalog() if r['family']=='satcom'}
    if len(config['entries'])!=26 or {e['id'] for e in config['entries']}!=set(rows):raise ValueError('Native Satcom scope changed')
    results=[]
    for target in config['entries']:
        if set(target)!={'id','translation','ganm_record_sha256','mask_sha256'}:raise ValueError('Unexpected native recipe fields')
        row=rows[target['id']]
        if target['translation']!=row['translation'] or target['ganm_record_sha256']!=row['ganm_record_sha256']:raise ValueError('Native label identity changed')
        previous=after;after,layout=render(after,row,aligned)
        if target['mask_sha256']!=layout['mask_sha256']:raise ValueError('Native raster mask drift')
        meta,_=inspect_texture(previous);old=unpack_indices(previous,meta);new=unpack_indices(after,meta);x,y,z,w=layout['inner_rect']
        for i,(p,q) in enumerate(zip(old,new)):
            if p!=q and not (x<=i%256<z and y<=i//256<w):raise ValueError('Native change outside label')
        results.append({'id':row['id'],'texture':3,'rect':row['rect'],**layout})
    meta,_=inspect_texture(before);p=meta['pixel_offset'];size=meta['pixel_bytes']
    if before[:p]!=after[:p] or before[p+size:]!=after[p+size:]:raise ValueError('Native palette/header/tail changed')
    if replace_indices(after,unpack_indices(before,meta))!=before:raise ValueError('Native reverse round-trip failed')
    patches=[p for p in patches if p['id']!='fbs.texture.3']+[
        {'resource':RESOURCE,'id':'fbs.texture.3','offset':0x30c70+meta['pixel_offset'],'before':before[p:p+size],'after':after[p:p+size]}]
    report.update(policy=config['policy'],results=[r for r in report['results'] if r['texture']!=3]+results,
        revised_labels=26,unchanged_other_graphic_labels=14,native_font_scaling=False,
        recovered_glyphs=sorted(SAMPLES),constructed_glyphs=['L','P','J','j','á','ú','ç'])
    if aligned:report.update(baseline_pixel=15,capital_top_pixel=3,xheight_top_pixel=7,
        boxed_capital_top_adjustments=BOXED_CAPITAL_TOP_ADJUSTMENTS,
        baseline_reference='original Remote; solid ink threshold 160; descenders reach row 18')
    return patches,report
