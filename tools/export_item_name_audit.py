"""Complete local item-name audit: original/applied/pending, no edits/import.

Original names and descriptions stay in work/. Public summary is metadata only.
The main catalogue is exhaustive for the known 1349-row table, not a claim
that every possible name resource in the game has been found.
"""
import argparse,collections,json
from pathlib import Path
from reinsertion import ROOT,local
from dialogue import sha
from interface_text import SOURCE
from item_names import catalog,compile_names,validate_review,protected,RESOURCE,STRIDE,ITEM_COUNT
from item_descriptions import catalog as description_catalog,original
from discover_remaining_catalogue import engine_variants
from gfi import encode,CHAR_TO_BYTES

POLICY='complete-item-name-human-audit-read-only-v001'
STATUS={'translated':'Traduzidos e aplicados','pending':'Pendentes — propostas não aplicadas',
    'preserved':'Nomes mantidos no original','empty':'Registros vazios'}


def budget(text):
    missing=sorted({c for c in text if c not in CHAR_TO_BYTES and not 0x20<=ord(c)<=0x7e})
    if missing:return {'bytes':None,'missing_glyphs':missing,'within_16':False}
    size=len(encode(text))
    return {'bytes':size,'missing_glyphs':[],'within_16':size<=16}


def catalogue(elf,raw,recipe):
    patches,compiled=compile_names(elf,recipe['item_names'])
    source_rows=catalog(raw);validate_review(recipe['item_name_review'],recipe['item_names'],source_rows)
    applied={r['id']:r for r in recipe['item_names']['entries']}
    pending={r['id']:r for r in recipe['item_name_review']['pending']}
    preserved={r['id']:r for r in recipe['item_name_review'].get('preserved',[])}
    fields={r['id']:bytearray(raw[r['offset']:r['offset']+24]) for r in source_rows}
    byid={r['id']:r for r in source_rows}
    for patch in patches:
        row=byid[patch['id']]
        if patch['resource']!=RESOURCE or patch['offset']!=row['offset'] or len(patch['before'])>24:
            raise ValueError('Item name patch escapes its name field')
        if fields[row['id']][:len(patch['before'])]!=patch['before']:raise ValueError('Item name patch source differs')
        fields[row['id']][:len(patch['after'])]=patch['after']
    descriptions={}
    translated_descriptions={r['id']:r['translation'] for r in recipe['item_descriptions']['entries']}
    for desc in description_catalog(raw):
        value=bytes.fromhex(desc['source_hex'])
        text=translated_descriptions.get(desc['id'])
        if text is None:text=value.decode('ascii') if not desc['native'] else '[bytes nativos não interpretados]'
        for item in desc['items']:descriptions[item['id']]={'id':desc['id'],'current_text':text.replace('|','\n')}
    result=[]
    for row in source_rows:
        key=row['id'];source=bytes.fromhex(row['source_hex'])
        if row['native']:raise ValueError('A native name needs explicit display policy before this export')
        name=source.decode('ascii');target=applied.get(key,{}).get('translation')
        current=target if target is not None else name
        if fields[key].split(b'\0',1)[0]!=encode(current):raise ValueError('Audit applied name readback differs')
        status='empty' if row['empty'] else 'translated' if key in applied else 'pending' if key in pending else 'preserved'
        decision=preserved.get(key,{}).get('reason')
        if status=='preserved' and decision is None:
            decision='Categoria protegida pela política atual; não é autorização automática para traduzir.' if protected(row['index']) else 'Nome sem tradução aplicada; precisa de revisão contextual.'
        proposal=pending.get(key,{}).get('proposed')
        result.append({'id':key,'index':row['index'],'offset':row['offset'],
            'source_sha256':row['source_sha256'],'record_sha256':row['record_sha256'],
            'original':name,'applied_translation':target,'current_name':current,
            'current_bytes':len(encode(current)),'current_name_field_hex':bytes(fields[key]).hex(),
            'status':status,'preservation_reason':decision,
            'existing_proposal':proposal,'proposal_budget':budget(proposal) if proposal is not None else None,
            'deferred_reason':pending.get(key,{}).get('reason'),
            'description':descriptions.get(row['index']),
            'byte_ceiling':16,'physical_name_field_bytes':24,
            'protected_category':protected(row['index']),
            'review_translation':None,'review_decision':None})
    if len(result)!=ITEM_COUNT or len({r['id'] for r in result})!=ITEM_COUNT:
        raise ValueError('Audit lost or duplicated item IDs')
    if sum(r['status']=='translated' for r in result)!=compiled['accepted']:
        raise ValueError('Applied name count differs from compiler')
    meta,variants=engine_variants(raw)
    for row in variants:
        row['original']=bytes.fromhex(row.pop('source_hex')).decode('ascii')
        row['current_name']=row['original'];row['applied_translation']=None
        row['current_bytes']=len(row['original'].encode('ascii'))
        row['review_translation']=None;row['review_decision']=None
    return result,fields,meta,variants


