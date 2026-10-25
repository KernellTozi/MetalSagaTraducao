"""Read-only FD_END credits discovery: bounded 1 KiB LZSS, no reinsertion."""
import struct
from dialogue import sha
from glyph_spacing import ORIGINAL_SHA
RESOURCE='DATA/FDATA/FD_END.SDA'
WINDOWS=((0x139074,0x139100),(0x19b6f8,0x19b734),(0x19b780,0x19b910))

def decode(raw,maximum=16*1024*1024):
    if len(raw)<4:raise ValueError('Truncated compressed header')
    size=struct.unpack_from('<I',raw)[0]
    if size>maximum:raise ValueError('Decompressed size exceeds discovery bound')
    dictionary=bytearray(1024);position=1006;at=4;output=bytearray();packets=[]
    def take(n):
        nonlocal at
        if at+n>len(raw):raise ValueError('Truncated compressed token')
        value=raw[at:at+n];at+=n;return value
    while len(output)<size:
        flags=take(1);tokens=[];packets.append({'flags':flags.hex(),'tokens':tokens})
        for bit in range(8):
            if flags[0]>>bit&1:
                token=take(1);length=1;start=None
            else:
                token=take(2);start=token[0]|((token[1]&240)<<4);length=(token[1]&15)+3
            if len(output)+length>size:raise ValueError('Back-reference exceeds declared output')
            tokens.append(token.hex())
            for i in range(length):
                value=token[0] if start is None else dictionary[(start+i)&1023]
                output.append(value);dictionary[position]=value;position=(position+1)&1023
            if len(output)==size:break
    return bytes(output),at,packets

def replay(packets):
    """Replays original token bytes; NOT a compressor for modified text."""
    return b''.join(bytes.fromhex(p['flags'])+b''.join(bytes.fromhex(t) for t in p['tokens']) for p in packets)

def execute_decoder_loop(elf,raw,maximum=16*1024*1024):
    """Original post-memset loop in synthetic RAM; prologue/allocator not executed."""
    if sha(elf)!=ORIGINAL_SHA:raise ValueError('Credits decoder ELF revision differs')
    size=struct.unpack_from('<I',raw)[0]
    if size>maximum:raise ValueError('Credits execution output exceeds bound')
    source=0x610000;destination=0x620000;scratch=0x70003c00
    output=bytearray(size);dictionary=bytearray(1024);regions=[(source,raw),(destination,output),(scratch,dictionary)]
    def access(at,value=None):
        for base,buffer in regions:
            if base<=at<base+len(buffer):
                if value is None:return buffer[at-base]
                if base==source:raise ValueError('Decoder tried to change source')
                buffer[at-base]=value&255;return
        raise ValueError(f'Credits loop escaped bounded memory {at:x}')
    r=[0]*32;r[16]=destination;r[17]=source+4;r[18]=destination+size;r[19]=destination
    pc=0x19b7c4;pending=None
    signed=lambda v:v if v<0x80000000 else v-0x100000000
    for step in range(max(100,200*size)):
        if pc==0x19b8f0:return bytes(output),r[17]-source,step
        if not 0x19b7c4<=pc<0x19b8f0:raise ValueError('Credits loop escaped verified code')
        w=struct.unpack_from('<I',elf,pc)[0];op=w>>26;rs=w>>21&31;rt=w>>16&31;rd=w>>11&31;fn=w&63
        u=w&65535;n=u if u<32768 else u-65536;old=pending;pending=None;nextpc=pc+4
        if op==0:
            if fn==0:r[rd]=r[rt]<<((w>>6)&31)
            elif fn==2:r[rd]=r[rt]>>((w>>6)&31)
            elif fn in (33,45):r[rd]=r[rs]+r[rt]
            elif fn==37:r[rd]=r[rs]|r[rt]
            elif fn==42:r[rd]=int(signed(r[rs])<signed(r[rt]))
            else:raise ValueError('Unsupported credits arithmetic')
        elif op==9:r[rt]=r[rs]+n
        elif op==10:r[rt]=int(signed(r[rs])<n)
        elif op==12:r[rt]=r[rs]&u
        elif op==13:r[rt]=r[rs]|u
        elif op==15:r[rt]=u<<16
        elif op==36:r[rt]=access((r[rs]+n)&0xffffffff)
        elif op==40:access((r[rs]+n)&0xffffffff,r[rt])
        elif op in (4,5,20,21):
            take=r[rs]==r[rt] if op in (4,20) else r[rs]!=r[rt]
            if op in (20,21) and not take:nextpc=pc+8
            else:pending=pc+4+n*4 if take else pc+8
        elif op==1 and rt in (0,1):pending=pc+4+n*4 if (signed(r[rs])<0 if rt==0 else signed(r[rs])>=0) else pc+8
        else:raise ValueError('Unsupported credits opcode')
        r=[v&0xffffffff for v in r];r[0]=0;pc=old if old is not None else nextpc
    raise ValueError('Credits loop step bound')

