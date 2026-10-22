"""Build a new ISO using validated fixed-size MAP message patches, without a MAP copy."""
from pathlib import Path
import argparse, hashlib, json, mmap, shutil
from dialogue import ROOT,changes
from disc import entries,digest,SECTOR

ORIGINAL_ISO_SHA256='ef8405bf9e34bffd7846bcf3386a73464864823e20cd46ee9dacec514028b403'

def compare_streams(original,modified,patches,chunk_size=1024*1024):
    """Require exact expected output for every byte, including bytes outside patches."""
    pos=0;before_hash=hashlib.sha256();after_hash=hashlib.sha256();changed=[]
    while block:=original.read(chunk_size):
        actual=modified.read(len(block));expected=bytearray(block)
        for patch in patches:
            start=patch['offset'];end=start+len(patch['before'])
            low=max(pos,start);high=min(pos+len(block),end)
            if high<=low:continue
            left=low-pos;right=high-pos;source_left=low-start;source_right=high-start
            if block[left:right]!=patch['before'][source_left:source_right]:
                raise ValueError('ISO source differs from patch baseline')
            expected[left:right]=patch['after'][source_left:source_right]
            changed.extend(pos+left+i for i,(a,b) in enumerate(zip(block[left:right],actual[left:right])) if a!=b)
        if actual!=expected:raise ValueError(f'Unexpected ISO changes near 0x{pos:X}')
        before_hash.update(block);after_hash.update(actual);pos+=len(block)
    if modified.read(1):raise ValueError('ISO length changed')
    return {'source_iso_sha256':before_hash.hexdigest(),'output_iso_sha256':after_hash.hexdigest(),
            'iso_size':pos,'changed_iso_offsets':changed,'all_bytes_match_expected_patch':True}

def main():
    p=argparse.ArgumentParser();p.add_argument('--plan',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--report',type=Path,required=True)
    a=p.parse_args();output=a.output.resolve();report=a.report.resolve()
    if not output.is_relative_to(ROOT/'work') or output.suffix.lower()!='.iso' or output.exists():
        raise ValueError('Use a new .iso under work/')
    if not report.is_relative_to(ROOT) or report.is_relative_to(ROOT/'JOGO') or report.is_relative_to(ROOT/'PCSX2') or report.exists():
        raise ValueError('Use a new project report outside protected folders')
    iso=ROOT/'JOGO/Metal Saga.iso';resource=ROOT/'JOGO/Metal Saga/DATA/MAP/MAP.MCT'
    document=json.loads(a.plan.read_text(encoding='utf-8'))
    with resource.open('rb') as f,mmap.mmap(f.fileno(),0,access=mmap.ACCESS_READ) as data:
        patches=changes(data,document)
    if not patches:raise ValueError('No changes; no redundant ISO generated')
    with iso.open('rb') as f:
        original_directory=entries(f)
        found=[r for r in original_directory if r['path']=='DATA/MAP/MAP.MCT']
        if len(found)!=1:raise ValueError('MAP.MCT extent not unique')
        extent=found[0];f.seek(extent['lba']*SECTOR)
        if extent['size']!=resource.stat().st_size or digest(f,extent['size'])!=document['source_sha256']:
            raise ValueError('ISO MAP.MCT does not match extracted reference')
    absolute=[{**patch,'offset':extent['lba']*SECTOR+patch['offset']} for patch in patches]
    partial=output.with_suffix('.iso.partial');output.parent.mkdir(parents=True,exist_ok=True)
    from iso_retention import prune
    prune(reserve=1)
    # Exclusive creation also protects previous incomplete experiments.
    with iso.open('rb') as src,partial.open('xb') as dst:shutil.copyfileobj(src,dst,1024*1024)
    with partial.open('r+b') as f:
        for patch in absolute:
            f.seek(patch['offset']);f.write(patch['after'])
    with iso.open('rb') as src,partial.open('rb') as dst:
        validation=compare_streams(src,dst,absolute)
    if validation['source_iso_sha256']!=ORIGINAL_ISO_SHA256:
        raise ValueError('Original ISO hash differs from recognized reference')
    expected_source=json.loads((ROOT/'reports/disc.json').read_text(encoding='utf-8'))
    # The original report anchors the reference resource independently of the plan.
    if next(r['sha256'] for r in expected_source if r['path']==extent['path'])!=document['source_sha256']:
        raise ValueError('Reference resource hash differs from inventory')
    with partial.open('rb') as f:
        if entries(f)!=original_directory:raise ValueError('ISO directory or LBAs changed')
    validation.update({'schema':1,'source_iso':'JOGO/Metal Saga.iso','output_iso':output.relative_to(ROOT).as_posix(),
                       'resource':extent['path'],'resource_lba':extent['lba'],'resource_size':extent['size'],
                       'resource_source_sha256':document['source_sha256'],'iso_directory_identical':True,
                       'patch_policy':document['policy'],'patched_entries':[
                           {key:entry[key] for key in ('id','offset','index','size','text_offset','capacity','source','translation','header_hex','record_sha256','neighbors')}
                           for entry in document['entries'] if entry['source']!=entry['translation']],
                       'visual_status':'pending_user_verification','accent_support_tested':False})
    report.parent.mkdir(parents=True,exist_ok=True)
    partial.rename(output)
    report.write_text(json.dumps(validation,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    print(f'Created {output}; {len(validation["changed_iso_offsets"])} changed bytes; full-image verification passed')

if __name__=='__main__':main()
