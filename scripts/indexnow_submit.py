#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Submit 01-10 URLs to IndexNow (Bing, Naver) only when the live site matches the latest local build.

Default is a dry run that only reports the comparison. Add --submit to send.
Google does not support IndexNow: resubmit the sitemap in Search Console instead.
"""
import argparse
import json
import re
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / 'concepts'
LOG = BASE / 'indexnow-log.jsonl'
ENDPOINTS = {
 'bing': 'https://www.bing.com/indexnow',
 'naver': 'https://searchadvisor.naver.com/indexnow',
}
UA = 'Mozilla/5.0 (compatible; mohamoa-indexnow-check/1.0)'

parser = argparse.ArgumentParser()
parser.add_argument('--version', choices=[str(n).zfill(2) for n in range(1, 11)])
parser.add_argument('--submit', action='store_true', help='actually send to Bing and Naver when every check passes')
args = parser.parse_args()
KEY = json.loads((BASE / 'indexnow.json').read_text())['key']


def fetch(url):
 req = urllib.request.Request(url, headers={'User-Agent': UA})
 try:
  with urllib.request.urlopen(req, timeout=20) as res:
   return res.status, dict(res.headers), res.read().decode('utf-8', 'replace')
 except urllib.error.HTTPError as e:
  return e.code, dict(e.headers), ''
 except Exception as e:
  return 0, {}, str(e)


def signature(page):
 """Fields that must match between live and local: title, H1, canonical, robots meta."""
 find = lambda pattern: (re.search(pattern, page, re.S | re.I) or [None, ''])[1].strip()
 return {
  'title': find(r'<title>(.*?)</title>'),
  'h1': re.sub(r'<[^>]+>', '', find(r'<h1[^>]*>(.*?)</h1>')).strip(),
  'canonical': find(r'<link[^>]*href="([^"]+)"[^>]*rel="canonical"') or find(r'<link[^>]*rel="canonical"[^>]*href="([^"]+)"'),
  'robots': find(r'<meta[^>]*content="([^"]+)"[^>]*name="robots"') or find(r'<meta[^>]*name="robots"[^>]*content="([^"]+)"'),
 }


def local_file(folder, url):
 path = urlparse(url).path.strip('/')
 return folder / path / 'index.html' if path else folder / 'index.html'


def check_version(ident):
 folder = ROOT / 'dist' / 'hoban' / ident
 urls = [e.text for e in ET.parse(folder / 'sitemap.xml').findall('.//{*}loc')]
 host = urlparse(urls[0]).netloc
 problems = []
 if 'noindex' in (folder / '_headers').read_text().lower():
  problems.append('local build is still noindex (_headers): not a release build')
 status, _, body = fetch(f'https://{host}/{KEY}.txt')
 if status != 200 or body.strip() != KEY:
  problems.append(f'key file not served on live host (HTTP {status})')
 for url in urls:
  local = signature(local_file(folder, url).read_text())
  status, headers, live_html = fetch(url)
  if status != 200:
   problems.append(f'{url}: live HTTP {status}')
   continue
  if 'noindex' in ' '.join(v for k, v in headers.items() if k.lower() == 'x-robots-tag').lower():
   problems.append(f'{url}: live X-Robots-Tag noindex')
  live = signature(live_html)
  if 'noindex' in live['robots'].lower():
   problems.append(f'{url}: live robots meta noindex')
  diff = [k for k in local if local[k] != live[k]]
  if diff:
   problems.append(f'{url}: live differs from latest build in {", ".join(diff)}')
 return host, urls, problems


def submit(host, urls):
 payload = json.dumps({'host': host, 'key': KEY, 'keyLocation': f'https://{host}/{KEY}.txt', 'urlList': urls}).encode()
 results = {}
 for name, endpoint in ENDPOINTS.items():
  req = urllib.request.Request(endpoint, data=payload, headers={'Content-Type': 'application/json; charset=utf-8', 'User-Agent': UA})
  try:
   with urllib.request.urlopen(req, timeout=20) as res:
    results[name] = res.status
  except urllib.error.HTTPError as e:
   results[name] = e.code
  except Exception as e:
   results[name] = str(e)
 return results


plan = json.loads((BASE / 'version-plan.json').read_text())
versions = [v['id'] for v in (plan['versions'] if isinstance(plan, dict) else plan)]
for ident in versions:
 if args.version and ident != args.version:
  continue
 host, urls, problems = check_version(ident)
 record = {'checked_at': datetime.now(timezone.utc).isoformat(timespec='seconds'), 'version': ident, 'host': host, 'urls': len(urls), 'problems': problems}
 if problems:
  print(f'{ident} {host}: SKIP, live is not the latest release build')
  for p in problems[:6]:
   print('   - ' + p)
  if len(problems) > 6:
   print(f'   - ... {len(problems) - 6} more')
 elif args.submit:
  record['submitted'] = submit(host, urls)
  print(f'{ident} {host}: submitted {len(urls)} URLs -> {record["submitted"]}')
 else:
  print(f'{ident} {host}: ready, {len(urls)} URLs match (dry run, add --submit to send)')
 with LOG.open('a') as f:
  f.write(json.dumps(record, ensure_ascii=False) + '\n')
print('Google: IndexNow unsupported. After deploy, resubmit sitemap.xml in Search Console for each domain.')
