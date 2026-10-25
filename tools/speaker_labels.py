"""Opt-in, source-bound generic role labels; legacy dialogue labels stay protected."""
import copy,struct
from dialogue import sha
from gfi import encode,decode,BYTES_TO_CHAR

POLICY='map-generic-speaker-label-fixed-slots-v001'
# Authored roles only. Proper names, factions, Hunter/Soldier/Punk and markers
# are deliberately absent. Full natural targets may be deferred by byte budget.
ROLES={
 'Control System':'Sistema','Announcement':'Aviso','Agent':'Agente',
 'Bar Patrons':'Clientes','Innkeeper':'Hospedaria','Inn Keeper':'Hospedaria',
 'Old Woman':'Idosa','Man on the Run':'Fugitivo','Man On the Run':'Fugitivo',
 'Railroad Staff':'Ferroviário','Repair Shop':'Oficina','Guard':'Guarda',
 'Mechanic':'Mecânico','Miner':'Mineiro','Equipment Shop':'Equipamentos',
 'Item Shop':'Loja geral','Bartender':'Barman','Part Shop':'Autopeças',
 'Assembly Shop':'Montadora','Gift Shop':'Presentes','Woman':'Mulher',
 'Old Man':'Idoso','Old man':'Idoso','Rich Daughter':'Filha rica','Rich Son':'Filho rico',
 'Apprentice Mechanic':'Aprendiz mecânico','Receptionist':'Recepcionista',
 'Manager':'Gerente','Station Staff':'Ferroviário','Traveler':'Viajante',
 "Banjo's Wife":'Esposa de Banjo','Middle-aged Hunter':'Hunter maduro',
 'Leader':'Líder','Rich Old Man':'Idoso rico','Note':'Bilhete','Waitress':'Garçonete',
 'Lady':'Senhora','Rich Kid':'Riquinho','Rich Dad':'Pai rico','Intercom':'Interfone',
 'Girl':'Garota','Attendant':'Atendente','Riffraff':'Gentalha','Rich Man':'Homem rico',
 'Rich Madam':'Dama rica','Seasonal Worker':'Temporário','Seasonal Work':'Temporário',
 'Passenger':'Passageiro','Ticket Seller':'Bilheteiro','Worker A':'Operário A',
 'Worker B':'Operário B','Worker C':'Operário C','Brigand':'Bandido',
 'New Recruit':'Recruta','Guy and Girl':'Rapaz e moça','Young Man':'Rapaz',
 'Middle-aged Man':'Homem maduro','Vulgar Man':'Grosseiro','Grumpy Old Man':'Idoso rabugento',
 'Housewife':'Dona do lar','Dowan Merchant':'Mercador Dowan',
 'Lorelei Merchant':'Mercador Lorelei','Member A':'Membro A',
 'Well Dressed Man':'Homem elegante','Man in a suit':'Homem de terno',
 'Military Dude':'Militar','Young Father':'Pai jovem','Young Mother':'Mãe jovem',
 'Scrap Shopkeeper':'Sucateiro','Medal Collector':'Caça-medalhas',
 'Regular Customer':'Cliente habitual','Mod Shop Apprentice':'Aprendiz de tuning',
 'Man':'Homem','Guy':'Rapaz','Cat':'Gato','Dog':'Cão','Worker':'Trabalhador',
 'Transporter':'Transportador','Trader':'Mercador','Stern Mechanic':'Mecânico severo',
 'Maintenance Man':'Técnico de manutenção','Cook':'Cozinheiro','PA System':'Alto-falante',
 'Elder ':'Ancião ',
}
WINDOWS=((0x1c6508,0x1c6554),(0x1c6db0,0x1c6de8),(0x1fd968,0x1fda40),
 (0x1fdb00,0x1fdb44),(0x2265b4,0x2265c8),(0x2266ac,0x2266d8),(0x2267f0,0x226810))

def bindings(elf):
    from glyph_spacing import ORIGINAL_SHA
    if sha(elf)!=ORIGINAL_SHA:raise ValueError('Speaker-label ELF revision differs')
    return [{'offset':a,'size':z-a,'sha256':sha(elf[a:z])} for a,z in WINDOWS]

