"""Launch only the existing isolated PCSX2; never restore a savestate."""
from pathlib import Path
import argparse, configparser, json, os, subprocess

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'work/pcsx2-functional'
ISOS={'diary':ROOT/'work/MetalSaga-ptbr-experimento.iso',
      'dialogue':ROOT/'work/MetalSaga-ptbr-dialogo-inicial-v001.iso',
      'accents':ROOT/'work/MetalSaga-ptbr-acentos-v001.iso'}

def launch_command(iso):
    exe=(BASE/'pcsx2-qt.exe').resolve()
    if not exe.is_file() or not (BASE/'portable.txt').is_file():
        raise ValueError('Isolated PCSX2 not prepared; run tools/prepare_pcsx2_test.py')
    image=ISOS.get(iso,Path(iso)).resolve()
    if image.suffix.lower()!='.iso' or not image.is_file() or not image.is_relative_to(ROOT/'work'):
        raise ValueError('Test ISO must be an existing .iso under work/')
    cfg=configparser.ConfigParser(interpolation=None,strict=False);cfg.optionxform=str
    cfg.read(BASE/'inis/PCSX2.ini',encoding='utf-8')
    for key in ('Bios','MemoryCards','Savestates','Snapshots','Logs','Cache'):
        value=Path(cfg.get('Folders',key))
        path=value if value.is_absolute() else BASE/value
        if not path.resolve().is_relative_to(BASE.resolve()):
            raise ValueError(f'Folder {key} escapes isolated environment')
    for _,value in cfg.items('GameList') if cfg.has_section('GameList') else []:
        if not Path(value).resolve().is_relative_to(ROOT):
            raise ValueError('Game list refers outside workspace')
    return [str(exe),'-portable','-fastboot',str(image)]

def main():
    p=argparse.ArgumentParser();p.add_argument('--iso',default='dialogue');p.add_argument('--dry-run',action='store_true');a=p.parse_args()
    command=launch_command(a.iso)
    print(subprocess.list2cmdline(command))
    if a.dry_run:return
    if os.name=='nt':
        # Refuse duplicate processes sharing mutable test settings/cards.
        result=subprocess.run(['powershell.exe','-NoProfile','-Command',
            "Get-CimInstance Win32_Process -Filter \"name='pcsx2-qt.exe'\" | Select-Object -ExpandProperty ExecutablePath"],capture_output=True,text=True,check=True,creationflags=subprocess.CREATE_NO_WINDOW)
        if any(path.strip().casefold()==command[0].casefold() for path in result.stdout.splitlines()):
            raise ValueError('Close the isolated PCSX2 before starting another clean test')
    subprocess.Popen(command,cwd=BASE,stdin=subprocess.DEVNULL,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)

if __name__=='__main__':main()
