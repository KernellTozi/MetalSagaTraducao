"""Source-bound follow-up: motion envelopes, model references and SAF packaging.

Read-only. Decoding a motion envelope does not decode its keyframe semantics
or authorize editing models, sounds or compressed payloads.
"""
import argparse, collections, json, struct
from io import BytesIO
from pathlib import Path
from reinsertion import ROOT, local
from dialogue import sha
from interface_text import SOURCE
from glyph_spacing import ORIGINAL_SHA
from discover_credits import decode, replay, execute_decoder_loop

SCOPE = 'Bounded binary remainder discovery v002'
TABLES = (
    ('RMGDOG.SDA', 0x2656d0, 1, 36, 0x150474),
    ('RMGKAERU.SDA', 0x265e88, 1, 36, 0x155c74),
    ('RMGTANK.SDA', 0x267a98, 10, 24, 0x15eba8),
    ('RMGTANK.SDA', 0x267b88, 9, 36, 0x15ebc4),
    ('RMGDANCE.SDA', 0x267f50, 11, 36, 0x164fe8),
    ('RMGALAN.SDA', 0x2684b8, 18, 36, 0x171c38),
    ('F_SPEND.SDA', 0x32e7d8, 5, 24, 0x13720c),
)
WINDOWS = ((0x13c9b4,0x13ca08),(0x190fc8,0x191000),
    (0x18baa4,0x18bb90),(0x18bc08,0x18bc58),(0x1906d8,0x1906ec),
    (0x19b738,0x19b910),(0x14d2f8,0x14d498),(0x137174,0x137214),
    (0x18a998,0x18a9e0),(0x203e08,0x203fbc),
    (0x171c9c,0x171cc0),(0x171cdc,0x171d00),(0x135678,0x1356cc),
    (0x15f1dc,0x15f240))


def bundle_ranges(raw):
    if len(raw)<8: raise ValueError('Short motion bundle')
    count=struct.unpack_from('<I',raw)[0]
    if not 1<=count<=256 or 4+4*count>len(raw): raise ValueError('Motion count outside bounds')
    offsets=list(struct.unpack_from(f'<{count}I',raw,4))
    if offsets[0]!=4+4*count or offsets!=sorted(set(offsets)) or offsets[-1]>=len(raw):
        raise ValueError('Motion offsets overlap or escape bundle')
    if any(v%4 for v in offsets): raise ValueError('Motion offset alignment differs')
    ranges=list(zip(offsets,offsets[1:]+[len(raw)]))
    if raw[:offsets[0]]+b''.join(raw[a:z] for a,z in ranges)!=raw:
        raise ValueError('Motion bundle round-trip differs')
    return ranges


def motion(raw):
    if len(raw)<16: raise ValueError('Short motion record')
    first,tracks,opaque,compressed=struct.unpack_from('<IHHI',raw)
    if not 1<=tracks<=4096 or not 12<=compressed<=len(raw)-4:
        raise ValueError('Motion track count/compressed pointer outside bounds')
    at=12; groups=[]
    for _ in range(tracks):
        start=at
        if at+8>compressed: raise ValueError('Motion track header overlaps payload')
        counts=raw[at+6:at+8];at+=8;blocks=[]
        for count in counts:
            for _ in range(count):
                if at+8>compressed: raise ValueError('Short supplementary motion block')
                n=struct.unpack_from('<H',raw,at)[0];size=8+8*n
                if at+size>compressed: raise ValueError('Supplementary motion block overflows')
                blocks.append({'offset':at,'count':n,'size':size});at+=size
        groups.append({'offset':start,'size':at-start,'list_counts':list(counts),'blocks':blocks})
    if at!=compressed: raise ValueError('Motion metadata end differs from compressed pointer')
    decoded,consumed,packets=decode(raw[compressed:],maximum=1024*1024)
    if replay(packets)!=raw[compressed+4:compressed+consumed]:
        raise ValueError('Motion compressed token replay differs')
    tail=raw[compressed+consumed:]
    # All bytes retained, including nonzero final-record suffixes. Not free space.
    if raw[:compressed]+raw[compressed:compressed+4]+replay(packets)+tail!=raw:
        raise ValueError('Motion record round-trip differs')
    return {'first_word_opaque':first,'track_count':tracks,'header_u16_opaque':opaque,
        'compressed_offset':compressed,'metadata_sha256':sha(raw[12:compressed]),
        'variable_blocks':sum(len(g['blocks']) for g in groups),
        'decoded_size':len(decoded),'decoded_sha256':sha(decoded),
        'compressed_consumed':consumed,'tail_size':len(tail),'tail_sha256':sha(tail),
        'tail_nonzero':bool(any(tail)),'roundtrip':True},decoded


