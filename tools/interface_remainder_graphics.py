"""Bounded remaining paint labels and five complete instruction panels.

Only indexed pixel planes change. Original frames, controller pictures,
palette/alpha, sprite geometry and all other minigame atlases stay intact.
"""
import json,struct
from collections import Counter
from functools import lru_cache
from pathlib import Path
from reinsertion import ROOT,local
from dialogue import sha
from interface_texture_pack import pillow,unpack_indices,replace_indices
from interface_graphics import original,mask as native_mask
from explore_interface_atlases import inspect

PAINT_POLICY='paint-six-approved-plus-chassi-and-stamp-labels-v002'
RULE_POLICY='five-latin-minigame-instruction-panels-v001'
PARENT='translations/interface-v046.json'

# Coordinates refer to original 512x512 index images, not screenshots.
# Icons are copied verbatim and never redrawn. No WIN/LOSE/ROUND atlas here.
PANELS={
 'RMGALAN.0.001':{'resource':'DATA/RDATA/RMGALAN.SDA','entry':1,'ganm':2,'operations':[
  ('text',None,14,26,'Regras'),
  ('paragraph',38,50,18,"Desvie dos ataques do tanque e chegue primeiro. Avance quando a torre não estiver mirando em você. Deitado, você sai da mira, mas o canhão ainda pode atingi-lo."),
  ('icon',(172,126,227,160),38,169),
  ('paragraph',108,174,18,'Esbarrar em um gato faz você tropeçar.'),
  ('paragraph',38,214,18,'Chegue em primeiro antes de o tempo acabar para vencer!'),
  ('text',None,265,24,'Controles'),
  ('icon',(86,255,112,280),52,301),('text',92,304,18,'Aperte várias vezes para avançar'),
  ('icon',(86,287,112,313),52,343),('text',92,346,18,'Deitar') ]},
 'RMGDANCE.0.000':{'resource':'DATA/RDATA/RMGDANCE.SDA','entry':0,'ganm':1,'operations':[
  ('text',None,14,26,'Regras'),
  ('paragraph',38,54,18,'Memorize e imite as poses dos Muscle Men. Observe as poses e repita-as com o direcional.'),
  ('icon',(295,90,406,118),38,116),('text',170,120,18,'Observe as poses'),
  ('icon',(319,124,419,149),38,151),('text',170,154,18,'Repita na mesma ordem'),
  ('icon',(219,183,333,213),38,186),('paragraph',170,190,18,'Pose diferente da rodada anterior'),
  ('paragraph',38,236,18,'Uma pose errada ou o tempo esgotado encerram o jogo. Vamos lá, mostre esses músculos!'),
  ('text',None,302,24,'Controles'),
  ('icon',(135,329,162,358),94,343),('text',141,348,18,'Direcional: fazer pose') ]},
 'RMGDANCE.0.015':{'resource':'DATA/RDATA/RMGDANCE.SDA','entry':15,'ganm':16,'operations':[
  ('text',None,14,26,'Regras'),
  ('paragraph',38,54,18,'Memorize e imite os movimentos dos dançarinos. Observe a dança e repita-a com o direcional.'),
  ('icon',(274,80,389,110),38,116),('text',170,120,18,'Observe os movimentos'),
  ('icon',(63,137,176,166),38,151),('text',170,154,18,'Repita na mesma ordem'),
  ('icon',(296,166,411,196),38,186),('paragraph',170,190,18,'Movimento diferente da rodada anterior'),
  ('paragraph',38,236,18,'Um passo errado ou o tempo esgotado encerram o jogo. Agora, solte o corpo!'),
  ('text',None,302,24,'Controles'),
  ('icon',(113,316,142,346),94,343),('text',141,348,18,'Direcional: dançar') ]},
 'RMGKAERU.0.000':{'resource':'DATA/RDATA/RMGKAERU.SDA','entry':0,'ganm':1,'operations':[
  ('text',None,12,26,'Regras'),
  ('paragraph',38,49,18,'Adivinhe qual sapo vai chegar primeiro. Faça sua aposta e a corrida começa. Se o seu sapo vencer, você ganha. Simples assim!'),
  ('text',None,133,24,'Controles'),('text',None,162,18,'Aposta'),
  ('icon',(119,183,146,211),72,188),('text',115,193,18,'Aumentar aposta'),
  ('icon',(119,215,146,242),72,223),('text',115,228,18,'Diminuir aposta'),
  ('text',None,261,18,'Escolher sapo'),
  ('icon',(119,272,147,300),72,288),('text',115,292,18,'Mover cursor'),
  ('icon',(119,303,146,330),72,321),('text',115,326,18,'Confirmar'),
  ('text',38,365,18,'Para correr: selecione'),
  ('icon',(290,333,361,356),240,360),('text',320,365,18,'e aperte'),
  ('icon',(119,183,146,211),440,358) ]},
 'RMGTANK.0.000':{'resource':'DATA/RDATA/RMGTANK.SDA','entry':0,'ganm':1,'operations':[
  ('text',None,12,26,'Regras'),
  ('paragraph',38,49,18,'Destrua o máximo de inimigos que puder e desvie dos ataques. Ao destruir um inimigo, uma cápsula pode aparecer:'),
  ('icon',(38,101,68,122),38,121),('text',83,124,18,'Invencibilidade temporária'),
  ('icon',(38,125,68,146),38,152),('text',83,155,18,'Disparos rápidos por um tempo'),
  ('icon',(38,149,68,171),38,183),('text',83,186,18,'Movimento mais rápido por um tempo'),
  ('icon',(39,185,109,219),38,216),('paragraph',123,222,18,'Atirar neles impede você de se mover por um tempo.'),
  ('paragraph',38,268,18,'O jogo acaba quando suas vidas ou o tempo se esgotam.'),
  ('text',None,309,24,'Controles'),
  ('icon',(119,302,147,330),38,347),('text',77,351,18,'Mover: esq./dir.'),
  ('icon',(119,333,146,361),247,347),('text',287,351,18,'Atirar') ]},
}

