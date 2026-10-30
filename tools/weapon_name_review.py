"""Complete local weapon review, never a translation applier or ISO writer."""
import argparse
import json
import re
import struct
from pathlib import Path
from dialogue import ROOT,sha
from item_names import original,RESOURCE,catalog,compile_names
from interface_text import SOURCE
from gfi import encode,decode

SUGGESTIONS='translations/sugestoes-armas-v001.json'
CURRENT='translations/interface-v055.json'
GROUPS={1:'Portáteis / personagens e cães',10:'Tanques — MAIN',11:'Tanques — SUB',12:'Tanques — SE',15:'Munição especial (anexo)'}
EXPECTED={1:100,10:30,11:21,12:24,15:15}


def collect(raw,recipe,proposals):
    if proposals.get('policy')!='weapon-suggestions-review-only-v001' or proposals.get('approved_for_application') is not False:
        raise ValueError('Not an unapproved weapon review')
    if sha(raw)!=proposals.get('source_sha256'):raise ValueError('Weapon source differs')
    selected=[]
    for row in catalog(raw):
        kind=struct.unpack_from('<I',raw,row['offset']+28)[0]
        if kind in GROUPS and not row['empty']:
            if row['native']:raise ValueError('Native weapon name requires separate investigation')
            selected.append((kind,row))
    counts={k:sum(kind==k for kind,_ in selected) for k in GROUPS}
    if counts!=EXPECTED:raise ValueError('Weapon category coverage differs')
    rows={r['id']:r for _,r in selected}
    decisions={r['id']:r for r in proposals['entries']}
    if len(decisions)!=len(proposals['entries']) or set(decisions)!=set(rows):
        raise ValueError('Missing/duplicate/foreign weapon review ID')
    patches,_=compile_names(SOURCE.read_bytes(),recipe['item_names'])
    from spack_battle import catalog as battle_catalog
    battle_rows=[r for r in battle_catalog(raw) if r['kind']=='action']
    patched={r['id']:r for r in patches};result=[]
    for kind,row in selected:
        decision=decisions[row['id']]
        if set(decision)!={'id','source_sha256','preserve_original','suggestion','reason'}:
            raise ValueError('Unexpected weapon decision metadata')
        if decision['source_sha256']!=row['source_sha256'] or not decision['reason']:
            raise ValueError('Weapon source/context binding differs')
        before=bytes.fromhex(row['source_hex']);source=before.decode('ascii')
        current=decode(patched[row['id']]['after'].split(b'\0')[0]) if row['id'] in patched else source
        if type(decision['preserve_original']) is not bool:raise ValueError('Invalid preservation flag')
        if decision['preserve_original']:
            if decision['suggestion'] is not None:raise ValueError('Preserved name has translation')
            suggestion=source
        else:
            suggestion=decision['suggestion'];value=encode(suggestion)
            if not value or decode(value)!=suggestion or any(c in value for c in (0,9,10,13,37,124)):
                raise ValueError('Invalid review encoding/control')
            if re.findall(r'\d+',source)!=re.findall(r'\d+',suggestion):raise ValueError('Weapon model/caliber numbers changed')
        target=encode(suggestion)
        result.append({'id':row['id'],'index':row['index'],'category':kind,'group':GROUPS[kind],
                       'offset':row['offset'],'source_sha256':row['source_sha256'],
                       'record_sha256':row['record_sha256'],'source':source,'current':current,
                       'battle_action_ids':[r['id'] for r in battle_rows if r['source_hex']==row['source_hex']],
                       'suggestion':suggestion,'reason':decision['reason'],
                       'suggested_game_bytes':len(target),'within_legacy_16_byte_guard':len(target)<=16,
                       'physical_name_capacity_bytes':23,'approval':None,
                       'application_authorized':False})
    # Duplicate names are separate records, but must have a consistent proposal.
    aliases={}
    for row in result:aliases.setdefault(row['source'],set()).add(row['suggestion'])
    if any(len(values)>1 for values in aliases.values()):raise ValueError('Inconsistent repeated weapon proposal')
    return result