def saf(raw):
    at=0;chunks=[]
    for expected in (b'SAF ',b'HD  ',b'BD  ',b'END '):
        if at+16>len(raw): raise ValueError('Truncated SAF chunk')
        tag,size,a,b=struct.unpack_from('<4sIII',raw,at)
        end=at+16+size;aligned=(end+15)&~15
        if tag!=expected or a or b or aligned>len(raw): raise ValueError('SAF chunk identity/size/flags differ')
        if any(raw[end:aligned]): raise ValueError('SAF alignment bytes differ')
        chunks.append({'tag':tag.decode(),'offset':at,'payload_offset':at+16,'size':size})
        at=aligned
    if at!=len(raw) or chunks[-1]['size'] or not chunks[0]['size'] or chunks[0]['size']%16:
        raise ValueError('SAF terminal bounds differ')
    hd=chunks[1];at=hd['payload_offset'];end=at+hd['size'];sub=[]
    for kind in (b'sreV',b'daeH',b'igaV',b'lpmS',b'tesS',b'gorP'):
        if at+12>end or raw[at:at+8]!=b'IECS'+kind: raise ValueError('Sound HD subsection identity differs')
        size=struct.unpack_from('<I',raw,at+8)[0]
        if size<12 or at+size>end: raise ValueError('Sound HD subsection size differs')
        sub.append({'kind':kind.decode(),'offset':at,'size':size});at+=size
    if at!=end: raise ValueError('Sound HD subsections do not tile header')
    pieces=[]
    for c in chunks:
        a=c['offset'];z=(a+16+c['size']+15)&~15
        pieces.append(struct.pack('<4sIII',c['tag'].encode(),c['size'],0,0)+raw[a+16:z])
    if b''.join(pieces)!=raw: raise ValueError('SAF round-trip differs')
    return {'kind':'sound-bank-chunk-envelope','chunks':chunks,'hd_subsections':sub,
        'roundtrip':True,'audio_samples_decoded':False}


def model_bindings(elf):
    if sha(elf)!=ORIGINAL_SHA: raise ValueError('Original model consumer ELF differs')
    result={}
    for name,table,count,stride,caller in TABLES:
        for index in range(count):
            at=table+index*stride;fields=struct.unpack_from(f'<{stride//4}I',elf,at)
            key=(name,fields[0])
            if key in result: raise ValueError('Duplicate model registration')
            result[key]={'table_offset':at,'table_sha256':sha(elf[at:at+stride]),
                'caller_offset':caller,'model_size':fields[1],
                'texture_offset':fields[2],'texture_size':fields[3],
                'format_semantics':'Model consumer binding; internal geometry not decoded',
                'motion_offset':fields[4] if stride==36 or name=='F_SPEND.SDA' else None,
                'motion_size':fields[5] if stride==36 or name=='F_SPEND.SDA' else None}
    if len(result)!=55: raise ValueError('Model registration count differs')
    return result


