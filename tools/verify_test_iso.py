"""Read-only preflight of a completed build, before opening its ISO."""
import argparse,hashlib,json,re,os
from pathlib import Path
from reinsertion import ROOT

def _hash_stream(stream):
    digest=hashlib.sha256()
    for block in iter(lambda:stream.read(4*1024*1024),b''):digest.update(block)
    return digest.hexdigest()

def verify_image(image):
    image=Path(image).absolute()
    if image.is_symlink():raise ValueError('A imagem não pode ser um link')
    work=(ROOT/'work').resolve()
    if not image.is_relative_to(work) or image.suffix.lower()!='.iso':
        raise ValueError('A imagem de teste deve estar em work/')
    for folder in (image.parent,*image.parent.parents):
        if folder==work:break
        if folder.is_symlink() or (hasattr(folder,'is_junction') and folder.is_junction()):
            raise ValueError('Não usar imagem por diretório vinculado')
    image=image.resolve()
    if not image.is_relative_to(work):raise ValueError('Imagem fora de work/')
    for folder in (image.parent,ROOT/'work/desenvolvimento'):
        if (folder/'transacao.json').exists():raise ValueError('Transação pendente; recuperar antes de abrir o jogo')
    if list(image.parent.glob('*.partial')):raise ValueError('Construção parcial; não abrir a imagem')
    report_path=image.parent/'relatorio.json'
    if report_path.is_symlink():raise ValueError('Relatório vinculado não é permitido')
    raw=report_path.read_bytes();report=json.loads(raw);iso=report.get('iso',{})
    if (report.get('valid') is not True or iso.get('all_bytes_match_expected_patch') is not True
        or iso.get('iso_directory_identical') is not True or iso.get('image_name')!=image.name):
        raise ValueError('A imagem não tem construção concluída e verificada')
    expected=iso.get('output_iso_sha256');size=iso.get('iso_size')
    if not isinstance(expected,str) or not re.fullmatch('[0-9a-f]{64}',expected) or type(size) is not int or size<=0:
        raise ValueError('Hash ou tamanho inválido no relatório')
    with image.open('rb') as stream:
        before=os.fstat(stream.fileno())
        if before.st_nlink!=1 or before.st_size!=size:raise ValueError('Tamanho ou independência da imagem não confere')
        actual=_hash_stream(stream);after=os.fstat(stream.fileno())
    current=image.stat()
    identity=lambda s:(s.st_size,s.st_mtime_ns,s.st_ino)
    if identity(before)!=identity(after) or identity(after)!=identity(current) or report_path.read_bytes()!=raw:
        raise ValueError('Imagem ou relatório mudou durante a conferência')
    if actual!=expected:raise ValueError('Hash da ISO não confere; não iniciar o jogo. Reconstruir pela receita, sem corrigir bytes por suposição.')
    return {'path':image.relative_to(ROOT).as_posix(),'size':size,'sha256':actual,'verified':True}

def main():
    p=argparse.ArgumentParser(description='Conferir imagem local antes de testar');p.add_argument('image',type=Path)
    a=p.parse_args();print(json.dumps(verify_image(a.image),ensure_ascii=False,indent=2))

if __name__=='__main__':main()
