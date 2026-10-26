"""Read-only investigation of the frozen 365 unknown atlas entries.

New parsers are separate from historical atlas/import policies. Container
recognition does not authorize edits or identify its opaque child payloads.
"""
import argparse,collections,json,struct
from pathlib import Path
from reinsertion import ROOT,local
from dialogue import sha
from explore_interface_atlases import classify
from interface_textures import inspect_texture
from interface_texture_pack import pillow,unpack_indices,replace_indices
from interface_text import SOURCE
from glyph_spacing import ORIGINAL_SHA

SCOPE='Bounded discovery of the frozen 365 unknown entries v001'

def execute_window(elf,start,stop,regs,regions):
    """Straight-line integer snippets only; no callee, GPU or allocator."""
    def access(at,size,value=None):
        for base,raw in regions:
            if base<=at and at+size<=base+len(raw):
                offset=at-base
                if value is None:return int.from_bytes(raw[offset:offset+size],'little')
                raw[offset:offset+size]=(value&((1<<(size*8))-1)).to_bytes(size,'little');return
        raise ValueError('Discovery probe outside supplied RAM')
    for pc in range(start,stop,4):
        word=struct.unpack_from('<I',elf,pc)[0];op=word>>26;rs=word>>21&31;rt=word>>16&31;rd=word>>11&31
        u=word&65535;n=u if u<32768 else u-65536
        if op==0:
            fn=word&63
            if fn in (33,45):regs[rd]=regs[rs]+regs[rt]
            elif fn==0:regs[rd]=regs[rt]<<((word>>6)&31)
            elif fn==2:regs[rd]=regs[rt]>>((word>>6)&31)
            else:raise ValueError('Unsupported straight-line discovery instruction')
        elif op==9:regs[rt]=regs[rs]+n
        elif op==12:regs[rt]=regs[rs]&u
        elif op in (35,36,37):regs[rt]=access(regs[rs]+n,{35:4,36:1,37:2}[op])
        elif op==43:access(regs[rs]+n,4,regs[rt])
        else:raise ValueError('Unsupported discovery opcode')
        regs=[v&0xffffffff for v in regs];regs[0]=0
    return regs


def consumer_evidence(elf,records,resources):
    windows=((0x19af98,0x19afa8),(0x19b254,0x19b264),
        (0x670c8,0x670e8),(0x67118,0x67130),(0x64250,0x64284))
    header_cases=frame_cases=0
    for row in records:
        if row['discovery']['kind']!='ganm-sprite-sequence-table':continue
        raw=resources[row['resource']][row['offset']:row['offset']+row['size']]
        parsed=ganm_sequences(raw,nonsequential_first=row['discovery']['first_field_profile']=='source-bound-nonsequential-opaque');obj=bytearray(64);r=[0]*32;r[5]=0x610000;r[16]=0x620000
        r=execute_window(elf,0x19af98,0x19afa8,r,[(0x610000,raw),(0x620000,obj)])
        if r[3]!=parsed['sequence_count'] or r[2]!=0x610000+parsed['sprite_offset']:
            raise ValueError('Original GANM count/base reader differs')
        header_cases+=1
        for group in parsed['groups']:
            for frame in group['frames']:
                r=[0]*32;r[3]=0x610000+group['offset']+8+12*frame['entry_index'];r[5]=0x610010;r[6]=0x620000
                r=execute_window(elf,0x19b254,0x19b264,r,[(0x610000,raw),(0x620000,obj)])
                if r[5]!=0x610010+frame['sprite']*16:raise ValueError('Original GANM frame sprite selection differs')
                frame_cases+=1
    for value in range(256):
        r=[0]*32;r[16]=0x610001;r[18]=0x30
        r=execute_window(elf,0x67118,0x67130,r,[(0x610001,bytes([value]))])
        if (r[3],r[4])!=(0x30+(value&15),value>>4):raise ValueError('Original stamp nibble order differs')
    return {'instruction_windows':[{'offset':a,'size':z-a,'sha256':sha(elf[a:z])} for a,z in windows],
        'ganm_original_header_cases':header_cases,'ganm_original_frame_lookup_cases':frame_cases,
        'stamp_original_nibble_cases':256,'stamp_dimensions_inspected':[64,64],
        'executed':'Only the two GANM integer windows and nibble window in supplied synthetic RAM',
        'not_executed':'Full GANM sequence loader, allocation, DAI/DPI/bundle consumers, stamp conversion/CLUT, draw, GPU, PS2'}


