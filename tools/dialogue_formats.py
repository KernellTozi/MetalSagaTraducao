"""MAP msg/msgn parsers backed by ELF loaders at VA 2C5228/2C5248/2C5410.

Extraction only: no new edit policy, pointer rewriting or guessed control effects.
"""
import re
import struct
from dialogue import instruction, neighbors, sha
from gfi import sjis_to_jis

KNOWN_COMMAND = re.compile(rb'%(?:[FNWP]-?\d+|M-?\d+_-?\d+)')
OPAQUE_COMMAND = re.compile(rb'%(?:[A-Za-z](?:-?\$?\d+)?(?:_-?\d+)?|\$-?\d+)')


def native_text(raw):
    """Decode strict native byte shapes; preserve individual original sequences."""
    output, spans = [], []
    at = 0
    while at < len(raw):
        value = raw[at]
        if value in (9,10) or 32 <= value <= 126:
            output.append(chr(value)); at += 1
            continue
        if 0xa1 <= value <= 0xdf:
            piece = raw[at:at+1]
            text = piece.decode('cp932', errors='strict')
            kind = 'halfwidth-kana'
        elif 0x81 <= value <= 0x9f or 0xe0 <= value <= 0xef:
            piece = raw[at:at+2]
            if len(piece) != 2:
                raise ValueError('Truncated native byte pair')
            jis = sjis_to_jis(int.from_bytes(piece,'big'))
            text = piece.decode('cp932', errors='strict')
            kind = f'jis-{jis:04x}'
        else:
            raise ValueError('Unrecognized native text byte')
        # Duplicate mappings in CP932 must not silently normalize source bytes.
        if text.encode('cp932') != piece:
            raise ValueError('Noncanonical native byte mapping')
        spans.append({'relative_offset':at,'hex':piece.hex(),'text':text,'kind':kind})
        output.append(text); at += len(piece)
    return ''.join(output), spans


def tokens(raw):
    result, unknown = [], False
    at = 0
    while at < len(raw):
        if raw[at] in (9,10):
            result.append({'relative_offset':at,'hex':raw[at:at+1].hex(),
                           'kind':'page' if raw[at] == 9 else 'line'})
        elif raw[at] == 37:
            known = KNOWN_COMMAND.match(raw,at)
            match = known or OPAQUE_COMMAND.match(raw,at)
            token = match.group() if match else b'%'
            result.append({'relative_offset':at,'hex':token.hex(),
                           'kind':'command-syntax' if known else 'opaque-percent',
                           'semantics':'not inferred'})
            unknown |= not bool(known)
            at += len(token)
            continue
        at += 1
    return result, unknown


def payload(data, at, named):
    info = instruction(data, at)
    expected = b'msgn' if named else b'msg\0'
    if data[at:at+4] != expected or info['size'] < 36:
        raise ValueError('Wrong format or short header')
    slot = data[at+32:at+info['size']]
    end = slot.find(b'\0')
    if end <= 0:
        raise ValueError('Missing/empty dialogue terminator')
    raw = slot[:end]
    source, native = native_text(raw)
    suffix = b''
    name = None
    capacity = len(slot)-1
    if named:
        start = end+1
        while start < len(slot) and slot[start] == 0:
            start += 1
        if start == len(slot):
            raise ValueError('msgn requires a bounded second string')
        name_end = slot.find(b'\0',start)
        if name_end <= start or any(slot[name_end:]):
            raise ValueError('msgn second string or final padding invalid')
        name_text, name_spans = native_text(slot[start:name_end])
        if any(c in name_text for c in '\n\t%'):
            raise ValueError('msgn name contains unproven controls')
        name = {'source':name_text,'text_offset':at+32+start,
                'original_text_hex':slot[start:name_end].hex(), 'native_spans':name_spans,
                'role':'display-label argument; not canonical character ID'}
        capacity = start-1
        suffix = slot[start:]
    elif any(slot[end:]):
        raise ValueError('msg has nonzero bytes after NUL')
    command_tokens, opaque = tokens(raw)
    item = {**info,'id':f'map.{"msgn" if named else "msg"}.{at:08x}',
            'profile':'msgn-named-v2' if named else 'msg-controls-v2',
            'text_offset':at+32,'capacity':capacity,'header_hex':data[at:at+32].hex(),
            'record_sha256':sha(data[at:at+info['size']]),'source':source,'translation':source,
            'original_text_hex':raw.hex(),'suffix_hex':suffix.hex(),
            'source_encoding':'native-sjis-shaped' if native else 'ascii',
            'native_spans':native,'control_tokens':command_tokens,
            'control_hex':[t['hex'] for t in command_tokens],
            'parameters_hex':[data[at+p:at+p+8].hex() for p in (8,16,24)],
            'editable':False, 'edit_policy':'not implemented for v2 profiles',
            'display_label':name}
    return item, opaque


def parse_msg(data, at):
    return payload(data,at,False)


def parse_msgn(data, at):
    return payload(data,at,True)


def classify(data, at):
    parser = parse_msgn if data[at:at+4] == b'msgn' else parse_msg
    item, opaque = parser(data,at)
    try:
        item['neighbors'] = neighbors(data,at)
    except ValueError as error:
        item['context_error'] = str(error)
    flags = []
    if opaque: flags.append('Opaque control syntax; original bytes retained')
    if item['native_spans']: flags.append('Native byte mapping decoded; per-font coverage/runtime not validated')
    if 'context_error' in item: flags.append('Full instruction context not proven')
    if flags:
        item['reason'] = '; '.join(flags)
        return 'identified', item
    return 'validated', item


def reconstruct(item):
    raw = bytes.fromhex(item['original_text_hex'])
    if native_text(raw)[0] != item['source']:
        raise ValueError('Decoded text does not match source bytes')
    count = item['capacity']+1-len(raw)
    if count < 1:
        raise ValueError('No terminator space')
    return bytes.fromhex(item['header_hex'])+raw+bytes(count)+bytes.fromhex(item.get('suffix_hex',''))
