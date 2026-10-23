"""Opt-in static title atlas labels with original consumers and native raster style."""
import argparse
import json
from pathlib import Path
import struct

from reinsertion import ROOT, local
from glyph_spacing import ORIGINAL_SHA
from interface_graphics import original, sha
from interface_textures import inspect_texture
from interface_texture_pack import pillow, unpack_indices, replace_indices
from title_native_font import RESOURCE, render

POLICY = 'title-native-raster-v006'
WINDOWS = ((0x38518, 0x3869c, '131f45153034ce67491ca49a3165d52c07bfd5adc59fc1fd66553ecb0ae96e52'),
           (0x386c0, 0x3875c, 'a0f01ff66a34118e9759bfcf439a831038732f75d51805b5145c34ba979d67e2'),
           (0x37de8, 0x37ea4, 'e877e59838f9aff80ad54612df15f17aa1cd8c2dcba4c0fb7fbf2c8e3f3ce983'),
           (0x19af80, 0x19afac, 'd5de4241dd1c35ef31f666cf3df684433d6a634d7479bf8cf679bfb7d5ef67d2'),
           (0x1acc58, 0x1acd38, '3f9e0c8bd8495ba82d88b4397dc628ba3958d0faa3325b7aa2869e3dc716ab04'),
           (0x2641c8, 0x264228, 'abaa5ca9274d9d13a809db8202aa7dcf1515098a4f5b7c2f4e34c025164bc866'))


def evidence(elf, raw):
    if sha(elf) != ORIGINAL_SHA:
        raise ValueError('Title consumer ELF mismatch')
    for a, z, digest in WINDOWS:
        if sha(elf[a:z]) != digest:
            raise ValueError('Title consumer instruction/data window changed')
    descriptor = struct.unpack_from('<4I', elf, 0x2641c8)
    if descriptor != (32, 66576, 66608, 112):
        raise ValueError('Title descriptor mismatch')
    # Static GANM: u16 frames, u16 animation count, frame offset, animation offset.
    # The field at +8 is an offset, not a stride inferred from its value 16.
    header = struct.unpack_from('<4sHHII', raw, 66608)
    if header != (b'ganm', 6, 0, 16, 112):
        raise ValueError('Title static GANM topology mismatch')
    sprites = [struct.unpack_from('<8h', raw, 66624+i*16) for i in range(6)]
    for index in range(3):
        if sprites[index] != (0, index*24, 180, (index+1)*24, 90, 12, 0, 0):
            raise ValueError('Title label rectangle/hotspot changed')
    objects = [struct.unpack_from('<Iff', elf, 0x2641e0+i*12) for i in range(6)]
    if [row[0] for row in objects] != [5, 0, 1, 2, 4, 3]:
        raise ValueError('Title sprite object order changed')
    return {'elf_sha256': sha(elf),
            'instruction_windows': [{'offset': a, 'size': z-a, 'sha256': h} for a, z, h in WINDOWS],
            'descriptor_offset': 0x2641c8, 'texture_offset': descriptor[0], 'texture_size': descriptor[1],
            'ganm_offset': descriptor[2], 'ganm_size': descriptor[3],
            'static_frames': 6, 'animations': 0, 'frame_table_offset': 16,
            'object_frames_and_positions': [list(r) for r in objects],
            'rectangles': [list(r) for r in sprites],
            'verification': 'Original instructions/data inspected and hash-bound; no full CPU or game execution'}


def compile_title(config):
    if config.get('policy') != POLICY:
        raise ValueError('Unknown title policy')
    binding = config['parent']
    if binding.get('recipe') != 'translations/interface-graphics-v005.json':
        raise ValueError('Title profile must preserve the aligned Satcom parent')
    path = ROOT/binding['recipe']
    payload = path.read_bytes()
    if sha(payload) != binding['sha256']:
        raise ValueError('Title parent recipe mismatch')
    raw = original(RESOURCE)
    if config.get('source_sha256') != sha(raw):
        raise ValueError('Title resource binding mismatch')
    proof = evidence(original('SLUS_212.93'), raw)
    after, rows = render()
    if config.get('entries') != rows:
        raise ValueError('Title reviewed labels/masks/geometry mismatch')
    before = raw[32:66608]
    meta, _ = inspect_texture(before)
    old = unpack_indices(before, meta)
    new = unpack_indices(after, meta)
    for i, (a, b) in enumerate(zip(old, new)):
        if a != b and not (i % 256 < 180 and i // 256 < 72):
            raise ValueError('Title change outside the three label rectangles')
    at, size = meta['pixel_offset'], meta['pixel_bytes']
    if before[:at] != after[:at] or before[at+size:] != after[at+size:]:
        raise ValueError('Title header/palette/tail changed')
    if replace_indices(after, old) != before:
        raise ValueError('Title reverse round-trip failed')
    from interface_graphics import compile_graphics
    patches, inherited = compile_graphics(json.loads(payload))
    patches.append({'resource': RESOURCE, 'id': 'title.texture.0', 'offset': 32+at,
                    'before': before[at:at+size], 'after': after[at:at+size]})
    results = inherited['results']+[{'id': f'title.label.{r["index"]}', 'family': 'title',
                                    'resource': RESOURCE, 'texture': 0, **r} for r in rows]
    return patches, {'policy': POLICY, 'accepted': inherited['accepted']+3, 'patches': len(patches),
                     'source_sha256': sha(raw), 'parent': binding,
                     'palettes_headers_ganm_unchanged': True, 'reverse_roundtrip': True,
                     'runtime_visual_status': 'pending_user_verification',
                     'title_evidence': proof, 'results': results}


def main():
    parser = argparse.ArgumentParser(description='Conferir título traduzido e preservar gráficos anteriores; sem ISO')
    parser.add_argument('--recipe', type=Path, default=ROOT/'translations/interface-graphics-v006.json')
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    recipe = args.recipe.resolve()
    if not recipe.is_relative_to(ROOT/'translations'):
        raise ValueError('Use receita revisada em translations/')
    output = local(args.output, True)
    patches, report = compile_title(json.loads(recipe.read_text(encoding='utf-8')))
    raw = original(RESOURCE)
    modified = bytearray(raw)
    for p in patches:
        if p['resource'] == RESOURCE:
            modified[p['offset']:p['offset']+len(p['after'])] = p['after']
    Image = pillow()
    from PIL import ImageDraw
    comparison = Image.new('RGB', (720, 170), '#303030')
    for column, (name, data) in enumerate((('ORIGINAL', raw), ('PT-BR', modified))):
        meta, rgb = inspect_texture(data[32:66608])
        image = Image.frombytes('RGB', (meta['width'], meta['height']), rgb)
        image = image.crop((0, 0, 180, 72)).resize((360, 144), Image.Resampling.NEAREST)
        comparison.paste(image, (column*360, 26))
        ImageDraw.Draw(comparison).text((column*360+8, 6), name, fill='white')
    output.mkdir(parents=True)
    comparison.save(output/'comparacao-titulo.png')
    report.update(iso_modified=False, recipe_sha256=sha(recipe.read_bytes()))
    (output/'relatorio.json').write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8')
    print(f"{report['accepted']} rótulos conferidos, incluindo os três do título; ISO não alterada")


if __name__ == '__main__':
    main()