def write_review_files(output,files):
    """Never overwrite the user's edited decisions on a repeated extraction."""
    for name,text in files.items():
        path=output/name
        if path.exists() and path.read_text(encoding='utf-8')!=text:
            raise ValueError('Revisão existente diferente: '+name+'. Preserve sua revisão e use outro --output.')
    for name,text in files.items():
        path=output/name
        if not path.exists():path.write_bytes(text.encode('utf-8'))


def export(output):
    output=output.resolve()
    if not output.is_relative_to(ROOT/'work'):raise ValueError('Review exports belong under work/')
    output.mkdir(parents=True,exist_ok=True)
    raw=original(RESOURCE);recipe_raw=(ROOT/CURRENT).read_bytes()
    proposals=json.loads((ROOT/SUGGESTIONS).read_bytes())
    rows=collect(raw,json.loads(recipe_raw),proposals)
    summary={'weapons':sum(r['category']!=15 for r in rows),
             'special_ammunition_appendix':sum(r['category']==15 for r in rows),
             'weapon_names_already_changed':sum(r['category']!=15 and r['source']!=r['current'] for r in rows),
             'weapon_suggestions_changed':sum(r['category']!=15 and r['source']!=r['suggestion'] for r in rows),
             'weapon_suggestions_over_16_bytes':sum(r['category']!=15 and not r['within_legacy_16_byte_guard'] for r in rows)}
    report={'policy':proposals['policy'],'recipe':CURRENT,'recipe_sha256':sha(recipe_raw),
            'source_sha256':sha(raw),'summary':summary,'rows':rows,
            'limits':'16 bytes is the historical global guard, not permission to edit protected weapons. 23 bytes is the physical NUL field only; larger names need consumer/layout proof.',
            'game_modified':False}
    lines=['# Metal Saga — auditoria completa de armas', '',
           '175 registros de armas, com todas as ocorrências e IDs. O registro 1042 também está incluído.',
           'As sugestões desta lista NÃO foram aplicadas. Nomes/modelos únicos foram preservados conservadoramente.',
           'O nome atual já considera a receita consolidada. MAIN, SUB e SE permanecem inalterados.', '',
           '**Como revisar:** preencha a última coluna com “aprovar”, “manter original” ou o nome que preferir.',
           '**Limites:** bytes indicam a codificação do jogo; acentos normalmente custam dois bytes. O teto genérico histórico é 16 bytes. “Investigar” indica que a sugestão o supera; não reduzi a fonte ou cortei palavras para fazê-la caber. O campo físico de 23 bytes não libera automaticamente nomes maiores. Mesmo propostas curtas de armas protegidas dependem da aprovação e de uma política técnica própria.', '',
           'O anexo contém as 15 munições especiais, com as traduções já aprovadas, para facilitar a comparação. Elas não entram na contagem das 175 armas.', '']
    for kind,group in GROUPS.items():
        lines.extend([f'## {group}', '', '| ID | Original | Atual | Sugestão | Bytes | Limite | Sua decisão |', '|---|---|---|---|---:|---|---|'])
        for row in rows:
            if row['category']!=kind:continue
            state='16 bytes' if row['within_legacy_16_byte_guard'] else 'Investigar'
            suggestion=row['suggestion']+(' (manter)' if row['suggestion']==row['source'] else '')
            lines.append(f"| {row['index']:04d} | {row['source']} | {row['current']} | {suggestion} | {row['suggested_game_bytes']} | {state} | |")
        lines.append('')
    write_review_files(output,{'armas-revisao.json':json.dumps(report,ensure_ascii=False,indent=2)+'\n',
                              'ARMAS-PARA-REVISAR.md':'\n'.join(lines)+'\n'})
    # Public report is metadata only; the bilingual catalogue stays local.
    public={k:v for k,v in report.items() if k!='rows'}
    public['ids']=[r['id'] for r in rows]
    (ROOT/'reports/revisao-armas-v001.json').write_text(json.dumps(public,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    return report


def main():
    p=argparse.ArgumentParser(description='Gerar revisão completa de armas, sem aplicar traduções')
    p.add_argument('--output',type=Path,default=ROOT/'work/revisao-armas-v001')
    args=p.parse_args();report=export(args.output);print(json.dumps(report['summary'],ensure_ascii=False))


if __name__=='__main__':main()
