"""Build a no-server audit browser with individual and component reading modes."""
from pathlib import Path
import argparse, json
ROOT=Path(__file__).resolve().parents[1]


def build(report,output):
    data=json.loads(report.read_text(encoding='utf8'))
    assert len(data['records'])>=433
    page=ROOT/'skills/transcriptomics-figure-workbench/assets/studio/review-browser.html'
    result=page.read_text(encoding='utf8').replace('/*REVIEW_ROWS*/[]',json.dumps(data['records'],ensure_ascii=False).replace('<','\\u003c'))
    with output.open('x',encoding='utf8') as stream:stream.write(result)


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--report',required=True,type=Path);parser.add_argument('--output',required=True,type=Path);args=parser.parse_args();build(args.report,args.output)
