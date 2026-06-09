# itsdong-course-indexer

> **아이티동스쿨(itsdong.com)의 강좌 카테고리를 한눈에 모아 공식 페이지로 바로 연결하고, 필요하면 전체 목록을 스프레드시트로 정리하는 비공식 오픈소스 도구**

> ⚠️ **비공식 고지** — 본 프로젝트는 아이티동스쿨/(주)스마트동스쿨과 **무관한 비공식 도구**입니다.
> 저장소에는 **강좌 카탈로그 데이터(제목·목차·가격 등)가 포함되지 않습니다.** 웹 런처는 카테고리 메뉴만
> 담아 공식 페이지로 연결하고, 파이썬 도구의 결과물은 `.gitignore`로 제외됩니다. 라이선스(MIT)는
> **코드에만** 적용되며, 수집 데이터의 공개 재배포는 저작권·DB권 등에 저촉될 수 있습니다.
> 전문은 **[NOTICE.md](NOTICE.md)** 참조.

## 1. 소개 (Introduction)

강좌가 매우 많아 일일이 찾기 어려운 아이티동스쿨을, **구분(프로그래밍·그래픽·컴퓨터일반·자격증)별로
정리**해 빠르게 탐색하도록 돕는 도구입니다. 두 부분으로 구성됩니다.

**주요 기능**
- **웹 링크 런처 (`docs/`)**: 카테고리를 **엑셀 창 형태**로 보여주고, 클릭하면 **공식 페이지로 바로 이동**합니다.
  서버·프록시 없이 동작하는 순수 정적 페이지이며, **강좌 데이터를 저장하지 않습니다.**
- **정리 도구 (Python)**: 필요 시 전체 강좌 목록·차시 목차·패키지 구성을 수집해 **Excel/CSV**로 만듭니다(개인용).

## 2. 기술 스택 (Tech Stack)

- **Frontend**: Vanilla JS · 단일 HTML (의존성·빌드 없음)
- **Data tooling**: Python 3, `requests`, `BeautifulSoup4`, `openpyxl`
- **Deployment**: GitHub Pages (`/docs`)

## 3. 설치 및 실행 (Quick Start)

### A) 웹 링크 런처
- 배포본: **`https://jtech-co.github.io/itsdong-course-indexer/`**
  (Settings → Pages → `main` `/docs` 활성화 후)
- 로컬: `docs/index.html` 을 브라우저로 열면 됩니다.
- 별도 설정이 없습니다. 시트 탭(대분류)에서 소분류 셀을 클릭하면 itsdong.com 공식 페이지가 새 탭으로 열립니다.

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
│   ├── index.html       # 웹 링크 런처 (엑셀 창 스타일, GitHub Pages)
│   └── .nojekyll
├── crawl_lib.py         # 공용 모듈: fetch/캐시/파서/라이브 택소노미
├── crawl_listings.py    # 1) 강좌·패키지 목록 수집
├── crawl_packages.py    # 2) 패키지 상세(포함 트랙)
├── crawl_lectures.py    # 3) 차시 목차(병렬·재개)
├── build_excel.py       # 4) Excel/CSV 생성
├── run_all.py           # 1~4 일괄 실행
├── requirements.txt
├── .gitignore           # 모든 수집 데이터 제외 (코드만 공개)
├── LICENSE              # MIT (코드 한정)
└── NOTICE.md            # 면책·상표·책임있는 사용·삭제요청
```

## 5. 정보 (Info)

- **License**: MIT — **코드에만** 적용됩니다. 데이터/브랜드 권리는 (주)스마트동스쿨에 있습니다([NOTICE.md](NOTICE.md)).
- **Contact / 삭제 요청**: `jtech-bryan@proton.me`
- 공개 재배포 전에는 운영사 동의 또는 전문가(변호사) 검토를 권장합니다.
