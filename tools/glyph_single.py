"""PT-BR metrics for the separate single-character drawing path.

Keep the original accented code for cache lookup; map to the base only AFTER
that call, so native per-letter layout can run without changing the bitmap.
Requires the bound v004 layout table in the adjacent function.
"""
import hashlib
import struct
from glyph_spacing import ORIGINAL_SHA,DELTA
from glyph_layout import BASES,elf_patch as adjacent_patch
START=0x3e2e0
END=0x3e520


def replacement(before,table_address):
    words=[];labels={};fixups=[]
    def mark(n):labels[n]=START+DELTA+4*len(words)
    def emit(w):words.append(w)
    def imm(op,rs,rt,n):emit(op<<26|rs<<21|rt<<16|(n&65535))
    def reg(rs,rt,rd,fn,sa=0):emit(rs<<21|rt<<16|rd<<11|sa<<6|fn)
    def branch(op,rs,rt,label):fixups.append((len(words),label));imm(op,rs,rt,0)
    def copy(a,b):
        for at in range(a,b,4):
            mark(at);w=struct.unpack_from('<I',before,at-START)[0]
            if w>>26 in (1,4,5,6,7,20,21,22,23):
                n=w&65535;n=n if n<32768 else n-65536
                fixups.append((len(words),at+4+n*4))
            emit(w)
    copy(START,0x3e394)
    imm(13,0,2,0x8240);reg(17,2,2,35);imm(11,2,3,15)
    branch(5,3,0,'map');emit(0)
    imm(9,2,2,-25);imm(11,2,3,3)
    branch(4,3,0,0x3e394);imm(9,2,2,15)
    mark('map')
    imm(15,0,3,(table_address+0x8000)>>16);imm(9,3,3,table_address)
    reg(3,2,3,33);imm(36,3,17,0)
    reg(0,19,20,3,1);imm(9,0,30,2)
    copy(0x3e394,0x3e3c0)
    mark(0x3e3c0)
    imm(9,17,3,-0x41);imm(11,3,2,26)
    branch(5,2,0,'letter');imm(15,0,6,0x41)
    imm(9,17,3,-0x61);imm(11,3,2,26)
    branch(4,2,0,0x3e444);imm(9,0,2,0x20)
    imm(9,3,3,26)
    mark('letter')
    branch(5,19,4,'large');reg(0,3,3,0,1)
    imm(9,6,6,0x5830);branch(4,0,0,'ready');emit(0)
    mark('large');imm(9,6,6,0x5898)
    mark('ready');reg(6,3,4,33);imm(32,4,16,1)
    branch(4,0,0,0x3e4a8);imm(32,4,5,0)
    copy(0x3e444,0x3e51c) # unchanged drawing, return, restore registers
    for i,target in fixups:
        destination=labels[target];d=(destination-(START+DELTA+i*4+4))//4
        if not -32768<=d<=32767:raise ValueError('Branch out of range')
        words[i]=(words[i]&0xffff0000)|(d&65535)
    result=struct.pack('<'+'I'*len(words),*words)
    if len(result)>END-START:raise ValueError('Single-character function overflows')
    return result+bytes(END-START-len(result))


def elf_patch(data):
    if hashlib.sha256(data).hexdigest()!=ORIGINAL_SHA:raise ValueError('ELF revision mismatch')
    adjacent=adjacent_patch(data)
    table=bytes(BASES[k] for k in sorted(BASES))
    offset=adjacent['after'].find(table)
    if offset<0 or adjacent['after'].count(table)!=1:raise ValueError('Adjacent mapping table not unique')
    before=data[START:END]
    return {'offset':START,'before':before,'after':replacement(before,adjacent['offset']+DELTA+offset)}
