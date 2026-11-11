"""渲染關卡（.agents/workflows/topic-slides.md G5）：用 Edge 無頭模式逐頁檢查簡報有沒有溢出。

用法：python tools/render_check.py [slides/deck.html] [--shots]
  - 以 1280×720（桌機）與 390×844（手機）兩種尺寸開啟
  - 每個 <section> 單獨顯示，量測內容是否超出畫面
  - --shots：另存每頁截圖到 slides/screenshots/
有溢出時 exit code = 1。不會修改 deck.html（檢查的是一份注入量測腳本的暫存複本）。
"""
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
EDGE = Path(r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe")
SIZES = {"桌機": (1280, 720), "手機": (390, 844)}

PROBE = """
<script>
window.addEventListener('load', () => setTimeout(() => {
  const secs = [...document.querySelectorAll('section')];
  const show = (location.hash.match(/show=(\\d+)/) || [])[1];
  const res = [];
  secs.forEach((s, i) => {
    secs.forEach(o => { o.style.setProperty('display', 'none', 'important'); });
    s.style.setProperty('display', 'block', 'important');
    s.style.setProperty('visibility', 'visible', 'important');
    s.style.setProperty('opacity', '1', 'important');
    s.style.setProperty('transform', 'none', 'important');
    const r = s.getBoundingClientRect();
    const over = s.scrollHeight > s.clientHeight + 1 || s.scrollWidth > s.clientWidth + 1
      || r.height > innerHeight + 1 || document.documentElement.scrollWidth > innerWidth + 1;
    res.push({i: i + 1, over, h: Math.round(Math.max(r.height, s.scrollHeight)), vh: innerHeight});
  });
  if (show) { secs.forEach((o, i) => o.style.setProperty('display', i + 1 == show ? 'block' : 'none', 'important')); }
  const pre = document.createElement('pre'); pre.id = '__render_report';
  pre.textContent = JSON.stringify(res); pre.style.display = 'none';
  document.body.appendChild(pre);
}, 300));
</script>
"""


def edge(args):
    return subprocess.run([str(EDGE), "--headless=new", "--disable-gpu", "--hide-scrollbars",
                           "--virtual-time-budget=4000", *args],
                          capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=120)


def main():
    sys.stdout.reconfigure(errors="replace")
    argv = [a for a in sys.argv[1:] if not a.startswith("--")]
    deck = (ROOT / (argv[0] if argv else "slides/deck.html")).resolve()
    if not deck.exists():
        sys.exit(f"找不到 {deck}")
    if not EDGE.exists():
        sys.exit("找不到 Microsoft Edge，無法做渲染檢查")

    html = deck.read_text(encoding="utf-8-sig")
    i = html.lower().rfind("</body>")
    probed = html[:i] + PROBE + html[i:] if i != -1 else html + PROBE
    # 暫存複本放在 deck 同一層，讓相對路徑的資源照常載入
    with tempfile.NamedTemporaryFile("w", suffix=".html", dir=deck.parent, delete=False, encoding="utf-8") as f:
        f.write(probed)
        tmp = Path(f.name)

    bad = 0
    try:
        for name, (w, h) in SIZES.items():
            out = edge([f"--window-size={w},{h}", "--dump-dom", tmp.as_uri()]).stdout
            m = re.search(r'<pre id="__render_report"[^>]*>(.*?)</pre>', out, re.S)
            if not m:
                print(f"ERROR {name}：量測腳本沒有回報（找不到 <section> 或頁面載入失敗）")
                bad += 1
                continue
            res = json.loads(m[1].replace("&quot;", '"'))
            if not res:
                print(f"ERROR {name}：找不到任何 <section>")
                bad += 1
            over = [r for r in res if r["over"]]
            for r in over:
                print(f"ERROR {name} {w}×{h}：第 {r['i']} 頁溢出（內容高 {r['h']}px，畫面 {r['vh']}px）")
            bad += len(over)
            print(f"{name} {w}×{h}：{len(res)} 頁，{len(over)} 頁溢出")

            if "--shots" in sys.argv:
                shots = deck.parent / "screenshots"
                shots.mkdir(exist_ok=True)
                for r in res:
                    dest = shots / f"{'desktop' if name == '桌機' else 'mobile'}-{r['i']:02d}.png"
                    edge([f"--window-size={w},{h}", f"--screenshot={dest}", f"{tmp.as_uri()}#show={r['i']}"])
                print(f"  截圖已存到 {shots.relative_to(ROOT).as_posix()}/")
    finally:
        tmp.unlink(missing_ok=True)

    print(f"結果：{bad} 個問題")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
