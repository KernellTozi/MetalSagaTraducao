"""Local, review-only paint button drawings and paired before/after previews.

New single-purpose pixel strokes, no installed font substitution or glyph
collages. Original indexed palette/crop transport; no ISO integration.
"""
import argparse,json,struct
from pathlib import Path
from reinsertion import ROOT,local
from paint_button_pack import inventory,export,import_pack
from interface_texture_pack import pillow,unpack_indices
from speaker_labels import _run
from dialogue import sha

POLICY='paint-pixel-stroke-proposals-work-only-v001'
TARGETS={0:'Editar',3:'Veículo',4:'Ferramentas',5:'Escolher carimbo',8:'Editar carimbo',9:'Paleta'}
# Native 16-pixel capital body; lowercase baseline 15, x-height starts at 5.
# Every polyline is an authored pixel grid, without font rasterization/scaling.
GLYPHS={
 'E':(8,[[(7,0),(0,0),(0,15),(7,15)],[(0,7),(6,7)]]),
 'F':(8,[[(7,0),(0,0),(0,15)],[(0,7),(6,7)]]),
 'P':(8,[[(0,15),(0,0),(5,0),(7,2),(7,5),(5,7),(0,7)]]),
 'V':(9,[[(0,0),(0,3),(4,15),(8,3),(8,0)]]),
 'a':(7,[[(0,6),(2,5),(4,5),(6,7),(6,15)],[(6,9),(2,9),(0,11),(0,13),(2,15),(4,15),(6,13)]]),
 'b':(7,[[(0,0),(0,15)],[(0,7),(2,5),(4,5),(6,7),(6,13),(4,15),(2,15),(0,13)]]),
 'c':(7,[[(6,6),(4,5),(2,5),(0,7),(0,13),(2,15),(4,15),(6,14)]]),
 'd':(7,[[(6,0),(6,15)],[(6,7),(4,5),(2,5),(0,7),(0,13),(2,15),(4,15),(6,13)]]),
 'e':(7,[[(0,10),(6,10),(6,7),(4,5),(2,5),(0,7),(0,13),(2,15),(4,15),(6,14)]]),
 'h':(7,[[(0,0),(0,15)],[(0,7),(2,5),(4,5),(6,7),(6,15)]]),
 'i':(1,[[(0,0),(0,1)],[(0,5),(0,15)]]),
 'í':(3,[[(2,0),(0,2)],[(0,5),(0,15)]]),
 'l':(1,[[(0,0),(0,15)]]),
 'm':(11,[[(0,5),(0,15)],[(0,7),(2,5),(3,5),(5,7),(5,15)],[(5,7),(7,5),(8,5),(10,7),(10,15)]]),
 'n':(7,[[(0,5),(0,15)],[(0,7),(2,5),(4,5),(6,7),(6,15)]]),
 'o':(7,[[(2,5),(4,5),(6,7),(6,13),(4,15),(2,15),(0,13),(0,7),(2,5)]]),
 'r':(6,[[(0,5),(0,15)],[(0,8),(2,5),(4,5),(5,6)]]),
 's':(7,[[(6,6),(4,5),(2,5),(0,7),(0,8),(2,10),(4,10),(6,12),(6,13),(4,15),(2,15),(0,14)]]),
 't':(5,[[(2,1),(2,13),(3,15),(4,15)],[(0,5),(4,5)]]),
 'u':(7,[[(0,5),(0,13),(2,15),(4,15),(6,13)],[(6,5),(6,15)]]),
}
WINDOWS=((0x5c728,0x5c744),(0x5c768,0x5c788))


