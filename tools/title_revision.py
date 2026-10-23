"""Pinned, uniformly rasterized title labels and on-screen translation credit."""
import json,struct
from pathlib import Path
from reinsertion import ROOT
from interface_graphics import original,sha
from interface_texture_pack import pillow,unpack_indices,replace_indices
from interface_textures import inspect_texture
from title_credit import artwork as previous_artwork,FRAMES
from title_native_font import RESOURCE,LABELS
from glyph_spacing import ORIGINAL_SHA
POLICY='title-uniform-labels-visible-credit-v008'
FONT=Path('C:/Windows/Fonts/ariblk.ttf')


def artwork():
    Image=pillow()
    from PIL import ImageFont,ImageDraw,ImageFilter
    before=original(RESOURCE);after,review=previous_artwork()
    record=before[32:66608];meta,_=inspect_texture(record)
    atlas=Image.frombytes('L',(256,256),unpack_indices(after[32:66608],meta))
    palette=[tuple(record[16+i*4:20+i*4]) for i in range(256)]
    font=ImageFont.truetype(str(FONT),96)
    rows=[]
    for i,text in enumerate(LABELS):
        probe=Image.new('L',(800,160));d=ImageDraw.Draw(probe)
        box=d.textbbox((0,0),text,font=font)
        ink=Image.new('L',(box[2]-box[0]+16,96))
        ImageDraw.Draw(ink).text((8-box[0],12-box[1]),text,font=font,fill=255)
        ink=ink.resize((round(ink.width/4),24),Image.Resampling.LANCZOS)
        outline=ink.filter(ImageFilter.MaxFilter(3))
        pix=Image.new('L',ink.size)
        for y in range(24):
            for x in range(ink.width):
                alpha=outline.getpixel((x,y))
                if alpha<4:continue
                value=round(255*ink.getpixel((x,y))/alpha)
                target=(value,value,value,round(alpha*127/255))
                idx=min(range(256),key=lambda k:sum((palette[k][j]-target[j])**2 for j in range(4)))
                pix.putpixel((x,y),idx)
        if pix.width>180:raise ValueError('Title label overflow')
        ox,oy=((0,0),(38,128),(0,24))[i]
        atlas.paste(0,(ox,oy,ox+180,oy+24))
        atlas.paste(pix,(ox+(180-pix.width)//2,oy))
        rows.append({'index':i,'translation':text,'width':pix.width,'mask_sha256':sha(pix.tobytes())})
    result=bytearray(after);result[32:66608]=replace_indices(record,atlas.tobytes())
    review['labels']=rows
    review['font']={'file':'ariblk.ttf','sha256':sha(FONT.read_bytes()),'size':24,'supersampling':4,'horizontal_rescale':False}
    review['menu_positions']={'two_options':[296,330],'three_options':[296,330,364],
        'credit_screen_rect':review['credit']['screen_rect']}
    return bytes(result),review


def compile_revision(config):
    if config.get('policy')!=POLICY:raise ValueError('Unknown title revision policy')
    parent=config['parent'];path=ROOT/parent['recipe'];payload=path.read_bytes()
    if parent['recipe']!='translations/interface-graphics-v007.json' or sha(payload)!=parent['sha256']:
        raise ValueError('Title revision parent binding mismatch')
    before=original(RESOURCE);elf=original('SLUS_212.93')
    if config['source_sha256']!=sha(before) or sha(elf)!=ORIGINAL_SHA:raise ValueError('Title revision source mismatch')
    after,review=artwork()
    if config['reviewed_artwork']!=review:raise ValueError('Title revision artwork drift')
    from interface_graphics import compile_graphics
    patches,report=compile_graphics(json.loads(payload))
    patches=[p for p in patches if p['resource']!=RESOURCE]
    for a,z,key in ((1072,66608,'title.texture.0'),(66624,66720,'title.frames')):
        patches.append({'resource':RESOURCE,'id':key,'offset':a,'before':before[a:z],'after':after[a:z]})
    # The two-option menu originally uses 306+42*i, placing v007 credit at y448.
    # Normalize to the same 296+34*i coordinates already used for three options.
    for a,old,new in ((0x393bc,0x2402002a,0x24020022),(0x393c8,0x24420132,0x24420128)):
        if struct.unpack_from('<I',elf,a)[0]!=old:raise ValueError('Title position instruction mismatch')
        patches.append({'resource':'SLUS_212.93','id':f'title.position.{a:x}','offset':a,
            'before':struct.pack('<I',old),'after':struct.pack('<I',new)})
    results=[r for r in report['results'] if r.get('resource')!=RESOURCE]
    results += [{'id':f'title.label.{r["index"]}','resource':RESOURCE,'texture':0,'family':'title',**r} for r in review['labels']]
    results.append({'id':'title.translation-credit','resource':RESOURCE,'texture':0,'family':'credit',**review['credit']})
    return patches,{**report,'policy':POLICY,'reviewed_artwork':review,'results':results,
        'executable_unchanged':False,'two_option_position_fix':True,'runtime_visual_status':'pending'}
