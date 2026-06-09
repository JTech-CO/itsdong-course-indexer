# -*- coding: utf-8 -*-
"""itsdong-course-indexer — 공용 모듈 (fetch / 캐시 / 파서 / 택소노미).

이 도구는 아이티동스쿨((주)스마트동스쿨)과 무관한 **비공식** 오픈소스 도구입니다.
저장소에는 어떤 수집 데이터도 포함하지 않으며, 카테고리 분류명 등 모든 콘텐츠는
실행 시점에 공개된 페이지에서 직접 가져옵니다. 자세한 내용은 NOTICE.md 참고.
"""
import sys, os, re, time, hashlib
try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass
import requests
from bs4 import BeautifulSoup

# ---- 설정 (환경변수로 재정의 가능) ----
BASE = os.environ.get('ITSDONG_BASE', 'https://www.itsdong.com/it/')
USER_AGENT = os.environ.get(
    'ITSDONG_UA',
    'itsdong-course-indexer/1.0 (+https://github.com/) open-source respectful crawler')
REQUEST_DELAY = float(os.environ.get('ITSDONG_DELAY', '0.3'))   # 요청 간 최소 대기(초)
TIMEOUT = int(os.environ.get('ITSDONG_TIMEOUT', '30'))
CACHE = os.environ.get('ITSDONG_CACHE',
                       os.path.join(os.path.dirname(os.path.abspath(__file__)), '_cache'))
os.makedirs(CACHE, exist_ok=True)

SESSION = requests.Session()
SESSION.headers.update({'User-Agent': USER_AGENT, 'Accept-Language': 'ko-KR,ko;q=0.9'})

# ---- 사이트 메뉴 구조(소분류 → 대분류) : ID(정수)만 담은 구조적 상수 ----
# 사람이 읽을 수 있는 분류명/강좌 데이터는 저장하지 않고 실행 시 라이브로 가져옵니다.
# 사이트 메뉴가 개편되면 index.php 의 lecture.php?category=N 링크 구성을 보고 갱신하세요.
PARENT_GROUPS = {
    '1': ['10', '11', '12', '13', '14', '15', '19', '16', '17', '18'],
    '2': ['20', '21', '22', '23', '24', '26', '27', '29', '28', '25'],
    '3': ['30', '31', '34', '32', '33', '35', '36'],
    '4': ['40', '45', '43', '41', '421', '44', '46', '47', '49',
          '422', '423', '424', '425', '427', '428', '426', '429', '48'],
}
# 대분류명 폴백(라이브 조회 실패 시에만 사용)
MAIN_NAME = {'1': '프로그래밍', '2': '그래픽', '3': '컴퓨터일반', '4': '자격증'}


def clean(s):
    return re.sub(r'\s+', ' ', s or '').strip()


def fetch(url, cache_key=None, retries=3, pause=None, persist=True):
    """GET (옵션) 디스크 캐시. persist=False 면 메모리로만 반환(대량 크롤 시 디스크 절약).
    캐시 파일은 모두 _cache/ 아래에 생기며 .gitignore 로 제외됩니다."""
    if pause is None:
        pause = REQUEST_DELAY
    if not url.startswith('http'):
        url = BASE + url
    if cache_key is None:
        cache_key = hashlib.md5(url.encode()).hexdigest()
    path = os.path.join(CACHE, cache_key + '.html')
    if os.path.exists(path):
        return open(path, encoding='utf-8').read()
    last = None
    for attempt in range(retries):
        try:
            r = SESSION.get(url, timeout=TIMEOUT)
            r.encoding = 'utf-8'
            if r.status_code == 200 and len(r.text) > 500:
                if persist:
                    open(path, 'w', encoding='utf-8').write(r.text)
                time.sleep(pause)
                return r.text
            last = 'HTTP %s len %s' % (r.status_code, len(r.text))
        except Exception as e:
            last = repr(e)
        time.sleep(0.6 * (attempt + 1))
    raise RuntimeError('fetch failed %s: %s' % (url, last))


def build_taxonomy(fetch_fn=None):
    """메뉴 페이지에서 카테고리명을 **라이브로** 가져와 택소노미 구성.
    returns dict: sub_id -> {'main_id','main_name','sub_name'}"""
    fetch_fn = fetch_fn or fetch
    html = fetch_fn('index.php', cache_key='_menu', persist=True)
    soup = BeautifulSoup(html, 'lxml')
    names = {}
    for a in soup.find_all('a', href=re.compile(r'lecture\.php\?category=\d+')):
        m = re.search(r'category=(\d+)', a['href'])
        cid = m.group(1)
        nm = clean(a.get_text(' ', strip=True))
        if nm and cid not in names:
            names[cid] = nm
    tax = {}
    for main_id, subs in PARENT_GROUPS.items():
        main_name = names.get(main_id) or MAIN_NAME.get(main_id, main_id)
        for sid in subs:
            tax[sid] = {'main_id': main_id, 'main_name': main_name,
                        'sub_name': names.get(sid, sid)}
    return tax


