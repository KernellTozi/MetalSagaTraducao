"""Archive the user-selected snapshot outside work/ retention; never overwrite it."""
import hashlib
import json
import os
import shutil
import stat
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/'work/interface-v001/MetalSaga-ptbr-interface-v001.iso'
TARGET=ROOT/'dist/alpha-v001/MetalSaga-ptbr-alpha-v001.iso'
EXPECTED='f928e0c375db669e16f078d6a0b7a4bd053ab3e933e7732e3772f14beb00bc58'


def checksum(path):
    with path.open('rb') as stream:return hashlib.file_digest(stream,'sha256').hexdigest()


def main():
    if TARGET.exists():raise ValueError('Alpha already exists; never replace it')
    if SOURCE.is_symlink() or checksum(SOURCE)!=EXPECTED:raise ValueError('Snapshot source mismatch')
    TARGET.parent.mkdir(parents=True,exist_ok=True)
    partial=TARGET.with_suffix('.iso.partial')
    with SOURCE.open('rb') as src,partial.open('xb') as dst:
        shutil.copyfileobj(src,dst,1024*1024);dst.flush();os.fsync(dst.fileno())
    if checksum(partial)!=EXPECTED:raise ValueError('Archived snapshot hash mismatch; partial retained')
    partial.rename(TARGET)
    TARGET.chmod(stat.S_IREAD)
    report={'schema':1,'source':SOURCE.relative_to(ROOT).as_posix(),'alpha':TARGET.relative_to(ROOT).as_posix(),
        'sha256':EXPECTED,'size':TARGET.stat().st_size,'read_only':not bool(TARGET.stat().st_mode&stat.S_IWRITE),
        'outside_work_retention':True,'source_commit':'0ce9b22',
        'recipe':'translations/interface-v001.json','base_dialogue_recipe':'translations/regiao-inicial-v029.json',
        'layout_profile':'ptbr-layout-v005','snapshot_status':'Archived at user request; not a new full-game visual approval'}
    report['recipe_sha256']=checksum(ROOT/report['recipe'])
    output=ROOT/'reports/alpha-v001.json'
    with output.open('x',encoding='utf-8') as stream:json.dump(report,stream,indent=2);stream.write('\n')
    print(json.dumps(report,indent=2))


if __name__=='__main__':main()
