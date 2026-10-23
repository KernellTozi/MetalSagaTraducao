import json,sys,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools'))
from prepare_title_wordart import prepare
from interface_texture_pack import pillow

class WordArtPreparation(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(dir=ROOT/'work');self.addCleanup(self.tmp.cleanup);self.root=Path(self.tmp.name)
        Image=pillow();from PIL import ImageDraw
        im=Image.new('RGBA',(800,180));d=ImageDraw.Draw(im)
        for y,w in ((5,400),(65,330),(125,360)):d.rectangle((20,y,w,y+35),fill='white')
        self.master=self.root/'master.png';im.save(self.master)
    def test_complete_word_preparation_and_palette(self):
        Image=pillow();before=self.master.read_bytes();report=prepare(self.master,self.root/'output')
        self.assertEqual(before,self.master.read_bytes());self.assertFalse(report['iso_modified']);self.assertFalse(report['runtime_tested'])
        self.assertEqual(len(report['rows']),3)
        for row in report['rows']:self.assertEqual(row['white_cap_height'],16);self.assertEqual(row['cell_size'],[228,24])
        palettes=[]
        for name in ('novo-jogo','retomar','instalar'):
            with Image.open(self.root/'output'/(name+'-24px.png')) as im:self.assertEqual(im.mode,'RGBA');self.assertEqual(im.size,(228,24))
            with Image.open(self.root/'output'/(name+'-paleta-original.png')) as im:
                self.assertEqual(im.mode,'P');palettes.append((im.getpalette(),im.info['transparency']))
        self.assertEqual(palettes[0],palettes[1]);self.assertEqual(palettes[1],palettes[2])
        self.assertEqual(list((self.root/'output').rglob('*.iso')),[])
    def test_existing_output_refused(self):
        folder=self.root/'existing';folder.mkdir()
        with self.assertRaises(ValueError):prepare(self.master,folder)
    def test_nontransparent_master_refused(self):
        Image=pillow();Image.new('RGB',(800,180)).save(self.master)
        with self.assertRaises(ValueError):prepare(self.master,self.root/'output')
        self.assertFalse((self.root/'output').exists())
    def test_wrong_line_count_refused(self):
        Image=pillow();from PIL import ImageDraw
        im=Image.new('RGBA',(800,180));ImageDraw.Draw(im).rectangle((20,10,500,70),fill='white');im.save(self.master)
        with self.assertRaises(ValueError):prepare(self.master,self.root/'output')
        self.assertFalse((self.root/'output').exists())

if __name__=='__main__':unittest.main()
