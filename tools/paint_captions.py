"""Opt-in paint captions: same 23-byte cells, complete aliases, ten-byte ceiling."""
from discover_paint import analyse, RESOURCE, START, COUNT, STRIDE, WINDOWS
from dialogue import sha
from gfi import encode, decode
from speaker_labels import _run
from spack_ui import execute_byte_length

POLICY = 'paint-caption-fixed-cells-observed-ten-byte-ceiling-v001'
EXTRA_WINDOWS = ((0x4f810,0x4f870),(0x3f838,0x3f898),
                 (0x3f910,0x3f930),(0x3db20,0x3dc84),
                 (0x2266cc,0x2266d8),(0x2267f0,0x226810))
SOURCE_SHA = '8962110f68a1fa7ad0c0abd355da966c58396e7f99176d26d80732e764aca8ee'


def bindings(elf):
    return [{'offset':a,'size':z-a,'sha256':sha(elf[a:z])}
            for a,z in WINDOWS+EXTRA_WINDOWS]


def consumer_probe(elf, value):
    """Bounded constructor forwarding and actual dynamic allocation arguments.

    Saved-register setup/prologues and font selection are supplied by harness;
    allocator, glyph conversion, text-object constructor and GPU are not run.
    """
    length = execute_byte_length(elf,value)
    if length != len(value):raise ValueError('Paint source byte count differs')
    regs=[0]*32;regs[6]=0x640001;regs[17]=22
    regs=_run(elf,0x4f82c,EXTRA_WINDOWS,regs,[],0x4f830)
    regs=_run(elf,0x4f834,EXTRA_WINDOWS,regs,[],0x3f838)
    if (regs[6],regs[7],regs[8])!=(0,0x640001,22):
        raise ValueError('Paint constructor forwarding differs')
    regs=[0]*32;regs[16]=0x620000;regs[17]=0x630000
    regs[18]=0;regs[19]=0x640001;regs[20]=22
    result=_run(elf,0x3f880,EXTRA_WINDOWS,regs,[],0x3f910)
    if (result[4],result[5],result[6],result[7],result[8])!=(0x620000,0x630000,0,0x640001,22):
        raise ValueError('Paint base text forwarding differs')
    # The same source is passed to strlen at 0x3DBAC; resume after its return.
    regs=[0]*32;regs[2]=length
    result=_run(elf,0x3dbb8,EXTRA_WINDOWS,regs,[],0x1a5df8)
    expected=(length+32)&~3
    if result[4]!=expected or expected < length+1:
        raise ValueError('Paint dynamic text allocation differs')
    return {'source_bytes':length,'allocation_request_bytes':expected}


def validate_value(text):
    value=encode(text)
    if (not value or len(value)>10 or text!=text.strip()
        or any(c in value for c in (0,9,10,13,37,124)) or decode(value)!=text):
        raise ValueError('Paint caption exceeds observed ten-byte ceiling or has controls')
    return value


def compile_captions(elf,config,raw=None):
    from interface_resources import original
    if raw is None:raw=original(RESOURCE)
    if sha(raw)!=SOURCE_SHA:raise ValueError('Paint original resource differs')
    metadata,catalogue=analyse(elf,raw)
    if (set(config)!={'policy','source_sha256','table_sha256','instruction_windows','entries'}
        or config['policy']!=POLICY or config['source_sha256']!=SOURCE_SHA
        or config['table_sha256']!=sha(raw[START:START+COUNT*STRIDE])
        or config['instruction_windows']!=bindings(elf)):
        raise ValueError('Paint policy/source/instruction bindings differ')
    rows=catalogue['rows'];aliases=catalogue['aliases']
    canonical={rows[a['indices'][0]]['id']:a for a in aliases}
    entries=config['entries'];ids=[e['id'] for e in entries]
    if len(ids)!=len(set(ids)) or set(ids)!=set(canonical):
        raise ValueError('Paint caption batch must cover all twelve alias groups once')
    patches=[];results=[];modified=bytearray(raw);probes=[]
    from translation_policy import validate
    for entry in entries:
        if set(entry)!={'id','source_sha256','translation'}:raise ValueError('Unknown paint target field')
        alias=canonical[entry['id']];first=rows[alias['indices'][0]]
        if entry['source_sha256']!=first['source_sha256']:raise ValueError('Paint caption source hash differs')
        value=validate_value(entry['translation'])
        if value==bytes.fromhex(first['source_hex']):raise ValueError('Unchanged paint caption')
        issues=validate(first['source_ascii'],entry['translation'])
        if issues:raise ValueError('Paint terminology: '+'; '.join(issues))
        probes.extend([consumer_probe(elf,bytes.fromhex(first['source_hex'])),consumer_probe(elf,value)])
        for index in alias['indices']:
            row=rows[index];at=row['name_offset'];before=raw[at:at+23];after=value+bytes(23-len(value))
            patches.append({'id':row['id'],'resource':RESOURCE,'offset':at,'before':before,'after':after})
            modified[at:at+23]=after
            results.append({'id':row['id'],'offset':at,'source_sha256':sha(before),
                            'target_sha256':sha(after),'source_bytes':row['source_bytes'],
                            'target_bytes':len(value),'alias_group':entry['id']})
    # Independent cell readback; all group/parameter bytes and outer SDA intact.
    for row in rows:
        at=row['offset'];record=modified[at:at+STRIDE]
        if record[0]!=raw[at] or record[24:]!=raw[at+24:at+STRIDE]:
            raise ValueError('Paint metadata changed')
        target=next(e['translation'] for e in entries if row['index'] in canonical[e['id']]['indices'])
        if decode(bytes(record[1:24]).split(b'\0',1)[0])!=target:raise ValueError('Paint readback differs')
    for p in patches:modified[p['offset']:p['offset']+23]=p['before']
    if modified!=raw:raise ValueError('Paint reverse round-trip differs')
    return patches,{'policy':POLICY,'accepted':len(patches),'unique_translations':len(entries),
        'source_sha256':SOURCE_SHA,'instruction_windows':bindings(elf),
        'maximum_target_bytes':max(r['target_bytes'] for r in results),
        'original_maximum_bytes':metadata['maximum_original_caption_bytes'],
        'source_and_target_consumer_probe_cases':len(probes),'aliases_preserved':True,
        'groups_parameters_sda_and_resource_size_unchanged':True,'reverse_roundtrip':True,
        'runtime_visual_status':'pending_user_verification','results':results,
        'limits':'Bounded forwarding/strlen/allocation argument probes only. Register setup and allocation return are supplied; full constructor, glyph drawing and PCSX2 not executed.'}
