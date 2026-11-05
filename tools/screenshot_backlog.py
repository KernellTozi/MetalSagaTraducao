"""Bounded v067 release for the user's diary, map, dance and paint reports."""
import copy
import json
import mmap
import re
import struct
from collections import Counter
from pathlib import Path

from dialogue import ROOT, sha
from gfi import encode
from interface_graphics import original
from interface_text import SOURCE as ELF, references, sections
from interface_texture_pack import pillow, unpack_indices
from interface_textures import inspect_texture
from reinsertion import SOURCE as MAP
from tank_drinking_gaps import display_palette, metadata

POLICY = 'reported-diary-native-ellipsis-map-and-dance-v001'
PARENT = 'translations/interface-v066.json'
CHILD = 'translations/interface-v067.json'
PARENT_MAP = 'translations/regiao-inicial-v046.json'
CHILD_MAP = 'translations/regiao-inicial-v047.json'
MANIFEST = 'translations/relatos-pos-v066-v001.json'
FOLDER = ROOT / 'work/interface-v067-investigacao'
FONT = Path('C:/Windows/Fonts/arialbd.ttf')
MCT = 'DATA/MAP/MAP.MCT'
DIARY = 'DATA/FDATA/DIARY.DAT'
STATUS = 'Relatos do diário, locais, pintura e dança; MC Hamir revisado; visual pendente.'
LOCATIONS = {
    'Retirement Compound': 'Vila dos Aposentados',
    'First Continental RR Tunnel': 'Túnel 1 - Ferrovia Continental',
    'Land Battleship Tiamat': 'Encouraçado Tiamat',
}
HAMIR = {
    'map.msgn.1774327c': 'E agora?\nIsso não é bom...\nCadê aquilo!?',
    'map.msgn.17743328': '......\t%F1%M0_8Ack!!\tP-Pra que falar\ncomigo assim, do nada!?\nMeu coração não aguenta!\tQue susto!',
}
ELLIPSIS = b'\x81\x63'
DIARY_TEXTS = {
    'title': 'Meu braço!',
    'body': 'E agora?||Dr. Mortem não pode ajudar…||Talvez o Professor Grey possa.',
}


def literal(elf, refs, at, source, target, cell_size=None):
    size = len(source) + 1 if cell_size is None else cell_size
    before = source + bytes(size - len(source))
    after = encode(target) if isinstance(target, str) else target
    if elf[at:at + len(before)] != before or len(after) >= size:
        raise ValueError('Reported ELF literal source or capacity differs')
    if any(at + 0xff000 + i in refs for i in range(1, len(before))):
        raise ValueError('Reported ELF literal has interior references')
    if not refs.get(at + 0xff000):
        raise ValueError('Reported ELF literal lacks a reference')
    if re.findall(rb'\$\x81.', source) != re.findall(rb'\$\x81.', after):
        raise ValueError('Controller icons changed')
    if source.count(b'\n') != after.count(b'\n'):
        raise ValueError('Literal line structure changed')
    return {'id': f'reported.elf.{at:08x}', 'resource': 'SLUS_212.93',
            'offset': at, 'before': before, 'after': after + bytes(len(before) - len(after))}


def elf_patches(elf):
    refs = references(elf, sections(elf))
    specs = [
        (0x342180, b'Load the selected sample paint?\n(Previous paint will be lost)',
         'Carregar esta pintura?\n(A pintura anterior será perdida)'),
        (0x338b18, b'Dance:$\x81{ Exit:$\x81\x9b Help:$\x81\xa2',
         encode('Dançar:') + b'$\x81{ Sair:$\x81\x9b Ajuda:$\x81\xa2', 32),
        (0x31b858, b'Land Battleship Tiamat', 'Encouraçado Tiamat'),
        (0x31b940, b'Land Battleship Tiamat', 'Encouraçado Tiamat'),
    ]
    return [literal(elf, refs, *s) for s in specs]


