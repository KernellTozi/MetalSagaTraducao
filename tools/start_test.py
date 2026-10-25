"""Launch only the existing isolated PCSX2; never restore a savestate."""
from pathlib import Path
import argparse, configparser, json, os, subprocess

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'work/pcsx2-functional'
ISOS={'interface':ROOT/'work/interface-v033/MetalSaga-ptbr-interface-v033.iso',
      'interface-v032':ROOT/'work/interface-v032/MetalSaga-ptbr-interface-v032.iso',
      'interface-v031':ROOT/'work/interface-v031/MetalSaga-ptbr-interface-v031.iso',
      'interface-v030':ROOT/'work/interface-v030/MetalSaga-ptbr-interface-v030.iso',
      'interface-v029':ROOT/'work/interface-v029/MetalSaga-ptbr-interface-v029.iso',
      'interface-v028':ROOT/'work/interface-v028/MetalSaga-ptbr-interface-v028.iso',
      'interface-v026':ROOT/'work/interface-v026/MetalSaga-ptbr-interface-v026.iso',
      'interface-v025':ROOT/'work/interface-v025/MetalSaga-ptbr-interface-v025.iso',
      'interface-v024':ROOT/'work/interface-v024/MetalSaga-ptbr-interface-v024.iso',
      'interface-v023':ROOT/'work/interface-v023/MetalSaga-ptbr-interface-v023.iso',
      'interface-v022':ROOT/'work/interface-v022/MetalSaga-ptbr-interface-v022.iso',
      'interface-v021':ROOT/'work/interface-v021/MetalSaga-ptbr-interface-v021.iso',
      'interface-v020':ROOT/'work/interface-v020/MetalSaga-ptbr-interface-v020.iso',
      'interface-v019':ROOT/'work/interface-v019/MetalSaga-ptbr-interface-v019.iso',
      'interface-v018':ROOT/'work/interface-v018/MetalSaga-ptbr-interface-v018.iso',
      'interface-v017':ROOT/'work/interface-v017/MetalSaga-ptbr-interface-v017.iso',
      'interface-v016':ROOT/'work/interface-v016/MetalSaga-ptbr-interface-v016.iso',
      'interface-v015':ROOT/'work/interface-v015/MetalSaga-ptbr-interface-v015.iso',
      'interface-v014':ROOT/'work/interface-v014/MetalSaga-ptbr-interface-v014.iso',
      'interface-v013':ROOT/'work/interface-v013/MetalSaga-ptbr-interface-v013.iso',
      'interface-v012':ROOT/'work/interface-v012/MetalSaga-ptbr-interface-v012.iso',
      'interface-v011':ROOT/'work/interface-v011/MetalSaga-ptbr-interface-v011.iso',
      'interface-v010':ROOT/'work/interface-v010/MetalSaga-ptbr-interface-v010.iso',
      'interface-v009':ROOT/'work/interface-v009/MetalSaga-ptbr-interface-v009.iso',
      'interface-v008':ROOT/'work/interface-v008/MetalSaga-ptbr-interface-v008.iso',
      'interface-v007':ROOT/'work/interface-v007/MetalSaga-ptbr-interface-v007.iso',
      'interface-v006':ROOT/'work/interface-v006/MetalSaga-ptbr-interface-v006.iso',
      'interface-v005':ROOT/'work/interface-v005/MetalSaga-ptbr-interface-v005.iso',
      'interface-v004':ROOT/'work/interface-v004/MetalSaga-ptbr-interface-v004.iso',
      'interface-v003':ROOT/'work/interface-v003/MetalSaga-ptbr-interface-v003.iso',
      'interface-v002':ROOT/'work/interface-v002/MetalSaga-ptbr-interface-v002.iso',
      'interface-v001':ROOT/'work/interface-v001/MetalSaga-ptbr-interface-v001.iso',
      'layout':ROOT/'work/fontes-layout-v005/MetalSaga-ptbr-layout-v005.iso',
      'layout-v004':ROOT/'work/fontes-layout-v004/MetalSaga-ptbr-layout-v004.iso',
      'diary':ROOT/'work/MetalSaga-ptbr-experimento.iso',
      'dialogue':ROOT/'work/MetalSaga-ptbr-dialogo-inicial-v001.iso',
      'accents':ROOT/'work/MetalSaga-ptbr-acentos-v001.iso',
      'fonts':ROOT/'work/MetalSaga-ptbr-fontes-v002.iso',
      'spacing':ROOT/'work/MetalSaga-ptbr-espacamento-v003.iso',
      'pilot':ROOT/'work/piloto-inicial-v001/MetalSaga-ptbr-piloto-inicial-v001.iso',
      'region':ROOT/'work/regiao-inicial-v029/MetalSaga-ptbr-regiao-inicial-v029.iso',
      'region-v028':ROOT/'work/regiao-inicial-v028/MetalSaga-ptbr-regiao-inicial-v028.iso',
      'region-v027':ROOT/'work/regiao-inicial-v027/MetalSaga-ptbr-regiao-inicial-v027.iso',
      'region-v026':ROOT/'work/regiao-inicial-v026/MetalSaga-ptbr-regiao-inicial-v026.iso',
      'region-v025':ROOT/'work/regiao-inicial-v025/MetalSaga-ptbr-regiao-inicial-v025.iso',
      'region-v024':ROOT/'work/regiao-inicial-v024/MetalSaga-ptbr-regiao-inicial-v024.iso',
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
    from verify_test_iso import verify_image
    verify_image(ISOS.get(iso,Path(iso)))
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
    p=argparse.ArgumentParser();p.add_argument('--iso',default='interface');p.add_argument('--dry-run',action='store_true');a=p.parse_args()
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
