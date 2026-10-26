import copy,json,struct,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools'))
import credits_translation as c
import credits_edit_pack as pack
from gfi import decode


class CreditsTranslationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.elf,cls.raw,cls.meta,cls.cat=pack.original()
        cls.config=json.loads((ROOT/'translations/creditos-v001.json').read_text(encoding='utf-8'))
        cls.patches,cls.report=c.compile_credits(cls.elf,cls.config)

    def test_all_translated_roles_readback_and_242_other_lines_preserved(self):
        self.assertEqual(self.report['accepted'],50)
        p=self.patches[0];self.assertEqual((p['offset'],len(p['before']),len(p['after'])),(0x800,4096,4096))
        decoded,used,_=pack.decode(p['after']);self.assertEqual(used,2433)
        rows=decoded[4:-2].split(b'\r\n');self.assertEqual(struct.unpack_from('<I',decoded)[0],292)
        self.assertEqual(len(rows),292);targets={r['id']:r['translation'] for r in self.config['entries']}
        changed=0
        for old,value in zip(self.cat['rows'],rows):
            source=bytes.fromhex(old['source_hex'])
            if old['id'] in targets:
                prefix=2 if source.startswith(b'\x81\x9f') else 0
                self.assertEqual(value[:prefix],source[:prefix]);self.assertEqual(decode(value[prefix:]),targets[old['id']])
            else:self.assertEqual(value,source)
            changed+=value!=source
        self.assertEqual(changed,50)

    def test_new_allocation_and_font_arguments_original_instructions(self):
        for size in (4222,4373,4478):
            proof=c.consumer_probe(self.elf,size)
            self.assertEqual(proof['decoded_allocation_request'],size)
            self.assertEqual(proof['consumer_size_from_compressed_header'],size)
            self.assertEqual(proof['constructor_font'],22)

    def test_decoder_parity_and_no_bytes_outside_extent(self):
        draft=pack.template(self.elf,self.raw,self.meta,self.cat)
        targets={r['id']:r['translation'] for r in self.config['entries']}
        for row in draft['rows']:
            if row['id'] in targets:row['translation']=targets[row['id']]
        result,report=pack.rebuild(self.elf,self.raw,self.meta,self.cat,draft,extra_decoded_bytes=256)
        self.assertEqual(result[:0x800],self.raw[:0x800]);self.assertEqual(result[0x1800:],self.raw[0x1800:])
        self.assertEqual(len(result),len(self.raw));self.assertTrue(report['original_decoder_matches'])
        with self.assertRaisesRegex(ValueError,'decompressed budget'):
            pack.rebuild(self.elf,self.raw,self.meta,self.cat,draft)

    def test_growth_override_remains_bounded_and_legacy_default_zero(self):
        draft=pack.template(self.elf,self.raw,self.meta,self.cat)
        for value in (-1,257,True,10000):
            with self.assertRaises(ValueError):pack.rebuild(self.elf,self.raw,self.meta,self.cat,draft,extra_decoded_bytes=value)
        result,report=pack.rebuild(self.elf,self.raw,self.meta,self.cat,draft)
        self.assertEqual(result,self.raw);self.assertEqual(report['extra_decoded_budget_bytes'],0)

    def test_recipe_hash_and_instruction_mutations_refused(self):
        for key in ('source_sha256','decoded_sha256','policy'):
            bad=copy.deepcopy(self.config);bad[key]='wrong'
            with self.assertRaises(ValueError):c.compile_credits(self.elf,bad)
        bad=copy.deepcopy(self.config);bad['instruction_windows'][0]['sha256']='0'*64
        with self.assertRaises(ValueError):c.compile_credits(self.elf,bad)

    def test_names_missing_duplicates_and_source_rebinding_refused(self):
        for mutation in ('name','missing','duplicate','hash'):
            bad=copy.deepcopy(self.config)
            if mutation=='name':bad['entries'][0]['id']='credits.line.0004'
            elif mutation=='missing':bad['entries'].pop()
            elif mutation=='duplicate':bad['entries'].append(bad['entries'][0])
            else:bad['entries'][0]['source_sha256']='0'*64
            with self.assertRaises(ValueError):c.compile_credits(self.elf,bad)

    def test_control_overflow_unknown_glyph_and_company_change_refused(self):
        for value in ('Linha\r\nExtra','%N$0','A'*36,'Ótimo','Traduzido|Teste'):
            bad=copy.deepcopy(self.config);bad['entries'][0]['translation']=value
            with self.assertRaises(ValueError):c.compile_credits(self.elf,bad)
        bad=copy.deepcopy(self.config)
        next(r for r in bad['entries'] if r['id']=='credits.line.0286')['translation']='Apresentado por outra empresa'
        with self.assertRaises(ValueError):c.compile_credits(self.elf,bad)

    def test_ui_child_preserves_all_v038_fields_and_bound_credits_recipe(self):
        old=json.loads((ROOT/'translations/interface-v038.json').read_text(encoding='utf-8'))
        new=json.loads((ROOT/'translations/interface-v039.json').read_text(encoding='utf-8'))
        self.assertEqual({k:v for k,v in old.items() if k not in ('iso_name','status')},
            {k:v for k,v in new.items() if k not in ('iso_name','status','ending_credits')})
        self.assertEqual(new['ending_credits']['sha256'],c.sha((ROOT/new['ending_credits']['recipe']).read_bytes()))
        self.assertEqual(new['layout_profile'],'ptbr-layout-v005')


if __name__=='__main__':unittest.main()
