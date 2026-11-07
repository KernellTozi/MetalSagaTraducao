import copy,json,mmap,sys,struct,tempfile,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
import final_candidate as f
import category_pool as categories
from gfi import decode


class FinalCandidateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from interface_text import compile_draft
        cls.elf=f.ELF.read_bytes();cls.parent=json.loads((f.ROOT/f.PARENT).read_bytes())
        cls.parents,cls.report=compile_draft(cls.elf,cls.parent)
        cls.new,cls.revised,cls.removed,cls.evidence=f.derive(cls.elf,cls.parents)
        cls.child=json.loads((f.ROOT/f.CHILD).read_bytes())
        cls.m=f.binding_load(cls.child['final_candidate_review'])

    def test_manifest_reproduces_all_outputs(self):
        self.assertEqual(self.m['new'],[f.metadata(p) for p in self.new])
        self.assertEqual(self.m['revised'],[f.metadata(p) for p in self.revised])
        self.assertEqual(self.m['removed'],self.removed)
        self.assertEqual(self.m['evidence'],self.evidence)

    def test_parent_hash_and_unrelated_changes_refused(self):
        self.assertEqual(f.validate(self.child)[0],self.parent)
        changed=copy.deepcopy(self.child);changed['entries'][0]['translation']='Outra'
        with self.assertRaises(ValueError):f.validate(changed)
        binding=copy.deepcopy(self.child['final_candidate_review']);binding['sha256']='0'*64
        with self.assertRaises(ValueError):f.binding_load(binding)

    def test_categories_fit_original_pool_and_all_refs_resolve(self):
        patch=next(p for p in self.new if p['id']=='final.categories.pool')
        self.assertEqual(len(patch['before']),72);self.assertEqual(len(patch['after']),72)
        for row in self.evidence['categories']['strings']:
            at=row['va']-categories.DELTA-categories.START
            self.assertEqual(decode(patch['after'][at:].split(b'\0')[0]),row['translation'])
        for row in self.evidence['categories']['references']:
            ref=row['consumer'];at=ref.get('immediate_offset',ref['offset'])
            updated=next((p for p in self.new if p['id']==f'final.category.reference.{at:08x}'),None)
            word=struct.unpack('<I',updated['after'] if updated else self.elf[at:at+4])[0]
            if ref['kind']=='data-pointer':self.assertEqual(word,row['target_va'])
            else:
                high=struct.unpack_from('<I',self.elf,ref['offset'])[0]&65535
                low=word&65535;low=low if low<32768 else low-65536
                self.assertEqual((high<<16)+low,row['target_va'])

    def test_category_native_length_and_unicode_roundtrip(self):
        from spack_ui import execute_byte_length
        for text in categories.NAMES.values():
            raw=f.encode(text);self.assertEqual(decode(raw),text)
            self.assertEqual(execute_byte_length(self.elf,raw),len(raw))

    def test_sprite_icons_and_unrelated_pixels_unchanged(self):
        patch=next(p for p in self.revised if p['id']=='reported.raster.tank')
        raw=f.original(f.HMAP);record=raw[0x80:];meta,_=f.inspect_texture(record)
        before=f.unpack_indices(record,meta)
        for y in range(256):
            for x in range(256):
                if 90<=x<192 and (44<=y<70 or 118<=y<144):continue
                self.assertEqual(patch['after'][y*256+x],before[y*256+x])
        palette=f.display_palette(record)
        for y in (69,143):
            # The recovered underlay remains black and fades out to the right.
            a=palette[patch['after'][y*256+91]];b=palette[patch['after'][y*256+190]]
            self.assertEqual(a[:3],(0,0,0));self.assertEqual(b[:3],(0,0,0));self.assertGreater(a[3],b[3])

    def test_headers_only_touch_reviewed_cells(self):
        patch=next(p for p in self.revised if p['id']=='observed.headers')
        old=next(p for p in self.parents if p['id']==patch['id'])
        for i,(a,b) in enumerate(zip(old['after'],patch['after'])):
            if a!=b:self.assertTrue((4<=i%256<62 and 60<=i//256<72) or
                                   (4<=i%256<156 and 216<=i//256<228))

    def test_locations_fixed_32_byte_prefix_and_census(self):
        rows=self.evidence['locations'];self.assertEqual(len(rows),18)
        self.assertEqual(sum(r['translation']=='Caverna desconhecida' for r in rows),2)
        for row in rows:
            p=next(p for p in self.new if p['id']==f'final.map.{row["field_offset"]:08x}')
            self.assertEqual(len(p['before']),len(p['after']));self.assertLessEqual(len(p['after']),32)
            self.assertEqual(decode(p['after'].split(b'\0')[0]),row['translation'])

    def test_diary_native_ellipsis_and_pipe_preserved(self):
        p=next(p for p in self.new if p['resource']==f.DIARY)
        self.assertEqual(p['before'].count(b'\x81\x63'),1)
        self.assertEqual(p['after'].count(b'\x81\x63'),1)
        self.assertEqual(p['before'].count(b'|'),p['after'].count(b'|'))
        self.assertIn(b'MC Hamir?',p['after']);self.assertEqual(len(p['before']),len(p['after']))

    def test_printf_and_alternate_yes_no(self):
        for p in f.literal_patches(self.elf):
            self.assertEqual(f.FORMAT.findall(p['before']),f.FORMAT.findall(p['after']))
            self.assertEqual(len(p['before']),len(p['after']))
        for at,expected in ((0x349a18,'Sim'),(0x349a20,'Não')):
            p=next(p for p in self.new if p['offset']==at and p['resource']=='SLUS_212.93')
            self.assertEqual(decode(p['after'].split(b'\0')[0]),expected)

    def test_ore_name_and_narrative_review_are_explicit(self):
        p=next(p for p in self.revised if p['id']=='item.name.0665')
        self.assertEqual(decode(p['after'].split(b'\0')[0]),'Minério pequeno')
        self.assertEqual(len(f.encode('Minério pequeno')),16)
        from build_translation_pilot import load_draft
        draft,_=load_draft(f.ROOT/f.CHILD_MAP);f.validate_narrative(draft)
        self.assertEqual(set(f.NARRATIVE),{'map.msg.040f10d4','map.msg.01dee21c'})
        self.assertTrue(all('Nãããão' in t and 'Noooo' not in t for t in f.NARRATIVE.values()))

    def test_compile_preserves_unrelated_patches(self):
        from unittest.mock import patch
        with patch('interface_text.compile_draft',return_value=(self.parents,self.report)):
            out,report=f.compile_interface(self.elf,self.child)
        changed={p['id'] for p in self.revised}|set(self.removed)
        by={p['id']:p for p in out}
        for old in self.parents:
            if old['id'] not in changed:self.assertEqual(old,by[old['id']])
        self.assertEqual(report['accepted'],self.report['accepted']+26)


class DeliveryCopyTests(unittest.TestCase):
    def test_old_images_survive_if_desktop_copy_conflicts(self):
        import package_final_candidate as pack
        from unittest.mock import patch
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);src=root/'work/new.iso';src.parent.mkdir();src.write_bytes(b'new fixture')
            desk=root/'desktop';desk.mkdir();(desk/'MetalSaga-PTBR-Candidata-Final-v070.iso').write_bytes(b'unrelated')
            old=root/'work/old.iso';old.write_bytes(b'old fixture')
            row={'path':'work/old.iso','sha256':pack.digest(old),'size':old.stat().st_size}
            values={'ROOT':root,'SOURCE':src,'MAINTENANCE':root/'dist/maintenance.iso',
                    'OLD_BACKUP':root/'dist/old.iso','REPORT':root/'report.json'}
            with patch.multiple(pack,**values),patch.object(pack,'verify_image',return_value={'sha256':pack.digest(src)}),\
                 patch.object(pack,'desktop_directory',return_value=desk),patch.object(pack,'old_images',return_value=[row]):
                with self.assertRaises(ValueError):pack.package(True)
            self.assertTrue(old.exists());self.assertEqual(old.read_bytes(),b'old fixture')

    def test_old_images_removed_only_after_two_verified_copies(self):
        import package_final_candidate as pack
        from unittest.mock import patch
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);src=root/'work/new.iso';src.parent.mkdir();src.write_bytes(b'new fixture')
            desk=root/'desktop';desk.mkdir();old=root/'work/old.iso';old.write_bytes(b'old fixture')
            row={'path':'work/old.iso','sha256':pack.digest(old),'size':old.stat().st_size}
            values={'ROOT':root,'SOURCE':src,'MAINTENANCE':root/'dist/maintenance.iso',
                    'OLD_BACKUP':root/'dist/old.iso','REPORT':root/'report.json'}
            with patch.multiple(pack,**values),patch.object(pack,'verify_image',return_value={'sha256':pack.digest(src)}),\
                 patch.object(pack,'desktop_directory',return_value=desk),patch.object(pack,'old_images',return_value=[row]):
                result=pack.package(True)
            self.assertFalse(old.exists());self.assertEqual(len(result['removed']),1)
            self.assertTrue(result['final_source_hash_verified'] and result['final_maintenance_hash_verified'] and result['final_desktop_hash_verified'])
            # Restore write permission only in the isolated temporary fixture.
            import os,stat
            os.chmod(root/'dist/maintenance.iso',stat.S_IWRITE|stat.S_IREAD)

    def test_verified_copy_is_repeatable_and_refuses_overwrite(self):
        from package_final_candidate import verified_copy,digest
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);src=root/'source.iso';src.write_bytes(b'fixture candidate')
            expected=digest(src);out=root/'out.iso'
            self.assertEqual(verified_copy(src,out,expected,allowed_root=root),'copied_verified')
            self.assertEqual(verified_copy(src,out,expected,allowed_root=root),'existing_verified')
            out.write_bytes(b'another file')
            with self.assertRaises(ValueError):verified_copy(src,out,expected,allowed_root=root)

    def test_copy_rejects_escape_and_wrong_source(self):
        from package_final_candidate import verified_copy,digest
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);src=root/'source.iso';src.write_bytes(b'fixture')
            with self.assertRaises(ValueError):verified_copy(src,root.parent/'outside.iso',digest(src),allowed_root=root)
            with self.assertRaises(ValueError):verified_copy(src,root/'out.iso','0'*64,allowed_root=root)
            self.assertFalse((root/'out.iso').exists())


if __name__=='__main__':unittest.main()
