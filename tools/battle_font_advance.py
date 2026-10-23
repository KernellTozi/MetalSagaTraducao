"""Opt-in battle text advance for exactly the 18 project character pairs.

Keep both input bytes and the original glyph dispatch; only the horizontal step
becomes the existing ASCII half-cell. Rebuild inside the original allocation.
"""
import struct
from glyph_spacing import ORIGINAL_SHA,DELTA
from interface_graphics import sha

START=0x8c0b8
END=0x8c2e0
WINDOW_SHA='a575ded23c980e6ae560cdb580e55f047cfc973620a2bc5ea8d5d6c2a2fe2958'
POLICY='battle-ptbr-half-cell-advance-v001'


def replacement(before):
    words=[];labels={};fixups=[]
    def mark(name):labels[name]=START+DELTA+len(words)*4
    def emit(w):words.append(w)
    def imm(op,rs,rt,n):emit(op<<26|rs<<21|rt<<16|(n&65535))
    def branch(op,rs,rt,label):fixups.append((len(words),label));imm(op,rs,rt,0)
    for at in range(START,END,4):
        if at==0x8c284:
            labels[at]=labels[0x8c220]
        elif not 0x8c270<at<0x8c2a4:
            mark(at)
        if at==0x8c270:
            branch(4,0,0,0x8c20c);emit(0)
        if at in (0x8c11c,0x8c130,0x8c1b8,0x8c1bc) or 0x8c270<=at<0x8c2a4:
            continue
        if at==0x8c198:
            # s2 points at the trail byte; s1 retains that byte across both calls.
            imm(36,18,2,-1);imm(14,2,2,0x82)
            branch(5,2,0,'full');imm(9,17,2,-0x40)
            imm(11,2,3,15);branch(5,3,0,0x8c220);imm(9,2,2,-25)
            imm(11,2,2,3);branch(5,2,0,0x8c220);emit(0)
            mark('full')
        w=struct.unpack_from('<I',before,at-START)[0]
        if at==0x8c118:w=(w&0xffff0000)|((-0x81)&65535)
        if at==0x8c12c:w=(w&0xffff0000)|((-0xe0)&65535)
        if w>>26 in (1,4,5,6,7,20,21,22,23):
            n=w&65535;n=n if n<32768 else n-65536
            fixups.append((len(words),at+4+n*4))
        emit(w)
        if at==0x8c0e4:
            imm(15,0,1,0x3f00);emit(0x4481a000) # mtc1 at,f20 (saved immediately before)
    for i,target in fixups:
        if target not in labels:raise ValueError(f'Unknown battle branch target {target}')
        displacement=(labels[target]-(START+DELTA+i*4+4))//4
        if not -32768<=displacement<=32767:raise ValueError('Battle branch out of range')
        words[i]=(words[i]&0xffff0000)|(displacement&65535)
    result=struct.pack('<'+'I'*len(words),*words)
    if len(result)>END-START:raise ValueError('Battle function overflow')
    return result+bytes(END-START-len(result)),labels


def elf_patch(elf,config):
    if config!={'policy':POLICY,'source_sha256':ORIGINAL_SHA,'window_sha256':WINDOW_SHA}:
        raise ValueError('Battle advance recipe binding mismatch')
    if sha(elf)!=ORIGINAL_SHA or sha(elf[START:END])!=WINDOW_SHA:
        raise ValueError('Battle advance original function mismatch')
    after,_=replacement(elf[START:END])
    return {'resource':'SLUS_212.93','id':'battle.ptbr-advance','offset':START,'before':elf[START:END],'after':after}
