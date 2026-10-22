"""Opt-in decimal variable 15; inherits the validated integer handler bindings."""
from control_numeric1 import tokenize as numeric1_tokens, verify as verify_numeric1

TOKEN=b'%$15'


def verify(data):
    inherited=verify_numeric1(data)
    return {**inherited,'allowed_token_hex':TOKEN.hex(),'variable_index':15,
            'grammar':'$15 reads uint32 at context+60; existing handler formats signed decimal'}


def tokenize(raw):
    parts,_=numeric1_tokens(raw);out=[]
    for part in parts:
        end=part['relative_offset']+len(bytes.fromhex(part['hex']))
        if (part['kind']=='opaque-percent' and bytes.fromhex(part['hex'])==TOKEN
                and raw[end:end+1]!=b'f'):
            part={**part,'kind':'preserved-numeric15-reference',
                  'semantics':'variable 15 -> signed decimal; immutable bytes'}
        out.append(part)
    return out,any(t['kind']=='opaque-percent' for t in out)
