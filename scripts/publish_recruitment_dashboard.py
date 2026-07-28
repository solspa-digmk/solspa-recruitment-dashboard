#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json
from pathlib import Path

ROOT = Path('/Users/giangvu/.hermes/repos/solspa-recruitment-dashboard')
DATA = ROOT / 'data'
TEMPLATE = ROOT / 'index_template.html'
OUT = ROOT / 'index.html'

def load(name):
    p = DATA / f'{name}.json'
    return json.loads(p.read_text(encoding='utf-8'))

branches = load('branches')
positions = load('positions')
stages = load('stages')
candidates = load('candidates')
demand = load('demand')
checklists = load('checklists')
activity = load('activity')

html = TEMPLATE.read_text(encoding='utf-8')
html = html.replace('__BRANCHES__', json.dumps(branches, ensure_ascii=False))
html = html.replace('__POSITIONS__', json.dumps(positions, ensure_ascii=False))
html = html.replace('__STAGES__', json.dumps(stages, ensure_ascii=False))
html = html.replace('__CANDIDATES__', json.dumps(candidates, ensure_ascii=False))
html = html.replace('__DEMAND__', json.dumps(demand, ensure_ascii=False))
html = html.replace('__CHECKLISTS__', json.dumps(checklists, ensure_ascii=False))
html = html.replace('__ACTIVITY__', json.dumps(activity, ensure_ascii=False))
html = html.replace('__TODAY__', __import__('datetime').date.today().isoformat())
OUT.write_text(html, encoding='utf-8')
print('PUBLISHED', OUT)
print('CANDIDATES', len(candidates), 'DEMAND', len(demand), 'ACTIVITY', len(activity))
