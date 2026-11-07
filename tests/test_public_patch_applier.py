"""Small local fixtures exercise rejection paths without invoking a decoder."""
import hashlib,json,shutil,subprocess,tempfile,unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
def sha(data):return hashlib.sha256(data).hexdigest()


class PublicApplierTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.root=Path(self.temp.name)
        self.source=self.root/'Original.iso';self.source.write_bytes(b'original fixture')
        self.target=self.root/'Translated.iso';self.patch=self.root/'translation.xdelta';self.patch.write_bytes(b'patch fixture')
        self.decoder=self.root/'decoder.exe';self.decoder.write_bytes(b'not executed')
        self.script=self.root/'Aplicar-Patch.ps1';shutil.copyfile(ROOT/'release/Aplicar-Patch.ps1',self.script)
        self.m={'source':{'size':self.source.stat().st_size,'sha256':sha(self.source.read_bytes())},
                'target':{'file':self.target.name,'size':10,'sha256':'0'*64},
                'patch':{'file':self.patch.name,'sha256':sha(self.patch.read_bytes())},
                'decoder':{'file':self.decoder.name,'sha256':sha(self.decoder.read_bytes())}}

    def tearDown(self):self.temp.cleanup()

    def run_applier(self,target=None):
        (self.root/'manifesto.json').write_text(json.dumps(self.m),encoding='utf-8')
        result=subprocess.run(['powershell.exe','-NoProfile','-ExecutionPolicy','Bypass','-File',str(self.script),
             '-IsoOriginal',str(self.source),'-Destino',str(target or self.target),'-SemInterface'],capture_output=True)
        self.assertEqual(result.returncode,1,result.stdout+result.stderr)
        self.assertFalse(Path(str(self.target)+'.partial').exists())

    def test_wrong_source_size(self):
        self.source.write_bytes(b'wrong');self.run_applier();self.assertFalse(self.target.exists())

    def test_wrong_source_hash(self):
        self.source.write_bytes(b'x'*self.source.stat().st_size);self.run_applier();self.assertFalse(self.target.exists())

    def test_existing_output_preserved(self):
        self.target.write_bytes(b'existing output');self.run_applier();self.assertEqual(self.target.read_bytes(),b'existing output')

    def test_preexisting_partial_preserved(self):
        partial=Path(str(self.target)+'.partial');partial.write_bytes(b'unrelated partial')
        (self.root/'manifesto.json').write_text(json.dumps(self.m),encoding='utf-8')
        r=subprocess.run(['powershell.exe','-NoProfile','-ExecutionPolicy','Bypass','-File',str(self.script),
            '-IsoOriginal',str(self.source),'-Destino',str(self.target),'-SemInterface'],capture_output=True)
        self.assertEqual(r.returncode,1);self.assertEqual(partial.read_bytes(),b'unrelated partial')

    def test_tampered_patch_rejected(self):
        self.patch.write_bytes(b'altered patch');self.run_applier();self.assertFalse(self.target.exists())

    def test_source_cannot_be_destination(self):
        original=self.source.read_bytes();self.run_applier(self.source);self.assertEqual(self.source.read_bytes(),original)

    def test_manifest_cannot_escape_package_directory(self):
        self.m['patch']['file']='../outside.xdelta';self.run_applier();self.assertFalse(self.target.exists())


if __name__=='__main__':unittest.main()
