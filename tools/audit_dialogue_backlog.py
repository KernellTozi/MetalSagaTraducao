"""One replaceable local dialogue backlog; originals never go into public metadata."""
import argparse,collections,json,mmap,re,struct
from pathlib import Path
from reinsertion import ROOT,SOURCE,local
from dialogue import sha
from dialogue_advanced import SsdIndex,LAYOUTS
from audit_translation_coverage import load_compiled,audit
from translation_policy import POLICY_PATH

SCOPE='Consolidated local dialogue backlog; classification is not edit approval'


def label_consumer_evidence(elf):
    from glyph_spacing import ORIGINAL_SHA
    if sha(elf)!=ORIGINAL_SHA:raise ValueError('Speaker-label ELF revision differs')
    words={0x1c6548:0x0c0bf25a,0x1c654c:0x0240282d,0x1c6de0:0x0c0bf25a,
        0x1c6de4:0x0200282d,0x1fd97c:0x00a0902d,0x1fd9d8:0x0c0c95b3,
        0x1fd9dc:0x0240202d,0x1fd9f4:0x24420004,0x1fda0c:0x00442024,
        0x1fda10:0x0c0a9478,0x1fda18:0x0240282d,0x1fda1c:0xae220034,
        0x1fda20:0x0c0c956d,0x1fda24:0x0040202d}
    for at,w in words.items():
        if struct.unpack_from('<I',elf,at)[0]!=w:raise ValueError('Speaker-label call/forwarding differs')
    return {'elf_sha256':ORIGINAL_SHA,'instruction_assertions':[{'offset':at,'word':f'{w:08x}'} for at,w in words.items()],
        'msgn_label_call':0x1c6548,'named_choice_label_call':0x1c6de0,'setter':0x1fd968,
        'setter_destination_field':0x34,'helper_call_offsets':[0x2266cc,0x1a61e0,0x2265b4],
        'observed':'Both callers forward their label pointer in a1; setter retains it, transforms helper return with +4/alignment mask, stores a returned pointer at object+0x34, and forwards source/destination to another helper',
        'hypothesis':'Length-based allocation and string copy; helper implementations/rendering and any portrait dependencies require further proof before editing',
        'editing_enabled':False,'instructions_executed':False,'pcsx2_executed':False}


def classify(document,report,protected):
    summary,rows=audit(document,report,json.loads(POLICY_PATH.read_text(encoding='utf-8')))
    protected={r['id']:r for r in protected};buckets=collections.defaultdict(list);native=collections.defaultdict(list)
    for row in rows:
        e=row['entry'];status=row['class'];key=e['id']
        if status=='deferred':
            if key in protected:
                if e['record_sha256']!=protected[key]['record_sha256']:raise ValueError('Protected N3 fingerprint differs')
                bucket='protected_tank_names_still_noneditable'
            elif any('nativos' in r for r in e['blocked_reasons']):
                bucket='native_pending_context';signature=tuple(s['source_hex'] for s in e['segments'] if s['editable'])
                native[signature].append(key)
            else:bucket='other_controls_pending'
            buckets[bucket].append(e)
        elif status=='review_unchanged':buckets['editorial_review_not_automatic_translation'].append(e)
    groups=[{'record_ids':ids,'records':len(ids),'source_segment_sha256':[sha(bytes.fromhex(v)) for v in sig],
        'decision':'Source repeated verbatim; runtime/context unresolved, not translated or declared debug'} for sig,ids in native.items()]
    metadata={'catalog_records':summary['records'],'translated_records':summary['classes']['modified'],
        'body_or_choice_changed_records':sum(any(s.get('key','body')!='label' and s['translation']!=s['source'] for s in e['segments']) for e in document['entries']),
        'technical_deferrals':summary['classes']['deferred'],
        'protected_tank_names_still_noneditable':len(buckets['protected_tank_names_still_noneditable']),
        'native_pending_context':len(buckets['native_pending_context']),
        'other_controls_pending':len(buckets['other_controls_pending']),
        'editorial_review_records':len(buckets['editorial_review_not_automatic_translation']),
        'name_expression_candidates':summary['classes']['name_or_expression_candidate'],
        'punctuation_control_candidates':summary['classes']['controls_or_punctuation'],
        'native_groups':groups,'automatic_edit_approval':False,'pcsx2_executed':False}
    return metadata,dict(buckets)


def scan_unparsed_ssd(data,index):
    counts=collections.Counter();hits=[];known=set(LAYOUTS)|{b'msg\0',b'msgn'};scanned=0
    for at,row in index.records.items():
        tag=bytes(data[at:at+4])
        if tag in known:continue
        counts[tag.hex()]+=1;ins=row['instruction'];raw=data[at+8:at+ins['size']];scanned+=len(raw)
        samples=[m.group().decode('ascii') for m in re.finditer(rb'[A-Za-z][ -~]{10,}',raw)
            if b' ' in m.group() and not any(c in m.group() for c in (b'/',b'\\',b'::'))]
        if samples:hits.append({'offset':at,'tag_hex':tag.hex(),'size':ins['size'],'source_candidates':samples})
    return {'indexed_ssd_blocks':len(index.blocks),'indexed_ssd_records':len(index.records),
        'other_records_scanned':sum(counts.values()),'other_payload_bytes_scanned':scanned,
        'other_tags':dict(sorted(counts.items())),'candidate_records':len(hits),
        'criterion':'ASCII letter followed by >=10 printable bytes, contains space, excludes path/scope delimiters',
        'limits':'Indexed SSD only; short/native/compressed/outside-SSD text may be missed; no completeness proof or automatic parser promotion'},hits


