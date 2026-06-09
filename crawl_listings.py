# -*- coding: utf-8 -*-
"""1단계: 카테고리별 리스팅을 크롤링하여 마스터 강좌/패키지 목록(listings.json) 생성.

생성물(listings.json)은 .gitignore 로 제외됩니다. 저장소에는 커밋하지 마세요.
"""
import sys, json
try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass
from crawl_lib import fetch, parse_listing, build_taxonomy, MAIN_NAME

tax = build_taxonomy(fetch)
sub_ids = list(tax.keys())
lectures, packages = {}, {}


def add(store, rec, main_id, main_name, sub_id, sub_name):
    cid = rec['id']
    if cid not in store:
        store[cid] = dict(rec)
        store[cid].update({'categories': [], 'main_id': main_id,
                           'main_name': main_name, 'sub_name': sub_name})
    r = store[cid]
    pair = (main_name, sub_name)
    if pair not in r['categories']:
        r['categories'].append(pair)
    for k in ('price', 'list_price', 'discount', 'period', 'instructor', 'title'):
        if not r.get(k) and rec.get(k):
            r[k] = rec[k]


for i, sid in enumerate(sub_ids, 1):
    info = tax[sid]
    html = fetch('lecture.php?category=%s' % sid, cache_key='cat_%s' % sid)
    lecs = parse_listing(html, 'lecture')
    pkgs = parse_listing(html, 'package')
    for r in lecs:
        add(lectures, r, info['main_id'], info['main_name'], sid, info['sub_name'])
    for r in pkgs:
        add(packages, r, info['main_id'], info['main_name'], sid, info['sub_name'])
    print('[%2d/%d] sub=%s %-26s lec=%3d pkg=%2d  (누적 lec=%d pkg=%d)' % (
        i, len(sub_ids), sid, info['sub_name'][:24], len(lecs), len(pkgs),
        len(lectures), len(packages)))

# 대분류 페이지로 소분류 미배정 강좌 보완
for mid in ['1', '2', '3', '4']:
    html = fetch('lecture.php?category=%s' % mid, cache_key='cat_%s' % mid)
    for r in parse_listing(html, 'lecture'):
        if r['id'] not in lectures:
            add(lectures, r, mid, MAIN_NAME[mid], mid, '(미분류)')
    for r in parse_listing(html, 'package'):
        if r['id'] not in packages:
            add(packages, r, mid, MAIN_NAME[mid], mid, '(미분류)')


def ser(store):
    out = []
    for r in store.values():
        d = dict(r)
        d['categories'] = [list(c) for c in r['categories']]
        d['cross_listed'] = len(r['categories']) > 1
        out.append(d)
    return out


json.dump({'lectures': ser(lectures), 'packages': ser(packages)},
          open('listings.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('\n완료: 단일강좌 %d, 패키지 %d  →  listings.json' % (len(lectures), len(packages)))
