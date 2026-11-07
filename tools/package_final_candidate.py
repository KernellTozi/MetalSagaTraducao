"""Verified v070 maintenance/Desktop copies, then removal of known older ISOs.

Only --apply writes. This command is specific to the user's v070 handoff.
No emulator resources or unknown images are removed.
"""
import argparse,hashlib,json,os,shutil,stat,subprocess
from pathlib import Path
from dialogue import ROOT
from verify_test_iso import verify_image

SOURCE=ROOT/'work/interface-v070/MetalSaga-ptbr-interface-v070.iso'
MAINTENANCE=ROOT/'dist/manutencao-v070/MetalSaga-ptbr-manutencao-v070.iso'
OLD_BACKUP=ROOT/'dist/backup-v059/MetalSaga-ptbr-backup-v059.iso'
OLD_SHA='ab243c520f6e84169d52ee765cb71faeeeb605fb79b34aecd9adc126ea008094'
REPORT=ROOT/'reports/entrega-candidata-v070.json'


def digest(path):
    with Path(path).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()


def safe_path(path,root):
    path=Path(path).absolute();root=Path(root).resolve()
    if path.is_symlink() or not path.resolve().is_relative_to(root):raise ValueError('Path outside authorized target')
    for folder in (path.parent,*path.parent.parents):
        if folder==root:break
        if folder.is_symlink() or (hasattr(folder,'is_junction') and folder.is_junction()):raise ValueError('Linked directory refused')
    return path


def verified_copy(source,target,expected,*,allowed_root):
    source=Path(source);target=safe_path(target,allowed_root)
    if digest(source)!=expected:raise ValueError('Copy source hash differs')
    if target.exists():
        if target.stat().st_size==source.stat().st_size and digest(target)==expected:return 'existing_verified'
        raise ValueError('Destination already contains different data')
    temporary=target.with_suffix(target.suffix+'.partial')
    if temporary.exists():raise ValueError('Destination has an unfinished copy')
    target.parent.mkdir(parents=True,exist_ok=True)
    try:
        shutil.copyfile(source,temporary)
        if temporary.stat().st_size!=source.stat().st_size or digest(temporary)!=expected:
            raise ValueError('Copied temporary file is corrupt')
        os.replace(temporary,target)
        if digest(target)!=expected:raise ValueError('Final copy hash differs')
    finally:
        if temporary.exists():temporary.unlink()
    return 'copied_verified'


def desktop_directory():
    result=subprocess.run(['powershell','-NoProfile','-Command',"[Environment]::GetFolderPath('Desktop')"],
        capture_output=True,text=True,check=True)
    path=Path(result.stdout.strip())
    if not path.is_absolute() or not path.is_dir():raise ValueError('Desktop is unavailable')
    return path


def old_images():
    rows=[]
    for image in sorted((ROOT/'work').rglob('*.iso')):
        safe_path(image,ROOT/'work')
        if image==SOURCE:continue
        report_path=image.parent/'relatorio.json'
        if not report_path.is_file():raise ValueError(f'Unknown image is preserved: {image}')
        data=json.loads(report_path.read_bytes());iso=data.get('iso',{})
        import re
        match=re.fullmatch(r'MetalSaga-ptbr-interface-v(\d+)\.iso',image.name)
        if not match or int(match[1])>=70 or not data.get('valid') or iso.get('image_name')!=image.name:
            raise ValueError(f'Image is not an authorized older build: {image}')
        checksum=digest(image)
        if checksum!=iso['output_iso_sha256'] or image.stat().st_size!=iso['iso_size']:
            raise ValueError('Older image does not match its historical report')
        rows.append({'path':image.relative_to(ROOT).as_posix(),'sha256':checksum,'size':image.stat().st_size})
    if OLD_BACKUP.exists():
        safe_path(OLD_BACKUP,ROOT/'dist')
        if digest(OLD_BACKUP)!=OLD_SHA:raise ValueError('Protected old backup differs; preserved')
        rows.append({'path':OLD_BACKUP.relative_to(ROOT).as_posix(),'sha256':OLD_SHA,'size':OLD_BACKUP.stat().st_size})
    return rows


def package(apply=False):
    checked=verify_image(SOURCE);expected=checked['sha256'];desktop=desktop_directory()
    target=desktop/'MetalSaga-PTBR-Candidata-Final-v070.iso'
    plan=old_images()
    result={'schema':1,'version':'interface-v070','status':'candidate_pending_gameplay_review',
            'source':checked,'maintenance':str(MAINTENANCE),'desktop':str(target),
            'planned_old_images':plan,'originals_bios_saves_unchanged':True,'applied':False}
    if not apply:return result
    result['maintenance_copy']=verified_copy(SOURCE,MAINTENANCE,expected,allowed_root=ROOT/'dist')
    os.chmod(MAINTENANCE,stat.S_IREAD)
    result['desktop_copy']=verified_copy(SOURCE,target,expected,allowed_root=desktop)
    result['new_backup_read_only']=bool(MAINTENANCE.stat().st_file_attributes&1)
    result['removed']=[];result['locked_or_failed']=[]
    # Both complete new copies have been verified before deleting any old file.
    for row in plan:
        path=safe_path(ROOT/row['path'],ROOT)
        if digest(path)!=row['sha256']:raise ValueError('Old image changed after planning')
        try:
            if path==OLD_BACKUP:os.chmod(path,stat.S_IWRITE|stat.S_IREAD)
            path.unlink()
            result['removed'].append(row)
        except OSError as error:
            if path==OLD_BACKUP and path.exists():os.chmod(path,stat.S_IREAD)
            result['locked_or_failed'].append({'path':row['path'],'error':str(error)})
    result['applied']=True
    result['final_source_hash_verified']=digest(SOURCE)==expected
    result['final_maintenance_hash_verified']=digest(MAINTENANCE)==expected
    result['final_desktop_hash_verified']=digest(target)==expected
    # Only this metadata is versioned; images remain outside Git.
    REPORT.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    return result


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--apply',action='store_true');args=p.parse_args()
    print(json.dumps(package(args.apply),ensure_ascii=False,indent=2))
