"""Offline, read-only MAP.MCT extractor. Stream results; reuse proven ASCII parser."""
from pathlib import Path
import argparse
import collections
from datetime import datetime
import json
import mmap
import re
import struct
import time

from dialogue import ROOT, record, instruction, neighbors, sha, changes
from build_accent_experiment import SECOND_OFFSET, SECOND_SOURCE, CONTROLS

RESOURCE = 'DATA/MAP/MAP.MCT'
DEFAULT_SOURCE = ROOT/'JOGO/Metal Saga'/RESOURCE


def inspect(data, at):
    """Return disposition and record. Unknown variants never enter editable plan."""
    try:
        info = instruction(data, at)
    except ValueError as error:
        return 'rejected', {'offset': at, 'reason': str(error),
                            'signature_hex': data[at:at+4].hex()}
    tag = data[at:at+4]
    if tag == b'msg\0':
        try:
            item = record(data, at)
            return 'validated', {**item, 'profile': 'ascii-lf-v1',
                                 'original_text_hex': item['source'].encode('ascii').hex(),
                                 'control_hex': [t.hex() for t in CONTROLS.findall(item['source'].encode('ascii'))]}
        except ValueError as error:
            reason = str(error)
    else:
        reason = 'msgn layout not proven; do not assume 32-byte header'
    # Retain all bytes of a framed uncertain record, without guessing its encoding.
    pending = {**info, 'id': f'map.candidate.{at:08x}', 'reason': reason,
               'record_hex': data[at:at+info['size']].hex(),
               'editable': False}
    if tag != b'msg\0' or info['size'] < 36:
        return 'pending', pending
    slot = data[at+32:at+info['size']]
    end = slot.find(b'\0')
    if end <= 0 or any(slot[end:]):
        return 'pending', pending
    raw = slot[:end]
    if any(c not in (9,10) and not 32 <= c <= 126 for c in raw):
        return 'pending', pending
    source = raw.decode('ascii')
    pending.update(readable_candidate=source, assumed_text_offset=at+32,
                   control_hex=[t.hex() for t in CONTROLS.findall(raw)])
    # This single controlled record has binary and user visual evidence. Other
    # command combinations remain pending, even if they look like English.
    if at == SECOND_OFFSET and source == SECOND_SOURCE:
        try:
            surrounding = neighbors(data, at)
        except ValueError:
            return 'pending', pending
        item = {**info, 'id':f'map.msg.{at:08x}', 'text_offset':at+32,
                'capacity':len(slot)-1, 'header_hex':data[at:at+32].hex(),
                'record_sha256':sha(data[at:at+info['size']]),
                'source':source, 'translation':source, 'neighbors':surrounding,
                'profile':'nina-controlled-pilot-v1', 'original_text_hex':raw.hex(),
                'control_hex':[t.hex() for t in CONTROLS.findall(raw)]}
        return 'validated', item
    return 'pending', pending


def reconstruct(item):
    """Unedited record, including exact original header, NUL and zero padding."""
    raw = bytes.fromhex(item['original_text_hex'])
    if raw.decode('ascii') != item['source']:
        raise ValueError('Text/byte mismatch')
    slot_size = item['capacity']+1
    if len(raw) >= slot_size:
        raise ValueError('Overflow or missing NUL')
    return bytes.fromhex(item['header_hex']) + raw + bytes(slot_size-len(raw))


def scan(data):
    for match in re.finditer(rb'msg(?:\x00|n)', data):
        yield inspect(data, match.start())


def legacy_entry(item):
    return {k:v for k,v in item.items() if k not in ('profile','original_text_hex','control_hex')}


