import copy
import json
import mmap
from pathlib import Path
import sys
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
import npc_menu_revision as v
import npc_default_names as n
import choice_text_metrics as c
from interface_text import SOURCE as ELF


class NpcMenuTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.elf=ELF.read_bytes();cls.stream=v.SOURCE.open('rb')
        cls.data=mmap.mmap(cls.stream.fileno(),0,access=mmap.ACCESS_READ)
        cls.child=json.loads((v.ROOT/'translations/interface-v060.json').read_bytes())
        cls.parent,cls.manifest=v.validate_interface(cls.child)
        cls.patches,cls.report=v.compile_additions(cls.data,cls.elf,cls.manifest)

    @classmethod
    def tearDownClass(cls):cls.data.close();cls.stream.close()

    def test_108_fields_55_labels_and_two_boys(self):
        rows=n.catalog(self.data);entries=self.manifest['entries']
        self.assertEqual(len(rows),409);self.assertEqual(len(entries),108)
        self.assertEqual(len({r['translation'] for r in entries}),55)
        self.assertEqual(sum(r['translation']=='Menino' for r in entries),2)
        self.assertEqual(sum(r['source'] is None for r in rows),19)
        self.assertEqual(len(self.patches),109)

    def test_fixed_fields_no_ids_offsets_attributes_or_other_names_changed(self):
        rows=n.catalog(self.data);patches={p['id']:p for p in self.patches}
        directory=bytearray(self.data[n.BASE:n.BASE+4+n.COUNT*n.STRIDE])
        for r in rows:
            p=patches.get(r['id'])
            if p:
                self.assertEqual(p['before'],r['field']);self.assertEqual(len(p['after']),32)
                zero=p['after'].index(0);self.assertFalse(any(p['after'][zero:]))
                at=p['offset']-n.BASE;directory[at:at+32]=p['after']
        self.assertEqual(directory[:4],self.data[n.BASE:n.BASE+4])
        for r in rows:
            at=r['record_offset']-n.BASE
            self.assertEqual(directory[at:at+12],r['record'][:12])
            if r['id'] not in patches:self.assertEqual(directory[at:at+44],r['record'])

    def test_original_virtual_getter_returns_translated_model_field(self):
        rows={r['id']:r for r in n.catalog(self.data)}
        for p in self.patches:
            if p['resource']!=n.RESOURCE:continue
            r=rows[p['id']];result=n.getter_probe(self.elf,r['record'][:12]+p['after'])
            self.assertEqual(result['returned_name_offset_in_record'],12)
            self.assertTrue(result['original_virtual_getter_executed'])
            self.assertTrue(result['only_stack_writes'])

    def test_explicit_labels_and_13_pending_names_are_not_hidden_by_fallback(self):
        r=n.catalog(self.data)[0]
        for name in [b'Worker',b'Nina',b'Hunter',b'Soldier']:
            proof=n.getter_probe(self.elf,r['record'],explicit=name)
            self.assertTrue(proof['explicit_name_preserved'])
        self.assertTrue(self.report['explicit_13_labels_still_pending'])

    def test_sim_nao_reproduce_old_error_and_use_actual_advances_afterward(self):
        for text,old,new in [('Sim',22,30),('Não',44,33)]:
            before=c.execute(self.elf,text,patched=False,mode=1)
            after=c.execute(self.elf,text,mode=1)
            self.assertEqual(before['width'],old);self.assertEqual(after['width'],new)
            self.assertEqual(after['width'],sum(after['glyph_advances']))
            self.assertEqual(after['height'],22)

    def test_modes_sizes_accents_empty_and_native_fullwidth(self):
        for mode in (0,1,2):
            for side in (19,22,26):
                for text in ('Sim','Não','Cancelar','Cão','',b'\x82\xa0\x82\xa2'):
                    r=c.execute(self.elf,text,mode=mode,side=side)
                    self.assertEqual(r['width'],sum(r['glyph_advances']))
                    self.assertEqual(r['height'],side)
                    self.assertTrue(r['callee_saved_and_stack_preserved'])
                r=c.execute(self.elf,b'\x82\xa0\x82\xa2',mode=mode,side=side)
                self.assertEqual(r['width'],2*side)
        multi=c.execute(self.elf,'Sim\nNão')
        self.assertEqual((multi['width'],multi['height']),(33,44))

    def test_wrapper_within_48_bytes_keeps_style_scale_and_draw_font(self):
        p=c.elf_patch(self.elf)
        self.assertEqual((p['offset'],len(p['before']),len(p['after'])),(0x99f78,48,48))
        for text in ('Sim','Não','Configurar'):
            r=c.execute(self.elf,text,style=0x1234)
            self.assertEqual(r['style'],0x1234);self.assertEqual(r['scale_bits'],0x3f666666)
            self.assertTrue(all(at in (0x20,0x2c,0x30,0x56) for at,_ in r['row_write_intervals']))

    def test_wrong_manifest_and_patch_metrics_are_rejected(self):
        for key in ['choice_patch_sha256','model_directory_sha256']:
            bad=copy.deepcopy(self.manifest);bad[key]='0'*64
            with self.assertRaises(ValueError):v.compile_additions(self.data,self.elf,bad)
        bad=copy.deepcopy(self.manifest);bad['entries'][0]['translation']='Outro nome'
        with self.assertRaises(ValueError):v.compile_additions(self.data,self.elf,bad)

    def test_wrong_source_model_field_and_native_code_are_rejected(self):
        bad=bytearray(self.elf);bad[c.START]^=1
        with self.assertRaises(ValueError):c.elf_patch(bytes(bad))
        bad_entries=copy.deepcopy(self.manifest['entries']);bad_entries[0]['offset']+=1
        with self.assertRaises(ValueError):n.compile_names(self.data,self.elf,bad_entries)

    def test_unrelated_child_changes_are_refused(self):
        for key,value in [('iso_name','bad.iso'),('status','other'),('layout_profile','other')]:
            bad=copy.deepcopy(self.child);bad[key]=value
            with self.assertRaises(ValueError):v.validate_interface(bad)
        bad=copy.deepcopy(self.child);bad['npc_and_choice_release']['sha256']='0'*64
        with self.assertRaises(ValueError):v.validate_interface(bad)

    def test_exact_parent_required_by_comparator_and_capacity_auditor(self):
        from verify_interface_revision import normalize_item_name_review_transition
        normalize_item_name_review_transition(self.parent,self.child,v.ROOT/v.PARENT,{}, {})
        with self.assertRaises(ValueError):
            normalize_item_name_review_transition(self.parent,self.child,v.ROOT/'translations/interface-v058.json',{}, {})
        from item_name_capacity import apply_authorized_fallback
        old=json.loads((v.ROOT/'reports/capacidade-nomes-v001.json').read_bytes())
        self.assertEqual(apply_authorized_fallback(old,v.ROOT/'translations/interface-v060.json')['counts']['blocked'],0)


if __name__=='__main__':unittest.main()
