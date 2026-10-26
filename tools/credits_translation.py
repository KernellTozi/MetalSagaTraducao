"""Opt-in FD_END role translations, bound original reader/font and same extent."""
from dialogue import sha
from discover_credits import RESOURCE
from credits_edit_pack import original,template,rebuild
from speaker_labels import _run

POLICY='credits-roles-same-slot-lzss-font22-v001'
WINDOWS=((0x1390a8,0x1390f0),(0x1399e4,0x139ab4),
    (0x139d40,0x139e98),(0x10e2d8,0x10e350),(0x10e608,0x10e658),
    (0x19b6f8,0x19b734))


def bindings(elf):
    return [{'offset':a,'size':z-a,'sha256':sha(elf[a:z])} for a,z in WINDOWS]


def consumer_probe(elf,size):
    regs=[0]*32;regs[4]=0x610000;header=bytearray(size.to_bytes(4,'little'))
    result=_run(elf,0x19b70c,WINDOWS,regs,[(0x610000,header)],0x1a5f78)
    if result[4]!=size:raise ValueError('Credits dynamic decoded allocation differs')
    obj=bytearray(0x10a4);regs=[0]*32;regs[2]=0x610000;regs[19]=0x630000
    _run(elf,0x1390b4,WINDOWS,regs,[(0x610000,header),(0x630000,obj)],0x1aefa0)
    if int.from_bytes(obj[0x50:0x54],'little')!=size:raise ValueError('Credits consumer size differs')
    regs=[0]*32;regs[2]=0x620000
    result=_run(elf,0x139a90,WINDOWS,regs,[],0x10e2d8)
    if result[4:8]!=[0x620000,22,0,0]:raise ValueError('Credits text constructor/font arguments differ')
    obj=bytearray(0x124);regs=[0]*32;regs[2]=0x620000;regs[20]=0x630000;regs[29]=0x640000
    result=_run(elf,0x139aa4,WINDOWS,regs,[(0x630000,obj)],0x10e608)
    if (result[4],result[5],int.from_bytes(obj[0x120:0x124],'little'))!=(0x620000,0x640000,0x620000):
        raise ValueError('Credits text setter/buffer forwarding differs')
    return {'constructor_font':22,'constructor_arguments_executed':True,'setter_buffer_forwarding_executed':True,
        'decoded_allocation_request':size,'consumer_size_from_compressed_header':size,
        'limits':'Bounded caller instructions in synthetic RAM; allocation return, object base and stack supplied. Constructor internals, font drawing, scrolling and PCSX2 not executed.'}


def compile_credits(elf,config):
    source_elf,raw,meta,cat=original()
    if elf!=source_elf:raise ValueError('Credits compiler original ELF differs')
    if (set(config)!={'policy','source_sha256','decoded_sha256','instruction_windows','entries'}
        or config['policy']!=POLICY or config['source_sha256']!=sha(raw)
        or config['decoded_sha256']!=meta['decoded_sha256'] or config['instruction_windows']!=bindings(elf)):
        raise ValueError('Credits policy/source/instruction binding differs')
    draft=template(elf,raw,meta,cat)
    editable={r['id']:r for r in draft['rows'] if r['kind']!='preserved-name-company-or-layout'}
    ids=[r['id'] for r in config['entries']]
    if len(ids)!=len(set(ids)) or set(ids)!=set(editable):raise ValueError('Credits recipe must cover all 51 eligible lines exactly once')
    for row in config['entries']:
        if set(row)!={'id','source_sha256','translation'}:raise ValueError('Unknown credits entry field')
        target=editable[row['id']]
        if row['source_sha256']!=target['source_sha256']:raise ValueError('Credits line source hash differs')
        target['translation']=row['translation']
        if not isinstance(row['translation'],str):raise ValueError('Credits translation must be text')
    after,report=rebuild(elf,raw,meta,cat,draft,extra_decoded_bytes=256)
    unchanged=set(editable)-set(report['changed_rows'])
    if unchanged!={'credits.line.0109'} or editable['credits.line.0109']['translation']!='Marketing':
        raise ValueError('Only the common Marketing heading may remain unchanged')
    report.update({'policy':POLICY,'accepted':report['changed_line_count'],
        'preserved_common_terms':sorted(unchanged),'consumer_probe':consumer_probe(elf,report['decoded_size']),
        'instruction_windows':bindings(elf),'runtime_visual_status':'pending_user_verification',
        'font_and_runtime_visual_validation':'Font 22 argument and setter forwarding verified; visual appearance/scrolling pending',
        'iso_modified':False})
    return [{'id':'credits.roles.same-extent-v001','resource':RESOURCE,'offset':0x800,
        'before':raw[0x800:0x1800],'after':after[0x800:0x1800]}],report
