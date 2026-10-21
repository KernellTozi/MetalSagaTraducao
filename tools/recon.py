"""Read-only inventory, SDA boundaries and full-file ASCII candidate scan."""
from pathlib import Path
import argparse, hashlib, json, mmap, re, struct

ROOT = Path(__file__).resolve().parents[1]

def sha(path):
    with path.open('rb') as f:
        return hashlib.file_digest(f, 'sha256').hexdigest()

def sda(data):
    if data[:4] != b'sda\0' or len(data) < 12:
        return None
    size, count = struct.unpack_from('<II', data, 4)
    if count > (len(data)-12)//4:
        return {'valid': False, 'reason': 'table exceeds file'}
    offsets = list(struct.unpack_from(f'<{count}I', data, 12))
    valid = size == len(data) and bool(offsets) and 12+4*count <= offsets[0] and all(a <= b <= size for a,b in zip(offsets, offsets[1:]+[size]))
    return {'valid': valid, 'size': size, 'count': count, 'offsets': offsets,
            'heads': [data[o:o+16].hex() for o in offsets] if valid else []}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--source', type=Path, default=ROOT/'JOGO/Metal Saga')
    parser.add_argument('--output', type=Path, default=ROOT/'reports/inventory.json')
    args = parser.parse_args()
    rows = []
    for p in sorted(args.source.rglob('*')):
        if not p.is_file():
            continue
        with p.open('rb') as f, mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ) as d:
            hits = []
            count = 0
            for m in re.finditer(rb'[\x20-\x7e]{12,}', d):
                text = m.group()
                if b' ' not in text or not re.search(rb'[A-Za-z]{3}', text):
                    continue
                count += 1
                # Keep offsets/lengths only: no bulk copyrighted text in Git.
                if len(hits) < 30:
                    hits.append({'offset': m.start(), 'length': len(text)})
            elf = None
            if d[:4] == b'\x7fELF':
                elf = dict(zip(['type','machine','version','entry','phoff','shoff'], struct.unpack_from('<HHIIII',d,16)))
            rows.append({'path': p.relative_to(args.source).as_posix(), 'size': len(d),
                         'sha256': sha(p), 'head': d[:32].hex(), 'elf': elf,
                         'sda': sda(d), 'ascii_candidates': count, 'candidate_offsets': hits})
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(rows,indent=2)+'\n',encoding='utf-8')
    print(f'{len(rows)} files; {sum(r["size"] for r in rows)} bytes; {sum(bool(r["sda"] and r["sda"]["valid"]) for r in rows)} valid SDA tables')

if __name__ == '__main__':
    main()