def offset_container(raw,magic):
    if len(raw)<16 or raw[:4]!=magic or magic not in (b'dai\0',b'dpi\0'):raise ValueError('Container signature differs')
    size,count=struct.unpack_from('<II',raw,4)
    if not 1<=count<=4096 or 12+4*count>size or size>len(raw):raise ValueError('Container count/size outside bounds')
    offsets=list(struct.unpack_from(f'<{count}I',raw,12))
    if offsets!=sorted(set(offsets)) or offsets[0]<((12+4*count+15)&~15) or offsets[-1]>=size:
        raise ValueError('Container offsets overlap header or are unordered')
    if any(v%16 for v in offsets):raise ValueError('Container alignment differs')
    ranges=list(zip(offsets,offsets[1:]+[size]))
    # Reassemble prefix, every bounded child and suffix byte-for-byte.
    if raw[:offsets[0]]+b''.join(raw[a:z] for a,z in ranges)+raw[size:]!=raw:raise ValueError('Container round-trip differs')
    return {'kind':magic[:3].decode()+'-texture-container','declared_size':size,'count':count,
        'offsets':offsets,'ranges':ranges,'header_padding_bytes':offsets[0]-12-4*count,
        'outer_tail_bytes':len(raw)-size,'roundtrip':True}


def bundle41(raw):
    if len(raw)<168 or struct.unpack_from('<I',raw)[0]!=41:raise ValueError('41-part bundle header differs')
    offsets=list(struct.unpack_from('<41I',raw,4))
    if offsets[0]!=168 or offsets!=sorted(set(offsets)) or offsets[-1]>=len(raw) or any(v%4 for v in offsets):
        raise ValueError('41-part bundle offsets differ')
    ranges=list(zip(offsets,offsets[1:]+[len(raw)]))
    if raw[:168]+b''.join(raw[a:z] for a,z in ranges)!=raw:raise ValueError('Bundle round-trip differs')
    return {'kind':'41-part-offset-bundle','count':41,'offsets':offsets,'ranges':ranges,
        'child_semantics':'unresolved numeric payloads, not decoded as text or skeletal tracks','roundtrip':True}


def ganm_sequences(raw,nonsequential_first=False):
    if len(raw)<16 or raw[:4]!=b'ganm':raise ValueError('GANM signature differs')
    sprites,sequences,stride,sequence_at=struct.unpack_from('<HHII',raw,4)
    if not 1<=sprites<=4096 or not 1<=sequences<=1024 or stride!=16 or sequence_at!=16+sprites*16 or sequence_at>len(raw):
        raise ValueError('GANM split header/bounds differ')
    p=sequence_at;groups=[]
    for i in range(sequences):
        if p+8>len(raw):raise ValueError('Truncated GANM sequence header')
        count,reserved,size=struct.unpack_from('<HHI',raw,p)
        if not count or size!=8+count*12 or p+size>len(raw):raise ValueError('GANM sequence bounds differ')
        frames=[]
        for j in range(count):
            first,sprite,duration,flags=struct.unpack_from('<HHII',raw,p+8+j*12)
            if (first!=j and not nonsequential_first) or sprite>=sprites:raise ValueError('GANM frame first field variant/sprite outside table')
            frames.append({'entry_index':j,'opaque_first_field':first,'sprite':sprite,'duration_field':duration,'opaque_flags':flags})
        groups.append({'index':i,'offset':p,'count':count,'reserved':reserved,'size':size,'frames':frames});p+=size
    if len(raw)-p>=16:raise ValueError('GANM extra unparsed tail exceeds observed alignment')
    rebuilt=struct.pack('<4sHHII',b'ganm',sprites,sequences,16,sequence_at)+raw[16:sequence_at]
    for g in groups:
        rebuilt+=struct.pack('<HHI',g['count'],g['reserved'],g['size'])
        rebuilt+=b''.join(struct.pack('<HHII',f['opaque_first_field'],f['sprite'],f['duration_field'],f['opaque_flags']) for f in g['frames'])
    rebuilt+=raw[p:]
    return {'kind':'ganm-sprite-sequence-table','sprite_count':sprites,'sequence_count':sequences,
        'sprite_offset':16,'sequence_offset':sequence_at,'groups':groups,'tail_offset':p,
        'first_field_profile':'source-bound-nonsequential-opaque' if nonsequential_first else 'sequential-value-observed-semantics-unproved',
        'nonsequential_first_fields':sum(f['opaque_first_field']!=f['entry_index'] for g in groups for f in g['frames']),
        'tail_bytes':len(raw)-p,'tail_nonzero':bool(any(raw[p:])),
        'tail_sha256':sha(raw[p:]),'roundtrip':rebuilt==raw}


