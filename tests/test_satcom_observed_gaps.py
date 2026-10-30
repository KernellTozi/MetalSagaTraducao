import copy,json,mmap,sys,unittest
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
import satcom_observed_gaps as s
from interface_text import SOURCE,compile_draft,controls


class ObservedGapsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.elf=SOURCE.read_bytes()
        cls.child=json.loads((s.ROOT/'translations/interface-v056.json').read_bytes())
        cls.parent,cls.manifest=s.validate_interface(cls.child)
        cls.before,cls.old_report=compile_draft(cls.elf,cls.parent)
        cls.after,cls.report=compile_draft(cls.elf,cls.child)

    def test_exact_patch_set_all_prior_translations_preserved(self):
        a={p['id']:p for p in self.before};b={p['id']:p for p in self.after}
        self.assertEqual(set(a)-set(b),set())
        self.assertEqual({k for k in a if a[k]!=b[k]},{'fbs.texture.2'})
        added=set(b)-set(a);self.assertEqual(len(added),116)
        self.assertEqual(sum(k.startswith('map.exit.') for k in added),113)
        self.assertEqual(self.report['accepted'],3978)
        self.assertEqual(self.report['item_names'],self.old_report['item_names'])
        self.assertEqual(self.report['battle_atlas_release'],self.old_report['battle_atlas_release'])

    def test_delayed_shop_argument_and_financial_arguments_executed(self):
        proof=s.probes(self.elf)
        self.assertEqual(proof['shop_pointer'],0x42bb78)
        self.assertEqual((proof['current_pointer'],proof['current_model_value']),(0x42b1c0,200))
        self.assertEqual((proof['target_pointer'],proof['target_model_value']),(0x42b248,500))
        self.assertEqual([r['type'] for r in proof['exit_getters']],[6,7])

    def test_literal_parameters_currency_newline_and_original_final_nul(self):
        targets={p['offset']:p for p in self.after if p['id'].startswith('elf.observed.')}
        self.assertEqual(set(targets),set(s.LITERALS))
        for at,p in targets.items():
            self.assertEqual(len(p['before']),len(p['after']))
            self.assertEqual(controls(p['before'][:-1]),controls(p['after'].split(b'\0')[0]))
            self.assertEqual(p['before'][-1],0);self.assertEqual(p['after'][-1],0)
            self.assertEqual(p['before'],self.elf[at:at+len(p['before'])])
        for at in (0x32c1c0,0x32c248):
            a,b=targets[at]['before'],targets[at]['after']
            self.assertEqual(a.index(b'%8dG'),b.index(b'%8dG'))
        self.assertEqual(targets[0x32cb78]['after'].split(b'\0')[0],b'Qual loja?')

    def test_all_raw_occurrences_are_typed_unique_exit_prefixes(self):
        path=s.ROOT/'JOGO/Metal Saga'/s.RESOURCE
        with path.open('rb') as f,mmap.mmap(f.fileno(),0,access=mmap.ACCESS_READ) as data:
            rows=s.exit_rows(data);offsets=set();at=data.find(s.EXIT_SOURCE)
            while at>=0:offsets.add(at);at=data.find(s.EXIT_SOURCE,at+1)
            self.assertEqual(offsets,{r['offset'] for r in rows})
            self.assertEqual(len(rows),113)
            self.assertEqual(sum(r['node_type']==6 for r in rows),8)
            self.assertEqual(sum(r['node_type']==7 for r in rows),105)

    def test_nonzero_metadata_and_exit_ids_untouched_roundtrip(self):
        patches={p['id']:p for p in self.after};nonzero=0
        path=s.ROOT/'JOGO/Metal Saga'/s.RESOURCE
        with path.open('rb') as f,mmap.mmap(f.fileno(),0,access=mmap.ACCESS_READ) as data:
            for row in self.manifest['exits']:
                at=row['offset'];raw=data[at:at+row['record_size']];p=patches[row['id']]
                edited=p['after']+raw[len(p['after']):]
                self.assertEqual(edited[13:],raw[13:])
                self.assertEqual(edited[:14],b'Mapa do mundo\0')
                self.assertEqual(p['before']+edited[13:],raw)
                self.assertEqual(s.sha(data[row['node_offset']:row['node_offset']+16]),row['node_sha256'])
                nonzero+=any(raw[14:32])
        self.assertEqual(nonzero,86)

    def test_native_header_only_inside_ganm_cell_and_no_font_scaling(self):
        a=next(p for p in self.before if p['id']=='fbs.texture.2')
        b=next(p for p in self.after if p['id']=='fbs.texture.2')
        self.assertEqual(a['before'],b['before'])
        count=0
        for at,(x,y) in enumerate(zip(a['after'],b['after'])):
            if x!=y:
                self.assertTrue(104<=at%256<248 and 232<=at//256<248);count+=1
        self.assertGreater(count,0)
        mask,layout=s.header_mask()
        self.assertEqual(mask.size,(101,15));self.assertFalse(layout['scaling'])
        self.assertEqual(layout,self.manifest['header'])

    def test_unrelated_names_dialogues_layout_and_root_changes_rejected(self):
        for key,value in [('layout_profile','bad'),('base_dialogue_draft','bad'),('iso_name','bad.iso')]:
            bad=copy.deepcopy(self.child);bad[key]=value
            with self.assertRaises(ValueError):s.validate_interface(bad)
        bad=copy.deepcopy(self.child);bad['item_names']['entries'][0]['translation']='Outra coisa'
        with self.assertRaises(ValueError):s.validate_interface(bad)
        bad=copy.deepcopy(self.child);bad['satcom_gap_release']['sha256']='0'*64
        with self.assertRaises(ValueError):s.validate_interface(bad)

    def test_source_record_offset_or_mask_drift_blocks_compilation(self):
        for key in ('offset','mask'):
            bad=copy.deepcopy(self.manifest)
            if key=='offset':bad['exits'][0]['offset']+=1
            else:bad['header']['mask_sha256']='0'*64
            with patch.object(s,'template',return_value=bad):
                with self.assertRaisesRegex(ValueError,'source/proof/layout'):s.compile_interface(self.elf,self.child)

    def test_auditor_and_comparator_use_exact_parent(self):
        from item_name_capacity import apply_authorized_fallback
        from verify_interface_revision import normalize_item_name_review_transition
        old=json.loads((s.ROOT/'reports/capacidade-nomes-v001.json').read_bytes())
        report=apply_authorized_fallback(old,s.ROOT/'translations/interface-v056.json')
        self.assertEqual(report['counts']['blocked'],0)
        normalize_item_name_review_transition(self.parent,self.child,s.ROOT/s.PARENT,{}, {})
        with self.assertRaises(ValueError):
            normalize_item_name_review_transition(self.parent,self.child,s.ROOT/'translations/interface-v054.json',{}, {})


if __name__=='__main__':unittest.main()
