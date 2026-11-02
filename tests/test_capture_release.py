import copy,json,mmap,struct,sys,unittest
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
import capture_release as c


class CaptureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from interface_text import compile_draft
        cls.elf=c.ELF.read_bytes();cls.raw=c.original(c.SPACK)
        cls.parent=json.loads((c.ROOT/c.PARENT_UI).read_bytes())
        cls.parents,cls.report=compile_draft(cls.elf,cls.parent)
        cls.new,cls.rev,cls.evidence=c.derive(cls.elf,cls.parents)
        cls.manifest=json.loads((c.ROOT/c.MANIFEST).read_bytes());cls.child=json.loads((c.ROOT/c.UI).read_bytes())
        cls.f=c.MAP.open('rb');cls.data=mmap.mmap(cls.f.fileno(),0,access=mmap.ACCESS_READ)

    @classmethod
    def tearDownClass(cls):cls.data.close();cls.f.close()

    def test_manifest_and_twenty_new_units(self):
        self.assertEqual(c.template(self.elf,self.parents),self.manifest)
        self.assertEqual(len(self.new),18);self.assertEqual(len(self.rev),6)
        self.assertEqual(len(self.new)+2,20)

    def test_all_patch_spans_preserved(self):
        for p in self.new+self.rev:
            self.assertEqual(len(p['before']),len(p['after']))
            if p['resource']=='SLUS_212.93':
                self.assertEqual(c.FORMAT.findall(p['before']),c.FORMAT.findall(p['after']))
                self.assertEqual(p['before'].count(b'\n'),p['after'].count(b'\n'))
                self.assertEqual(p['after'][-1],0)

    def test_ore_and_approved_names_fit_sixteen_bytes(self):
        from item_names import catalog
        rows={r['index']:r for r in catalog(self.raw)}
        self.assertEqual(set(c.NAMES),{190,336,665,666,667})
        for index,(_,text) in c.NAMES.items():
            p=next(p for p in self.new+self.rev if p['id']==f'item.name.{index:04d}')
            self.assertEqual(len(p['after']),24)
            value=p['after'].split(b'\0')[0];self.assertEqual(c.text_decode(value),text);self.assertLessEqual(len(value),16)
            at=rows[index]['offset'];record=bytearray(self.raw[at:at+128]);record[:24]=p['after']
            self.assertEqual(record[24:],self.raw[at+24:at+128])

    def test_assembly_cardinals_keep_four_original_pointers(self):
        self.assertEqual(struct.unpack_from('<4I',self.elf,0x2fcb38),tuple(a+0xff000 for a in (0x349ea0,0x349ea8,0x349eb0,0x349eb8)))
        for number,at in enumerate((0x349ea0,0x349ea8,0x349eb0,0x349eb8),1):
            p=next(p for p in self.new if p['resource']=='SLUS_212.93' and p['offset']==at)
            self.assertEqual(p['after'],str(number).encode()+bytes(7))
        fmt=next(p for p in self.rev if p['id']=='elf.ui.00341ca8')
        self.assertEqual(c.text_decode(fmt['after'].split(b'\0')[0]),'Escolha a peça %s.')

    def test_learning_prompt_keeps_first_line_and_parameters(self):
        p=next(p for p in self.new if p['id']=='capture.learn.prompt')
        self.assertEqual(len(p['after']),32)
        self.assertEqual(p['before'].split(b'\n')[0],p['after'].split(b'\n')[0])
        self.assertIn(c.encode('Quem aprenderá?'),p['after'])

    def test_search_and_equipment_caption_are_distinct_literals(self):
        by={p['id']:p for p in self.new}
        self.assertEqual(by['capture.elf.003179b0']['after'].split(b'\0')[0],b'Sem inimigos por perto.')
        self.assertEqual(by['capture.elf.00349540']['after'],b'Equipar\0')
        self.assertFalse(any(p['offset']==0x31a794 for p in self.new))

    def test_location_names_preserve_proper_names_and_node_boundaries(self):
        locations=[p for p in self.new if p['resource']==c.MCT]
        self.assertEqual(len(locations),7)
        for p in locations:
            self.assertLessEqual(len(p['after']),32)
            text=c.text_decode(p['after'].split(b'\0')[0]);self.assertIn(text,c.LOCATIONS.values())
            self.assertEqual(p['before'],self.data[p['offset']:p['offset']+len(p['before'])])
        self.assertIn('Iwasaki',c.LOCATIONS['Iwasaki Medical Laboratory'])
        self.assertIn('Grand Master',c.LOCATIONS["Grand Master's Tent"])
        self.assertEqual(len(c.encode(c.LOCATIONS['Mysterious Transport Pod'])),31)

    def test_new_native_header_preserves_all_earlier_cells(self):
        parent=next(p for p in self.parents if p['id']=='observed.headers')
        p=next(p for p in self.rev if p['id']==parent['id'])
        self.assertEqual(p['before'],parent['before'])
        for i,(a,b) in enumerate(zip(parent['after'],p['after'])):
            if a!=b:self.assertTrue(4<=i%256<176 and 180<=i//256<192)
        self.assertEqual(self.evidence['observed.headers']['width'],159)
        self.assertFalse(self.evidence['observed.headers']['resized'])

    def test_ui_pool_preserves_every_alias_and_other_string(self):
        from plan_interface_menus import counted_strings
        parent=next(p for p in self.parents if p['id']=='spack.ui.table')
        revised=next(p for p in self.rev if p['id']==parent['id'])
        old=counted_strings(parent['after'],0,8192,378);new=counted_strings(revised['after'],0,8192,378)
        expected={tuple(r['pointer_ids']):(c.encode('Combinar peças') if 318 in r['pointer_ids'] else bytes.fromhex(r['source_hex'])) for r in old['entries']}
        self.assertEqual({tuple(r['pointer_ids']):bytes.fromhex(r['source_hex']) for r in new['entries']},expected)

    def test_renascimento_reaction_preserves_other_texts_keys_and_opaque_tail(self):
        from spack_interactions import catalog
        parent=next(p for p in self.parents if p['id']=='spack.reaction.pool')
        revised=next(p for p in self.rev if p['id']==parent['id'])
        at=parent['offset'];old=bytearray(self.raw);new=bytearray(self.raw)
        old[at:at+len(parent['after'])]=parent['after'];new[at:at+len(revised['after'])]=revised['after']
        a=catalog(old,'reaction');b=catalog(new,'reaction')
        expected={tuple(r['references']):bytes.fromhex(r['source_hex']).replace(b'Revigorante',b'Renascimento') for r in a['rows']}
        self.assertEqual({tuple(r['references']):bytes.fromhex(r['source_hex']) for r in b['rows']},expected)
        limit=self.evidence['spack.reaction.pool']['text_limit']
        self.assertEqual(parent['after'][limit:],revised['after'][limit:])
        for i in range(179):self.assertEqual(parent['after'][4+i*16:8+i*16],revised['after'][4+i*16:8+i*16])

    def test_first_strike_keeps_atlas_palette_and_other_art(self):
        from discover_credits import decode
        from battle_menu_atlas import tim2
        p=next(p for p in self.new if p['id']=='capture.battle.first-strike')
        old,_,_=decode(p['before'],maximum=66624);new,used,_=decode(p['after'],maximum=66624)
        self.assertEqual(old[:64],new[:64]);self.assertEqual(old[65600:],new[65600:])
        self.assertFalse(any(p['after'][used:]))
        rects=[r['rect'] for r in self.evidence['strike']['labels']]
        a,_=tim2(old);b,_=tim2(new)
        for i,(x,y) in enumerate(zip(a,b)):
            if x!=y:self.assertTrue(any(l<=i%256<r and t<=i//256<z for l,t,r,z in rects))
        self.assertEqual(len(rects),2);self.assertGreater(self.evidence['strike']['native_decoder_steps'],0)

    def test_pun_structure_controls_and_laughter(self):
        from reinsertion import control_check
        from dialogue_formats import parse_msg
        spec=c.pun_spec(self.data);parsed,_=parse_msg(self.data,spec['offset'])
        value=c.encode(c.PUN);control_check(bytes.fromhex(parsed['original_text_hex']),value)
        self.assertLessEqual(len(value),spec['capacity'])
        self.assertEqual(value.split(b'\t')[1],b'Mwahahahaha!')
        self.assertIn(b'Dis...assembler',value)

    def test_narrative_compiles_one_body_with_same_record_and_header(self):
        from build_translation_pilot import load_draft
        draft,_=load_draft(c.ROOT/c.NARRATIVE)
        doc,patches,report=c.compile_narrative(self.data,draft)
        p=next(p for p in patches if p['id']==c.PUN_ID);spec=self.manifest['evidence']['pun']
        self.assertEqual(c.sha(p['after']),spec['after_sha256']);self.assertEqual(len(p['after']),88)
        self.assertEqual(p['before'][:32],p['after'][:32]);self.assertEqual(report['capture_context_review']['revised_bodies'],1)

    def test_ui_merge_preserves_other_parent_patches_and_counts(self):
        with patch('interface_text.compile_draft',return_value=(copy.deepcopy(self.parents),copy.deepcopy(self.report))):
            out,report=c.compile_interface(self.elf,self.child)
        changed={p['id'] for p in self.rev};by={p['id']:p for p in out}
        for p in self.parents:
            if p['id'] not in changed:self.assertEqual(p,by[p['id']])
        self.assertEqual(report['accepted'],4362);self.assertEqual(report['item_names']['accepted'],633)
        self.assertEqual(report['capture_release']['new_units'],20)

    def test_child_and_narrative_mutations_are_rejected(self):
        bad=copy.deepcopy(self.child);bad['layout_profile']='bad'
        with self.assertRaises(ValueError):c.validate_interface(bad)
        from build_translation_pilot import load_draft
        draft,_=load_draft(c.ROOT/c.NARRATIVE);draft['translations'][c.PUN_ID]='Outra fala.'
        with self.assertRaises(ValueError):c.validate_narrative(draft)
        bad=copy.deepcopy(self.child);bad['capture_release']['sha256']='0'*64
        with self.assertRaises(ValueError):c.validate_interface(bad)

    def test_revitalizer_prefix_and_comparator_parent_are_narrow(self):
        from verify_interface_revision import normalize_item_name_review_transition
        old={(p['resource'],p['offset']):p for p in self.parents}
        new={k:p for k,p in old.items()}
        for p in self.rev:new[(p['resource'],p['offset'])]=p
        normalize_item_name_review_transition(self.parent,self.child,c.ROOT/c.PARENT_UI,old,new)
        at=next(p['offset'] for p in self.rev if p['id']=='item.name.0336')
        self.assertEqual(len(old[(c.SPACK,at)]['before']),24)
        with self.assertRaises(ValueError):normalize_item_name_review_transition(self.parent,self.child,c.ROOT/'translations/interface-v061.json',old,new)


if __name__=='__main__':unittest.main()
