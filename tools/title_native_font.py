"""Title-only raster construction from original indexed glyphs; no font substitution."""
from functools import lru_cache
from interface_graphics import original, sha
from interface_textures import inspect_texture
from interface_texture_pack import unpack_indices, replace_indices, pillow

RESOURCE = 'DATA/RDATA/RTITLE.SDA'
SAMPLES = {'C': (24, 2, 26), 'O': (24, 25, 49), 'N': (24, 48, 73),
           'T': (24, 72, 97), 'I': (24, 97, 110), 'U': (24, 135, 160),
           'E': (24, 160, 179), 'W': (0, 42, 83), 'G': (0, 89, 113),
           'A': (0, 112, 136), 'M': (0, 135, 161), 'S': (48, 54, 80),
           'L': (48, 141, 159)}
LABELS = ('NOVO JOGO', 'RETOMAR', 'INSTALAR')


@lru_cache(maxsize=2)
def alphabet(revised=False):
    Image = pillow()
    raw = original(RESOURCE)[32:66608]
    meta, _ = inspect_texture(raw)
    atlas = Image.frombytes('L', (256, 256), unpack_indices(raw, meta))
    colors = [tuple(raw[16+i*4:20+i*4]) for i in range(256)]
    # Tight native ink bounds; retain one pixel of original soft edge on each side.
    result = {}
    for char, (y, x0, x1) in SAMPLES.items():
        glyph = atlas.crop((x0, y, x1, y+24))
        core = glyph.point([255 if max(c[:3]) >= 176 else 0 for c in colors])
        box = core.getbbox()
        result[char] = glyph.crop((max(0, box[0]-1), 0, min(glyph.width, box[2]+1), 24))
    # V: the right-hand V of the original broad W, preserving its original slope.
    w = result['W']
    result['V'] = w.crop((w.width//2-1, 0, w.width, 24))
    # J: right stem and lower bowl of U; remove only its upper left stem.
    j = result['U'].copy()
    for yy in range(2, 15):
        for xx in range(0, j.width//2):
            j.putpixel((xx, yy), 0)
    result['J'] = j
    # R: native O upper bowl over the N's left stem and descending diagonal.
    r = result['N'].copy()
    o = result['O']
    for yy in range(0, 12):
        for xx in range(r.width):
            r.putpixel((xx, yy), o.getpixel((xx, yy)) if xx < o.width else 0)
    e = result['E']
    for yy in range(0, 12):
        for xx in range(min(8+(max(0, yy-8)//4), e.width)):
            r.putpixel((xx, yy), e.getpixel((xx, yy)))
    result['R'] = r
    if revised:
        # A real R needs an open lower counter and a diagonal leg, not the
        # N's complete right stem. Keep native pixel values, height and slope.
        r = Image.new('L', (24, 24))
        n = result['N']
        for y in range(24):
            if y < 7:
                for x in range(o.width):r.putpixel((x,y),o.getpixel((x,y)))
            elif y < 12:
                for x in range(12,o.width):r.putpixel((x+2,y),o.getpixel((x,y)))
            if y < 12:
                for x in range(min(9,e.width)):r.putpixel((x,y),e.getpixel((x,y)))
            elif y < 14:
                for x in range(n.width):r.putpixel((x,y),n.getpixel((x,y)))
            elif y < 20:
                for x in range(12):r.putpixel((x,y),n.getpixel((x,y)))
                for x in range(13,21):r.putpixel((x-2+y-14,y),n.getpixel((x,y)))
        result['R'] = r
    return result


def line(text,revised=False):
    Image = pillow()
    glyphs = alphabet(revised)
    if not text or any(char != ' ' and char not in glyphs for char in text):
        raise ValueError('Unsupported title character or empty label')
    width = sum(7 if char == ' ' else glyphs[char].width-1 for char in text)+1
    if width > 176:
        raise ValueError(f'Title label overflow: {text}: {width}')
    canvas = Image.new('L', (width, 24))
    raw = original(RESOURCE)[32:66608]
    colors = [tuple(raw[16+i*4:20+i*4]) for i in range(256)]
    priority = [(max(c[:3]), c[3]) for c in colors]
    cursor = 0
    for char in text:
        if char == ' ':
            cursor += 7
            continue
        glyph = glyphs[char]
        for y in range(24):
            for x in range(glyph.width):
                value = glyph.getpixel((x, y))
                if priority[value] > priority[canvas.getpixel((cursor+x, y))]:
                    canvas.putpixel((cursor+x, y), value)
        cursor += glyph.width-1
    return canvas


def render(revised=False):
    raw = original(RESOURCE)
    before = raw[32:66608]
    meta, _ = inspect_texture(before)
    pixels = bytearray(unpack_indices(before, meta))
    rows = []
    for index, text in enumerate(LABELS):
        glyph = line(text,revised)
        encoded = glyph.tobytes()
        x0 = (180-glyph.width)//2
        for y in range(24):
            start = (index*24+y)*256
            pixels[start:start+180] = bytes(180)
            pixels[start+x0:start+x0+glyph.width] = encoded[y*glyph.width:(y+1)*glyph.width]
        rows.append({'index': index, 'translation': text, 'width': glyph.width,
                     'mask_sha256': sha(glyph.tobytes()), 'rect': [0, index*24, 180, (index+1)*24]})
    return replace_indices(before, pixels), rows
