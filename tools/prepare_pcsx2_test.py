"""Create an isolated portable PCSX2 test install; never reuse personal cards/states."""
from pathlib import Path
import argparse, configparser, hashlib, json, shutil

ROOT=Path(__file__).resolve().parents[1]
PROTECTED=('BIOS','inis','memcards','sstates','gamesettings','inputprofiles')

def protected_hashes():
    result={}
    for folder in PROTECTED:
        for path in sorted((ROOT/'PCSX2'/folder).rglob('*')):
            if path.is_file():
                with path.open('rb') as f:
                    result[path.relative_to(ROOT/'PCSX2').as_posix()]=hashlib.file_digest(f,'sha256').hexdigest()
    return result

def main():
    p=argparse.ArgumentParser();p.add_argument('--verify',action='store_true');p.add_argument('--automation-input',action='store_true');a=p.parse_args()
    base=ROOT/'work/pcsx2-functional'
    manifest=ROOT/'work/pcsx2-protected-before.json'
    if a.verify:
        before=json.loads(manifest.read_text(encoding='utf-8'))
        if before!=protected_hashes():raise ValueError('Original PCSX2 resources changed')
        print(f'{len(before)} protected files unchanged');return
    if base.exists() or manifest.exists():raise ValueError('Test environment or manifest already exists')
    before=protected_hashes();base.mkdir(parents=True)
    manifest.write_text(json.dumps(before,indent=2)+'\n',encoding='utf-8')
    source=ROOT/'PCSX2'
    for path in source.iterdir():
        if path.is_file() and (path.suffix.lower() in ('.exe','.dll') or path.name in ('qt.conf','portable.txt')):
            shutil.copy2(path,base/path.name)
    for folder in ('QtPlugins','resources','translations','BIOS'):
        shutil.copytree(source/folder,base/folder)
    for folder in ('inis','memcards','sstates','snaps','logs','cache','cheats','patches','textures','inputprofiles','videos','gamesettings'):
        (base/folder).mkdir(exist_ok=True)
    c=configparser.ConfigParser(interpolation=None,strict=False);c.optionxform=str
    # Read only the original BIOS selection, not game-list paths or user input mappings.
    c.read(source/'inis/PCSX2.ini',encoding='utf-8')
    bios=c.get('Filenames','BIOS')
    if Path(bios).name!=bios or not (base/'BIOS'/bios).is_file():raise ValueError('Unsupported BIOS path')
    out=configparser.ConfigParser(interpolation=None);out.optionxform=str
    out['UI']={'SettingsVersion':'1','SetupWizardIncomplete':'false','StartFullscreen':'false','PauseOnFocusLoss':'false','ConfirmShutdown':'false'}
    out['Folders']={key:str(base/value) for key,value in {'Bios':'BIOS','Snapshots':'snaps','Savestates':'sstates','MemoryCards':'memcards','Logs':'logs','Cache':'cache','Cheats':'cheats','Patches':'patches','Textures':'textures','InputProfiles':'inputprofiles','Videos':'videos','UserResources':'resources'}.items()}
    out['Filenames']={'BIOS':bios}
    out['EmuCore']={'EnableFastBoot':'true','SaveStateOnShutdown':'false','EnableCheats':'false','EnablePatches':'false','EnableWideScreenPatches':'false','EnableNoInterlacingPatches':'false','EnableDiscordPresence':'false'}
    out['MemoryCards']={'Slot1_Enable':'false','Slot2_Enable':'false'}
    out['InputSources']={'Keyboard':'true','SDL':'false','Mouse':'false'}
    out['Pad1']={'Type':'DualShock2',**{key:'Keyboard/'+value for key,value in {'Up':'Up','Down':'Down','Left':'Left','Right':'Right','Cross':'X','Circle':'C','Triangle':'T','Square':'S','Start':'Return','Select':'Backspace','L1':'Q','R1':'E','L2':'1','R2':'3','LUp':'W','LDown':'Z','LLeft':'A','LRight':'D'}.items()}}
    out['Pad2']={'Type':'None'}
    # Toggle macros make short host key events visible to the game's frame polling.
    # Press each key once to hold, again to release. No game-memory modification.
    if a.automation_input:
        for i,(key,bind) in enumerate([('I','Up'),('K','Down'),('J','Left'),('L','Right'),('U','Cross'),('O','Circle'),('P','Triangle'),('H','Start')],1):
            for suffix,value in [('',f'Keyboard/{key}'),('Binds',bind),('Toggle','true'),('Frequency','0')]:
                out['Pad1'][f'Macro{i}{suffix}']=value
    out['Hotkeys']={'Screenshot':'Keyboard/F8','TogglePause':'Keyboard/Space','OpenPauseMenu':'Keyboard/Escape','SaveStateToSlot':'Keyboard/F1','LoadStateFromSlot':'Keyboard/F3','NextSaveStateSlot':'Keyboard/F2'}
    out['Logging']={'EnableFileLogging':'true','EnableTimestamps':'true','EnableEEConsole':'true','EnableVerbose':'true','EnableLogWindow':'false'}
    out['EmuCore/GS']={'upscale_multiplier':'1','OsdShowFPS':'true','OsdShowVersion':'true'}
    out['GameList']={}
    with (base/'inis/PCSX2.ini').open('w',encoding='utf-8') as f:out.write(f)
    assert before==protected_hashes()
    print(base/'pcsx2-qt.exe')

if __name__=='__main__':main()
