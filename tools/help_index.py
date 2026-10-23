"""Opt-in grammar for the 56-row NDATA help index, not arbitrary CSV."""
import argparse
import hashlib
import json
from pathlib import Path
import re
from reinsertion import local
from gfi import encode,decode
from glyph_spacing import ORIGINAL_SHA

POLICY='ndata-help-index-fixed-load-v005'
OFFSET=0x10e4800
SIZE=798
WINDOWS=((0xd35cc,0xd35f0,'ba02d0936241914dcd95ffc2719e738d5b9914f09df24c3a791cfa72b026209b'),
         (0xd3600,0xd37d0,'6d2d868bf93c20a84a6ed94c436518c27f0e3d2b1d9fa2d4994d25c5c5a15345'))


def sha(raw):return hashlib.sha256(raw).hexdigest()


def parse(raw):
    if b'\0' in raw:raw=raw[:raw.index(0)]
    if not raw.endswith(b'\n') or b'\r' in raw:raise ValueError('Help index LF framing mismatch')
    result=[];group=None
    for index,line in enumerate(raw[:-1].split(b'\n')):
        match=re.fullmatch(rb'(\t[0-9]{3}|[0-9]{4}),([^\x00-\x1f,]+)',line)
        if not match:raise ValueError('Help index grammar mismatch')
        prefix,text=match.groups();is_page=prefix.startswith(b'\t')
        if is_page and group is None:raise ValueError('Help topic without category')
        if not is_page:group=index
        result.append({'id':f'ndata.help-index.{index:03d}','prefix':prefix.decode('ascii'),
                       'kind':'page' if is_page else 'category','reference':int(prefix),
                       'category_row':group,'text':decode(text),'source_sha256':sha(text)})
    return result


def catalog(elf,raw):
    if sha(elf)!=ORIGINAL_SHA:raise ValueError('Help index ELF mismatch')
    for a,z,h in WINDOWS:
        if sha(elf[a:z])!=h:raise ValueError('Help index instruction binding mismatch')
    payload=raw[OFFSET:OFFSET+SIZE];rows=parse(payload)
    if len(rows)!=56 or sum(r['kind']=='category' for r in rows)!=12:
        raise ValueError('Help index row topology mismatch')
    from help_text import catalog as pages,TABLE
    known=pages(elf,raw)
    descriptors={(e['descriptor_offset']-TABLE)//8 for e in known}
    references=[r['reference'] for r in rows if r['kind']=='page']
    if len(set(references))!=44 or set(references)!=descriptors:raise ValueError('Help topic/page linkage mismatch')
    return {'policy':POLICY,'source_sha256':sha(payload),'offset':OFFSET,'loaded_bytes':SIZE,'rows':rows}


def compile_index(elf,config):
    from interface_resources import original,NDATA
    from weapon_terms import validate
    raw=original(NDATA);source=catalog(elf,raw)
    if config.get('policy')!=POLICY or config.get('source_sha256')!=source['source_sha256']:
        raise ValueError('Help index recipe binding mismatch')
    if len(config['rows'])!=len(source['rows']):raise ValueError('Help index row count changed')
    output=[];results=[]
    for before,target in zip(source['rows'],config['rows']):
        if target['id']!=before['id'] or target['source_sha256']!=before['source_sha256']:
            raise ValueError('Help index identity/order mismatch')
        text=target['translation'];payload=encode(text)
        if not payload.strip() or payload!=payload.strip() or any(c in payload for c in (0,9,10,13,44,37,60,62,124)):
            raise ValueError('Help index injected delimiter or empty label')
        issues=validate(before['text'],text)
        from translation_policy import validate as terminology
        issues+=terminology(before['text'],text)
        if issues:raise ValueError('Help index terminology: '+'; '.join(issues))
        output.append(before['prefix'].encode('ascii')+b','+payload+b'\n')
        if text!=before['text']:results.append({'id':target['id'],'resource':NDATA,'kind':before['kind'],
            'reference':before['reference'],'category_row':before['category_row'],'source_bytes':len(encode(before['text'])),
            'target_bytes':len(payload)})
    after=b''.join(output)
    if len(after)>SIZE:raise ValueError('Help index loaded window overflow')
    reread=parse(after)
    for old,new in zip(source['rows'],reread):
        for key in ('id','prefix','kind','reference','category_row'):
            if old[key]!=new[key]:raise ValueError('Help index topology changed')
    return [{'resource':NDATA,'id':'ndata.help-index','offset':OFFSET,'before':raw[OFFSET:OFFSET+SIZE],
             'after':after+bytes(SIZE-len(after))}],results


def main():
    p=argparse.ArgumentParser(description='Exportar índice comprovado da ajuda do Satcom, sem APIs')
    p.add_argument('--output',required=True,type=Path);a=p.parse_args();output=local(a.output,True)
    from interface_text import SOURCE
    from interface_resources import original,NDATA
    result=catalog(SOURCE.read_bytes(),original(NDATA));output.parent.mkdir(parents=True,exist_ok=True)
    with output.open('x',encoding='utf-8') as f:json.dump(result,f,ensure_ascii=False,indent=2);f.write('\n')
    print('56 rótulos exportados: 12 categorias e 44 tópicos vinculados às páginas')


if __name__=='__main__':main()
