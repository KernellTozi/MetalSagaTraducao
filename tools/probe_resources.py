"""Record structural evidence without exporting game text to Git."""
from pathlib import Path
import json,mmap,re,struct
from recon import ROOT,sda

def nested(d,base=0,limit=None,depth=0):
    limit=len(d) if limit is None else limit
    if depth>8 or base+12>limit or d[base:base+4]!=b'sda\0':return []
    size=struct.unpack_from('<I',d,base+4)[0]
    if not 12<=size<=limit-base:return []
    node=sda(d[base:base+size])
    if not node or not node['valid']:return []
    result=[{'offset':base,'declared_size':size,'slot_size':limit-base,'count':node['count'],'offsets':node['offsets']}]
    offsets=node['offsets']
    for a,b in zip(offsets,offsets[1:]+[size]):result+=nested(d,base+a,base+b,depth+1)
    return result

def main():
    evidence={}
    for name in ['DATA/S/S_PACK.SDA','DATA/MAP/MAP.MCT']:
        with (ROOT/'JOGO/Metal Saga'/name).open('rb') as f,mmap.mmap(f.fileno(),0,access=mmap.ACCESS_READ) as d:
            evidence[name]={'sda_nodes':nested(d)}
            if name.endswith('MAP.MCT'):
                candidates=[]
                for m in re.finditer(rb'msg[\x00n]',d):
                    a=m.start()
                    if a+32>len(d):continue
                    size=struct.unpack_from('<H',d,a+6)[0]
                    if size<36 or a+size>len(d) or size%4:continue
                    raw=d[a+32:a+size];zero=raw.find(b'\0')
                    if zero<1:continue
                    text=raw[:zero]
                    if all(32<=c<127 or c in (9,10,13) for c in text):
                        candidates.append({'offset':a,'tag':m.group().hex(),'size':size,'text_offset':a+32,'text_length':zero})
                evidence[name]['message_candidate_count']=len(candidates)
                evidence[name]['message_candidates_first_30']=candidates[:30]
                print(len(candidates),'plausible ASCII msg/msgn records (heuristic)')
    (ROOT/'reports/structures.json').write_text(json.dumps(evidence,indent=2)+'\n',encoding='utf-8')

if __name__=='__main__':main()