def usage_proof(elf,raw):
    """Original table argument forwarding only, with supplied owner/source base."""
    from paint_captions import SOURCE_SHA
    from glyph_spacing import ORIGINAL_SHA
    if sha(elf)!=ORIGINAL_SHA or sha(raw)!=SOURCE_SHA:raise ValueError('Paint consumer source differs')
    from explore_interface_atlases import inspect
    records={r['entry']:r for r in inspect(raw) if r['node_offset']==0}
    cases=[]
    for index,(texture,ganm) in enumerate(((11,12),(13,14),(15,16),(17,18))):
        table=0x318ea0+index*8;pair=elf[table:table+8];gtable=0x318ec0+index*4
        if struct.unpack('<II',pair)!=(records[texture]['offset'],records[texture]['size']):
            raise ValueError('Paint original texture table differs')
        if struct.unpack_from('<I',elf,gtable)[0]!=records[ganm]['offset']:
            raise ValueError('Paint original GANM table differs')
        r=[0]*32;r[16]=0x318ea0+0xff000+index*8;r[17]=0x620000+index*0x150;r[22]=0x600000
        result=_run(elf,0x5c728,WINDOWS,r,[(0x318ea0+0xff000,elf[0x318ea0:0x318ec0])],0x1acc58)
        if (result[4],result[5],result[6],result[7],result[8])!=(0x620000+index*0x150,0x600000+records[texture]['offset'],0,records[texture]['size'],0):
            raise ValueError('Paint texture arguments differ')
        r=[0]*32;r[19]=0x318ec0+0xff000+index*4;r[16]=0x630000+index*64;r[22]=0x600000
        result=_run(elf,0x5c768,WINDOWS,r,[(0x318ec0+0xff000,elf[0x318ec0:0x318ed0])],0x19af80)
        if (result[4],result[5])!=(0x630000+index*64,0x600000+records[ganm]['offset']):
            raise ValueError('Paint GANM arguments differ')
        cases.append({'index':index,'texture_entry':texture,'ganm_entry':ganm,
            'texture_offset':records[texture]['offset'],'ganm_offset':records[ganm]['offset'],
            'texture_table_offset':table,'ganm_table_offset':gtable,'forwarding_executed':True})
    return {'cases':cases,'bound_windows':[{'kind':'code' if a<0x318ea0 else 'data-table',
        'offset':a,'size':z-a,'sha256':sha(elf[a:z])} for a,z in WINDOWS+((0x318ea0,0x318ee4),)],
        'limits':'Two original integer argument windows executed for each table row. Owner/source bases supplied; uploads, drawing, selection, full dispatch and PCSX2 not executed.'}


def mask(text):
    Image=pillow()
    from PIL import ImageDraw
    if not text or any(c not in GLYPHS and c!=' ' for c in text):raise ValueError('Unmapped proposal glyph')
    advances=[5 if c==' ' else GLYPHS[c][0]+3 for c in text]
    out=Image.new('L',(sum(advances)-2,18));draw=ImageDraw.Draw(out);x=1
    for c,advance in zip(text,advances):
        if c!=' ':
            for line in GLYPHS[c][1]:draw.line([(x+a,1+b) for a,b in line],fill=255,width=1)
        x+=advance
    return out


def render_crop(before,text):
    Image=pillow();im=before.copy()
    if im.mode!='P' or im.size!=(238,29):raise ValueError('Unexpected main paint cell')
    glyph=mask(text)
    if glyph.width>im.width-12:raise ValueError('Paint proposal width overflow; no scaling allowed')
    pixels=bytearray(im.tobytes());bg=2
    # Preserve the entire two-pixel frame, including source alpha/index detail.
    for y in range(2,27):pixels[y*238+2:y*238+236]=bytes([bg])*234
    ox=(238-glyph.width)//2;oy=4
    # Original palette only: black bevel, bright left edge, medium front face.
    for dx,dy,color in ((1,1,14),(-1,0,10),(0,0,8)):
        for y in range(glyph.height):
            for x in range(glyph.width):
                if glyph.getpixel((x,y)):pixels[(oy+y+dy)*238+ox+x+dx]=color
    im.frombytes(bytes(pixels))
    return im,{'translation':text,'mask_sha256':sha(glyph.tobytes()),'width':glyph.width,
        'capital_body_pixels':16,'baseline_in_crop':20,'horizontal_scale':1,
        'font':'authored integer pixel strokes; original indexed palette; review-only'}


def preview(folder,manifest):
    Image=pillow();from PIL import ImageDraw
    rows=[r for r in manifest['entries'] if r['texture_entry']==13 and r['sprite_index'] in TARGETS]
    sheet=Image.new('RGB',(1020,85+len(rows)*86),(30,34,38));d=ImageDraw.Draw(sheet)
    d.text((25,18),'ORIGINAL',fill='white');d.text((535,18),'PROPOSTA PT-BR - AINDA FORA DA ISO',fill='white')
    d.text((25,42),'Mesma escala nas duas colunas (2x). Desenho proposto para revisao.',fill=(200,205,210))
    for i,row in enumerate(rows):
        for side,path in enumerate((folder/'originais'/row['png'],folder/'botoes'/row['png'])):
            im=Image.open(path).convert('RGBA').convert('RGB').resize((476,58),Image.Resampling.NEAREST)
            sheet.paste(im,(25+side*510,75+i*86))
        d.text((535,136+i*86),TARGETS[row['sprite_index']],fill=(185,205,220))
    sheet.save(folder/'comparacao-pintura.png')
    return folder/'comparacao-pintura.png'


