"""Offline reproducible v003 audit: SSD bounds, rejected signatures and coverage."""
from pathlib import Path
import argparse
import collections
import json
import mmap
import re
import struct
import bisect
from dialogue import ROOT, sha
from dialogue_advanced import SsdIndex, LAYOUTS
from gfi import Gfi, sjis_to_jis


def audit(catalog):
    catalog=catalog.resolve()
    if not catalog.is_relative_to(ROOT/'work'):raise ValueError('Use work/')
    elf=(ROOT/'JOGO/Metal Saga/SLUS_212.93').read_bytes()
    expected=json.loads((ROOT/'reports/gfi-encoding-analysis.json').read_text(encoding='utf-8'))['elf_sha256']
    if sha(elf)!=expected:raise ValueError('ELF revision changed')
    words={0x2bc900:0x24020469,0x2bcfe4:0x2494000c,0x2bd00c:0x8c830008,
           0x2bd010:0x0083a821,0x2c563c:0x24050001,0x2c592c:0x24050004,
           0x2c5bac:0x24050005,0x2c5e3c:0x24050005,0x2c58ac:0x24050002,
           0x2c5f5c:0x24c50018,0x2cbb9c:0x24c50030,
           0x2ba324:0x24c50018,0x2bad5c:0x26250020}
    for va,word in words.items():
        if struct.unpack_from('<I',elf,va-0xff000)[0]!=word:raise ValueError(f'Opcode changed: {va:x}')
    ranges={'ssd_header':(0x2bc8c8,96),'ssd_bounds':(0x2bcfd8,76),
            'selection_strings':(0x2c59f0,196),'choice_tab_split':(0x2c57dc,96),
            'msgb_loader':(0x2c5f58,52),'supr_loader':(0x2cbb98,112),
            'mc_loader':(0x2ba2e8,76),'sp_st_loader':(0x2bad38,60)}
    report={'schema':1,'elf_sha256':sha(elf),'opcode_assertions_passed':True,
            'elf_windows':{k:{'virtual_address':va,'file_offset':va-0xff000,'size':n,
                               'sha256':sha(elf[va-0xff000:va-0xff000+n])} for k,(va,n) in ranges.items()}}
    known=set(LAYOUTS)|{b'msg\0',b'msgn'}
    rejected=[];context_resolved=0;tags=collections.Counter();new=collections.Counter();segments=0
    native_pairs=set();uncovered=[]
    with (ROOT/'JOGO/Metal Saga/DATA/MAP/MAP.MCT').open('rb') as stream,mmap.mmap(stream.fileno(),0,access=mmap.ACCESS_READ) as data:
        manifest=json.loads((catalog/'relatorio.json').read_text(encoding='utf-8'))
        if sha(data)!=manifest['source_sha256']:raise ValueError('Catalog does not match MAP')
        index=SsdIndex(data);starts=sorted(index.records)
        for line in (catalog/'catalogo-consolidado.jsonl').open(encoding='utf-8'):
            wrapper=json.loads(line);e=wrapper['record'];at=e['offset']
            if wrapper['classification']=='rejected':
                footer=index.footer(at)
                parent=None;i=bisect.bisect_right(starts,at)-1
                if i>=0:
                    pos=starts[i];ins=index.records[pos]['instruction']
                    if pos<at<pos+ins['size']:parent=pos
                rejected.append({'offset':at,'signature_hex':data[at:at+4].hex(),
                                 'basis':'outside-ssd-end' if footer else 'inside-other-instruction' if parent is not None else 'outside-all-verified-ssd-streams',
                                 'ssd_evidence':footer,'parent_instruction_offset':parent})
            if e.get('context_error') and at in index.records:context_resolved+=1
            if e.get('profile')=='renderer-text-v3':
                new[bytes.fromhex(e['tag']).rstrip(b'\0').decode('ascii')]+=1
                segments+=len(e['segments'])
            for item in [e]+e.get('segments',[]):
                for span in item.get('native_spans',[]):native_pairs.add(span['hex'])
        for at,c in index.records.items():
            tag=data[at:at+4];tags[tag.hex()]+=1
            if tag in known:continue
            size=c['instruction']['size']
            matches=list(re.finditer(rb"[A-Za-z][A-Za-z ,.!?'\-]{14,}",data[at+8:at+size]))
            if matches:uncovered.append({'offset':at,'tag_hex':tag.hex(),'size':size,
                                         'candidate_relative_offsets':[m.start()+8 for m in matches]})
        report.update(ssd_blocks=len(index.blocks),ssd_instructions=len(index.records),ssd_errors=index.errors,
                      instruction_tag_counts=dict(tags),new_text_profiles=dict(new),new_string_segments=segments,
                      rejected_decisions=rejected,rejection_groups=dict(collections.Counter(r['basis'] for r in rejected)),
                      v002_context_boundaries_resolved=context_resolved,
                      text_instruction_count=sum(tags[t.hex()] for t in known),
                      uncovered_textlike_instructions=uncovered,
                      coverage_limit='All 13 known text-bearing instruction families in 2741 verified SSD streams; residual long ASCII spans audited but not a proof about all resources/short strings/indirect text')
    font_coverage={}
    for name in ('SUC20I22.GFI','SUC24I26.GFI'):
        data=(ROOT/'JOGO/Metal Saga/DATA/SYS'/name).read_bytes();font=Gfi(data);checks={}
        extras=struct.unpack_from(f'<{font.extra_count}H',data,font.extra_codes)
        for raw in sorted(native_pairs):
            pair=bytes.fromhex(raw)
            if len(pair)!=2:checks[raw]='halfwidth path not audited';continue
            jis=sjis_to_jis(int.from_bytes(pair,'big'))
            try:offset=font.glyph_offset(jis)
            except ValueError:
                offset=font.extra_start+extras.index(jis)*font.stride if jis in extras else None
            checks[raw]=('nonzero glyph' if offset is not None and any(data[offset:offset+font.stride])
                         else 'blank fullwidth space (expected)' if pair.decode('cp932')=='\u3000'
                         else 'missing/blank')
        font_coverage[name]=checks
    report['native_glyph_inventory']=font_coverage
    report['font_runtime_or_editing_validated']=False
    return report


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--catalog',type=Path,required=True);parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args();output=args.output.resolve()
    if not output.is_relative_to(ROOT/'reports') or output.exists():parser.error('Use um novo relatório em reports/')
    result=audit(args.catalog)
    with output.open('x',encoding='utf-8') as stream:
        json.dump(result,stream,indent=2,ensure_ascii=False);stream.write('\n')
    print('Auditoria offline concluida.')


if __name__=='__main__':main()
