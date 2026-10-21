# -*- coding: utf-8 -*-
"""Render reviewed source paragraphs and locally copied Mohamoa narration."""
import html,json,copy
from pathlib import Path
from bs4 import BeautifulSoup
ROOT=Path(__file__).resolve().parents[1]
esc=lambda v:html.escape(str(v),quote=True)
def frag(s):return BeautifulSoup(s,'html.parser')
def audio_markup(model,key,asset_base):
 audio=model.get('audio')
 if not audio:return ''
 text='<aside class="report-audio" aria-label="'+esc('모하모아 '+{'location':'생활권','types':'평면','cost':'비용','directions':'방문'}[key]+' 음성 안내')+'"><h2>음성으로 먼저 들어보세요</h2><p>모하모아 리포트 핵심 안내 · '+esc(audio['durationLabel'])+' · 한국어 남성 AI 음성</p><audio controls preload="none"><source src="'+asset_base+audio['aacSrc']+'" type="audio/mp4"><source src="'+asset_base+audio['src']+'" type="audio/mpeg">음성을 재생할 수 없습니다. 아래 대본을 읽어 주세요.</audio><details><summary>음성 안내 대본 보기</summary>'+''.join('<p>'+esc(p)+'</p>' for p in audio['paragraphs'])+'</details><p class="source-note"><a href="'+esc(model['report_url'])+'" target="_blank" rel="noopener">모하모아 원문과 음성 보기 ↗</a></p></aside>'
 return text
def augment(section,model,key,asset_base):
 container=section.select_one('.calc-inner') or section
 if model.get('audio'):section.select_one('.section-answer').insert_after(frag(audio_markup(model,key,asset_base)))
 body='<div class="expanded-reading" data-enrichment="20261022">'
 for d in model.get('details',[]):
  body+='<article class="reading-block"><h2>'+esc(d['title'])+'</h2>'+''.join('<p>'+esc(p)+'</p>' for p in d['paragraphs'])
  body+='<p class="source-note">자료 확인 '+esc(d['checked_at'])+' · '+' · '.join('<a href="https://hobansummit-kjcd.co.kr/'+esc(r)+'" target="_blank" rel="noopener">'+('모집공고' if '.pdf' in r else '공식 안내')+' ↗</a>' for r in d['refs'])+'</p></article>'
 body+='</div>';container.append(frag(body))
 if key=='premium':
  for n in [7,8]:
   container.append(frag('<figure class="official-image community-original"><a href="'+asset_base+'official-community-a'+str(n)+'.jpg" target="_blank" rel="noopener"><img src="'+asset_base+'official-community-a'+str(n)+'.jpg" alt="A'+str(n)+'블록 공식 커뮤니티 시설 구성도" loading="lazy"></a><figcaption>A'+str(n)+'블록 커뮤니티 시설 계획 · 이미지를 누르면 원본을 볼 수 있습니다.</figcaption></figure>'))
 if key=='cost':
  data=json.loads((ROOT/'concepts/source-data.json').read_text());exp={'84A':919,'84B':1204,'117A':1286,'117B':1286,'135':1415}
  from sale_content import table
  container.append(frag('<h2 class="reading-table-title">주택형·층별 공고 공급금액과 발코니 확장비</h2>'+table('2026.06.05 공고 · 단위 만원 · 확장비는 분양가와 별도',['블록·주택형']+[r['floor'] for r in data['units'][0]['prices']]+['발코니 확장'],[[u['block']+' '+u['id']]+[format(r['won']//10000,',') for r in u['prices']]+[format(exp[u['id']],',')] for u in data['units']])+'<p class="source-note">확장비 근거: <a href="https://hobansummit-kjcd.co.kr/images/gonggo7bl_01_v2.pdf#page=44">A7 공고44쪽</a> · <a href="https://hobansummit-kjcd.co.kr/images/gonggo8bl_01_v2.pdf#page=39">A8 공고39쪽</a>. 현재 잔여 세대의 견적표가 아닙니다.</p>'))
def replace_calculator(section,asset_base,audio_model):
 inner=section.select_one('.calc-inner')
 for child in list(inner.children):
  if getattr(child,'name',None) and not child.select_one('.section-answer') and 'section-answer' not in child.get('class',[]) and 'section-heading' not in child.get('class',[]):child.decompose()
 inner.append(frag(audio_markup(audio_model,'cost',asset_base)))
 markup=(ROOT/'concepts/vendor/mohamoa-cost/initial.html').read_text()
 inner.append(frag('<div id="mohamoa-calculator">'+markup+'</div><noscript><p>금액 계산과 탭 전환을 사용하려면 자바스크립트를 켜 주세요. 공식 가격표는 분양가 메뉴에서 읽을 수 있습니다.</p></noscript>'))