def _run(elf,start,windows,regs,regions,stop):
    """Small integer interpreter for the inspected allocation/copy/getter paths.

    PCs/RA use file offsets. No allocator, cleanup, aligned SIMD or rendering.
    """
    def access(at,size,value=None):
        for base,raw in regions:
            if base<=at and at+size<=base+len(raw):
                off=at-base
                if value is None:return int.from_bytes(raw[off:off+size],'little')
                raw[off:off+size]=(value&((1<<(size*8))-1)).to_bytes(size,'little');return
        raise ValueError(f'Speaker probe outside supplied memory {at:x}')
    pc=start;pending=None
    for _ in range(10000):
        if pc==stop:return regs
        if not any(a<=pc<z for a,z in windows):raise ValueError(f'Speaker probe escaped code {pc:x}')
        w=struct.unpack_from('<I',elf,pc)[0];op=w>>26;rs=w>>21&31;rt=w>>16&31;rd=w>>11&31;fn=w&63
        u=w&65535;n=u if u<32768 else u-65536;old=pending;pending=None;nextpc=pc+4
        if op==0:
            if fn==0:regs[rd]=regs[rt]<<((w>>6)&31)
            elif fn in (33,45):regs[rd]=regs[rs]+regs[rt]
            elif fn==36:regs[rd]=regs[rs]&regs[rt]
            elif fn==37:regs[rd]=regs[rs]|regs[rt]
            elif fn==8:pending=regs[rs]
            else:raise ValueError('Unsupported speaker integer opcode')
        elif op==9:regs[rt]=regs[rs]+n
        elif op==12:regs[rt]=regs[rs]&u
        elif op==13:regs[rt]=regs[rs]|u
        elif op==15:regs[rt]=u<<16
        elif op in (35,36,55):regs[rt]=access((regs[rs]+n)&0xffffffff,{35:4,36:1,55:8}[op])
        elif op in (40,43):access((regs[rs]+n)&0xffffffff,1 if op==40 else 4,regs[rt])
        elif op==5:pending=pc+4+n*4 if regs[rs]!=regs[rt] else pc+8
        elif op==3:regs[31]=pc+8;pending=((w&0x3ffffff)<<2)-0xff000
        else:raise ValueError('Unsupported speaker probe opcode')
        regs=[r&0xffffffff for r in regs];regs[0]=0;pc=old if old is not None else nextpc
    raise ValueError('Speaker probe step limit')

def probe(elf,raw):
    from spack_ui import execute_byte_length
    if not raw or b'\0' in raw:raise ValueError('Invalid probe string')
    length=execute_byte_length(elf,raw)
    if length!=len(raw):raise ValueError('Speaker strlen mismatch')
    regs=[0]*32;regs[2]=length
    arena=bytearray(struct.pack('<I',0x680000))
    regs=_run(elf,0x1fd9e0,WINDOWS,regs,[(0x4842e4,arena)],0x1a61e0)
    size=regs[4]
    if (size,regs[5],regs[6])!=((length+4)&~3,0x680000,16):raise ValueError('Speaker allocation arguments differ')
    # Stub allocation; resume the original setter through strcpy call/delay slot.
    obj=bytearray(0x40);source=bytearray(raw+b'\0');dest=bytearray(b'\xa5'*size+b'GUARD')
    regs[2]=0x650001;regs[17]=0x630000;regs[18]=0x640003
    regions=[(0x630000,obj),(0x640003,source),(0x650001,dest)]
    regs=_run(elf,0x1fda18,WINDOWS,regs,regions,0x2265b4)
    if (regs[4],regs[5],struct.unpack_from('<I',obj,0x34)[0])!=(0x650001,0x640003,0x650001):raise ValueError('Speaker setter arguments differ')
    regs[31]=0x700000
    copied=_run(elf,0x2265b4,WINDOWS,regs,regions,0x700000)
    if copied[2]!=0x650001 or dest[:length+1]!=raw+b'\0' or dest[length+1:]!=b'\xa5'*(size-length-1)+b'GUARD' or source!=raw+b'\0':raise ValueError('Speaker copy/guards differ')
    stack=bytearray(struct.pack('<Q',0x700000)+bytes(8));regs=[0]*32;regs[4]=0x630000;regs[29]=0x660000
    result=_run(elf,0x1fdb00,WINDOWS,regs,[(0x630000,obj),(0x660000,stack)],0x700000)
    if result[2]!=0x650001:raise ValueError('Speaker static getter differs')
    return {'bytes':length,'allocated_bytes':size,'copy_and_guards':True,'static_getter':True}

def validate_label(source,target,capacity):
    from translation_policy import validate
    if source not in ROLES or target!=ROLES[source]:raise ValueError('Unreviewed speaker role/target')
    raw=encode(target)
    if any(c in raw for c in (0,9,10,13,37)) or decode(raw)!=target:raise ValueError('Speaker delimiter/codec mismatch')
    if len(raw)>capacity:raise ValueError('Speaker label exceeds original slot')
    if validate(source,target):raise ValueError('Speaker terminology mismatch: '+repr(validate(source,target)))
    return raw

