"""Title revision retaining native letters, with three explicitly reconstructed glyphs."""
import json,struct
from pathlib import Path
from reinsertion import ROOT
from interface_graphics import original,sha
from interface_textures import inspect_texture
from interface_texture_pack import pillow,unpack_indices,replace_indices
from title_native_font import alphabet,RESOURCE,LABELS
from title_credit import FRAMES,TEXT
POLICY='title-native-separated-labels-credit-v009'
FONT=Path('C:/Windows/Fonts/ARLRDBD.TTF')


def glyphs():
    Image=pillow();g={k:v.copy() for k,v in alphabet().items()}
    w=g['W'];v=w.crop((14,0,w.width,24))
    # Remove the unrelated first stroke of W that crossed the old crop.
    for y in range(24):
        edge=max(0,round((y-5)*0.6)-1)
        for x in range(min(edge,v.width)):v.putpixel((x,y),0)
    g['V']=v
    j=g['U'].copy()
    for y in range(2,14):
        for x in range(12):j.putpixel((x,y),0)
    g['J']=j
    # Native O upper counter, E left stem, T crossbar and N diagonal leg.
    # Never replace the native O/N/E/etc. or horizontally scale their bodies.
    r=Image.new('L',(25,24));o,e,n,t=(g[c] for c in 'OENT')
    r.paste(o.crop((0,0,o.width,11)),(0,0))
    for y in range(11,20):
        for x in range(min(12,e.width)):r.putpixel((x,y),e.getpixel((x,y)))
    for y in range(10,13):
        for x in range(4,21):r.putpixel((x,y),t.getpixel((x,5)))
    for y in range(13,20):
        x0=11+round((y-13)*0.85)
        for dx in range(8):r.putpixel((x0+dx,y),n.getpixel((min(n.width-1,12+dx),y)))
    g['R']=r
    return g


def compose(text):
    Image=pillow();g=glyphs();width=sum(9 if c==' ' else g[c].width for c in text)+len(text)-1
    if width>224:raise ValueError('Native title exceeds border interior')
    out=Image.new('L',(width,24));x=0
    for c in text:
        if c==' ':x+=10;continue
        out.paste(g[c],(x,0));x+=g[c].width+1
    return out


def artwork():
    Image=pillow()
    from PIL import ImageFont,ImageDraw,ImageFilter
    before=original(RESOURCE);record=before[32:66608];meta,_=inspect_texture(record)
    src=Image.frombytes('L',(256,256),unpack_indices(record,meta));out=Image.new('L',(256,256))
    frames=list(FRAMES);frames[0]=(0,0,228,24,114,12,0,0);frames[2]=(0,24,228,48,114,12,0,0)
    rows=[]
    for i,text in enumerate(LABELS):
        im=compose(text);fx,fy,ex,ey,hx,hy,*_=frames[i]
        out.paste(im,(fx+(ex-fx-im.width)//2,fy))
        rows.append({'index':i,'translation':text,'width':im.width,'mask_sha256':sha(im.tobytes())})
    for old,new in (((1,74,6,78),(240,0)),((0,96,228,136),(0,48)),((0,136,228,176),(0,88))):out.paste(src.crop(old),new)
    # Rounded bold small print follows the official credits' body/outline family,
    # rather than the condensed dialogue GFI used by the rejected credit.
    font=ImageFont.truetype(str(FONT),56);probe=ImageDraw.Draw(Image.new('L',(1,1)));box=probe.textbbox((0,0),TEXT,font=font)
    ink=Image.new('L',(box[2]-box[0]+16,64));ImageDraw.Draw(ink).text((8-box[0],4-box[1]),TEXT,font=font,fill=255)
    ink=ink.resize((round(ink.width/4),16),Image.Resampling.LANCZOS);outline=ink.filter(ImageFilter.MaxFilter(3))
    palette=[tuple(record[16+i*4:20+i*4]) for i in range(256)]
    x0=(256-ink.width)//2;y0=238
    if ink.width>252:raise ValueError('Credit exceeds texture')
    for y in range(16):
        for x in range(ink.width):
            alpha=outline.getpixel((x,y))
            if alpha<4:continue
            value=round(255*ink.getpixel((x,y))/alpha);target=(value,value,value,round(alpha*127/255))
            idx=min(range(256),key=lambda k:sum((palette[k][j]-target[j])**2 for j in range(4)))
            out.putpixel((x0+x,y0+y),idx)
    result=bytearray(before);result[32:66608]=replace_indices(record,out.tobytes())
    for i,f in enumerate(frames):struct.pack_into('<8h',result,66624+i*16,*f)
    review={'labels':rows,'frames':[list(f) for f in frames],
        'native_letters_preserved':sorted(set('CONTINUEWGAMS L'.replace(' ',''))),
        'constructed_letters':['V','J','R'],'horizontal_rescale':False,'interglyph_gap':1,
        'credit':{'text':TEXT,'texture_rect':[x0,y0,x0+ink.width,y0+16],
            'screen_rect':[192+x0,428,192+x0+ink.width,444],
            'mask_sha256':sha(ink.tobytes()),'font_file':FONT.name,'font_sha256':sha(FONT.read_bytes()),
            'body_size':14,'outline_pixels':1,'inherits_continue_tint_and_visibility':True}}
    return bytes(result),review


def compile_authentic(config):
    if config.get('policy')!=POLICY:raise ValueError('Unknown native title revision')
    parent=config['parent'];payload=(ROOT/parent['recipe']).read_bytes()
    if parent['recipe']!='translations/interface-graphics-v008.json' or sha(payload)!=parent['sha256']:raise ValueError('Native title parent mismatch')
    before=original(RESOURCE);after,review=artwork()
    if config.get('source_sha256')!=sha(before) or config.get('reviewed_artwork')!=review:raise ValueError('Native title artwork mismatch')
    from interface_graphics import compile_graphics
    patches,report=compile_graphics(json.loads(payload));patches=[p for p in patches if p['resource']!=RESOURCE]
    for a,z,key in ((1072,66608,'title.texture.0'),(66624,66720,'title.frames')):
        patches.append({'resource':RESOURCE,'id':key,'offset':a,'before':before[a:z],'after':after[a:z]})
    results=[r for r in report['results'] if r.get('resource')!=RESOURCE]
    results += [{'id':f'title.label.{r["index"]}','resource':RESOURCE,'texture':0,'family':'title',**r} for r in review['labels']]
    results.append({'id':'title.translation-credit','resource':RESOURCE,'texture':0,'family':'credit',**review['credit']})
    return patches,{**report,'policy':POLICY,'reviewed_artwork':review,'results':results,'runtime_visual_status':'pending_user_verification'}
