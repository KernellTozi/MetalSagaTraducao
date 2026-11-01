"""Exact v062 screenshot follow-up; fixed cells, original tables and atlas only."""
import copy
import json
import mmap
import struct
from dialogue import ROOT,sha
from interface_text import SOURCE as ELF,FORMAT,references,sections
from interface_resources import original
from reinsertion import SOURCE as MAP
from gfi import encode,decode
from glyph_spacing import ORIGINAL_SHA

PARENT='translations/interface-v061.json'
MANIFEST='translations/telas-revisadas-v001.json'
CHILD='translations/interface-v062.json'
POLICY='screenshot-followup-exact-names-map-labels-and-stat-cells-v001'
STATUS='Reboque, blindagem, jukebox, habilidades, itens e alinhamento dos resultados; visual pendente.'
SPACK='DATA/S/S_PACK.SDA'
MCT='DATA/MAP/MAP.MCT'
ITEMS={190:('Scrap Armor','Colete avariado'),864:('Animal Instinct','Instinto animal'),
       959:('Animal Instinct','Instinto animal')}
LITERALS={0x315e90:'Reboque ',0x315ea0:'Rebocar ',
          0x315f10:'Soltar reboque ',
          0x32aed0:'Quanto descartar?\n\nPlacas            %4d\n'}
STATS={0x3239e0:(16,'Nível:     %3d'),0x323a28:(24,'Prêmio          %8d')}
JICONS=(b'$\x81\x7b',b'$\x81\x7e',b'$\x81\xa2',b'$\x81\x9b',b'$L1$L2$R1$R2')
HEADERS=((84,106,'ITENS',3),(144,118,'HABILIDADES',1))
WINDOWS=((0x3239e0,0x323a58),(0x113200,0x1133b0),
         (0x315e30,0x315f50),(0x146e20,0x146e70),
         (0x79eb8,0x79ec8),(0x7e5c0,0x7e5c8),(0x7e988,0x7e990))


def instruction_binding(elf):
    if sha(elf)!=ORIGINAL_SHA:raise ValueError('Follow-up ELF differs')
    return [{'offset':a,'size':z-a,'sha256':sha(elf[a:z])} for a,z in WINDOWS]


def literal_rows(elf):
    instruction_binding(elf);targets={a:encode(t) for a,t in LITERALS.items()}
    before=elf[0x32af00:elf.index(b'\0',0x32af00)]
    if before.count(b'\x81\xa8')!=3:raise ValueError('Discard native arrows differ')
    targets[0x32af00]=before.replace(b'Load   ',b'Carga  ').replace(b'Free  ',b'Livre ')
    before=elf[0x331cd0:elf.index(b'\0',0x331cd0)]
    expected=b'Select:'+JICONS[0]+b' Play:'+JICONS[1]+b' Stop:'+JICONS[2]+b' Exit:'+JICONS[3]+b' Percussion:'+JICONS[4]
    if before!=expected:raise ValueError('Jukebox actions/icons differ')
    targets[0x331cd0]=b' '.join(encode(t)+icon for t,icon in zip(('Mover','Tocar','Parar','Sair','Percussão'),JICONS))
    rows=[]
    for at,value in targets.items():
        end=elf.index(b'\0',at);before=elf[at:end+1]
        if len(value)>=len(before) or b'\0' in value or FORMAT.findall(before)!=FORMAT.findall(value):
            raise ValueError('Follow-up literal budget/printf differs')
        if before.count(b'\n')!=value.count(b'\n'):raise ValueError('Follow-up newline differs')
        rows.append({'id':f'followup.elf.{at:08x}','offset':at,'size':len(before),
                     'source_sha256':sha(before),'target_hex':value.hex()})
    refs=references(elf,sections(elf))
    for at,(size,text) in STATS.items():
        end=elf.index(b'\0',at);value=encode(text)
        if len(value)>=size or any(elf[end:at+size]) or any(at+0xff000+i in refs for i in range(1,size)):
            raise ValueError('Statistics cell tail/capacity/interior reference differs')
        if FORMAT.findall(value)!=FORMAT.findall(elf[at:end]):raise ValueError('Statistics numeric format differs')
        rows.append({'id':f'elf.ui.{at:08x}','offset':at,'size':size,
                     'source_sha256':sha(elf[at:at+size]),'target_hex':value.hex(),'revision':True})
    return rows