def overlay(data,document,patches,report,config,elf,preserved=()):
    """Merge exact fixed-slot label deltas into already validated body patches.

    Build a private copy first. Return no changes on any exception; the core
    compiler's protected labels, extraction fingerprints and old policies stay.
    """
    if not report['valid'] or config.get('policy')!=POLICY:raise ValueError('Invalid speaker overlay policy/base')
    if config.get('instruction_windows')!=bindings(elf):raise ValueError('Speaker instruction binding mismatch')
    doc=copy.deepcopy(document);rep=copy.deepcopy(report);out={p['id']:dict(p) for p in patches}
    by_id={e['id']:e for e in doc['entries']};results={r['id']:r for r in rep['results']}
    seen=set();rows=[];roles=set();new_records=0
    for item in config['entries']:
        key=item['id']
        if key in seen or key in preserved:raise ValueError('Duplicate/protected speaker record')
        seen.add(key);entry=by_id[key]
        family=bytes.fromhex(entry['tag'])
        if family not in (b'msgn',b'smnn',b'2snm') or entry['mode']!='slots' or entry['blocked_reasons']:raise ValueError('Ineligible speaker record')
        labels=[s for s in entry['segments'] if s['key']=='label']
        if len(labels)!=1 or labels[0]['editable']:raise ValueError('Speaker label metadata mismatch')
        label=labels[0];original=bytes(data[entry['offset']:entry['offset']+entry['size']]);src=bytes.fromhex(label['source_hex'])
        if (sha(original),sha(src))!=(item['record_sha256'],item['label_sha256']) or sha(original)!=entry['record_sha256']:raise ValueError('Speaker source binding mismatch')
        if src.decode('ascii')!=label['source'] or label['translation']!=label['source']:raise ValueError('Speaker source text mismatch')
        raw=validate_label(label['source'],item['translation'],label['capacity']);evidence=probe(elf,raw)
        prior=out.get(key);base=prior['after'] if prior else original
        if prior and prior['before']!=original:raise ValueError('Speaker base patch source differs')
        start=label['offset']-entry['offset'];end=start+label['capacity']+1
        if not 0<=start<end<=len(original) or base[start:end]!=original[start:end] or original[start:end]!=src+bytes(end-start-len(src)):raise ValueError('Speaker slot/padding changed before overlay')
        after=base[:start]+raw+bytes(end-start-len(raw))+base[end:]
        if after[:start]!=base[:start] or after[end:]!=base[end:] or len(after)!=len(original):raise ValueError('Speaker escaped slot')
        # Reparse the whole record with the same codec-neutral structural shadow
        # used by the main compiler. Do not alter parser/metadata fingerprints.
        shadow=bytearray(after)
        for s in entry['segments']:
            at=s['offset']-entry['offset'];value=after[at:].split(b'\0',1)[0];i=0
            while i<len(value):
                if value[i:i+2] in BYTES_TO_CHAR:shadow[at+i:at+i+2]=b'aa';i+=2
                else:i+=1
        if family==b'msgn':
            from dialogue_formats import parse_msgn
            parsed,_=parse_msgn(shadow,0);offsets=[parsed['text_offset'],parsed['display_label']['text_offset']]
        else:
            from dialogue_advanced import parse as parse_advanced
            _,parsed=parse_advanced(shadow,0);offsets=[s['text_offset'] for s in parsed['segments']]
        if offsets!=[s['offset']-entry['offset'] for s in entry['segments']]:raise ValueError('Speaker structural round-trip differs')
        label['translation']=item['translation'];roles.add(label['source'])
        out[key]={'resource':document['resource'],'offset':entry['offset'],'before':original,'after':after,'id':key}
        row=results[key]
        if row['status']=='unchanged':
            new_records+=1;row.update(status='accepted',mode='slots',warnings=[],record_offset=entry['offset'],record_size=entry['size'],block_offset=entry['block_offset'],visual_status='pending_manual_validation')
        elif row['status']!='accepted':raise ValueError('Refused speaker base record')
        row.update(source_lengths=[len(bytes.fromhex(s['source_hex'])) for s in entry['segments']],
            target_lengths=[len(encode(s['translation'])) for s in entry['segments']],
            source_capacities=[s['capacity'] for s in entry['segments']],
            source_offsets=[s['offset'] for s in entry['segments']],target_offsets=[s['offset'] for s in entry['segments']],speaker_label_changed=True)
        rows.append({'id':key,'offset':label['offset'],'capacity':label['capacity'],'target_sha256':sha(raw),**evidence})
    if not rows:raise ValueError('Empty speaker overlay')
    compiled=sorted(out.values(),key=lambda p:p['offset'])
    if any(a['offset']+len(a['before'])>b['offset'] for a,b in zip(compiled,compiled[1:])):raise ValueError('Speaker patches overlap')
    doc['speaker_label_policy']=POLICY
    rep.update(accepted=len(compiled),unchanged=len(doc['entries'])-len(compiled),requires_ptbr_fonts=True)
    rep['speaker_labels']={'policy':POLICY,'accepted':len(rows),'distinct_roles':len(roles),'new_changed_records':new_records,
        'instruction_windows':bindings(elf),'results':rows,'legacy_labels_remain_protected':True,
        'pcsx2_executed':False,'runtime_visual_status':'pending_user_verification',
        'probe_limits':'Original scalar strlen, allocation arguments, setter forwarding, unaligned scalar strcpy and nonzero-label getter executed in synthetic memory; allocator stubbed; cleanup, aligned SIMD, drawing and portraits not executed'}
    return doc,compiled,rep
