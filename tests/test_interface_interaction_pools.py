import copy,json,sys,struct,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools'))
import spack_interactions as s

class InteractionPools(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw=s.original(s.RESOURCE);cls.elf=s.original('SLUS_212.93')
        cls.cfg=json.loads((ROOT/'translations/interface-v026.json').read_text(encoding='utf-8'))['spack_interactions']
        cls.patches,cls.report=s.compile_interactions(cls.elf,cls.cfg)
    def test_counts_source_regions_and_opaque_trailer(self):
        self.assertEqual(self.report['accepted'],299)
        self.assertEqual(self.report['tables']['reaction']['accepted'],149)
        self.assertEqual(self.report['tables']['bar']['accepted'],150)
        reaction=s.catalog(self.raw,'reaction');self.assertEqual(reaction['pool_end'],8849)
        self.assertEqual(self.report['tables']['reaction']['used_bytes'],8470)
        self.assertEqual(self.report['tables']['bar']['used_bytes'],3736)
        p=self.patches[0];self.assertEqual(p['before'][8849:],p['after'][8849:])
    def test_all_logical_aliases_nuls_and_prefixes_readback(self):
        for kind,p in zip(('reaction','bar'),self.patches):
            raw=bytearray(self.raw);raw[p['offset']:p['offset']+len(p['after'])]=p['after']
            before=s.catalog(self.raw,kind);after=s.catalog(raw,kind)
            values={e['id']:s.encode(e['translation']) for e in self.cfg[kind]['entries']}
            logical={tuple(r['references']):bytes.fromhex(r['source_hex']) for r in after['rows']}
            for row in before['rows']:
                expected=values.get(row['id'],bytes.fromhex(row['source_hex']))
                self.assertEqual(logical[tuple(row['references'])],expected)
            restored=bytearray(raw);restored[p['offset']:p['offset']+len(p['before'])]=p['before'];self.assertEqual(restored,self.raw)
    def test_every_original_lookup_for_all_variants_and_bar_ids(self):
        for kind,p in zip(('reaction','bar'),self.patches):
            if kind=='reaction':
                for i in range(179):
                    self.assertEqual(p['after'][4+i*16:8+i*16],p['before'][4+i*16:8+i*16])
                    for variant in range(3):self.assertEqual(s.execute_reaction(self.elf,p['after'],i,variant),struct.unpack_from('<I',p['after'],8+i*16+variant*4)[0])
            else:
                for i in range(172):self.assertEqual(s.execute_bar(self.elf,p['after'],i),struct.unpack_from('<I',p['after'],4+i*4)[0])
    def test_digit_prefix_unknown_tokens_and_glyphs_rejected(self):
        t=s.catalog(self.raw,'bar');row=next(r for r in t['rows'] if bytes.fromhex(r['source_hex'])==b'[4]Monkey Swirl')
        for text in ('[5]Macaco','Macaco','[4][x]Macaco','[4]Teste %s','[4]Óculos'):
            with self.subTest(text=text),self.assertRaises(ValueError):s.validate_value(row,text,t)
        marker=next(r for r in t['rows'] if bytes.fromhex(r['source_hex']).startswith(b'*'))
        with self.assertRaises(ValueError):s.validate_value(marker,'Outro marcador',t)
    def test_pool_overflow_cannot_consume_opaque_tail_or_next_section(self):
        for kind in ('reaction','bar'):
            t=s.catalog(self.raw,kind)
            with self.assertRaises(ValueError):s.rebuild(self.raw,t,{r['id']:b'x'*200 for r in t['rows']})
    def test_source_window_hashes_duplicates_and_target_ids_fail_closed(self):
        for case in ('window','table','hash','duplicate','unknown'):
            cfg=copy.deepcopy(self.cfg)
            if case=='window':cfg['instruction_windows'][0]['sha256']='0'*64
            elif case=='table':cfg['bar']['table_sha256']='0'*64
            elif case=='hash':cfg['reaction']['entries'][0]['source_sha256']='0'*64
            elif case=='duplicate':cfg['reaction']['entries'].append(cfg['reaction']['entries'][0])
            else:cfg['reaction']['entries'][0]['id']='reaction.fffff'
            with self.subTest(case=case),self.assertRaises(ValueError):s.compile_interactions(self.elf,cfg)
    def test_pointer_into_header_and_interior_alias_are_rejected(self):
        raw=bytearray(self.raw);struct.pack_into('<I',raw,s.REACTION_BASE+8,4)
        with self.assertRaises(ValueError):s.catalog(raw,'reaction')
        raw=bytearray(self.raw);first=struct.unpack_from('<I',raw,s.REACTION_BASE+8)[0];struct.pack_into('<I',raw,s.REACTION_BASE+12,first+1)
        with self.assertRaises(ValueError):s.catalog(raw,'reaction')

if __name__=='__main__':unittest.main()
