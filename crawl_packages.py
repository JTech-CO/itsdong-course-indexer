# -*- coding: utf-8 -*-
"""Phase 2a: 패키지 상세 크롤링 (포함 트랙 + 목차)."""
import sys, json
sys.stdout.reconfigure(encoding='utf-8')
from crawl_lib import fetch, parse_package_detail

d = json.load(open('listings.json', encoding='utf-8'))
packages = d['packages']
details = {}
for i, p in enumerate(packages, 1):
    pid = p['id']
    html = fetch('package_detail.php?id=%s' % pid, cache_key='pkg_%s' % pid)
    det = parse_package_detail(html)
    details[pid] = det
    print('[%2d/%d] pkg id=%-4s tracks=%2d lessons=%3d  %s' % (
        i, len(packages), pid, det['track_count'], det['lesson_count'],
        (det['title'] or p['title'])[:40]))

json.dump(details, open('package_details.json', 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1)
print('\npackage_details.json 저장 (%d개)' % len(details))
