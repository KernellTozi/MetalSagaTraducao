"""v064: sales header, complete-word Load artwork, independent title credit.

No font/ELF/ISO extent changes. The official credit quad is extended in its
own ADATA scene; the translation line no longer belongs to a menu sprite.
"""
import copy,json,struct
from pathlib import Path
from dialogue import ROOT,sha
from interface_graphics import original
from interface_texture_pack import pillow,unpack_indices,replace_indices
from interface_textures import inspect_texture

POLICY='sales-load-and-attract-credit-v001'
PARENT='translations/interface-v063.json'
CHILD='translations/interface-v064.json'
MANIFEST='translations/menu-titulo-v001.json'
FOLDER=ROOT/'work/title-revision-v064'
MASTER=FOLDER/'carregar-master.png'
WORD=FOLDER/'carregar-paleta-original.png'
TITLE='DATA/RDATA/RTITLE.SDA'
TEXTURE='DATA/ADATA/ATTLTEX.SDA'
SCENE='DATA/ADATA/ATTLSCN.LDT'
SPACK='DATA/S/S_PACK.SDA'
TEXT='tradução: Kernell Tozi'
FONT=Path('C:/Windows/Fonts/arialbd.ttf')
STATUS='Vendas, Carregar e crédito junto ao bloco original; aparência pendente.'


