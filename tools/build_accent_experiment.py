"""Create the isolated accent experiment: two messages and blank cells in two GFI files."""
from pathlib import Path
import argparse,hashlib,json,mmap,re,shutil,sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'work/python-deps'))
from gfi import CHAR_TO_BYTES,Gfi,decode,encode,font_patches,sjis_to_jis
from dialogue import instruction,neighbors,PILOT_OFFSET,PILOT_SOURCE
from build_dialogue_iso import compare_streams,ORIGINAL_ISO_SHA256
from disc import entries,digest,SECTOR

SECOND_OFFSET=0x1df47f9c
SECOND_SOURCE="%F1%M0_5(Why's he thinking\nabout this, all of a\nsudden?)\tWell, I think it's a bad\nidea. It's a terrible,\nneedless job."
GROUP_A='A: \u00e7 \u00e1 \u00e0 \u00e3\n\u00e2 \u00e9 \u00ea \u00ed'
GROUP_B='%F1%M0_5Teste B:\n\u00f3 \u00f4 \u00f5 \u00fa \u00fc\n\u00c7 \u00c1 \u00c9 \u00c3 \u00d5\tWell, I think it\'s a bad\nidea. It\'s a terrible,\nneedless job.'
CONTROLS=re.compile(rb'%[A-Za-z][0-9]+(?:_[0-9]+)?|[\x09\x0a]')

def message_patch(data,offset,expected,replacement):
    info=instruction(data,offset)
    if data[offset:offset+4]!=b'msg\0' or info['size']<36:raise ValueError('Unsupported message')
    slot=data[offset+32:offset+info['size']];end=slot.find(b'\0')
    if end<0 or any(slot[end:]) or slot[:end]!=expected.encode('ascii'):
        raise ValueError('Message source/padding differs from documented baseline')
    surrounding=neighbors(data,offset)
    target=encode(replacement)
    if decode(target)!=replacement:raise ValueError('Project encoding roundtrip failed')
    if CONTROLS.findall(target)!=CONTROLS.findall(slot[:end]):raise ValueError('Control sequence changed')
    if len(target)>=len(slot):raise ValueError('Accent group overflows message slot')
    # Conservative full-width budget per existing page, using 1/2-cell units.
    old_pages=CONTROLS.sub(lambda m:m.group() if m.group() in (b'\t',b'\n') else b'',slot[:end]).decode('ascii').split('\t')
    new_pages=re.sub(r'%[A-Za-z][0-9]+(?:_[0-9]+)?','',replacement).split('\t')
    for old,new in zip(old_pages,new_pages):
        limit=max(map(len,old.split('\n')))
        if any(sum(2 if char in CHAR_TO_BYTES else 1 for char in line)>limit for line in new.split('\n')):
            raise ValueError('Conservative page width exceeded')
    return {'offset':offset+32,'before':slot,'after':target+bytes(len(slot)-len(target)),
            'record_offset':offset,'index':info['index'],'record_size':info['size'],
            'source':expected,'replacement':replacement,'encoded_hex':target.hex(' '),
            'encoded_length':len(target),'slot_size':len(slot),'neighbors':surrounding}