def item_fields(elf,raw):
    from item_names import catalog,execute_record_pointer,STRIDE
    from spack_battle import catalog as actions,execute_action,ACTION_STRIDE
    rows={r['index']:r for r in catalog(raw)};out=[]
    for idx,(source,text) in ITEMS.items():
        row=rows[idx];value=encode(text);at=row['offset'];before=raw[at:at+24]
        if bytes.fromhex(row['source_hex'])!=source.encode() or any(before[row['source_bytes']:]):
            raise ValueError('Reviewed item source/tail differs')
        if len(value)>16 or decode(value)!=text or any(c in value for c in (0,10,13,37,124)):
            raise ValueError('Reviewed item violates known codec/16-byte ceiling')
        if execute_record_pointer(elf,idx)!=idx*STRIDE:raise ValueError('Reviewed item getter differs')
        out.append({'id':row['id'],'offset':at,'size':24,'record_sha256':row['record_sha256'],
                    'source_sha256':sha(before),'translation':text,'target_hex':value.hex(),'kind':'item'})
    action=next(r for r in actions(raw) if r['id']=='battle.action.0219')
    at=action['offset'];value=encode('Instinto animal')
    if bytes.fromhex(action['source_hex'])!=b'Animal Instinct' or any(raw[at+15:at+32]):
        raise ValueError('Animal Instinct action differs')
    if execute_action(elf,219)!=219*ACTION_STRIDE:raise ValueError('Action getter differs')
    out.append({'id':action['id'],'offset':at,'size':32,'record_sha256':action['record_sha256'],
                'source_sha256':sha(raw[at:at+32]),'translation':'Instinto animal',
                'target_hex':value.hex(),'kind':'action'})
    return out


def map_rows(data):
    from scene_name_fields import parse
    parsed=parse(data)
    if (parsed['map_count'],parsed['name_fields'])!=(300,839):raise ValueError('Map scene profile differs')
    out=[]
    for index in range(300):
        tree,size,blob,script=struct.unpack_from('<4I',data,0x830+16*index)
        for at in range(0x800+tree,0x800+tree+size,16):
            typ,children,identity,offset,length=struct.unpack_from('<HHIII',data,at)
            pos=0x800+blob+offset;field=bytes(data[pos:pos+32]);name=field.split(b'\0')[0]
            text=None
            if typ in (2,7) and name==b"Snake's Den":text='Toca da Cobra'
            if typ==6 and name==b'Jukebox':text='Vitrola'
            if text is None:continue
            span=max(len(name),len(encode(text)))+1
            if any(field[len(name):span]) or span>32 or (typ in (6,7) and length!={6:204,7:216}[typ]):
                raise ValueError('Follow-up map label field/layout differs')
            if typ==6 and len(encode(text))!=len(name):raise ValueError('Jukebox name must retain its original NUL position')
            out.append({'id':f'followup.map.{index:03d}.{at-0x800-tree:06x}',
                        'node_offset':at,'node_type':typ,'record_size':length,
                        'node_sha256':sha(data[at:at+16]),'offset':pos,'size':span,
                        'record_sha256':sha(data[pos:pos+length]),'source_sha256':sha(field[:span]),
                        'translation':text,'target_hex':encode(text).hex()})
    if len(out)!=13 or sum(r['translation']=='Vitrola' for r in out)!=11:
        raise ValueError('Follow-up map occurrence set differs')
    return out


def map_source():
    expected=next(r for r in json.loads((ROOT/'reports/inventory.json').read_bytes()) if r['path']==MCT)
    with MAP.open('rb') as f,mmap.mmap(f.fileno(),0,access=mmap.ACCESS_READ) as data:
        if sha(data)!=expected['sha256']:raise ValueError('Follow-up original MAP differs')
        return expected['sha256'],map_rows(data)


def getters(elf):
    from name_source_paths import run
    evidence=[]
    for typ,getter in ((2,0x79eb8),(6,0x7e5c0),(7,0x7e988)):
        obj=bytearray(64);struct.pack_into('<I',obj,0x3c,0x620000)
        regs=[0]*32;regs[4]=0x610000;regs[31]=0x7ff000
        result=run(elf,getter,((getter,getter+8),),regs,[(0x610000,obj,False)],0x7ff000)
        if result['registers'][2]!=0x620000 or result['writes']:raise ValueError('Native name getter differs')
        evidence.append({'type':typ,'getter_offset':getter,'returns_existing_name_pointer':True})
    return evidence


