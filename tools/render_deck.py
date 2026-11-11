"""G5：把 slides/drafts/*.md 原文渲染成 slides/deck.html（不改任何文字）。

用法：python tools/render_deck.py
"""
import html
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SLIDES = ROOT / "slides"
CARD_LINE = re.compile(r"^- (C\d+)：(.+?)〔wiki: ([^〕]+)〕\s*$")
CITE = re.compile(r"〔([a-z0-9-]+)#(C\d+)〕")


def card_wiki():
    out = {}
    for p in (SLIDES / "cards").glob("*.md"):
        for line in p.read_text(encoding="utf-8-sig").splitlines():
            m = CARD_LINE.match(line)
            if m:
                out[(p.stem, m[1])] = m[3].split()
    return out


def render_line(text):
    esc = html.escape(text)
    return CITE.sub(lambda m: f'<span class="cite">{m[1]}#{m[2]}</span>', esc)


def main():
    wiki_of = card_wiki()
    sections = []
    for p in sorted((SLIDES / "drafts").glob("*.md")):
        text = p.read_text(encoding="utf-8-sig")
        _, fm, body = text.split("---", 2)
        num = re.search(r"^slide:\s*(\d+)", fm, re.M)[1]
        title = re.search(r"^title:\s*(.+)$", fm, re.M)[1].strip()
        cards = re.findall(r"([a-z0-9-]+)#(C\d+)", re.search(r"^cards:\s*\[(.*?)\]", fm, re.M)[1])
        wiki = []
        for c in cards:
            for w in wiki_of.get(c, []):
                if w not in wiki:
                    wiki.append(w)
        items, paras = [], []
        for line in body.strip().splitlines():
            if line.lstrip().startswith("- "):
                items.append(f"<li>{render_line(line.lstrip()[2:])}</li>")
            elif line.strip():
                paras.append(f"<p>{render_line(line.strip())}</p>")
        cls = ' class="cover"' if num == "01" else ""
        sections.append(
            f'<section{cls} data-draft="{num}" data-wiki="{" ".join(wiki)}">\n'
            f'  <h2>{html.escape(title)}</h2>\n'
            + (f'  {"".join(paras)}\n' if paras else "")
            + f'  <ul>\n    ' + "\n    ".join(items) + "\n  </ul>\n"
            f'  <footer><span>出處（wiki）：{html.escape("、".join(wiki))}</span><span class="pg">{int(num)} / {{TOTAL}}</span></footer>\n'
            "</section>"
        )
    deck = TEMPLATE.replace("{SECTIONS}", "\n".join(sections)).replace("{TOTAL}", str(len(sections)))
    (SLIDES / "deck.html").write_text(deck, encoding="utf-8")
    print(f"slides/deck.html：{len(sections)} 頁")


TEMPLATE = """<!doctype html>
<html lang="zh-Hant">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>第一次自由行規劃</title>
<style>
:root { --bg:#fbfaf7; --fg:#1f2328; --muted:#6b7280; --accent:#c2410c; --line:#e5e1d8; --cite:#8a6d3b; }
@media (prefers-color-scheme: dark) { :root:not([data-theme="light"]) { --bg:#16181d; --fg:#e8e6e1; --muted:#9aa0a8; --accent:#fb923c; --line:#2c2f36; --cite:#d4b483; } }
:root[data-theme="dark"] { --bg:#16181d; --fg:#e8e6e1; --muted:#9aa0a8; --accent:#fb923c; --line:#2c2f36; --cite:#d4b483; }
* { box-sizing: border-box; }
html, body { margin:0; height:100%; background:var(--bg); color:var(--fg);
  font-family: "Noto Sans TC","Microsoft JhengHei","PingFang TC",sans-serif; }
section { display:none; height:100vh; width:100%; overflow:hidden; flex-direction:column;
  padding: clamp(16px,4vh,48px) clamp(16px,6vw,96px) 0; }
section.active { display:flex; }
h2 { margin:0 0 .6em; font-size:clamp(22px,3.6vw,40px); color:var(--accent); line-height:1.25;
  border-bottom:2px solid var(--line); padding-bottom:.3em; }
ul { margin:0; padding-left:1.2em; flex:1; font-size:clamp(15px,2.1vw,23px); line-height:1.5; }
li { margin:.35em 0; }
p { font-size:clamp(15px,2.1vw,23px); line-height:1.5; margin:.3em 0; }
.cite { font-size:.62em; color:var(--cite); margin-left:.3em; white-space:nowrap; }
footer { display:flex; justify-content:space-between; gap:1em; font-size:clamp(10px,1.1vw,13px);
  color:var(--muted); border-top:1px solid var(--line); padding:.6em 0 1em; }
footer span:first-child { overflow-wrap:anywhere; }
section.cover { justify-content:center; }
section.cover h2 { font-size:clamp(28px,5.2vw,60px); border:none; }
section.cover ul { flex:0; }
.nav { position:fixed; right:16px; bottom:48px; display:flex; gap:8px; }
.nav button { font-size:18px; width:40px; height:40px; border-radius:50%; border:1px solid var(--line);
  background:var(--bg); color:var(--fg); cursor:pointer; }
</style>
</head>
<body>
{SECTIONS}
<div class="nav"><button id="prev" aria-label="上一頁">‹</button><button id="next" aria-label="下一頁">›</button></div>
<script>
const S = [...document.querySelectorAll("section")];
let i = 0;
function go(n) { i = Math.max(0, Math.min(S.length - 1, n)); S.forEach((s, k) => s.classList.toggle("active", k === i)); history.replaceState(null, "", "#" + (i + 1)); }
const m = location.hash.match(/(\\d+)/); go(m ? +m[1] - 1 : 0);
document.addEventListener("keydown", e => {
  if (["ArrowRight","PageDown"," "].includes(e.key)) go(i + 1);
  if (["ArrowLeft","PageUp"].includes(e.key)) go(i - 1);
});
document.getElementById("next").onclick = () => go(i + 1);
document.getElementById("prev").onclick = () => go(i - 1);
let x0 = null;
document.addEventListener("touchstart", e => x0 = e.touches[0].clientX);
document.addEventListener("touchend", e => { if (x0 === null) return; const d = e.changedTouches[0].clientX - x0; if (Math.abs(d) > 50) go(i + (d < 0 ? 1 : -1)); x0 = null; });
</script>
</body>
</html>
"""

if __name__ == "__main__":
    main()
