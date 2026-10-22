"""v004 batch compiler: immutable source bindings, fixed records, explicit policies."""
from pathlib import Path
import json
import mmap
import struct

from dialogue import ROOT, sha
from dialogue_formats import parse_msg, parse_msgn, tokens
from dialogue_advanced import SsdIndex, LAYOUTS, parse as parse_advanced
from gfi import encode, decode, CHAR_TO_BYTES, BYTES_TO_CHAR

RESOURCE='DATA/MAP/MAP.MCT'
SOURCE=ROOT/'JOGO/Metal Saga'/RESOURCE
POLICY='fixed-record-segment-slots-or-proven-repack-v004'
NAMED_POLICY='fixed-record-named-choice-slots-v005'
B15_POLICY='fixed-record-b15-preserved-slots-v006'
NUMERIC1_POLICY='fixed-record-numeric1-preserved-slots-v007'
NUMERIC15_POLICY='fixed-record-numeric15-preserved-slots-v008'
T0_POLICY='fixed-record-t0-preserved-slots-v009'
I0_POLICY='fixed-record-i0-preserved-slots-v010'
REPACK={b'msgn',b'smsg',b'2smg'}
COPY_LIMITS={b'MC\0\0':31,b'SP\0\0':31,b'ST\0\0':31}


def local(path, new=False):
    path=Path(path).resolve()
    if not path.is_relative_to(ROOT/'work'):raise ValueError('Use caminhos em work/')
    if new and path.exists():raise ValueError(f'Saída já existe: {path}')
    return path


def descriptor(data,at,index,*,named_choices=False,b15=False,numeric1=False,numeric15=False,t0=False,i0=False):
    tokenizer=tokens
    if i0:
        from control_i0 import tokenize as tokenizer
    elif t0:
        from control_t0 import tokenize as tokenizer
    elif numeric15:
        from control_numeric15 import tokenize as tokenizer
    elif numeric1:
        from control_numeric1 import tokenize as tokenizer
    elif b15:
        from control_b15 import tokenize as tokenizer
    if at not in index.records:raise ValueError('Offset não é uma instrução SSD comprovada')
    tag=bytes(data[at:at+4]); segments=[]; blocked=[]
    if tag in (b'msg\0',b'msgn'):
        item,_=(parse_msgn if tag==b'msgn' else parse_msg)(data,at)
        header=32
        fields=[('body',item['source'],bytes.fromhex(item['original_text_hex']),at+32,item['capacity'],True)]
        if item['display_label']:
            label=item['display_label'];offset=label['text_offset']
            fields.append(('label',label['source'],bytes.fromhex(label['original_text_hex']),offset,
                           at+item['size']-offset-1,False))
    elif tag in LAYOUTS:
        _,item=parse_advanced(data,at);header=item['header_size'];fields=[]
        count=len(item['segments'])
        if count==3 and not (named_choices and tag in (b'smnn',b'2snm')):
            blocked.append('Papel da terceira string ainda não liberado para edição')
        for s in item['segments']:
            key='choices' if tag in (b'sel\0',b'2sel') or count>1 and s['number']==1 else 'label' if s['number']==2 else 'body'
            fields.append((key,s['source'],bytes.fromhex(s['original_text_hex']),s['text_offset'],
                           len(bytes.fromhex(s['original_text_hex']))+s['zero_count']-1,key!='label'))
    else:raise ValueError('Família não textual ou não suportada')
    for key,text,raw,offset,capacity,editable in fields:
        if any(c not in (9,10) and not 32<=c<=126 for c in raw):
            blocked.append('Origem com bytes nativos: preservação permitida, edição bloqueada')
        _,opaque=tokenizer(raw)
        if opaque:blocked.append('Controle opaco: edição bloqueada')
        # Selection helper appends TWO NULs in its 256-byte temporary buffer.
        limit=254 if key=='choices' else COPY_LIMITS.get(tag)
        segments.append({'key':key,'source':text,'translation':text,'source_hex':raw.hex(),
                         'offset':offset,'capacity':capacity,'editable':editable,'runtime_byte_limit':limit})
    return {'id':f'map.{tag.rstrip(bytes(1)).decode("ascii")}.{at:08x}','offset':at,
            'tag':tag.hex(),'size':item['size'],'header_hex':data[at:at+header].hex(),
            'record_sha256':sha(data[at:at+item['size']]),'block_offset':index.records[at]['block_offset'],
            'mode':'slots','repack_supported':tag in REPACK,
            'blocked_reasons':sorted(set(blocked)),'segments':segments}


