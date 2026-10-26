"""Lossless indexed PNG transport for the newly surveyed UI atlas resources.

Produces standalone work copies only; no ISO integration or generic UV approval.
"""
import argparse
import json
from pathlib import Path

from reinsertion import ROOT, local
from explore_interface_atlases import SOURCES, inspect, sha
from interface_texture_pack import pillow, unpack_indices, replace_indices

POLICY = 'surveyed-ui-atlases-original-palette-v001'
REMAINING_POLICY = 'remaining-ui-atlases-original-palette-v002'
REMAINING_SOURCES = tuple('DATA/FDATA/'+n+'.SDA' for n in
    ('F_COMMON','F_PCDKF','F_SPEND','FBS_DATA','FD_END','FD_POST','FNAME_DT','FNP_VIEW','PASSWORD')) + tuple(
    'DATA/RDATA/'+n+'.SDA' for n in ('RLOADING','RMGALAN','RMGDANCE','RMGDOG','RMGKAERU','RMGTANK','RTITLE')) + ('DATA/S/S_PAINT.SDA',)


def sources(policy=POLICY):
    if policy not in (POLICY,REMAINING_POLICY):raise ValueError('Unknown atlas profile')
    inventory = {r['path']: r for r in json.loads((ROOT/'reports/inventory.json').read_text(encoding='utf-8'))}
    result = {}
    for resource in (SOURCES if policy==POLICY else REMAINING_SOURCES):
        raw = (ROOT/'JOGO/Metal Saga'/resource).read_bytes()
        if sha(raw) != inventory[resource]['sha256']:
            raise ValueError('Atlas source binding mismatch')
        result[resource] = raw
    return result


def entries(originals):
    result = []
    for resource, raw in originals.items():
        for record in inspect(raw):
            if record['kind'] != 'texture':
                continue
            row = dict(record)
            row.update(resource=resource, source_sha256=sha(raw),
                       id=f"{Path(resource).stem}.{row['node_offset']:x}.{row['entry']:03d}")
            row['png'] = row['id']+'.png'
            result.append(row)
    return result


def manifest(rows,policy=POLICY):
    return {'schema': 1, 'policy': policy, 'entries': rows,
            'scope': 'Standalone work copies only; not authorization to patch ISO or all sprite uses',
            'alpha': 'Keep raw original PS2 palette alpha bytes; no normalization',
            'allowed_changes': 'Pixel indices only; dimensions/palette/header/tail/GANM/SDA immutable'}


def export(folder,policy=POLICY):
    folder = local(folder, True)
    originals = sources(policy)
    rows = entries(originals)
    Image = pillow()
    folder.mkdir(parents=True)
    for row in rows:
        meta = row['texture']
        raw = originals[row['resource']][row['offset']:row['offset']+row['size']]
        count = 1 << meta['bpp']
        palette = raw[16:meta['pixel_offset']]
        rgb = bytes(c for i in range(count) for c in palette[i*4:i*4+3])
        alpha = bytes(palette[i*4+3] for i in range(count))
        image = Image.frombytes('P', (meta['width'], meta['height']), unpack_indices(raw, meta))
        image.putpalette(rgb+bytes(768-len(rgb)))
        image.save(folder/row['png'], transparency=alpha, bits=meta['bpp'])
    result = manifest(rows,policy)
    (folder/'manifest.json').write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8')
    return result


def import_pack(folder, output):
    folder = local(folder)
    output = local(output, True)
    if (folder/'manifest.json').is_symlink():
        raise ValueError('Linked manifest blocked')
    actual = json.loads((folder/'manifest.json').read_text(encoding='utf-8'))
    policy=actual.get('policy');originals=sources(policy);rows=entries(originals)
    if actual != manifest(rows,policy):
        raise ValueError('Atlas manifest mismatch')
    Image = pillow()
    selected={r['resource'] for r in rows}
    rebuilt = {resource: bytearray(raw) for resource, raw in originals.items() if resource in selected}
    results = []
    for row in rows:
        path = folder/row['png']
        if path.is_symlink():
            raise ValueError('Linked PNG blocked')
        meta = row['texture']
        before = originals[row['resource']][row['offset']:row['offset']+row['size']]
        count = 1 << meta['bpp']
        palette = before[16:meta['pixel_offset']]
        with Image.open(path) as image:
            if image.mode != 'P' or image.size != (meta['width'], meta['height']):
                raise ValueError('Keep indexed PNG and original dimensions')
            rgb = bytes(c for i in range(count) for c in palette[i*4:i*4+3])
            if bytes(image.getpalette()[:count*3]) != rgb:
                raise ValueError('Palette RGB changed')
            if image.info.get('transparency') != bytes(palette[i*4+3] for i in range(count)):
                raise ValueError('Palette alpha changed')
            indices = image.tobytes()
        after = replace_indices(before, indices)
        if unpack_indices(after, meta) != indices or replace_indices(after, unpack_indices(before, meta)) != before:
            raise ValueError('Atlas index round-trip failed')
        rebuilt[row['resource']][row['offset']:row['offset']+row['size']] = after
        results.append({'id': row['id'], 'changed_bytes': sum(a != b for a, b in zip(before, after)),
                        'sha256': sha(after), 'reverse_roundtrip': True})
    # Reject every malformed asset before creating any output directory/file.
    resources = []
    for resource, data in rebuilt.items():
        if len(data) != len(originals[resource]):
            raise ValueError('Atlas resource length changed')
        resources.append({'resource': resource, 'size': len(data), 'sha256': sha(data),
                          'source_sha256': sha(originals[resource])})
    output.mkdir(parents=True)
    for row in resources:
        path = output/Path(row['resource']).name
        with path.open('xb') as stream:
            stream.write(rebuilt[row['resource']])
        if sha(path.read_bytes()) != row['sha256']:
            raise ValueError('Atlas output readback failed')
    result = {'schema': 1, 'policy': policy, 'records': results, 'resources': resources,
              'iso_modified': False, 'originals_unchanged': True,
              'runtime_visual_status': 'not_tested', 'uv_usage_approval': False}
    (output/'roundtrip.json').write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8')
    return result


def main():
    parser = argparse.ArgumentParser(description='Exportar/importar atlas de interface em cópias; não altera ISO')
    sub = parser.add_subparsers(dest='action', required=True)
    e = sub.add_parser('export')
    e.add_argument('--output', type=Path, required=True)
    e.add_argument('--profile',choices=('legacy','remaining-v002'),default='legacy')
    i = sub.add_parser('import')
    i.add_argument('--pack', type=Path, required=True)
    i.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    result = export(args.output,REMAINING_POLICY if args.profile=='remaining-v002' else POLICY) if args.action == 'export' else import_pack(args.pack, args.output)
    print(f"{len(result['entries'] if args.action == 'export' else result['records'])} texturas processadas; ISO não alterada")


if __name__ == '__main__':
    main()
