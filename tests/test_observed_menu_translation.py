import copy
import json
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
import observed_menu_translation as menu
from interface_textures import inspect_texture
from interface_texture_pack import unpack_indices,replace_indices


class ObservedMenuTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.elf=menu.ELF.read_bytes()
        cls.patches,cls.evidence=menu.compile_additions(cls.elf)
        cls.manifest=json.loads((menu.ROOT/menu.MANIFEST).read_bytes())
        cls.child=json.loads((menu.ROOT/menu.CHILD).read_bytes())

    def test_manifest_reproduces_all_18_physical_patches(self):
        self.assertEqual(menu.template(self.elf),self.manifest)
        self.assertEqual(len(self.patches),18)
        self.assertEqual(len(self.evidence['literal_rows']),15)

    def test_all_fixed_literals_keep_size_and_final_nul(self):
        for p in self.patches:
            if p['resource']!='SLUS_212.93':continue
            self.assertEqual(len(p['before']),len(p['after']))
            self.assertEqual(p['after'][-1],0)
            self.assertLessEqual(len(p['after'].split(b'\0')[0]),len(p['before'])-1)
            self.assertEqual(menu.FORMAT.findall(p['before']),menu.FORMAT.findall(p['after']))
            self.assertEqual(p['before'].count(b'\n'),p['after'].count(b'\n'))

    def test_save_native_colon_eight_visible_columns_and_16_byte_cells(self):
        for p in self.patches:
            if p['offset'] not in menu.SAVE:continue
            prefix,tail=p['after'].split(b'\x81F',1)
            self.assertEqual(len(menu.decode(prefix)),8)
            self.assertEqual(p['before'][10:].rstrip(b'\0'),tail.rstrip(b'\0'))
            self.assertEqual(len(p['before']),16)
            self.assertEqual(p['after'][-1],0)

    def test_controller_actions_preserve_original_icons_in_order(self):
        p=next(p for p in self.patches if p['offset']==0x32ff38)
        for icon in menu.ICONS:
            self.assertEqual(p['after'].count(icon),1)
        self.assertLess(p['after'].index(menu.ICONS[0]),p['after'].index(menu.ICONS[1]))
        self.assertLess(p['after'].index(menu.ICONS[1]),p['after'].index(menu.ICONS[2]))
        self.assertIn(b'Comprar',p['after']);self.assertIn(b'Sair',p['after'])

    def test_warning_concatenation_does_not_grow_or_reach_128_bytes(self):
        rows=[p for p in self.patches if 0x32ed10<=p['offset']<0x32ed80]
        self.assertEqual(len(rows),6)
        # All 64 combinations of the six append-only warning strings.
        for bits in range(64):
            selected=[p for i,p in enumerate(rows) if bits>>i&1]
            before=b''.join(p['before'].split(b'\0')[0] for p in selected)
            after=b''.join(p['after'].split(b'\0')[0] for p in selected)
            self.assertLessEqual(len(after),len(before))
            self.assertLess(len(after),128)

    def test_native_headers_only_change_the_three_cells(self):
        p=next(p for p in self.patches if p['id']=='observed.headers')
        for i,(a,b) in enumerate(zip(p['before'],p['after'])):
            if a==b:continue
            x,y=i%256,i//256
            self.assertTrue(any(4<=x<right and top<=y<top+12 for top,right,_ in menu.HEADERS))
        self.assertEqual([r['translation'] for r in self.evidence['headers']],['CIDADES','FROTA','MEMBROS'])
        self.assertTrue(all(not r['scaling'] for r in self.evidence['headers']))

    def test_native_header_f_keeps_e_stem_and_removes_only_bottom_bar(self):
        source=menu.original(menu.SPACK)[0x8c830:0x9cc40]
        glyphs=menu.header_glyphs(source);w,e=glyphs['E'];_,f=glyphs['F']
        self.assertEqual(e[:9*w+3],f[:9*w+3])
        self.assertEqual(f[9*w+3:],bytes([241])*(w-3))

    def test_vending_changes_only_instruction_and_retains_bonus_wall(self):
        for p,row in zip([p for p in self.patches if p['resource']==menu.NDATA],self.evidence['vending']):
            left,top,right,bottom=row['rect'];width=512 if row['entry']==13 else 128
            for i,(a,b) in enumerate(zip(p['before'],p['after'])):
                if a==b:continue
                self.assertTrue(left<=i%width<right and top<=i//width<bottom)
            self.assertGreater(sum(v!=0 for v in p['after']),0)
            self.assertEqual(row['alpha'],128)
            self.assertTrue(all(r['horizontal_scale']==1.0 for r in row['layout']))
            raw=menu.original(menu.NDATA)
            start=0x97000 if row['entry']==13 else 0xd7800
            palette=[tuple(raw[start+16+4*i:start+20+4*i]) for i in range(256)]
            for a,z in ((312,328),(330,346)):
                white=sum(palette[p['after'][y*width+x]][3]==128 and
                          min(palette[p['after'][y*width+x]][:3])>=150
                          for y in range(a,z) for x in range(left,right))
                self.assertGreater(white,20,'Each line must retain visible opaque ink on both sides of the seam')

    def test_palette_header_tail_and_reverse_transport(self):
        for resource,start,end in ((menu.SPACK,0x8c830,0x9cc40),
                                   (menu.NDATA,0x97000,0xd7800),(menu.NDATA,0xd7800,0xe8000)):
            raw=menu.original(resource);record=raw[start:end];meta,_=inspect_texture(record)
            p=next(p for p in self.patches if p['resource']==resource and p['offset']==start+meta['pixel_offset'])
            changed=bytearray(record);at=meta['pixel_offset'];changed[at:at+len(p['after'])]=p['after']
            self.assertEqual(record[:at],changed[:at])
            self.assertEqual(record[at+meta['pixel_bytes']:],changed[at+meta['pixel_bytes']:])
            self.assertEqual(replace_indices(changed,unpack_indices(record,meta)),record)

    def test_wrong_elf_and_oversized_label_rejected(self):
        data=bytearray(self.elf);data[0x13b090]^=1
        with self.assertRaises(ValueError):menu.bindings(data)
        with patch.dict(menu.LITERALS,{0x348f78:'Este texto não cabe'}):
            with self.assertRaises(ValueError):menu.literal_rows(self.elf)

    def test_no_relocation_and_exact_parent_binding(self):
        parent,_=menu.validate_interface(self.child)
        self.assertEqual(parent,json.loads((menu.ROOT/menu.PARENT).read_bytes()))
        for key in ('status','layout_profile','npc_and_choice_release'):
            child=copy.deepcopy(self.child);child[key]='changed'
            with self.assertRaises(ValueError):menu.validate_interface(child)
        binding=copy.deepcopy(self.child);binding['observed_menu_release']['sha256']='0'*64
        with self.assertRaises(ValueError):menu.validate_interface(binding)
        self.assertFalse(any(p['resource'].endswith('.GFI') for p in self.patches))
        self.assertFalse(any(0x349248<=p['offset']<=0x349e90 for p in self.patches if p['resource']=='SLUS_212.93'))

    def test_save_padding_and_interior_address_evidence_are_not_free_capacity(self):
        changed=bytearray(self.elf);changed[0x32120d]=1
        with self.assertRaises(ValueError):menu.literal_rows(changed)
        with patch.object(menu,'references',return_value={0x3211f4+0xff000:[{'kind':'data-pointer'}]}):
            with self.assertRaises(ValueError):menu.literal_rows(self.elf)

    def test_comparator_and_capacity_auditor_use_the_exact_parent(self):
        from verify_interface_revision import normalize_item_name_review_transition
        parent,_=menu.validate_interface(self.child)
        normalize_item_name_review_transition(parent,self.child,menu.ROOT/menu.PARENT,{}, {})
        with self.assertRaises(ValueError):
            normalize_item_name_review_transition(parent,self.child,menu.ROOT/'translations/interface-v059.json',{}, {})
        from item_name_capacity import apply_authorized_fallback
        old=json.loads((menu.ROOT/'reports/capacidade-nomes-v001.json').read_bytes())
        self.assertEqual(apply_authorized_fallback(old,menu.ROOT/menu.CHILD)['counts']['blocked'],0)


if __name__=='__main__':unittest.main()
