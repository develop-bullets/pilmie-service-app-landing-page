# pilmie.com — Pilmie 랜딩 페이지

[Pilmie](https://pilmie.com) (독서 기록 · 리뷰 커뮤니티 앱)의 랜딩 페이지 및 정책 문서 호스팅.

- **배포**: GitHub Pages (레거시 빌드, `master` 브랜치 → 자동 재배포). Actions 워크플로 없음.
- **도메인**: `pilmie.com` (`CNAME`)
- **구성**: Jekyll + `jekyll-seo-tag` + `jekyll-sitemap`. **JS 0줄 · 제3자 요청 0건 · 애널리틱스 없음.**

## ⚠️ `_pages/*.md`는 생성물이다 — 여기서 고치지 말 것

개인정보처리방침·이용약관 6개 파일

```
_pages/{privacy,privacy-en,privacy-ja,terms,terms-en,terms-ja}.md
```

은 **앱 repo가 원본(source of truth)** 이며, 스크립트로 생성된다.

```bash
# 앱 repo에서
vi docs/legal/privacy-policy.ko.md                  # ① 국문 정본부터 수정
./docs/legal/sync-landing-pages.sh <이 repo 경로>   # ② 6개 파일 재생성
```

이 repo에서 직접 고치면 **다음 동기화 때 덮어써진다.** 개정 절차(사전 고지 기간,
재동의, 스토어 라벨 정합)는 앱 repo `docs/legal/README.md`를 따른다.

배포된 앱이 `https://pilmie.com/privacy/` · `/terms/`를 하드코딩하고 있고
(`lib/src/common/constants/app_links.dart`), 스토어 콘솔에도 등록돼 있다.
**이 URL들은 절대 바뀌면 안 된다.**

## 구조

```
index.html · en/ · ja/      로케일별 홈 (layout: home)
_data/i18n/{ko,en,ja}.yml   홈의 모든 문자열 ← 원본: 앱 repo docs/store-listing.md 캐논
_data/alternates.yml        hreflang + 언어 전환기를 함께 구동하는 URL 매핑
_layouts/{base,home,page}   page.html은 sync 스크립트 생성물 전용 (계약: layout/title/
                            include_in_header 외에 아무것도 요구하지 않는다)
_includes/sections/*        히어로 · 갤러리 · 기능7블록 · 리더 · CTA
_sass/_tokens.scss          앱의 lib/src/common/theme/app_colors.dart를 미러링
assets/shots/{ko,en,ja}/    스크린샷 (앱 repo store/ios → WebP)
assets/og/                  1200×630 소셜 카드 (tool/og_image.py로 생성)
tool/og_image.py            OG 이미지 재생성 (로컬 실행, 결과 PNG를 커밋)
```

### 카피는 창작하지 않는다

홈 문구는 앱 repo `docs/store-listing.md`의 **캐논**(슬로건 · 한 줄 소개 · 기능 7블록 ·
마무리 CTA)을 현지화한 것이다. 기능 7블록의 **순서는 고정**이며, 앱·스토어·랜딩이
같은 메시지를 쓰도록 유지한다. 새 문구가 필요하면 캐논부터 고친다.

## 로컬 실행

```bash
bundle install
bundle exec jekyll serve --livereload   # http://127.0.0.1:4000
```

`_config.yml` 변경은 핫리로드되지 않는다 — 서버를 재시작할 것.

## 에셋 재생성

```bash
brew install webp                       # cwebp (sips는 WebP 쓰기 불가)
python3 tool/og_image.py                # assets/og/og-{ko,en,ja}.png
```

스크린샷은 앱 repo `store/ios/{ko,en,ja}/`(기기 프레임 적용본)를 `cwebp -q 80`으로
440w/880w 변환해 `assets/shots/`에 넣는다.

## 기여

`master` 직접 푸시는 차단돼 있다. 브랜치 → 커밋 → PR → 머지.

Pages 배포가 "Deployment failed"로 실패하면 재빌드를 트리거한다:

```bash
gh api -X POST repos/develop-bullets/pilmie-service-app-landing-page/pages/builds
```

## 라이선스

코드는 [MIT](LICENSE) © 2026 Bullets. 브랜드 자산(마스코트 · 워드마크 · 앱 아이콘 ·
스크린샷)과 사이트 문구는 이에 포함되지 않으며 모든 권리를 보유한다.
연혁 및 저작자 표시는 [NOTICE.md](NOTICE.md) 참조.