def header_revision(raw):
    from observed_menu_translation import render_headers,header_glyphs
    from interface_texture_pack import pillow
    Image=pillow();old=render_headers(raw)[0][0];pixels=bytearray(old['after'])
    glyphs=header_glyphs(raw[0x8c830:0x9cc40]);results=[]
    for top,right,text,gap in HEADERS:
        pieces=[]
        for char in text:
            width,bitmap=glyphs[char]
            if text=='HABILIDADES' and char=='D':
                bitmap=b''.join(bitmap[y*width:y*width+5]+bitmap[y*width+6:(y+1)*width] for y in range(10));width-=1
            pieces.append((width,bitmap))
        total=sum(w for w,_ in pieces)+gap*(len(pieces)-1)
        if total>right-5:raise ValueError('Native title exceeds existing ink cell')
        for y in range(top,top+12):pixels[y*256+4:y*256+right]=bytes([241])*(right-4)
        cursor=5
        for width,bitmap in pieces:
            for y in range(10):pixels[(top+y)*256+cursor:(top+y)*256+cursor+width]=bitmap[y*width:(y+1)*width]
            cursor+=width+gap
        results.append({'translation':text,'rect':[4,top,right,top+12],'width':total,'height':10,
                        'gap':gap,'glyph_D_counter_columns_removed':1 if text=='HABILIDADES' else 0,
                        'resized':False})
    return {**old,'after':bytes(pixels)},results


def template(elf):
    raw=original(SPACK);map_hash,mrows=map_source();header,layout=header_revision(raw)
    return {'schema':1,'policy':POLICY,'parent_recipe':PARENT,'parent_sha256':sha((ROOT/PARENT).read_bytes()),
            'elf_sha256':ORIGINAL_SHA,'spack_sha256':sha(raw),'map_sha256':map_hash,
            'source_windows':instruction_binding(elf),'literals':literal_rows(elf),
            'names':item_fields(elf,raw),'map_labels':mrows,'map_getters':getters(elf),
            'headers':layout,'header_after_sha256':sha(header['after'])}


def validate_interface(recipe):
    binding=recipe['screen_followup_release']
    if set(binding)!={'recipe','sha256'} or binding['recipe']!=MANIFEST:raise ValueError('Unknown follow-up binding')
    raw=(ROOT/MANIFEST).read_bytes()
    if sha(raw)!=binding['sha256']:raise ValueError('Follow-up manifest differs')
    m=json.loads(raw);parent=json.loads((ROOT/PARENT).read_bytes());expected=copy.deepcopy(parent)
    expected.update(screen_followup_release=binding,iso_name='MetalSaga-ptbr-interface-v062.iso',status=STATUS)
    if recipe!=expected or m['parent_recipe']!=PARENT or m['parent_sha256']!=sha((ROOT/PARENT).read_bytes()):
        raise ValueError('Unrelated follow-up parent/child change')
    return parent,m


def additions(elf,m):
    if m!=template(elf):raise ValueError('Follow-up source/field/glyph evidence changed')
    raw=original(SPACK);patches=[];revisions=[]
    with MAP.open('rb') as f,mmap.mmap(f.fileno(),0,access=mmap.ACCESS_READ) as data:
        for resource,rows,source in (('SLUS_212.93',m['literals'],elf),(SPACK,m['names'],raw),(MCT,m['map_labels'],data)):
            for row in rows:
                at=row['offset'];before=bytes(source[at:at+row['size']]);value=bytes.fromhex(row['target_hex'])
                if sha(before)!=row['source_sha256']:raise ValueError('Follow-up patch source differs')
                p={'id':row['id'],'resource':resource,'offset':at,'before':before,'after':value+bytes(len(before)-len(value))}
                (revisions if row.get('revision') else patches).append(p)
    header,_=header_revision(raw);revisions.append(header)
    return patches,revisions