def source_hash(data):
    expected=next(x['sha256'] for x in json.loads((ROOT/'reports/inventory.json').read_text(encoding='utf-8')) if x['path']==RESOURCE)
    actual=sha(data)
    if actual!=expected:raise ValueError('MAP não corresponde ao inventário reconhecido')
    return actual


def export(data,index):
    entries=[]
    for at in sorted(index.records):
        if bytes(data[at:at+4]) in set(LAYOUTS)|{b'msg\0',b'msgn'}:
            entries.append(descriptor(data,at,index))
    return {'schema':1,'policy':POLICY,'resource':RESOURCE,'source_sha256':source_hash(data),
            'catalog_version':'v003','entries':entries}


def identity(entry):
    result={k:v for k,v in entry.items() if k not in ('mode','segments')}
    result['segments']=[{k:v for k,v in s.items() if k!='translation'} for s in entry['segments']]
    return result


def control_check(before,after,tokenizer=tokens):
    a,opaque_a=tokenizer(before);b,opaque_b=tokenizer(after)
    if opaque_a or opaque_b:raise ValueError('Sintaxe de controle não aprovada')
    if [x['hex'] for x in a]!=[x['hex'] for x in b]:raise ValueError('Controles, quebras ou escolhas alterados')
    # Preserve command adjacency and empty spans, including prefix/suffix commands.
    def empties(raw,parts):
        cursor=0;out=[]
        for token in parts:
            pos=token['relative_offset'];out.append(pos==cursor)
            cursor=pos+len(bytes.fromhex(token['hex']))
        out.append(cursor==len(raw));return out
    if empties(before,a)!=empties(after,b):raise ValueError('Posição de comandos ou spans vazios incompatíveis')


def width_units(raw,tokenizer=tokens):
    parts,_=tokenizer(raw);visible=bytearray();cursor=0
    for t in parts:
        at=t['relative_offset'];visible.extend(raw[cursor:at])
        if t['kind'] in ('page','line'):visible.extend(bytes.fromhex(t['hex']))
        cursor=at+len(bytes.fromhex(t['hex']))
    visible.extend(raw[cursor:])
    return [sum(2 if c in CHAR_TO_BYTES else 1 for c in line) for line in decode(bytes(visible)).replace('\t','\n').split('\n')]


