"""Pinned FBS atlas labels, composed locally from the game's existing GFI glyphs."""
import argparse
from datetime import datetime
from functools import lru_cache
import hashlib
import json
from pathlib import Path
import struct
import sys
import unicodedata
from reinsertion import ROOT,local
from interface_textures import inspect_texture
from interface_texture_pack import unpack_indices,replace_indices
from probe_resources import nested
from glyph_spacing import ORIGINAL_SHA
from gfi import Gfi,CHAR_TO_BYTES,sjis_to_jis,encode

POLICY='fbs-ganm-native-glyph-labels-v003'
RESOURCE='DATA/FDATA/FBS_DATA.SDA'
FONT='DATA/SYS/SUC24I26.GFI'
WINDOWS=((0x12cd28,0x12ceb0,'711e97671bb3687971d8ba951ce4337c3c5e7d07ee017526512f729cb9ac0c77'),
         (0x12cae0,0x12cb04,'7989199582dfc3a3c786d79139de6ca183945dccf538853f5187e5beea18f9d4'),
         (0x127a50,0x127b10,'353fb75fe404d6164eeea2b7cb6a3a034d7d0ae7a8d4d43c171c851b99e2c002'),
         (0x316898,0x316900,'23eb2987e51cf886a3e568bc242d7881365e3473107a2969ed1055321063ab16'))
# These are identified sprite usages, not a generic release of all GANM records.
SATCOM={0:'Lojas',2:'Dados',3:'Caça',4:'Procurados',5:'Mensagens',6:'Alerta',7:'Música',8:'Jogos',9:'Ajustes',
        10:'Diário',11:'Ajuda',12:'Lojas',14:'Dados',15:'Caça',16:'Procurados',17:'Mensagens',18:'Alerta',
        19:'Música',20:'Jogos',21:'Ajustes',22:'Diário',23:'Ajuda',24:'Cancelar',25:'Cancelar',26:'Confirmar',27:'Confirmar'}
BATTLE={3:'MAIN',4:'SUB',5:'SE',6:'Habil.',7:'Equip.',8:'Munição',10:'Fugir',12:'Arma',13:'Passar',14:'Defesa'}
HEADERS={8:'De',9:'Assunto',21:'Tempo de jogo',22:'Título'}


def sha(raw):return hashlib.sha256(raw).hexdigest()


def original(resource):
    inventory={e['path']:e for e in json.loads((ROOT/'reports/inventory.json').read_text(encoding='utf-8'))}
    raw=(ROOT/'JOGO/Metal Saga'/resource).read_bytes()
    if sha(raw)!=inventory[resource]['sha256']:raise ValueError('Graphic source binding mismatch')
    return raw


def catalog():
    raw=original(RESOURCE);root=nested(raw)[0];offsets=root['offsets'];rows=[]
    for family,texture,ganm,labels in [('satcom',3,8,SATCOM),('battle',0,5,BATTLE),('header',2,7,HEADERS)]:
        a,z=offsets[texture:texture+2];meta,_=inspect_texture(raw[a:z]);at=offsets[ganm]
        tag,count,stride,size=struct.unpack_from('<4sIII',raw,at)
        if tag!=b'ganm' or stride!=16 or size!=16+16*count:raise ValueError('GANM format mismatch')
        for index,text in labels.items():
            u,v,x,y,ox,oy,r0,r1=struct.unpack_from('<8h',raw,at+16+16*index)
            if not 0<=u<x<=meta['width'] or not 0<=v<y<=meta['height'] or r0 or r1:raise ValueError('Unsafe GANM rectangle')
            rows.append({'id':f'fbs.{family}.{index:02d}','family':family,'texture':texture,'ganm':ganm,
                'ganm_index':index,'rect':[u,v,x,y],'ganm_record_sha256':sha(raw[at+16+16*index:at+32+16*index]),
                'translation':text})
    return rows


@lru_cache(maxsize=1)
def font_data():
    sys.path.insert(0,str(ROOT/'work/python-deps'))
    from gfi_refined import font_patches
    raw=original(FONT);modified=bytearray(raw)
    for p in font_patches(raw):modified[p['offset']:p['offset']+len(p['after'])]=p['after']
    known=json.loads((ROOT/'reports/fontes-v002-validation.json').read_text(encoding='utf-8'))
    expected=next(r['patched_sha256'] for r in known['fonts'] if r['path']==FONT)
    if sha(modified)!=expected:raise ValueError('Native glyph profile drift')
    elf=original('SLUS_212.93')
    if sha(elf)!=ORIGINAL_SHA:raise ValueError('Graphic consumer ELF mismatch')
    for a,z,h in WINDOWS:
        if sha(elf[a:z])!=h:raise ValueError('Graphic consumer/metric binding changed')
    return bytes(modified),elf[0x316898:0x316898+104]