def create(output,report,profile='v001'):
    composer=font_patches
    if profile=='v002':
        from gfi_refined import font_patches as composer
    elif profile!='v001':raise ValueError('Unknown font profile')
    output=output.resolve();report=report.resolve()
    if not output.is_relative_to(ROOT/'work') or output.suffix.lower()!='.iso' or output.exists():
        raise ValueError('Use a new ISO under work/')
    if report.exists() or not report.is_relative_to(ROOT/'reports'):raise ValueError('Use a new report under reports/')
    reference=ROOT/'JOGO/Metal Saga'
    inventory={item['path']:item for item in json.loads((ROOT/'reports/inventory.json').read_text(encoding='utf-8'))}
    elf=reference/'SLUS_212.93'
    with elf.open('rb') as f:
        if hashlib.file_digest(f,'sha256').hexdigest()!=inventory['SLUS_212.93']['sha256']:raise ValueError('ELF revision changed')
    resources=[]
    name='DATA/MAP/MAP.MCT'
    with (reference/name).open('rb') as f,mmap.mmap(f.fileno(),0,access=mmap.ACCESS_READ) as data:
        if hashlib.sha256(data).hexdigest()!=inventory[name]['sha256']:raise ValueError('MAP reference changed')
        group_a,group_b=GROUP_A,GROUP_B
        if profile=='v002':
            group_a='Teste expandido:\nMesmo registro'
            group_b='%F1%M0_5Teste: a\u00e7\u00e3o.\n\u00e1 \u00e9 \u00ed \u00f3 \u00fa\n\u00c7 \u00c1 \u00c9 \u00c3 \u00d5\t'+SECOND_SOURCE.split('\t',1)[1]
        messages=[message_patch(data,PILOT_OFFSET,PILOT_SOURCE,group_a),message_patch(data,SECOND_OFFSET,SECOND_SOURCE,group_b)]
    resources.append({'path':name,'patches':messages})
    fonts=[]
    for name in ('DATA/SYS/SUC20I22.GFI','DATA/SYS/SUC24I26.GFI'):
        data=(reference/name).read_bytes()
        if hashlib.sha256(data).hexdigest()!=inventory[name]['sha256']:raise ValueError('GFI reference changed')
        font=Gfi(data);patches=composer(data)
        # Exercise structural parser and require every other byte to stay identical.
        modified=bytearray(data)
        for patch in patches:modified[patch['offset']:patch['offset']+len(patch['after'])]=patch['after']
        rebuilt=Gfi(modified)
        if rebuilt.rows!=font.rows:raise ValueError('GFI row table changed')
        a=font.ascii_offset('!');b=a+94*font.stride
        if data[a:b]!=modified[a:b]:raise ValueError('ASCII glyph bank changed')
        resources.append({'path':name,'patches':patches})
        fonts.append({'path':name,'source_sha256':hashlib.sha256(data).hexdigest(),
                      'patched_sha256':hashlib.sha256(modified).hexdigest(),'size':len(data),
                      'cell_side':font.side,'glyph_stride':font.stride,'row_23_offset':font.rows[2],
                      'blank_columns_before':font.blank_columns(),'ascii_bank_identical':True,
                      'glyph_edits':[{k:p[k] for k in ('offset','character','bytes','jis')} for p in patches]})
    iso=ROOT/'JOGO/Metal Saga.iso';absolute=[]
    with iso.open('rb') as f:
        original_directory=entries(f)
        for resource in resources:
            candidates=[r for r in original_directory if r['path']==resource['path']]
            if len(candidates)!=1:raise ValueError('Resource extent not unique')
            extent=candidates[0];f.seek(extent['lba']*SECTOR)
            if extent['size']!=inventory[resource['path']]['size'] or digest(f,extent['size'])!=inventory[resource['path']]['sha256']:
                raise ValueError('ISO/extracted resource mismatch')
            resource['lba']=extent['lba']
            absolute.extend({**patch,'offset':extent['lba']*SECTOR+patch['offset']} for patch in resource['patches'])
    absolute.sort(key=lambda p:p['offset'])
    if any(a['offset']+len(a['before'])>b['offset'] for a,b in zip(absolute,absolute[1:])):raise ValueError('Overlapping patches')
    output.parent.mkdir(parents=True,exist_ok=True);partial=output.with_suffix('.iso.partial')
    with iso.open('rb') as src,partial.open('xb') as dst:shutil.copyfileobj(src,dst,1024*1024)
    with partial.open('r+b') as f:
        for patch in absolute:f.seek(patch['offset']);f.write(patch['after'])
    with iso.open('rb') as src,partial.open('rb') as dst:validation=compare_streams(src,dst,absolute)
    if validation['source_iso_sha256']!=ORIGINAL_ISO_SHA256:raise ValueError('Unexpected original ISO')
    with partial.open('rb') as f:
        if entries(f)!=original_directory:raise ValueError('ISO directory changed')
    validation.update({'schema':1,'experiment':'ptbr-gfi-reserved-row23-'+profile,'font_profile':profile,'output_iso':output.relative_to(ROOT).as_posix(),
                       'encoding':'project PT-BR extension using engine SJIS-shaped byte pairs; not standard CP932',
                       'messages':[{k:v for k,v in p.items() if k not in ('before','after')} for p in messages],
                       'mapping':[{'character':c,'unicode':f'U+{ord(c):04X}','bytes':b.hex(' '),'jis':f'{sjis_to_jis(int.from_bytes(b,"big")):04x}'} for c,b in CHAR_TO_BYTES.items()],
                       'fonts':fonts,'iso_directory_identical':True,'elf_identical':True,
                       'resource_extents':[{'path':r['path'],'lba':r['lba']} for r in resources],
                       'visual_status':'pending_user_verification','native_accent_support':False,
                       'glyph_style':'experimental composites of native base letters with added diacritics',
                       'limitations':['new accents use full-width glyph advance','optical spacing not yet validated','no mass accented translation authorized by this experiment']})
    partial.rename(output);report.parent.mkdir(parents=True,exist_ok=True)
    report.write_text(json.dumps(validation,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    print(f'Built {output}; {len(validation["changed_iso_offsets"])} changed bytes; original ELF and ASCII bank preserved')

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,default=ROOT/'work/MetalSaga-ptbr-acentos-v001.iso');parser.add_argument('--report',type=Path,default=ROOT/'reports/acentos-v001-validation.json')
    parser.add_argument('--profile',choices=('v001','v002'),default='v001')
    args=parser.parse_args();create(args.output,args.report,args.profile)

if __name__=='__main__':main()
