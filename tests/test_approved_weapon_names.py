import copy,json,re,sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
import approved_weapon_names as w
from interface_text import SOURCE,compile_draft
from item_names import catalog,original,RESOURCE,validate_value,compile_names
from gfi import encode


class ApprovedWeaponTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.elf=SOURCE.read_bytes();cls.raw=original(RESOURCE)
        cls.child=json.loads((w.ROOT/'translations/interface-v058.json').read_bytes())
        cls.parent,cls.manifest=w.validate_interface(cls.child)
        cls.before,cls.old_report=compile_draft(cls.elf,cls.parent)
        cls.after,cls.report=compile_draft(cls.elf,cls.child)
        cls.names={r['id']:r for r in catalog(cls.raw)}

    def test_complete_user_table_agrees_with_all_175_decisions(self):
        doc=(w.ROOT/w.DOCUMENT).read_bytes();self.assertEqual(w.sha(doc),w.DOCUMENT_SHA)
        expected={int(i):(s.strip(),t.strip(),int(n),a) for i,s,t,n,a in re.findall(
            r'^\| (\d{4}) \| ([^|]+) \| ([^|]+) \| (\d+) \| (ALTERAR|MANTER) \|\s*$',doc.decode(),re.M)}
        self.assertEqual(set(expected),w.WEAPON_IDS)
        for d in self.manifest['decisions']:
            source,target,n,action=expected[d['index']];row=self.names[d['id']]
            self.assertEqual(bytes.fromhex(row['source_hex']).decode(),source)
            self.assertEqual(w.sha(encode(target)),d['approved_name_sha256'])
            self.assertEqual(len(encode(target)),n);self.assertEqual(d['decision'],action)

    def test_86_new_names_91_actions_all_other_patches_identical(self):
        a={p['id']:p for p in self.before};b={p['id']:p for p in self.after}
        self.assertTrue(set(a)<=set(b));self.assertTrue(all(a[k]==b[k] for k in a))
        self.assertEqual(set(b)-set(a),{r['id'] for r in self.manifest['items']+self.manifest['actions']})
        self.assertEqual(len(b)-len(a),177)
        self.assertEqual(self.report['item_names']['accepted'],627)
        self.assertEqual(self.report['accepted'],4155)

    def test_89_kept_names_and_15_ammunition_names_untouched(self):
        old={p['id']:p['after'].split(b'\0')[0] for p in self.before}
        new={p['id']:p['after'].split(b'\0')[0] for p in self.after}
        kept=[r for r in self.manifest['decisions'] if r['decision']=='MANTER'];self.assertEqual(len(kept),89)
        for r in kept:
            key=r['id'];source=bytes.fromhex(self.names[key]['source_hex'])
            self.assertEqual(new.get(key,source),old.get(key,source))
        for i in range(835,850):
            key=f'item.name.{i:04d}';self.assertEqual(new[key],old[key])
        self.assertEqual(new['item.name.1042'],encode('Rede elétrica'))

    def test_source_attributes_metadata_and_roundtrip_preserved(self):
        patches,_=compile_names(self.elf,self.child['item_names']);out=bytearray(self.raw)
        for p in patches:
            at=p['offset'];self.assertEqual(out[at:at+len(p['before'])],p['before'])
            self.assertEqual(len(p['before']),len(p['after']))
            out[at:at+len(p['after'])]=p['after']
        for r in self.names.values():
            at=r['offset'];self.assertEqual(out[at+24:at+128],self.raw[at+24:at+128])
        for p in patches:out[p['offset']:p['offset']+len(p['before'])]=p['before']
        self.assertEqual(out,self.raw)

    def test_real_encoding_16_bytes_and_no_fallback(self):
        out={p['id']:p for p in self.after}
        for r in self.manifest['items']:
            value=out[r['id']]['after'].split(b'\0')[0]
            self.assertEqual(value,encode(r['translation']));self.assertLessEqual(len(value),16)
        self.assertEqual(self.report['approved_weapons']['fallback'],0)
        self.assertEqual(self.report['approved_weapons']['conflicts'],0)
        self.assertEqual(self.report['approved_weapons']['already_applied'],0)

    def test_battle_aliases_exact_names_and_no_stat_changes(self):
        from spack_battle import catalog as actions
        out={p['id']:p for p in self.after};items={self.names[r['id']]['source_hex']:r['translation'] for r in self.manifest['items']}
        rows={r['id']:r for r in actions(self.raw)}
        for r in self.manifest['actions']:
            p=out[r['id']];self.assertEqual(p['after'].split(b'\0')[0],encode(items[rows[r['id']]['source_hex']]))
            self.assertEqual(len(p['after']),32)
        self.assertEqual(len(self.manifest['actions']),91)

    def test_duplicate_ids_not_deduplicated_and_outside_skill_preserved(self):
        out={p['id']:p for p in self.after}
        self.assertEqual(out['item.name.0019']['after'].split(b'\0')[0],encode('Mãos nuas'))
        self.assertEqual(out['item.name.0074']['after'].split(b'\0')[0],encode('Mãos nuas'))
        self.assertNotIn('item.name.0946',out)
        self.assertEqual(self.report['item_names']['approved_weapons']['external_alias_exceptions'],
                         [{'translated_item':55,'out_of_scope_item_preserved':946}])

    def test_legacy_weapon_protection_remains_closed(self):
        for index in (1,5,55,191,247):
            r=self.names[f'item.name.{index:04d}']
            with self.assertRaises(ValueError):validate_value(r,'Outro nome',ceiling=16)
        r=self.names['item.name.0005']
        with self.assertRaises(ValueError):w.checked_value(r,'Garra de tigre',[])
        with self.assertRaises(ValueError):w.checked_value(r,'Nome com mais de dezesseis bytes',w.TERM_EXCEPTIONS[5])

    def test_unrelated_root_names_actions_and_fonts_rejected(self):
        for key in ('layout_profile','base_dialogue_draft'):
            bad=copy.deepcopy(self.child);bad[key]='bad'
            with self.assertRaises(ValueError):w.validate_interface(bad)
        for key in ('item_names','spack_battle'):
            bad=copy.deepcopy(self.child);bad[key]['entries'][-1]['translation']='Outro'
            with self.assertRaises(ValueError):w.validate_interface(bad)
        bad=copy.deepcopy(self.child);bad['approved_weapons']['sha256']='0'*64
        with self.assertRaises(ValueError):w.validate_interface(bad)

    def test_metrics_below_proved_menu_and_price_budgets(self):
        p=json.loads((w.ROOT/w.PROOF).read_bytes())
        self.assertEqual(len(p['items']),86);self.assertEqual(p['maximum_advance'],176)
        self.assertEqual(p['minimum_direct_panel_margin'],58);self.assertEqual(p['minimum_shop_margin'],66)
        self.assertLess(p['maximum_advance'],234)

    def test_comparator_and_capacity_ledger_use_exact_parent(self):
        from verify_interface_revision import normalize_item_name_review_transition
        from item_name_capacity import apply_authorized_fallback
        normalize_item_name_review_transition(self.parent,self.child,w.ROOT/w.PARENT,{}, {})
        with self.assertRaises(ValueError):
            normalize_item_name_review_transition(self.parent,self.child,w.ROOT/'translations/interface-v056.json',{}, {})
        historical=json.loads((w.ROOT/'reports/capacidade-nomes-v001.json').read_bytes())
        r=apply_authorized_fallback(historical,w.ROOT/'translations/interface-v058.json')
        self.assertEqual(r['counts']['blocked'],0)


if __name__=='__main__':unittest.main()