def mask(text,height,max_width):
    encode(text)
    raw,metrics=font_data();font=Gfi(raw);glyphs=[];width=0
    from PIL import Image,ImageChops
    for char in text:
        if char==' ':glyphs.append((None,7));width+=7;continue
        base=unicodedata.normalize('NFD',char)[0]
        if not base.isascii() or not base.isalpha():left,right=0,10
        else:
            index=ord(base)-ord('A') if base.isupper() else ord(base)-ord('a')+26
            left,right=struct.unpack_from('<bb',metrics,index*2)
        at=font.glyph_offset(sjis_to_jis(int.from_bytes(CHAR_TO_BYTES[char],'big'))) if char in CHAR_TO_BYTES else font.ascii_offset(char)
        glyph=Image.new('L',(26,26));glyph.putdata([p*17 for p in font.pixels(at)])
        advance=right-left+1;glyph=glyph.crop((left,0,min(26,right+3),26));glyphs.append((glyph,advance));width+=advance
    canvas=Image.new('L',(width+2,26));cursor=0
    for glyph,advance in glyphs:
        if glyph is not None:
            box=(cursor,0,cursor+glyph.width,26);canvas.paste(ImageChops.lighter(canvas.crop(box),glyph),box)
        cursor+=advance
    natural=max(1,round(canvas.width*height/26));target=min(natural,max_width)
    if target/natural<0.72:raise ValueError('Label would be excessively compressed')
    rendered=canvas.resize((target,height),Image.Resampling.LANCZOS)
    return rendered,{'natural_width':natural,'rendered_width':target,'height':height,'horizontal_scale':target/natural}


def render(record,row):
    meta,_=inspect_texture(record);indices=bytearray(unpack_indices(record,meta));palette=[tuple(record[16+i*4:20+i*4]) for i in range(1<<meta['bpp'])]
    x,y,z,w=row['rect'];margin=3 if row['family']!='header' else 2
    inner=(x+margin,y+margin,z-margin,w-margin)
    if row['family']=='satcom':
        # First twelve and Cancel/Confirm boxed variants share the original dark style.
        boxed=row['ganm_index']<12 or row['ganm_index'] in (24,26)
        bg,fg=(5,4) if boxed else (4,7)
    elif row['family']=='battle':bg,fg=51,255
    else:bg,fg=216,255
    a,b,c,d=inner;height=16 if row['family']!='header' else 12
    glyph,layout=mask(row['translation'],height,c-a)
    if height>d-b:raise ValueError('Graphic label height overflow')
    # Palette unchanged: choose only original, equally opaque palette entries.
    colors=[]
    for coverage in range(256):
        rgb=tuple(round(palette[bg][k]+(palette[fg][k]-palette[bg][k])*coverage/255) for k in range(3))
        colors.append(min((i for i,p in enumerate(palette) if p[3]==palette[bg][3]),
                          key=lambda i:sum((palette[i][k]-rgb[k])**2 for k in range(3))))
    for yy in range(b,d):indices[yy*meta['width']+a:yy*meta['width']+c]=bytes([bg])*(c-a)
    ox=a+(c-a-glyph.width)//2;oy=b+(d-b-height)//2
    for yy in range(height):
        for xx in range(glyph.width):indices[(oy+yy)*meta['width']+ox+xx]=colors[glyph.getpixel((xx,yy))]
    return replace_indices(record,indices),{**layout,'inner_rect':list(inner),'mask_sha256':sha(glyph.tobytes()),
        'background_index':bg,'foreground_index':fg}