def diary_patches():
    from diary import fields
    from interface_resources import tokens
    raw = original(DIARY)
    result = []
    for row in fields(raw):
        if row['record'] != 31:
            continue
        at, capacity = row['offset'], row['capacity']
        before = raw[at:at + capacity + 1]
        source = before.split(b'\0')[0]
        text = DIARY_TEXTS[row['field']]
        pieces = text.split('…')
        after = ELLIPSIS.join(encode(s) for s in pieces)
        if row['field'] == 'body':
            if source.count(ELLIPSIS) != 1 or len(pieces) != 2:
                raise ValueError('Diary 31 native ellipsis identity differs')
            if any(c >= 128 for c in source.replace(ELLIPSIS, b'')):
                raise ValueError('Additional native diary bytes remain blocked')
        elif source != b'My Arm!' or len(pieces) != 1:
            raise ValueError('Diary 31 title differs')
        if tokens(source, True) != tokens(after, True) or len(after) > capacity:
            raise ValueError('Diary controls or fixed slot exceeded')
        if b'\0' in after or b'\n' in after:
            raise ValueError('Injected diary delimiter')
        result.append({'id': f'diary.031.{row["field"]}', 'resource': DIARY,
                       'offset': at, 'before': before, 'after': after + bytes(len(before) - len(after))})
    if len(result) != 2:
        raise ValueError('Diary field census differs')
    return result


def location_patches(data):
    from scene_name_fields import parse
    proof = parse(data)
    if (proof['map_count'], proof['name_fields']) != (300, 839):
        raise ValueError('Scene catalogue differs')
    patches, evidence = [], []
    for index in range(300):
        tree, size, blob, script = struct.unpack_from('<4I', data, 0x830 + 16 * index)
        for node in range(0x800 + tree, 0x800 + tree + size, 16):
            typ, children, identity, offset, length = struct.unpack_from('<HHIII', data, node)
            if typ not in (2, 7):
                continue
            at = 0x800 + blob + offset
            field = bytes(data[at:at + 32])
            name = field.split(b'\0')[0]
            source = name.decode('ascii', errors='replace')
            if source not in LOCATIONS:
                continue
            value = encode(LOCATIONS[source])
            span = max(len(name), len(value)) + 1
            if span > 32 or any(field[len(name):span]) or (typ == 7 and length != 216):
                raise ValueError('Location fixed field bounds differ')
            patches.append({'id': f'reported.map.{at:08x}', 'resource': MCT,
                            'offset': at, 'before': field[:span],
                            'after': value + bytes(span - len(value))})
            evidence.append({'map': index, 'node_offset': node, 'type': typ,
                             'node_sha256': sha(data[node:node + 16]),
                             'record_sha256': sha(data[at:at + length]),
                             'translation': LOCATIONS[source]})
    if len(patches) != 6:
        raise ValueError('Reported location occurrence census differs')
    return patches, evidence