def collect_labels(document):
    labels={};references=0;translated=0
    for entry in document['entries']:
        for segment in entry['segments']:
            if segment['key']!='label':continue
            if segment['editable']:raise ValueError('Historical speaker labels unexpectedly editable')
            signature=segment['source_hex'];references+=1
            row=labels.setdefault(signature,{'source':segment['source'],'source_hex':signature,
                'source_sha256':sha(bytes.fromhex(signature)),'references':[],'editing_authorized':False})
            target=segment.get('translation',segment['source']);changed=target!=segment['source'];translated+=changed
            position=document.get('compiled_speaker_label_offsets',{}).get(entry['id'],segment['offset'])
            row['references'].append({'record_id':entry['id'],'offset':segment['offset'],'capacity':segment['capacity'],
                'compiled_offset':position,'compiled_capacity':entry['offset']+entry['size']-position-1 if position!=segment['offset'] else segment['capacity'],
                'translation':target,'translated':changed})
    return {'label_references':references,'unique_labels':len(labels),'editing_authorized':False,
        'translated_label_references':translated,'remaining_label_references':references-translated,
        'explicit_overlay_policy':document.get('speaker_label_policy'),
        'explicit_relocation_policy':document.get('speaker_label_relocation_policy'),
        'explicit_byte_tail_policy':document.get('speaker_label_byte_policy'),
        'explicit_context_review_policy':document.get('speaker_context_policy'),
        'explicit_body_review_policy':document.get('speaker_body_policy'),
        'explicit_faction_review_policy':document.get('speaker_faction_policy'),
        'explicit_context_finish_policy':document.get('context_finish_policy'),
        'limits':'No unrestricted or automatic label editing; explicit source-bound overlay may translate reviewed generic roles only; proper names, markers and unknown labels remain protected'},list(labels.values())


def run(folder,output,summary_path=None):
    folder=local(folder);output=local(output)
    if summary_path is not None:
        summary_path=Path(summary_path).resolve()
        if not summary_path.is_relative_to(ROOT/'reports') or summary_path.exists():raise ValueError('Use new metadata report under reports/')
    if output.exists() and json.loads(output.read_text(encoding='utf-8')).get('scope')!=SCOPE:raise ValueError('Refuse unrelated output')
    temporary=output.with_suffix('.json.tmp')
    if temporary.exists():raise ValueError('Backlog temporary file already exists')
    p,r=load_compiled(folder);document=json.loads(p);report=json.loads(r)
    protected=json.loads((ROOT/'reports/n3-preservation-v001.json').read_text(encoding='utf-8'))['records']
    metadata,buckets=classify(document,report,protected)
    label_metadata,labels=collect_labels(document)
    from interface_text import SOURCE as ELF_SOURCE
    label_evidence=label_consumer_evidence(ELF_SOURCE.read_bytes())
    with SOURCE.open('rb') as stream,mmap.mmap(stream.fileno(),0,access=mmap.ACCESS_READ) as data:
        scan,hits=scan_unparsed_ssd(data,SsdIndex(data))
    metadata.update({'schema':1,'scope':SCOPE,'build':folder.relative_to(ROOT).as_posix(),
        'source_map_sha256':document['source_sha256'],'compiled_plan_sha256':sha(p),
        'compiled_report_sha256':sha(r),'outside_known_parsers_scan':scan,
        'speaker_label_catalogue':label_metadata,'speaker_label_consumer_evidence':label_evidence,
        'speaker_label_overlay_evidence':{k:v for k,v in report.get('speaker_labels',{}).items() if k!='results'},
        'speaker_label_relocation_evidence':{k:v for k,v in report.get('speaker_label_relocations',{}).items() if k!='results'},
        'speaker_label_byte_tail_evidence':{k:v for k,v in report.get('speaker_label_byte_packing',{}).items() if k!='results'},
        'speaker_context_review_evidence':{k:v for k,v in report.get('speaker_context_review',{}).items() if k!='results'},
        'speaker_body_review_evidence':{k:v for k,v in report.get('speaker_body_review',{}).items() if k!='results'},
        'speaker_faction_review_evidence':{k:v for k,v in report.get('speaker_faction_review',{}).items() if k!='results'},
        'context_finish_evidence':{k:v for k,v in report.get('context_finish_review',{}).items() if k not in ('results','body_results')},
        'originals_modified':False,'iso_created':False})
    result={**metadata,'local_review_entries':buckets,'local_new_candidates':hits,'local_speaker_labels':labels}
    output.parent.mkdir(parents=True,exist_ok=True)
    with temporary.open('x',encoding='utf-8') as stream:json.dump(result,stream,ensure_ascii=False,indent=2);stream.write('\n')
    temporary.replace(output)
    if summary_path is not None:
        with summary_path.open('x',encoding='utf-8') as stream:json.dump(metadata,stream,ensure_ascii=False,indent=2);stream.write('\n')
    return metadata


if __name__=='__main__':
    p=argparse.ArgumentParser(description='Consolidar pendências de diálogo localmente em um JSON, sem IA/APIs')
    p.add_argument('--build-dir',type=Path,default=ROOT/'work/interface-v062')
    p.add_argument('--output',type=Path,default=ROOT/'work/dialogos-pendencias-atual.json')
    p.add_argument('--summary',type=Path);a=p.parse_args()
    print(json.dumps(run(a.build_dir,a.output,a.summary),ensure_ascii=False,indent=2))