def compile_graphics(config):
    if config.get('policy') == 'title-native-separated-labels-credit-v009':
        from title_authentic import compile_authentic
        return compile_authentic(config)
    if config.get('policy') == 'title-uniform-labels-visible-credit-v008':
        from title_revision import compile_revision
        return compile_revision(config)
    if config.get('policy') == 'title-credit-and-raster-v007':
        from title_credit import compile_credit
        return compile_credit(config)
    if config.get('policy') == 'title-native-raster-v006':
        from title_graphics import compile_title
        return compile_title(config)
    if config.get('policy') in ('satcom-original-raster-typeface-v004','satcom-native-baseline-v005'):
        from satcom_native_font import compile_native
        return compile_native(config)
    if config.get('policy')!=POLICY:raise ValueError('Unknown graphic policy')
    raw=original(RESOURCE)
    if config.get('source_sha256')!=sha(raw):raise ValueError('Graphic recipe source mismatch')
    known={r['id']:r for r in catalog()};seen=set();result={};reports=[];root=nested(raw)[0];offsets=root['offsets']
    for target in config['entries']:
        if set(target)!={'id','ganm_record_sha256','translation','mask_sha256'}:raise ValueError('Unexpected sprite recipe fields')
        key=target['id']
        if key in seen or key not in known:raise ValueError('Duplicate or unapproved sprite ID')
        seen.add(key);row=known[key]
        if target['ganm_record_sha256']!=row['ganm_record_sha256'] or target['translation']!=row['translation']:
            raise ValueError('Graphic label binding or reviewed translation changed')
        texture=row['texture'];a,z=offsets[texture:texture+2];before=result.get(texture,raw[a:z])
        after,layout=render(before,row)
        if target.get('mask_sha256')!=layout['mask_sha256']:raise ValueError('Graphic rasterizer output drift')
        meta,_=inspect_texture(before);old=unpack_indices(before,meta);new=unpack_indices(after,meta);u,v,x,y=layout['inner_rect']
        for i,(p,q) in enumerate(zip(old,new)):
            if p!=q and not (u<=i%meta['width']<x and v<=i//meta['width']<y):raise ValueError('Change outside label drawing area')
        result[texture]=after;reports.append({'id':key,'texture':texture,'rect':row['rect'],**layout})
    patches=[]
    for texture,after in sorted(result.items()):
        a,z=offsets[texture:texture+2];before=raw[a:z];meta,_=inspect_texture(before);p=meta['pixel_offset'];n=meta['pixel_bytes']
        if before[:p]!=after[:p] or before[p+n:]!=after[p+n:]:raise ValueError('Graphic header/palette/tail changed')
        if replace_indices(after,unpack_indices(before,meta))!=before:raise ValueError('Graphic reverse round-trip failed')
        patches.append({'resource':RESOURCE,'id':f'fbs.texture.{texture}','offset':a+p,'before':before[p:p+n],'after':after[p:p+n]})
    return patches,{'policy':POLICY,'accepted':len(reports),'patches':len(patches),'source_sha256':sha(raw),
        'palettes_headers_ganm_unchanged':True,'reverse_roundtrip':True,'runtime_visual_status':'pending_user_verification',
        'results':reports}


def main():
    parser=argparse.ArgumentParser(description='Compor e conferir rótulos gráficos usando glifos do jogo; sem alterar a ISO')
    parser.add_argument('--recipe',type=Path,default=ROOT/'translations/interface-graphics-v003.json')
    parser.add_argument('--output',type=Path,default=ROOT/'work/graficos'/f'{datetime.now():%Y%m%d-%H%M%S-%f}')
    args=parser.parse_args();recipe=args.recipe.resolve();output=local(args.output,True)
    if not recipe.is_relative_to(ROOT/'translations'):raise ValueError('Use a reviewed recipe under translations/')
    config=json.loads(recipe.read_text(encoding='utf-8'));patches,report=compile_graphics(config)
    from PIL import Image
    resources=sorted({p['resource'] for p in patches});output.mkdir(parents=True)
    for resource in resources:
        source=original(resource);modified=bytearray(source)
        for p in patches:
            if p['resource']==resource:
                if source[p['offset']:p['offset']+len(p['before'])]!=p['before']:raise ValueError('Preview patch source mismatch')
                modified[p['offset']:p['offset']+len(p['after'])]=p['after']
        offsets=nested(source)[0]['offsets']+[len(source)]
        textures={r['texture'] for r in report['results'] if r.get('resource',RESOURCE)==resource}
        prefix='' if len(resources)==1 else Path(resource).stem+'-'
        for texture in sorted(textures):
            a,z=offsets[texture:texture+2]
            for name,raw in (('original',source),('ptbr',modified)):
                meta,rgb=inspect_texture(raw[a:z])
                Image.frombytes('RGB',(meta['width'],meta['height']),rgb).save(output/f'{prefix}textura-{texture}-{name}.png')
    report.update(recipe_sha256=sha(recipe.read_bytes()),iso_modified=False)
    (output/'relatorio.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(f"{report['accepted']} rótulos conferidos; previews em {output}")


if __name__=='__main__':main()