def raster_patch(resource, at, rect, text, size, kind):
    Image = pillow()
    from PIL import ImageDraw, ImageFont, ImageFilter
    from explore_interface_atlases import inspect
    raw = original(resource)
    rows = inspect(raw)
    row = next(r for r in rows if r['offset'] == at and r['kind'] == 'texture')
    meta = row['texture']
    record = raw[at:at + row['size']]
    if meta['bpp'] != 8:
        raise ValueError('Reported raster needs indexed 8-bit transport')
    pixels = unpack_indices(record, meta)
    palette = display_palette(record)
    image = Image.frombytes('L', (meta['width'], meta['height']), pixels)
    x, y, right, bottom = rect
    used = Counter(image.crop(rect).tobytes())
    font = ImageFont.truetype(str(FONT), size)
    box = font.getbbox(text)
    ink = Image.new('L', (box[2] - box[0] + 2, box[3] - box[1] + 2))
    ImageDraw.Draw(ink).text((1 - box[0], 1 - box[1]), text, font=font, fill=255)
    if ink.width > right - x or ink.height > bottom - y:
        raise ValueError('Reported raster word exceeds original sprite')
    out = image.copy()
    if kind == 'tank':
        background, foreground, stroke = 0, 255, 85
        if palette[background][3] != 0 or palette[foreground] != (255,255,255,127):
            raise ValueError('Tank icon palette differs')
        outline = ink.filter(ImageFilter.MaxFilter(3))
        canvas = Image.new('L', ink.size, background)
        shades = [i for i in used if palette[i][3] == 127 and len(set(palette[i][:3])) == 1]
        for iy in range(ink.height):
            for ix in range(ink.width):
                coverage = ink.getpixel((ix, iy))
                if outline.getpixel((ix, iy)) >= 64:
                    shade = 40 + round(coverage * 215 / 255)
                    canvas.putpixel((ix, iy), min(shades, key=lambda i: abs(palette[i][0] - shade)))
    else:
        background, foreground = 54, 176
        if palette[background] != (93,78,66,128) or palette[foreground] != (239,155,13,128):
            raise ValueError('Dance HUD palette differs')
        shades = list(used)
        canvas = Image.new('L', ink.size, background)
        for iy in range(ink.height):
            for ix in range(ink.width):
                coverage = ink.getpixel((ix, iy)) / 255
                color = tuple(round(a + coverage * (b-a)) for a,b in zip(palette[background], palette[foreground]))
                canvas.putpixel((ix, iy), min(shades, key=lambda i: sum((a-b)**2 for a,b in zip(palette[i], color))))
    out.paste(background, rect)
    left = x + (right - x - ink.width) // 2
    top = y + (bottom - y - ink.height) // 2
    out.paste(canvas, (left, top))
    sprite_at, sprite_index, expected_rect = ((0x10500, 0, [4,4,196,70]) if kind == 'tank'
                                             else (0x141210, 3, [0,0,456,32]))
    sprite = raw[sprite_at + 16 + sprite_index*16:sprite_at + 32 + sprite_index*16]
    if list(struct.unpack('<8h', sprite)[:4]) != expected_rect:
        raise ValueError('Reported sprite descriptor differs')
    if not (expected_rect[0] <= x < right <= expected_rect[2] and expected_rect[1] <= y < bottom <= expected_rect[3]):
        raise ValueError('Raster rectangle outside sprite')
    patch = {'id': f'reported.raster.{kind}', 'resource': resource,
             'offset': at + meta['pixel_offset'], 'before': pixels, 'after': out.tobytes()}
    evidence = {'resource_sha256': sha(raw), 'texture_sha256': sha(record),
                'texture_offset': at, 'texture': meta, 'rect': list(rect),
                'translation': text, 'font_size': size, 'mask_sha256': sha(ink.tobytes()),
                'sprite_offset': sprite_at + 16 + sprite_index*16, 'sprite_sha256': sha(sprite)}
    FOLDER.mkdir(exist_ok=True)
    board = Image.new('RGB', ((right-x)*6, (bottom-y)*3 + 22), (30,30,30))
    draw = ImageDraw.Draw(board)
    for col, source in enumerate((image, out)):
        crop = source.crop(rect)
        rgb = bytes(v for i in crop.tobytes() for v in palette[i][:3])
        preview = Image.frombytes('RGB', crop.size, rgb).resize((crop.width*3,crop.height*3), Image.Resampling.NEAREST)
        board.paste(preview, (col*crop.width*3,22))
        draw.text((col*crop.width*3+3,3), 'Original' if col == 0 else 'PT-BR', fill='white')
    board.save(FOLDER / f'{kind}-comparacao.png')
    return patch, evidence


def derive(elf):
    patches = elf_patches(elf) + diary_patches()
    with MAP.open('rb') as stream, mmap.mmap(stream.fileno(),0,access=mmap.ACCESS_READ) as data:
        locations, location_evidence = location_patches(data)
    patches.extend(locations)
    graphics = []
    for spec in [('DATA/MAP/HMAPAC.SDA',0x80,(90,44,192,70),'Sem tanques',14,'tank'),
                 ('DATA/RDATA/RMGDANCE.SDA',0x130e00,(34,5,100,27),'TEMPO',17,'dance')]:
        patch, evidence = raster_patch(*spec)
        patches.append(patch)
        graphics.append(evidence)
    return patches, {'locations': location_evidence, 'graphics': graphics,
                     'font_sha256': sha(FONT.read_bytes()),
                     'diary_sha256': sha(original(DIARY))}


def binding_load(binding):
    if set(binding) != {'recipe','sha256'} or binding['recipe'] != MANIFEST:
        raise ValueError('Unknown reported backlog binding')
    raw = (ROOT / MANIFEST).read_bytes()
    manifest = json.loads(raw)
    if (sha(raw) != binding['sha256'] or manifest['policy'] != POLICY
        or manifest['parent_sha256'] != sha((ROOT/PARENT).read_bytes())
        or manifest['parent_map_sha256'] != sha((ROOT/PARENT_MAP).read_bytes())):
        raise ValueError('Reported backlog manifest or parent differs')
    return manifest


def validate(recipe):
    manifest = binding_load(recipe['screenshot_backlog_release'])
    parent = json.loads((ROOT/PARENT).read_bytes())
    expected = copy.deepcopy(parent)
    expected.update(screenshot_backlog_release=recipe['screenshot_backlog_release'],
                    base_dialogue_draft=CHILD_MAP, iso_name='MetalSaga-ptbr-interface-v067.iso', status=STATUS)
    if expected != recipe:
        raise ValueError('Unrelated reported backlog UI mutation')
    return parent, manifest


