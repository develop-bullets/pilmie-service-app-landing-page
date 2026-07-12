#!/usr/bin/env python3
"""OG(Open Graph) 소셜 카드 이미지 합성 — en/ja/ko.

규격: PNG, 1200x630 (Facebook/Slack/LinkedIn 권장 1.91:1). 카카오(2:1)·X도 정상 렌더.
출력: assets/og/og-<locale>.png  (Jekyll이 그대로 서빙, 재생성은 로컬에서만)

디자인은 앱 repo의 tool/feature_graphic.py(Play 피처 그래픽, 1024x500)와 동일 계열:
- 배경: 브랜드 앰버(#F4AA2B) → 마스코트 핑크(#F48FC2) 대각 그라데이션
- 화이트 워드마크 "Pilmie" + 슬로건(스토어 부제 캐논), 우측 마스코트 배지 + 소프트 글로우
- 화이트 텍스트는 이미 출시된 Play 피처 그래픽과 동일(소셜 카드는 사이트 히어로와 달리
  상호작용 WCAG 대상이 아니며, 브랜드 자산 일관성을 우선)

마스코트 원본은 앱 repo가 정본. 재생성은 이 스크립트를 로컬에서 실행:
    python3 tool/og_image.py
GitHub Pages는 Python을 실행하지 않으므로 결과 PNG를 커밋한다. tool/은 _site에서 제외.
"""
import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "assets", "og")

# 마스코트 원본(정본) — 앱 repo. 없으면 tool/mascot-src.png 폴백.
MASCOT_CANDIDATES = [
    "/Users/jyr/StudioProjects/bullets/pilmie/assets/images/pilmie.png",
    os.path.join(ROOT, "tool", "mascot-src.png"),
]

CANVAS = (1200, 630)
LOCALES = ["en", "ja", "ko"]

# 슬로건 = 스토어 부제 캐논(docs/store-listing.md).
SLOGANS = {
    "en": "Track reading & share reviews",
    "ja": "読書を記録して感想をシェア",
    "ko": "독서 기록하고 리뷰 나누기",
}

# 브랜드 색 — lib/src/common/theme/app_colors.dart
AMBER = (244, 170, 43)   # #F4AA2B accent
PINK = (244, 143, 194)   # #F48FC2 마스코트 핑크
WHITE = (255, 255, 255)

WORDMARK_FONT = "/System/Library/Fonts/SFNS.ttf"
FONT_CANDIDATES = {
    "ko": ["/System/Library/Fonts/AppleSDGothicNeo.ttc"],
    "en": ["/System/Library/Fonts/SFNS.ttf"],
    "ja": [
        "/System/Library/Fonts/ヒラギノ角ゴシック W6.ttc",
        "/System/Library/Fonts/ヒラギノ角ゴシック W3.ttc",
    ],
}


def _font(paths, size, variation=None):
    for path in paths:
        if os.path.exists(path):
            try:
                f = ImageFont.truetype(path, size)
                if variation:
                    try:
                        f.set_variation_by_name(variation)
                    except Exception:
                        pass
                return f
            except Exception:
                continue
    return ImageFont.load_default()


def _gradient_diag(size, c0, c1, small=(128, 64)):
    sw, sh = small
    base = Image.new("RGB", (sw, sh))
    px = base.load()
    for y in range(sh):
        for x in range(sw):
            t = (x / (sw - 1) + y / (sh - 1)) / 2
            px[x, y] = tuple(int(c0[i] + (c1[i] - c0[i]) * t) for i in range(3))
    return base.resize(size, Image.BILINEAR)


def _glow(size, color, alpha):
    glow = Image.new("RGBA", size, (0, 0, 0, 0))
    d = ImageDraw.Draw(glow)
    cx, cy = size[0] / 2, size[1] / 2
    r = min(size) * 0.30
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(*color, alpha))
    return glow.filter(ImageFilter.GaussianBlur(min(size) * 0.14))