def compile_entry(data,entry,old,*,b15=False,numeric1=False,numeric15=False,t0=False,i0=False):
    tokenizer=tokens
    if i0:
        from control_i0 import tokenize as tokenizer
    elif t0:
        from control_t0 import tokenize as tokenizer
    elif numeric15:
        from control_numeric15 import tokenize as tokenizer
    elif numeric1:
        from control_numeric1 import tokenize as tokenizer
    elif b15:
        from control_b15 import tokenize as tokenizer
    if identity(entry)!=identity(old):raise ValueError('Metadados, fonte ou bytes originais alterados')
    mode=entry.get('mode')
    if mode not in ('slots','repack'):raise ValueError('Modo de edição inválido')
    if mode=='repack' and not old['repack_supported']:raise ValueError('Repack não comprovado para esta família')
    changed=any(s['translation']!=s['source'] for s in entry['segments'])
    if not changed:return None,{'status':'unchanged','id':old['id']}
    if old['blocked_reasons']:raise ValueError('; '.join(old['blocked_reasons']))
    output=bytearray.fromhex(old['header_hex']);raws=[];warnings=[]
    limited=(b15 or numeric1 or numeric15 or t0 or i0) and any(any(t['kind'] in ('preserved-b15-reference','preserved-numeric1-reference','preserved-numeric15-reference','preserved-t0-reference','preserved-i0-reference') for t in tokenizer(bytes.fromhex(s['source_hex']))[0]) for s in old['segments'])
    if limited and mode!='slots':raise ValueError('Dynamic reference requires fixed slots')
    for new,src in zip(entry['segments'],old['segments']):
        text=new['translation']
        if not isinstance(text,str) or not text:raise ValueError('Tradução vazia ou inválida')
        if not src['editable'] and text!=src['source']:raise ValueError('Rótulo/nome protegido')
        raw=bytes.fromhex(src['source_hex']) if text==src['source'] else encode(text)
        if text!=src['source']:
            if decode(raw)!=text:raise ValueError('Round-trip de Unicode falhou')
            control_check(bytes.fromhex(src['source_hex']),raw,tokenizer)
            if limited and len(raw)>len(bytes.fromhex(src['source_hex'])):raise ValueError('Dynamic reference: source byte budget exceeded')
            if max(width_units(raw,tokenizer))>max(width_units(bytes.fromhex(src['source_hex']),tokenizer)):
                warnings.append(f'{src["key"]}: linha mais larga; validação visual necessária')
        if src['runtime_byte_limit'] is not None and len(raw)>src['runtime_byte_limit']:
            raise ValueError('Limite do buffer de execução excedido')
        raws.append(raw)
    offsets=[]
    for n,(raw,src) in enumerate(zip(raws,old['segments'])):
        if mode=='slots':
            if len(output)!=src['offset']-old['offset']:raise ValueError('Fronteira de segmento incompatível')
            if len(raw)>src['capacity']:raise ValueError(f'Overflow em {src["key"]}: {len(raw)} > {src["capacity"]} bytes')
            offsets.append(old['offset']+len(output));output.extend(raw)
            output.extend(bytes(src['capacity']+1-len(raw)))
        else:
            offsets.append(old['offset']+len(output));output.extend(raw);output.append(0)
            if n<len(raws)-1:output.extend(bytes((-len(output))%4))
    if len(output)>old['size']:raise ValueError('Payload expandido excede o registro; realocação externa bloqueada')
    output.extend(bytes(old['size']-len(output)))
    at=old['offset'];before=bytes(data[at:at+old['size']])
    if bytes.fromhex(old['tag']) in (b'smnn',b'2snm'):
        label=old['segments'][2]
        label_start=label['offset']-at
        if output[label_start:]!=before[label_start:]:
            raise ValueError('Rótulo e padding de escolha nomeada alterados')
    if len(output)!=len(before) or output[:len(bytes.fromhex(old['header_hex']))]!=bytes.fromhex(old['header_hex']):
        raise ValueError('Tamanho/cabeçalho do registro alterado')
    # Reparse structure at identical byte positions. Reserved PT-BR pairs are
    # replaced by two ASCII bytes only in this in-memory structural shadow.
    shadow=bytearray(output)
    for raw,pos in zip(raws,offsets):
        i=0
        while i<len(raw):
            if raw[i:i+2] in BYTES_TO_CHAR:
                shadow[pos-at+i:pos-at+i+2]=b'aa';i+=2
            else:i+=1
    tag=bytes.fromhex(old['tag'])
    if tag==b'msg\0':parsed,_=parse_msg(shadow,0);readback=[parsed['text_offset']]
    elif tag==b'msgn':parsed,_=parse_msgn(shadow,0);readback=[parsed['text_offset'],parsed['display_label']['text_offset']]
    else:
        _,parsed=parse_advanced(shadow,0);readback=[s['text_offset'] for s in parsed['segments']]
    if readback!=[pos-at for pos in offsets]:raise ValueError('Parser da família diverge dos offsets compilados')
    for n,(raw,pos) in enumerate(zip(raws,offsets)):
        relative=pos-at
        if output[relative:relative+len(raw)+1]!=raw+b'\0':raise ValueError('Falha na releitura do segmento')
    info={'status':'accepted','id':old['id'],'mode':mode,'warnings':warnings,
          'source_lengths':[len(bytes.fromhex(s['source_hex'])) for s in old['segments']],
          'target_lengths':list(map(len,raws)),'source_capacities':[s['capacity'] for s in old['segments']],
          'source_offsets':[s['offset'] for s in old['segments']],'target_offsets':offsets,
          'record_offset':at,'record_size':old['size'],'block_offset':old['block_offset'],
          'visual_status':'pending_manual_validation'}
    return {'resource':RESOURCE,'offset':at,'before':before,'after':bytes(output),'id':old['id']},info


