#!/usr/bin/env python3
"""data/products.json -> site/index.html (링크 모음 페이지 생성기).

파이프라인에서 새 영상이 발행되면 products.json에 한 줄 추가하고 이 스크립트를 돌린다.
사용법: python3 build.py
"""
import html
import json
from pathlib import Path

ROOT = Path(__file__).parent
DATA = ROOT / "data" / "products.json"
OUT = ROOT / "site" / "index.html"

# 버튼 순서와 라벨: 키 -> (라벨, 보조문구, CSS 클래스)
LINK_TYPES = {
    "ali": ("알리 최저가", "5~7일 배송", "ali"),
    "coupang": ("쿠팡 로켓배송", "내일 도착", "coupang"),
    "naver": ("네이버에서 보기", "네이버페이", "naver"),
    "kakao": ("카톡 선물하기", "선물용", "kakao"),
}

CSS = """
:root{--pink:#ff6f91;--pink-soft:#ffe3e8;--ink:#4a2b36;--muted:#8a6c76;--bg:#fff7f8;}
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:-apple-system,BlinkMacSystemFont,"Apple SD Gothic Neo","Noto Sans KR",sans-serif;
  background:var(--bg);color:var(--ink);line-height:1.5;-webkit-font-smoothing:antialiased}
.wrap{max-width:480px;margin:0 auto;padding:28px 18px 48px}
header{text-align:center;margin-bottom:18px}
header img{width:84px;height:84px;border-radius:50%;box-shadow:0 4px 14px rgba(255,111,145,.25)}
header h1{font-size:20px;margin-top:10px}
header p{color:var(--muted);font-size:14px;margin-top:2px}
.social{display:flex;gap:8px;justify-content:center;margin-top:12px}
.social a{font-size:13px;color:var(--ink);text-decoration:none;background:#fff;border:1px solid #f3d3da;
  padding:6px 12px;border-radius:999px}
.notice{font-size:12px;color:var(--muted);background:#fff;border:1px solid #f3d3da;border-radius:12px;
  padding:10px 12px;margin-bottom:14px}
.search{position:sticky;top:0;background:var(--bg);padding:6px 0 10px;z-index:2}
.search input{width:100%;font-size:16px;padding:12px 14px;border-radius:12px;border:1.5px solid #f0c3cd;
  background:#fff;color:var(--ink);outline:none}
.search input:focus{border-color:var(--pink)}
.card{background:#fff;border-radius:16px;padding:14px;margin-bottom:12px;box-shadow:0 2px 10px rgba(74,43,54,.06)}
.card .top{display:flex;align-items:center;gap:10px}
.no{flex:none;min-width:44px;height:28px;border-radius:999px;background:var(--pink-soft);color:var(--pink);
  font-weight:700;font-size:13px;display:flex;align-items:center;justify-content:center;padding:0 10px}
.name{font-weight:700;font-size:16px}
.note{color:var(--muted);font-size:13px;margin:6px 0 10px}
.btns{display:grid;gap:8px}
.btn{display:flex;justify-content:space-between;align-items:center;text-decoration:none;border-radius:12px;
  padding:12px 14px;font-weight:700;font-size:15px}
.btn small{font-weight:500;font-size:12px;opacity:.85}
.btn.ali{background:#ff4747;color:#fff}
.btn.coupang{background:#346aff;color:#fff}
.btn.naver{background:#03c75a;color:#fff}
.btn.kakao{background:#fee500;color:#3c1e1e}
.empty{text-align:center;color:var(--muted);font-size:14px;padding:30px 0;display:none}
footer{text-align:center;color:var(--muted);font-size:11px;margin-top:24px}
"""

JS = """
const q=document.getElementById('q'),cards=[...document.querySelectorAll('.card')],empty=document.getElementById('empty');
function filter(){const v=q.value.trim().replace(/^#/,'').toLowerCase();let n=0;
 cards.forEach(c=>{const hit=!v||c.dataset.no===v||c.dataset.text.includes(v);c.style.display=hit?'':'none';if(hit)n++;});
 empty.style.display=n?'none':'block';}
q.addEventListener('input',filter);
const h=location.hash.replace('#','');if(h){q.value=h;filter();}
"""


def esc(s):
    return html.escape(str(s), quote=True)


def card(p):
    buttons = []
    for key, (label, sub, cls) in LINK_TYPES.items():
        url = p.get("links", {}).get(key)
        if url:
            buttons.append(
                f'<a class="btn {cls}" href="{esc(url)}" target="_blank" rel="sponsored noopener">'
                f'{esc(label)}<small>{esc(sub)}</small></a>'
            )
    text = f'{p["no"]} {p["name"]} {p.get("note", "")}'.lower()
    note = f'<p class="note">{esc(p["note"])}</p>' if p.get("note") else ""
    return (
        f'<article class="card" id="p{p["no"]}" data-no="{p["no"]}" data-text="{esc(text)}">'
        f'<div class="top"><span class="no">#{p["no"]}</span><span class="name">{esc(p["name"])}</span></div>'
        f'{note}<div class="btns">{"".join(buttons)}</div></article>'
    )


def main():
    data = json.loads(DATA.read_text(encoding="utf-8"))
    s = data["site"]
    products = sorted(data["products"], key=lambda p: p["no"], reverse=True)
    cards = "\n".join(card(p) for p in products) or (
        '<p class="empty" style="display:block">첫 영상이 곧 올라와요! 조금만 기다려 주세요 🩷</p>'
    )
    page = f"""<!DOCTYPE html>
<html lang="ko"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(s["title"])}</title>
<meta name="description" content="{esc(s["tagline"])}">
<meta name="robots" content="index,follow">
<link rel="icon" href="logo.png">
<style>{CSS}</style></head>
<body><div class="wrap">
<header><img src="logo.png" alt="데일리픽 로고">
<h1>{esc(s["title"])}</h1><p>{esc(s["tagline"])}</p>
<div class="social"><a href="{esc(s["instagram"])}" target="_blank" rel="noopener">인스타그램</a>
<a href="{esc(s["youtube"])}" target="_blank" rel="noopener">유튜브</a></div></header>
<p class="notice">📢 {esc(s["disclosure"])}</p>
<div class="search"><input id="q" type="search" inputmode="search" placeholder="영상 번호나 상품명으로 찾기 (예: 12)"></div>
{cards}
<p class="empty" id="empty">찾는 상품이 없어요. 영상 번호를 다시 확인해 주세요.</p>
<footer>© 데일리픽 · 가격과 재고는 판매처에서 확인해 주세요.</footer>
</div><script>{JS}</script></body></html>
"""
    OUT.write_text(page, encoding="utf-8")
    print(f"생성 완료: {OUT} (상품 {len(products)}개)")


if __name__ == "__main__":
    main()
