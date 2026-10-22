"""Narrow opt-in for the original signed decimal variable 1 formatter."""
import hashlib
import struct
from control_b15 import tokenize as b15_tokens, verify as verify_b15

TOKEN=b'%$1'
HANDLER=(0x1b5dec,0x1b5e84)
HANDLER_SHA='34410c8529e2e6613013f4f1a831fd9f3c1d44312a47e588cc81aabeebc038e9'


def verify(data):
    inherited=verify_b15(data)
    if hashlib.sha256(data[HANDLER[0]:HANDLER[1]]).hexdigest()!=HANDLER_SHA:
        raise ValueError('Numeric formatter handler mismatch')
    if struct.unpack_from('<I',data,0x33dd60)[0]!=0x2b4dec:
        raise ValueError('Numeric dispatch mismatch')
    if data[0x349dc0:0x349dc3]!=b'%d\0':raise ValueError('Decimal format mismatch')
    return {'elf_sha256':inherited['elf_sha256'],'argument_reader':inherited['argument_reader'],
        'handler':list(HANDLER),'handler_sha256':HANDLER_SHA,'dispatch_table':0x33dd60,
        'format_offset':0x349dc0,'format_hex':'256400','allowed_token_hex':TOKEN.hex(),
        'variable_index':1,'format':'signed 32-bit decimal; at most 11 visible ASCII bytes',
        'excluded_suffix':'lowercase f invokes another argument and floating-point formatting',
        'growth_allowed':False,'mode':'slots','runtime_visual_status':'pending_manual_validation'}


def tokenize(raw):
    parts,_=b15_tokens(raw);out=[]
    for part in parts:
        end=part['relative_offset']+len(bytes.fromhex(part['hex']))
        if (part['kind']=='opaque-percent' and bytes.fromhex(part['hex'])==TOKEN
                and raw[end:end+1]!=b'f'):
            part={**part,'kind':'preserved-numeric1-reference',
                  'semantics':'variable 1 -> signed decimal; immutable bytes'}
        out.append(part)
    return out,any(t['kind']=='opaque-percent' for t in out)
