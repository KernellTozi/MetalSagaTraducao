"""Six source-bound records; two native symbols retained, no general CP932 input."""
from pathlib import Path
from gfi import encode as project_encode,decode as project_decode,BYTES_TO_CHAR,Gfi,sjis_to_jis
from dialogue import sha,ROOT

RECORDS={
 'map.msg.07b264e0':'05ac6d2c037111c1540478154e31ba6ac038656b71d19733f858c7d226934810',
 'map.msg.128226b4':'f02f8e7baf03e9c5bd93b864e32ccb35a008716ef6cb4000ff19c782b298387a',
 'map.msg.128226fc':'cd1c22b333f6197eccb7ce1321ad2821d7e9b37604516259b7244988230730ac',
 'map.msg.12822744':'0ce4f5e378673eb252318cc2d68ae449069c508f02f2b6272c810edc46666ec7',
 'map.msg.12822790':'0ecf74021d08dfe220857a22967c4bfe0a52a31c76f76bb7d9bb35d3a47a6338',
 'map.msg.13709cc0':'d2d87533c548e6e01c6dd37bfc085fbc566c2c5548f6131ba19a5daacfb7b981'}
SYMBOLS={'☆':b'\x81\x99','。':b'\x81\x42'}


def allowed(key,digest):return key in RECORDS and RECORDS[key]==digest


def encode(text,key):
    if key not in RECORDS:return project_encode(text)
    permitted={'☆'} if key=='map.msg.07b264e0' else {'。'} if key=='map.msg.13709cc0' else set()
    out=bytearray()
    for c in text:out.extend(SYMBOLS[c] if c in permitted else project_encode(c))
    if key=='map.msg.07b264e0' and (not text.endswith('☆') or text.count('☆')!=1):raise ValueError('Native star suffix must remain')
    if key=='map.msg.13709cc0' and (not text.startswith('。\n') or text.count('。')!=1):raise ValueError('Native punctuation prefix must remain')
    return bytes(out)


def decode(raw):
    raw=bytes(raw);out=[];i=0
    while i<len(raw):
        pair=raw[i:i+2]
        if pair in BYTES_TO_CHAR:out.append(BYTES_TO_CHAR[pair]);i+=2
        elif raw[i] in (9,10) or 32<=raw[i]<=126:out.append(chr(raw[i]));i+=1
        else:
            size=1 if 0xa1<=raw[i]<=0xdf else 2
            out.append(raw[i:i+size].decode('cp932',errors='strict'));i+=size
    return ''.join(out)


def width_units(raw,tokenizer):
    parts,_=tokenizer(raw);visible=bytearray();cursor=0
    for p in parts:
        at=p['relative_offset'];visible.extend(raw[cursor:at]);visible.extend(bytes.fromhex(p.get('literal_tail_hex','')))
        if p['kind'] in ('line','page'):visible.extend(b'\n')
        cursor=at+len(bytes.fromhex(p['hex']))
    visible.extend(raw[cursor:])
    return [sum(2 if ord(c)>126 else 1 for c in line) for line in decode(visible).split('\n')]


def verify_fonts():
    from interface_resources import original
    from dialogue_formats import native_text
    import struct
    pairs=set(SYMBOLS.values());sources=[]
    with (ROOT/'JOGO/Metal Saga/DATA/MAP/MAP.MCT').open('rb') as stream:
        for key,expected in RECORDS.items():
            at=int(key.split('.')[-1],16);stream.seek(at);header=stream.read(8)
            size=struct.unpack_from('<H',header,6)[0];stream.seek(at);record=stream.read(size)
            if sha(record)!=expected:raise ValueError('Reviewed native source changed')
            body=record[32:].split(b'\0',1)[0];_,spans=native_text(body)
            pairs.update(bytes.fromhex(p['hex']) for p in spans)
            sources.append({'id':key,'record_sha256':expected,'body_sha256':sha(body),'native_sequences':len(spans)})
    rows=[]
    for name in ('SUC20I22.GFI','SUC24I26.GFI'):
        raw=original('DATA/SYS/'+name);font=Gfi(raw)
        for pair in sorted(pairs):
            jis=sjis_to_jis(int.from_bytes(pair,'big'));offset=font.glyph_offset(jis)
            if jis>>8==0x23 or (pair!=b'\x81\x40' and not any(font.pixels(offset))):raise ValueError('Native glyph missing or collides with PT-BR bank')
            rows.append({'font':name,'bytes_hex':pair.hex(),'jis':jis,'glyph_offset':offset,'glyph_sha256':sha(raw[offset:offset+font.stride])})
    return {'reviewed_record_hashes':RECORDS,'source_records':sources,'native_glyphs':rows,'new_japanese_input_allowed':False,
        'scope':'Original font glyphs and source-bound replacements; native input remains blocked elsewhere; no PS2 execution'}
