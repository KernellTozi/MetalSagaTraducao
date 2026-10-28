"""Four proven name-entry literals; fixed ASCII slots amid immutable native bytes."""
import re
from interface_graphics import sha
from glyph_spacing import ORIGINAL_SHA

POLICY = 'name-entry-fixed-literals-v001'
OFFSETS = (0x33b3b8, 0x32a310, 0x32a348, 0x32a380)
WINDOWS = ((0x177780, 0x177810, 'cdd1367c3b7cdb7aa3ffcd9bcb458712d0b220c09d8e9967ff74f1e05eca5c17'),
           (0x10b368, 0x10b3a0, '7a3b6239e7177ad215860b55e39ca243e782581ad2f308af3831a417529982d1'),
           (0x10a980, 0x10aa80, 'd19524783c93c6fe591eff3daa257632229fb0d74b2960f447af1d862428c2f0'),
           (0x10e608, 0x10e6e0, 'd6f3d7b36d079e19c503ecdf9ebde758e737f2c4eb7bba43c5f7c6d56fa43823'))


def catalog(elf):
    if sha(elf) != ORIGINAL_SHA:
        raise ValueError('Name entry ELF revision mismatch')
    for a, z, expected in WINDOWS:
        if sha(elf[a:z]) != expected:
            raise ValueError('Name entry consumer changed')
    from interface_text import references,sections
    refs=references(elf,sections(elf))
    rows = []
    for offset in OFFSETS:
        end = elf.index(0, offset)
        raw = elf[offset:end]
        if len(raw) > 128:
            raise ValueError('Name entry literal boundary mismatch')
        if any(offset+0xff000+i in refs for i in range(1,len(raw))):
            raise ValueError('Name entry has an unreviewed interior alias')
        slots = [{'offset': m.start(), 'size': len(m.group()), 'source_sha256': sha(m.group())}
                 for m in re.finditer(rb'[A-Z]+', raw)] if offset != OFFSETS[0] else []
        rows.append({'id': f'name-entry.{offset:08x}', 'offset': offset, 'size': len(raw),
                     'source_sha256': sha(raw), 'kind': 'heading' if offset == OFFSETS[0] else 'legend',
                     'slots': slots})
    return rows


def compile_name_entry(elf, config):
    from name_back_command import POLICY as BACK_POLICY,proof as back_proof
    from interface_gaps import TITLE_POLICY,title_proof
    if config.get('policy') not in (POLICY,BACK_POLICY,TITLE_POLICY):
        raise ValueError('Unknown name entry policy')
    back=None
    if config['policy'] in (BACK_POLICY,TITLE_POLICY):back=back_proof(elf,config['back_evidence'])
    elif 'back_evidence' in config:raise ValueError('Historic name policy cannot release BACK')
    title=None
    if config['policy']==TITLE_POLICY:
        title=title_proof(elf)
        if config.get('title_evidence')!=title:raise ValueError('Name exit evidence differs')
    elif 'title_evidence' in config:raise ValueError('Historic name policy cannot release TITLE')
    rows = catalog(elf)
    targets = config.get('entries', [])
    if len(targets) != len(rows):
        raise ValueError('Name entry literal set changed')
    patches, reports = [], []
    for row, target in zip(rows, targets):
        if target.get('id') != row['id'] or target.get('source_sha256') != row['source_sha256']:
            raise ValueError('Name entry binding/order mismatch')
        start, size = row['offset'], row['size']
        before = elf[start:start+size]
        after = bytearray(before)
        if row['kind'] == 'heading':
            if set(target) != {'id', 'source_sha256', 'translation'}:
                raise ValueError('Unknown heading metadata')
            text = target['translation']
            if text != 'DIGITE SEU NOME':
                raise ValueError('Unreviewed name heading')
            encoded = text.encode('ascii')
            if len(encoded) > size:
                raise ValueError('Name heading overflow')
            after[:] = encoded+bytes(size-len(encoded))
        else:
            if set(target) != {'id', 'source_sha256', 'slots'} or len(target['slots']) != len(row['slots']):
                raise ValueError('Name legend slot topology changed')
            reviewed = {b'INPUT': 'INS.', b'SELECT': 'SEL.', b'END': 'FIM',
                        b'CANCEL': 'CANC.', b'DELETE': 'APAGAR', b'TITLE': 'TITLE', b'BACK': 'BACK'}
            if back:reviewed[b'BACK']='VOL.'
            if title:reviewed[b'TITLE']='SAIR'
            for slot, replacement in zip(row['slots'], target['slots']):
                a, n = slot['offset'], slot['size']
                if set(replacement) != {'offset', 'size', 'source_sha256', 'translation'}:
                    raise ValueError('Unknown name legend slot metadata')
                if any(replacement.get(k) != slot[k] for k in slot):
                    raise ValueError('Name legend slot offset/size/hash changed')
                text = replacement['translation']
                if text != reviewed.get(before[a:a+n]):
                    raise ValueError('Unreviewed name legend translation')
                value = text.encode('ascii')
                if not value or len(value) > n:
                    raise ValueError('Name legend slot overflow')
                after[a:a+n] = value.ljust(n, b' ')
            authorized = {i for slot in row['slots'] for i in range(slot['offset'], slot['offset']+slot['size'])}
            if any(a != b and i not in authorized for i, (a, b) in enumerate(zip(before, after))):
                raise ValueError('Native name legend bytes/spacing changed')
        if len(after) != len(before):
            raise ValueError('Name literal resized')
        patches.append({'resource': 'SLUS_212.93', 'id': row['id'], 'offset': start,
                        'before': before+b'\0', 'after': bytes(after)+b'\0'})
        reports.append({**row, 'target_sha256': sha(after), 'changed_bytes': sum(a != b for a, b in zip(before, after))})
    return patches, {'policy': config['policy'], 'accepted': len(rows), 'results': reports,
                     'native_bytes_and_slot_offsets_unchanged': True,
                     'runtime_visual_status': 'pending_user_verification',
                     'pending_command_semantics': [] if title else ['TITLE'] if back else ['TITLE', 'BACK'],
                     **({'back_navigation':back} if back else {}),
                     **({'title_exit':title} if title else {}),
                     'instruction_windows': [{'offset': a, 'size': z-a, 'sha256': h} for a, z, h in WINDOWS]}
