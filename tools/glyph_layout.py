"""PT-BR layout extension: reuse native ASCII metrics, retain original glyph code.

Original function stays within its 824-byte allocation. The duplicate 19px
lowercase metric conversion reuses the identical uppercase conversion body.
"""
import hashlib
import struct
import unicodedata
from gfi import CHAR_TO_BYTES
from glyph_spacing import ORIGINAL_SHA,DELTA

START=0x3e520
END=0x3e858
WINDOW_SHA='f41beaffa20879e2fd90490dc354df14902202fa967b2fd4a80c91c1dc9d699a'
BASES={int.from_bytes(v,'big'):ord(unicodedata.normalize('NFD',k)[0]) for k,v in CHAR_TO_BYTES.items()}


def replacement(original):
    words=[];labels={};fixups=[]
    def here():return START+DELTA+4*len(words)
    def emit(w):words.append(w)
    def mark(name):labels[name]=here()
    def imm(op,rs,rt,n):emit(op<<26|rs<<21|rt<<16|(n&65535))
    def reg(rs,rt,rd,fn,shift=0):emit(rs<<21|rt<<16|rd<<11|shift<<6|fn)
    def branch(op,rs,rt,label):fixups.append((len(words),'branch',label));imm(op,rs,rt,0)
    def jump(label):fixups.append((len(words),'jump',label));emit(2<<26)
    def copy(a,b):
        for at in range(a,b,4):
            mark(at)
            w=struct.unpack_from('<I',original,at-START)[0];op=w>>26
            if op in (4,5,6,7,20,21,22,23):
                n=w&65535;n=n if n<32768 else n-65536
                fixups.append((len(words),'branch',at+4+n*4))
            words.append(w)
    copy(START,0x3e568) # original prologue, classifier call and delay
    branch(1,2,1,'ascii');imm(35,17,3,0) # bgez v0; common pointer read
    imm(36,3,2,0);imm(36,3,5,1);reg(0,2,2,0,8);reg(2,5,21,37)
    imm(9,3,3,2);imm(43,17,3,0);imm(43,29,21,0x08)
    imm(13,0,2,0x8240);reg(21,2,2,35);imm(11,2,3,15)
    branch(5,3,0,'mapped');emit(0)
    imm(9,2,2,-25);imm(11,2,3,3)
    branch(4,3,0,'native');imm(9,2,2,15)
    mark('mapped')
    # Local table address, bound inside this function allocation.
    fixups.append((len(words),'table_hi','table'));imm(15,0,3,0)
    fixups.append((len(words),'table_lo','table'));imm(9,3,3,0)
    reg(3,2,3,33);imm(36,3,21,0)
    jump('half');emit(0)
    mark('native')
    imm(43,18,16,0);imm(43,22,0,0);imm(43,20,0,0)
    jump('finish');imm(43,19,16,0)
    mark('ascii')
    imm(36,3,21,0);imm(9,3,3,1);imm(43,17,3,0);imm(43,29,21,0x08)
    mark('half')
    reg(0,16,4,3,1);imm(9,0,5,2);imm(9,0,6,1)
    imm(43,18,4,0);imm(43,22,5,0);imm(43,20,0,0);imm(43,19,4,0)
    # Keep native ASCII letters/punctuation logic byte-for-byte apart from
    # relocated internal branches. Convert early returns into common finish.
    copy(0x3e5cc,0x3e720)
    mark(0x3e720)
    branch(4,0,0,0x3e658);imm(9,3,3,26) # lower table = upper table + 52
    copy(0x3e790,0x3e82c)
    mark(0x3e82c);mark(0x3e830);mark('finish')
    imm(35,29,2,0x08) # original code, NOT the base used for metrics
    copy(0x3e830,END)
    # copy() overwrites old 830 mapping; redirect all original early exits.
    labels[0x3e830]=labels['finish']
    mark('table')
    table=bytes(BASES[k] for k in sorted(BASES));table+=bytes((-len(table))%4)
    words.extend(struct.unpack('<'+'I'*(len(table)//4),table))
    for i,kind,target in fixups:
        dest=labels[target]
        if kind=='branch':
            displacement=(dest-(START+DELTA+i*4+4))//4
            if not -32768<=displacement<=32767:raise ValueError('Branch out of range')
            words[i]=(words[i]&0xffff0000)|(displacement&65535)
        elif kind=='jump':words[i]|=(dest>>2)&0x3ffffff
        elif kind=='table_hi':words[i]|=((dest+0x8000)>>16)&65535
        else:words[i]|=dest&65535
    code=struct.pack('<'+'I'*len(words),*words)
    if len(code)>END-START:raise ValueError(f'Layout exceeds native function: {len(code)} bytes')
    return code+bytes(END-START-len(code))


def elf_patch(data):
    if hashlib.sha256(data).hexdigest()!=ORIGINAL_SHA:raise ValueError('ELF revision mismatch')
    before=data[START:END]
    if hashlib.sha256(before).hexdigest()!=WINDOW_SHA:raise ValueError('Layout function differs')
    return {'offset':START,'before':before,'after':replacement(before)}
