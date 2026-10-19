"""Shared initial-HTML metadata and evidence-date contract for the ten pages."""
import html
import json
import re
from datetime import date
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def load_dates():
    values = json.loads((ROOT / 'concepts/page-dates.json').read_text())
    for value in [values['page_updated_at'], values['deployed_at'], *values['records'].values()]:
        if value is not None:
            date.fromisoformat(value)
    return values

def time_tag(value, kind):
    return '<time data-date-kind="'+kind+'" datetime="'+value+'">'+value.replace('-', '.')+'</time>'

def apply_contract(page, editorial, dates=None):
    dates = dates or load_dates()
    # Only labelled review dates change. Publication dates, prices and schedules are untouched.
    for original, value in dates['records'].items():
        page = re.sub(r'(확인일\s*)'+re.escape(original),
                      lambda m: m[1]+time_tag(value, 'record'), page)
    topic = editorial.get('h1_topic')
    if topic:
        page = re.sub(r'(<h1>)(.*?)(</h1>)',
                      lambda m: m[1]+m[2]+'<span class="h1-topic">'+html.escape(topic)+ '</span>'+m[3],
                      page, count=1, flags=re.S)
    canonical = editorial['url']
    hero = re.search(r'<img class="hero-image" src="[^"]*/assets/([^"/]+)"', page)
    image = canonical+'assets/'+hero[1] if hero else canonical+'branding/favicon-96.png'
    metadata = ('<link rel="canonical" href="'+html.escape(canonical, quote=True)+'">'
                '<meta property="og:url" content="'+html.escape(canonical, quote=True)+'">'
                '<meta property="og:image" content="'+image+'">'
                '<meta property="og:image:alt" content="호반써밋 첨단3지구 단지 투시도">')
    page = page.replace('</head>', metadata+'</head>', 1)
    dates_html = '<p class="page-dates">페이지 업데이트: '+time_tag(dates['page_updated_at'], 'updated')
    if dates['deployed_at']:
        dates_html += ' · 운영 배포일: '+time_tag(dates['deployed_at'], 'deployed')
    dates_html += '</p>'
    return page.replace('</footer>', dates_html+'</footer>', 1)

class Metadata(HTMLParser):
    def __init__(self):
        super().__init__()
        self.in_head = False
        self.items = {}
        self.h1 = 0
    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'head': self.in_head = True
        if tag == 'h1': self.h1 += 1
        key = None
        if tag == 'title': key = 'title'
        elif tag == 'meta': key = attrs.get('name', attrs.get('property'))
        elif tag == 'link' and attrs.get('rel') == 'canonical': key = 'canonical'
        if key:
            self.items.setdefault(key, []).append((self.in_head, attrs))
    def handle_endtag(self, tag):
        if tag == 'head': self.in_head = False

def verify_contract(page, editorial):
    p = Metadata(); p.feed(page)
    for key in ['title', 'description', 'robots', 'canonical', 'og:title', 'og:description', 'og:url', 'og:image']:
        assert len(p.items.get(key, [])) == 1, f'{key}: missing or duplicated'
        assert p.items[key][0][0], f'{key}: outside head'
    assert p.h1 == 1, 'H1: expected exactly one'
    description = p.items['description'][0][1]['content']
    assert description == editorial['description'] and 0 < len(description) <= 150
    assert description.endswith(('.', '!', '?')), 'description: incomplete sentence'
    assert p.items['canonical'][0][1]['href'] == editorial['url']
    assert p.items['og:url'][0][1]['content'] == editorial['url']
    assert p.items['og:title'][0][1]['content'] == editorial['title']
    assert p.items['og:description'][0][1]['content'] == description
    if editorial.get('h1_topic'):
        assert html.escape(editorial['h1_topic']) in re.search(r'<h1>(.*?)</h1>', page, re.S)[1]
    assert 'data-date-kind="updated"' in page