def compile_batch(data,document,index=None,verify_source=True):
    if not isinstance(document,dict) or not isinstance(document.get('entries'),list):raise ValueError('Formato de lote inválido')
    if any(not isinstance(e,dict) or not isinstance(e.get('segments'),list) or any(not isinstance(s,dict) for s in e['segments']) for e in document['entries']):
        raise ValueError('Estrutura de registros/segmentos inválida')
    if document.get('schema')!=1 or document.get('policy') not in (POLICY,NAMED_POLICY,B15_POLICY,NUMERIC1_POLICY,NUMERIC15_POLICY,T0_POLICY,I0_POLICY) or document.get('resource')!=RESOURCE:
        raise ValueError('Schema/política incompatível')
    named_choices=document['policy'] in (NAMED_POLICY,B15_POLICY,NUMERIC1_POLICY,NUMERIC15_POLICY,T0_POLICY,I0_POLICY)
    i0=document['policy']==I0_POLICY
    t0=document['policy'] in (T0_POLICY,I0_POLICY)
    if i0:
        from control_i0 import verify as verify_i0
        i0_evidence=verify_i0((ROOT/'JOGO/Metal Saga/SLUS_212.93').read_bytes())
    numeric15=document['policy'] in (NUMERIC15_POLICY,T0_POLICY,I0_POLICY)
    if t0:
        from control_t0 import verify as verify_t0
        t0_evidence=verify_t0((ROOT/'JOGO/Metal Saga/SLUS_212.93').read_bytes())
    numeric1=document['policy'] in (NUMERIC1_POLICY,NUMERIC15_POLICY,T0_POLICY,I0_POLICY)
    if numeric15:
        from control_numeric15 import verify as verify_numeric15
        numeric15_evidence=verify_numeric15((ROOT/'JOGO/Metal Saga/SLUS_212.93').read_bytes())
    b15=document['policy'] in (B15_POLICY,NUMERIC1_POLICY,NUMERIC15_POLICY,T0_POLICY,I0_POLICY)
    if numeric1:
        from control_numeric1 import verify as verify_numeric1
        numeric1_evidence=verify_numeric1((ROOT/'JOGO/Metal Saga/SLUS_212.93').read_bytes())
    if b15:
        from control_b15 import verify
        b15_evidence=verify((ROOT/'JOGO/Metal Saga/SLUS_212.93').read_bytes())
    if named_choices:
        from investigate_named_choices import verify_elf,ORIGINAL_SHA
        evidence=verify_elf((ROOT/'JOGO/Metal Saga/SLUS_212.93').read_bytes())
    actual=source_hash(data) if verify_source else sha(data)
    if document.get('source_sha256')!=actual:raise ValueError('Hash de origem do lote incorreto')
    index=index or SsdIndex(data);results=[];patches=[];seen=set()
    for entry in document['entries']:
        try:
            at=entry['offset']
            if at in seen:raise ValueError('ID/offset duplicado no lote')
            seen.add(at);old=descriptor(data,at,index,named_choices=named_choices,b15=b15,numeric1=numeric1,numeric15=numeric15,t0=t0,i0=i0)
            patch,result=compile_entry(data,entry,old,b15=b15,numeric1=numeric1,numeric15=numeric15,t0=t0,i0=i0)
            results.append(result)
            if patch:patches.append(patch)
        except (ValueError,KeyError,TypeError,UnicodeError) as error:
            results.append({'id':entry.get('id','?'),'status':'refused','reason':str(error)})
    valid=all(r['status']!='refused' for r in results)
    patches.sort(key=lambda p:p['offset'])
    if any(a['offset']+len(a['before'])>b['offset'] for a,b in zip(patches,patches[1:])):
        raise ValueError('Patches sobrepostos')
    report={'schema':1,'policy':document['policy'],'valid':valid,'transaction':'all-or-nothing',
            'accepted':sum(r['status']=='accepted' for r in results),
            'refused':sum(r['status']=='refused' for r in results),
            'unchanged':sum(r['status']=='unchanged' for r in results),'results':results,
            'requires_ptbr_fonts':any(isinstance(s.get('translation'),str) and any(c in CHAR_TO_BYTES for c in s['translation']) for e in document['entries'] for s in e.get('segments',[]) if s.get('translation')!=s.get('source')),
            'source_sha256':actual,'ssd_boundaries_unchanged':True,
            'record_relocation':False,'pixel_metrics_verified':False}
    if named_choices:
        report['named_choice_evidence']={'elf_sha256':ORIGINAL_SHA,'instruction_assertions':len(evidence),
            'named_slots_only':True,'label_and_tail_immutable':True,'runtime_visual_status':'pending_manual_validation'}
    if b15:report['b15_evidence']=b15_evidence
    if numeric1:report['numeric1_evidence']=numeric1_evidence
    if numeric15:report['numeric15_evidence']=numeric15_evidence
    if t0:report['t0_evidence']=t0_evidence
    if i0:report['i0_evidence']=i0_evidence
    return (patches if valid else []),report


