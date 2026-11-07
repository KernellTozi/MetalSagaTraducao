import copy,json,sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
import item_use_release as r


class ItemUseTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from interface_text import compile_draft
        cls.elf=r.ELF.read_bytes();cls.parent=json.loads((r.ROOT/r.PARENT).read_bytes())
        cls.parents,cls.report=compile_draft(cls.elf,cls.parent)
        cls.patches,cls.absorbed,cls.proof=r.derive(cls.elf,cls.parents)
        cls.child=json.loads((r.ROOT/r.CHILD).read_bytes())
        cls.m=r.validate(cls.child)[1]
        cls.pool=next(p for p in cls.patches if p['id']=='item-use.message.pool')

    def test_manifest_reproduces_all_outputs(self):
        self.assertEqual(self.m['patches'],[r.metadata(p) for p in self.patches])
        self.assertEqual(self.m['absorbed'],self.absorbed);self.assertEqual(self.m['evidence'],self.proof)

    def test_parent_and_unrelated_mutation_refused(self):
        self.assertEqual(r.validate(self.child)[0],self.parent)
        changed=copy.deepcopy(self.child);changed['entries'][0]['translation']='Outro texto'
        with self.assertRaises(ValueError):r.validate(changed)
        changed=copy.deepcopy(self.child);changed['item_use_release']['sha256']='0'*64
        with self.assertRaises(ValueError):r.validate(changed)

    def test_same_pool_size_and_twenty_messages(self):
        self.assertEqual(len(self.pool['before']),560);self.assertEqual(len(self.pool['after']),560)
        self.assertEqual(len(self.proof['messages']['messages']),20)
        self.assertEqual(sum(row['new_translation'] for row in self.proof['messages']['messages']),14)
        self.assertLessEqual(self.proof['messages']['used_bytes'],560)

    def test_readback_codec_and_native_length(self):
        from spack_ui import execute_byte_length
        for row in self.proof['messages']['messages']:
            at=row['target_va']-r.DELTA-r.START;raw=self.pool['after'][at:].split(b'\0')[0]
            self.assertEqual(r.decode(raw),row['translation'])
            self.assertEqual(execute_byte_length(self.elf,raw),len(raw))
            self.assertEqual(row['target_va']%8,0)

    def test_fixed_copy_reads_fit_and_terminate(self):
        for row in self.proof['messages']['messages']:
            if row['fixed_copy_read_bytes'] is None:continue
            at=row['target_va']-r.DELTA-r.START;size=row['fixed_copy_read_bytes']
            copied=self.pool['after'][at:at+size]
            self.assertEqual(len(copied),size);self.assertIn(0,copied)
            self.assertEqual(r.decode(copied.split(b'\0')[0]),row['translation'])
            self.assertGreaterEqual(row['reserved_bytes'],size)
        self.assertEqual(r.PRESERVED[0x31a618],'Ineficaz')

    def test_printf_order_newlines_and_sample_messages(self):
        for row in self.proof['messages']['messages']:
            source=self.elf[row['source_offset']:].split(b'\0',1)[0];target=r.encode(row['translation'])
            self.assertEqual(r.FORMAT.findall(source),r.FORMAT.findall(target))
            self.assertEqual(source.count(b'\n'),target.count(b'\n'))
        self.assertEqual(r.TARGETS[0x31a600]%('Kernell',1000),'Kernell recuperou\n1000HP')
        self.assertEqual(r.TARGETS[0x31a800]%200,'Todos recuperaram\n200HP')
        self.assertEqual(r.TARGETS[0x31a628]%('Bernie',5),'Pelo de Bernie\nbrilha mais (+5)')
        self.assertEqual(r.TARGETS[0x31a700]%('Bull','Demag'),'Reparo: Bull\nVeículo: Demag')
        self.assertEqual(r.TARGETS[0x31a6b0]%(200,'Demag'),'Recuperou 200SP\nem Demag')

    def test_pointer_instruction_shapes_and_addresses(self):
        import struct
        for row in self.proof['messages']['references']:
            high=struct.unpack_from('<I',self.elf,row['high_offset'])[0]
            old=struct.unpack_from('<I',self.elf,row['low_offset'])[0]
            patch=next((p for p in self.patches if p['id']==f'item-use.pointer.{row["low_offset"]:08x}'),None)
            word=struct.unpack('<I',patch['after'])[0] if patch else old
            self.assertEqual(word&0xffff0000,old&0xffff0000)
            low=word&65535;low=low if low<32768 else low-65536
            self.assertEqual(((high&65535)<<16)+low,row['target_va'])

    def test_stun_shared_high_reference_is_proven(self):
        row=next(row for row in self.proof['messages']['references'] if row['source_offset']==0x31a660)
        self.assertEqual((row['high_offset'],row['low_offset']),(0x70e44,0x70e70))

    def test_help_and_five_mountain_names(self):
        help_patch=next(p for p in self.patches if p['id']=='item-use.help.category')
        self.assertEqual(r.decode(help_patch['after'].split(b'\0')[0]),'Qual categoria?')
        self.assertEqual(len(help_patch['before']),len(help_patch['after']))
        self.assertEqual(self.elf[help_patch['offset']-4:help_patch['offset']],b'\xff'*4)
        rows=self.proof['mountains'];self.assertEqual(len(rows),5)
        self.assertEqual(sum(row['translation']=='Montanha de Sucata' for row in rows),3)
        self.assertEqual(sum(row['translation']=='Monte Macaco' for row in rows),2)
        for p in self.patches:
            if p['resource']=='DATA/MAP/MAP.MCT':
                self.assertEqual(len(p['before']),len(p['after']));self.assertLessEqual(len(p['after']),32)

    def test_normalization_keeps_old_pool_exact(self):
        old={(p['resource'],p['offset']):p for p in self.parents}
        new={(p['resource'],p['offset']):p for p in self.patches}
        expected=bytearray(self.pool['before'])
        for p in self.parents:
            if p['id'] in self.absorbed:
                at=p['offset']-r.START;expected[at:at+len(p['after'])]=p['after']
        r.normalize(old,new)
        self.assertEqual(old[('SLUS_212.93',r.START)]['after'],bytes(expected))

    def test_compiler_keeps_every_unrelated_patch(self):
        from unittest.mock import patch
        with patch('interface_text.compile_draft',return_value=(self.parents,self.report)):
            result,report=r.compile_interface(self.elf,self.child)
        by={p['id']:p for p in result}
        for p in self.parents:
            if p['id'] not in self.absorbed:self.assertEqual(p,by[p['id']])
        self.assertEqual(report['accepted'],self.report['accepted']+20)


if __name__=='__main__':unittest.main()
