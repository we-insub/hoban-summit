# -*- coding: utf-8 -*-
"""빌드된 한 번호의 모든 페이지를 읽는 순서대로 출력한다(검수용). python3 scripts/page_text.py NN [slug]"""
import re,sys
from pathlib import Path
from bs4 import BeautifulSoup
ROOT=Path(__file__).resolve().parents[1]
SLUGS=['','overview','location','premium','site-plan','floorplan','price','calculator','visit','pyeong-converter','subscription-score','loan-calculator']
def show(n,s):
    p=ROOT/'dist/hoban'/n/(s+'/' if s else '')/'index.html'
    d=BeautifulSoup(p.read_text(encoding='utf-8'),'html.parser')
    print('='*70);print(f'[{n}] /{s}/  title: {d.title.text}');print('description:',d.select_one('meta[name=description]')['content']);print('H1:',d.h1.get_text(strip=True))
    for t in d(['script','style','noscript','svg']):t.decompose()
    for t in d.select('.reservation-modal,.visit-bottom-bar,header.site-header,.desktop-nav,#mobile-menu,footer,#mohamoa-calculator,.report-audio details'):t.decompose()
    m=d.select_one('main')
    for el in m.select('h2,h3,p,li,summary,dt,dd,th,td,figcaption'):
        t=re.sub(r'\s+',' ',el.get_text(' ')).strip()
        if t:print(('## ' if el.name in('h2','h3') else '  ')+t)
if __name__=='__main__':
    n=sys.argv[1]
    for s in ([sys.argv[2]] if len(sys.argv)>2 else SLUGS):show(n,s)
