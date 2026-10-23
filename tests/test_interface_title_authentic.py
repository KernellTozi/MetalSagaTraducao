import copy,json,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools'))
from title_authentic import artwork,glyphs,compose,compile_authentic
from title_native_font import alphabet,RESOURCE
from interface_graphics import original
from interface_texture_pack import pillow,unpack_indices
from interface_textures import inspect_texture

class AuthenticTitle(unittest.TestCase):
    def test_native_letters_preserved_byte_for_byte(self):
        a=alphabet();b=glyphs()
        for c in 'CONTINUEWGAMSL':self.assertEqual(a[c].tobytes(),b[c].tobytes(),c)
        self.assertEqual(set(c for c in b if a[c].tobytes()!=b[c].tobytes()),{'V','J','R'})
    def test_no_scaling_and_labels_fit_border(self):
        for text in ('NOVO JOGO','RETOMAR','INSTALAR'):
            im=compose(text);self.assertEqual(im.height,24);self.assertLessEqual(im.width,224)
        a=glyphs();im=compose('NO')
        self.assertEqual(im.crop((0,0,a['N'].width,24)).tobytes(),a['N'].tobytes())
        self.assertEqual(im.crop((a['N'].width,0,a['N'].width+1,24)).getbbox(),None)
    def test_atlas_palette_frames_and_decorations(self):
        before=original(RESOURCE);after,r=artwork();self.assertEqual(len(before),len(after));self.assertEqual(before[:1072],after[:1072])
        Image=pillow();meta,_=inspect_texture(before[32:66608]);a=Image.frombytes('L',(256,256),unpack_indices(before[32:66608],meta));b=Image.frombytes('L',(256,256),unpack_indices(after[32:66608],meta))
        for old,new in (((1,74,6,78),(240,0,245,4)),((0,96,228,136),(0,48,228,88)),((0,136,228,176),(0,88,228,128))):self.assertEqual(a.crop(old).tobytes(),b.crop(new).tobytes())
        self.assertEqual(r['credit']['screen_rect'][1:], [428,414,444])
        self.assertEqual(b.crop((0,152,256,238)).getbbox(),None)
    def test_recipe_rejects_changed_credit_or_parent(self):
        cfg=json.loads((ROOT/'translations/interface-graphics-v009.json').read_text(encoding='utf-8'))
        patches,r=compile_authentic(cfg);self.assertEqual(r['accepted'],44)
        for key in ('source_sha256','parent','reviewed_artwork'):
            bad=copy.deepcopy(cfg)
            if key=='parent':bad[key]['sha256']='0'*64
            elif key=='reviewed_artwork':bad[key]['credit']['body_size']=12
            else:bad[key]='0'*64
            with self.assertRaises(ValueError):compile_authentic(bad)
    def test_v013_changes_only_title_recipe(self):
        a=json.loads((ROOT/'translations/interface-v012.json').read_text(encoding='utf-8'));b=json.loads((ROOT/'translations/interface-v013.json').read_text(encoding='utf-8'))
        for key in ('entries','base_dialogue_draft','layout_profile','battle_spacing','restored_originals'):self.assertEqual(a[key],b[key])

if __name__=='__main__':unittest.main()
