# -*- coding: utf-8 -*-
"""1~4단계 파이프라인을 순서대로 실행합니다.

  python run_all.py

각 단계는 이전 단계의 산출물(JSON)을 입력으로 사용합니다.
중간에 실패하면 그 지점에서 멈춥니다. 차시 수집(3단계)은 재실행 시 이어서 진행됩니다.
"""
import sys, subprocess

STEPS = [
    ('1/4  강좌·패키지 목록', 'crawl_listings.py'),
    ('2/4  패키지 상세',     'crawl_packages.py'),
    ('3/4  차시 목차',       'crawl_lectures.py'),
    ('4/4  Excel/CSV 생성',  'build_excel.py'),
]

for label, script in STEPS:
    print('\n' + '=' * 60)
    print('▶ %s  (%s)' % (label, script))
    print('=' * 60)
    rc = subprocess.run([sys.executable, script]).returncode
    if rc != 0:
        print('\n[중단] %s 실패 (exit %d)' % (script, rc))
        sys.exit(rc)

print('\n완료. 생성된 Excel/CSV는 개인 참고용으로만 사용하세요 (NOTICE.md 참조).')
