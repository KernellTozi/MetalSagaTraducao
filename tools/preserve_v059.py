"""User-requested replacement of old generated ISOs with the verified v059.

Fixed paths and hashes only. Recipes/reports are preserved, unknown images
are never deleted, and original game/emulator files are outside this scope.
"""
import argparse
import copy
import hashlib
import json
import os
from pathlib import Path
import shutil
import stat

ROOT=Path(__file__).resolve().parents[1]
SOURCE=Path('work/interface-v059/MetalSaga-ptbr-interface-v059.iso')
BACKUP=Path('dist/backup-v059/MetalSaga-ptbr-backup-v059.iso')
WORKING=Path('work/falantes-lookup-v001/MetalSaga-ptbr-falantes-base-v059.iso')
EXPECTED='ab243c520f6e84169d52ee765cb71faeeeb605fb79b34aecd9adc126ea008094'
SIZE=1704427520
OLD_ALPHA=Path('dist/alpha-v001/MetalSaga-ptbr-alpha-v001.iso')
ALPHA_SHA='f928e0c375db669e16f078d6a0b7a4bd053ab3e933e7732e3772f14beb00bc58'


def safe(relative):
    if relative.is_absolute() or '..' in relative.parts:
        raise ValueError('Only fixed project-relative paths are allowed')
    path=ROOT/relative
    if not path.resolve().is_relative_to(ROOT.resolve()):
        raise ValueError('Snapshot path escapes workspace')
    for parent in (path,*path.parents):
        if parent==ROOT:break
        if parent.is_symlink() or (hasattr(parent,'is_junction') and parent.is_junction()):
            raise ValueError('Linked snapshot path refused')
    return path


def checksum(path):
    with path.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()


def verified(relative,expected,size=None):
    if size is None:size=SIZE
    path=safe(relative);before=path.stat()
    if before.st_nlink!=1 or before.st_size!=size:
        raise ValueError('Image size/link count differs')
    actual=checksum(path);after=path.stat()
    if (before.st_ino,before.st_mtime_ns,before.st_size)!=(after.st_ino,after.st_mtime_ns,after.st_size):
        raise ValueError('Image changed during hash verification')
    if actual!=expected:raise ValueError('Image hash differs')
    return {'path':relative.as_posix(),'size':size,'sha256':actual,
            'mtime_ns':after.st_mtime_ns,'inode':after.st_ino}


def copy_checked(relative,read_only=False):
    target=safe(relative)
    if (target.parent/'transacao.json').exists() or target.with_suffix('.iso.partial').exists():
        raise ValueError('Destination has pending copy/transaction')
    if target.exists():
        result=verified(relative,EXPECTED)
    else:
        target.parent.mkdir(parents=True,exist_ok=True)
        partial=target.with_suffix('.iso.partial')
        with safe(SOURCE).open('rb') as src,partial.open('xb') as dst:
            shutil.copyfileobj(src,dst,1024*1024);dst.flush();os.fsync(dst.fileno())
        if partial.stat().st_size!=SIZE or checksum(partial)!=EXPECTED:
            raise ValueError('Copy verification failed; partial retained')
        partial.rename(target);result=verified(relative,EXPECTED)
    if read_only:target.chmod(stat.S_IREAD)
    return {**result,'read_only':not bool(target.stat().st_mode&stat.S_IWRITE)}


def removal_plan():
    result=[]
    for version in range(55,59):
        rel=Path(f'work/interface-v{version:03d}/MetalSaga-ptbr-interface-v{version:03d}.iso')
        path=safe(rel)
        if not path.exists():continue
        from verify_test_iso import verify_image
        info=verify_image(path)
        report=json.loads((ROOT/f'reports/interface-v{version:03d}.json').read_bytes())
        if info['sha256']!=report['iso']['sha256']:
            raise ValueError('Old ISO differs from its public build record')
        result.append(verified(rel,info['sha256']))
    if safe(OLD_ALPHA).exists():result.append(verified(OLD_ALPHA,ALPHA_SHA))
    return result


def run(apply=False):
    from verify_test_iso import verify_image
    info=verify_image(safe(SOURCE))
    if info['sha256']!=EXPECTED or info['size']!=SIZE:
        raise ValueError('Current v059 differs')
    planned=removal_plan()
    if not apply:return {'source':info,'delete_after_verified_copies':planned,
                         'backup':BACKUP.as_posix(),'new_working_copy':WORKING.as_posix()}
    backup=copy_checked(BACKUP,True);working=copy_checked(WORKING)
    receipt=copy.deepcopy(json.loads((safe(SOURCE).parent/'relatorio.json').read_bytes()))
    receipt['iso']['image_name']=WORKING.name
    receipt['verified_copy_of']={'source':SOURCE.as_posix(),'sha256':EXPECTED,
                                'purpose':'Unmodified v059 base for speaker lookup investigation'}
    out=safe(WORKING).parent/'relatorio.json'
    if out.exists() and json.loads(out.read_bytes())!=receipt:
        raise ValueError('Working copy receipt already differs')
    out.write_bytes((json.dumps(receipt,ensure_ascii=False,indent=2)+'\n').encode())
    verify_image(safe(WORKING))
    report_path=ROOT/'reports/backup-v059.json'
    prior=json.loads(report_path.read_bytes()) if report_path.exists() else None
    if prior and (prior.get('source',{}).get('sha256')!=EXPECTED
                  or prior.get('backup',{}).get('path')!=BACKUP.as_posix()):
        raise ValueError('Existing snapshot ledger belongs to a different operation')
    deleted=prior['deleted'] if prior else []
    planned_ids={r['path'] for r in deleted}
    if planned_ids.intersection(r['path'] for r in planned):
        raise ValueError('Deleted image unexpectedly reappeared; manual review required')
    log={'schema':1,'source':info,'backup':backup,'working_copy':working,
         'deleted':deleted,'planned_remaining_deletions':planned,
         'status':'copies_verified_cleanup_in_progress','preserved_recipes_and_reports':True,
         'old_alpha_replaced_by_user_request':True,'changes_to_game_content':False,
         'backup_outside_work_retention':True}
    def write():report_path.write_bytes((json.dumps(log,ensure_ascii=False,indent=2)+'\n').encode())
    write()
    for item in planned:
        path=safe(Path(item['path']));now=path.stat()
        if now.st_nlink!=1 or (now.st_size,now.st_mtime_ns,now.st_ino)!=(item['size'],item['mtime_ns'],item['inode']):
            raise ValueError('Deletion target changed after planning')
        if (path.parent/'transacao.json').exists():raise ValueError('Deletion target has pending transaction')
        path.chmod(stat.S_IREAD|stat.S_IWRITE);path.unlink()
        log['deleted'].append(item)
        log['planned_remaining_deletions']=[r for r in log['planned_remaining_deletions'] if r['path']!=item['path']]
        write()
    log['status']='complete';write()
    return log


if __name__=='__main__':
    p=argparse.ArgumentParser(description='Preservar v059 e retirar somente ISOs antigas vinculadas')
    p.add_argument('--apply',action='store_true');a=p.parse_args()
    print(json.dumps(run(a.apply),ensure_ascii=True,indent=2))
