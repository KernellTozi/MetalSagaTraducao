"""v065: native-size hinted credit raster; revise only its existing pixel strip."""
import copy,json,math
from dialogue import ROOT,sha
from interface_graphics import original
from interface_texture_pack import pillow,unpack_indices
from interface_textures import inspect_texture
from title_menu_revision import TEXT,TEXTURE,FONT

POLICY='credit-native-hinted-integer-raster-v001'
PARENT='translations/interface-v064.json'
CHILD='translations/interface-v065.json'
MANIFEST='translations/credito-legivel-v001.json'
FOLDER=ROOT/'work/credit-v065'
STATUS='Crédito redesenhado no tamanho nativo, com e aberto; teste visual pendente.'


def raster():
    Image=pillow()
    from PIL import ImageDraw,ImageFont
    font=ImageFont.truetype(str(FONT),12);top=font.getbbox(TEXT)[1]
    advances=[math.ceil(font.getlength(c)) for c in TEXT]
    ink=Image.new('L',(sum(advances)+4,15));draw=ImageDraw.Draw(ink);x=2;placements=[]
    for c,advance in zip(TEXT,advances):
        draw.text((x,1-top),c,font=font,fill=255)
        placements.append({'character':c,'x':x,'advance':advance});x+=advance
    ink=ink.point(lambda v:255 if v>=128 else 0)
    if ink.width>233 or ink.getbbox()[1]<1 or ink.getbbox()[3]>14:raise ValueError('Native credit clips outline or cell')
    e=Image.new('L',(12,15));ImageDraw.Draw(e).text((1,1-top),'e',font=font,fill=255)
    e=e.point(lambda v:255 if v>=128 else 0);e=e.crop(e.getbbox())
    rows=[''.join('#' if e.getpixel((x,y)) else '.' for x in range(e.width)) for y in range(e.height)]
    return ink,{'text':TEXT,'font_file':FONT.name,'font_sha256':sha(FONT.read_bytes()),'body_size':12,
                'rasterization':'native size, hinted glyphs, integer origins, no resizing',
                'threshold':128,'width':ink.width,'height':15,'outline_pixels':1,
                'mask_sha256':sha(ink.tobytes()),'placements':placements,'e_bitmap':rows,
                'font_identified_as_original':False,'visual_status':'pending_user'}


def revised_patch(parent):
    Image=pillow();ink,review=raster()
    from PIL import ImageFilter
    raw=original(TEXTURE);record=raw[0x40430:0x40430+263184];meta,_=inspect_texture(record)
    pixels=unpack_indices(record,meta);palette=[tuple(record[16+i*4:20+i*4]) for i in range(256)]
    zero=palette.index((0,0,0,0));black=palette.index((0,0,0,127));white=palette.index((255,255,255,127))
    start=284*512+275;end=337*512+510
    if (parent['id'],parent['resource'],parent['offset'],parent['before'])!=('title.official-block-credit',TEXTURE,0x40430+1040+start,pixels[start:end]):
        raise ValueError('Readability parent credit span differs')
    # Row 337 of the original official block becomes row 323 after relocation.
    # It is transparent padding, not part of any of the three official lines.
    if any(palette[pixels[337*512+x]][3] for x in range(275,510)):raise ValueError('Official padding row is occupied')
    out=bytearray(parent['after'])
    for y in range(323,338):
        offset=(y-284)*512;out[offset:offset+235]=bytes([zero])*235
    outline=ink.filter(ImageFilter.MaxFilter(3));left=275+(235-ink.width)//2
    for y in range(15):
        for x in range(ink.width):
            if outline.getpixel((x,y)):
                out[(323+y-284)*512+left+x-275]=white if ink.getpixel((x,y)) else black
    review.update(texture_rect=[left,323,left+ink.width,338],edit_rect=[275,323,510,338],
                  official_line_ink_preserved=True,scene_geometry_unchanged=True)
    return {**parent,'after':bytes(out)},review


def metadata(p):return {'id':p['id'],'resource':p['resource'],'offset':p['offset'],'size':len(p['before']),
                        'source_sha256':sha(p['before']),'parent_sha256':sha(p['after'])}