def compile_interface(elf,recipe):
    from interface_text import compile_draft
    parent,m=validate_interface(recipe);patches,report=compile_draft(elf,parent)
    extra,revisions=additions(elf,m);byid={p['id']:p for p in patches}
    for p in revisions:
        old=byid.get(p['id'])
        if old is None or old['resource']!=p['resource'] or old['offset']!=p['offset'] or p['before'][:len(old['before'])]!=old['before']:
            raise ValueError('Follow-up revised parent patch differs')
        if p['id']=='observed.headers':
            from observed_menu_translation import render_headers
            if old!=render_headers(original(SPACK))[0][0]:raise ValueError('Parent native title patch differs')
        byid[p['id']]=p
    output=[byid[p['id']] for p in patches]
    for p in extra:
        if any(q['resource']==p['resource'] and max(p['offset'],q['offset'])<min(p['offset']+len(p['before']),q['offset']+len(q['before'])) for q in output):
            raise ValueError('Follow-up additions overlap previous translation')
        output.append(p)
    report=copy.deepcopy(report);report['accepted']+=len(extra)+2
    report['item_names']['accepted']+=3
    report['item_names']['results'].extend({'id':r['id'],'index':int(r['id'].rsplit('.',1)[1]),'target_bytes':len(bytes.fromhex(r['target_hex'])),'group':'explicit-screenshot-review'} for r in m['names'] if r['kind']=='item')
    report['spack_battle']['accepted']+=1;report['spack_battle']['actions']+=1
    report['spack_battle']['results'].append({'id':'battle.action.0219','kind':'action','index':219,'target_bytes':15})
    current={p['id']:p for p in output}
    report['item_names']['unique_translated_labels']=len({current[r['id']]['after'].split(b'\0')[0] for r in report['item_names']['results']})
    for row in report['results']:
        if row['id'] in {f'elf.ui.{a:08x}' for a in STATS}:
            value=current[row['id']]['after'].split(b'\0')[0]
            row.update(target_bytes=len(value),target_sha256=sha(value))
    report['screen_followup_release']={'policy':POLICY,'new_units':len(extra)+2,'new_item_names':3,
        'new_action_labels':1,'new_map_labels':len(m['map_labels']),'new_elf_literals':len(m['literals'])-2,
        'new_native_titles':2,'revised_statistic_formats':2,'context':'Names of songs, unique equipment and wanted names preserved.',
        'pcsx2_executed':False,'visual_status':'pending_user'}
    return output,report


def normalize_statistics(old_patches,new_patches):
    elf=ELF.read_bytes()
    for at,(size,_) in STATS.items():
        key=('SLUS_212.93',at);old=old_patches[key];new=new_patches[key]
        if old['id']!=new['id'] or new['before']!=elf[at:at+size] or old['before']!=new['before'][:len(old['before'])]:
            raise ValueError('Statistics comparison source/span differs')
        old_patches[key]={**old,'before':new['before'],'after':old['after']+new['before'][len(old['after']):]}


def prepare():
    m=template(ELF.read_bytes());raw=(json.dumps(m,ensure_ascii=False,indent=2)+'\n').encode()
    (ROOT/MANIFEST).write_bytes(raw);child=json.loads((ROOT/PARENT).read_bytes())
    child.update(screen_followup_release={'recipe':MANIFEST,'sha256':sha(raw)},
                 iso_name='MetalSaga-ptbr-interface-v062.iso',status=STATUS)
    (ROOT/CHILD).write_bytes((json.dumps(child,ensure_ascii=False,indent=2)+'\n').encode())
    validate_interface(child)
    return {'names':len(m['names']),'map_labels':len(m['map_labels']),'elf_literals':len(m['literals']),'headers':2}


def previews():
    from interface_texture_pack import pillow
    from interface_textures import inspect_texture
    Image=pillow()
    from PIL import ImageDraw
    raw=original(SPACK);p,_=header_revision(raw);modified=bytearray(raw)
    modified[p['offset']:p['offset']+len(p['after'])]=p['after']
    canvas=Image.new('RGB',(900,115),(30,30,30));draw=ImageDraw.Draw(canvas)
    for column,source in enumerate((raw,modified)):
        _,rgb=inspect_texture(source[0x8c830:0x9cc40]);image=Image.frombytes('RGB',(256,256),rgb)
        draw.text((column*450+5,3),'Original' if column==0 else 'PT-BR',fill='white')
        for i,(top,right,_,_) in enumerate(HEADERS):
            crop=image.crop((4,top,right,top+12)).resize(((right-4)*3,36),Image.Resampling.NEAREST)
            canvas.paste(crop,(column*450+5,22+i*44))
    folder=ROOT/'work/interface-v062-previews';folder.mkdir(exist_ok=True)
    canvas.save(folder/'titulos.png')
    return {'previews':folder.relative_to(ROOT).as_posix(),'gpu_render':False}


if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser(description='Preparar revisão de telas ou previews locais, sem alterar ISO')
    parser.add_argument('--previews',action='store_true')
    args=parser.parse_args()
    print(json.dumps(previews() if args.previews else prepare()))
