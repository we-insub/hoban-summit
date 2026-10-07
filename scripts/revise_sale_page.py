#!/usr/bin/env python3
"""Apply one authored sale-page brief. Build and verify it before moving on."""
import json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
brief=json.load(sys.stdin)
ident=brief['id']
plan_path=ROOT/'concepts/version-plan.json'
plan=json.loads(plan_path.read_text())
profile=next(p for p in plan['versions'] if p['id']==ident)
profile['question'],profile['answer']=brief['question'],brief['answer']
profile['editorial_brief']=f'editorial/{ident}.json'
profile['content_checked_at']='2026-10-07'
plan_path.write_text(json.dumps(plan,ensure_ascii=False,indent=2)+'\n')
(ROOT/f'concepts/editorial/{ident}.json').write_text(json.dumps(brief,ensure_ascii=False,indent=2)+'\n')
print(f'{ident}: authored brief and version plan updated')
