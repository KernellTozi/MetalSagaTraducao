"""Keep the ten newest generated work ISOs; preserve originals and recovery state."""
import argparse
import json
import os
from pathlib import Path
import time

ROOT=Path(__file__).resolve().parents[1]
WORK=ROOT/'work'
ORIGINAL=ROOT/'JOGO/Metal Saga.iso'
# User policy: experiments participate in the same chronological retention queue.
PINNED=()


def images_without_links(root):
    pending=[root]
    while pending:
        folder=pending.pop()
        with os.scandir(folder) as stream:
            for item in stream:
                path=Path(item.path)
                # Never descend through a junction or symlink, even to inventory
                # it: the target might be outside the authorized project.
                if item.is_symlink() or (hasattr(path,'is_junction') and path.is_junction()):continue
                if item.is_dir(follow_symlinks=False):pending.append(path)
                elif item.is_file(follow_symlinks=False) and path.suffix.lower()=='.iso':yield path


def plan(root=WORK,limit=10,reserve=0,pinned=PINNED):
    root=Path(root).resolve()
    if not root.is_relative_to(WORK.resolve()) or not root.is_dir():
        raise ValueError('ISO retention is restricted to work/')
    if not 1<=limit<=10 or not 0<=reserve<limit:raise ValueError('Invalid retention limit/reserve')
    protected={Path(p).resolve() for p in pinned};candidates=[];images=[]
    for path in images_without_links(root):
        resolved=path.resolve()
        if not resolved.is_relative_to(root):raise ValueError('ISO link escapes retention root')
        parents=[path,*path.parents[:len(path.parents)-len(root.parents)]]
        if any(p.is_symlink() or (hasattr(p,'is_junction') and p.is_junction()) for p in parents):
            raise ValueError('Refuse to prune linked ISO paths')
        if not path.is_file():continue
        stat=path.stat();item={'path':str(resolved),'size':stat.st_size,'mtime_ns':stat.st_mtime_ns}
        images.append(item)
        if resolved in protected or (path.parent/'transacao.json').exists():continue
        if not path.name.startswith('MetalSaga-ptbr-') or stat.st_nlink!=1:continue
        if ORIGINAL.exists() and path.samefile(ORIGINAL):continue
        candidates.append(item)
    count=max(0,len(images)+reserve-limit)
    candidates.sort(key=lambda p:(p['mtime_ns'],p['path']))
    if len(candidates)<count:raise ValueError('Cannot satisfy ISO limit without deleting protected/unknown files')
    return {'root':str(root),'limit':limit,'reserve':reserve,'before_count':len(images),
            'delete':candidates[:count],'remaining_count':len(images)-count,
            'original_excluded':True,'pinned_paths':[str(p) for p in sorted(protected)]}


def prune(root=WORK,limit=10,reserve=0,pinned=PINNED):
    result=plan(root,limit,reserve,pinned);log=WORK/'iso-retention.jsonl'
    for item in result['delete']:
        path=Path(item['path']);stat=path.stat()
        if stat.st_size!=item['size'] or stat.st_mtime_ns!=item['mtime_ns']:
            raise ValueError('ISO changed after retention planning')
        event={'time':time.time(),'action':'delete_old_generated_iso','file':item}
        with log.open('a',encoding='utf-8') as stream:stream.write(json.dumps({**event,'status':'planned'})+'\n')
        path.unlink()
        with log.open('a',encoding='utf-8') as stream:stream.write(json.dumps({**event,'status':'deleted'})+'\n')
    return result


def main():
    parser=argparse.ArgumentParser(description='Retenção de até dez ISOs de trabalho')
    parser.add_argument('--apply',action='store_true');parser.add_argument('--reserve',type=int,default=0)
    args=parser.parse_args();print(json.dumps((prune if args.apply else plan)(reserve=args.reserve),indent=2))


if __name__=='__main__':main()