def extract(source, output):
    started = time.perf_counter()
    source, output = source.resolve(), output.resolve()
    if source != DEFAULT_SOURCE.resolve() and not source.is_relative_to(ROOT/'work'):
        raise ValueError('Fonte deve ser o MAP de referência ou uma cópia em work/')
    if not output.is_relative_to(ROOT/'work') or output.exists():
        raise ValueError('Use uma pasta nova em work/; resultados anteriores são preservados')
    output.mkdir(parents=True)
    counts = collections.Counter(validated=0, pending=0, rejected=0)
    reasons = {'pending':collections.Counter(), 'rejected':collections.Counter()}
    profiles = collections.Counter()
    ascii_entries = []
    with source.open('rb') as stream:
        if source.stat().st_size == 0:
            raise ValueError('Arquivo vazio')
        with mmap.mmap(stream.fileno(), 0, access=mmap.ACCESS_READ) as data:
            source_hash = sha(data)
            inventory = json.loads((ROOT/'reports/inventory.json').read_text(encoding='utf-8'))
            expected = next(e['sha256'] for e in inventory if e['path'] == RESOURCE)
            if source == DEFAULT_SOURCE.resolve() and source_hash != expected:
                raise ValueError('Hash do MAP original diverge do inventário')
            with (output/'dialogos.jsonl').open('x', encoding='utf-8') as good, \
                 (output/'pendentes.jsonl').open('x', encoding='utf-8') as pending, \
                 (output/'rejeitados.jsonl').open('x', encoding='utf-8') as rejected:
                files = {'validated':good, 'pending':pending, 'rejected':rejected}
                for state, item in scan(data):
                    counts[state] += 1
                    if state == 'validated':
                        rebuilt = reconstruct(item)
                        at = item['offset']
                        if rebuilt != data[at:at+item['size']]:
                            raise ValueError(f'Round-trip incorreto em 0x{at:X}')
                        profiles[item['profile']] += 1
                        if item['profile'] == 'ascii-lf-v1':
                            ascii_entries.append(legacy_entry(item))
                    else:
                        reasons[state][item['reason']] += 1
                    files[state].write(json.dumps(item, ensure_ascii=False)+'\n')
            plan = {'schema':1, 'resource':RESOURCE, 'source_sha256':source_hash,
                    'policy':'msg-null-fixed-size-ascii-lf-v1', 'entries':ascii_entries}
            if changes(data, plan):
                raise ValueError('Plano sem traduções produziu alterações')
            if sha(data) != source_hash:
                raise ValueError('Fonte mudou durante a extração')
            baseline = ROOT/'work/dialogue-catalog-ascii-v001.json'
            comparison = {'available':False}
            if baseline.is_file():
                old = json.loads(baseline.read_text(encoding='utf-8'))
                if old['source_sha256'] == source_hash:
                    comparison = {'available':True, 'baseline_entries':len(old['entries']),
                                  'exact_entries_equal':old['entries'] == ascii_entries}
                    if not comparison['exact_entries_equal']:
                        raise ValueError('Catálogo ASCII diverge da base já investigada')
    with (output/'plano-ascii.json').open('x', encoding='utf-8') as stream:
        json.dump(plan, stream, ensure_ascii=False, indent=2)
        stream.write('\n')
    summary = {'schema':1, 'source':source.relative_to(ROOT).as_posix(),
               'resource':RESOURCE, 'source_sha256':source_hash, 'source_size':source.stat().st_size,
               'recognized_revision':source_hash == expected, 'counts':dict(counts),
               'total_signatures':sum(counts.values()), 'profiles':dict(profiles),
               'reasons':{k:dict(v) for k,v in reasons.items()},
               'baseline_comparison':comparison, 'record_roundtrip_passed':True,
               'ascii_no_edit_patches':0, 'source_hash_unchanged':True,
               'elapsed_seconds':round(time.perf_counter()-started,3),
               'context':'physical offsets, local indices, raw headers, three adjacent instructions; speaker/scene mapping unknown',
               'scope':'heuristic msg-null/msgn signatures, not a complete script container parser',
               'output_files':['dialogos.jsonl','pendentes.jsonl','rejeitados.jsonl','plano-ascii.json'],
               'completed':True}
    with (output/'relatorio.json').open('x', encoding='utf-8') as stream:
        json.dump(summary, stream, ensure_ascii=False, indent=2)
        stream.write('\n')
    return summary


def main():
    parser = argparse.ArgumentParser(description='Extrator local e offline de diálogos Metal Saga')
    parser.add_argument('--source', type=Path, default=DEFAULT_SOURCE)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    output = args.output or ROOT/'work/extracoes'/datetime.now().strftime('%Y%m%d-%H%M%S-%f')
    try:
        summary = extract(args.source, output)
        print(f'Concluído: {output.resolve()}')
        print(json.dumps(summary['counts'], ensure_ascii=False))
        print('Nenhum texto traduzido; nenhum arquivo do jogo modificado.')
    except (ValueError, OSError, KeyError) as error:
        parser.exit(2, f'Erro: {error}\nPasta sem relatorio.json completo não é uma extração concluída.\n')


if __name__ == '__main__':
    main()
