"""Six user-reviewed paint buttons; pixel-plane patch, never whole SDA import."""
import json
from reinsertion import ROOT
from dialogue import sha
from glyph_spacing import ORIGINAL_SHA
from interface_texture_pack import pillow,unpack_indices,replace_indices
from paint_button_pack import inventory
from paint_graphic_proposals import TARGETS,render_crop,usage_proof

POLICY='paint-six-reviewed-main-menu-buttons-v001'
APPROVAL='reports/pintura-graficos-aprovacao-v001.json'
PIXELS_SHA='76c68dc7cf4ea9eaed43dddeabc5010637578b7db9a6ed7826f3c2c4aacdd16c'


def render(raw,manifest):
    rows=[r for r in manifest['entries'] if r['texture_entry']==13]
    first=rows[0];at=first['texture_offset'];size=first['texture_size'];meta=first['texture']
    before=raw[at:at+size];old=unpack_indices(before,meta);indices=bytearray(old)
    Image=pillow();pal=before[16:meta['pixel_offset']]
    source=Image.frombytes('P',(meta['width'],meta['height']),old)
    source.putpalette(bytes(c for i in range(256) for c in pal[4*i:4*i+3]))
    source.info['transparency']=bytes(pal[4*i+3] for i in range(256))
    result=[]
    for row in rows:
        i=row['sprite_index']
        if i not in TARGETS:continue
        x,y,z,w=row['rect'];crop=source.crop((x,y,z,w));after,layout=render_crop(crop,TARGETS[i])
        data=after.tobytes()
        for yy in range(w-y):
            start=(y+yy)*meta['width']+x
            indices[start:start+z-x]=data[yy*(z-x):(yy+1)*(z-x)]
        result.append({'id':row['id'],'translation':TARGETS[i],'rect':row['rect'],
            'ganm_sha256':row['ganm_sha256'],'source_crop_indices_sha256':sha(crop.tobytes()),
            'target_crop_indices_sha256':sha(data),'mask_sha256':layout['mask_sha256'],
            'capital_body_pixels':layout['capital_body_pixels'],'baseline':layout['baseline_in_crop'],
            'horizontal_scale':layout['horizontal_scale']})
    allowed=[r['rect'] for r in result]
    for i,(a,b) in enumerate(zip(old,indices)):
        if a!=b and not any(x+2<=i%meta['width']<z-2 and y+2<=i//meta['width']<w-2 for x,y,z,w in allowed):
            raise ValueError('Paint art changed outside six approved interiors')
    after=replace_indices(before,indices);p=meta['pixel_offset'];n=meta['pixel_bytes']
    if after[:p]!=before[:p] or after[p+n:]!=before[p+n:]:raise ValueError('Paint header/palette/alpha/tail changed')
    if replace_indices(after,old)!=before:raise ValueError('Paint art reverse round-trip differs')
    if sha(after[p:p+n])!=PIXELS_SHA:raise ValueError('Paint raster differs from user-reviewed pixel output')
    return {'resource':manifest['resource'],'id':'paint.menu.six-reviewed-buttons','offset':at+p,
        'before':before[p:p+n],'after':after[p:p+n]},result


def approval():
    path=ROOT/APPROVAL;raw=path.read_bytes();value=json.loads(raw)
    expected_ids=[f'paint.button.13.{i:02d}' for i in TARGETS]
    if (value.get('approved_art_ids')!=expected_ids or value.get('target_pixel_sha256')!=PIXELS_SHA
        or value.get('user_art_approved') is not True or value.get('runtime_visual_validation') is not False):
        raise ValueError('Paint art approval evidence differs')
    return {'report':APPROVAL,'sha256':sha(raw)}


def config(elf):
    raw,manifest=inventory()
    if sha(elf)!=ORIGINAL_SHA:raise ValueError('Paint original ELF differs')
    evidence=usage_proof(elf,raw);patch,rows=render(raw,manifest)
    return {'policy':POLICY,'source_sha256':sha(raw),'elf_sha256':sha(elf),
        'bound_windows':evidence['bound_windows'],'art_approval':approval(),
        'pixel_offset':patch['offset'],'pixel_size':len(patch['after']),
        'target_pixel_sha256':PIXELS_SHA,'entries':rows}


def compile_graphics(elf,value):
    from interface_remainder_graphics import PAINT_POLICY
    if value.get('policy')==PAINT_POLICY:
        from interface_remainder_graphics import compile_paint
        return compile_paint(elf,value)
    expected=config(elf)
    if value!=expected:raise ValueError('Paint menu policy/source/geometry/approval/raster binding differs')
    raw,manifest=inventory();patch,rows=render(raw,manifest)
    return [patch],{'policy':POLICY,'accepted':6,'source_sha256':sha(raw),
        'art_approval':approval(),'target_pixel_sha256':PIXELS_SHA,'results':rows,
        'bound_windows':expected['bound_windows'],'original_scalar_forwarding_cases':8,
        'protected_labels_and_six_other_crops_unchanged':True,'reverse_roundtrip':True,
        'palette_alpha_frames_ganm_sda_and_resource_size_unchanged':True,
        'runtime_visual_status':'pending_user_verification',
        'limits':'Only reviewed texture 13 pixel plane; never whole original-based SDA. File-load/forwarding snippets already tested; full dispatch/GPU/PCSX2 not executed.'}
