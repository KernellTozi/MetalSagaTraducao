"""Exact screenshot-driven fixes: three ELF literals, typed exits, one banner.

No general release of scene names, unknown strings, pointers or map records.
"""
import copy,json,mmap,struct
from dialogue import ROOT,sha
from glyph_spacing import ORIGINAL_SHA
from interface_text import SOURCE as ELF,controls
from gfi import encode
from spack_battle import _run
from spack_ui import _reader

POLICY='satcom-observed-gaps-and-fixed-exit-labels-v001'
PARENT='translations/interface-v055.json'
MANIFEST='translations/satcom-lacunas-v001.json'
RESOURCE='DATA/MAP/MAP.MCT'
FBS='DATA/FDATA/FBS_DATA.SDA'
STATUS='Lacunas observadas de lojas, meta financeira e saídas; cabeçalho nativo do tempo de jogo.'
LITERALS={0x32cb78:'Qual loja?',0x32c1c0:'Atual:        %8dG',0x32c248:'Meta:         %8dG\n'}
EXIT_SOURCE=b'Overworld Map'
EXIT_TARGET=b'Mapa do mundo'
WINDOWS=((0x1253b4,0x1253ec),(0x12cb80,0x12cc1c),
         (0x12002c,0x12004c),(0x120610,0x120638),
         (0x445e8,0x44630),(0x44f74,0x44fac),(0x45064,0x450cc),
         (0x7e408,0x7e448),(0x7e7e0,0x7e820),
         (0x7e5c0,0x7e5c8),(0x7e988,0x7e990),
         (0x304e78,0x304f28),(0x47328,0x473a8))


def probes(elf):
    if sha(elf)!=ORIGINAL_SHA:raise ValueError('Observed gap ELF differs')
    # Mode 1 branch: the LUI is in a delay slot, missed by the old scanner.
    regs=[0]*32;regs[2]=regs[3]=1;regs[16]=0x610000
    shop=_run(elf,0x1253b8,0x1253ec,regs,_reader([]),0x12cb80)
    if shop[5]!=0x42bb78 or shop[4]!=0x610000:raise ValueError('Shop literal forwarding differs')
    regs=[0]*32;regs[3]=0x620000;regs[17]=0x475280
    read=_reader([(0x475580,struct.pack('<I',0x630000)),
                  (0x620004,struct.pack('<I',0x640000)),(0x630044,struct.pack('<I',200))])
    current=_run(elf,0x120034,0x12004c,regs,read,0x10e608)
    if (current[5],current[6])!=(0x42b1c0,200):raise ValueError('Current formatter arguments differ')
    regs=[0]*32;regs[2]=500;regs[3]=0x610000
    target=_run(elf,0x120620,0x120630,regs,_reader([(0x6101e8,struct.pack('<I',0x640000))]),0x120630)
    if (target[5],target[6])!=(0x42b248,500):raise ValueError('Target formatter arguments differ')
    getters=[]
    for typ,vtable,getter in ((6,0x403ed0,0x7e5c0),(7,0x403e78,0x7e988)):
        if struct.unpack_from('<I',elf,vtable-0xff000+0x4c)[0]!=getter+0xff000:
            raise ValueError('Exit name virtual getter differs')
        regs=[0]*32;regs[4]=0x610000
        r=_run(elf,getter+4,getter+8,regs,_reader([(0x61003c,struct.pack('<I',0x620000))]),getter+8)
        if r[2]!=0x620000:raise ValueError('Exit payload getter differs')
        getters.append({'type':typ,'vtable':vtable,'getter_file_offset':getter,'payload_pointer_returned':True})
    return {'shop_pointer':shop[5],'current_pointer':current[5],'current_model_value':current[6],
            'target_pointer':target[5],'target_model_value':target[6],'exit_getters':getters,
            'scope':'Original scalar forwarding/getter windows in bounded synthetic RAM; no formatter, complete loader, scene transition or GPU execution.'}


