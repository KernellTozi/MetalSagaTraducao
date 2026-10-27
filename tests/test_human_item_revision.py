import copy,json,mmap,sys,unittest
from pathlib import Path
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools'))
import item_names as names
import item_name_user_review as human
import spack_battle as battle
from build_translation_pilot import load_draft,SOURCE as MAP
from interface_text import SOURCE as ELF
from dialogue_advanced import SsdIndex
from reinsertion import descriptor
from gfi import encode


class HumanItemRevisionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.old=json.loads((ROOT/'translations/interface-v041.json').read_text(encoding='utf-8'))
        cls.new=json.loads((ROOT/'translations/interface-v042.json').read_text(encoding='utf-8'))
        cls.m=human.load_manifest(cls.new['item_names']['user_review'])
        cls.elf=ELF.read_bytes();cls.raw=names.original(names.RESOURCE);cls.rows=names.catalog(cls.raw)
        cls.byid={r['id']:r for r in cls.rows}
        cls.a,cls.a_report=names.compile_names(cls.elf,cls.old['item_names'])
        cls.b,cls.b_report=names.compile_names(cls.elf,cls.new['item_names'])
        cls.old_by={r['id']:r for r in cls.old['item_names']['entries']}
        cls.new_by={r['id']:r for r in cls.new['item_names']['entries']}
        cls.allowed={r['id'] for r in cls.m['approved']}

    def test_exact_72_revisions_three_new_and_all_other_names_frozen(self):
        self.assertEqual(len(self.allowed),72)
        self.assertEqual(self.b_report['accepted'],519)
        changed={k for k,v in self.new_by.items() if k not in self.old_by or self.old_by[k]!=v}
        self.assertEqual(changed,self.allowed)
        self.assertEqual(set(self.new_by)-set(self.old_by),{'item.name.0332','item.name.0378','item.name.0383'})
        for k,v in self.old_by.items():
            if k not in self.allowed:self.assertEqual(v,self.new_by[k])

    def test_blocked_16_unconfirmed_one_ratified_35_preserved(self):
        self.assertEqual(len(self.m['blocked']),16);self.assertEqual(len(self.m['ratified_unchanged']),35)
        for r in self.m['blocked']+self.m['ratified_unchanged']+[self.m['alternative_unconfirmed']]:
            self.assertNotIn(r['id'],self.allowed);self.assertEqual(self.old_by[r['id']],self.new_by[r['id']])
        self.assertEqual(self.new_by['item.name.0861']['translation'],'Sentidos finos')
        for r in self.m['ratified_unchanged']:self.assertEqual(self.new_by[r['id']]['translation'],r['translation'])

    def test_all_targets_within_16_project_bytes_and_metadata_unchanged(self):
        out=bytearray(self.raw)
        for p in self.b:
            out[p['offset']:p['offset']+len(p['after'])]=p['after']
        for r in self.rows:
            at=r['offset'];self.assertEqual(out[at+24:at+128],self.raw[at+24:at+128])
            target=self.new_by.get(r['id'],{}).get('translation')
            if target is not None:
                self.assertLessEqual(len(encode(target)),16)
                self.assertEqual(bytes(out[at:at+24]).split(b'\0',1)[0],encode(target))
            elif r['id'] not in self.allowed:self.assertEqual(out[at:at+24],self.raw[at:at+24])
        for p in reversed(self.b):out[p['offset']:p['offset']+len(p['before'])]=p['before']
        self.assertEqual(out,self.raw)

    def test_legacy_remote_checks_remain_strict_and_only_exact_three_accepted(self):
        rows={r['index']:r for r in self.rows}
        for index,(source,target) in human.REMOTE.items():
            with self.assertRaisesRegex(ValueError,'Remote'):names.validate_value(rows[index],target,ceiling=16)
            self.assertEqual(names.validate_value(rows[index],target,ceiling=16,remote_review=True),encode(target))
            with self.assertRaises(ValueError):names.validate_value(rows[index],'Outro nome',ceiling=16,remote_review=True)
        with self.assertRaises(ValueError):names.validate_value(rows[319],'Comprimido',ceiling=16,remote_review=True)

    def test_only_two_exact_record_specific_alias_groups(self):
        self.assertEqual(self.b_report['human_review']['record_specific_alias_groups'],[[142,780],[822,823,824]])
        self.assertTrue(self.b_report['human_review']['all_other_shared_labels_consistent'])
        vals={k:encode(v['translation']) for k,v in self.new_by.items()}
        group=[r for r in self.rows if r['index'] in human.SCRAP]
        self.assertTrue(human.alias_allowed(b'Scrap Metal',group,vals))
        bad=vals.copy();bad['item.name.0822']=encode('Sucata outra')
        self.assertFalse(human.alias_allowed(b'Scrap Metal',group,bad))
        self.assertFalse(human.alias_allowed(b'Scrap Metal',group[:2],vals))
        self.assertEqual(self.new_by['item.name.0142']['translation'],'Traje de criada')

    def test_nonapproved_change_source_or_manifest_rebinding_refused(self):
        for key,value in (('policy','wrong'),('source_sha256','0'*64)):
            c=copy.deepcopy(self.new['item_names']);c[key]=value
            with self.assertRaises(ValueError):names.compile_names(self.elf,c)
        c=copy.deepcopy(self.new['item_names']);c['user_review']['sha256']='0'*64
        with self.assertRaises(ValueError):names.compile_names(self.elf,c)
        c=copy.deepcopy(self.new['item_names']);next(r for r in c['entries'] if r['id']=='item.name.0100')['translation']='Capacete'
        with self.assertRaises(ValueError):names.compile_names(self.elf,c)
        c=copy.deepcopy(self.new['item_names']);c['policy']=names.CEILING_POLICY
        with self.assertRaises(ValueError):names.compile_names(self.elf,c)

    def test_bound_parent_and_audit_conflict_guard(self):
        m=copy.deepcopy(self.m);m['approved'][0]['audited_translation']='Divergente'
        with self.assertRaises(ValueError):human.prepare_config(self.old,m,self.rows,self.new['item_names']['user_review'])
        m=copy.deepcopy(self.m);m['approved'][0]['source_sha256']='0'*64
        with self.assertRaises(ValueError):human.prepare_config(self.old,m,self.rows,self.new['item_names']['user_review'])
        m=copy.deepcopy(self.m);m['approved'].pop()
        with self.assertRaises(ValueError):human.prepare_config(self.old,m,self.rows,self.new['item_names']['user_review'])

    def test_30_battle_counterparts_only_and_legacy_remote_not_relaxed(self):
        old={r['id']:r for r in self.old['spack_battle']['entries']}
        new={r['id']:r for r in self.new['spack_battle']['entries']}
        changed={k for k in new if new[k]!=old[k]};self.assertEqual(len(changed),30)
        patches,report=battle.compile_battle(self.elf,self.new['spack_battle'],self.new['item_names'])
        self.assertEqual({r['id'] for r in report['reviewed_item_counterparts']},changed)
        r=next(r for r in battle.catalog(self.raw) if r['id']=='battle.action.0112')
        with self.assertRaisesRegex(ValueError,'Remote'):battle.validate_value(r,'Granada Remota')
        self.assertEqual(battle.validate_value(r,'Granada Remota',reviewed_remote=True),encode('Granada Remota'))
        bad=copy.deepcopy(self.new['spack_battle']);bad['entries'][0]['translation']='Outro'
        with self.assertRaises(ValueError):battle.compile_battle(self.elf,bad,self.new['item_names'])

    def test_choice_article_only_with_same_separator_mechanic_option_and_capacity(self):
        before,_=load_draft(ROOT/'translations/regiao-inicial-v037.json')
        after,_=load_draft(ROOT/'translations/regiao-inicial-v038.json')
        key='map.sel.1df48484';target=after['translations'][key]
        self.assertEqual(target,'Eu quero ser um Hunter.\tEstá bem, serei mecânico.')
        self.assertEqual(before['translations'][key].split('\t')[1],target.split('\t')[1])
        self.assertEqual({k:v for k,v in before['translations'].items() if k!=key},{k:v for k,v in after['translations'].items() if k!=key})
        self.assertEqual(before.get('aliases'),after.get('aliases'));self.assertEqual(before['deferred'],after['deferred'])
        with MAP.open('rb') as f,mmap.mmap(f.fileno(),0,access=mmap.ACCESS_READ) as raw:
            entry=descriptor(raw,0x1df48484,SsdIndex(raw),named_choices=True,b15=True,numeric1=True,numeric15=True,t0=True,i0=True,n0=True,variable_refs=True,scaled_refs=True,quirk_refs=True)
            self.assertEqual(entry['segments'][0]['capacity'],55);self.assertEqual(len(encode(target)),51)

    def test_complete_ui_other_fields_and_pending_ledger_unchanged(self):
        exceptions={'item_names','item_name_review','spack_battle','base_dialogue_draft','iso_name','status'}
        self.assertEqual({k:v for k,v in self.old.items() if k not in exceptions},{k:v for k,v in self.new.items() if k not in exceptions})
        names.validate_review(self.new['item_name_review'],self.new['item_names'],self.rows)
        self.assertEqual(len(self.new['item_name_review']['pending']),22)
        self.assertEqual(self.new['item_name_review']['preserved'],self.old['item_name_review']['preserved'])

    def test_layout_advance_audit_flags_only_reviewed_name_939(self):
        from measure_item_name_widths import measure
        r=measure(ROOT/'translations/interface-v042.json')
        self.assertEqual(r['reviewed_names_measured'],72)
        self.assertEqual(r['names_above_observed_advance_envelope'],['item.name.0939'])
        self.assertEqual(r['unique_glyph_profile_probes'],474)
        for row in r['results']:
            self.assertLessEqual(row['encoded_bytes'],16)
            self.assertTrue(all(p['within_original_maximum'] for p in row['profiles'] if p['mode'] in (0,2)))

    def test_prefix_normalization_matches_real_old_new_name_bytes(self):
        from verify_interface_revision import normalize_item_name_review_transition
        old={(p['resource'],p['offset']):p for p in self.a};new={(p['resource'],p['offset']):p for p in self.b}
        old_bytes=bytearray(self.raw);new_bytes=bytearray(self.raw)
        for p in self.a:old_bytes[p['offset']:p['offset']+len(p['after'])]=p['after']
        for p in self.b:new_bytes[p['offset']:p['offset']+len(p['after'])]=p['after']
        normalize_item_name_review_transition(self.old,self.new,ROOT/'translations/interface-v041.json',old,new)
        for key,patch_ in new.items():
            if key not in old:continue
            prior=old[key];self.assertEqual(prior['before'],patch_['before'])
            at=patch_['offset'];width=len(patch_['after'])
            self.assertEqual(new_bytes[at:at+width],patch_['after']);self.assertEqual(old_bytes[at:at+width],prior['after'])
        bad_old={(p['resource'],p['offset']):copy.deepcopy(p) for p in self.a}
        first=self.byid[self.m['approved'][0]['id']];k=(names.RESOURCE,first['offset'])
        bad_old[k]['before']+=bytes(25)
        with self.assertRaises(ValueError):normalize_item_name_review_transition(self.old,self.new,ROOT/'translations/interface-v041.json',bad_old,new)


if __name__=='__main__':unittest.main()
