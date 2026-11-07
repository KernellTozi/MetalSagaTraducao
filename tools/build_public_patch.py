"""Build a verified public xdelta package; never bundle an ISO or game files."""
import argparse,hashlib,json,os,re,shutil,subprocess,zipfile
from pathlib import Path
from dialogue import ROOT
from build_dialogue_iso import ORIGINAL_ISO_SHA256
from verify_test_iso import verify_image

ASSET='xdelta3-3.2.2-windows-x86_64.zip'
ASSET_SHA='d48f7651d86b78fdca397057b46601f89131f37219675df736db70af44ec3379'
UPSTREAM='https://github.com/jmacd/xdelta/releases/tag/v3.2.2'
LICENSES=('LICENSE-xdelta3.txt','LICENSE-BLAKE3-CC0.txt','LICENSE-XZ.txt','LICENSE-liblzma-0BSD.txt')


def digest(path):
    with Path(path).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()


def build(folder,cache,output):
    folder=Path(folder).resolve();cache=Path(cache).resolve();output=Path(output).resolve()
    if not folder.is_relative_to(ROOT/'work') or not cache.is_relative_to(ROOT/'work'):
        raise ValueError('Use local build/cache under work/')
    if not output.is_relative_to(ROOT/'dist') or output.exists():raise ValueError('Use a new package directory under dist/')
    report=json.loads((folder/'relatorio.json').read_bytes());image=folder/report['iso']['image_name']
    checked=verify_image(image);match=re.fullmatch(r'MetalSaga-ptbr-interface-v(\d+)\.iso',image.name)
    if not match:raise ValueError('Consolidated version name required')
    version='v'+match[1];source=ROOT/'JOGO/Metal Saga.iso'
    if digest(source)!=ORIGINAL_ISO_SHA256 or source.stat().st_size!=checked['size']:
        raise ValueError('Original source ISO differs')
    archive=cache/ASSET
    if digest(archive)!=ASSET_SHA:raise ValueError('Official xdelta archive hash differs')
    with zipfile.ZipFile(archive) as z:
        for tool in ('xdelta3.exe','xdelta3decode.exe'):
            name=next(n for n in z.namelist() if n.endswith('/'+tool))
            if z.read(name)!=(cache/tool).read_bytes():raise ValueError('Extracted upstream executable differs')
    for name in LICENSES:
        if not (cache/name).is_file():raise ValueError('Missing upstream license: '+name)
    output.mkdir(parents=True);payload=output/('MetalSaga-PTBR-'+version);payload.mkdir()
    patch=payload/('MetalSaga-PTBR-'+version+'.xdelta');temporary=output/'roundtrip.iso.partial'
    env=dict(os.environ);env.pop('XDELTA',None)
    encode=[str(cache/'xdelta3.exe'),'-a','-A=','-S','none','-9','-D','-e','-s',str(source),str(image),str(patch)]
    subprocess.run(encode,env=env,check=True)
    try:
        subprocess.run([str(cache/'xdelta3decode.exe'),'-D','-R','-d','-s',str(source),str(patch),str(temporary)],env=env,check=True)
        if temporary.stat().st_size!=checked['size'] or digest(temporary)!=checked['sha256']:
            raise ValueError('Round-trip ISO differs from verified build')
    finally:
        if temporary.exists():temporary.unlink()
    decoder=payload/'xdelta3decode.exe';shutil.copyfile(cache/'xdelta3decode.exe',decoder)
    # UTF-8 BOM for Windows PowerShell 5.1; .cmd has native Windows line endings.
    ps=(ROOT/'release/Aplicar-Patch.ps1').read_text(encoding='utf-8-sig')
    (payload/'Aplicar-Patch.ps1').write_bytes(b'\xef\xbb\xbf'+ps.replace('\r\n','\n').replace('\n','\r\n').encode())
    cmd=(ROOT/'release/Aplicar-Patch.cmd').read_text(encoding='utf-8-sig')
    (payload/'Aplicar-Patch.cmd').write_bytes(cmd.replace('\r\n','\n').replace('\n','\r\n').encode())
    for name in LICENSES:shutil.copyfile(cache/name,payload/name)
    manifest={'schema':1,'version':version,'game':'Metal Saga','platform':'PlayStation 2','serial':'SLUS-21293',
              'region':'USA / NTSC-U','status':'candidate_pending_gameplay_review',
              'source':{'size':source.stat().st_size,'sha256':ORIGINAL_ISO_SHA256},
              'target':{'file':'MetalSaga-PTBR-'+version+'.iso','size':checked['size'],'sha256':checked['sha256']},
              'patch':{'file':patch.name,'size':patch.stat().st_size,'sha256':digest(patch),'format':'VCDIFF/xdelta3, legacy header, no secondary compression'},
              'decoder':{'file':decoder.name,'sha256':digest(decoder),'version':'3.2.2','license':'Apache-2.0','upstream':UPSTREAM}}
    (payload/'manifesto.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    readme=f'''METAL SAGA - TRADUCAO PT-BR {version}
Tradução: Kernell Tozi
Projeto: https://github.com/KernellTozi/MetalSagaTraducao

ESTE PACOTE NAO CONTEM ISO, BIOS, EMULADOR OU ARQUIVOS EXTRAIDOS DO JOGO.
É um patch de diferenças; você precisa fornecer sua própria ISO original.
Não aplique sobre outra tradução, modificação, ISO reconstruída ou CHD.

COMO APLICAR NO WINDOWS 11 (SEM PYTHON E SEM INTERNET)
1. Extraia TODOS os arquivos do ZIP para uma pasta.
2. Abra Aplicar-Patch.cmd e selecione a ISO ORIGINAL americana.
   Também pode arrastar essa ISO para cima de Aplicar-Patch.cmd.
3. Aguarde a conferência e a criação de MetalSaga-PTBR-{version}.iso
   na mesma pasta da ISO original. Reserve pelo menos 2 GB livres ali.
4. Abra a NOVA ISO no PCSX2. A original não será alterada.
O aplicador recusa versões erradas, patch alterado e destinos existentes.
Se já existir uma ISO traduzida com esse nome, escolha outro destino pelo
PowerShell ou mova sua cópia antiga antes de repetir. Nenhum arquivo será sobrescrito.

ORIGEM EXIGIDA
Metal Saga (USA / NTSC-U), SLUS-21293
Tamanho: {source.stat().st_size} bytes
SHA-256: {ORIGINAL_ISO_SHA256}
O hash exato prevalece sobre o nome do arquivo ou da edição.

RESULTADO ESPERADO
Tamanho: {checked['size']} bytes
SHA-256: {checked['sha256']}
O aplicador confere o resultado completo antes de entregar a nova ISO.

APLICACAO MANUAL COM XDELTA3 COMPATIVEL
xdelta3 -d -s "Original.iso" "{patch.name}" "MetalSaga-PTBR-{version}.iso"
Neste pacote, xdelta3decode.exe pode ser usado no lugar de xdelta3.

ESTADO DA TRADUCAO
Candidata final para revisão em partida. Treze rótulos curtos de falantes
ainda permanecem em inglês por limitação técnica. Dummy/UP/DOWN/Damage
Override estão preservados por decisão contextual. Não há comprovação de
100% de cobertura textual ou aprovação visual de todas as telas.
Histórico, correções e limites: docs/interface-{version}.md no repositório.

PUBLICACAO
Compartilhe este ZIP de patch. Não acrescente sua ISO, BIOS, saves ou emulador.
Este arquivo não foi publicado automaticamente pelo construtor.
'''
    (payload/'LEIA-ME.txt').write_text(readme,encoding='utf-8-sig')
    notice='''FERRAMENTAS DE TERCEIROS
xdelta3decode.exe 3.2.2, binário oficial sem alterações.
Copyright (C) Joshua MacDonald. Apache License 2.0.
Fonte/binários: https://github.com/jmacd/xdelta/releases/tag/v3.2.2
Arquivo oficial: xdelta3-3.2.2-windows-x86_64.zip
SHA-256 do arquivo: '''+ASSET_SHA+'''
O release oficial liga estaticamente liblzma (xz v5.8.3, 0BSD)
e BLAKE3 1.8.5 (oferecido sob CC0/Apache-2.0).
Licenças e informações de terceiros estão nos arquivos LICENSE-*.
Fontes das dependências:
https://github.com/tukaani-project/xz/tree/v5.8.3
https://github.com/BLAKE3-team/BLAKE3/tree/1.8.5
Os scripts de aplicação são próprios do projeto MetalSagaTraducao.
'''
    (payload/'TERCEIROS.txt').write_text(notice,encoding='utf-8-sig')
    zip_path=output/('MetalSaga-PTBR-'+version+'-Patch.zip')
    with zipfile.ZipFile(zip_path,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for file in sorted(payload.iterdir()):z.write(file,file.name)
    with zipfile.ZipFile(zip_path) as z:
        if z.testzip() or any(Path(n).suffix.lower() in ('.iso','.bin','.chd','.gfi','.sda','.dat') for n in z.namelist()):
            raise ValueError('Unexpected/corrupt archive payload')
    result={'version':version,'source':manifest['source'],'target':manifest['target'],'patch':manifest['patch'],
            'zip':{'path':zip_path.relative_to(ROOT).as_posix(),'size':zip_path.stat().st_size,'sha256':digest(zip_path)},
            'decoder':manifest['decoder'],'upstream_archive_sha256':ASSET_SHA,
            'binary_decode_roundtrip_verified':True,'no_game_iso_or_original_resources_bundled':True,
            'no_automatic_publication':True,'original_iso_unchanged':digest(source)==ORIGINAL_ISO_SHA256,
            'target_iso_unchanged':digest(image)==checked['sha256'],'pcsx2_executed':False}
    result_path=ROOT/'reports'/('patch-interface-'+version+'.json')
    if result_path.exists():raise ValueError('Patch metadata already exists; preserve historical release')
    result_path.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    return result


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--build-dir',type=Path,default=ROOT/'work/interface-v070')
    p.add_argument('--cache',type=Path,default=ROOT/'work/publicacao-v070')
    p.add_argument('--output',type=Path,default=ROOT/'dist/publicacao-v070');a=p.parse_args()
    print(json.dumps(build(a.build_dir,a.cache,a.output),ensure_ascii=False,indent=2))
