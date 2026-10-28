import copy,json,struct,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools'))
import interface_gaps as gaps
from interface_text import SOURCE
from item_descriptions import original,RESOURCE
from name_entry_text import compile_name_entry
from gfi import encode,decode

class InterfaceGapsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.old=json.loads((ROOT/'translations/interface-v045.json').read_text(encoding='utf-8'))
        cls.new=json.loads((ROOT/'translations/interface-v046.json').read_text(encoding='utf-8'))
        cls.elf=SOURCE.read_bytes();cls.raw=original(RESOURCE)
        cls.before,_=compile_name_entry(cls.elf,cls.old['name_entry'])
        cls.after,cls.name_report=compile_name_entry(cls.elf,cls.new['name_entry'])
        cls.patches,cls.locations=gaps.compile_locations(cls.elf,cls.new['generic_destination_names'])

    def test_only_authorized_interface_fields_change_and_all_prior_content_frozen(self):
        gaps.validate_interface(self.new)
        changed={'name_entry','generic_destination_names','interface_gap_review','iso_name','status'}
        self.assertEqual({k:v for k,v in self.old.items() if k not in changed},{k:v for k,v in self.new.items() if k not in changed})
        self.assertEqual(len(self.new['item_names']['entries']),541)
        self.assertEqual(self.new['base_dialogue_draft'],'translations/regiao-inicial-v040.json')
        bad=copy.deepcopy(self.new);bad['entries'][0]['translation']='Extra'
        with self.assertRaises(ValueError):gaps.validate_interface(bad)

    def test_only_five_title_slot_bytes_change_no_native_bytes_or_other_legends(self):
        a=bytearray(self.elf);b=bytearray(self.elf)
        for out,patches in ((a,self.before),(b,self.after)):
            for p in patches:out[p['offset']:p['offset']+len(p['after'])]=p['after']
        self.assertEqual(b[0x32a31e:0x32a323],b'SAIR ')
        self.assertEqual({i for i,(x,y) in enumerate(zip(a,b)) if x!=y},set(range(0x32a31e,0x32a323)))
        for p in reversed(self.after):b[p['offset']:p['offset']+len(p['before'])]=p['before']
        self.assertEqual(b,self.elf)
        self.assertEqual(self.name_report['pending_command_semantics'],[])

    def test_exit_completion_and_commit_skip_are_bound_to_original_code(self):
        proof=gaps.title_proof(self.elf)
        self.assertEqual([(r['fade_field_9e'],r['completion']) for r in proof['terminal_and_dispatch_cases']],[(0,1),(1,0),(65535,0)])
        self.assertTrue(all(r['name_commit_skipped'] for r in proof['terminal_and_dispatch_cases']))
        bad=copy.deepcopy(self.new['name_entry']);bad['title_evidence']['terminal_and_dispatch_cases'][0]['completion']=0
        with self.assertRaises(ValueError):compile_name_entry(self.elf,bad)

    def test_historical_title_remains_locked_without_opt_in(self):
        bad=copy.deepcopy(self.old['name_entry'])
        for row in bad['entries']:
            for slot in row.get('slots',[]):
                if slot['translation']=='TITLE':slot['translation']='SAIR'
        with self.assertRaises(ValueError):compile_name_entry(self.elf,bad)

    def test_four_location_slots_roundtrip_without_metadata_or_other_destinations(self):
        out=bytearray(self.raw);allowed=set()
        for p in self.patches:
            self.assertEqual(len(p['before']),32);self.assertEqual(len(p['after']),32)
            idx=int(p['id'].rsplit('.',1)[1]);value=p['after'].split(b'\0',1)[0]
            self.assertEqual(decode(value),gaps.DESTINATIONS[idx]);self.assertLessEqual(len(value),14)
            self.assertEqual(p['after'][len(value):],bytes(32-len(value)))
            out[p['offset']:p['offset']+32]=p['after'];allowed.update(range(p['offset'],p['offset']+32))
        self.assertTrue({i for i,(a,b) in enumerate(zip(self.raw,out)) if a!=b}<=allowed)
        for p in reversed(self.patches):out[p['offset']:p['offset']+32]=p['before']
        self.assertEqual(out,self.raw)
        self.assertEqual(self.locations['preserved_records'],21)
        self.assertEqual(len(self.locations['source_evidence']['forwarding_cases']),25)
        self.assertNotIn(0,gaps.DESTINATIONS);self.assertNotIn(1,gaps.DESTINATIONS)

    def test_unknown_destination_scope_source_and_charset_changes_refused(self):
        for mutate in ('translation','source','scope'):
            bad=copy.deepcopy(self.new['generic_destination_names'])
            if mutate=='translation':bad['entries'][0]['translation']='X'*33
            elif mutate=='source':bad['source_sha256']='0'*64
            else:bad['entries'][0]['index']=0
            with self.assertRaises(ValueError):gaps.compile_locations(self.elf,bad)
        elf=bytearray(self.elf);elf[0x10bf94]^=1
        with self.assertRaises(ValueError):gaps.title_proof(bytes(elf))

    def test_signed_lh_and_unsigned_sltu_harness_cover_original_instructions(self):
        from speaker_labels import _run
        for value in (0,1,32767,32768,65535):
            memory=bytearray(0xa0);struct.pack_into('<H',memory,0x9e,value)
            before=bytes(memory);regs=[0]*32;regs[16]=0x620000
            out=_run(self.elf,0x10bfc8,((0x10bfc8,0x10bfcc),),regs,[(0x620000,memory)],0x10bfcc)
            expected=value if value<32768 else value-65536
            self.assertEqual(out[3],expected&0xffffffff);self.assertEqual(bytes(memory),before)
        for value in (0,1,0x80000000,0xffffffff):
            regs=[0]*32;regs[2]=value
            out=_run(self.elf,0x10d658,((0x10d658,0x10d65c),),regs,[],0x10d65c)
            self.assertEqual(out[17],int(value!=0))

    def test_widths_use_original_envelope_and_title_never_grows(self):
        proof=gaps.width_proof(self.elf,self.raw)
        self.assertEqual(len(proof['destination_cases']),12)
        self.assertEqual(len(proof['title_cases']),6)
        self.assertTrue(all(r['within_original_envelope'] for r in proof['destination_cases']))
        self.assertTrue(all(r['not_wider'] for r in proof['title_cases']))

if __name__=='__main__':unittest.main()
