"""Second experimental glyph profile. Keeps v001 generation reproducible."""
import unicodedata
from gfi import Gfi, CHAR_TO_BYTES, sjis_to_jis, pack


def accented_pixels(font, char):
    from PIL import Image, ImageDraw, ImageFilter, ImageChops
    base, mark = unicodedata.normalize('NFD', char)
    side = font.side
    body = Image.new('L', (side, side))
    body.putdata([p * 17 for p in font.pixels(font.ascii_offset(base))])
    # Separate solid strokes from the faint halo when finding attachment points.
    if base == 'i':
        body.paste(0, (0, 0, side, 7 if side == 22 else 8))
    core = body.point(lambda p: 255 if p >= 119 else 0).getbbox()
    if core is None:
        raise ValueError('Missing native stroke')
    left, top, right, bottom = core
    center = (left + right - 1) / 2
    if mark == '\u0327':
        # Anchor in the actual lower stroke, not the bottom of its shadow.
        # Lowercase c retains every original pixel; uppercase C moves up one row.
        shift = max(0, bottom + 3 - side)
        if shift:
            shifted = Image.new('L', body.size)
            shifted.paste(body, (0, -shift))
            body = shifted
            bottom -= shift
        points = [(center, bottom - 1), (center + 1, bottom),
                  (center + 1, bottom + 1), (center - 1, bottom + 2)]
    else:
        # Keep lowercase body unchanged. Uppercase needs at most two rows of
        # vertical compression, retaining the baseline and native width.
        required_top = 5 if side == 22 else 6
        if top < required_top:
            delta = required_top - top
            crop = body.crop((0, top, side, side))
            crop = crop.resize((side, side - required_top), Image.Resampling.LANCZOS)
            body = Image.new('L', (side, side))
            body.paste(crop, (0, required_top))
            top += delta
        low = top - 2
        high = max(0, low - (3 if side == 22 else 4))
        if mark == '\u0301': points = [(center - 1.5, low), (center + 1.5, high)]
        elif mark == '\u0300': points = [(center + 1.5, low), (center - 1.5, high)]
        elif mark == '\u0302': points = [(center - 3, low), (center, high), (center + 3, low)]
        elif mark == '\u0303': points = [(center - 3, low - 1), (center - 1, high + 1), (center + 1, low), (center + 3, high + 2)]
        elif mark == '\u0308': points = None
        else: raise ValueError('Unknown mark')
    scale = 4
    ink = Image.new('L', (side * scale, side * scale))
    draw = ImageDraw.Draw(ink)
    thickness = 1.8 if side == 22 else 2.0
    if points is not None:
        draw.line([(round(x * scale), round(y * scale)) for x, y in points],
                  fill=255, width=round(thickness * scale), joint='curve')
    else:
        for dx in (-2.5, 2.5):
            x = center + dx
            draw.ellipse((int((x-0.9)*scale), int(high*scale),
                          int((x+0.9)*scale), int((high+1.8)*scale)), fill=255)
    ink = ink.resize(body.size, Image.Resampling.LANCZOS)
    halo = ink.filter(ImageFilter.GaussianBlur(0.65)).point(lambda p: round(p * 0.35))
    result = ImageChops.lighter(body, ImageChops.lighter(ink, halo))
    values = result.get_flattened_data() if hasattr(result, 'get_flattened_data') else result.getdata()
    return [min(15, max(0, round(p / 17))) for p in values]


def font_patches(data):
    font = Gfi(data)
    result = []
    for char, pair in CHAR_TO_BYTES.items():
        jis = sjis_to_jis(int.from_bytes(pair, 'big'))
        offset = font.glyph_offset(jis)
        before = data[offset:offset + font.stride]
        if any(before): raise ValueError('Reserved cell is occupied')
        result.append(dict(offset=offset, before=before,
                           after=pack(accented_pixels(font, char)),
                           character=char, bytes=pair.hex(), jis=f'{jis:04x}'))
    return result
