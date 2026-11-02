import copy,json,mmap,struct,sys,unittest
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
import tank_drinking_gaps as t


class TankDrinkingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from interface_text import compile_draft
        cls.elf=t.ELF.read_bytes();cls.parent=json.loads((t.ROOT/t.PARENT).read_bytes())
        cls.parents,cls.report=compile_draft(cls.elf,cls.parent)
        cls.rev,cls.new,cls.proof=t.derive(cls.elf,cls.parents)
        cls.child=json.loads((t.ROOT/t.CHILD).read_bytes());cls.manifest=json.loads((t.ROOT/t.MANIFEST).read_bytes())
        cls.stream=t.MAP.open('rb');cls.data=mmap.mmap(cls.stream.fileno(),0,access=mmap.ACCESS_READ)
    @classmethod
    def tearDownClass(cls):cls.data.close();cls.stream.close()

    def test_manifest_output_and_scoped_child(self):
        self.assertEqual(self.manifest['revised'],[t.metadata(p) for p in self.rev])
        self.assertEqual(self.manifest['new'],[t.metadata(p) for p in self.new])
        self.assertEqual(self.manifest['evidence'],self.proof)
        self.assertEqual(len(self.rev),1);self.assertEqual(len(self.new),10)
        self.assertEqual(t.validate(self.child)[0],self.parent)

    def test_headers_native_cells_and_cedilla(self):
        p=self.rev[0];old=next(q for q in self.parents if q['id']==p['id'])
        for i,(a,b) in enumerate(zip(old['after'],p['after'])):
            if a!=b:self.assertTrue(any(x<=i%256<z and y<=i//256<w for x,y,z,w,_ in t.HEADERS))
        marks=[(x,y) for y in (130,131) for x in range(118,256) if p['after'][y*256+x]==253]
        self.assertEqual(len(marks),2)
        self.assertEqual([r['translation'] for r in self.proof['headers']],['PEÇAS','NOME','SELECIONADOS'])
        for r in self.proof['headers']:self.assertEqual(r['cap_height'],10)

    def test_map_names_seven_occurrences_and_original_flags(self):
        rows=[p for p in self.new if p['resource']==t.MCT];self.assertEqual(len(rows),7)
        self.assertEqual({r['type'] for r in self.proof['map_labels']},{2,6,7})
        for p in rows:
            self.assertEqual(p['before'],self.data[p['offset']:p['offset']+len(p['before'])])
            self.assertEqual(len(p['before']),len(p['after']));self.assertLessEqual(len(p['after']),32)
        portal=next(p for p in rows if p['offset']==0x970d7dc)
        self.assertEqual(len(portal['after']),19);self.assertEqual(self.data[portal['offset']+31],255)
        self.assertEqual(portal['after'][-1],0)

    def test_location_title_limits_and_original_headers(self):
        rows=t.title_specs(self.data);self.assertEqual(rows,self.proof['titles'])
        self.assertEqual([r['capacity'] for r in rows],[23,19])
        for r in rows:self.assertLessEqual(len(t.encode(r['translation'])),r['capacity'])
        self.assertGreater(len(t.encode('- Prédios abandonados -')),rows[0]['capacity'])

    def test_location_titles_compile_through_existing_parser(self):
        from build_translation_pilot import load_draft
        draft,_=load_draft(t.ROOT/t.CHILD_MAP);doc,rows,report=t.compile_narrative(self.data,draft)
        self.assertEqual(report['accepted'],6044)
        for r in self.proof['titles']:
            p=next(p for p in rows if p['id']==r['id'])
            self.assertEqual(t.sha(p['after']),r['after_sha256']);self.assertEqual(p['before'][:48],p['after'][:48])
            self.assertEqual(len(p['before']),len(p['after']))

    def test_controller_legend_keeps_all_three_native_tokens(self):
        p=next(p for p in self.new if p['id']=='tank-gaps.drink-input')
        self.assertEqual(len(p['after']),32);self.assertEqual(p['after'].split(b'\0')[0],b'Beber:$\x81~ Sair:$\x81\x9b Ajuda:$\x81\xa2')
        self.assertEqual(t.re.findall(rb'\$\x81.',p['before']),t.re.findall(rb'\$\x81.',p['after']))
        self.assertFalse(any(p['before'][27:]))

    def test_hud_only_four_cells_numbers_art_and_decorative_titles_intact(self):
        p=next(p for p in self.new if p['id']=='tank-gaps.drinking-hud')
        rects=[r['clear_rect'] for r in self.proof['hud']]
        self.assertEqual([r['text'] for r in self.proof['hud']],['Tempo','Bebidas','BEBER','PERIGO'])
        for i,(a,b) in enumerate(zip(p['before'],p['after'])):
            if a!=b:self.assertTrue(any(x<=i%512<z and y<=i//512<w for x,y,z,w in rects))
        raw=t.original(t.NDATA);rec,meta=t.ndata_texture(raw,96,0xb6a800)
        self.assertEqual(p['before'],t.unpack_indices(rec,meta))

    def test_csml_palette_is_involution_and_uses_existing_colors(self):
        raw=t.original(t.NDATA);rec,_=t.ndata_texture(raw,96,0xb6a800);pal=t.display_palette(rec)
        self.assertEqual(pal[51],(0,83,163,127));self.assertEqual(pal[241],(237,229,217,127))
        for i in range(256):
            j=(i&~24)|((i&8)<<1)|((i&16)>>1)
            self.assertEqual((j&~24)|((j&8)<<1)|((j&16)>>1),i)

    def test_rules_icons_footer_border_and_padding_preserved(self):
        p=next(p for p in self.new if p['id']=='tank-gaps.drinking-rules')
        for i,(a,b) in enumerate(zip(p['before'],p['after'])):
            if a!=b:self.assertTrue(4<=i%512<508 and 4<=i//512<396)
        for icon in self.proof['rules']['icons']:
            x,y,z,w=icon['source_rect'];a,b,c,d=icon['target_rect']
            old=b''.join(p['before'][yy*512+x:yy*512+z] for yy in range(y,w))
            new=b''.join(p['after'][yy*512+a:yy*512+c] for yy in range(b,d))
            self.assertEqual(old,new);self.assertEqual(t.sha(new),icon['sha256'])

    def test_ui_merge_preserves_all_other_translations(self):
        with patch('interface_text.compile_draft',return_value=(copy.deepcopy(self.parents),copy.deepcopy(self.report))):
            rows,report=t.compile_interface(self.elf,self.child)
        by={p['id']:p for p in rows}
        for p in self.parents:
            if p['id']!='observed.headers':self.assertEqual(p,by[p['id']])
        self.assertEqual(report['accepted'],4379);self.assertEqual(report['item_names'],self.report['item_names'])
        self.assertEqual(report['tank_drinking_release']['new_units'],16)

    def test_reject_recipe_and_narrative_mutation(self):
        bad=copy.deepcopy(self.child);bad['layout_profile']='bad'
        with self.assertRaises(ValueError):t.validate(bad)
        from build_translation_pilot import load_draft
        draft,_=load_draft(t.ROOT/t.CHILD_MAP);draft['translations'][next(iter(t.TITLES))]='errado'
        with self.assertRaises(ValueError):t.validate_narrative(draft)

    def test_comparator_parent_and_patch_overlap(self):
        from verify_interface_revision import normalize_item_name_review_transition
        normalize_item_name_review_transition(self.parent,self.child,t.ROOT/t.PARENT,{}, {})
        with self.assertRaises(ValueError):normalize_item_name_review_transition(self.parent,self.child,t.ROOT/'translations/interface-v064.json',{}, {})
        rows=self.rev+self.new
        for i,a in enumerate(rows):
            for b in rows[i+1:]:
                if a['resource']==b['resource']:self.assertFalse(max(a['offset'],b['offset'])<min(a['offset']+len(a['before']),b['offset']+len(b['before'])))


if __name__=='__main__':unittest.main()
