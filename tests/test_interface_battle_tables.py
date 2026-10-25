import copy,json,sys,struct,unittest,collections
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools'))
import spack_battle as b

class BattleTables(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw=b.original(b.RESOURCE);cls.elf=b.original('SLUS_212.93')
        cls.draft=json.loads((ROOT/'translations/interface-v026.json').read_text(encoding='utf-8'))
        cls.config=cls.draft['spack_battle'];cls.rows=b.catalog(cls.raw);cls.byid={r['id']:r for r in cls.rows}
        cls.patches,cls.report=b.compile_battle(cls.elf,cls.config,cls.draft['item_names'])
    def test_structures_and_all_original_pointer_forwarders(self):
        self.assertEqual(len(self.rows),1489)
        for i in range(b.ACTION_COUNT):self.assertEqual(b.execute_action(self.elf,i),i*228)
        for i in range(b.ENEMY_COUNT):
            self.assertEqual(b.execute_enemy(self.elf,i),i*276)
            self.assertEqual(b.execute_enemy_name(self.elf,i),i*276)
            self.assertEqual(b.execute_hint(self.elf,i),i*276+232)
    def test_exact_counts_and_no_duplicate_ids(self):
        self.assertEqual((self.report['accepted'],self.report['actions'],self.report['hints'],self.report['generic_enemy_names']),(999,679,248,72))
        self.assertEqual(len({p['id'] for p in self.patches}),999)
    def test_readback_roundtrip_all_attributes_and_opaque_tails(self):
        out=bytearray(self.raw)
        for p in self.patches:out[p['offset']:p['offset']+len(p['after'])]=p['after']
        targets={e['id']:e['translation'] for e in self.config['entries']}
        for row in self.rows:
            value=bytes(out[row['offset']:row['offset']+row['field_bytes']]).split(b'\0')[0]
            self.assertEqual(value,b.encode(targets[row['id']]) if row['id'] in targets else bytes.fromhex(row['source_hex']))
        for i in range(b.ACTION_COUNT):
            at=b.ACTION_BASE+i*228;self.assertEqual(out[at+32:at+228],self.raw[at+32:at+228])
        for i in range(b.ENEMY_COUNT):
            at=b.ENEMY_BASE+i*276;self.assertEqual(out[at+24:at+232],self.raw[at+24:at+232])
        self.assertEqual(out[0x7e714:0x7e720],self.raw[0x7e714:0x7e720])
        for p in reversed(self.patches):out[p['offset']:p['offset']+len(p['before'])]=p['before']
        self.assertEqual(out,self.raw)
    def test_generic_identity_source_alignment_and_protected_names(self):
        targets={e['id']:e['translation'] for e in self.config['entries']}
        for source,target in (('Bunny Gunner','Coelho atirador'),('Agent','Agente'),('Outlaw','Fora da lei'),('Marauder','Saqueador'),('Brigand','Bandido')):
            rows=[r for r in self.rows if r['kind']=='enemy_name' and bytes.fromhex(r['source_hex']).decode()==source]
            self.assertTrue(rows)
            for row in rows:self.assertEqual(targets[row['id']],target)
        for source in ('Scarlet','Alex','Ghost Tank','Manhunter','G.E. Simmons','M61 Vulcan','Wild Bus','Missile Fish'):
            for row in self.rows:
                if row['kind']=='enemy_name' and bytes.fromhex(row['source_hex']).decode()==source:self.assertNotIn(row['id'],targets)
    def test_native_controls_overflow_and_named_enemy_rejected(self):
        for row,text in ((next(r for r in self.rows if r['kind']=='action' and r['native']),'Teste'),
                         (self.byid['battle.action.0000'],'x'*19),
                         (self.byid['battle.hint.0000'],'x'*44),
                         (self.byid['battle.hint.0000'],'a|b|c'),
                         (self.byid['battle.action.0000'],'%s'),
                         (self.byid['battle.enemy_name.0199'],'Nome'),
                         (self.byid['battle.enemy_name.0001'],'x'*17)):
            with self.subTest(id=row['id'],text=text),self.assertRaises(ValueError):b.validate_value(row,text)
    def test_wrong_source_evidence_duplicate_ids_and_unreviewed_item_aliases(self):
        for kind in ('source','window','record','duplicate','alias'):
            cfg=copy.deepcopy(self.config)
            if kind=='source':cfg['source_sha256']='0'*64
            elif kind=='window':cfg['instruction_windows'][0]['sha256']='0'*64
            elif kind=='record':cfg['entries'][0]['record_sha256']='0'*64
            elif kind=='duplicate':cfg['entries'].append(cfg['entries'][0])
            else:
                row=next(r for r in self.rows if r['kind']=='action' and bytes.fromhex(r['source_hex'])==b'Gibson')
                cfg['entries'].append({k:row[k] for k in ('id','source_sha256','record_sha256')}|{'translation':'Outra arma'})
            with self.subTest(kind=kind),self.assertRaises(ValueError):b.compile_battle(self.elf,cfg,self.draft['item_names'])
    def test_repeated_label_cannot_split_and_ascii_facts_preserved(self):
        cfg=copy.deepcopy(self.config)
        row=next(r for r in self.rows if r['kind']=='action' and bytes.fromhex(r['source_hex'])==b'Attack')
        next(e for e in cfg['entries'] if e['id']==row['id'])['translation']='Golpear'
        with self.assertRaisesRegex(ValueError,'inconsistently'):b.compile_battle(self.elf,cfg,self.draft['item_names'])
        row=next(r for r in self.rows if r['kind']=='enemy_name' and bytes.fromhex(r['source_hex'])==b'T1 Gorilla')
        with self.assertRaises(ValueError):b.validate_value(row,'Gorila T2')
    def test_nonzero_name_padding_and_changed_sda_bounds_rejected(self):
        for at in (b.ACTION_BASE+8,0x3500c+4):
            raw=bytearray(self.raw);raw[at]^=1
            with self.assertRaises(ValueError):b.catalog(raw)

if __name__=='__main__':unittest.main()
