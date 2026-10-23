import struct,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools'))
from plan_interface_menus import counted_strings,classify_elf

class CountedMenuPlanning(unittest.TestCase):
    def test_nonmonotonic_aliases_are_one_string_with_all_ids(self):
        raw=struct.pack('<4I',3,19,16,19)+b'AA\0B\0'
        result=counted_strings(raw,0,len(raw),3)
        self.assertEqual(result['unique_strings'],2);self.assertEqual(result['alias_references'],1)
        self.assertEqual(result['entries'][1]['pointer_ids'],[0,2]);self.assertEqual(result['entries'][0]['pointer_ids'],[1])
        self.assertEqual(result['offsets'],[19,16,19])
        self.assertTrue(all(r['status']=='identified-not-editable' for r in result['entries']))
    def test_native_bytes_are_preserved_without_guessing(self):
        raw=struct.pack('<2I',1,8)+bytes.fromhex('826e00')
        row=counted_strings(raw,0,len(raw),1)['entries'][0]
        self.assertEqual(row['source_hex'],'826e');self.assertIsNone(row['source_ascii']);self.assertEqual(row['repertoire'],'native-bytes-unmapped')
    def test_bounds_count_and_terminator_fail_closed(self):
        for raw in (struct.pack('<2I',1,4)+b'A\0',struct.pack('<2I',1,999)+b'A\0',struct.pack('<2I',1,8)+b'A'):
            with self.assertRaises(ValueError):counted_strings(raw,0,len(raw),1)
        with self.assertRaises(ValueError):counted_strings(struct.pack('<2I',1,8)+b'A\0',0,10,2)
    def test_interior_offsets_are_not_promoted(self):
        raw=struct.pack('<3I',2,12,13)+b'AB\0'
        with self.assertRaises(ValueError):counted_strings(raw,0,len(raw),2)
    def test_control_sequence_is_reported_not_removed(self):
        raw=struct.pack('<2I',1,8)+b'%%I%02d%s|%d\0'
        row=counted_strings(raw,0,len(raw),1)['entries'][0]
        self.assertEqual(row['control_sequence_hex'],[b'%%'.hex(),b'%02d'.hex(),b'%s'.hex(),b'|'.hex(),b'%d'.hex()])
        self.assertEqual(row['source_ascii'],'%%I%02d%s|%d')
    def test_classification_does_not_override_existing_translations(self):
        row={'id':'id','source':'Hunter','offset':0x349590,'status':'referenced-candidate'}
        self.assertEqual(classify_elf(row,{'id':{}},set()),'translated')
        self.assertEqual(classify_elf(row,{},set()),'protected-term')
        row['source']='sShop_ConfirmWnd';self.assertEqual(classify_elf(row,{},set()),'technical-candidate')
        row['source']='%-14s%10s';self.assertEqual(classify_elf(row,{},set()),'format-or-data-only')
        row['source']='Coat: %4d';self.assertEqual(classify_elf(row,{},set()),'review-reference')

if __name__=='__main__':unittest.main()