def indexed(raw,row):
    Image=pillow();meta=row['texture'];a=row['offset'];rec=raw[a:a+row['size']]
    pal=rec[16:meta['pixel_offset']];count=1<<meta['bpp']
    image=Image.frombytes('P',(meta['width'],meta['height']),unpack_indices(rec,meta))
    image.putpalette(bytes(c for i in range(count) for c in pal[4*i:4*i+3])+bytes(768-count*3))
    image.info['transparency']=bytes(pal[4*i+3] for i in range(count))
    return image,rec

@lru_cache(maxsize=2048)
def lettering(text,height):
    image,layout=native_mask(text,height,10000)
    if layout['horizontal_scale']!=1:raise ValueError('No condensed lettering allowed')
    return image

def paragraph(text,width,height):
    lines=[];line=''
    for word in text.split(' '):
        trial=(line+' '+word).strip()
        if lettering(trial,height).width<=width:line=trial
        else:
            if not line or lettering(word,height).width>width:raise ValueError('Unbreakable panel text')
            lines.append(line);line=word
    if line:lines.append(line)
    return lines

@lru_cache(maxsize=16)
def palette_ramp(pal,alpha,background):
    bg=pal[background*3:background*3+3]
    indices=[i for i in range(len(alpha)) if alpha[i]>0]
    lookup=[]
    for level in range(256):
        rgb=[round(a+(b-a)*level/255) for a,b in zip(bg,(185,182,181))]
        lookup.append(min(indices,key=lambda i:sum((pal[i*3+k]-rgb[k])**2 for k in range(3))))
    return lookup

def draw_text(image,text,x,y,height,background,occupied):
    glyph=lettering(text,height)
    if x is None:x=(image.width-glyph.width)//2
    box=(x,y,x+glyph.width,y+glyph.height)
    if not (4<=box[0]<box[2]<=508 and 4<=box[1]<box[3]<=396):raise ValueError('Panel lettering outside original frame')
    # Occupancy catches accidental row/icon collision, including accents.
    if any(box[0]<b[2] and b[0]<box[2] and box[1]<b[3] and b[1]<box[3] for b in occupied):raise ValueError('Panel text/icon overlap')
    occupied.append(box)
    lookup=palette_ramp(tuple(image.getpalette()),image.info['transparency'],background)
    for yy in range(glyph.height):
        for xx in range(glyph.width):
            value=glyph.getpixel((xx,yy))
            if value:image.putpixel((x+xx,y+yy),lookup[value])
    return list(box)

