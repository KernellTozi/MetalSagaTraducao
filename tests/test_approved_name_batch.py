import copy,json,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools'))
import item_names as names
import item_name_approved_batch as batch
from gfi import encode,decode
from interface_text import SOURCE

class ApprovedNameBatchTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.old=json.loads((ROOT/'translations/interface-v042.json').read_text(encoding='utf-8'))
        cls.new=json.loads((ROOT/'translations/interface-v043.json').read_text(encoding='utf-8'))
        cls.m,_=batch.load(cls.new['item_names']['approved_extension'])
        cls.raw=names.original(names.RESOURCE);cls.rows=names.catalog(cls.raw)
        cls.by={r['index']:r for r in cls.rows};cls.elf=SOURCE.read_bytes()
        cls.a,_=names.compile_names(cls.elf,cls.old['item_names'])
        cls.b,cls.report=names.compile_names(cls.elf,cls.new['item_names'])

    def test_exact_nine_ids_and_untouched_other_ui_fields(self):
        a={r['id']:r for r in self.old['item_names']['entries']};b={r['id']:r for r in self.new['item_names']['entries']}
        changed={k for k in a.keys()|b.keys() if a.get(k)!=b.get(k)}
        self.assertEqual(changed,{f'item.name.{i:04d}' for i in batch.APPROVED})
        self.assertEqual(len(b)-len(a),8);self.assertEqual(self.report['accepted'],527)
        excepted={'item_names','item_name_review','iso_name','status'}
        self.assertEqual({k:v for k,v in self.old.items() if k not in excepted},{k:v for k,v in self.new.items() if k not in excepted})
        names.validate_review(self.new['item_name_review'],self.new['item_names'],self.rows)
        self.assertEqual(len(self.new['item_name_review']['pending']),14)

    def test_glyph_fallback_only_oculos_and_byte_round_trip(self):
        self.assertEqual([r['index'] for r in self.m['approved'] if r['accent_fallback']],[103])
        for r in self.m['approved']:
            value=encode(r['translation']);self.assertLessEqual(len(value),16)
            self.assertEqual(decode(value),r['translation']);self.assertEqual(value.hex(),r['encoded_hex'])
            self.assertEqual(len(value),r['encoded_bytes'])
        self.assertEqual(len(encode('Superpercepção')),16)
        self.assertEqual(batch.selected(109),'Máscara hóquei')

    def test_skill_actual_source_and_description_not_sixth_sense(self):
        self.assertEqual(bytes.fromhex(self.by[861]['source_hex']),b'Keen Senses')
        from item_descriptions import catalog
        r=next(d for d in catalog(self.raw) if any(i['id']==861 for i in d['items']))
        self.assertEqual(r['source_sha256'],self.m['perception_description_sha256'])
        self.assertEqual(bytes.fromhex(r['source_hex']),b'Temporarily raises your|chances of First Strike.')

    def test_metadata_all_other_names_and_reverse_roundtrip(self):
        old=bytearray(self.raw);new=bytearray(self.raw)
        for dest,patches in ((old,self.a),(new,self.b)):
            for p in patches:dest[p['offset']:p['offset']+len(p['after'])]=p['after']
        for row in self.rows:
            at=row['offset'];self.assertEqual(old[at+24:at+128],new[at+24:at+128])
            if row['index'] not in batch.APPROVED:self.assertEqual(old[at:at+128],new[at:at+128])
            else:self.assertEqual(new[at:at+24].split(b'\0',1)[0],encode(batch.selected(row['index'])))
        for p in reversed(self.b):new[p['offset']:p['offset']+len(p['before'])]=p['before']
        self.assertEqual(new,self.raw)

    def test_legacy_repair_guard_and_exact_exception(self):
        with self.assertRaisesRegex(ValueError,'Repair Kit'):names.validate_value(self.by[342],'Kit de reparo',ceiling=16)
        self.assertEqual(names.validate_value(self.by[342],'Kit de reparo',ceiling=16,repair_review=True),encode('Kit de reparo'))
        with self.assertRaises(ValueError):names.validate_value(self.by[342],'Kit comum',ceiling=16,repair_review=True)
        with self.assertRaises(ValueError):names.validate_value(self.by[103],'Oculos',ceiling=16,repair_review=True)

    def test_unapproved_name_binding_and_scope_changes_refused(self):
        c=copy.deepcopy(self.new['item_names']);c['entries'][0]['translation']='Outro'
        with self.assertRaises(ValueError):names.compile_names(self.elf,c)
        c=copy.deepcopy(self.new['item_names']);c['approved_extension']['sha256']='0'*64
        with self.assertRaises(ValueError):names.compile_names(self.elf,c)
        m=copy.deepcopy(self.m);m['approved'][0]['translation']='oculos'
        with self.assertRaises(ValueError):batch.prepare(self.old,m,self.rows,self.new['item_names']['approved_extension'])
        m=copy.deepcopy(self.m);m['approved'].pop()
        with self.assertRaises(ValueError):batch.prepare(self.old,m,self.rows,self.new['item_names']['approved_extension'])

    def test_perception_patch_prefix_union_is_exact(self):
        from verify_interface_revision import normalize_item_name_review_transition
        old={(p['resource'],p['offset']):p for p in self.a};new={(p['resource'],p['offset']):p for p in self.b}
        normalize_item_name_review_transition(self.old,self.new,ROOT/'translations/interface-v042.json',old,new)
        k=(names.RESOURCE,self.by[861]['offset'])
        self.assertEqual(old[k]['before'],new[k]['before']);self.assertEqual(len(old[k]['after']),17)
        self.assertEqual(new[k]['after'],encode('Superpercepção')+b'\0')
        with self.assertRaises(ValueError):normalize_item_name_review_transition(self.old,self.new,ROOT/'translations/interface-v041.json',old,new)

if __name__=='__main__':unittest.main()
