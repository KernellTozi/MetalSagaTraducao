import copy,json,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
import paint_captions as paint
from interface_text import SOURCE


class PaintCaptionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.elf=SOURCE.read_bytes()
        cls.raw=(ROOT/'JOGO/Metal Saga'/paint.RESOURCE).read_bytes()
        cls.recipe=json.loads((ROOT/'translations/interface-v038.json').read_text(encoding='utf-8'))
        cls.config=cls.recipe['paint_captions']

    def compile(self,config=None,elf=None,raw=None):
        return paint.compile_captions(elf if elf is not None else self.elf,
            config if config is not None else self.config,raw if raw is not None else self.raw)

    def test_complete_batch_all_aliases_fixed_cells_and_byte_exact_reverse(self):
        patches,report=self.compile();changed=bytearray(self.raw)
        self.assertEqual((report['accepted'],report['unique_translations']),(228,12))
        self.assertEqual(report['source_and_target_consumer_probe_cases'],24)
        self.assertEqual(report['maximum_target_bytes'],10)
        self.assertEqual(len({p['id'] for p in patches}),228)
        for p in patches:
            self.assertEqual(len(p['before']),23);self.assertEqual(len(p['after']),23)
            self.assertEqual(changed[p['offset']:p['offset']+23],p['before'])
            changed[p['offset']:p['offset']+23]=p['after']
        names=[]
        for i in range(228):
            at=paint.START+i*36
            self.assertEqual(changed[at],self.raw[at])
            self.assertEqual(changed[at+24:at+36],self.raw[at+24:at+36])
            names.append(bytes(changed[at+1:at+24]).split(b'\0',1)[0])
        self.assertEqual(len(set(names)),12)
        self.assertTrue(all(names[i]==names[i%12] for i in range(228)))
        for p in patches:changed[p['offset']:p['offset']+23]=p['before']
        self.assertEqual(changed,self.raw)

    def test_twelve_names_preserve_portuguese_accents(self):
        targets=[e['translation'] for e in self.config['entries']]
        for target in ('Azul-bebê','Aço frio','Pântano'):
            self.assertIn(target,targets)
            self.assertEqual(paint.decode(paint.validate_value(target)),target)

    def test_overflow_including_multibyte_and_control_injection_refused(self):
        for value in ('A'*11,'á'*6,'A\0B','A|B','A%B','A\nB',' A','A ',''):
            cfg=copy.deepcopy(self.config);cfg['entries'][0]['translation']=value
            with self.assertRaises(ValueError):self.compile(cfg)

    def test_missing_extra_duplicate_and_alias_member_targets_refused(self):
        for mutation in ('missing','extra','duplicate','alias'):
            cfg=copy.deepcopy(self.config)
            if mutation=='missing':cfg['entries'].pop()
            elif mutation=='extra':cfg['entries'].append({**cfg['entries'][0],'id':'paint.caption.9999'})
            elif mutation=='duplicate':cfg['entries'][1]=cfg['entries'][0]
            else:cfg['entries'][0]['id']='paint.caption.0012'
            with self.assertRaises(ValueError):self.compile(cfg)

    def test_source_table_instruction_and_entry_hashes_are_mandatory(self):
        for field in ('source_sha256','table_sha256','policy','instruction_windows'):
            cfg=copy.deepcopy(self.config);cfg[field]=[] if field=='instruction_windows' else 'bad'
            with self.assertRaises(ValueError):self.compile(cfg)
        cfg=copy.deepcopy(self.config);cfg['entries'][0]['source_sha256']='0'*64
        with self.assertRaises(ValueError):self.compile(cfg)

    def test_original_resource_and_code_tampering_refused(self):
        for at in (0,paint.START,paint.START+24,len(self.raw)-1):
            raw=bytearray(self.raw);raw[at]^=1
            with self.assertRaises(ValueError):self.compile(raw=raw)
        elf=bytearray(self.elf);elf[0x4f82c]^=1
        with self.assertRaises(ValueError):self.compile(elf=elf)

    def test_unknown_fields_and_unchanged_targets_refused(self):
        cfg=copy.deepcopy(self.config);cfg['growth']=True
        with self.assertRaises(ValueError):self.compile(cfg)
        cfg=copy.deepcopy(self.config);cfg['entries'][0]['offset']=1
        with self.assertRaises(ValueError):self.compile(cfg)
        cfg=copy.deepcopy(self.config);cfg['entries'][0]['translation']='Baby Blue'
        with self.assertRaises(ValueError):self.compile(cfg)

    def test_previous_recipe_is_preserved_and_only_new_profile_is_added(self):
        parent=json.loads((ROOT/'translations/interface-v037.json').read_text(encoding='utf-8'))
        child=copy.deepcopy(self.recipe)
        for key in ('paint_captions','iso_name','status'):child.pop(key,None);parent.pop(key,None)
        self.assertEqual(child,parent)
        self.assertEqual(self.recipe['base_dialogue_draft'],'translations/regiao-inicial-v037.json')
        self.assertEqual(self.recipe['layout_profile'],'ptbr-layout-v005')


if __name__=='__main__':unittest.main()
