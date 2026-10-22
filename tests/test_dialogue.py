import copy,io,struct,sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from dialogue import changes,plan,record
from build_dialogue_iso import compare_streams

def fixture():
    before=b''.join(struct.pack('<4sHH',b'wait',i,8) for i in range(3))
    header=struct.pack('<4sHH',b'msg\0',3,64)+bytes(24)
    body=b'You want to become\na hunter?\0'+bytes(3)
    after=b''.join(struct.pack('<4sHH',b'wait',i,8) for i in range(4,7))
    return before+header+body+after

class DialogueTests(unittest.TestCase):
    def test_roundtrip_no_edits(self):
        data=fixture();self.assertEqual(changes(data,plan(data,[24])),[])

    def test_pilot_patch_and_full_comparison(self):
        data=fixture();document=plan(data,[24]);document['entries'][0]['translation']='Quer ser um\nHunter?'
        patches=changes(data,document);output=bytearray(data)
        for patch in patches:output[patch['offset']:patch['offset']+len(patch['before'])]=patch['after']
        self.assertEqual(record(output,24)['source'],'Quer ser um\nHunter?')
        self.assertEqual(data[:56],output[:56]);self.assertEqual(data[88:],output[88:])
        self.assertTrue(compare_streams(io.BytesIO(data),io.BytesIO(output),patches,chunk_size=7)['all_bytes_match_expected_patch'])

    def test_reject_unsafe_translation(self):
        data=fixture()
        for text in ['Voce quer ser um cacador?','x'*50+'\ny','Quer ser um\nCaçador?','Quer\0ser\num?','Quer %N1\nHunter?','A\n\nB','Longer than source line\na hunter?']:
            document=plan(data,[24]);document['entries'][0]['translation']=text
            with self.subTest(text=text),self.assertRaises((ValueError,UnicodeEncodeError)):changes(data,document)

    def test_reject_metadata_hash_duplicate_and_context(self):
        data=fixture();document=plan(data,[24])
        for key,value in [('source_sha256','0'*64),('schema',2)]:
            bad=copy.deepcopy(document);bad[key]=value
            with self.assertRaises(ValueError):changes(data,bad)
        bad=copy.deepcopy(document);bad['entries'][0]['index']=2
        with self.assertRaises(ValueError):changes(data,bad)
        bad=copy.deepcopy(document);bad['entries']*=2
        with self.assertRaises(ValueError):changes(data,bad)
        invalid=bytearray(data);invalid[88:92]=b'!!!!'
        with self.assertRaises(ValueError):record(invalid,24)

    def test_reject_nonzero_padding_and_unknown_encoding(self):
        data=bytearray(fixture());data[87]=1
        with self.assertRaises(ValueError):record(data,24)
        data=bytearray(fixture());data[56]=0x81
        with self.assertRaises(ValueError):record(data,24)

    def test_unexpected_image_change_or_length(self):
        data=fixture();bad=bytearray(data);bad[0]^=1
        with self.assertRaises(ValueError):compare_streams(io.BytesIO(data),io.BytesIO(bad),[])
        with self.assertRaises(ValueError):compare_streams(io.BytesIO(data),io.BytesIO(data+b'x'),[])

    def test_batch_keeps_independent_slots(self):
        data=fixture()*2;document=plan(data,[24,len(fixture())+24])
        for entry in document['entries']:entry['translation']='Quer ser um\nHunter?'
        patches=changes(data,document);self.assertEqual(len(patches),2)
        output=bytearray(data)
        for patch in patches:output[patch['offset']:patch['offset']+len(patch['after'])]=patch['after']
        result=compare_streams(io.BytesIO(data),io.BytesIO(output),patches,chunk_size=13)
        self.assertTrue(result['all_bytes_match_expected_patch'])
        self.assertEqual(len(output),len(data))

if __name__=='__main__':unittest.main()
