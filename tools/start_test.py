"""Launch only the existing isolated PCSX2; never restore a savestate."""
from pathlib import Path
import argparse, configparser, json, os, subprocess

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'work/pcsx2-functional'
ISOS={'layout':ROOT/'work/fontes-layout-v005/MetalSaga-ptbr-layout-v005.iso',
      'layout-v004':ROOT/'work/fontes-layout-v004/MetalSaga-ptbr-layout-v004.iso',
      'diary':ROOT/'work/MetalSaga-ptbr-experimento.iso',
      'dialogue':ROOT/'work/MetalSaga-ptbr-dialogo-inicial-v001.iso',
      'accents':ROOT/'work/MetalSaga-ptbr-acentos-v001.iso',
      'fonts':ROOT/'work/MetalSaga-ptbr-fontes-v002.iso',
      'spacing':ROOT/'work/MetalSaga-ptbr-espacamento-v003.iso',
      'pilot':ROOT/'work/piloto-inicial-v001/MetalSaga-ptbr-piloto-inicial-v001.iso',
      'region':ROOT/'work/regiao-inicial-v024/MetalSaga-ptbr-regiao-inicial-v024.iso',
      'region-v023':ROOT/'work/regiao-inicial-v023/MetalSaga-ptbr-regiao-inicial-v023.iso',
      'region-v022':ROOT/'work/regiao-inicial-v022/MetalSaga-ptbr-regiao-inicial-v022.iso',
      'region-v021':ROOT/'work/regiao-inicial-v021/MetalSaga-ptbr-regiao-inicial-v021.iso',
      'region-v020':ROOT/'work/regiao-inicial-v020/MetalSaga-ptbr-regiao-inicial-v020.iso',
      'region-v019':ROOT/'work/regiao-inicial-v019/MetalSaga-ptbr-regiao-inicial-v019.iso',
      'region-v018':ROOT/'work/regiao-inicial-v018/MetalSaga-ptbr-regiao-inicial-v018.iso',
      'region-v017':ROOT/'work/regiao-inicial-v017/MetalSaga-ptbr-regiao-inicial-v017.iso',
      'region-v016':ROOT/'work/regiao-inicial-v016/MetalSaga-ptbr-regiao-inicial-v016.iso',
      'region-v015':ROOT/'work/regiao-inicial-v015/MetalSaga-ptbr-regiao-inicial-v015.iso',
      'region-v014':ROOT/'work/regiao-inicial-v014/MetalSaga-ptbr-regiao-inicial-v014.iso',
      'region-v013':ROOT/'work/regiao-inicial-v013/MetalSaga-ptbr-regiao-inicial-v013.iso',
      'region-v012':ROOT/'work/regiao-inicial-v012/MetalSaga-ptbr-regiao-inicial-v012.iso',
      'region-v011':ROOT/'work/regiao-inicial-v011/MetalSaga-ptbr-regiao-inicial-v011.iso',
      'region-v010':ROOT/'work/regiao-inicial-v010/MetalSaga-ptbr-regiao-inicial-v010.iso',
      'region-v009':ROOT/'work/regiao-inicial-v009/MetalSaga-ptbr-regiao-inicial-v009.iso',
      'region-v008':ROOT/'work/regiao-inicial-v008/MetalSaga-ptbr-regiao-inicial-v008.iso',
      'region-v007':ROOT/'work/regiao-inicial-v007/MetalSaga-ptbr-regiao-inicial-v007.iso',
      'region-v006':ROOT/'work/regiao-inicial-v006/MetalSaga-ptbr-regiao-inicial-v006.iso',
      'region-v005':ROOT/'work/regiao-inicial-v005/MetalSaga-ptbr-regiao-inicial-v005.iso',
      'region-v004':ROOT/'work/regiao-inicial-v004/MetalSaga-ptbr-regiao-inicial-v004.iso',
      'region-v002':ROOT/'work/regiao-inicial-v002/MetalSaga-ptbr-regiao-inicial-v002.iso',
      'region-v003':ROOT/'work/regiao-inicial-v003/MetalSaga-ptbr-regiao-inicial-v003.iso',
      'development':ROOT/'work/desenvolvimento/MetalSaga-ptbr-desenvolvimento.iso'}

def launch_command(iso):
    exe=(BASE/'pcsx2-qt.exe').resolve()
    if not exe.is_file() or not (BASE/'portable.txt').is_file():
        raise ValueError('Isolated PCSX2 not prepared; run tools/prepare_pcsx2_test.py')
    image=ISOS.get(iso,Path(iso)).resolve()
    if image==ISOS['development'].resolve() and (ROOT/'work/desenvolvimento/transacao.json').exists():
        raise ValueError('Development ISO has an interrupted transaction; recover before launching')
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
    p=argparse.ArgumentParser();p.add_argument('--iso',default='region');p.add_argument('--dry-run',action='store_true');a=p.parse_args()
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
