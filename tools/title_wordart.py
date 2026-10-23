"""Apply approved complete-word indexed artwork to the established title atlas."""
import json
from pathlib import Path
from reinsertion import ROOT,local
from interface_graphics import original,sha
from interface_textures import inspect_texture
from interface_texture_pack import pillow,unpack_indices,replace_indices
from title_native_font import RESOURCE,LABELS
POLICY='title-approved-complete-word-art-v010'
NAMES=('novo-jogo','retomar','instalar')


def load_word(binding,palette):
    path=local(ROOT/binding['path'])
    if not path.is_relative_to(ROOT/'work') or path.is_symlink():raise ValueError('Word artwork must be a local work file')
    if sha(path.read_bytes())!=binding['file_sha256']:raise ValueError('Approved word file hash mismatch')
    Image=pillow()
    with Image.open(path) as im:
        if im.mode!='P' or im.size!=(228,24):raise ValueError('Keep indexed 228x24 word cell')
        if bytes(im.getpalette()[:768])!=bytes(v for c in palette for v in c[:3]):raise ValueError('Title palette RGB changed')
        if im.info.get('transparency')!=bytes(c[3] for c in palette):raise ValueError('Title raw alpha palette changed')
        indices=im.tobytes()
    if sha(indices)!=binding['indices_sha256']:raise ValueError('Approved word indices mismatch')
    return indices


def compile_wordart(config):
    if config.get('policy')!=POLICY:raise ValueError('Unknown complete-word title policy')
    parent=config['parent'];payload=(ROOT/parent['recipe']).read_bytes()
    if parent['recipe']!='translations/interface-graphics-v009.json' or sha(payload)!=parent['sha256']:raise ValueError('Word art parent mismatch')
    before=original(RESOURCE)
    if config.get('source_sha256')!=sha(before):raise ValueError('Word art source mismatch')
    from interface_graphics import compile_graphics
    patches,report=compile_graphics(json.loads(payload))
    old=next(p for p in patches if p['resource']==RESOURCE and p['id']=='title.texture.0')
    resource=bytearray(before);resource[old['offset']:old['offset']+len(old['after'])]=old['after']
    record=bytes(resource[32:66608]);meta,_=inspect_texture(record);pixels=bytearray(unpack_indices(record,meta))
    palette=[tuple(record[16+i*4:20+i*4]) for i in range(256)]
    if len(config['words'])!=3:raise ValueError('Exactly three approved words required')
    rows=[]
    for index,(name,text,binding) in enumerate(zip(NAMES,LABELS,config['words'])):
        if binding['text']!=text or Path(binding['path']).name!=name+'-paleta-original.png':raise ValueError('Word identity/order mismatch')
        indices=load_word(binding,palette)
        y0=(0,128,24)[index];x0=14 if index==1 else 0;width=256 if index==1 else 228
        for y in range(24):
            start=(y0+y)*256;pixels[start:start+width]=bytes(width)
            pixels[start+x0:start+x0+228]=indices[y*228:(y+1)*228]
        rows.append({'id':f'title.label.{index}','resource':RESOURCE,'texture':0,'family':'title',
            'index':index,'translation':text,'cell_size':[228,24],'indices_sha256':sha(indices),
            'file_sha256':binding['file_sha256'],'artwork_approved_by_user':True,'runtime_visual_status':'pending_user_verification'})
    after=replace_indices(record,pixels)
    previous=unpack_indices(record,meta);current=unpack_indices(after,meta)
    for i,(a,b) in enumerate(zip(previous,current)):
        x,y=i%256,i//256
        if a!=b and not ((x<228 and y<48) or 128<=y<152):raise ValueError('Word art escaped title label regions')
    if replace_indices(after,previous)!=record:raise ValueError('Word art reverse round-trip failed')
    new_patch={**old,'after':after[1040:]}
    patches=[new_patch if p is old else p for p in patches]
    results=[r for r in report['results'] if r.get('id') not in {f'title.label.{i}' for i in range(3)}]+rows
    return patches,{**report,'policy':POLICY,'results':results,'approved_words':config['words'],
        'prior_title_geometry_credit_and_executable_preserved':True,'reverse_roundtrip':True,
        'reviewed_artwork':{'words':config['words'],'frames':report['reviewed_artwork']['frames'],
            'credit':report['reviewed_artwork']['credit'],'source':'approved complete-word art'},
        'runtime_visual_status':'pending_user_verification'}