def render_panel(raw,row,spec):
    source,record=indexed(raw,row)
    if source.size!=(512,512) or row['texture']['bpp']!=8:raise ValueError('Rules texture revision differs')
    out=source.copy();out.info=source.info.copy()
    background=Counter(source.crop((4,4,508,396)).tobytes()).most_common(1)[0][0]
    out.paste(background,(4,4,508,396));occupied=[];text_rows=[];icons=[]
    for op in spec['operations']:
        if op[0]=='icon':
            _,rect,x,y=op;icon=source.crop(rect);box=(x,y,x+icon.width,y+icon.height)
            if not (4<=x<box[2]<=508 and 4<=y<box[3]<=396):raise ValueError('Icon outside frame')
            if any(x<b[2] and b[0]<box[2] and y<b[3] and b[1]<box[3] for b in occupied):raise ValueError('Icon overlaps panel text')
            occupied.append(box);out.paste(icon,(x,y));icons.append({'source_rect':list(rect),'target_rect':list(box),'indices_sha256':sha(icon.tobytes())})
        else:
            kind,x,y,h,text=op;lines=paragraph(text,474-x,h) if kind=='paragraph' else [text]
            for i,line in enumerate(lines):
                box=draw_text(out,line,x,y+i*(h+2),h,background,occupied)
                text_rows.append({'text':line,'rect':box,'height':h,'horizontal_scale':1})
    old=source.tobytes();new=out.tobytes()
    for i,(a,b) in enumerate(zip(old,new)):
        if a!=b and not (4<=i%512<508 and 4<=i//512<396):raise ValueError('Panel frame or bottom padding changed')
    after=replace_indices(record,new);p=row['texture']['pixel_offset'];n=row['texture']['pixel_bytes']
    if after[:p]!=record[:p] or after[p+n:]!=record[p+n:] or replace_indices(after,old)!=record:raise ValueError('Rules palette/alpha/reverse roundtrip differs')
    return {'id':row['id']+'.ptbr-instructions','resource':row['resource'],'offset':row['offset']+p,
        'before':record[p:p+n],'after':after[p:p+n]}, {'id':row['id'],'source_texture_sha256':sha(record),
        'target_pixels_sha256':sha(after[p:p+n]),'rows':text_rows,'icons':icons,
        'frame_and_bottom_padding_unchanged':True,'reverse_roundtrip':True},source,out

def rules_assets():
    from interface_atlas_pack import entries
    resources={v['resource']:original(v['resource']) for v in PANELS.values()}
    rows={r['id']:r for r in entries(resources)};result=[]
    for key,spec in PANELS.items():
        row=rows[key];raw=resources[row['resource']]
        geometry=next(r for r in inspect(raw) if r['node_offset']==0 and r['entry']==spec['ganm'])
        if geometry['kind']!='ganm' or len(geometry['sprites'])!=1 or geometry['sprites'][0]['rect']!=[0,0,512,400]:raise ValueError('Full rules panel geometry differs')
        patch,report,before,after=render_panel(raw,row,spec)
        report.update(source_sha256=sha(raw),texture_offset=row['offset'],ganm_offset=geometry['offset'],
            ganm_sha256=geometry['sha256'],full_panel_rect=[0,0,512,400])
        result.append((patch,report,before,after))
    return result

def rules_config():
    return {'policy':RULE_POLICY,'font_profile':'existing-gfi-refined-v002-26px-native-mask',
        'entries':[r for _,r,_,_ in rules_assets()]}

def compile_rules(value):
    assets=rules_assets();expected={'policy':RULE_POLICY,'font_profile':'existing-gfi-refined-v002-26px-native-mask','entries':[r for _,r,_,_ in assets]}
    if value!=expected:raise ValueError('Rules recipe/source/translation/geometry/raster differs')
    return [p for p,_,_,_ in assets],{'policy':RULE_POLICY,'accepted':5,'unit':'complete instruction panels',
        'results':expected['entries'],'decorative_titles_and_wanted_posters_unchanged':True,
        'runtime_visual_status':'pending_user_verification',
        'limits':'Source-bound indexed transport and adjacent full-panel GANM geometry; source image contents inspected. No complete consumer census, controller/render loop or PCSX2 execution.'}

def stamp_proof(elf,raw,manifest):
    from speaker_labels import _run
    from glyph_spacing import ORIGINAL_SHA
    if sha(elf)!=ORIGINAL_SHA:raise ValueError('Stamp original ELF differs')
    row=next(r for r in manifest['entries'] if r['id']=='paint.button.08.19')
    if (row['texture_offset'],row['texture_size'],row['ganm_offset'])!=(0xf140,0x4410,0x13550):raise ValueError('Stamp source extents differ')
    owner=bytearray(0x200);context=bytearray(0x3c);struct.pack_into('<I',context,0x38,0x600000)
    regs=[0]*32;regs[16]=0x620000;regs[2]=0x630000;regs[3]=0xf140
    windows=((0x64a34,0x64a70),)
    a=_run(elf,0x64a34,windows,regs,[(0x620000,owner),(0x630000,context)],0x1acc58)
    if (a[4],a[5],a[6],a[7],a[8])!=(0x620020,0x60f140,0,0x4410,0):raise ValueError('Stamp texture forwarding differs')
    a=_run(elf,0x64a54,windows,a,[(0x620000,owner),(0x630000,context)],0x19af80)
    if (a[4],a[5])!=(0x620170,0x613550):raise ValueError('Stamp GANM forwarding differs')
    return {'bound_windows':[{'offset':a,'size':z-a,'sha256':sha(elf[a:z])} for a,z in windows],
        'texture_entry':8,'ganm_entry':9,'sprite_index':19,'source_sha256':sha(raw),
        'texture_and_ganm_forwarding_executed':True,
        'limits':'Two bounded scalar argument windows with supplied owner/context/source bases. Sprite draw dispatch, palette upload, controls and PCSX2 not executed.'}

def paint_assets():
    from paint_button_pack import inventory
    from paint_menu_graphics import render as render_six
    from paint_graphic_proposals import mask as paint_mask,GLYPHS
    raw,manifest=inventory();old_patch,approved=render_six(raw,manifest)
    # One additional authored capital; all existing glyphs and six approved cells unchanged.
    GLYPHS.setdefault('C',(9,[[(8,1),(6,0),(2,0),(0,2),(0,13),(2,15),(6,15),(8,14)]]))
    result=[]
    for texture,sprite,box,text in ((13,1,(14,2,104,27),'Chassi'),(6,0,(2,2,62,22),'Chassi'),(8,19,(2,2,46,22),'Editar')):
        row=next(r for r in manifest['entries'] if r['texture_entry']==texture and r['sprite_index']==sprite)
        atlasrow={'offset':row['texture_offset'],'size':row['texture_size'],'texture':row['texture']}
        source,record=indexed(raw,atlasrow);out=source.copy();out.info=source.info.copy()
        if texture==13:
            composed=bytearray(record);p=row['texture']['pixel_offset'];composed[p:p+len(old_patch['after'])]=old_patch['after']
            out.frombytes(unpack_indices(composed,row['texture']))
        x,y,z,w=row['rect'];crop=source.crop(row['rect']);b0,b1,b2,b3=box
        # Preserve the original Main Gun half of the mixed label verbatim.
        glyph=paint_mask(text)
        if texture==8:
            # Native stamp caption is a smaller cell; uniform scaling only.
            glyph=glyph.resize((round(glyph.width*14/18),14),pillow().Resampling.LANCZOS)
        if glyph.width>b2-b0-2 or glyph.height>b3-b1:raise ValueError('Chassi label overflow')
        background=Counter(crop.crop(box).tobytes()).most_common(1)[0][0]
        if texture==8:
            pal=source.getpalette()
            # The old word occupies much of this small crop: its light face
            # must not be mistaken for the green button background.
            counts=Counter(crop.crop(box).tobytes())
            background=max((i for i in counts if 30<sum(pal[i*3:i*3+3])/3<85),key=counts.get)
        out.paste(background,(x+b0,y+b1,x+b2,y+b3))
        gx=x+b0+(b2-b0-glyph.width)//2;gy=y+b1+(b3-b1-glyph.height)//2
        if texture==13:
            for dx,dy,color in ((1,1,14),(-1,0,10),(0,0,8)):
                for yy in range(glyph.height):
                    for xx in range(glyph.width):
                        if glyph.getpixel((xx,yy))>127:out.putpixel((gx+xx+dx,gy+yy+dy),color)
        else:
            alpha=source.info['transparency'];pal=source.getpalette()
            foreground=max((i for i in range(len(alpha)) if alpha[i]==alpha[background]),key=lambda i:sum(pal[3*i:3*i+3]))
            if texture==8:
                foreground=min((i for i in range(len(alpha)) if alpha[i]==128),key=lambda i:sum((v-189)**2 for v in pal[i*3:i*3+3]))
            for yy in range(glyph.height):
                for xx in range(glyph.width):
                    if glyph.getpixel((xx,yy))>100:out.putpixel((gx+xx,gy+yy),foreground)
        before=source.tobytes();afterindices=out.tobytes()
        baseline=unpack_indices(bytes(composed),row['texture']) if texture==13 else before
        for i,(a,b) in enumerate(zip(baseline,afterindices)):
            if a!=b and not (x+b0<=i%source.width<x+b2 and y+b1<=i//source.width<y+b3):raise ValueError('Chassi outside declared subrectangle')
        after=replace_indices(record,afterindices);p=row['texture']['pixel_offset'];n=row['texture']['pixel_bytes']
        if after[:p]!=record[:p] or replace_indices(after,before)!=record:raise ValueError('Chassi palette/reverse roundtrip differs')
        patch={'id':old_patch['id'] if texture==13 else 'paint.component.chassi' if texture==6 else 'paint.stamp.editar','resource':manifest['resource'],
            'offset':row['texture_offset']+p,'before':record[p:p+n],'after':after[p:p+n]}
        result.append((patch,{'id':row['id'],'translation':text,'changed_rect':[x+b0,y+b1,x+b2,y+b3],
            'target_pixels_sha256':sha(patch['after']),'original_ganm_sha256':row['ganm_sha256'],
            'base_six_approved_cells_unchanged':True,'mixed_main_gun_original_pixels_unchanged':True},source,out))
    return result

def paint_config(elf):
    from paint_menu_graphics import config
    raw,manifest=__import__('paint_button_pack').inventory()
    return {'policy':PAINT_POLICY,'parent_six_buttons':config(elf),
        'component_forwarding_windows':manifest['instruction_windows'],'stamp_forwarding':stamp_proof(elf,raw,manifest),
        'entries':[r for _,r,_,_ in paint_assets()]}

def compile_paint(elf,value):
    if value!=paint_config(elf):raise ValueError('Remaining paint source/geometry/raster differs')
    assets=paint_assets()
    return [p for p,_,_,_ in assets],{'policy':PAINT_POLICY,'accepted':9,'preserved_approved_buttons':6,'new_labels':3,
        'results':[r for _,r,_,_ in assets],'reverse_roundtrip':True,
        'runtime_visual_status':'pending_user_verification','protected_SUB_SE_MAIN_pixels_unchanged':True}

def validate_interface(recipe):
    if 'native_fallback_review' in recipe:
        from dialogue_native_eight import validate_interface as validate_native
        return validate_native(recipe)
    binding=recipe['interface_remainder_review']
    if set(binding)!={'parent_recipe','parent_sha256'} or binding['parent_recipe']!=PARENT:raise ValueError('Remainder parent scope differs')
    raw=(ROOT/PARENT).read_bytes()
    if sha(raw)!=binding['parent_sha256']:raise ValueError('Remainder parent changed')
    expected=json.loads(raw)
    from interface_text import SOURCE
    expected.update(paint_menu_graphics=paint_config(SOURCE.read_bytes()),minigame_rules_graphics=rules_config(),
        interface_remainder_review=binding,iso_name='MetalSaga-ptbr-interface-v047.iso',
        status='Cinco painéis de instruções e três rótulos de pintura; base v046 integralmente preservada.')
    if recipe!=expected:raise ValueError('Non-authorized interface remainder change')

def preview(folder):
    folder=local(folder,True);folder.mkdir(parents=True);Image=pillow();from PIL import ImageDraw
    assets=rules_assets()+paint_assets();paths=[]
    for _,report,before,after in assets:
        if report['id'].startswith('paint.'):
            rect=([0,32,238,61] if report['id']=='paint.button.13.01' else [0,0,64,24] if report['id']=='paint.button.06.00' else [64,72,112,96])
            before=before.crop(rect).resize(((rect[2]-rect[0])*2,(rect[3]-rect[1])*2),Image.Resampling.NEAREST)
            after=after.crop(rect).resize(before.size,Image.Resampling.NEAREST)
        else:before=before.crop((0,0,512,400));after=after.crop((0,0,512,400))
        sheet=Image.new('RGB',(before.width*2+24,before.height+45),(28,32,36));draw=ImageDraw.Draw(sheet)
        draw.text((6,8),'ORIGINAL',fill='white');draw.text((before.width+18,8),'PT-BR - VALIDACAO NO JOGO PENDENTE',fill='white')
        sheet.paste(before.convert('RGB'),(0,36));sheet.paste(after.convert('RGB'),(before.width+24,36))
        path=folder/(report['id']+'.png');sheet.save(path);paths.append(str(path))
    (folder/'indice.json').write_text(json.dumps(paths,indent=2)+'\n',encoding='utf-8')
    return paths

if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser(description='Comparar as instruções e os dois rótulos de pintura, sem alterar a ISO')
    p.add_argument('--preview',type=Path,required=True);a=p.parse_args();print('\n'.join(preview(a.preview)))