def verify_iso_fields(image,rows,variants):
    from verify_test_iso import verify_image
    from disc import entries,SECTOR
    evidence=verify_image(image)
    with image.open('rb') as f:
        matches=[r for r in entries(f) if r['path']==RESOURCE]
        if len(matches)!=1:raise ValueError('Item ISO resource extent not unique')
        base=matches[0]['lba']*SECTOR;size=matches[0]['size']
        for row in rows:
            if not 0<=row['offset']<=size-24:raise ValueError('Audit name outside ISO resource')
            f.seek(base+row['offset'])
            if f.read(24)!=bytes.fromhex(row['current_name_field_hex']):raise ValueError('Audit name differs from playable ISO')
        for row in variants:
            f.seek(base+row['offset']);value=f.read(24).split(b'\0',1)[0]
            if sha(value)!=row['source_sha256']:raise ValueError('Engine variant differs from playable ISO')
    return {**evidence,'main_name_fields_compared':len(rows),'engine_variant_fields_compared':len(variants)}


def cell(value):
    if value is None:return '—'
    return str(value).replace('\\','\\\\').replace('|','\\|').replace('\r',' ').replace('\n',' / ')


def markdown(rows,variants,summary):
    parts=['# Auditoria completa dos nomes de itens e habilidades','',
        'Base: '+summary['recipe']+'. Conferência contra os nomes efetivos da ISO concluída.',
        'Esta é uma lista para revisão; nenhum nome foi alterado por esta exportação.','',
        'A tabela principal tem 1.349 IDs: '+str(summary['nonempty_names'])+' preenchidos e '+str(summary['counts']['empty'])+' vazios. Não há deduplicação: nomes iguais de IDs diferentes aparecem separadamente.',
        'O catálogo também contém habilidades e marcadores técnicos. A presença de uma linha não prova que seja um item obtível ou exibido em jogo.','',
        'Limite atual: **16 bytes por nome**. Letras ASCII, números, espaços e pontuação ASCII ocupam 1 byte; cada acento/cedilha mapeado ocupa 2. O terminador é reservado pelo compilador. O campo físico de 24 bytes não autoriza 23 bytes de texto.',
        'Acentos disponíveis: ç á à ã â é ê í ó ô õ ú ü Ç Á É Ã Õ. Ó maiúsculo ainda não está mapeado. Bytes não substituem o teste visual de largura.',
        'Nomes próprios e termos protegidos continuam preservados até revisão explícita. Não remover acentos ou artigos apenas para caber.','',
        'Para responder no chat: `ID → nome proposto`. O JSON ao lado inclui contexto de descrições, motivos e campos review_translation/review_decision, sem importação automática.','']
    for status in ('translated','pending','preserved','empty'):
        group=[r for r in rows if r['status']==status]
        parts+=['## '+STATUS[status]+' ('+str(len(group))+')','']
        if status=='pending':
            parts+=['| ID | Original | Proposta anterior — não aplicada | Bytes — máximo 16 | Motivo registrado |','| --- | --- | --- | ---: | --- |']
            for r in group:
                b=r['proposal_budget'];size=b['bytes'] if not b['missing_glyphs'] else 'Glifo ausente: '+', '.join(b['missing_glyphs'])
                parts.append('| '+' | '.join(cell(v) for v in (r['index'],r['original'],r['existing_proposal'],size,r['deferred_reason']))+' |')
        elif status=='translated':
            parts+=['| ID | Original | Tradução aplicada | Bytes — máximo 16 |','| --- | --- | --- | ---: |']
            for r in group:parts.append('| '+' | '.join(cell(v) for v in (r['index'],r['original'],r['applied_translation'],r['current_bytes']))+' |')
        elif status=='preserved':
            parts+=['O nome inglês continua no jogo. Esses registros não são todos traduções obrigatórias pendentes.','',
                '| ID | Original | Tradução aplicada | Bytes do original | Motivo |','| --- | --- | --- | ---: | --- |']
            for r in group:parts.append('| '+' | '.join(cell(v) for v in (r['index'],r['original'],None,r['current_bytes'],r['preservation_reason']))+' |')
        else:
            parts+=['Incluídos somente para conferir todos os IDs; não inventar nomes para estes campos.','',
                '| ID | Original | Tradução aplicada | Bytes |','| --- | --- | --- | ---: |']
            for r in group:parts.append('| '+str(r['index'])+' | *(vazio)* | — | 0 |')
        parts.append('')
    parts+=['## Apêndice — variantes de nomes de motores','',
        'São campos adicionais fora da tabela principal, vinculados a dez registros de motores. Não contam como 50 novos itens. Há '+str(sum(not r['empty'] for r in variants))+' nomes preenchidos; os demais campos estão vazios. Permanecem no original pela regra de preservação dos motores.','',
        '| ID do motor / variante | Original | Tradução aplicada | Bytes do original |','| --- | --- | --- | ---: |']
    for r in variants:parts.append('| '+' | '.join(cell(v) for v in (str(r['item_id'])+' / '+r['id'].rsplit('.',1)[-1],r['original'] or '(vazio)',None,r['current_bytes']))+' |')
    return '\n'.join(parts)+'\n'


