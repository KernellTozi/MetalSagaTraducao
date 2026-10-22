"""v003: bounded SSD instruction streams and renderer-backed text layouts."""
import bisect
import collections
import re
import struct
from dialogue import instruction, sha
from dialogue_formats import native_text, tokens

# Header sizes follow loader parameter counts; string counts are strict per tag.
LAYOUTS = {b'smsg':(40,2), b'sel\0':(16,1), b'smnn':(40,3),
           b'2smg':(48,2), b'2snm':(48,3), b'2sel':(24,1),
           b'msgb':(24,1), b'supr':(48,1), b'MC\0\0':(24,1),
           b'SP\0\0':(32,1), b'ST\0\0':(32,1)}


class SsdIndex:
    def __init__(self,data):
        self.blocks=[]; self.records={}; self.errors=[]
        for match in re.finditer(rb'ssd\x00\x69\x04\x00\x00',data):
            at=match.start()
            if at%4 or at+12>len(data):continue
            size=struct.unpack_from('<I',data,at+8)[0]; end=at+size
            if size<12 or size%4 or end>len(data):
                self.errors.append({'offset':at,'reason':'Invalid SSD size'});continue
            pos=at+12; records=[]
            try:
                while pos<end:
                    item=instruction(data,pos)
                    if pos+item['size']>end:raise ValueError('Instruction crosses SSD end')
                    records.append(item);pos+=item['size']
            except ValueError as error:
                self.errors.append({'offset':at,'reason':str(error)});continue
            self.blocks.append({'offset':at,'end':end,'size':size,'instruction_count':len(records)})
            for ordinal,item in enumerate(records):
                if item['offset'] in self.records:raise ValueError('Overlapping SSD instruction streams')
                self.records[item['offset']]={'block_offset':at,'block_end':end,
                                               'ordinal':ordinal,'instruction':item}
        self.starts=[b['offset'] for b in self.blocks]
        for a,b in zip(self.blocks,self.blocks[1:]):
            if a['end']>b['offset']:raise ValueError('Overlapping SSD blocks')

    def footer(self,at,size=4):
        i=bisect.bisect_right(self.starts,at)-1
        if i<0:return None
        block=self.blocks[i]
        if block['end']<=at<block['end']+12:
            return {'block_offset':block['offset'],'block_end':block['end'],
                    'relative_offset':at-block['end'], 'claimed_size':size,
                    'reason':'Signature outside declared SSD instruction stream; inside 12-byte adjacent region'}
        return None


def parse(data,at):
    info=instruction(data,at);tag=bytes(data[at:at+4]);header,count=LAYOUTS[tag]
    if info['size']<header+4:raise ValueError('Short advanced text record')
    body=data[at+header:at+info['size']];pos=0;segments=[];opaque=False;native=False
    for number in range(count):
        start=pos;end=body.find(b'\0',start)
        if end<=start:raise ValueError('Empty/missing advanced text string')
        raw=body[start:end];source,spans=native_text(raw);control,unknown=tokens(raw)
        opaque|=unknown; native|=bool(spans)
        pos=end+1
        while pos<len(body) and body[pos]==0:pos+=1
        segments.append({'number':number,'text_offset':at+header+start,'relative_offset':start,
                         'source':source,'translation':source,'original_text_hex':raw.hex(),
                         'zero_count':pos-end,'control_tokens':control,'native_spans':spans})
    if pos!=len(body):raise ValueError('Unexpected additional advanced payload')
    item={**info,'id':f'map.{tag.rstrip(bytes(1)).decode("ascii")}.{at:08x}',
          'profile':'renderer-text-v3','header_size':header,'header_hex':data[at:at+header].hex(),
          'record_sha256':sha(data[at:at+info['size']]),'source':segments[0]['source'],
          'translation':segments[0]['source'],'segments':segments,'editable':False,
          'edit_policy':'extraction only; string roles and capacity must remain fixed'}
    flags=[]
    if opaque:flags.append('Opaque control syntax')
    if native:flags.append('Native glyph coverage not validated')
    if count==3:flags.append('Third display string role not fully validated')
    if flags:item['reason']='; '.join(flags)
    return ('identified' if flags else 'validated'),item


def reconstruct(item):
    output=bytearray.fromhex(item['header_hex'])
    for segment in item['segments']:
        raw=bytes.fromhex(segment['original_text_hex'])
        if native_text(raw)[0]!=segment['source'] or segment['zero_count']<1:
            raise ValueError('Advanced string bytes/text mismatch')
        if len(output)!=segment['text_offset']-item['offset']:
            raise ValueError('Advanced string offset mismatch')
        output.extend(raw);output.extend(bytes(segment['zero_count']))
    return bytes(output)
