import copy
import json
import re
import sys
import unittest
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
import minigames_release as release


class MinigamesReleaseTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from interface_text import compile_draft
        cls.elf=release.ELF.read_bytes()
        cls.parent=json.loads((release.ROOT/release.PARENT).read_bytes())
        cls.parents,cls.parent_report=compile_draft(cls.elf,cls.parent)
        cls.revised,cls.new,cls.evidence=release.derive(cls.elf,cls.parents)
        cls.content=json.loads((release.ROOT/release.CONTENT).read_bytes())
        cls.child=json.loads((release.ROOT/release.CHILD).read_bytes())
        cls.manifest=release.binding_load(cls.child['all_minigames_release'])
        cls.patches=cls.revised+cls.new

    def test_manifest_reproduces_all_outputs(self):
        self.assertEqual(self.manifest['new'],[release.metadata(p) for p in self.new])
        self.assertEqual(self.manifest['revised'],[release.metadata(p) for p in self.revised])
        self.assertEqual(self.manifest['evidence'],self.evidence)

    def test_source_bound_child_rejects_unrelated_changes(self):
        self.assertEqual(release.validate(self.child)[0],self.parent)
        changed=copy.deepcopy(self.child)
        changed['entries'][0]['translation']='Outro texto'
        with self.assertRaises(ValueError):
            release.validate(changed)
        binding=copy.deepcopy(self.child['all_minigames_release'])
        binding['sha256']='0'*64
        with self.assertRaises(ValueError):
            release.binding_load(binding)

    def test_scope_includes_all_six_resource_families(self):
        resources={e['resource'] for e in self.evidence}
        self.assertEqual(resources,{'DATA/NDATA/NDATA.SDA'}|{
            'DATA/RDATA/'+name+'.SDA' for name in ('RMGALAN','RMGDANCE','RMGDOG','RMGKAERU','RMGTANK')})
        self.assertEqual(len(self.evidence),53)
        self.assertEqual(sum(bool(e['instructions']) for e in self.evidence),17)
        self.assertEqual(sum(len(e['words']) for e in self.evidence),200)

    def test_pixel_changes_stay_inside_reviewed_rectangles(self):
        for spec,proof in zip(self.content['textures'],self.evidence):
            p=next(p for p in self.patches if p['resource']==spec['resource']
                   and p['offset']==spec['offset']+proof['texture']['pixel_offset'])
            original=release.original(spec['resource'])
            meta=proof['texture'];start=spec['offset'];header=original[start:p['offset']]
            parent=next((q for q in self.parents if q['id']==p['id']),None)
            old=release.unpack_indices(header+(parent['after'] if parent else p['before']),meta)
            new=release.unpack_indices(header+p['after'],meta)
            rectangles=[r['rect'] for r in spec['labels']]+spec.get('erase',[])
            if 'panel' in spec:rectangles.append(spec['panel']['rect'])
            if 'cloth' in spec:rectangles.append(spec['cloth']['rect'])
            for i,(a,b) in enumerate(zip(old,new)):
                if a!=b:
                    x,y=i%meta['width'],i//meta['width']
                    self.assertTrue(any(l<=x<r and t<=y<z for l,t,r,z in rectangles),(spec['offset'],x,y))

    def test_four_bit_and_eight_bit_round_trips(self):
        depths=set()
        for proof in self.evidence:
            resource=proof['resource'];at=proof['offset'];meta=proof['texture'];depths.add(meta['bpp'])
            p=next(p for p in self.patches if p['resource']==resource and p['offset']==at+meta['pixel_offset'])
            raw=release.original(resource)[at:at+meta['pixel_offset']+meta['pixel_bytes']]
            changed=raw[:meta['pixel_offset']]+p['after']
            self.assertEqual(release.replace_indices(changed,release.unpack_indices(raw,meta)),raw)
            self.assertEqual(len(p['before']),len(p['after']))
        self.assertEqual(depths,{4,8})

    def test_instruction_icons_and_examples_keep_their_pixels(self):
        for spec,proof in zip(self.content['textures'],self.evidence):
            if 'panel' not in spec:continue
            meta=proof['texture'];at=spec['offset'];raw=release.original(spec['resource'])
            p=next(p for p in self.patches if p['resource']==spec['resource'] and p['offset']==at+meta['pixel_offset'])
            old=release.image(raw[at:at+meta['pixel_offset']+meta['pixel_bytes']],meta)
            new=release.image(raw[at:at+meta['pixel_offset']]+p['after'],meta)
            for part in spec['panel']['parts']:
                if part['kind']!='copy':continue
                l,t,r,b=part['rect'];x,y=part['x'],part['y']
                for iy in range(b-t):
                    for ix in range(r-l):
                        px,py=x+ix,y+iy
                        if any(a<=px<c and z<=py<d for a,z,c,d in (s['rect'] for s in spec['labels'])):
                            continue
                        self.assertEqual(new.getpixel((px,py)),old.getpixel((l+ix,t+iy)))

    def test_frog_controls_keep_all_original_button_icons(self):
        resource='DATA/RDATA/RMGKAERU.SDA';at=0x154e00
        raw=release.original(resource);meta,_=release.inspect_texture(raw[at:])
        p=next(p for p in self.patches if p['resource']==resource and p['offset']==at+meta['pixel_offset'])
        old=release.image(raw[at:],meta);new=release.image(raw[at:at+meta['pixel_offset']]+p['after'],meta)
        for rect in [(0,0,24,24),(72,0,96,24),(160,0,184,24),(0,24,24,48),(0,48,24,72),(176,24,201,48)]:
            self.assertEqual(old.crop(rect).tobytes(),new.crop(rect).tobytes())

    def test_elf_preserves_icons_formatting_and_exact_cell_bounds(self):
        patches=[p for p in self.new if p['resource']=='SLUS_212.93']
        self.assertEqual(len(patches),27)
        for p in patches:
            self.assertEqual(p['before'],self.elf[p['offset']:p['offset']+len(p['before'])])
            self.assertEqual(release.ICON.findall(p['before']),release.ICON.findall(p['after']))
            self.assertEqual(len(p['before']),len(p['after']))
            self.assertEqual(p['after'][-1],0)
        for at in (0x31e160,0x31e7c8,0x31ec08):
            p=next(p for p in patches if p['offset']==at)
            self.assertEqual(len(p['after']),40)

    def test_minigame_word_cannot_overflow_a_sprite(self):
        with self.assertRaises(ValueError):
            release.font_mask('PALAVRA IMPOSSÍVEL','arial',16,2,2,1)

    def test_dense_dance_letters_keep_the_original_transparent_background(self):
        resource='DATA/RDATA/RMGDANCE.SDA';at=0x130e00
        raw=release.original(resource);meta,_=release.inspect_texture(raw[at:])
        old=release.image(raw[at:],meta)
        p=next(p for p in self.patches if p['resource']==resource and p['offset']==at+meta['pixel_offset'])
        new=release.image(raw[at:at+meta['pixel_offset']]+p['after'],meta)
        self.assertEqual(new.getpixel((192,32)),old.getpixel((400,100)))

    def test_japanese_roulette_table_has_no_untranslated_bottom_strip(self):
        resource='DATA/NDATA/NDATA.SDA';at=0x6d6000
        raw=release.original(resource);meta,_=release.inspect_texture(raw[at:])
        p=next(p for p in self.patches if p['resource']==resource and p['offset']==at+meta['pixel_offset'])
        new=release.image(raw[at:at+meta['pixel_offset']]+p['after'],meta)
        self.assertEqual(len(set(new.crop((35,380,480,490)).tobytes())),1)

    def test_dog_rules_keep_automatic_fights_and_five_rounds(self):
        dog=next(s['panel'] for s in self.content['textures']
                 if s['resource']=='DATA/RDATA/RMGDOG.SDA' and 'panel' in s)
        text=' '.join(p.get('text','') for p in dog['parts'])
        self.assertIn('automáticas',text)
        self.assertIn('cinco rodadas',text)
        self.assertIn('prêmio acumulado',text)

    def test_card_ranks_and_frog_proper_names_are_preserved(self):
        for at in (0xfab800,0xfec000,0x102c800,0x106d000):
            proof=next(e for e in self.evidence if e['offset']==at and e['resource']=='DATA/NDATA/NDATA.SDA')
            p=next(p for p in self.patches if p['resource']==proof['resource'] and p['offset']==at+proof['texture']['pixel_offset'])
            old=release.original(proof['resource'])[at:];meta=proof['texture']
            before=release.image(old,meta);after=release.image(old[:meta['pixel_offset']]+p['after'],meta)
            self.assertEqual(before.crop((0,0,432,512)).tobytes(),after.crop((0,0,432,512)).tobytes())
            if at in (0x102c800,0x106d000):
                self.assertEqual(before.crop((432,220,504,330)).tobytes(),after.crop((432,220,504,330)).tobytes())
        proof=next(e for e in self.evidence if e['resource']=='DATA/RDATA/RMGKAERU.SDA' and e['offset']==0x11ac40)
        p=next(p for p in self.patches if p['resource']==proof['resource'] and p['offset']==proof['offset']+proof['texture']['pixel_offset'])
        old=release.original(proof['resource'])[proof['offset']:];meta=proof['texture']
        before=release.image(old,meta);after=release.image(old[:meta['pixel_offset']]+p['after'],meta)
        self.assertEqual(before.crop((0,0,136,240)).tobytes(),after.crop((0,0,136,240)).tobytes())

    def test_language_neutral_money_reels_are_preserved(self):
        proof=next(e for e in self.evidence if e['resource']=='DATA/RDATA/RMGTANK.SDA')
        p=next(p for p in self.patches if p['resource']==proof['resource'] and p['offset']==proof['offset']+proof['texture']['pixel_offset'])
        old=release.original(proof['resource'])[proof['offset']:];meta=proof['texture']
        a=release.image(old,meta);b=release.image(old[:meta['pixel_offset']]+p['after'],meta)
        self.assertEqual(a.crop((0,0,512,24)).tobytes(),b.crop((0,0,512,24)).tobytes())


if __name__=='__main__':
    unittest.main()