def came(raw):
    if len(raw)<8 or raw[:4]!=b'CAME':raise ValueError('CAME signature differs')
    count=struct.unpack_from('<I',raw,4)[0];end=8+20*count
    if not count or end>len(raw) or len(raw)-end>=16 or any(raw[end:]):raise ValueError('CAME fixed record bounds/padding differ')
    return {'kind':'came-counted-fixed20-records','count':count,'record_offset':8,'stride':20,
        'tail_bytes':len(raw)-end,'semantics':'CAME tag and fixed record layout; camera meaning/consumer not proved',
        'roundtrip':raw[:8]+b''.join(raw[a:a+20] for a in range(8,end,20))+raw[end:]==raw}


def direct_texture(raw):
    if len(raw)<16:raise ValueError('Truncated direct texture')
    width,height,bpp,palette,at=struct.unpack_from('<HHIII',raw)
    if not 1<=width<=1024 or not 1<=height<=1024 or bpp not in (24,32) or palette!=0 or at!=16:
        raise ValueError('Unsupported direct texture header')
    end=at+width*height*(bpp//8)
    if end>len(raw) or any(raw[end:]):raise ValueError('Direct pixels truncated or nonzero tail')
    return {'kind':'direct-rgb-texture' if bpp==24 else 'direct-rgba-texture','width':width,'height':height,
        'bpp':bpp,'pixel_offset':16,'pixel_bytes':end-16,'tail_bytes':len(raw)-end,'roundtrip':True}


def stamp(raw):
    if len(raw)!=2112 or any(raw[i] not in (0,127,128) for i in range(3,64,4)):
        raise ValueError('Stamp palette/record size differs')
    pixels=bytes(v for b in raw[64:] for v in (b&15,b>>4))
    packed=bytes(pixels[i]|pixels[i+1]<<4 for i in range(0,len(pixels),2))
    if raw[:64]+packed!=raw:raise ValueError('Stamp reverse round-trip differs')
    return {'kind':'paint-headerless-palette16-stamp','width':64,'height':64,'bpp':4,
        'palette_offset':0,'palette_bytes':64,'pixel_offset':64,'pixel_bytes':2048,'roundtrip':True}


def kanji_list(raw):
    body=raw.rstrip(b'\xa5');payload=body.replace(b'\r\n',b'')
    if len(raw)!=6080 or not body.endswith(b'\r\n') or len(payload)!=5930 or body.count(b'\r\n')!=46:
        raise ValueError('Character list line boundaries differ')
    pairs=[bytes(payload[i:i+2]) for i in range(0,len(payload),2)]
    if len(set(pairs))!=2965 or any(not (0x81<=p[0]<=0x9f and 0x40<=p[1]<=0xfc and p[1]!=127) for p in pairs):
        raise ValueError('Character list pair repertoire differs')
    text=payload.decode('cp932')
    if text.encode('cp932')!=payload:raise ValueError('Character list CP932 round-trip differs')
    return {'kind':'name-entry-kanji-pair-list','pairs':2965,'crlf_rows':46,'body_bytes':len(body),
        'a5_tail_bytes':len(raw)-len(body),'roundtrip':True,
        'encoding_scope':'Only this list round-trips CP932; not a change to the project GFI codec'}


def note(raw):
    end=raw.find(b'\r\n\r\n\r\n\r\n')+8
    if len(raw)!=192 or not raw.startswith(b'kanji.txt\r\n') or end<8:raise ValueError('Name-entry technical note shape differs')
    raw[:end].decode('cp932')
    return {'kind':'name-entry-technical-note-with-opaque-tail','note_bytes':end,
        'tail_bytes':len(raw)-end,'tail_sha256':sha(raw[end:]),'roundtrip':True}


def child_texture(raw):
    try:
        meta,_=inspect_texture(raw)
        if replace_indices(raw,unpack_indices(raw,meta))!=raw:raise ValueError('Indexed texture round-trip failed')
        return {'kind':'indexed-texture',**meta,'roundtrip':True}
    except ValueError:return direct_texture(raw)


def image_review(row,meta):
    resource=row['resource'];at=row['offset']
    if resource.endswith('FD_END.SDA'):kind='protected-company-logo'
    elif meta['kind']=='paint-headerless-palette16-stamp':kind='paint-stamp-symbol-or-alphabet'
    elif (resource,at) in {('DATA/RDATA/RMGDANCE.SDA',0x43d20),('DATA/RDATA/RMGKAERU.SDA',0x15f2e0)}:
        kind='environment-or-gameplay-word-review'
    elif resource.endswith('RMGTANK.SDA') and at in (0xc8b70,0xcf1a0,0xd57d0):kind='gameplay-letter-symbol-preserve-review'
    else:kind='no-localizable-word-observed'
    return {'resource':resource,'offset':at,'size':row['size'],'sha256':row['sha256'],
        'format':meta['kind'],'visual_class':kind,'reviewed_in_source_contact_sheet':True,
        'editing_authorized':False,'limits':'Source RGB previews only; not runtime/UV usage proof'}


def text_shape_probe(records,children,resources):
    from io import BytesIO
    from discover_remaining_catalogue import ascii_stream,phrase_candidate
    ranges=[r for r in records if r['discovery']['kind']=='unresolved']+[
        c for c in children if c.get('discovery',{}).get('kind')=='opaque-bundle-child']
    candidates=[];total=0
    for row in ranges:
        raw=resources[row['resource']][row['offset']:row['offset']+row['size']];total+=len(raw)
        for offset,text in ascii_stream(BytesIO(raw)):
            if phrase_candidate(text):candidates.append({'resource':row['resource'],
                'offset':row['offset']+offset,'length':len(text),'sha256':sha(text)})
    return {'ranges_scanned':len(ranges),'bytes_scanned':total,'candidate_count':len(candidates),
        'candidates':candidates,'filter':'Existing bounded ASCII phrase-shape filter; no AI/API',
        'limits':'No hit does not rule out compressed, native, tokenized or differently framed text. Shape is not dialogue validation.'}


def write_local(path,value):
    path=local(path)
    if path.exists() and json.loads(path.read_text(encoding='utf-8')).get('scope')!=SCOPE:
        raise ValueError('Refuse unrelated local discovery output')
    path.parent.mkdir(parents=True,exist_ok=True);temp=path.with_suffix('.json.tmp')
    with temp.open('x',encoding='utf-8') as f:json.dump(value,f,ensure_ascii=False,indent=2);f.write('\n')
    temp.replace(path)


def run(output,summary=None,previews=None):
    from verify_test_iso import verify_image
    baseline=json.loads((ROOT/'reports/triagem-grafica-v001.json').read_text(encoding='utf-8'))
    if len(baseline['unresolved'])!=365:raise ValueError('Frozen discovery baseline count differs')
    if summary is not None:
        summary=Path(summary).resolve()
        if not summary.is_relative_to(ROOT/'reports') or summary.exists():raise ValueError('Use new public report path')
    image=ROOT/'work/interface-v038/MetalSaga-ptbr-interface-v038.iso';before=verify_image(image)
    recipes={p.name:sha(p.read_bytes()) for p in (ROOT/'translations').glob('*.json')}
    inv={r['path']:r for r in json.loads((ROOT/'reports/inventory.json').read_text(encoding='utf-8'))}
    elf=SOURCE.read_bytes()
    if sha(elf)!=ORIGINAL_SHA:raise ValueError('Original ELF differs')
    resources={};records=[];children=[];pictures=[]
    for row in baseline['unresolved']:
        resource=row['resource']
        if resource not in resources:
            resources[resource]=(ROOT/'JOGO/Metal Saga'/resource).read_bytes()
            if sha(resources[resource])!=inv[resource]['sha256']:raise ValueError('Source resource differs')
        raw=resources[resource][row['offset']:row['offset']+row['size']]
        if sha(raw)!=row['sha256']:raise ValueError('Frozen entry binding differs')
        result={'kind':'unresolved','reason':'No proven parser for this numeric/SAF payload'}
        try:
            if resource.endswith('F_PCDKF.SDA'):result=bundle41(raw)
            elif raw[:4] in (b'dai\0',b'dpi\0'):result=offset_container(raw,raw[:4])
            elif raw[:4]==b'ganm':result=ganm_sequences(raw,nonsequential_first=resource=='DATA/RDATA/RMGKAERU.SDA' and row['offset'] in (0x91260,0x11a940))
            elif raw[:4]==b'CAME':result=came(raw)
            elif resource.endswith('S_PAINT.SDA') and row['size']==2112:result=stamp(raw);pictures.append((row,raw,result))
            elif resource.endswith('FNAME_DT.SDA'):
                result=kanji_list(raw) if row['offset']==0x86c40 else note(raw)
            elif resource.endswith('FD_END.SDA') and row['offset']!=0x800:
                result=direct_texture(raw);pictures.append((row,raw,result))
            elif resource.endswith('FD_END.SDA'):
                from discover_credits import analyse
                m,_=analyse(elf,resources[resource]);result={'kind':'known-compressed-credits','decoded_size':m['decoded_size'],'not_new':True}
            elif resource.endswith('S_PAINT.SDA') and row['offset']==0xae6a0:
                from discover_paint import analyse
                m,_=analyse(elf,resources[resource]);result={'kind':'known-paint-captions','records':m['records'],'not_new':True}
        except ValueError as error:result={'kind':'unresolved','reason':str(error)}
        records.append({**row,'discovery':{k:v for k,v in result.items() if k not in ('ranges','groups')},'editing_authorized':False})
        if result['kind']=='ganm-sprite-sequence-table':
            for g in result['groups']:children.append({'resource':resource,'parent_offset':row['offset'],'relative_offset':g['offset'],'kind':'ganm-sequence','data':g})
        for index,(a,z) in enumerate(result.get('ranges',[])):
            part=raw[a:z];meta={'kind':'opaque-bundle-child'}
            if result['kind']!='41-part-offset-bundle':
                try:meta=child_texture(part)
                except ValueError as error:meta={'kind':'unresolved-container-child','reason':str(error)}
            child={'resource':resource,'parent_offset':row['offset'],'index':index,'offset':row['offset']+a,
                'size':z-a,'sha256':sha(part),'discovery':meta,'editing_authorized':False}
            children.append(child)
            if meta['kind'] in ('indexed-texture','direct-rgb-texture','direct-rgba-texture'):pictures.append((child,part,meta))
    proof=consumer_evidence(elf,records,resources)
    if previews is not None:make_sheets(pictures,previews)
    after=verify_image(image)
    if after!=before or recipes!={p.name:sha(p.read_bytes()) for p in (ROOT/'translations').glob('*.json')}:raise ValueError('Baseline ISO or recipes changed')
    visual=[image_review(row,meta) for row,_,meta in pictures]
    pending_groups=collections.Counter()
    for row in records:
        if row['discovery']['kind']!='unresolved':continue
        raw=resources[row['resource']][row['offset']:row['offset']+row['size']]
        group='SAF' if raw[:4]==b'SAF ' else 'numeric-third-float-0.01' if raw[8:12]==struct.pack('<f',0.01) else 'numeric-third-float-1.0' if raw[8:12]==struct.pack('<f',1.0) else 'other-numeric'
        pending_groups[group]+=1
    report={'schema':1,'scope':SCOPE,'baseline_entries':365,'source_files_verified':len(resources),
        'classes':dict(collections.Counter(r['discovery']['kind'] for r in records)),
        'child_classes':dict(collections.Counter(c.get('discovery',{}).get('kind',c.get('kind')) for c in children)),
        'consumer_evidence':proof,
        'opaque_text_probe':text_shape_probe(records,children,resources),
        'unresolved_groups':dict(pending_groups),'new_image_visual_classes':dict(collections.Counter(r['visual_class'] for r in visual)),
        'new_image_visual_review':visual,'new_contact_sheets_reviewed':15,
        'new_image_records':len(pictures),'baseline_iso':after,'recipes_verified_unchanged':len(recipes),
        'records':records,'editing_authorized':False,'originals_modified':False,'translation_created':False,
        'iso_created':False,'pcsx2_executed':False,'limits':'Structural identification is not text or runtime proof; 41-part bundles retain all opaque children. Historical parsers/manifests unchanged.'}
    write_local(output,{**report,'children':children})
    if summary is not None:
        with summary.open('x',encoding='utf-8') as f:json.dump(report,f,ensure_ascii=False,indent=2);f.write('\n')
    return report


def make_sheets(pictures,output):
    output=local(output,True);Image=pillow()
    from PIL import ImageDraw
    output.mkdir(parents=True);index=[]
    for start in range(0,len(pictures),12):
        selected=pictures[start:start+12];sheet=Image.new('RGB',(1200,320*((len(selected)+3)//4)),(45,45,45));ids=[]
        for i,(row,raw,meta) in enumerate(selected):
            kind=meta['kind'];w=meta['width'];h=meta['height']
            if kind=='indexed-texture':_,rgb=inspect_texture(raw);im=Image.frombytes('RGB',(w,h),rgb)
            elif kind=='paint-headerless-palette16-stamp':
                ix=bytes(v for b in raw[64:] for v in (b&15,b>>4));rgb=bytes(c for v in ix for c in raw[v*4:v*4+3]);im=Image.frombytes('RGB',(64,64),rgb)
            else:
                mode='RGB' if meta['bpp']==24 else 'RGBA';im=Image.frombytes(mode,(w,h),raw[16:16+meta['pixel_bytes']]).convert('RGB')
            im.thumbnail((290,280),Image.Resampling.NEAREST)
            if w<=64 and h<=64:im=im.resize((w*3,h*3),Image.Resampling.NEAREST)
            x=i%4*300;y=i//4*320;sheet.paste(im,(x+(300-im.width)//2,y+35))
            label=Path(row['resource']).stem+' @'+hex(row['offset']);ImageDraw.Draw(sheet).text((x+5,y+4),label,fill='white');ids.append({'resource':row['resource'],'offset':row['offset'],'kind':kind})
        name=f'novos-{start//12:02d}.png';sheet.save(output/name);index.append({'sheet':name,'records':ids})
    with (output/'indice.json').open('x',encoding='utf-8') as f:json.dump(index,f,indent=2);f.write('\n')


if __name__=='__main__':
    p=argparse.ArgumentParser(description='Investigar entradas desconhecidas sem editar jogo/ISO')
    p.add_argument('--output',type=Path,required=True);p.add_argument('--summary',type=Path);p.add_argument('--previews',type=Path)
    a=p.parse_args();r=run(a.output,a.summary,a.previews);print(json.dumps({'classes':r['classes'],'children':r['child_classes'],'images':r['new_image_records']},indent=2))
