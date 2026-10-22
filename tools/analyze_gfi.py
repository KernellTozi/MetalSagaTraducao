"""Reproduce GFI geometry, native code-path evidence and reserved-cell usage survey."""
from pathlib import Path
import argparse,hashlib,json,mmap,re,struct,sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'work/python-deps'))
from gfi import CHAR_TO_BYTES,Gfi,font_patches,sjis_to_jis

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--preview',action='store_true');args=parser.parse_args()
    reference=ROOT/'JOGO/Metal Saga';elf=(reference/'SLUS_212.93').read_bytes()
    code_ranges={'byte_classifier_init':(0x197098,0x197144),'glyph_lookup':(0x197218,0x197340),
                 'byte_stream_reader':(0x197858,0x197910),'sjis_to_jis':(0x197ee8,0x197f74),
                 'gfi_pointer_relocation':(0x1971a8,0x197218)}
    evidence={'elf_sha256':hashlib.sha256(elf).hexdigest(),'elf_file_to_virtual_delta':'0xFF000',
              'code_windows':{key:{'file_offset':start,'virtual_address':start+0xff000,'size':end-start,
                                   'sha256':hashlib.sha256(elf[start:end]).hexdigest()} for key,(start,end) in code_ranges.items()},
              'classification':{'0x20-0x7F':1,'0xA0-0xDF':2,'0x80-0x9F and 0xE0-0xEF':-1,
                                '0xF0-0xF9':-2,'below_0x20':0,'remaining':-1},
              'standard_cp932_requested_characters':[],'fonts':[]}
    for character in CHAR_TO_BYTES:
        try:encoded=character.encode('cp932').hex();status='encodable'
        except UnicodeEncodeError:encoded=None;status='unrepresentable'
        evidence['standard_cp932_requested_characters'].append({'unicode':f'U+{ord(character):04X}','status':status,'bytes':encoded})
    for name in ('SUC20I22.GFI','SUC24I26.GFI'):
        data=(reference/'DATA/SYS'/name).read_bytes();font=Gfi(data)
        evidence['fonts'].append({'name':name,'sha256':hashlib.sha256(data).hexdigest(),'size':len(data),
                                  'side':font.side,'stride':font.stride,'data_start':font.data_start,
                                  'full_glyph_count':3384,'extra_glyph_count':font.extra_count,'halfwidth_kana_count':font.kana_count,
                                  'extra_start':font.extra_start,'kana_start':font.kana_start,'fallback':font.fallback,
                                  'row_offsets':font.rows,'blank_row23_columns':font.blank_columns()})
        if args.preview:
            from PIL import Image,ImageDraw
            patches=font_patches(data);scale=3;cell=font.side*scale+12;height=font.side*scale+35
            preview=Image.new('RGB',(6*cell,3*height),'#303030');draw=ImageDraw.Draw(preview)
            for index,patch in enumerate(patches):
                pixels=[]
                for byte in patch['after']:pixels.extend(((byte&15)*17,(byte>>4)*17))
                glyph=Image.new('L',(font.side,font.side));glyph.putdata(pixels)
                x=index%6*cell;y=index//6*height
                preview.paste(glyph.resize((font.side*scale,font.side*scale)),(x,y))
                draw.text((x,y+font.side*scale+2),f"{patch['character']} {patch['bytes']}",fill='white')
            folder=ROOT/'work/font-analysis';folder.mkdir(parents=True,exist_ok=True)
            preview.save(folder/f'{name}-ptbr-preview.png')
    counts={pair.hex():0 for pair in CHAR_TO_BYTES.values()};count=0
    with (reference/'DATA/MAP/MAP.MCT').open('rb') as f,mmap.mmap(f.fileno(),0,access=mmap.ACCESS_READ) as data:
        for match in re.finditer(rb'msg(?:\x00|n)',data):
            at=match.start()
            if at%4 or at+33>len(data):continue
            size=struct.unpack_from('<H',data,at+6)[0]
            if size<36 or size%4 or at+size>len(data):continue
            raw=data[at+32:at+size].split(b'\0')[0];count+=1
            for pair in CHAR_TO_BYTES.values():counts[pair.hex()]+=raw.count(pair)
    evidence['usage_survey']={'framed_message_candidates':count,'reserved_pair_occurrences':counts,
                             'scope':'heuristic msg-null/msgn candidates in MAP.MCT, not all game resources'}
    evidence['conclusions']={'native_ptbr_not_demonstrated':True,'reserved_cells_blank_in_both_fonts':True,
                             'custom_mapping_uses_existing_reader':True,'visual_rendering_pending':True}
    (ROOT/'reports/gfi-encoding-analysis.json').write_text(json.dumps(evidence,indent=2)+'\n',encoding='utf-8')
    print('GFI structure and lookup evidence written; previews remain local under work/font-analysis')

if __name__=='__main__':main()
