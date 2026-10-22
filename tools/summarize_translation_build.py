"""Export publishable metadata from a completed local batch, without game text."""
import argparse
import json
from pathlib import Path
from reinsertion import ROOT,local
from iso_retention import plan as retention_plan


def summarize(folder,tests_passed=None):
    folder=local(folder)
    report=json.loads((folder/'relatorio.json').read_text(encoding='utf-8'))
    document=json.loads((folder/'plano.json').read_text(encoding='utf-8'))
    draft=json.loads((folder/'rascunho.json').read_text(encoding='utf-8'))
    if not report['valid'] or 'iso' not in report:raise ValueError('Batch has no valid completed ISO build')
    iso=report['iso'];image=local(folder/iso.get('image_name',draft.get('iso_name','MetalSaga-ptbr-piloto-inicial-v001.iso')))
    if image.stat().st_size!=iso['iso_size']:raise ValueError('ISO size no longer matches build report')
    records=document['entries']
    return {'schema':1,'metadata_source':'completed build report; no new runtime validation',
        'draft_sources':report['draft_sources'],'source_sha256':report['source_sha256'],
        'reinsertion_policy':report['policy'],'named_choice_evidence':report.get('named_choice_evidence'),'b15_evidence':report.get('b15_evidence'),'numeric1_evidence':report.get('numeric1_evidence'),'numeric15_evidence':report.get('numeric15_evidence'),'t0_evidence':report.get('t0_evidence'),
        'scope':draft['scope'],'accepted':report['accepted'],'unchanged':report['unchanged'],
        'refused':report['refused'],'deferred':report['deferred'],'preservation_decisions':report.get('preservation_decisions',{}),
        'translated_segments':sum(s['translation']!=s['source'] for e in records for s in e['segments']),
        'ssd_groups':len({e['block_offset'] for e in records}),
        'terminology_issues':report['terminology_issues'],
        'terminology_policy_sha256':report.get('terminology_policy_sha256'),
        'source_iso_sha256':iso['source_iso_sha256'],'output_iso_sha256':iso['output_iso_sha256'],
        'iso_size':iso['iso_size'],'changed_byte_count':len(iso['changed_iso_offsets']),
        'all_bytes_match_expected_patch':iso['all_bytes_match_expected_patch'],
        'iso_directory_identical':iso['iso_directory_identical'],'fonts':iso['fonts'],
        'elf_profile':iso['elf_profile'],'layout_patch':iso.get('layout_patch'),'output_iso':image.relative_to(ROOT).as_posix(),
        'record_relocation':False,'modes':sorted({e['mode'] for e in records}),
        'unit_tests_passed_reported':tests_passed,
        'legacy_width_warnings':sum(bool(r.get('warnings')) for r in report['results']),
        'visual_status':report['visual_status'],'narrative_status':report['narrative_status'],
        'pcsx2_executed':False,'iso_retention':retention_plan(),
        'results':report['results']}


def main():
    parser=argparse.ArgumentParser(description='Exportar metadados próprios sem textos originais')
    parser.add_argument('--build-dir',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--tests-passed',type=int)
    args=parser.parse_args();output=args.output.resolve()
    if not any(output.is_relative_to(ROOT/d) for d in ('reports','work')) or output.exists():
        raise ValueError('Use a new output under reports/ or work/')
    if args.tests_passed is not None and args.tests_passed<0:raise ValueError('Invalid test count')
    result=summarize(args.build_dir,args.tests_passed)
    output.parent.mkdir(parents=True,exist_ok=True)
    with output.open('x',encoding='utf-8') as stream:json.dump(result,stream,ensure_ascii=False,indent=2);stream.write('\n')
    print(f"Registros: {result['scope']['records']}; traduzidos: {result['accepted']}; segmentos: {result['translated_segments']}")


if __name__=='__main__':main()
