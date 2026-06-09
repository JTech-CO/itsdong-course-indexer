# -*- coding: utf-8 -*-
"""2단계: 전체 단일강좌 상세(차시별 목차)를 크롤링 → lecture_details.json.

병렬 수집 + 중단 시 재개 지원. 생성물은 .gitignore 로 제외됩니다.
정중한 크롤링을 위해 동시 워커/요청간격을 환경변수로 조절하세요.
  ITSDONG_WORKERS (기본 4)   동시 요청 수
  ITSDONG_DELAY   (기본 0.3) 요청 간 최소 대기(초, crawl_lib에서 사용)
"""
import sys, os, json, time
try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass
from concurrent.futures import ThreadPoolExecutor, as_completed
from requests.adapters import HTTPAdapter
from crawl_lib import fetch, parse_lecture_detail, SESSION

WORKERS = int(os.environ.get('ITSDONG_WORKERS', '4'))
OUT = 'lecture_details.json'
SESSION.mount('https://', HTTPAdapter(pool_connections=WORKERS, pool_maxsize=WORKERS + 2))

ids = [l['id'] for l in json.load(open('listings.json', encoding='utf-8'))['lectures']]
results = {}
if os.path.exists(OUT):
    results = json.load(open(OUT, encoding='utf-8'))
    print('재개: 기존 %d개 로드' % len(results))
todo = [i for i in ids if i not in results]
print('총 %d강좌, 남은 %d개, 워커 %d\n' % (len(ids), len(todo), WORKERS))


def work(lid):
    html = fetch('lecture_detail.php?id=%s' % lid, cache_key='lec_%s' % lid, persist=False)
    d = parse_lecture_detail(html)
    return lid, {'title': d['title'], 'level': d['level'],
                 'lesson_count': d['lesson_count'], 'lessons': d['lessons']}


def save():
    tmp = OUT + '.tmp'
    json.dump(results, open(tmp, 'w', encoding='utf-8'), ensure_ascii=False)
    os.replace(tmp, OUT)


done, fails, t0 = 0, [], time.time()
with ThreadPoolExecutor(max_workers=WORKERS) as ex:
    futs = {ex.submit(work, lid): lid for lid in todo}
    for fut in as_completed(futs):
        lid = futs[fut]
        try:
            lid, rec = fut.result()
            results[lid] = rec
        except Exception as e:
            fails.append(lid)
            results[lid] = {'title': None, 'level': None, 'lesson_count': 0,
                            'lessons': [], 'error': str(e)[:120]}
        done += 1
        if done % 100 == 0 or done == len(todo):
            rate = done / max(time.time() - t0, 1)
            print('  %4d/%d  (%.1f/s, ETA %.0fs, 실패 %d)' % (
                done, len(todo), rate, (len(todo) - done) / max(rate, 0.1), len(fails)))
            save()

save()
tot = sum(r['lesson_count'] for r in results.values())
print('\n완료: 강좌 %d, 총 차시 %d, 실패 %d  →  %s' % (len(results), tot, len(fails), OUT))
