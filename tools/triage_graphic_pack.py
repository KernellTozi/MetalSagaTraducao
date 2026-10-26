"""Contact sheets and bound observations for the remaining-atlas transport pack."""
import argparse,collections,json
from pathlib import Path
from reinsertion import ROOT,local
from interface_atlas_pack import sources,entries,manifest,REMAINING_POLICY
from interface_texture_pack import pillow

# Human review of the 18 source contact sheets on 25/10/2026. Classification is
# texture-level, never a count of words or approval of runtime/UV associations.
REVIEW={
    'candidate-latin-interface':{'FD_POST':(0,3),'RLOADING':(2,), 'RMGALAN':(1,3),
        'RMGDANCE':(0,15,17),'RMGDOG':(2,),'RMGKAERU':(0,26,30,32,38),
        'RMGTANK':(0,2),'S_PAINT':(8,13)},
    'candidate-mixed-protected-category':{'S_PAINT':(6,)},
    'candidate-native-interface':{'RMGDOG':(0,)},
    'covered-text-review':{'FBS_DATA':(0,2,3),'FNAME_DT':(2,),'PASSWORD':(6,),'RTITLE':(0,)},
    'protected-names-artwork':{'FD_POST':(4,5,6,7,8,44)},
    'protected-control-markings':{'F_COMMON':(0,),'PASSWORD':(5,),'S_PAINT':(0,)}}


def review_report(output):
    output=Path(output).resolve()
    if not output.is_relative_to(ROOT/'reports') or output.exists():raise ValueError('Use new own reports metadata path')
    originals=sources(REMAINING_POLICY);rows=entries(originals);review=[];seen=set()
    from explore_interface_atlases import inspect
    for row in rows:
        stem=Path(row['resource']).stem
        classes=[name for name,groups in REVIEW.items() if row['entry'] in groups.get(stem,())]
        if len(classes)>1:raise ValueError('Ambiguous atlas visual classification')
        category=classes[0] if classes else 'no-localizable-word-observed'
        seen.add((stem,row['entry']))
        review.append({k:row[k] for k in ('id','resource','offset','size','sha256','source_sha256','texture')} |
            {'visual_class':category,'source_preview_reviewed':True,'iso_edit_approval':False,
             'limits':'Source atlas inspection; not a PS2 usage proof. Existing translated assets require overlay review; names/categories remain protected.'})
    required={(stem,index) for groups in REVIEW.values() for stem,indices in groups.items() for index in indices}
    if not required<=seen:raise ValueError('Reviewed atlas binding disappeared')
    unresolved=[{'resource':resource,'offset':r['offset'],'size':r['size'],'sha256':r['sha256'],'reason':r.get('reason')}
        for resource,raw in originals.items() for r in inspect(raw) if r['kind']=='unknown']
    result={'schema':1,'scope':'Human visual triage of all 119 recognized source atlases; unresolved records are not silently covered',
        'baseline_recipe':'translations/interface-v038.json','recognized_textures':len(review),'reviewed_textures':len(review),
        'reviewed_contact_sheets':18,'classes':dict(collections.Counter(r['visual_class'] for r in review)),
        'unresolved_structure_records':len(unresolved),'records':review,'unresolved':unresolved,
        'runtime_and_complete_game_coverage_proven':False,'originals_modified':False,'iso_created':False}
    with output.open('x',encoding='utf-8') as stream:json.dump(result,stream,ensure_ascii=False,indent=2);stream.write('\n')
    return result


def sheets(pack,output):
    pack=local(pack);output=local(output,True)
    actual=json.loads((pack/'manifest.json').read_text(encoding='utf-8'))
    rows=entries(sources(REMAINING_POLICY))
    if actual!=manifest(rows,REMAINING_POLICY):raise ValueError('Triage pack source bindings differ')
    Image=pillow()
    from PIL import ImageDraw
    output.mkdir(parents=True);groups=collections.defaultdict(list);result=[]
    for row in rows:groups[row['resource']].append(row)
    for resource,group in groups.items():
        for page in range(0,len(group),12):
            selected=group[page:page+12];sheet=Image.new('RGB',(1440,330*((len(selected)+3)//4)),(45,45,45))
            for i,row in enumerate(selected):
                path=pack/row['png']
                if path.is_symlink():raise ValueError('Linked preview blocked')
                with Image.open(path) as original:
                    # Index palette RGB, deliberately without normalizing PS2 alpha.
                    image=original.convert('RGBA').convert('RGB')
                image.thumbnail((352,294),Image.Resampling.NEAREST)
                x=i%4*360;y=i//4*330
                sheet.paste(image,(x+(360-image.width)//2,y+32))
                ImageDraw.Draw(sheet).text((x+4,y+4),row['id']+' @'+hex(row['offset']),fill='white')
            name=Path(resource).stem+'-'+str(page//12)+'.png';sheet.save(output/name)
            result.append({'resource':resource,'sheet':name,'ids':[r['id'] for r in selected]})
    with (output/'indice.json').open('x',encoding='utf-8') as stream:json.dump(result,stream,indent=2);stream.write('\n')
    return result


if __name__=='__main__':
    p=argparse.ArgumentParser(description='Preparar folhas de triagem dos atlas, sem alterar imagens ou ISO')
    p.add_argument('--pack',type=Path);p.add_argument('--output',type=Path)
    p.add_argument('--review-summary',type=Path,help='New reports/ path for the source-bound human review metadata')
    a=p.parse_args()
    if a.review_summary:
        if a.pack or a.output:p.error('Use review-summary separately from contact sheet generation')
        r=review_report(a.review_summary);print(f"{r['reviewed_textures']} texturas classificadas; estruturas desconhecidas preservadas")
    else:
        if not a.pack or not a.output:p.error('Contact sheets require --pack and --output')
        r=sheets(a.pack,a.output);print(f'{len(r)} folhas para revisão dos 119 atlas conhecidos')
