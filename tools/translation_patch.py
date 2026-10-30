"""Local, streaming same-size ISO patch. Python standard library only.

Container: ZIP with manifest.json and delta.bin; delta entries are <QI> plus
up to 4096 replacement bytes. Never extracts archive paths or overwrites files.
This is a project-specific format, not an xdelta/IPS/BPS patch.
"""
import argparse,hashlib,json,os,re,shutil,struct,tempfile,zipfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
PAGE=4096
HEADER=struct.Struct('<QI')
FORMAT='metal-saga-same-size-page-patch-v001'
KEYS={'format','page_size','source_size','target_size','source_sha256','target_sha256','records','delta_sha256'}


def digest(stream):
    h=hashlib.sha256()
    for b in iter(lambda:stream.read(1024*1024),b''):h.update(b)
    return h.hexdigest()


def no_duplicates(pairs):
    result={}
    for k,v in pairs:
        if k in result:raise ValueError('Campo duplicado no manifesto')
        result[k]=v
    return result


def manifest(archive):
    infos=archive.infolist()
    if len(infos)!=2 or {x.filename for x in infos}!={'manifest.json','delta.bin'}:
        raise ValueError('O pacote deve conter somente manifesto e delta')
    if archive.getinfo('manifest.json').file_size>4096:raise ValueError('Manifesto excessivo')
    m=json.loads(archive.read('manifest.json'),object_pairs_hook=no_duplicates)
    if set(m)!=KEYS or m['format']!=FORMAT or m['page_size']!=PAGE:raise ValueError('Formato de patch incompatível')
    if any(type(m[k]) is not int for k in ('source_size','target_size','records','page_size')):
        raise ValueError('Tamanho/contagem inválidos')
    if m['source_size']<=0 or m['target_size']!=m['source_size'] or not 0<=m['records']<=(m['source_size']+PAGE-1)//PAGE:
        raise ValueError('Patch exige tamanho fixo e intervalos limitados')
    if any(not isinstance(m[k],str) or not re.fullmatch('[0-9a-f]{64}',m[k]) for k in ('source_sha256','target_sha256','delta_sha256')):
        raise ValueError('Hash inválido')
    size=archive.getinfo('delta.bin').file_size
    if not HEADER.size*m['records']<=size<=min((HEADER.size+PAGE)*m['records'],m['source_size']+HEADER.size*m['records']):
        raise ValueError('Delta excede seus intervalos declarados')
    return m


def destination(path,inputs):
    path=Path(path).absolute()
    if path.is_symlink() or path.exists():raise ValueError('Use um arquivo de saída novo; nenhum existente será substituído')
    resolved=path.resolve()
    if any(resolved==Path(x).resolve() for x in inputs):raise ValueError('Saída coincide com uma entrada')
    if not path.parent.is_dir():raise ValueError('Crie primeiro a pasta de saída')
    return path


def temporary_for(output):
    fd,name=tempfile.mkstemp(prefix='.'+output.name+'-',suffix='.partial',dir=output.parent)
    os.close(fd)
    return Path(name)


def publish(temp,output):
    # Windows rename fails if destination exists; POSIX hardlink also refuses
    # replacement. Both publish the verified file within the same filesystem.
    if os.name=='nt':os.rename(temp,output)
    else:os.link(temp,output);temp.unlink()