# ---------------- 리스팅 파서 ----------------
def parse_listing(html, kind):
    """kind in {'lecture','package'}. 콘텐츠 행만 반환(메뉴 배너 &f= 링크 제외)."""
    soup = BeautifulSoup(html, 'lxml')
    rows = []
    for a in soup.find_all('a', href=True):
        m = re.search(kind + r'_detail\.php\?id=(\d+)(&f=[a-z_0-9]+)?$', a['href'])
        if not m or m.group(2):
            continue
        txt = clean(a.get_text(' ', strip=True))
        if not txt or txt == '자세히보기':
            continue
        cid = m.group(1)
        tr = a.find_parent('tr')
        rowtext = clean(tr.get_text(' ', strip=True)) if tr else txt
        prices = re.findall(r'([\d,]+)\s*원', rowtext)
        period_m = re.search(r'(\d+\s*일|무제한|평생)', rowtext)
        inst_m = re.search(r'강사\s*[:：]\s*([가-힣A-Za-z·.\s]{1,20}?)(?:\s*\d|\s*\||$)', rowtext)
        disc_m = re.search(r'\((\d+)%\s*할인', rowtext)
        rows.append({
            'id': cid, 'title': txt,
            'price': (prices[0] + '원') if prices else None,
            'list_price': (prices[1] + '원') if len(prices) > 1 else None,
            'discount': (disc_m.group(1) + '%') if disc_m else None,
            'period': period_m.group(1).replace(' ', '') if period_m else None,
            'instructor': clean(inst_m.group(1)) if inst_m else None,
        })
    best = {}
    for r in rows:
        if r['id'] not in best or len(r['title']) > len(best[r['id']]['title']):
            best[r['id']] = r
    return list(best.values())


# ---------------- 상세 파서 ----------------
def _og(soup, prop):
    m = soup.find('meta', property=prop)
    return m.get('content').strip() if m and m.get('content') else None


def strip_brand(title):
    if not title:
        return title
    return clean(re.sub(r'\s*아이티동스쿨.*$', '', title))


_TIME_RE = re.compile(r'(\d{1,2}\s*:\s*\d{2})')
_GANG_RE = re.compile(r'(\d{1,3})\s*강[\s.]+(.+?)\s+(\d{1,2}\s*:\s*\d{2})(?=\s|<|$)')


def _curriculum_from_table(soup):
    """'차시 | 강의 내용 | 시간' 헤더 테이블을 찾아 모든 차시 행 추출."""
    lessons = []
    for header_td in soup.find_all('td'):
        if clean(header_td.get_text()) != '차시':
            continue
        table = header_td.find_parent('table')
        if not table:
            continue
        for tr in table.find_all('tr'):
            tds = tr.find_all('td', recursive=False)
            if len(tds) < 3:
                continue
            no_txt = clean(tds[0].get_text())
            if not no_txt.isdigit():
                continue
            title = clean(tds[1].get_text(' ', strip=True))
            tcell = clean(tds[2].get_text())
            tm = _TIME_RE.search(tcell)
            tm = tm.group(1).replace(' ', '') if tm else None
            if title and len(title) < 250:
                lessons.append({'no': int(no_txt), 'title': title, 'time': tm})
        if lessons:
            return lessons
    return lessons


def parse_curriculum(html):
    """차시 테이블 우선 파싱(시간 없는 행 포함), 실패 시 'N강 …MM:SS' 폴백."""
    soup = BeautifulSoup(html, 'lxml')
    lessons = _curriculum_from_table(soup)
    if not lessons:
        text = soup.get_text('\n', strip=True)
        for m in _GANG_RE.finditer(text):
            title = clean(m.group(2))
            if title and len(title) < 250 and not title.startswith('강'):
                lessons.append({'no': int(m.group(1)), 'title': title,
                                'time': m.group(3).replace(' ', '')})
    seen = set(); uniq = []
    for l in lessons:
        key = (l['no'], l['title'])
        if key in seen:
            continue
        seen.add(key); uniq.append(l)
    return uniq


def _extract_level(desc):
    if not desc:
        return None
    m = re.search(r'학습난이도\s*[\n:：]?\s*([가-힣A-Za-z/]+)', desc)
    return clean(m.group(1)) if m else None


def parse_lecture_detail(html):
    soup = BeautifulSoup(html, 'lxml')
    title = strip_brand(_og(soup, 'og:title'))
    desc = _og(soup, 'og:description')
    lessons = parse_curriculum(html)
    return {'title': title, 'desc': desc, 'level': _extract_level(desc),
            'lessons': lessons, 'lesson_count': len(lessons)}


def parse_package_detail(html):
    soup = BeautifulSoup(html, 'lxml')
    title = strip_brand(_og(soup, 'og:title'))
    desc = _og(soup, 'og:description')
    inner = []
    seen = set()
    for a in soup.find_all('a', href=True):
        m = re.search(r'lecture_detail\.php\?id=(\d+)(&f=[a-z_0-9]+)?$', a['href'])
        if not m or m.group(2):
            continue
        lid = m.group(1)
        if lid in seen:
            continue
        seen.add(lid)
        t = clean(a.get_text(' ', strip=True))
        if t and t != '자세히보기':
            inner.append({'id': lid, 'title': t})
    lessons = parse_curriculum(html)
    return {'title': title, 'desc': desc, 'tracks': inner,
            'track_count': len(inner), 'lesson_count': len(lessons)}
