"""Export/import the 18 PT-BR cells as lossless editable PNGs, entirely offline."""
import argparse
import hashlib
import json
from pathlib import Path
import sys
import unicodedata
import zipfile
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'work/python-deps'))
from PIL import Image
from gfi import Gfi,CHAR_TO_BYTES,sjis_to_jis,pack
from gfi_refined import font_patches
NAMES=('SUC20I22.GFI','SUC24I26.GFI')


def workspace(path,new=False):
    p=Path(path).resolve()
    if not p.is_relative_to(ROOT/'work') or new and p.exists():raise ValueError('Use work/; output must be new')
    return p


def reference(name):
    data=(ROOT/'JOGO/Metal Saga/DATA/SYS'/name).read_bytes()
    inventory=json.loads((ROOT/'reports/inventory.json').read_text(encoding='utf-8'))
    expected=next(r['sha256'] for r in inventory if r['path']=='DATA/SYS/'+name)
    if hashlib.sha256(data).hexdigest()!=expected:raise ValueError('Reference font differs')
    return data


def export(output):
    output=workspace(output,True);output.mkdir(parents=True)
    manifest={'schema':1,'profile':'v002-native-size-editable','fonts':{}}
    for name in NAMES:
        data=reference(name);font=Gfi(data);modified=bytearray(data)
        for p in font_patches(data):modified[p['offset']:p['offset']+len(p['after'])]=p['after']
        edited=Gfi(modified);folder=output/name;folder.mkdir()
        manifest['fonts'][name]={'side':font.side,'source_sha256':hashlib.sha256(data).hexdigest()}
        for char,pair in CHAR_TO_BYTES.items():
            offset=font.glyph_offset(sjis_to_jis(int.from_bytes(pair,'big')))
            image=Image.new('L',(font.side,font.side));image.putdata([v*17 for v in edited.pixels(offset)])
            image.save(folder/f'U{ord(char):04X}.png')
        refs=folder/'referencias-nao-editar';refs.mkdir()
        for base in sorted({unicodedata.normalize('NFD',c)[0] for c in CHAR_TO_BYTES}):
            image=Image.new('L',(font.side,font.side));image.putdata([v*17 for v in font.pixels(font.ascii_offset(base))])
            image.save(refs/f'{base}.png')
    (output/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')
    (output/'LEIA-ME.txt').write_text('''FONTES EDITÁVEIS PT-BR — CÓPIA LOCAL
Edite somente Uxxxx.png. Referências ASCII ficam em referencias-nao-editar.
Cada PNG tem o tamanho nativo (22x22 ou 26x26). Use zoom no editor, sem redimensionar.
Preto = transparente; branco = intensidade máxima. Tons cinza são antialiasing.
Salvar PNG em tons de cinza (L), sem paleta nem transparência adicional.
Não mudar o nome, as dimensões nem manifest.json. Não editar os GFI originais.
A importação gera cópias; não altera automaticamente nenhuma ISO.

Exemplo na raiz do projeto, usando saídas novas:
python tools/edit_font_pack.py import --pack work/fontes-editaveis-v005 --output work/fontes-editadas-teste

Os desenhos são do perfil v002. A distorção no jogo também depende do layout.
Importar um desenho não comprova que as métricas ou a aparência estejam corretas.
Não enviar estas imagens originais/referências para o GitHub.
''',encoding='utf-8')
    (output/'MAPEAMENTO.txt').write_text('\n'.join(f'U{ord(c):04X}.png = {c} | base {unicodedata.normalize("NFD",c)[0]} | bytes {pair.hex(" ")}' for c,pair in CHAR_TO_BYTES.items())+'\n',encoding='utf-8')
    archive=output.with_suffix('.zip')
    if archive.exists():raise ValueError('Archive already exists')
    with zipfile.ZipFile(archive,'x',zipfile.ZIP_DEFLATED) as z:
        for p in sorted(output.rglob('*')):
            if p.is_file():z.write(p,p.relative_to(output))
    return archive


def import_pack(folder,output):
    folder=workspace(folder);output=workspace(output,True)
    manifest_path=(folder/'manifest.json').resolve()
    if not manifest_path.is_relative_to(folder):raise ValueError('Manifest link escapes pack')
    manifest=json.loads(manifest_path.read_text(encoding='utf-8'))
    if manifest.get('schema')!=1 or manifest.get('profile')!='v002-native-size-editable' or set(manifest['fonts'])!=set(NAMES):raise ValueError('Unsupported manifest')
    pending=[]
    for name in NAMES:
        data=reference(name);font=Gfi(data)
        if manifest['fonts'][name]!={'side':font.side,'source_sha256':hashlib.sha256(data).hexdigest()}:raise ValueError('Source binding changed')
        changed=bytearray(data)
        for char,pair in CHAR_TO_BYTES.items():
            source=(folder/name/f'U{ord(char):04X}.png').resolve()
            if not source.is_relative_to(folder):raise ValueError('Image link escapes pack')
            with Image.open(source) as im:
                if im.size!=(font.side,font.side) or im.mode!='L':raise ValueError('Use native-size grayscale PNG, no palette or RGBA')
                pixels=im.get_flattened_data() if hasattr(im,'get_flattened_data') else im.getdata()
                raw=pack([round(p/17) for p in pixels])
            offset=font.glyph_offset(sjis_to_jis(int.from_bytes(pair,'big')))
            if any(data[offset:offset+font.stride]):raise ValueError('Reserved cell occupied')
            changed[offset:offset+font.stride]=raw
        pending.append((name,bytes(changed)))
    output.mkdir(parents=True)
    report={'schema':1,'source_pack':folder.relative_to(ROOT).as_posix(),'iso_modified':False,'fonts':[]}
    for name,data in pending:
        (output/name).write_bytes(data)
        report['fonts'].append({'name':name,'sha256':hashlib.sha256(data).hexdigest(),'size':len(data)})
    (output/'importacao.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    return output


def main():
    parser=argparse.ArgumentParser(description='Editar glifos PT-BR localmente sem modificar originais')
    sub=parser.add_subparsers(dest='command',required=True)
    e=sub.add_parser('export');e.add_argument('--output',type=Path,required=True)
    i=sub.add_parser('import');i.add_argument('--pack',type=Path,required=True);i.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    print(export(args.output) if args.command=='export' else import_pack(args.pack,args.output))

if __name__=='__main__':main()
