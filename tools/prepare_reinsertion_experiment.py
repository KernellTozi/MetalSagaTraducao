"""Prepare only three technical test edits; no mass translation or ISO writes."""
import argparse
import json
import mmap
from pathlib import Path
from reinsertion import SOURCE,RESOURCE,POLICY,source_hash,descriptor,local,compile_batch
from dialogue import PILOT_OFFSET,PILOT_SOURCE
from build_accent_experiment import SECOND_OFFSET,SECOND_SOURCE
from dialogue_advanced import SsdIndex
from development_iso import atomic_json


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args();path=local(args.output,True)
    with SOURCE.open('rb') as stream,mmap.mmap(stream.fileno(),0,access=mmap.ACCESS_READ) as data:
        index=SsdIndex(data)
        entries=[descriptor(data,at,index) for at in (PILOT_OFFSET,SECOND_OFFSET,0x1df48484)]
        if entries[0]['segments'][0]['source']!=PILOT_SOURCE or entries[1]['segments'][0]['source']!=SECOND_SOURCE:
            raise ValueError('Cena inicial difere da referência')
        entries[0]['segments'][0]['translation']='Teste expandido:\nMesmo registro'
        english_page=entries[1]['segments'][0]['source'].split('\t',1)[1]
        entries[1]['segments'][0]['translation']='%F1%M0_5Teste: a\u00e7\u00e3o.\n\u00e1 \u00e9 \u00ed \u00f3 \u00fa\n\u00c7 \u00c1 \u00c9 \u00c3 \u00d5\t'+english_page
        entries[2]['segments'][0]['translation']='Vou ser Hunter.\tVou ser mec\u00e2nico.'
        document={'schema':1,'policy':POLICY,'resource':RESOURCE,'source_sha256':source_hash(data),
                  'catalog_version':'v003','entries':entries}
        patches,report=compile_batch(data,document,index)
        if not report['valid'] or len(patches)!=3:raise ValueError(json.dumps(report,ensure_ascii=False))
    atomic_json(path,document)
    print(f'Lote experimental preparado: {path}')


if __name__=='__main__':main()
