import json,mmap,struct,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools'))
import scene_name_fields as s
from reinsertion import SOURCE


def fixture():
    base=s.BASE;header=0x12f0;trees=header;blobs=trees+300*32;size=blobs+300*64
    data=bytearray(base+size);data[base:base+4]=b'maps';struct.pack_into('<III',data,base+4,14,header,size)
    for i in range(300):
        t=trees+i*32;b=blobs+i*64
        struct.pack_into('<4I',data,base+48+16*i,t,32,b,b+64)
        struct.pack_into('<HHIII',data,base+t,0,1,i,0,64)
        struct.pack_into('<HHIII',data,base+t+16,3,0,i,0,64)
        data[base+b:base+b+5]=b'Room\0'
    return data


class SceneNameFields(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with SOURCE.open('rb') as f,mmap.mmap(f.fileno(),0,access=mmap.ACCESS_READ) as data:cls.real=s.parse(data)

    def test_actual_300_trees_839_unique_fields_no_item_dependencies(self):
        r=self.real
        self.assertEqual((r['map_count'],r['name_fields'],r['native_fields'],r['inherited_names'],r['item_references']),(300,839,2,400,0))
        self.assertEqual(len({x['offset'] for x in r['rows']}),839)
        self.assertTrue(all(x['source_bytes']<=31 for x in r['rows']))

    def test_synthetic_complete_tree_bank_and_unknown_types(self):
        d=fixture();self.assertEqual(s.parse(d)['name_fields'],300)
        tree=struct.unpack_from('<I',d,s.BASE+48)[0]
        struct.pack_into('<H',d,s.BASE+tree+16,13)
        with self.assertRaises(ValueError):s.parse(d)

    def test_incomplete_children_and_payload_outside_entry_refused(self):
        d=fixture();tree=struct.unpack_from('<I',d,s.BASE+48)[0]
        struct.pack_into('<H',d,s.BASE+tree+2,2)
        with self.assertRaises(ValueError):s.parse(d)
        d=fixture();struct.pack_into('<I',d,s.BASE+tree+16+12,1000)
        with self.assertRaises(ValueError):s.parse(d)

    def test_nul_tail_and_inherited_parent_are_not_relaxed(self):
        for mode in ('no-nul','nonzero-tail','wrong-parent'):
            d=fixture();blob=struct.unpack_from('<I',d,s.BASE+48+8)[0];at=s.BASE+blob
            if mode=='no-nul':d[at:at+32]=b'A'*32
            elif mode=='nonzero-tail':d[at+20]=1
            else:struct.pack_into('<I',d,at+32,256)
            with self.assertRaises(ValueError):s.parse(d)

    def test_payload_alias_and_bank_overflow_refused(self):
        d=fixture();blob=struct.unpack_from('<I',d,s.BASE+48+8)[0]
        struct.pack_into('<II',d,s.BASE+48+16+8,blob,blob+64)
        with self.assertRaises(ValueError):s.parse(d)
        d=fixture();struct.pack_into('<I',d,s.BASE+12,len(d)*2)
        with self.assertRaises(ValueError):s.parse(d)

    def test_real_message_budget_proof_includes_independent_maxima(self):
        r=json.loads((ROOT/'reports/prova-seis-nomes-v007.json').read_bytes())['budgets']
        self.assertEqual((r['field_count'],r['page_count'],r['maximum_page_content_cells'],r['maximum_body_bytes']),(34,35,91,332))
        self.assertTrue(r['independent_variable_values_bounded'])
        self.assertEqual(r['N0_byte_bound_for_valid_field'],31)

    def test_synthetic_message_overflow_unknown_control_and_role_refused(self):
        def document(text='%I$0'):
            return {'entries':[{'id':str(i),'segments':[{'key':'body','translation':text if i else '%I$0\t%N0 %I$1'}]} for i in range(34)]}
        self.assertEqual(s.message_budgets(document())['page_count'],35)
        for text in ('A'*1000+'%I$0','%I$0 %N$0','%I$0 %W9'):
            with self.assertRaises(ValueError):s.message_budgets(document(text))
        d=document();d['entries'][0]['segments'][0]['key']='label'
        with self.assertRaises(ValueError):s.message_budgets(d)


if __name__=='__main__':unittest.main()
