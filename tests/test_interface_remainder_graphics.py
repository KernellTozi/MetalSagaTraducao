import copy,json,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools'))
import interface_remainder_graphics as r
from interface_text import SOURCE
from interface_texture_pack import unpack_indices

class InterfaceRemainderTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.elf=SOURCE.read_bytes();cls.recipe=json.loads((ROOT/'translations/interface-v047.json').read_text(encoding='utf-8'))
        cls.rules=r.rules_assets();cls.paint=r.paint_assets()

    def test_exact_five_panels_not_decorative_titles_or_posters(self):
        patches,report=r.compile_rules(self.recipe['minigame_rules_graphics'])
        self.assertEqual(report['accepted'],5)
        self.assertEqual([v['id'] for _,v,_,_ in self.rules],list(r.PANELS))
        self.assertEqual({p['resource'] for p in patches},{'DATA/RDATA/'+n+'.SDA' for n in ('RMGALAN','RMGDANCE','RMGKAERU','RMGTANK')})
        self.assertEqual(report['runtime_visual_status'],'pending_user_verification')

    def test_frame_padding_palette_alpha_and_source_plane_roundtrip(self):
        for patch,report,before,after in self.rules:
            a,b=before.tobytes(),after.tobytes()
            self.assertEqual(before.getpalette(),after.getpalette())
            self.assertEqual(before.info['transparency'],after.info['transparency'])
            for y in range(512):
                if y<4 or y>=396:self.assertEqual(a[y*512:(y+1)*512],b[y*512:(y+1)*512])
                else:
                    self.assertEqual(a[y*512:y*512+4],b[y*512:y*512+4])
                    self.assertEqual(a[y*512+508:(y+1)*512],b[y*512+508:(y+1)*512])
            self.assertTrue(report['reverse_roundtrip'])
            self.assertEqual(len(patch['before']),len(patch['after']))
            raw=r.original(patch['resource']);out=bytearray(raw);at=patch['offset']
            out[at:at+len(patch['after'])]=patch['after']
            self.assertEqual(out[:at],raw[:at]);self.assertEqual(out[at+len(patch['after']):],raw[at+len(patch['after']):])
            out[at:at+len(patch['before'])]=patch['before'];self.assertEqual(out,raw)

    def test_all_original_controller_icons_exact_including_start_and_powerups(self):
        counts=[]
        for _,report,before,after in self.rules:
            for icon in report['icons']:
                source=before.crop(icon['source_rect']).tobytes()
                self.assertEqual(after.crop(icon['target_rect']).tobytes(),source)
                self.assertEqual(r.sha(source),icon['indices_sha256'])
            counts.append(len(report['icons']))
        self.assertEqual(counts,[3,4,4,6,6])

    def test_original_opaque_text_colour_not_background_alpha_only(self):
        for _,report,before,after in self.rules:
            palette=after.getpalette()
            # A previous draft preview restricted itself to background alpha,
            # yielding invisible glyphs. The title must have bright pixels.
            box=report['rows'][0]['rect'];pixels=after.crop(box).tobytes()
            self.assertGreater(sum(sum(palette[i*3:i*3+3])>450 for i in pixels),20)

    def test_text_rows_uncondensed_inside_native_panel(self):
        for _,report,_,_ in self.rules:
            self.assertEqual(report['full_panel_rect'],[0,0,512,400])
            for row in report['rows']:
                x,y,z,w=row['rect'];self.assertTrue(4<=x<z<=508 and 4<=y<w<=396)
                self.assertEqual(row['horizontal_scale'],1)
            self.assertIn('Regras',[row['text'] for row in report['rows']])
            self.assertIn('Controles',[row['text'] for row in report['rows']])

    def test_config_mutations_are_rejected(self):
        for path in ('policy','source','geometry','text','raster','missing','duplicate'):
            bad=copy.deepcopy(self.recipe['minigame_rules_graphics'])
            if path=='policy':bad['policy']='relaxed'
            elif path=='source':bad['entries'][0]['source_sha256']='0'*64
            elif path=='geometry':bad['entries'][0]['full_panel_rect'][2]-=1
            elif path=='text':bad['entries'][0]['rows'][0]['text']='Outra regra'
            elif path=='raster':bad['entries'][0]['target_pixels_sha256']='0'*64
            elif path=='missing':bad['entries'].pop()
            else:bad['entries'].append(copy.deepcopy(bad['entries'][0]))
            with self.assertRaises(ValueError):r.compile_rules(bad)

    def test_paint_preserves_approved_six_and_all_main_sub_se_pixels(self):
        from paint_menu_graphics import render,config
        from paint_button_pack import inventory
        raw,manifest=inventory();old,_=render(raw,manifest)
        patches,report=r.compile_paint(self.elf,self.recipe['paint_menu_graphics'])
        self.assertEqual(report['accepted'],9);self.assertEqual(report['new_labels'],3)
        self.assertEqual(self.recipe['paint_menu_graphics']['parent_six_buttons'],config(self.elf))
        for patch,new,before,after in self.paint:
            if new['id']!='paint.button.13.01':continue
            row=next(v for v in manifest['entries'] if v['id']==new['id']);p=row['texture']['pixel_offset']
            rec=raw[row['texture_offset']:row['texture_offset']+row['texture_size']]
            baseline=rec[:p]+old['after'];source=r.pillow().frombytes('P',before.size,unpack_indices(baseline,row['texture']))
            for sprite in manifest['entries']:
                if sprite['texture_entry']==13 and sprite['sprite_index']!=1:
                    self.assertEqual(after.crop(sprite['rect']).tobytes(),source.crop(sprite['rect']).tobytes())
            self.assertEqual(after.crop((104,32,238,61)).tobytes(),before.crop((104,32,238,61)).tobytes())
        self.assertEqual(len(patches),3)

    def test_stamp_original_texture_and_geometry_argument_windows(self):
        from paint_button_pack import inventory
        raw,manifest=inventory();proof=r.stamp_proof(self.elf,raw,manifest)
        self.assertTrue(proof['texture_and_ganm_forwarding_executed'])
        self.assertEqual((proof['texture_entry'],proof['ganm_entry'],proof['sprite_index']),(8,9,19))
        elf=bytearray(self.elf);elf[0x64a4c]^=1
        with self.assertRaises(ValueError):r.stamp_proof(elf,raw,manifest)

    def test_remaining_paint_palette_roundtrip_and_228_caption_composition(self):
        from paint_captions import compile_captions
        from paint_button_pack import inventory
        raw,_=inventory();patches,_=r.compile_paint(self.elf,self.recipe['paint_menu_graphics'])
        captions,report=compile_captions(self.elf,self.recipe['paint_captions'],raw=raw)
        self.assertEqual(report['accepted'],228);out=bytearray(raw)
        for p in patches+captions:
            at=p['offset'];self.assertEqual(out[at:at+len(p['before'])],p['before']);out[at:at+len(p['after'])]=p['after']
        for p in reversed(patches+captions):out[p['offset']:p['offset']+len(p['before'])]=p['before']
        self.assertEqual(out,raw)
        for _,_,before,after in self.paint:
            self.assertEqual(before.getpalette(),after.getpalette());self.assertEqual(before.info['transparency'],after.info['transparency'])

    def test_root_recipe_preserves_every_non_graphic_parent_field(self):
        parent=json.loads((ROOT/r.PARENT).read_text(encoding='utf-8'));child=self.recipe
        allowed={'paint_menu_graphics','status','iso_name','interface_remainder_review','minigame_rules_graphics'}
        self.assertEqual({k:v for k,v in parent.items() if k not in allowed},{k:v for k,v in child.items() if k not in allowed})
        r.validate_interface(child)
        for path in ('entries','layout_profile','base_dialogue_draft','item_names'):
            bad=copy.deepcopy(child);bad[path]=None
            with self.assertRaises(ValueError):r.validate_interface(bad)

    def test_root_validator_dispatch_and_legacy_v046_still_valid(self):
        from interface_gaps import validate_interface
        validate_interface(self.recipe)
        validate_interface(json.loads((ROOT/r.PARENT).read_text(encoding='utf-8')))

    def test_reject_text_and_icon_overflow_before_export(self):
        key='RMGDANCE.0.000';spec=copy.deepcopy(r.PANELS[key]);raw=r.original(spec['resource'])
        from interface_atlas_pack import entries
        row=next(v for v in entries({spec['resource']:raw}) if v['id']==key)
        for operation in [('text',500,50,18,'Não cabe'),('icon',(295,90,406,118),500,50),('text',None,390,26,'Regras')]:
            bad={**spec,'operations':[operation]}
            with self.assertRaises(ValueError):r.render_panel(raw,row,bad)

if __name__=='__main__':unittest.main()