def analyse(elf,raw):
    if sha(elf)!=ORIGINAL_SHA:raise ValueError('Credits source ELF differs')
    if raw[:4]!=b'sda\0' or struct.unpack_from('<I',raw,8)[0]!=3 or struct.unpack_from('<3I',raw,12)!=(0x800,0x1800,0x1a000):raise ValueError('Credits SDA boundaries differ')
    compressed=raw[0x800:0x1800];out,consumed,packets=decode(compressed)
    actual,original_consumed,steps=execute_decoder_loop(elf,compressed)
    if actual!=out or consumed!=original_consumed or replay(packets)!=compressed[4:consumed]:raise ValueError('Credits decoder/token replay differs')
    if any(compressed[consumed:]):raise ValueError('Nonzero credits tail requires investigation')
    count=struct.unpack_from('<I',out)[0]
    if not out.endswith(b'\r\n'):raise ValueError('Credits have no terminal CRLF')
    rows=out[4:-2].split(b'\r\n')
    if len(rows)!=count or any(b'\r' in r or b'\n' in r for r in rows):raise ValueError('Credits line count/CRLF mismatch')
    metadata={'resource':RESOURCE,'source_sha256':sha(raw),'entry':0,'slot_offset':0x800,'slot_size':4096,
        'compressed_bytes_consumed':consumed,'original_zero_tail_bytes':4096-consumed,'decoded_size':len(out),'decoded_sha256':sha(out),
        'declared_lines':count,'crlf_lines':len(rows),'nonempty_lines':sum(bool(r.strip()) for r in rows),
        'non_ascii_line_count':sum(any(b>=128 for b in r) for r in rows),
        'non_ascii_byte_values':[f'{v:02x}' for v in sorted(set(out[4:])) if v>=128],
        'dictionary_size':1024,'initial_dictionary_position':1006,'dictionary_initialization':'zero',
        'literal_flag':'LSB first, 1=literal','backref':'low byte + high nibble <<4, dictionary index wraps &1023, length low nibble+3',
        'original_decoder_loop_executed':True,'original_decoder_steps':steps,'token_replay_roundtrip':True,
        'instruction_windows':[{'offset':a,'size':z-a,'sha256':sha(elf[a:z])} for a,z in WINDOWS],
        'consumer':'FD_END entry 0 -> 0x19B6F8 allocation wrapper -> 0x19B780 decoder; 0x1390E0 reads first decoded u32 as row count',
        'editing_authorized':False,'recompressor_implemented':False,'pcsx2_executed':False,
        'pending':['Prove credits row renderer/control bytes before editing','Implement tested same-slot recompressor','Preserve staff names, row count, layout and unknown bytes'],
        'limits':'Only original post-memset decoder loop executed; dictionary initialized by harness, allocator/prologue/renderer/PS2 not executed. Token replay is not reinsertion of edited text.'}
    return metadata,{'decoded_hex':out.hex(),'rows':[{'id':f'credits.line.{i:04d}','row':i,'source_hex':r.hex(),'source_sha256':sha(r),'ascii_preview':r.decode('ascii','backslashreplace')} for i,r in enumerate(rows)],'original_token_packets':packets}