def compile_interface(elf, recipe):
    from interface_text import compile_draft
    parent, manifest = validate(recipe)
    patches, report = compile_draft(elf, parent)
    new, evidence = derive(elf)
    if manifest['new'] != [metadata(p) for p in new] or manifest['evidence'] != evidence:
        raise ValueError('Reported backlog output or evidence differs')
    for patch in new:
        if any(p['resource'] == patch['resource'] and max(p['offset'],patch['offset']) < min(p['offset']+len(p['before']),patch['offset']+len(patch['before'])) for p in patches):
            raise ValueError('Reported backlog overlaps inherited translation')
        patches.append(patch)
    report = copy.deepcopy(report)
    report['accepted'] += len(new)
    report['screenshot_backlog_release'] = {'policy': POLICY, 'new_units': len(new),
        'diary_fields': 2, 'map_names': 6, 'elf_literals': 4, 'raster_labels': 2,
        'pcsx2_executed': False, 'visual_status': 'pending_user'}
    return patches, report


def validate_narrative(draft):
    from build_translation_pilot import load_draft
    manifest = binding_load(draft['hamir_context_review'])
    expected, _ = load_draft(ROOT/PARENT_MAP)
    expected['translations'].update(HAMIR)
    expected.update(hamir_context_review=draft['hamir_context_review'], name='regiao-inicial-v047',
                    status=STATUS, reviewed_changes=list(HAMIR))
    if expected != draft:
        raise ValueError('Unrelated Hamir narrative mutation')
    return manifest


def compile_narrative(data, draft):
    from build_translation_pilot import load_draft, compile_draft
    from reinsertion import compile_entry
    validate_narrative(draft)
    parent, _ = load_draft(ROOT/PARENT_MAP)
    doc, patches, report = compile_draft(data, parent)
    replacements = {}
    report = copy.deepcopy(report)
    for key, target in HAMIR.items():
        entry = next(e for e in doc['entries'] if e['id'] == key)
        if entry['mode'] != 'slots' or len(entry['segments']) != 2 or entry['blocked_reasons']:
            raise ValueError('Hamir fixed record structure differs')
        before = bytes.fromhex(entry['segments'][0]['source_hex'])
        if [c for c in before if c in (9,10)] != [c for c in encode(target) if c in (9,10)]:
            raise ValueError('Hamir page and line control sequence changed')
        changed = copy.deepcopy(entry)
        changed['segments'][0]['translation'] = target
        patch, info = compile_entry(data, changed, changed, quirk_refs=True)
        if not patch:
            raise ValueError('Hamir replacement missing')
        replacements[key] = patch
        entry['segments'][0]['translation'] = target
        next(r for r in report['results'] if r['id'] == key).update(target_lengths=info['target_lengths'],warnings=info['warnings'])
    report['hamir_context_review'] = {'policy': POLICY, 'revised_dialogues': 2, 'pcsx2_executed': False}
    return doc, [replacements.get(p['id'],p) for p in patches], report


def prepare():
    patches, evidence = derive(ELF.read_bytes())
    manifest = {'schema':1, 'policy':POLICY, 'parent':PARENT,
                'parent_sha256':sha((ROOT/PARENT).read_bytes()), 'parent_map':PARENT_MAP,
                'parent_map_sha256':sha((ROOT/PARENT_MAP).read_bytes()),
                'new':[metadata(p) for p in patches], 'evidence':evidence}
    raw = (json.dumps(manifest,ensure_ascii=False,indent=2)+'\n').encode()
    (ROOT/MANIFEST).write_bytes(raw)
    binding = {'recipe':MANIFEST,'sha256':sha(raw)}
    child = copy.deepcopy(json.loads((ROOT/PARENT).read_bytes()))
    child.update(screenshot_backlog_release=binding, base_dialogue_draft=CHILD_MAP,
                 iso_name='MetalSaga-ptbr-interface-v067.iso', status=STATUS)
    (ROOT/CHILD).write_bytes((json.dumps(child,ensure_ascii=False,indent=2)+'\n').encode())
    narrative = {'schema':1,'extends':PARENT_MAP.rsplit('/',1)[1],'name':'regiao-inicial-v047',
                 'status':STATUS,'translations':HAMIR,'reviewed_changes':list(HAMIR),'hamir_context_review':binding}
    (ROOT/CHILD_MAP).write_bytes((json.dumps(narrative,ensure_ascii=False,indent=2)+'\n').encode())
    validate(child)
    print(json.dumps({'new_patches':len(patches),'hamir_revisions':len(HAMIR)}))


if __name__ == '__main__':
    prepare()