def verify_caption_overlay(raw,proposed,elf):
    """Test independent art + current captions in memory; do not write an ISO.

    Never import a whole original-based SDA over already translated captions.
    The future art patch must contain only the original texture pixel plane.
    """
    from paint_captions import compile_captions
    from gfi import decode
    draft_path=ROOT/'translations/interface-v039.json'
    draft=json.loads(draft_path.read_text(encoding='utf-8'))
    captions,caption_report=compile_captions(elf,draft['paint_captions'],raw=raw)
    _,manifest=inventory();row=next(r for r in manifest['entries'] if r['texture_entry']==13)
    meta=row['texture'];start=row['texture_offset']+meta['pixel_offset'];end=start+meta['pixel_bytes']
    if len(raw)!=len(proposed) or proposed[:start]!=raw[:start] or proposed[end:]!=raw[end:]:
        raise ValueError('Proposal changes something outside main texture pixels')
    before=raw[row['texture_offset']:row['texture_offset']+row['texture_size']]
    after=proposed[row['texture_offset']:row['texture_offset']+row['texture_size']]
    old=unpack_indices(before,meta);new=unpack_indices(after,meta)
    rects=[r['rect'] for r in manifest['entries'] if r['texture_entry']==13 and r['sprite_index'] in TARGETS]
    for index,(a,b) in enumerate(zip(old,new)):
        if a!=b and not any(x+2<=index%meta['width']<z-2 and y+2<=index//meta['width']<w-2 for x,y,z,w in rects):
            raise ValueError('Proposal changes outside six crop interiors')
    combined=bytearray(proposed)
    for p in captions:
        a=p['offset'];z=a+len(p['before'])
        if max(a,start)<min(z,end) or combined[a:z]!=p['before']:raise ValueError('Caption/art overlap or source mismatch')
        combined[a:z]=p['after']
        if decode(bytes(combined[a:z]).split(b'\0',1)[0])!=decode(p['after'].split(b'\0',1)[0]):
            raise ValueError('Translated caption readback differs')
    restored=bytearray(combined);restored[start:end]=raw[start:end]
    for p in captions:restored[p['offset']:p['offset']+len(p['before'])]=p['before']
    if restored!=raw:raise ValueError('Caption/art combined reverse round-trip differs')
    return {'recipe':draft_path.relative_to(ROOT).as_posix(),'recipe_sha256':sha(draft_path.read_bytes()),
        'caption_fields_preserved':caption_report['accepted'],'caption_art_overlap':False,
        'future_art_pixel_offset':start,'future_art_pixel_bytes':end-start,
        'future_art_pixel_sha256':sha(proposed[start:end]),'combined_resource_sha256':sha(combined),
        'combined_reverse_roundtrip':True,'combined_only_in_memory':True,
        'iso_integration':False,'limits':'Tests only S_PAINT pixel/caption composition, not live menu selection or rendering.'}


def run(output):
    from interface_text import SOURCE
    output=local(output,True);raw,manifest=inventory();proof=usage_proof(SOURCE.read_bytes(),raw)
    export(output/'originais');export(output/'botoes');Image=pillow();changed=[]
    for row in manifest['entries']:
        index=row['sprite_index']
        if row['texture_entry']!=13 or index not in TARGETS:continue
        path=output/'botoes'/row['png']
        with Image.open(path) as before:after,layout=render_crop(before,TARGETS[index])
        alpha=after.info['transparency'];after.save(path,bits=8,transparency=alpha)
        changed.append({'id':row['id'],'png_sha256':sha(path.read_bytes()),**layout})
    imported=import_pack(output/'botoes',output/'reconstruido')
    overlay=verify_caption_overlay(raw,(output/'reconstruido/S_PAINT.SDA').read_bytes(),SOURCE.read_bytes())
    image=preview(output,manifest)
    report={'schema':1,'policy':POLICY,'source_sha256':manifest['source_sha256'],'elf_sha256':manifest['elf_sha256'],
        'proposed_labels':changed,'preserved_crop_ids':[r['id'] for r in manifest['entries'] if r['id'] not in {c['id'] for c in changed}],
        'usage_proof':proof,'work_copy_import':imported,'caption_overlay':overlay,'preview':image.relative_to(ROOT).as_posix(),
        'iso_modified':False,'pcsx2_executed':False,'art_approval':'pending_user_review',
        'limits':'Six proposed drawings only. Main mixed label, SUB/SE, Zoom, component and stamp-background captions remain original. Source-table binding does not prove complete live dispatch.'}
    with (output/'relatorio.json').open('x',encoding='utf-8') as f:json.dump(report,f,ensure_ascii=False,indent=2);f.write('\n')
    return report


if __name__=='__main__':
    p=argparse.ArgumentParser(description='Preparar seis desenhos de pintura e comparacao visual, sem ISO')
    p.add_argument('--output',required=True,type=Path);a=p.parse_args();r=run(a.output)
    print(r['preview'])