def create_patch(source,image,output,*,expected_source_sha,expected_target_sha):
    source=Path(source);image=Path(image);output=destination(output,(source,image))
    if source.resolve()==image.resolve() or os.path.samefile(source,image):raise ValueError('Original e imagem devem ser independentes')
    size=source.stat().st_size
    if not size or image.stat().st_size!=size:raise ValueError('Imagens devem ter o mesmo tamanho positivo')
    temp=temporary_for(output)
    try:
        hs=hashlib.sha256();ht=hashlib.sha256();hd=hashlib.sha256();count=0;replacement_bytes=0
        with source.open('rb') as a,image.open('rb') as b,zipfile.ZipFile(temp,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as archive:
            before=[os.fstat(a.fileno()),os.fstat(b.fileno())]
            with archive.open('delta.bin','w',force_zip64=True) as delta:
                at=0
                while old:=a.read(1024*1024):
                    new=b.read(len(old))
                    if len(new)!=len(old):raise ValueError('Imagem mudou de tamanho durante a leitura')
                    hs.update(old);ht.update(new)
                    if old!=new:
                        for start in range(0,len(old),PAGE):
                            value=new[start:start+PAGE]
                            if value==old[start:start+PAGE]:continue
                            header=HEADER.pack(at+start,len(value));delta.write(header);delta.write(value)
                            hd.update(header);hd.update(value);count+=1;replacement_bytes+=len(value)
                    at+=len(old)
                if at!=size or b.read(1):raise ValueError('Tamanho de imagem mudou')
            if hs.hexdigest()!=expected_source_sha or ht.hexdigest()!=expected_target_sha:
                raise ValueError('Hash da origem ou da tradução não confere')
            identity=lambda s:(s.st_size,s.st_mtime_ns,s.st_ino)
            if [identity(x) for x in before]!=[identity(os.fstat(f.fileno())) for f in (a,b)]:raise ValueError('Entrada mudou durante a geração')
            m={'format':FORMAT,'page_size':PAGE,'source_size':size,'target_size':size,
               'source_sha256':hs.hexdigest(),'target_sha256':ht.hexdigest(),'records':count,'delta_sha256':hd.hexdigest()}
            archive.writestr('manifest.json',json.dumps(m,sort_keys=True,separators=(',',':'))+'\n')
        with zipfile.ZipFile(temp) as archive:
            if manifest(archive)!=m:raise ValueError('Manifesto gerado inconsistente')
        publish(temp,output)
        with output.open('rb') as f:package_sha=digest(f)
        return {**m,'package_size':output.stat().st_size,'package_sha256':package_sha,
                'replacement_page_bytes':replacement_bytes}
    finally:
        if temp.exists():temp.unlink()


def apply_patch(source,patch,output,*,before_publish=None):
    source=Path(source);patch=Path(patch);output=destination(output,(source,patch))
    temp=None
    try:
        with zipfile.ZipFile(patch) as archive,source.open('rb') as a:
            m=manifest(archive);before=os.fstat(a.fileno())
            if before.st_size!=m['source_size'] or digest(a)!=m['source_sha256']:
                raise ValueError('ISO original incompatível; nenhum resultado foi criado')
            temp=temporary_for(output);a.seek(0)
            with temp.open('w+b') as b:
                shutil.copyfileobj(a,b,1024*1024)
                if (before.st_size,before.st_mtime_ns,before.st_ino)!=(os.fstat(a.fileno()).st_size,os.fstat(a.fileno()).st_mtime_ns,os.fstat(a.fileno()).st_ino):raise ValueError('Original mudou durante a cópia')
                hd=hashlib.sha256();end=0
                with archive.open('delta.bin') as delta:
                    for i in range(m['records']):
                        header=delta.read(HEADER.size)
                        if len(header)!=HEADER.size:raise ValueError('Cabeçalho de intervalo truncado')
                        at,length=HEADER.unpack(header)
                        if at%PAGE or at<end or length!=min(PAGE,m['target_size']-at) or not 0<length<=PAGE:
                            raise ValueError('Intervalo sobreposto, desalinhado ou fora da imagem')
                        value=delta.read(length)
                        if len(value)!=length:raise ValueError('Dados de intervalo truncados')
                        hd.update(header);hd.update(value);b.seek(at);b.write(value);end=at+length
                    if delta.read(1):raise ValueError('Dados excedentes no delta')
                if hd.hexdigest()!=m['delta_sha256']:raise ValueError('Hash do delta não confere')
                b.flush();b.seek(0)
                if os.fstat(b.fileno()).st_size!=m['target_size'] or digest(b)!=m['target_sha256']:
                    raise ValueError('ISO reconstruída não corresponde à tradução esperada')
        if before_publish is not None:before_publish()
        publish(temp,output)
        return {'size':m['target_size'],'sha256':m['target_sha256'],'verified':True}
    finally:
        if temp is not None and temp.exists():temp.unlink()


def reserve_work_iso(source,patch,output):
    """CLI only: retain five work ISOs, after full reconstruction validation.

    Core fixture tests never run project-wide retention. Alpha is outside work.
    """
    target=Path(output).resolve()
    if not target.is_relative_to(ROOT/'work') or target.suffix.lower()!='.iso':return
    from iso_retention import plan,prune
    decision=plan(reserve=1)
    protected={Path(p).resolve() for p in (source,patch,output)}
    if any(Path(row['path']).resolve() in protected for row in decision['delete']):
        raise ValueError('Retenção atingiria uma entrada desta aplicação; operação recusada')
    prune(reserve=1)


def main():
    p=argparse.ArgumentParser(description='Gerar/aplicar patch local com verificação integral; não sobrescreve arquivos')
    sub=p.add_subparsers(dest='mode',required=True)
    c=sub.add_parser('create');c.add_argument('--original',type=Path,default=ROOT/'JOGO/Metal Saga.iso')
    c.add_argument('--image',type=Path);c.add_argument('--output',type=Path,required=True)
    a=sub.add_parser('apply');a.add_argument('--original',type=Path,required=True);a.add_argument('--patch',type=Path,required=True);a.add_argument('--output',type=Path,required=True)
    args=p.parse_args()
    if args.mode=='create':
        from start_test import ISOS
        from verify_test_iso import verify_image
        from build_dialogue_iso import ORIGINAL_ISO_SHA256
        image=args.image or ISOS['interface'];check=verify_image(image)
        result=create_patch(args.original,image,args.output,expected_source_sha=ORIGINAL_ISO_SHA256,expected_target_sha=check['sha256'])
    else:result=apply_patch(args.original,args.patch,args.output,
                           before_publish=lambda:reserve_work_iso(args.original,args.patch,args.output))
    print(json.dumps(result,ensure_ascii=False,indent=2))


if __name__=='__main__':main()