def prepare_word():
    """Quantize a generated complete word, preserving one scale in both axes."""
    Image=pillow()
    from PIL import ImageChops,ImageDraw
    with Image.open(MASTER) as opened:
        if opened.mode!='RGBA':raise ValueError('Transparent master required')
        im=opened.copy()
    alpha=im.getchannel('A')
    core=ImageChops.multiply(im.convert('L').point(lambda v:255 if v>=200 else 0),alpha.point(lambda v:255 if v>=192 else 0))
    body=core.getbbox();bounds=alpha.point(lambda v:255 if v>=32 else 0).getbbox()
    if not body or not bounds:raise ValueError('Missing white word/alpha')
    scale=16/(body[3]-body[1]);crop=im.crop(bounds);size=(round(crop.width*scale),round(crop.height*scale))
    top=4-round((body[1]-bounds[1])*scale)
    if size[0]>224 or top<0 or top+size[1]>24:raise ValueError('Whole word exceeds native cell')
    tile=crop.resize(size,Image.Resampling.LANCZOS);cell=Image.new('RGBA',(228,24))
    cell.alpha_composite(tile,((228-size[0])//2,top))
    source=original(TITLE)[32:66608];palette=[tuple(source[16+i*4:20+i*4]) for i in range(256)]
    cache={};pixels=[]
    for red,green,blue,alpha in struct.iter_unpack('4B',cell.tobytes()):
        if alpha<4:pixels.append(0);continue
        target=(red,green,blue,round(alpha*127/255))
        if target not in cache:cache[target]=min(range(256),key=lambda k:sum((palette[k][j]-target[j])**2 for j in range(4)))
        pixels.append(cache[target])
    indices=bytes(pixels);out=Image.frombytes('P',(228,24),indices)
    out.putpalette([v for c in palette for v in c[:3]])
    out.save(WORD,transparency=bytes(c[3] for c in palette))
    return {'text':'CARREGAR','master_sha256':sha(MASTER.read_bytes()),'master_size':list(im.size),
            'path':WORD.relative_to(ROOT).as_posix(),'file_sha256':sha(WORD.read_bytes()),'indices_sha256':sha(indices),
            'cell':[228,24],'scale_xy':scale,'rendered_size':list(size),'cap_height':16,
            'source':'built-in imagegen, complete word with approved master as style reference',
            'prompt':'CARREGAR uppercase; match approved heavy white slab-serif lettering, black outline, restrained extrusion; transparent background, common baseline; new complete word, no collage.'}


def word_pixels(binding):
    from title_wordart import load_word
    record=original(TITLE)[32:66608];palette=[tuple(record[16+i*4:20+i*4]) for i in range(256)]
    return load_word(binding,palette)


def title(pixels_patch,frames_patch,word):
    Image=pillow();out=bytearray(pixels_patch['after'])
    if (pixels_patch['offset'],len(out),frames_patch['offset'])!=(1072,65536,66624):raise ValueError('Parent title spans differ')
    for y in range(24):out[(128+y)*256:(129+y)*256]=bytes(14)+word[y*228:(y+1)*228]+bytes(14)
    # The region below the label contains only the inherited translation credit.
    if any(out[152*256:238*256]) or any(out[254*256:]):raise ValueError('Unexpected title art below Load')
    out[152*256:]=bytes(104*256)
    frames=bytearray(frames_patch['after'])
    if struct.unpack_from('<8h',frames,16)!=(0,128,256,256,128,12,0,0):raise ValueError('Parent expanded Continue frame differs')
    struct.pack_into('<8h',frames,16,14,128,242,152,114,12,0,0)
    return [{**pixels_patch,'after':bytes(out)},{**frames_patch,'after':bytes(frames)}]


def sales(parent):
    from observed_menu_translation import header_glyphs
    raw=original(SPACK);record=raw[0x8c830:0x9cc40];glyphs=header_glyphs(record);text='VENDAS'
    width=sum(glyphs[c][0] for c in text)+3*(len(text)-1)
    if width>132:raise ValueError('Sales header overflows')
    out=bytearray(parent['after'])
    for y in range(144,156):out[y*256+120:y*256+256]=bytes([241])*136
    x=121
    for c in text:
        w,g=glyphs[c]
        for y in range(10):out[(144+y)*256+x:(144+y)*256+x+w]=g[y*w:(y+1)*w]
        x+=w+3
    return {**parent,'after':bytes(out)},{'translation':text,'rect':[120,144,256,156],'width':width,'height':10,'resized':False}


def credit():
    Image=pillow()
    from PIL import ImageFont,ImageDraw,ImageFilter
    raw=original(TEXTURE);scene=original(SCENE)
    if len(raw)!=526400 or len(scene)!=4108 or raw[:4]!=b'sda\0':raise ValueError('Attract resources differ')
    at=0x40430;record=raw[at:at+263184];meta,_=inspect_texture(record)
    if (meta['width'],meta['height'],meta['bpp'])!=(512,512,8):raise ValueError('Attract credit texture differs')
    pixels=unpack_indices(record,meta);palette=[tuple(record[16+i*4:20+i*4]) for i in range(256)]
    transparent=next(i for i,p in enumerate(palette) if p[3]==0)
    # A shared 16x8 white/black fade swatch occupies part of the extension.
    # Move it losslessly to a verified free area and update all twelve UV keys.
    if any(palette[pixels[y*512+x]][3] for y in range(284,298) for x in range(275,510)
           if not (320<=x<336 and 290<=y<298)):
        raise ValueError('Credit extension would overwrite original art')
    if any(palette[pixels[y*512+x]][3] for y in range(480,488) for x in range(480,496)):
        raise ValueError('Fade swatch destination is occupied')
    for left,top,right,bottom in ((320,290,336,298),(480,480,496,488)):
        if any(palette[pixels[y*512+x]][3] for y in range(top-1,bottom+1) for x in range(left-1,right+1)
               if x in (left-1,right) or y in (top-1,bottom)):
            raise ValueError('Fade swatch filtering guard border is not transparent')
    out=bytearray(pixels)
    for y in range(8):out[(480+y)*512+480:(480+y)*512+496]=pixels[(290+y)*512+320:(290+y)*512+336]
    for y in range(284,338):out[y*512+275:y*512+510]=bytes([transparent])*235
    for y in range(40):out[(284+y)*512+275:(284+y)*512+510]=pixels[(298+y)*512+275:(298+y)*512+510]
    font=ImageFont.truetype(str(FONT),44);box=font.getbbox(TEXT)
    ink=Image.new('L',(box[2]-box[0]+8,52));ImageDraw.Draw(ink).text((4-box[0],4-box[1]),TEXT,font=font,fill=255)
    ink=ink.resize((round(ink.width/4),13),Image.Resampling.LANCZOS)
    # Official small print is a crisp white/black raster, not grey antialias.
    ink=ink.point(lambda v:255 if v>=96 else 0)
    outline=ink.filter(ImageFilter.MaxFilter(3));left=275+(235-ink.width)//2
    if ink.width>233:raise ValueError('Translation credit too wide')
    cache={}
    for y in range(13):
        for x in range(ink.width):
            alpha=outline.getpixel((x,y))
            if alpha<4:continue
            value=round(255*ink.getpixel((x,y))/alpha);target=(value,value,value,round(alpha*128/255))
            if target not in cache:cache[target]=min(range(256),key=lambda k:sum((palette[k][j]-target[j])**2 for j in range(4)))
            out[(325+y)*512+left+x]=cache[target]
    # Patch only a bounded row span; pixels outside the rectangle remain identical.
    start=284*512+275;end=337*512+510
    patches=[{'id':'title.official-block-credit','resource':TEXTURE,'offset':at+meta['pixel_offset']+start,
              'before':pixels[start:end],'after':bytes(out[start:end])}]
    start=480*512+480;end=487*512+496
    patches.append({'id':'title.relocated-fade-swatch','resource':TEXTURE,'offset':at+meta['pixel_offset']+start,
                    'before':pixels[start:end],'after':bytes(out[start:end])})
    uv_offsets=(0x288,0x294,0x2a0,0x2ac,0x308,0x314,0x320,0x32c,0x914,0x964,0xf70,0xfb0)
    census=tuple(i for i in range(0,len(scene)-7,4) if struct.unpack_from('<2f',scene,i)[0] in (320/512,328/512,336/512)
                 and struct.unpack_from('<2f',scene,i)[1] in (290/512,298/512))
    if census!=uv_offsets:raise ValueError('Fade swatch UV reference census differs')
    for offset in uv_offsets:
        u,v=struct.unpack_from('<2f',scene,offset)
        patches.append({'id':f'title.fade-swatch-uv.{offset:04x}','resource':SCENE,'offset':offset,
                        'before':scene[offset:offset+8],'after':struct.pack('<2f',u+160/512,v+190/512)})
    # Quad node 5: preserve its centre X, original top edge and UV/position scales.
    expected={0xcde:struct.pack('<h',20),0xce2:struct.pack('<h',40),0xd18:struct.pack('<f',176),
              0xd9e:struct.pack('<h',-19),0xdd6:struct.pack('<h',20),0xdb4:struct.pack('<f',298/512)}
    changes={0xcde:struct.pack('<h',27),0xce2:struct.pack('<h',54),0xd18:struct.pack('<f',183),
             0xd9e:struct.pack('<h',-26),0xdd6:struct.pack('<h',27),0xdb4:struct.pack('<f',284/512)}
    if struct.unpack_from('<II',scene,0xcb8)!=(0x144001c,0x4b27) or struct.unpack_from('<HH',scene,0xcc0)!=(0,5):raise ValueError('Credit node differs')
    if struct.unpack_from('<2f',scene,0xdb0)!=(275/512,298/512) or struct.unpack_from('<2f',scene,0xde8)!=(510/512,338/512):raise ValueError('Credit UV rectangle differs')
    for offset,value in changes.items():
        before=expected[offset]
        if scene[offset:offset+len(before)]!=before:raise ValueError('Credit scene field differs')
        patches.append({'id':f'title.credit-scene.{offset:04x}','resource':SCENE,'offset':offset,'before':before,'after':value})
    return patches,{'text':TEXT,'resource_sha256':sha(raw),'scene_sha256':sha(scene),
        'texture_offset':at,'old_uv_pixels':[275,298,510,338],'new_uv_pixels':[275,284,510,338],
        'official_lines_shift_in_atlas':-14,'screen_top_before_after':[381,381],'screen_bottom_before_after':[420,434],
        'font':FONT.name,'font_sha256':sha(FONT.read_bytes()),'font_identified_as_original':False,
        'fade_swatch_old_rect':[320,290,336,298],'fade_swatch_new_rect':[480,480,496,488],
        'fade_uv_references':list(uv_offsets),'fade_swatch_pixels_preserved':True,
        'body_size':11,'outline':1,'ink_width':ink.width,'mask_sha256':sha(ink.tobytes()),
        'inherits_button_tint':False,'official_line_pixels_preserved':True,
        'scene_parser_executed':False,'visual_status':'pending_user'}


def derive(parents,word):
    by={p['id']:p for p in parents};revised=title(by['title.texture.0'],by['title.frames'],word)
    p,h=sales(by['observed.headers']);revised.append(p);new,c=credit()
    return revised,new,{'sales':h,'credit':c}


def metadata(p):return {k:p[k] for k in ('id','resource','offset')}|{'size':len(p['before']),'before_sha256':sha(p['before']),'after_sha256':sha(p['after'])}


def validate(recipe):
    binding=recipe['title_menu_release']
    if set(binding)!={'recipe','sha256'} or binding['recipe']!=MANIFEST:raise ValueError('Unknown title menu binding')
    raw=(ROOT/MANIFEST).read_bytes();m=json.loads(raw);parent=json.loads((ROOT/PARENT).read_bytes())
    if sha(raw)!=binding['sha256'] or m['parent_sha256']!=sha((ROOT/PARENT).read_bytes()) or m['policy']!=POLICY:raise ValueError('Title menu binding differs')
    expected=copy.deepcopy(parent);expected.update(title_menu_release=binding,iso_name='MetalSaga-ptbr-interface-v064.iso',status=STATUS)
    if expected!=recipe:raise ValueError('Unrelated title menu mutation')
    return parent,m


def compile_interface(elf,recipe):
    from interface_text import compile_draft
    parent,m=validate(recipe);patches,report=compile_draft(elf,parent)
    revised,new,evidence=derive(patches,word_pixels(m['word']))
    if m['revised']!=[metadata(p) for p in revised] or m['new']!=[metadata(p) for p in new] or m['evidence']!=evidence:raise ValueError('Title output drift')
    by={p['id']:p for p in revised};out=[by.get(p['id'],p) for p in patches]
    for p in new:
        if any(q['resource']==p['resource'] and max(p['offset'],q['offset'])<min(p['offset']+len(p['before']),q['offset']+len(q['before'])) for q in out):raise ValueError('New credit overlaps inherited patch')
        out.append(p)
    report=copy.deepcopy(report);report['accepted']+=1
    report['title_menu_release']={'policy':POLICY,'new_sales_header':1,'revised_load_button':1,'relocated_credit':1,
                                  'independent_of_button_tint':True,'pcsx2_executed':False,'visual_status':'pending_user'}
    graphics=report['graphic_labels']
    graphics.update(policy=POLICY,original_credits_untouched=False,official_line_pixels_preserved=True,
                    prior_title_geometry_credit_and_executable_preserved=False,executable_unchanged=True)
    graphics['approved_words'][1]={**m['word'],'artwork_approved_by_user':False}
    graphics['reviewed_artwork']={'words':graphics['approved_words'],
        'frames':[list(struct.unpack_from('<8h',by['title.frames']['after'],i*16)) for i in range(6)],
        'credit':evidence['credit'],'source':'complete word and independent ADATA credit quad'}
    for i,row in enumerate(graphics['results']):
        if row['id']=='title.label.1':row.update(translation='CARREGAR',indices_sha256=m['word']['indices_sha256'],
            file_sha256=m['word']['file_sha256'],artwork_approved_by_user=False)
        if row['id']=='title.translation-credit':graphics['results'][i]={'id':row['id'],'resource':TEXTURE,
            'texture':1,'family':'credit',**evidence['credit']}
    return out,report


def prepare():
    from interface_text import compile_draft,SOURCE
    parent=json.loads((ROOT/PARENT).read_bytes());patches,report=compile_draft(SOURCE.read_bytes(),parent)
    word=prepare_word();revised,new,evidence=derive(patches,word_pixels(word))
    m={'schema':1,'policy':POLICY,'parent':PARENT,'parent_sha256':sha((ROOT/PARENT).read_bytes()),'word':word,
       'revised':[metadata(p) for p in revised],'new':[metadata(p) for p in new],'evidence':evidence}
    raw=(json.dumps(m,ensure_ascii=False,indent=2)+'\n').encode();(ROOT/MANIFEST).write_bytes(raw)
    child=copy.deepcopy(parent);child.update(title_menu_release={'recipe':MANIFEST,'sha256':sha(raw)},iso_name='MetalSaga-ptbr-interface-v064.iso',status=STATUS)
    (ROOT/CHILD).write_bytes((json.dumps(child,ensure_ascii=False,indent=2)+'\n').encode());validate(child)
    previews(revised,new)
    return {'revised_patches':len(revised),'new_patches':len(new),'credit_text':TEXT}


def previews(revised,new):
    Image=pillow()
    from PIL import ImageDraw
    # Original credits next to the new four-line block, using the atlas palette.
    raw=original(TEXTURE);changed=bytearray(raw)
    for p in new:
        if p['resource']==TEXTURE:changed[p['offset']:p['offset']+len(p['after'])]=p['after']
    board=Image.new('RGB',(1000,145),(35,35,35));draw=ImageDraw.Draw(board)
    for col,blob in enumerate((raw,changed)):
        _,rgb=inspect_texture(blob[0x40430:0x40430+263184]);im=Image.frombytes('RGB',(512,512),rgb)
        draw.text((col*500+5,3),'Original' if col==0 else 'Novo bloco',fill='white')
        rect=(275,298,510,338) if col==0 else (275,284,510,338)
        board.paste(im.crop(rect).resize((470,(rect[3]-rect[1])*2),Image.Resampling.NEAREST),(col*500+5,22))
    board.save(FOLDER/'creditos-comparacao.png')
    before=original(TITLE);old=bytearray(before)
    # Load current approved parent word separately; credit is shown only above.
    word=Image.open(ROOT/'work/title-wordart-v001/preparado/retomar-paleta-original.png').convert('RGBA')
    rec=bytearray(before[32:66608]);p=next(p for p in revised if p['id']=='title.texture.0');rec[1040:]=p['after']
    _,rgb=inspect_texture(rec);im=Image.frombytes('RGB',(256,256),rgb).crop((14,128,242,152))
    board=Image.new('RGB',(912,80),(35,35,35));draw=ImageDraw.Draw(board)
    draw.text((5,3),'Anterior',fill='white');draw.text((461,3),'CARREGAR',fill='white')
    board.paste(word.convert('RGB').resize((456,48),Image.Resampling.NEAREST),(0,23));board.paste(im.resize((456,48),Image.Resampling.NEAREST),(456,23))
    board.save(FOLDER/'carregar-comparacao.png')
    raw=original(SPACK);modified=bytearray(raw);p=next(p for p in revised if p['id']=='observed.headers')
    modified[p['offset']:p['offset']+len(p['after'])]=p['after']
    board=Image.new('RGB',(850,70),(35,35,35));draw=ImageDraw.Draw(board)
    for col,blob in enumerate((raw,modified)):
        _,rgb=inspect_texture(blob[0x8c830:0x9cc40]);im=Image.frombytes('RGB',(256,256),rgb)
        draw.text((col*425+5,3),'Original' if col==0 else 'VENDAS',fill='white')
        board.paste(im.crop((120,144,256,156)).resize((408,36),Image.Resampling.NEAREST),(col*425+5,25))
    board.save(FOLDER/'vendas-comparacao.png')


if __name__=='__main__':print(json.dumps(prepare(),ensure_ascii=False))
