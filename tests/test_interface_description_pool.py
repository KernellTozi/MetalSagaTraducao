import copy,json,struct,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools'))
from description_pool import *
from interface_text import SOURCE,compile_draft
from item_descriptions import compile_descriptions


class DescriptionPool(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.elf=SOURCE.read_bytes();cls.raw=original(RESOURCE)
        cls.old=json.loads((ROOT/'translations/interface-v026.json').read_text(encoding='utf-8'))
        cls.new=json.loads((ROOT/'translations/interface-v027.json').read_text(encoding='utf-8'))
        cls.config=cls.new['item_descriptions'];cls.rows=topology(cls.raw)
        cls.patches,cls.report=compile_pool(cls.elf,cls.config)
    def test_original_pool_reconstruction_is_byte_identical(self):
        out,offsets,used=rebuild(self.raw,self.rows,{})
        self.assertEqual(out,self.raw[POOL:POOL+SIZE]);self.assertEqual(used,20155)
        self.assertEqual(len(offsets),567)
    def test_previous_translations_unchanged_explicit_24_resumptions(self):
        before={r['id']:r for r in self.old['item_descriptions']['entries']}
        after={r['id']:r for r in self.config['entries']}
        for key,value in before.items():self.assertEqual(value,after[key])
        self.assertEqual(set(after)-before.keys(),set(self.config['resumed_ids']))
        self.assertEqual(len(self.config['resumed_ids']),24)
        self.assertEqual((self.report['accepted'],self.report['item_occurrences']),(565,923))
        self.assertEqual(self.report['free_bytes'],1732)
        self.assertEqual(len(self.new['description_review']['pending']),1)
    def test_every_item_pointer_alias_and_sentinel_read_back(self):
        output=bytearray(self.raw)
        for p in self.patches:output[p['offset']:p['offset']+len(p['after'])]=p['after']
        targets={r['id']:encode(r['translation']) for r in self.config['entries']}
        for row in self.rows:
            refs=[]
            for item in row['items']:
                at=ITEM_BASE+item['id']*STRIDE+24;rel=struct.unpack_from('<I',output,at)[0];refs.append(rel)
                found=output[POOL+rel:POOL+SIZE].split(b'\0',1)[0]
                self.assertEqual(found,targets.get(row['id'],bytes.fromhex(row['source_hex'])))
            self.assertEqual(len(set(refs)),1)
        for index in range(ITEM_COUNT):
            at=ITEM_BASE+index*STRIDE
            self.assertEqual(output[at:at+24],self.raw[at:at+24]);self.assertEqual(output[at+28:at+STRIDE],self.raw[at+28:at+STRIDE])
            if self.raw[at+24:at+28]==b'\xff'*4:self.assertEqual(output[at:at+STRIDE],self.raw[at:at+STRIDE])
        self.assertEqual(output[:ITEM_BASE],self.raw[:ITEM_BASE])
        self.assertEqual(output[POOL+SIZE:],self.raw[POOL+SIZE:])
    def test_all_17_forwarders_and_927_indices_executed(self):
        self.assertEqual(self.report['forwarding_cases'],15759)
        self.assertEqual(self.report['evidence']['bounded_lw_immediate_census'],list(READS))
        record=bytearray(128)
        for rel in (0,1,18427,SIZE-1):
            struct.pack_into('<I',record,24,rel)
            for site in READS:self.assertEqual(execute_forwarding(self.elf,bytes(record),site),rel)
    def test_mutated_parent_evidence_and_old_translation_refused(self):
        for change in ('parent','window','old-text','name-policy'):
            c=copy.deepcopy(self.config)
            if change=='parent':c['fixed_slot_parent']['sha256']='0'*64
            elif change=='window':c['pool_repack_windows'][0]['sha256']='0'*64
            elif change=='old-text':c['entries'][0]['translation']='Mudou'
            else:c['name_reference_policy']='unknown'
            with self.subTest(change=change),self.assertRaises(ValueError):compile_pool(self.elf,c)
    def test_resume_unknown_duplicate_omission_and_record_binding_refused(self):
        for change in ('resume','duplicate','omission','record'):
            c=copy.deepcopy(self.config)
            if change=='resume':c['resumed_ids'].append('item.description.03226')
            elif change=='duplicate':c['entries'].append(c['entries'][0])
            elif change=='omission':c['entries'].pop(0)
            else:c['entries'][0]['item_records'][0]['id']+=1
            with self.subTest(change=change),self.assertRaises(ValueError):compile_pool(self.elf,c)
    def test_percent_native_injection_and_observed_bounds_refused(self):
        for before,text in ((b'80%%','80%%'),(b'Native\x82\x40','Texto'),(b'Hello','a'*60),
            (b'Hello','a'*30),(b'Hello','Oi|oi'),(b'Hello','Oi\0'),(b'Hello','Oi%'),(b'Item 2','Item 3')):
            with self.subTest(text=text),self.assertRaises(ValueError):validate_value(before,text)
    def test_opaque_source_topology_and_total_pool_overflow_refused(self):
        raw=bytearray(self.raw);raw[POOL+SIZE-1]=1
        with self.assertRaises(ValueError):topology(raw)
        with self.assertRaises(ValueError):rebuild(self.raw,self.rows,{r['id']:b'a'*59 for r in self.rows})
    def test_native_and_percent_strings_untouched_logically(self):
        out=self.patches[0]['after'];targets={e['id'] for e in self.config['entries']}
        percent=next(r for r in self.rows if r['id']=='item.description.03226')
        offset=next(struct.unpack('<I',p['after'])[0] for p in self.patches if p['id']==f'item.description-ref.{percent["items"][0]["id"]:04d}')
        self.assertEqual(out[offset:].split(b'\0',1)[0],bytes.fromhex(percent['source_hex']))
        self.assertNotIn(percent['id'],targets)
    def test_legacy_profile_still_refuses_growth(self):
        row=next(r for r in self.rows if r['id']=='item.description.0259f')
        from item_descriptions import validate_value as fixed
        with self.assertRaises(ValueError):fixed(bytes.fromhex(row['source_hex']),'Cura paralisia.')
        self.assertEqual(validate_value(bytes.fromhex(row['source_hex']),'Cura paralisia.'),encode('Cura paralisia.'))
    def test_integration_has_disjoint_patches(self):
        patches,report=compile_draft(self.elf,self.new)
        self.assertEqual(report['accepted'],3443)
        groups={}
        for p in patches:groups.setdefault(p['resource'],[]).append(p)
        for group in groups.values():
            group.sort(key=lambda p:p['offset'])
            for a,b in zip(group,group[1:]):self.assertLessEqual(a['offset']+len(a['before']),b['offset'])
    def test_only_24_pending_entries_reclassified(self):
        old={r['id']:r for r in self.old['description_review']['pending']};new=self.new['description_review']
        for row in new['pending']:self.assertEqual(row,old[row['id']])
        self.assertEqual(self.new['item_names'],self.old['item_names'])
        self.assertEqual(self.new['spack_battle'],self.old['spack_battle'])
        self.assertEqual(self.new['spack_interactions'],self.old['spack_interactions'])
    def test_transition_comparator_preserves_historical_overlay(self):
        from verify_interface_revision import normalize_description_transition
        previous,_=compile_descriptions(self.elf,self.old['item_descriptions'])
        old={(p['resource'],p['offset']):p for p in previous}
        new={(p['resource'],p['offset']):p for p in self.patches}
        normalize_description_transition(self.old,self.new,ROOT/'translations/interface-v026.json',old,new)
        self.assertEqual(len(old),1)
        overlay=bytearray(self.raw[POOL:POOL+SIZE])
        for p in previous:overlay[p['offset']-POOL:p['offset']-POOL+len(p['after'])]=p['after']
        self.assertEqual(old[(RESOURCE,POOL)]['after'],bytes(overlay))
    def test_transition_comparator_refuses_unrelated_drops_or_wrong_parent(self):
        from verify_interface_revision import normalize_description_transition
        previous,_=compile_descriptions(self.elf,self.old['item_descriptions'])
        new={(p['resource'],p['offset']):p for p in self.patches}
        for fault in ('missing','outside','parent'):
            old={(p['resource'],p['offset']):p for p in copy.deepcopy(previous)}
            if fault=='missing':old.pop(next(iter(old)))
            elif fault=='outside':old[next(iter(old))]['offset']=0
            path=ROOT/('translations/interface-v025.json' if fault=='parent' else 'translations/interface-v026.json')
            with self.subTest(fault=fault),self.assertRaises(ValueError):normalize_description_transition(self.old,self.new,path,old,new)
    def test_planner_exports_original_ids_and_relocated_destinations(self):
        import tempfile
        from plan_interface_menus import audit
        with tempfile.TemporaryDirectory(dir=ROOT/'work',prefix='test-description-plan-') as folder:
            path=Path(folder)/'plan.json';result=audit(ROOT/'translations/interface-v027.json',path)
            data=json.loads(path.read_text(encoding='utf-8'))
            self.assertEqual(data['description_pool']['free_bytes'],1732)
            self.assertEqual(result['item_statuses']['translated-in-recipe-pending-visual'],565)
            self.assertTrue(all('original_offset' in r and 'planned_pool_relative_offset' in r for r in data['item_descriptions']))

if __name__=='__main__':unittest.main()
