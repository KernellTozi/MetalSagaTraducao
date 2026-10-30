import json,sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
import item_box_proof as probe
from interface_text import SOURCE
from dialogue import ROOT


class BoxProofTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.elf=SOURCE.read_bytes()

    def test_original_virtual_setter_getter_with_both_skins(self):
        for style in (0,1):
            for x,y,w,h in ((80,144,272,208),(0,0,320,240),(336,144,288,68)):
                r=probe.panel(self.elf,x,y,w,h,style)
                self.assertEqual(r['requested_and_returned'],[x,y,w,h])
                self.assertEqual(r['stored_rectangle'][2],w+4)

    def test_original_shop_multiplication_and_price_column(self):
        r=probe.shop(self.elf)
        self.assertEqual(r['logical_row_width'],374)
        self.assertEqual(r['eight_digit_price_origin'],264)
        self.assertEqual(r['name_budget_before_price'],242)

    def test_modified_code_and_unknown_skin_rejected(self):
        data=bytearray(self.elf);data[0x1b6268]^=1
        with self.assertRaises(ValueError):probe.panel(bytes(data))
        with self.assertRaises(ValueError):probe.panel(self.elf,style=2)

    def test_19_byte_message_budget_preserves_original_template_set(self):
        proof=json.loads((ROOT/'reports/prova-nove-nomes-v002.json').read_bytes())
        b=proof['budgets']
        self.assertEqual((b['field_count'],b['page_count'],b['item_byte_bound']),(34,35,19))
        self.assertEqual((b['maximum_page_content_cells'],b['maximum_body_bytes']),(92,333))
        old=json.loads((ROOT/'reports/prova-seis-nomes-v007.json').read_bytes())['budgets']
        self.assertEqual([(p['id'],p['page'],p['text_sha256']) for p in b['pages']],
                         [(p['id'],p['page'],p['text_sha256']) for p in old['pages']])

    def test_runner_rejects_out_of_scope_code_and_writes_to_source(self):
        regs=[0]*32;regs[4]=0x600000;regs[31]=0x7ffff0
        with self.assertRaises(ValueError):probe.scalar(self.elf,0x43720,regs,[(0x600000,bytes(64),False)],0x7ffff0)
        with self.assertRaises(ValueError):probe.scalar(self.elf,0x43734,[0]*32,[],0x7ffff0)


if __name__=='__main__':unittest.main()