def merge(documents):
    """Merge independently saved batches; reject competing edits to the same field."""
    if not documents:raise ValueError('Nenhum lote informado')
    if any(not isinstance(d,dict) or not isinstance(d.get('entries'),list) for d in documents):raise ValueError('Formato de lote inválido')
    result={k:v for k,v in documents[0].items() if k!='entries'};by_id={}
    for document in documents:
        if not isinstance(document,dict) or not isinstance(document.get('entries'),list):raise ValueError('Formato de lote inválido')
        if {k:v for k,v in document.items() if k!='entries'}!=result:raise ValueError('Lotes têm origens/políticas diferentes')
        local_ids=set()
        for entry in document['entries']:
            key=entry['id']
            if key in local_ids:raise ValueError('ID duplicado dentro de um lote')
            local_ids.add(key)
            if key not in by_id:by_id[key]=json.loads(json.dumps(entry));continue
            old=by_id[key]
            if identity(old)!=identity(entry):raise ValueError('Metadados conflitantes entre lotes')
            edited_old=any(s['translation']!=s['source'] for s in old['segments'])
            edited_new=any(s['translation']!=s['source'] for s in entry['segments'])
            if edited_old and edited_new and old['mode']!=entry['mode']:raise ValueError('Modos de edição conflitantes')
            if edited_new:old['mode']=entry['mode']
            for a,b in zip(old['segments'],entry['segments']):
                if b['translation']==b['source']:continue
                if a['translation'] not in (a['source'],b['translation']):raise ValueError(f'Traduções conflitantes: {key}/{a["key"]}')
                a['translation']=b['translation']
    result['entries']=sorted(by_id.values(),key=lambda e:e['offset'])
    return result