def run(recipe_path,output,summary_path=None):
    recipe_path=Path(recipe_path).resolve();output=local(output,True)
    if not recipe_path.is_relative_to(ROOT/'translations'):raise ValueError('Recipe must be in translations/')
    recipe_bytes=recipe_path.read_bytes();recipe=json.loads(recipe_bytes)
    if summary_path is not None:
        summary_path=Path(summary_path).resolve()
        if not summary_path.is_relative_to(ROOT/'reports') or summary_path.exists():raise ValueError('Use new reports path')
    raw=original(RESOURCE);elf=SOURCE.read_bytes()
    rows,fields,engine_meta,variants=catalogue(elf,raw,recipe)
    name=recipe['iso_name']
    if Path(name).name!=name or not name.startswith('MetalSaga-ptbr-') or not name.endswith('.iso'):
        raise ValueError('Audit ISO name is not a generated project image name')
    image=ROOT/'work'/Path(name).stem.removeprefix('MetalSaga-ptbr-')/name
    build=json.loads((image.parent/'relatorio.json').read_text(encoding='utf-8'))
    if (build.get('interface',{}).get('recipe')!=recipe_path.relative_to(ROOT).as_posix()
        or build['interface'].get('recipe_sha256')!=sha(recipe_bytes)):
        raise ValueError('Audit recipe does not match completed playable build')
    iso=verify_iso_fields(image,rows,variants)
    counts=dict(collections.Counter(r['status'] for r in rows))
    summary={'schema':1,'policy':POLICY,'recipe':recipe_path.relative_to(ROOT).as_posix(),
        'recipe_sha256':sha(recipe_bytes),'source_sha256':sha(raw),'source_elf_sha256':sha(elf),
        'main_records':len(rows),'nonempty_names':sum(bool(r['original']) for r in rows),
        'counts':counts,'engine_variant_fields':len(variants),'nonempty_engine_variant_fields':sum(not r['empty'] for r in variants),
        'playable_iso':iso,'output':output.relative_to(ROOT).as_posix(),
        'all_main_ids_present_once':True,'originals_modified':False,'iso_modified':False,'translation_applied':False,
        'limits':'Known main table and known engine-variant fields; not proof of all possible item resources or live contexts.'}
    document={**summary,'rows':rows,'engine_variant_metadata':engine_meta,'engine_variants':variants}
    text=markdown(rows,variants,summary)
    if recipe_path.read_bytes()!=recipe_bytes or sha(original(RESOURCE))!=summary['source_sha256']:
        raise ValueError('Recipe or source changed during audit')
    output.mkdir(parents=True)
    for name,value in (('auditoria-completa.md',text),('revisao-editavel.json',json.dumps(document,ensure_ascii=False,indent=2)+'\n')):
        with (output/name).open('x',encoding='utf-8') as f:f.write(value)
    if summary_path is not None:
        with summary_path.open('x',encoding='utf-8') as f:json.dump(summary,f,ensure_ascii=False,indent=2);f.write('\n')
    return summary


if __name__=='__main__':
    p=argparse.ArgumentParser(description='Exportar TODOS os nomes conhecidos para auditoria humana, sem alterar traduções/ISO')
    p.add_argument('--recipe',type=Path,default=ROOT/'translations/interface-v040.json')
    p.add_argument('--output',type=Path,required=True);p.add_argument('--summary',type=Path)
    a=p.parse_args();print(json.dumps(run(a.recipe,a.output,a.summary),ensure_ascii=False,indent=2))