def run(output,summary=None):
    from discover_remaining_catalogue import ascii_stream,phrase_candidate
    from verify_test_iso import verify_image
    output=local(output)
    if output.exists() and json.loads(output.read_text(encoding='utf-8')).get('scope')!=SCOPE:
        raise ValueError('Unrelated output exists')
    if summary is not None:
        summary=Path(summary).resolve()
        if not summary.is_relative_to(ROOT/'reports') or summary.exists(): raise ValueError('Use new public report path')
    previous=json.loads((ROOT/'reports/descoberta-desconhecidos-v001.json').read_text(encoding='utf-8'))
    inventory={r['path']:r['sha256'] for r in json.loads((ROOT/'reports/inventory.json').read_text(encoding='utf-8'))}
    elf=SOURCE.read_bytes();bindings=model_bindings(elf);resources={};records=[];children=[];unique={};hits=[];cpu=[]
    image=ROOT/'work/interface-v038/MetalSaga-ptbr-interface-v038.iso';before=verify_image(image)
    recipes={p.name:sha(p.read_bytes()) for p in (ROOT/'translations').glob('*.json')}
    for row in previous['records']:
        if row['discovery']['kind'] not in ('unresolved','41-part-offset-bundle'): continue
        resource=row['resource'];name=Path(resource).name
        if resource not in resources:
            resources[resource]=(ROOT/'JOGO/Metal Saga'/resource).read_bytes()
            if sha(resources[resource])!=inventory[resource]: raise ValueError('Original resource differs')
        raw=resources[resource][row['offset']:row['offset']+row['size']]
        if sha(raw)!=row['sha256']: raise ValueError('Historical entry hash differs')
        result=None
        if raw[:4]==b'SAF ': result=saf(raw)
        elif (name,row['offset']) in bindings:
            binding=bindings[(name,row['offset'])]
            if not 0<binding['model_size']<=len(raw):
                raise ValueError('Model registered size exceeds extent')
            suffix=raw[binding['model_size']:]
            result={'kind':'consumer-bound-model-opaque-geometry',**binding,
                'opaque_suffix_size':len(suffix),'opaque_suffix_sha256':sha(suffix),
                'opaque_suffix_nonzero':bool(any(suffix))}
        elif name=='RMGALAN.SDA' and row['offset'] in (0x381810,0x387630):
            result={'kind':'special-consumer-bound-opaque-payload','consumer_offset':0x135678,
                'caller_offset':0x171c9c if row['offset']==0x381810 else 0x171cdc,
                'limits':'Original bounded resource forwarded to object initializer; internal format and exact purpose unresolved'}
        elif name=='RMGTANK.SDA' and row['offset']==0x1661b0:
            if struct.unpack_from('<II',elf,0x349ac0)!=(row['offset'],row['size']): raise ValueError('Special RMGTANK extent differs')
            result={'kind':'special-table-bound-opaque-payload','table_offset':0x349ac0,
                'table_sha256':sha(elf[0x349ac0:0x349ac8]),
                'limits':'Bound size/offset and caller references; payload semantics unresolved'}
        else:
            ranges=bundle_ranges(raw)
            result={'kind':'motion-offset-bundle','count':len(ranges),'roundtrip':True}
            for index,(a,z) in enumerate(ranges):
                part=raw[a:z];key=sha(part)
                if key not in unique:
                    meta,decoded=motion(part)
                    unique[key]=meta
                    for offset,text in ascii_stream(BytesIO(decoded)):
                        if phrase_candidate(text): hits.append({'child_sha256':key,'decoded_offset':offset,'size':len(text),'sha256':sha(text)})
                    # Representative independent original-instruction executions,
                    # rather than repeatedly executing duplicate animations.
                    profile='variable' if meta['variable_blocks'] else 'flat'
                    if meta['tail_nonzero']: profile='nonzero-tail'
                    if profile not in [c['profile'] for c in cpu] and len(decoded)<32000:
                        actual,used,steps=execute_decoder_loop(elf,part[meta['compressed_offset']:])
                        if actual!=decoded or used!=meta['compressed_consumed']: raise ValueError('Original motion decoder differs')
                        cpu.append({'profile':profile,'child_sha256':key,'decoded_size':len(decoded),'steps':steps,'matches':True})
                meta=unique[key]
                tail=meta['tail_size']
                if index<len(ranges)-1 and (tail>3 or meta['tail_nonzero']): raise ValueError('Nonfinal motion tail differs')
                if index==len(ranges)-1 and tail>127: raise ValueError('Final motion suffix exceeds observed bound')
                if meta['tail_nonzero'] and not (name=='F_SPEND.SDA' and index==len(ranges)-1 and tail<16):
                    raise ValueError('Nonzero suffix outside source-bound F_SPEND final record')
                children.append({'resource':resource,'parent_offset':row['offset'],'index':index,
                    'offset':row['offset']+a,'size':z-a,'sha256':key,'editing_authorized':False})
        records.append({**{k:row[k] for k in ('resource','offset','size','sha256')},'discovery':result,'editing_authorized':False})
    if len(records)!=221: raise ValueError('Follow-up root count differs')
    if before!=verify_image(image) or recipes!={p.name:sha(p.read_bytes()) for p in (ROOT/'translations').glob('*.json')}:
        raise ValueError('Playable baseline or recipes changed')
    report={'schema':1,'scope':SCOPE,'historical_baseline':365,'follow_up_roots':len(records),
        'classes':dict(collections.Counter(r['discovery']['kind'] for r in records)),
        'motion_child_occurrences':len(children),'unique_motion_payloads':len(unique),
        'decoded_unique_bytes':sum(m['decoded_size'] for m in unique.values()),
        'maximum_decoded_payload':max(m['decoded_size'] for m in unique.values()),
        'nonzero_tail_unique_payloads':sum(m['tail_nonzero'] for m in unique.values()),
        'decoded_ascii_phrase_probe':{'candidates':hits,'count':len(hits),
            'limits':'No hit does not prove absence of native/custom encoded text. Motion purpose also supported by original consumers.'},
        'original_decoder_cases':cpu,
        'instruction_windows':[{'offset':a,'size':z-a,'sha256':sha(elf[a:z])} for a,z in WINDOWS],
        'elf_sha256':sha(elf),'source_sha256':{r:sha(b) for r,b in resources.items()},
        'recipes_verified_unchanged':len(recipes),'iso_verified_unchanged':before,
        'records':records,'remaining_unresolved_root_semantics':3,
        'limits':'Motion numeric/keyframe semantics, model geometry, audio decoding and three special payloads remain incomplete. No editing release, no 100% game text coverage claim.',
        'iso_created':False,'pcsx2_executed':False,'translation_created':False}
    output.parent.mkdir(parents=True,exist_ok=True);temp=output.with_suffix('.json.tmp')
    with temp.open('x',encoding='utf-8') as f: json.dump({**report,'children':children,'unique_payloads':unique},f,indent=2);f.write('\n')
    temp.replace(output)
    if summary is not None:
        with summary.open('x',encoding='utf-8') as f: json.dump(report,f,indent=2);f.write('\n')
    return report


if __name__=='__main__':
    p=argparse.ArgumentParser(description='Investigar animações/modelos/bancos SAF sem alterar fontes ou ISO')
    p.add_argument('--output',type=Path,required=True);p.add_argument('--summary',type=Path)
    a=p.parse_args();r=run(a.output,a.summary)
    print(json.dumps({k:r[k] for k in ('classes','motion_child_occurrences','unique_motion_payloads','decoded_unique_bytes')},indent=2))
