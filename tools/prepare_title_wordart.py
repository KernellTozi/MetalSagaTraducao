"""Prepare complete-word art at native PS2 size, without patching game files."""
import argparse,hashlib,json
from pathlib import Path
from reinsertion import ROOT,local
from interface_texture_pack import pillow

LABELS=('NOVO JOGO','RETOMAR','INSTALAR')

def prepare(master,output):
    Image=pillow()
    from PIL import ImageChops,ImageDraw
    master=local(master);output=local(output,True)
    if output.exists():raise ValueError('Use a new output folder')
    with Image.open(master) as opened:
        if opened.mode!='RGBA':raise ValueError('Transparent RGBA master required')
        im=opened.copy()
    alpha=im.getchannel('A');active=[]
    for y in range(im.height):
        if alpha.crop((0,y,im.width,y+1)).getextrema()[1]>=32:
            if active and y==active[-1][-1]+1:active[-1].append(y)
            else:active.append([y])
    groups=[g for g in active if len(g)>im.height//12]
    if len(groups)!=3:raise ValueError('Expected exactly three separated word lines')
    tiles=[];rows=[]
    for i,group in enumerate(groups):
        part=im.crop((0,max(0,group[0]-2),im.width,min(im.height,group[-1]+3)))
        a=part.getchannel('A');rgb=part.convert('RGB')
        core=ImageChops.multiply(rgb.convert('L').point(lambda v:255 if v>=200 else 0),a.point(lambda v:255 if v>=192 else 0))
        box=core.getbbox()
        if not box:raise ValueError('Missing white letter body')
        # One scale factor for the whole word, preserving all letter proportions.
        scale=16/(box[3]-box[1]);bounds=a.point(lambda v:255 if v>=32 else 0).getbbox()
        crop=part.crop(bounds);size=(round(crop.width*scale),round(crop.height*scale))
        if size[0]>224 or size[1]>24:raise ValueError('Word art exceeds title slot')
        tile=crop.resize(size,Image.Resampling.LANCZOS)
        top=4-round((box[1]-bounds[1])*scale)
        if top<0 or top+tile.height>24:raise ValueError('Word art exceeds common baseline cell')
        cell=Image.new('RGBA',(228,24));cell.alpha_composite(tile,((228-tile.width)//2,top))
        tiles.append((crop,cell));rows.append({'text':LABELS[i],'master_core_box':list(box),
            'source_rows':[group[0],group[-1]],'scale_xy':scale,'rendered_size':list(size),
            'cell_size':[228,24],'white_cap_height':16,'cap_top':4,
            'cell_rgba_sha256':hashlib.sha256(cell.tobytes()).hexdigest()})
    output.mkdir(parents=True)
    for name,(crop,cell) in zip(('novo-jogo','retomar','instalar'),tiles):
        crop.save(output/(name+'-master.png'));cell.save(output/(name+'-24px.png'))
    # Original image is a style reference only; no cropped letters compose new art.
    from interface_graphics import original
    from interface_textures import inspect_texture
    raw=original('DATA/RDATA/RTITLE.SDA')[32:66608];meta,rgb=inspect_texture(raw)
    old=Image.frombytes('RGB',(256,256),rgb)
    board=Image.new('RGB',(912,240),(70,73,53));draw=ImageDraw.Draw(board)
    draw.text((8,6),'ORIGINAL / ARTE NOVA - ampliacao 2x',fill='white')
    for i,(_,cell) in enumerate(tiles):
        original_cell=Image.new('RGB',(228,24),(70,73,53));original_cell.paste(old.crop((0,i*24,180,i*24+24)),(24,0))
        board.paste(original_cell.resize((456,48),Image.Resampling.NEAREST),(0,30+i*68))
        bg=Image.new('RGBA',cell.size,(70,73,53,255));bg.alpha_composite(cell)
        board.paste(bg.convert('RGB').resize((456,48),Image.Resampling.NEAREST),(456,30+i*68))
    palette=[tuple(raw[16+i*4:20+i*4]) for i in range(256)]
    palette_cache={};palette_rows=[]
    rgb_palette=[v for c in palette for v in c[:3]]
    alpha_palette=bytes(c[3] for c in palette)
    for name,(_,cell) in zip(('novo-jogo','retomar','instalar'),tiles):
        indices=bytearray()
        rgba=cell.tobytes()
        for pixel_at in range(0,len(rgba),4):
            red,green,blue,alpha=rgba[pixel_at:pixel_at+4]
            if alpha<4:indices.append(0);continue
            target=(red,green,blue,round(alpha*127/255))
            if target not in palette_cache:
                palette_cache[target]=min(range(256),key=lambda k:sum((palette[k][j]-target[j])**2 for j in range(4)))
            indices.append(palette_cache[target])
        indexed=Image.frombytes('P',cell.size,bytes(indices));indexed.putpalette(rgb_palette)
        indexed.save(output/(name+'-paleta-original.png'),transparency=alpha_palette)
        normalized=bytes(v for idx in indices for v in (*palette[idx][:3],min(255,palette[idx][3]*2)))
        Image.frombytes('RGBA',cell.size,normalized).save(output/(name+'-preview-paleta.png'))
        palette_rows.append({'label':name,'indices_sha256':hashlib.sha256(indices).hexdigest(),
            'palette_sha256':hashlib.sha256(raw[16:1040]).hexdigest(),'palette_unchanged':True})
    board.save(output/'comparacao.png')
    # Native 1:1 preview to judge legibility instead of relying on the large master.
    native=Image.new('RGBA',(228,96),(70,73,53,255))
    for i,(_,cell) in enumerate(tiles):native.alpha_composite(cell,(0,i*32))
    native.convert('RGB').save(output/'tamanho-real.png')
    report={'schema':1,'master_sha256':hashlib.sha256(master.read_bytes()).hexdigest(),
        'master_size':list(im.size),'source':'complete words generated from reference; no letter collage',
        'rows':rows,'palette_conversion':palette_rows,'iso_modified':False,'runtime_tested':False,'status':'artwork prepared and quantized; not applied to game'}
    (output/'manifest.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    return report

if __name__=='__main__':
    p=argparse.ArgumentParser(description='Preparar palavras completas do titulo para revisao, sem modificar ISO')
    p.add_argument('--master',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    r=prepare(a.master,a.output);print(f"{len(r['rows'])} palavras preparadas; ISO inalterada")
