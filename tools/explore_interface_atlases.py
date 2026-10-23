"""Read-only, bounded SDA atlas explorer. Discovery never authorizes edits."""
import argparse
import hashlib
import json
import struct
from pathlib import Path

from reinsertion import ROOT, local
from probe_resources import nested
from interface_textures import inspect_texture
from interface_texture_pack import pillow, unpack_indices, replace_indices

SOURCES = ('DATA/RDATA/RTITLE.SDA', 'DATA/FDATA/FNAME_DT.SDA',
           'DATA/FDATA/F_COMMON.SDA', 'DATA/FDATA/FD_POST.SDA',
           'DATA/FDATA/PASSWORD.SDA')


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def classify(raw):
    """Accept exact known structures only; retain unknown records as unknown."""
    if raw[:4] == b'ganm' and len(raw) >= 16:
        _, count, stride, size = struct.unpack_from('<4sIII', raw)
        if stride == 16 and size == 16 + count * 16 and size <= len(raw):
            return {'kind': 'ganm', 'count': count, 'stride': stride,
                    'declared_size': size, 'trailing_bytes': len(raw) - size}
        return {'kind': 'unknown', 'reason': 'invalid GANM bounds/stride'}
    try:
        meta, _ = inspect_texture(raw)
    except ValueError:
        return {'kind': 'unknown', 'reason': 'not a supported texture/GANM'}
    # The explorer proves reversible index transport, not texture usage/UV pairing.
    if replace_indices(raw, unpack_indices(raw, meta)) != raw:
        raise ValueError('Texture index round-trip failed')
    return {'kind': 'texture', 'texture': meta, 'index_roundtrip': True}


def inspect(raw):
    nodes = nested(raw)
    rows = []
    for node in nodes:
        offsets = node['offsets'] + [node['declared_size']]
        for index, (a, b) in enumerate(zip(offsets, offsets[1:])):
            start, end = node['offset'] + a, node['offset'] + b
            record = raw[start:end]
            row = {'node_offset': node['offset'], 'entry': index, 'offset': start,
                   'size': end - start, 'sha256': sha(record)}
            row.update({'kind': 'sda'} if record[:4] == b'sda\0' and
                       any(n['offset'] == start for n in nodes) else classify(record))
            rows.append(row)
    textures = [r for r in rows if r['kind'] == 'texture']
    for row in rows:
        if row['kind'] != 'ganm':
            continue
        sprites = []
        for index in range(row['count']):
            values = struct.unpack_from('<8h', raw, row['offset']+16+index*16)
            x0, y0, x1, y1, hx, hy, reserved0, reserved1 = values
            candidates = [t['offset'] for t in textures if
                          t['node_offset'] == row['node_offset'] and
                          0 <= x0 < x1 <= t['texture']['width'] and
                          0 <= y0 < y1 <= t['texture']['height']]
            sprites.append({'index': index, 'rect': [x0, y0, x1, y1],
                            'hotspot': [hx, hy], 'reserved': [reserved0, reserved1],
                            'geometric_texture_candidates': candidates})
        row['sprites'] = sprites
    return rows


def export(output):
    output = local(output, True)
    if output.exists():
        raise ValueError('Use a new output directory')
    inventory = {r['path']: r for r in json.loads((ROOT/'reports/inventory.json').read_text(encoding='utf-8'))}
    prepared = []
    for resource in SOURCES:
        raw = (ROOT/'JOGO/Metal Saga'/resource).read_bytes()
        if sha(raw) != inventory[resource]['sha256']:
            raise ValueError('Source revision mismatch: ' + resource)
        prepared.append((resource, raw, inspect(raw)))
    Image = pillow()
    from PIL import ImageDraw
    output.mkdir(parents=True)
    resources = []
    for resource, raw, rows in prepared:
        name = Path(resource).stem
        textures = [r for r in rows if r['kind'] == 'texture']
        thumbs = []
        for row in textures:
            meta = row['texture']
            _, rgb = inspect_texture(raw[row['offset']:row['offset']+row['size']])
            image = Image.frombytes('RGB', (meta['width'], meta['height']), rgb)
            png = f"{name}-{row['node_offset']:x}-{row['entry']:03d}.png"
            image.save(output/png)
            row['preview'] = png
            thumb = image.copy()
            thumb.thumbnail((256, 256), Image.Resampling.NEAREST)
            tile = Image.new('RGB', (280, 288), '#303030')
            tile.paste(thumb, ((280-thumb.width)//2, 26))
            ImageDraw.Draw(tile).text((6, 5), f"{name} node {row['node_offset']:x} entry {row['entry']} @{row['offset']:x}", fill='white')
            thumbs.append(tile)
        sheets = []
        for page in range(0, len(thumbs), 12):
            group = thumbs[page:page+12]
            sheet = Image.new('RGB', (1120, 288*((len(group)+3)//4)), '#303030')
            for i, tile in enumerate(group):
                sheet.paste(tile, ((i%4)*280, (i//4)*288))
            filename = f'{name}-sheet-{page//12:02d}.png'
            sheet.save(output/filename)
            sheets.append(filename)
        resources.append({'resource': resource, 'source_sha256': sha(raw),
                          'records': rows, 'contact_sheets': sheets})
    report = {'schema': 1, 'policy': 'read-only-known-sda-atlas-discovery-v001',
              'preview': 'RGB only; raw PS2 alpha not normalized; no edit/import authority',
              'uv_associations': 'not inferred from record adjacency', 'resources': resources}
    (output/'catalogo.json').write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8')
    return report


def main():
    parser = argparse.ArgumentParser(description='Catalogar e visualizar atlas de interface sem alterar originais')
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    report = export(args.output)
    for resource in report['resources']:
        counts = {kind: sum(r['kind'] == kind for r in resource['records'])
                  for kind in ('texture', 'ganm', 'sda', 'unknown')}
        print(resource['resource'], counts)


if __name__ == '__main__':
    main()
