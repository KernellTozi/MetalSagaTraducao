import copy, sys, unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from diary import extract,rebuild,fields
import struct

def fixture():
    title=b'Test'+bytes(36)
    body=b'Hello %N1|world\0\0'
    return struct.pack('<II',1,8)+struct.pack('<II',1001,1)+title+body

class DiaryTest(unittest.TestCase):
    def test_roundtrip(self):
        d=fixture();self.assertEqual(rebuild(d,extract(d)),d)
    def test_edit_preserves_structure(self):
        d=fixture();j=extract(d);j['fields'][0]['text']='Teste'
        out=rebuild(d,j);self.assertEqual(len(out),len(d));self.assertEqual(out[:16],d[:16]);self.assertEqual(fields(out)[0]['text'],'Teste')
    def test_rejects_overflow_token_and_metadata(self):
        d=fixture()
        for index,key,value in [(0,'text','x'*40),(1,'text','Hello'),(0,'offset',0)]:
            j=extract(d);j['fields'][index][key]=value
            with self.assertRaises(ValueError):rebuild(d,j)
    def test_source_hash(self):
        d=fixture();j=extract(d);j['source_sha256']='0'*64
        with self.assertRaises(ValueError):rebuild(d,j)
    def test_special_bytes_roundtrip_and_preservation(self):
        d=fixture().replace(b'Hello',b'MC\x81c!')
        j=extract(d);self.assertEqual(rebuild(d,j),d)
        j['fields'][1]['text']=j['fields'][1]['text'].replace('world','mundo')
        self.assertIn(b'\x81c',rebuild(d,j))
        j['fields'][1]['text']='MC! %N1|mundo'
        with self.assertRaises(ValueError):rebuild(d,j)

if __name__=='__main__':unittest.main()
