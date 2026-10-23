"""Explicit delivery only: verify completed build, copy atomically, verify again."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import tempfile
from reinsertion import ROOT

DESTINATION = Path(r'C:\Users\Kernell\OneDrive\METAL SAGA')
FILENAME = 'MetalSaga-PTBR.iso'


def checksum(path):
    digest = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(4 * 1024 * 1024), b''):
            digest.update(block)
    return digest.hexdigest()


def check_pending(folder):
    for path in (ROOT/'work/desenvolvimento/transacao.json', folder/'transacao.json'):
        if path.exists():
            raise ValueError('Transação pendente: recuperar e revalidar antes de copiar')
    if list(folder.glob('*.partial')):
        raise ValueError('Construção parcial no diretório selecionado')


def deliver(folder, destination=DESTINATION):
    folder = folder.resolve()
    destination = destination.resolve()
    # A destination override is only permitted for isolated tests inside work/.
    if destination != DESTINATION.resolve() and not destination.is_relative_to(ROOT/'work'):
        raise ValueError('Destino não autorizado')
    if not folder.is_relative_to(ROOT/'work'):
        raise ValueError('Selecionar construção consolidada sob work/')
    check_pending(folder)
    report_path = folder/'relatorio.json'
    report_raw = report_path.read_bytes()
    report = json.loads(report_raw)
    if not report.get('valid') or 'iso' not in report:
        raise ValueError('Construção incompleta ou inválida')
    iso = report['iso']
    name = iso['image_name']
    if Path(name).name != name or not name.startswith('MetalSaga-ptbr-') or not name.endswith('.iso'):
        raise ValueError('Nome de imagem inválido')
    source = folder/name
    if source.is_symlink() or source.resolve().parent != folder:
        raise ValueError('Imagem deve ser arquivo local independente')
    expected = iso['output_iso_sha256']
    size = iso['iso_size']
    if not iso.get('all_bytes_match_expected_patch') or not iso.get('iso_directory_identical'):
        raise ValueError('Construção sem verificação integral')
    before_stat = source.stat()
    if before_stat.st_size != size or checksum(source) != expected:
        raise ValueError('Integridade da ISO de origem não confere')
    destination.mkdir(parents=True, exist_ok=True)
    final = destination/FILENAME
    if final.is_symlink():
        raise ValueError('Destino não pode ser link')
    descriptor, temporary_name = tempfile.mkstemp(prefix='.MetalSaga-', suffix='.partial', dir=destination)
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, 'wb') as output, source.open('rb') as stream:
            for block in iter(lambda: stream.read(4 * 1024 * 1024), b''):
                output.write(block)
            output.flush()
            os.fsync(output.fileno())
        if temporary.stat().st_size != size or checksum(temporary) != expected:
            raise ValueError('Integridade da cópia temporária não confere')
        check_pending(folder)
        after_stat = source.stat()
        if (after_stat.st_size, after_stat.st_mtime_ns) != (before_stat.st_size, before_stat.st_mtime_ns) or checksum(source) != expected:
            raise ValueError('Origem mudou durante a transferência')
        if report_path.read_bytes() != report_raw:
            raise ValueError('Relatório mudou durante a transferência')
        os.replace(temporary, final)
        if final.stat().st_size != size or checksum(final) != expected:
            raise ValueError('Integridade da cópia final não confere')
    finally:
        if temporary.exists():
            temporary.unlink()
    return {'source':source.relative_to(ROOT).as_posix(), 'destination':str(final),
            'sha256':expected, 'size':size, 'source_preserved':True,
            'local_copy_verified':True, 'cloud_sync_confirmed':False}


def main():
    parser = argparse.ArgumentParser(description='Copiar ISO validada para OneDrive somente por solicitação explícita')
    parser.add_argument('--build-dir', type=Path, required=True)
    parser.add_argument('--report', type=Path, required=True)
    args = parser.parse_args()
    output = args.report.resolve()
    if not output.is_relative_to(ROOT/'reports') or output.exists():
        raise ValueError('Usar relatório novo sob reports/')
    result = deliver(args.build_dir)
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    print('Cópia local verificada: '+result['destination'])


if __name__ == '__main__':
    main()