def exit_rows(data):
    from scene_name_fields import parse
    validated=parse(data)
    if (validated['map_count'],validated['name_fields'])!=(300,839):raise ValueError('Scene bank revision differs')
    rows=[];seen=set()
    for index in range(300):
        tree,size,blob,script=struct.unpack_from('<4I',data,0x830+16*index)
        for at in range(0x800+tree,0x800+tree+size,16):
            typ,children,identity,offset,length=struct.unpack_from('<HHIII',data,at)
            if typ not in (6,7):continue
            pos=0x800+blob+offset
            if bytes(data[pos:pos+14])!=EXIT_SOURCE+b'\0':continue
            # Only the 13-byte text prefix is editable. Some later bytes are
            # nonzero metadata; they are NOT padding or extra text capacity.
            if length!={6:204,7:216}[typ]:
                raise ValueError('Observed exit name/layout differs')
            if pos in seen:raise ValueError('Exit name aliases require separate analysis')
            seen.add(pos)
            rows.append({'id':f'map.exit.{index:03d}.{at-0x800-tree:06x}',
                         'map_index':index,'node_type':typ,'node_offset':at,'node_identity':identity,
                         'node_sha256':sha(data[at:at+16]),'offset':pos,'record_size':length,
                         'record_sha256':sha(data[pos:pos+length]),'prefix_window_sha256':sha(data[pos:pos+32])})
    if len(rows)!=113 or sum(r['node_type']==6 for r in rows)!=8:
        raise ValueError('Observed exit occurrence set differs')
    return rows


def source_rows():
    path=ROOT/'JOGO/Metal Saga'/RESOURCE
    expected=next(r for r in json.loads((ROOT/'reports/inventory.json').read_bytes()) if r['path']==RESOURCE)
    with path.open('rb') as stream,mmap.mmap(stream.fileno(),0,access=mmap.ACCESS_READ) as data:
        if sha(data)!=expected['sha256']:raise ValueError('Original MAP revision differs')
        rows=exit_rows(data)
    return expected['sha256'],rows


def header_mask():
    """Native Satcom typeface, no dialogue font and no glyph scaling."""
    from interface_graphics import original
    from interface_texture_pack import unpack_indices,pillow
    from interface_textures import inspect_texture
    from satcom_native_font import alphabet
    Image=pillow();glyphs={k:v.copy() for k,v in alphabet(False,True).items()}
    raw=original(FBS)
    def coverage(record,bg,fg):
        meta,_=inspect_texture(record);pixels=unpack_indices(record,meta)
        pal=[tuple(record[16+i*4:19+i*4]) for i in range(1<<meta['bpp'])]
        vector=[pal[fg][k]-pal[bg][k] for k in range(3)];norm=sum(v*v for v in vector)
        colors=[max(0,min(255,round(255*sum((p[k]-pal[bg][k])*vector[k] for k in range(3))/norm))) for p in pal]
        return pixels,colors
    # Lowercase p from the original plain Shops sprite; native cap top = 5.
    pixels,colors=coverage(raw[0x30c70:0x38cc0],4,7)
    p=Image.new('L',(7,18));p.putdata([colors[pixels[(48+2+y)*256+80+45+x]] for y in range(18) for x in range(7)])
    glyphs['p']=p
    # Capital T from original Title, aligned to the same 12-pixel baseline.
    pixels,colors=coverage(raw[0x20860:0x30c70],216,255)
    t=Image.new('L',(12,18))
    for y in range(12):
        for x in range(12):t.putpixel((x,y+3),colors[pixels[(194+min(y,10))*256+189+x]])
    glyphs['T']=t;glyphs[' ']=Image.new('L',(4,18))
    text='Tempo de jogo';width=sum(glyphs[c].width for c in text)+len(text)-1
    if width>140:raise ValueError('Native time label does not fit without scaling')
    mask=Image.new('L',(width,15));cursor=0
    for c in text:
        glyph=glyphs[c].crop((0,3,glyphs[c].width,18));mask.paste(glyph,(cursor,0));cursor+=glyph.width+1
    return mask,{'translation':text,'height':15,'width':width,'scaling':False,
                 'font_source':'Native Satcom raster alphabet; p from Shops and T from Title',
                 'mask_sha256':sha(mask.tobytes()),'rect':[104,232,248,248]}


