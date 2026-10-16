"""Unified scientific figure catalog, preflight, render, restyle, Studio and review."""
import argparse
import copy
import json
import os
from pathlib import Path
from figure_workbench.contracts import read_json,write_new,make_plan,validate_spec
from figure_workbench.registry import read_registry,resolve,digest


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    commands=parser.add_subparsers(dest='command',required=True)
    catalog=commands.add_parser('catalog');catalog.add_argument('--search',default='')
    describe=commands.add_parser('describe');describe.add_argument('renderer')
    methods=commands.add_parser('methods');methods.add_argument('--search',default='')
    method=commands.add_parser('method');method.add_argument('entry')
    forms=commands.add_parser('forms');forms.add_argument('--search',default='')
    form=commands.add_parser('form');form.add_argument('entry')
    lp=commands.add_parser('layout-plan');lp.add_argument('--request',required=True,type=Path);lp.add_argument('--output',required=True,type=Path)
    le=commands.add_parser('layout-export');le.add_argument('--plan',required=True,type=Path);le.add_argument('--output',required=True,type=Path)
    design=commands.add_parser('design');design.add_argument('--brief',required=True,type=Path);design.add_argument('--output',required=True,type=Path)
    method_spec=commands.add_parser('method-spec');method_spec.add_argument('--entry',required=True)
    method_spec.add_argument('--template',required=True,type=Path);method_spec.add_argument('--output',required=True,type=Path)
    plan=commands.add_parser('plan');plan.add_argument('--spec',required=True,type=Path);plan.add_argument('--output',required=True,type=Path)
    render=commands.add_parser('render');source=render.add_mutually_exclusive_group(required=True)
    source.add_argument('--spec',type=Path);source.add_argument('--plan',type=Path);render.add_argument('--output',required=True,type=Path)
    migrate=commands.add_parser('migrate');migrate.add_argument('--input',required=True,type=Path)
    for name in ['style','meta','theme','output']:migrate.add_argument('--'+name,required=True,type=Path)
    migrate.add_argument('--id',required=True)
    restyle=commands.add_parser('restyle');restyle.add_argument('--spec',required=True,type=Path)
    restyle.add_argument('--appearance',required=True,type=Path);restyle.add_argument('--id',required=True);restyle.add_argument('--output',required=True,type=Path)
    review=commands.add_parser('review');review.add_argument('--bundle',required=True,type=Path)
    review.add_argument('--record',type=Path);review.add_argument('--decision',choices=['accepted','changes_requested'])
    review.add_argument('--checks',type=Path);review.add_argument('--notes');review.add_argument('--output',type=Path)
    review.add_argument('--inspection',type=Path)
    studio=commands.add_parser('studio');studio.add_argument('--output',required=True,type=Path)
    studio.add_argument('--gallery',type=Path);studio.add_argument('--demo-svg',type=Path)
    reading=commands.add_parser('reading-plan');reading.add_argument('--index',required=True,type=Path);reading.add_argument('--root',required=True,type=Path);reading.add_argument('--output',required=True,type=Path)
    reading.add_argument('--width-mm',type=float,default=178.);reading.add_argument('--minimum-text-pt',type=float,default=7.5);reading.add_argument('--volume-size',type=int,default=75)
    reading_export=commands.add_parser('reading-export');reading_export.add_argument('--plan',required=True,type=Path);reading_export.add_argument('--output',required=True,type=Path)
    args=parser.parse_args()
    if args.command=='catalog':
        registry=read_registry();query=args.search.casefold()
        result={'counts':registry['counts'],'renderers':[r for r in registry['renderers'] if query in json.dumps(r,ensure_ascii=False).casefold()],
                'runtime_validation':'separate receipts required','plotting_dependencies_loaded':False}
    elif args.command=='describe':result=resolve(args.renderer)
    elif args.command=='methods':
        from figure_workbench.methods import catalog_methods
        result={'entries':catalog_methods(args.search),'native_packages_executed':False}
    elif args.command=='method':
        from figure_workbench.methods import method_entry
        result=method_entry(args.entry)
    elif args.command=='forms':
        from figure_workbench.forms import catalog_forms
        result=catalog_forms(args.search)
    elif args.command=='form':
        from figure_workbench.forms import form_entry
        result=form_entry(args.entry)
    elif args.command=='layout-plan':
        from figure_workbench.layout import make_layout
        result=make_layout(read_json(args.request),args.request.resolve().parent);write_new(args.output,result)
        result={'status':result['status'],'panels':result['panel_count'],'pages':len(result['pages']),'analysis_performed':False}
    elif args.command=='layout-export':
        from figure_workbench.layout import export_layout
        result=export_layout(read_json(args.plan),args.output,args.plan.resolve().parent)
        result={'status':result['status'],'files':list(result['files']),'analysis_performed':False,'visual_acceptance':False}
    elif args.command=='method-spec':
        from figure_workbench.methods import prepare_method_spec
        spec=prepare_method_spec(args.entry,read_json(args.template),args.template.resolve().parent,args.output)
        write_new(args.output,spec);result={'status':'METHOD_SPEC_PREPARED','entry':args.entry,'output':str(args.output),'native_package_executed':False}
    elif args.command=='design':
        from figure_workbench.design import design_plan
        result=design_plan(read_json(args.brief),args.brief.resolve().parent)
        write_new(args.output,result)
        result={'status':result['state'],'preferred':result['preferred'],'output':str(args.output),'inference_performed':False}
    elif args.command=='plan':
        result=make_plan(read_json(args.spec),args.spec.resolve().parent);write_new(args.output,result)
        result={'status':'PREFLIGHT_ONLY','rows':result['rows'],'renderer':result['renderer'],'output':str(args.output)}
    elif args.command=='render':
        from figure_workbench.pipeline import render_plan
        selected=read_json(args.plan) if args.plan else make_plan(read_json(args.spec),args.spec.resolve().parent)
        result=render_plan(selected,args.output)
    elif args.command=='restyle':
        from figure_workbench.pipeline import restyle_spec
        spec=read_json(args.spec);appearance=read_json(args.appearance)
        # Keep a relative source binding meaningful when saving the replacement elsewhere.
        original=Path(spec['input']['path'])
        if not original.is_absolute():spec['input']['path']=os.path.relpath(args.spec.resolve().parent/original,args.output.resolve().parent)
        result=restyle_spec(spec,appearance,args.id);write_new(args.output,result)
        result={'status':'RESTYLE_SPEC_PREPARED','data_and_analysis_parameters_preserved':True,'output':str(args.output)}
    elif args.command=='migrate':
        style,meta,theme=map(read_json,[args.style,args.meta,args.theme])
        key=style.get('adapter') or (style.get('module','')+'.'+style.get('function',''))
        row=resolve(key)
        if any(k in style and style[k]!=row[k] for k in ['module','function']):raise ValueError('Saved style identifies a different renderer')
        from figure_workbench.contracts import META_FIELDS
        if meta.get('input_hash') and meta['input_hash']!=digest(args.input):raise ValueError('Saved metadata does not match selected input')
        spec={'schema_version':1,'figure_id':args.id,'renderer':key,
              'input':{'path':os.path.relpath(args.input.resolve(),args.output.resolve().parent),'sha256':digest(args.input)},
              'parameters':style.get('params',{}),'theme':theme,'provenance':{k:meta[k] for k in META_FIELDS},
              'appearance':{'preset':'paper'}}
        validate_spec(spec);write_new(args.output,spec)
        result={'status':'LEGACY_INPUTS_MIGRATED','output':str(args.output),'original_files_modified':False}
    elif args.command=='review':
        from figure_workbench.review import inspect_bundle,record_visual,verify_visual
        if args.record:result=verify_visual(args.bundle,read_json(args.record))
        elif args.decision:
            if not args.checks or not args.output or not args.notes:parser.error('A decision needs --checks, --notes and --output')
            result=record_visual(args.bundle,args.decision,read_json(args.checks),args.notes,args.output,read_json(args.inspection) if args.inspection else None)
        else:result=inspect_bundle(args.bundle)
    elif args.command=='reading-plan':
        from figure_workbench.reading import make_reading_plan
        result=make_reading_plan(args.index,args.root,args.width_mm,args.minimum_text_pt,args.volume_size);write_new(args.output,result)
        result={'status':'READING_PLAN_ONLY','figures':len(result['records']),'scientific_analysis':False}
    elif args.command=='reading-export':
        from figure_workbench.reading import export_reading
        result=export_reading(read_json(args.plan),args.output)
        result={'status':result['state'],'figures':result['figures'],'volumes':len(result['volumes']),'scientific_analysis':False}
    else:
        from figure_workbench.studio import build_studio
        result=build_studio(args.output,args.gallery,args.demo_svg)
    print(json.dumps(result,ensure_ascii=False,allow_nan=False))


if __name__=='__main__':main()