def _text_shadow(canvas, pos, text, font, fill, stroke=0):
    x, y = pos
    sh = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    ImageDraw.Draw(sh).text(
        (x, y + 2), text, font=font, fill=(0, 0, 0, 90),
        stroke_width=stroke, stroke_fill=(0, 0, 0, 90),
    )
    sh = sh.filter(ImageFilter.GaussianBlur(5))
    canvas = Image.alpha_composite(canvas, sh)
    ImageDraw.Draw(canvas).text(
        (x, y), text, font=font, fill=fill, stroke_width=stroke, stroke_fill=fill,
    )
    return canvas


def _wrap(draw, text, font, max_w):
    words = text.split(" ")
    if len(words) == 1:  # CJK: 문자 단위
        line, lines = "", []
        for ch in text:
            if draw.textlength(line + ch, font=font) <= max_w:
                line += ch
            else:
                lines.append(line)
                line = ch
        if line:
            lines.append(line)
        return lines
    lines, line = [], ""
    for w in words:
        cand = (line + " " + w).strip()
        if draw.textlength(cand, font=font) <= max_w:
            line = cand
        else:
            lines.append(line)
            line = w
    if line:
        lines.append(line)
    return lines


def compose(locale, bg, mascot, glow):
    cw, ch = CANVAS
    canvas = bg.copy()
    draw = ImageDraw.Draw(canvas)

    wm_font = _font([WORDMARK_FONT], 132, variation="Bold")
    sl_font = _font(FONT_CANDIDATES[locale], 52, variation="Bold")

    wordmark = "Pilmie"
    slogan = SLOGANS[locale]
    sl_lines = _wrap(draw, slogan, sl_font, 700)

    wm_ascent, wm_descent = wm_font.getmetrics()
    wm_h = wm_ascent + wm_descent
    sl_h = int(sl_font.getmetrics()[0] * 1.32)
    gap_wm_sl = 28
    total_h = wm_h + gap_wm_sl + sl_h * len(sl_lines)
    y = (ch - total_h) // 2

    gap = 44
    mw, mh = mascot.size
    wm_w = int(draw.textlength(wordmark, font=wm_font))
    text_w = wm_w
    for line in sl_lines:
        text_w = max(text_w, int(draw.textlength(line, font=sl_font)))
    total_w = text_w + gap + mw
    start_x = (cw - total_w) // 2

    canvas = _text_shadow(canvas, (start_x, y), wordmark, wm_font, WHITE, stroke=1)

    sy = y + wm_h + gap_wm_sl
    for line in sl_lines:
        canvas = _text_shadow(canvas, (start_x, sy), line, sl_font, WHITE, stroke=0)
        sy += sl_h

    mascot_x = start_x + text_w + gap
    mascot_y = (ch - mh) // 2

    gx = mascot_x + mw // 2 - glow.size[0] // 2
    gy = mascot_y + mh // 2 - glow.size[1] // 2
    glow_layer = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    glow_layer.paste(glow, (gx, gy), glow)
    canvas = Image.alpha_composite(canvas, glow_layer)

    canvas.paste(mascot, (mascot_x, mascot_y), mascot)

    out_path = os.path.join(OUT, f"og-{locale}.png")
    canvas.convert("RGB").save(out_path, "PNG")
    return out_path, start_x, cw - (mascot_x + mw)


def main():
    os.makedirs(OUT, exist_ok=True)

    mascot_src = next((p for p in MASCOT_CANDIDATES if os.path.exists(p)), None)
    if not mascot_src:
        raise SystemExit("마스코트 원본을 찾을 수 없음: " + " / ".join(MASCOT_CANDIDATES))

    bg = _gradient_diag(CANVAS, AMBER, PINK).convert("RGBA")

    mascot = Image.open(mascot_src).convert("RGBA")
    m_h = 400
    m_w = int(mascot.size[0] * m_h / mascot.size[1])
    mascot = mascot.resize((m_w, m_h), Image.LANCZOS)

    glow = _glow((int(m_w * 1.7), int(m_h * 1.5)), WHITE, 150)

    for locale in LOCALES:
        out, lp, rp = compose(locale, bg, mascot, glow)
        sym = "대칭 OK" if abs(lp - rp) <= 1 else f"좌 {lp} · 우 {rp}"
        print(f"  ✓ {os.path.relpath(out, ROOT)}  ({sym})")

    print(f"\n완료: {len(LOCALES)}장 → assets/og/")


if __name__ == "__main__":
    main()
