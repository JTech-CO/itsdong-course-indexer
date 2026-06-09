# itsdong-course-indexer

> **아이티동스쿨(itsdong.com)의 공개 강좌를 카테고리별로 모아 보고(웹·실시간) 스프레드시트로 정리하는 비공식 오픈소스 도구**

> ⚠️ **비공식 고지** — 본 프로젝트는 아이티동스쿨/(주)스마트동스쿨과 **무관한 비공식 도구**입니다.
> 저장소에는 **강좌 데이터가 포함되지 않으며**, 모든 콘텐츠는 실행/방문 시점에 공식 사이트에서
> 실시간으로 불러옵니다(저장 안 함). 라이선스(MIT)는 **코드에만** 적용되고, 수집 데이터의
> 공개 재배포는 저작권·데이터베이스권 등에 저촉될 수 있습니다. 전문은 **[NOTICE.md](NOTICE.md)** 참조.

## 1. 소개 (Introduction)

강좌가 매우 많아 일일이 찾기 어려운 아이티동스쿨을, **구분(프로그래밍·그래픽·컴퓨터일반·자격증)별로
정리해 공식 페이지로 바로 연결**해 주는 도구입니다. 강좌 영상 등 콘텐츠는 다루지 않고, 결과물은
**제목·분류와 공식 페이지로 가는 링크**입니다.

**주요 기능**
- **웹 링크 탐색기 (`docs/`)**: 방문자 브라우저에서 사이트를 **실시간 호출**하여 카테고리별 강좌/패키지를
  링크로 보여줍니다. **어떤 데이터도 저장하지 않습니다.**
- **정리 도구 (Python)**: 전체 강좌 목록·차시 목차·패키지 구성을 수집해 **Excel/CSV**로 만듭니다(개인용).

## 2. 기술 스택 (Tech Stack)

- **Frontend**: Vanilla JS · 단일 HTML(의존성 없음)
- **Data tooling**: Python 3, `requests`, `BeautifulSoup4`, `openpyxl`
- **Live fetch (CORS)**: 공개 프록시 자동 폴백 + (권장) 본인 **Cloudflare Worker** (`cors-proxy-worker.example.js`)
- **Deployment**: GitHub Pages (`/docs`)

## 3. 설치 및 실행 (Quick Start)

### A) 웹 링크 탐색기
- 배포본: **`https://jtech-co.github.io/itsdong-course-indexer/`** (Settings → Pages → `main` `/docs` 활성화 후)
- 로컬: `docs/index.html` 을 브라우저로 열면 됩니다.
- **실시간 목록 보기(선택)**: itsdong.com은 CORS를 허용하지 않아 브라우저 직접 호출이 막힙니다.
  안정적으로 보려면 `cors-proxy-worker.example.js` 를 Cloudflare Worker로 배포한 뒤,
  페이지의 **[⚙ 연결 설정]** 에 워커 주소(`https://…workers.dev/?url=`)를 입력하세요.
  설정하지 않으면 공개 프록시를 시도하고, 실패 시 **공식 페이지 링크로 대체**됩니다.

### B) 정리 도구 (Excel/CSV 생성)
**요구 사항**: Python 3.9 이상

1. **설치 (Install)**
   ```bash
   git clone https://github.com/JTech-CO/itsdong-course-indexer.git
   cd itsdong-course-indexer
   pip install -r requirements.txt
   ```
2. **환경 변수 (Environment, 선택)** — 정중한 크롤링을 위해 조절
   ```bash
   ITSDONG_DELAY=0.5     # 요청 간 최소 대기(초), 기본 0.3
   ITSDONG_WORKERS=2     # 동시 요청 수, 기본 4
   ```
3. **실행 (Run)**
   ```bash
   python run_all.py     # 1~4단계 일괄 → itsdong_강좌DB.xlsx 등 생성 (모두 .gitignore 대상)
   ```

## 4. 폴더 구조 (Structure)

```text
itsdong-course-indexer/
├── docs/
│   └── index.html       # 웹 링크 탐색기 (GitHub Pages, 데이터 미저장)
├── crawl_lib.py         # 공용 모듈: fetch/캐시/파서/라이브 택소노미
├── crawl_listings.py    # 1) 강좌·패키지 목록 수집
├── crawl_packages.py    # 2) 패키지 상세(포함 트랙)
├── crawl_lectures.py    # 3) 차시 목차(병렬·재개)
├── build_excel.py       # 4) Excel/CSV 생성
├── run_all.py           # 1~4 일괄 실행
├── cors-proxy-worker.example.js  # (선택) Cloudflare Worker 프록시
├── requirements.txt
├── .gitignore           # 모든 수집 데이터 제외 (코드만 공개)
├── LICENSE              # MIT (코드 한정)
└── NOTICE.md            # 면책·상표·책임있는 사용·삭제요청
```

## 5. 정보 (Info)

- **License**: MIT — **코드에만** 적용됩니다. 데이터/브랜드 권리는 (주)스마트동스쿨에 있습니다([NOTICE.md](NOTICE.md)).
- **Contact / 삭제 요청**: `jtech-bryan@proton.me`
- 공개 재배포 전에는 운영사 동의 또는 전문가(변호사) 검토를 권장합니다.