def revise_header(patch):
    from interface_graphics import original
    raw=original(FBS);meta_start=0x20860;pixels_start=meta_start+1040
    if patch['id']!='fbs.texture.2' or patch['resource']!=FBS or patch['offset']!=pixels_start:
        raise ValueError('Time label parent patch differs')
    if patch['before']!=raw[pixels_start:pixels_start+65536]:raise ValueError('Time label source pixels differ')
    palette=[tuple(raw[meta_start+16+i*4:meta_start+20+i*4]) for i in range(256)]
    mask,layout=header_mask();out=bytearray(patch['after']);x,y,z,w=layout['rect'];bg,fg=216,255
    colors=[]
    for v in range(256):
        rgb=[round(palette[bg][k]+(palette[fg][k]-palette[bg][k])*v/255) for k in range(3)]
        colors.append(min((i for i,p in enumerate(palette) if p[3]==palette[bg][3]),key=lambda i:sum((palette[i][k]-rgb[k])**2 for k in range(3))))
    for yy in range(y,w):out[yy*256+x:yy*256+z]=bytes([bg])*(z-x)
    ox=x+(z-x-mask.width)//2
    for yy in range(mask.height):
        for xx in range(mask.width):out[(y+yy)*256+ox+xx]=colors[mask.getpixel((xx,yy))]
    for at,(a,b) in enumerate(zip(patch['after'],out)):
        if a!=b and not (x<=at%256<z and y<=at//256<w):
            raise ValueError('Header revision outside selected sprite')
    return {**patch,'after':bytes(out)},layout


def template(elf):
    proof=probes(elf);source_hash,rows=source_rows();literals=[]
    for offset,text in LITERALS.items():
        end=elf.find(b'\0',offset);before=elf[offset:end];value=encode(text)
        if len(value)>len(before) or controls(value)!=controls(before):raise ValueError('Literal format/slot differs')
        literals.append({'id':f'elf.observed.{offset:08x}','offset':offset,'size':len(before)+1,
                         'source_sha256':sha(elf[offset:end+1]),'translation':text})
    _,header=header_mask()
    return {'schema':1,'policy':POLICY,'parent_recipe':PARENT,'parent_sha256':sha((ROOT/PARENT).read_bytes()),
            'elf_sha256':sha(elf),'map_sha256':source_hash,'literals':literals,'exits':rows,'header':header,
            'instruction_windows':[{'offset':a,'size':z-a,'sha256':sha(elf[a:z])} for a,z in WINDOWS],
            'forwarding_proof':proof}


def validate_interface(recipe):
    binding=recipe['satcom_gap_release']
    if set(binding)!={'recipe','sha256'} or binding['recipe']!=MANIFEST:raise ValueError('Unknown observed gap binding')
    raw=(ROOT/MANIFEST).read_bytes()
    if sha(raw)!=binding['sha256']:raise ValueError('Observed gap manifest differs')
    m=json.loads(raw);parent_raw=(ROOT/PARENT).read_bytes();parent=json.loads(parent_raw)
    if m.get('parent_recipe')!=PARENT or m.get('parent_sha256')!=sha(parent_raw):raise ValueError('Observed gap parent differs')
    expected=copy.deepcopy(parent)
    expected.update(satcom_gap_release=binding,iso_name='MetalSaga-ptbr-interface-v056.iso',status=STATUS)
    if recipe!=expected:raise ValueError('Unrelated modification in observed gap child')
    return parent,m


def compile_interface(elf,recipe):
    from interface_text import compile_draft
    parent,manifest=validate_interface(recipe)
    if manifest!=template(elf):raise ValueError('Observed gap source/proof/layout changed')
    patches,report=compile_draft(elf,parent);extra=[]
    for row in manifest['literals']:
        at=row['offset'];size=row['size'];value=encode(row['translation'])
        extra.append({'id':row['id'],'resource':'SLUS_212.93','offset':at,'before':elf[at:at+size],
                      'after':value+bytes(size-len(value))})
    if len(EXIT_SOURCE)!=len(EXIT_TARGET):raise ValueError('Exit label must retain exact encoded length')
    for row in manifest['exits']:
        extra.append({'id':row['id'],'resource':RESOURCE,'offset':row['offset'],'before':EXIT_SOURCE,'after':EXIT_TARGET})
    selected=[p for p in patches if p['id']=='fbs.texture.2']
    if len(selected)!=1:raise ValueError('Expected one parent header atlas')
    revised,layout=revise_header(selected[0]);patches=[revised if p['id']==revised['id'] else p for p in patches]
    for new in extra:
        for old in patches:
            if old.get('resource')==new['resource'] and max(old['offset'],new['offset'])<min(old['offset']+len(old['after']),new['offset']+len(new['after'])):
                raise ValueError('Observed gap patch overlaps prior translation')
    report=copy.deepcopy(report);report['accepted']+=len(extra)
    report['satcom_gap_release']={'policy':POLICY,'new_units':len(extra),'elf_literals':3,'exit_labels':113,
                                  'revised_graphic_labels':1,'header':layout,'pcsx2_executed':False,
                                  'visual_validation':'pending_user','map_dialogue_recipe_unchanged':True}
    return patches+extra,report
