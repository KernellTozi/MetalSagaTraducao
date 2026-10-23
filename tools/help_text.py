"""Exact NDATA help pages; preserve markup, loaded windows and original whitespace."""
import argparse
import hashlib
import json
import re
import struct
from pathlib import Path
from reinsertion import ROOT,local
from glyph_spacing import ORIGINAL_SHA
from gfi import encode,decode

POLICY='ndata-html-help-fixed-load-v004'
INDEXES=(127,129,*range(131,173))
TABLE=0x322368
WINDOWS=((0xd4160,0xd424c,'8b6da68e8b1e6abfe2901e99078ea926f14fd2a2dc6474f74d0242be796083b7'),
         (0xd4fb8,0xd54a0,'fb27631924e1f6cc5bd284974be25b150f68e271741b155fe98b9d085708d178'),
         (0xd4f38,0xd4f80,'f1b388dd974fbf1f715ef497ccd79a58c0d2ad94ac4e1b2743556bdced0458f4'))
TAGS=re.compile(rb'(<[^>]+>)')


def sha(raw):return hashlib.sha256(raw).hexdigest()


def catalog(elf,raw):
    if sha(elf)!=ORIGINAL_SHA:raise ValueError('Help ELF revision mismatch')
    for a,z,h in WINDOWS:
        if sha(elf[a:z])!=h:raise ValueError('Help consumer/parser window mismatch')
    n=struct.unpack_from('<I',raw,8)[0];offsets=struct.unpack_from('<'+str(n)+'I',raw,12);result=[]
    for index in INDEXES:
        at=offsets[index];slot_end=offsets[index+1];payload=raw[at:slot_end].rstrip(b'\0')
        descriptors=[i for i in range(64) if struct.unpack_from('<II',elf,TABLE+i*8)==(at,len(payload))]
        if len(descriptors)!=1 or not payload.startswith(b'<HTML>') or not payload.rstrip().endswith(b'</HTML>'):
            raise ValueError('Help descriptor/HTML boundary mismatch')
        if any(c not in (10,13) and not 32<=c<127 for c in payload):raise ValueError('Native help bytes blocked')
        result.append({'id':f'ndata.help.{index:03d}','index':index,'offset':at,'loaded_bytes':len(payload),
            'descriptor_offset':TABLE+descriptors[0]*8,'source_sha256':sha(payload),'source':payload.decode('ascii')})
    return result


def restore_whitespace(before,text):
    after=encode(text)
    if any(c in after for c in (0,9)):raise ValueError('Unsupported help delimiter')
    source=TAGS.split(before);target=TAGS.split(after)
    if source[1::2]!=target[1::2]:raise ValueError('Help markup sequence changed')
    if target[0].strip() or target[-1].strip():raise ValueError('Text outside HTML page')
    output=[]
    for old,new in zip(source[::2],target[::2]):
        value=new.strip()
        if b'\r' in new or b'\n' in new:raise ValueError('Injected help newline')
        if b'<' in value or b'>' in value or b'\r' in value or b'\n' in value:raise ValueError('Injected help markup/newline')
        if not old.strip():
            # Ordinary characters before/between tags follow the same reader
            # path. Preserve source CR/LF while permitting translated articles.
            output.append(old+new);continue
        prefix=re.match(rb'\s*',old).group();suffix=re.search(rb'\s*$',old).group()
        output.append(prefix+value+suffix)
    payload=b''.join(part for pair in zip(output,source[1::2]+[b'']) for part in pair)
    # Literal percentages and gameplay quantities are immutable.
    old_plain=TAGS.sub(b' ',before);new_plain=TAGS.sub(b' ',payload)
    if re.findall(rb'\d+(?:\.\d+)?',old_plain)!=re.findall(rb'\d+(?:\.\d+)?',new_plain):raise ValueError('Help gameplay numbers changed')
    if re.findall(rb'%%',before)!=re.findall(rb'%%',payload) or b'%' in re.sub(rb'%%',b'',payload):raise ValueError('Help percent controls changed')
    from translation_policy import validate,POLICY_PATH
    policy=json.loads(POLICY_PATH.read_text(encoding='utf-8'));policy['case_sensitive_names']=policy['protected_names']
    source_text=re.sub(r'\s+',' ',old_plain.decode('ascii'));target_text=re.sub(r'\s+',' ',decode(new_plain.replace(b'\r',b'')))
    issues=validate(source_text,target_text,policy)
    from weapon_terms import validate as validate_weapon
    issues+=validate_weapon(source_text,target_text)
    if issues:raise ValueError('Help terminology: '+'; '.join(issues))
    return payload


def compile_help(elf,items):
    from interface_resources import original,NDATA
    raw=original(NDATA);known={e['id']:e for e in catalog(elf,raw)};patches=[];results=[];seen=set()
    for target in items:
        key=target['id']
        if key in seen:raise ValueError('Duplicate help ID')
        seen.add(key);old=known[key];at=old['offset'];size=old['loaded_bytes'];before=raw[at:at+size]
        if target['source_sha256']!=old['source_sha256']:raise ValueError('Help source binding mismatch')
        after=restore_whitespace(before,target['translation'])
        if len(after)>size:raise ValueError(f'Help loaded window overflow: {key}: {len(after)} > {size}')
        if after==before:raise ValueError('Unchanged help page must be omitted')
        patches.append({'resource':NDATA,'id':key,'offset':at,'before':before,'after':after+bytes(size-len(after))})
        results.append({'id':key,'resource':NDATA,'offset':at,'descriptor_offset':old['descriptor_offset'],
            'source_bytes':size,'target_bytes':len(after),'markup_tokens':len(TAGS.findall(before))})
    return patches,results


def main():
    parser=argparse.ArgumentParser(description='Exportar 44 páginas de ajuda comprovadas, sem APIs')
    parser.add_argument('--output',type=Path,required=True);args=parser.parse_args()
    from interface_resources import original,NDATA
    from interface_text import SOURCE
    output=local(args.output,True);rows=catalog(SOURCE.read_bytes(),original(NDATA));output.parent.mkdir(parents=True,exist_ok=True)
    with output.open('x',encoding='utf-8') as stream:json.dump({'policy':POLICY,'pages':rows},stream,ensure_ascii=False,indent=2);stream.write('\n')
    print(f'{len(rows)} páginas exportadas; originais preservados')


if __name__=='__main__':main()
