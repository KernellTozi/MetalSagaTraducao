import copy
import json
import mmap
from pathlib import Path
import sys
import unittest
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
import screen_followup as follow
from interface_text import FORMAT


class FollowupTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.elf=follow.ELF.read_bytes();cls.raw=follow.original(follow.SPACK)
        cls.manifest=json.loads((follow.ROOT/follow.MANIFEST).read_bytes())
        cls.child=json.loads((follow.ROOT/follow.CHILD).read_bytes())
        cls.extra,cls.revised=follow.additions(cls.elf,cls.manifest)
        cls.stream=follow.MAP.open('rb');cls.map=mmap.mmap(cls.stream.fileno(),0,access=mmap.ACCESS_READ)

    @classmethod
    def tearDownClass(cls):cls.map.close();cls.stream.close()

    def test_exact_manifest_and_25_new_units(self):
        self.assertEqual(follow.template(self.elf),self.manifest)
        self.assertEqual(len(self.extra),23)
        self.assertEqual(len(self.revised),3)
        self.assertEqual(len(self.extra)+len(self.manifest['headers']),25)

    def test_literals_keep_printf_newlines_and_fixed_physical_spans(self):
        for p in self.extra+self.revised:
            self.assertEqual(len(p['before']),len(p['after']))
            if p['resource']!='SLUS_212.93':continue
            self.assertEqual(FORMAT.findall(p['before']),FORMAT.findall(p['after']))
            self.assertEqual(p['before'].count(b'\n'),p['after'].count(b'\n'))
            self.assertEqual(p['after'][-1],0)

    def test_stats_preserve_visible_prefix_columns_not_just_bytes(self):
        for p in self.revised:
            if p['offset'] not in follow.STATS:continue
            old=p['before'].split(b'\0')[0].decode('ascii')
            new=follow.decode(p['after'].split(b'\0')[0])
            self.assertEqual(len(old.split('%')[0]),len(new.split('%')[0]))
            self.assertEqual(len(follow.encode(new))-len(new),1)

    def test_native_monospaced_number_positions_match_exp_and_money(self):
        from choice_text_metrics import execute
        parent=json.loads((follow.ROOT/follow.PARENT).read_bytes())
        prior={r['id']:r['translation'] for r in parent['entries']}
        for mode in (0,2):
            for number in (0,25,999):
                for at,reference in ((0x3239e0,'Exp:       %3d'),(0x323a28,'Dinheiro        %8d')):
                    text=follow.STATS[at][1]%number
                    old=prior[f'elf.ui.{at:08x}']%number
                    width=execute(self.elf,text,mode=mode)['width']
                    self.assertEqual(width,execute(self.elf,reference%number,mode=mode)['width'])
                    self.assertEqual(width-execute(self.elf,old,mode=mode)['width'],11)

    def test_stats_reject_interior_references_and_wrong_original(self):
        with patch.object(follow,'references',return_value={0x3239e4+0xff000:[{'kind':'data-pointer'}]}):
            with self.assertRaises(ValueError):follow.literal_rows(self.elf)
        bad=bytearray(self.elf);bad[0x3239ef]=1
        with self.assertRaises(ValueError):follow.literal_rows(bytes(bad))

    def test_three_explicit_item_names_keep_attributes_and_legacy_locks(self):
        from item_names import protected
        names=[r for r in self.manifest['names'] if r['kind']=='item']
        self.assertEqual({r['id'] for r in names},{'item.name.0190','item.name.0864','item.name.0959'})
        self.assertTrue(protected(864));self.assertTrue(protected(959))
        for row in names:
            p=next(p for p in self.extra if p['id']==row['id'])
            self.assertEqual(len(p['after']),24)
            value=p['after'].split(b'\0')[0]
            self.assertLessEqual(len(value),16)
            self.assertEqual(follow.decode(value),row['translation'])
            record=bytearray(self.raw[row['offset']:row['offset']+128]);record[:24]=p['after']
            self.assertEqual(record[24:],self.raw[row['offset']+24:row['offset']+128])

    def test_animal_instinct_aliases_match_battle_action(self):
        patches=[p for p in self.extra if p['id'] in ('item.name.0864','item.name.0959','battle.action.0219')]
        self.assertEqual(len(patches),3)
        self.assertEqual({p['after'].split(b'\0')[0] for p in patches},{b'Instinto animal'})

    def test_cave_and_all_eleven_jukebox_names_without_record_growth(self):
        labels=self.manifest['map_labels']
        self.assertEqual(sum(r['translation']=='Vitrola' for r in labels),11)
        self.assertEqual(sum(r['translation']=='Toca da Cobra' for r in labels),2)
        for r in labels:
            p=next(p for p in self.extra if p['id']==r['id'])
            self.assertEqual(p['after'].split(b'\0')[0],follow.encode(r['translation']))
            if r['translation']=='Vitrola':self.assertEqual(len(p['after']),8)
        # Junkyard's Jukebox has a nonzero opaque byte at +31. It is outside
        # the exact eight-byte name patch and must not be cleared as padding.
        at=0x1df263d8
        self.assertEqual(self.map[at+31],255)
        p=next(p for p in self.extra if p['resource']==follow.MCT and p['offset']==at)
        field=bytearray(self.map[at:at+32]);field[:len(p['after'])]=p['after']
        self.assertEqual(field[31],255)

    def test_three_native_name_getters_return_pointer_without_writes(self):
        evidence=follow.getters(self.elf)
        self.assertEqual({r['type'] for r in evidence},{2,6,7})
        self.assertTrue(all(r['returns_existing_name_pointer'] for r in evidence))

    def test_two_header_cells_preserve_v061_art_and_glyph_height(self):
        from observed_menu_translation import render_headers
        parent=render_headers(self.raw)[0][0]
        p,layout=follow.header_revision(self.raw)
        self.assertEqual(p['before'],parent['before'])
        self.assertEqual([(r['translation'],r['width']) for r in layout],[('ITENS',59),('HABILIDADES',113)])
        self.assertTrue(all(r['height']==10 and not r['resized'] for r in layout))
        for i,(a,b) in enumerate(zip(parent['after'],p['after'])):
            if a==b:continue
            self.assertTrue(any(4<=i%256<right and top<=i//256<top+12 for top,right,_,_ in follow.HEADERS))

    def test_music_names_and_crimson_manzier_are_not_patched(self):
        from item_names import catalog
        crimson=next(r for r in catalog(self.raw) if r['index']==176)
        self.assertEqual(bytes.fromhex(crimson['source_hex']),b'Crimson Manzier')
        self.assertFalse(any(p['resource']==follow.SPACK and p['offset']<=crimson['offset']<p['offset']+len(p['after']) for p in self.extra))
        self.assertFalse(any(p['resource']=='DATA/NDATA/NDATA.SDA' for p in self.extra+self.revised))
        # Song-name atlases remain in NDATA. The technical ELF texJukebox
        # identifier is outside the translated command string.
        self.assertTrue(all(p['offset']!=0x331cc0 for p in self.extra if p['resource']=='SLUS_212.93'))

    def test_music_controller_tokens_remain_exact_and_ordered(self):
        p=next(p for p in self.extra if p['offset']==0x331cd0 and p['resource']=='SLUS_212.93')
        positions=[]
        for token in follow.JICONS:
            self.assertEqual(p['before'].count(token),1);self.assertEqual(p['after'].count(token),1)
            positions.append(p['after'].index(token))
        self.assertEqual(positions,sorted(positions))
        self.assertIn(follow.encode('Percussão'),p['after'])

    def test_discard_arrows_and_numeric_formats_keep_their_positions(self):
        p=next(p for p in self.extra if p['offset']==0x32af00 and p['resource']=='SLUS_212.93')
        for term in (b'\x81\xa8',b'%2d',b'%s'):
            self.assertEqual([i for i in range(len(p['before'])) if p['before'].startswith(term,i)],
                             [i for i in range(len(p['after'])) if p['after'].startswith(term,i)])
        self.assertIn(b'Carga',p['after']);self.assertIn(b'Livre',p['after'])

    def test_towing_labels_keep_fixed_slots_and_full_portuguese(self):
        for at,target in ((0x315e90,b'Reboque '),(0x315ea0,b'Rebocar '),(0x315f10,b'Soltar reboque ')):
            p=next(p for p in self.extra if p['offset']==at and p['resource']=='SLUS_212.93')
            self.assertEqual(p['after'].split(b'\0')[0],target)
            self.assertEqual(len(p['before']),len(p['after']))

    def test_exact_child_and_manifest_required(self):
        for key in ('iso_name','status','layout_profile'):
            bad=copy.deepcopy(self.child);bad[key]='bad'
            with self.assertRaises(ValueError):follow.validate_interface(bad)
        bad=copy.deepcopy(self.child);bad['screen_followup_release']['sha256']='0'*64
        with self.assertRaises(ValueError):follow.validate_interface(bad)
        bad=copy.deepcopy(self.manifest);bad['names'][0]['offset']+=1
        with self.assertRaises(ValueError):follow.additions(self.elf,bad)

    def test_statistics_comparator_only_widens_two_proved_cells(self):
        parent=json.loads((follow.ROOT/follow.PARENT).read_bytes());by={r['id']:r['translation'] for r in parent['entries']}
        old={};new={}
        for p in self.revised:
            if p['offset'] not in follow.STATS:continue
            at=p['offset'];length=len(self.elf[at:self.elf.index(b'\0',at)])+1
            value=follow.encode(by[p['id']]);key=(p['resource'],at)
            old[key]={**p,'before':p['before'][:length],'after':value+bytes(length-len(value))};new[key]=p
        follow.normalize_statistics(old,new)
        self.assertEqual({k:len(v['after']) for k,v in old.items()},{k:len(v['after']) for k,v in new.items()})
        from verify_interface_revision import normalize_item_name_review_transition
        with self.assertRaises(ValueError):
            normalize_item_name_review_transition(parent,self.child,follow.ROOT/'translations/interface-v060.json',old,new)
        from item_name_capacity import apply_authorized_fallback
        result=json.loads((follow.ROOT/'reports/capacidade-nomes-v001.json').read_bytes())
        self.assertEqual(apply_authorized_fallback(result,follow.ROOT/follow.CHILD)['counts']['blocked'],0)


if __name__=='__main__':unittest.main()
