"""Reproduce v002 format evidence without disassembler, network or game edits."""
from pathlib import Path
import argparse
import collections
import json
import mmap
import struct
from dialogue import ROOT, sha


def evidence(catalog):
    catalog = catalog.resolve()
    if not catalog.is_relative_to(ROOT/'work'):
        raise ValueError('Use um catálogo local em work/')
    elf = (ROOT/'JOGO/Metal Saga/SLUS_212.93').read_bytes()
    reference = json.loads((ROOT/'reports/gfi-encoding-analysis.json').read_text(encoding='utf-8'))
    if sha(elf) != reference['elf_sha256']:
        raise ValueError('ELF de outra revisão')
    def word(va): return struct.unpack_from('<I',elf,va-0xff000)[0]
    def jal(va,target):
        if word(va) != (3<<26 | target>>2): raise ValueError('JAL evidence mismatch')
    def exact(va,value):
        if word(va) != value: raise ValueError('Instruction evidence mismatch')
    exact(0x2bd4b4,0x3c020067)  # lui v0, upper msg fourcc
    exact(0x2bd4b8,0x3442736d)
    exact(0x2be134,0x3c026e67)  # upper msgn fourcc
    exact(0x2be138,0x3442736d)
    exact(0x40a884,0x2c5228)    # base msg loader entry
    exact(0x40a84c,0x2c5228)    # named msgn loader entry
    jal(0x2c5230,0x2c5248)
    exact(0x2c5234,0x24050003)  # three 8-byte parameters
    exact(0x2c5270,0x001188c0)  # sll s1,s1,3
    exact(0x2c5278,0x26310008)  # + common eight-byte header
    exact(0x2c5280,0xae12001c)  # store text pointer
    jal(0x2c5494,0x3252c8)      # strchr (TAB)
    jal(0x2c54a4,0x3252c8)      # strchr (NUL)
    exact(0x2c551c,0x26520001)  # skip separator zeros toward display label
    jal(0x2c5548,0x2fc968)      # forward label to UI method
    ranges = {'msg_dispatch':(0x2bd4b4,16),'msgn_dispatch':(0x2be134,16),
              'shared_loader':(0x2c5228,112),'parameter_copy':(0x2c23a0,48),
              'msgn_label_path':(0x2c548c,196)}
    report = {'schema':1,'elf_sha256':sha(elf),'instruction_assertions_passed':True,
              'elf_windows':{k:{'virtual_address':va,'file_offset':va-0xff000,
                                'size':size,'sha256':sha(elf[va-0xff000:va-0xff000+size])}
                             for k,(va,size) in ranges.items()},
              'interpretation':'msg/msgn share three 8-byte parameters after an 8-byte instruction header; msgn walks past NUL and separator zeros to a display-label string; control effects not inferred'}
    counts = collections.Counter(); controls = collections.Counter(); samples = collections.defaultdict(list)
    unknown = []; native = []; labels = 0
    with (ROOT/'JOGO/Metal Saga/DATA/MAP/MAP.MCT').open('rb') as stream, mmap.mmap(stream.fileno(),0,access=mmap.ACCESS_READ) as data:
        manifest = json.loads((catalog/'relatorio.json').read_text(encoding='utf-8'))
        if sha(data) != manifest['source_sha256']: raise ValueError('Catalog/source mismatch')
        for line in (catalog/'catalogo-consolidado.jsonl').open(encoding='utf-8'):
            row = json.loads(line); item = row['record']; state = row['classification']
            counts[state] += 1
            profile = item.get('profile',state)
            if len(samples[profile]) < 4:
                samples[profile].append({'offset':item['offset'],'size':item.get('size'),
                                         'record_sha256':item.get('record_sha256'),'classification':state})
            for token in item.get('control_tokens',[]):
                controls[bytes.fromhex(token['hex']).decode('ascii')] += 1
            if item.get('display_label'): labels += 1
            if item.get('native_spans'):
                native.append({'offset':item['offset'],'sequence_count':len(item['native_spans']),
                               'record_sha256':item['record_sha256']})
            if state == 'pending':
                at = item['offset']; raw = data[at:at+item['size']]
                markers = []; cursor = 0
                while (cursor := raw.find(b'ssd\0',cursor)) >= 0:
                    markers.append(cursor);cursor += 4
                unknown.append({'offset':at,'size':item['size'],'sha256':sha(raw),
                                'parser_failure':item.get('v2_reason'),'ssd_relative_offsets':markers})
    report.update(counts=dict(counts),profile_samples=dict(samples),control_syntax_counts=dict(controls),
                  named_label_records=labels,native_records=native,unresolved_records=unknown,
                  limitations=['opcode assertions cover MIPS subset, not whole R5900 decoding',
                               'display labels are not canonical speaker identities',
                               'ssd crossings are evidence against naive fixed-header parsing, not proof of a complete container layout'])
    return report


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--catalog',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args(); output=args.output.resolve()
    if not output.is_relative_to(ROOT/'reports') or output.exists():
        parser.error('Use um relatório novo em reports/')
    result=evidence(args.catalog)
    with output.open('x',encoding='utf-8') as stream:
        json.dump(result,stream,indent=2,ensure_ascii=False);stream.write('\n')
    print('Evidências e grupos registrados; sem edição dos recursos.')


if __name__=='__main__':main()