def validate(recipe):
    binding=recipe['credit_readability_release']
    if set(binding)!={'recipe','sha256'} or binding['recipe']!=MANIFEST:raise ValueError('Unknown readability binding')
    raw=(ROOT/MANIFEST).read_bytes();m=json.loads(raw);parent=json.loads((ROOT/PARENT).read_bytes())
    if sha(raw)!=binding['sha256'] or m['policy']!=POLICY or m['parent']!=PARENT or m['parent_sha256']!=sha((ROOT/PARENT).read_bytes()):
        raise ValueError('Readability parent or manifest differs')
    expected=copy.deepcopy(parent);expected.update(credit_readability_release=binding,iso_name='MetalSaga-ptbr-interface-v065.iso',status=STATUS)
    if expected!=recipe:raise ValueError('Unrelated readability mutation')
    return parent,m


def compile_interface(elf,recipe):
    from interface_text import compile_draft
    parent,m=validate(recipe);patches,report=compile_draft(elf,parent)
    old=next(p for p in patches if p['id']=='title.official-block-credit');new,review=revised_patch(old)
    if m['patch']!=metadata(old) or m['after_sha256']!=sha(new['after']) or m['review']!=review:raise ValueError('Readability output drift')
    report=copy.deepcopy(report)
    report['credit_readability_release']={'policy':POLICY,'revised_credit_lines':1,'new_units':0,'pcsx2_executed':False,'visual_status':'pending_user'}
    graphics=report['graphic_labels'];graphics['reviewed_artwork']['credit']={**graphics['reviewed_artwork']['credit'],**review,'ink_width':review['width']}
    for i,row in enumerate(graphics['results']):
        if row['id']=='title.translation-credit':graphics['results'][i]={**row,**review,'ink_width':review['width']}
    return [new if p is old else p for p in patches],report


def previews(old,new):
    Image=pillow()
    from PIL import ImageDraw
    raw=original(TEXTURE);board=Image.new('RGB',(1000,150),(70,73,53));draw=ImageDraw.Draw(board)
    for col,p in enumerate((old,new)):
        blob=bytearray(raw);blob[p['offset']:p['offset']+len(p['after'])]=p['after']
        rec=blob[0x40430:0x40430+263184];meta,_=inspect_texture(rec);pixels=unpack_indices(rec,meta)
        rgba=bytes(v for i in pixels for v in (*rec[16+i*4:19+i*4],min(255,rec[19+i*4]*2)))
        im=Image.frombytes('RGBA',(512,512),rgba).crop((275,284,510,338))
        bg=Image.new('RGBA',im.size,(70,73,53,255));bg.alpha_composite(im)
        draw.text((col*500+5,3),'v064 anterior' if col==0 else 'v065 proposta',fill='white')
        board.paste(bg.convert('RGB').resize((470,108),Image.Resampling.NEAREST),(col*500+5,24))
    FOLDER.mkdir(exist_ok=True);board.save(FOLDER/'comparacao.png')


def prepare():
    from interface_text import SOURCE,compile_draft
    parent=json.loads((ROOT/PARENT).read_bytes());patches,report=compile_draft(SOURCE.read_bytes(),parent)
    old=next(p for p in patches if p['id']=='title.official-block-credit');new,review=revised_patch(old)
    m={'schema':1,'policy':POLICY,'parent':PARENT,'parent_sha256':sha((ROOT/PARENT).read_bytes()),'patch':metadata(old),
       'after_sha256':sha(new['after']),'review':review,'user_rejected_v064_credit':True,
       'evidence':'codex-clipboard-9c9c2023-4e3f-458c-ad8d-64f81e21b255.png'}
    raw=(json.dumps(m,ensure_ascii=False,indent=2)+'\n').encode();(ROOT/MANIFEST).write_bytes(raw)
    child=copy.deepcopy(parent);child.update(credit_readability_release={'recipe':MANIFEST,'sha256':sha(raw)},iso_name='MetalSaga-ptbr-interface-v065.iso',status=STATUS)
    (ROOT/CHILD).write_bytes((json.dumps(child,ensure_ascii=False,indent=2)+'\n').encode());validate(child);previews(old,new)
    print(json.dumps({'revised_patches':1,'width':review['width'],'body_size':12}))


if __name__=='__main__':prepare()
