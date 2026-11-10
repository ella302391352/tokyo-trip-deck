"""把網頁原文轉存成 raw/papers/<slug>.md（AGENTS.md N1）。

只做格式轉換（HTML → markdown），不改寫、不摘要。raw 建立後不可修改，所以檔案已存在時拒絕覆寫。

用法：
  python tools/fetch_raw.py <url> <slug> --title "..." --publisher "..." \
      --type official|guide|blog --published 2026-03-05 \
      [--start "內文開頭的一段文字"] [--end "內文結尾之後的一段文字"]

--start / --end 用來切掉導覽列、頁尾等非內文部分（保留 start 那行，不含 end 那行）。
"""
import argparse
import re
import sys
import urllib.request
from datetime import date
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "raw" / "papers"

SKIP = {"script", "style", "noscript", "svg", "nav", "header", "footer", "aside", "form", "button", "select", "iframe"}
BLOCK = {"p", "div", "section", "article", "main", "br", "tr", "table", "ul", "ol", "dl", "dt", "dd", "figure", "figcaption", "blockquote"}
HEAD = {"h1": "# ", "h2": "## ", "h3": "### ", "h4": "#### ", "h5": "##### ", "h6": "###### "}
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Safari/537.36"


class ToMarkdown(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.out = []
        self.skip = 0
        self.href = None

    def handle_starttag(self, tag, attrs):
        if tag in SKIP:
            self.skip += 1
            return
        if self.skip:
            return
        if tag in HEAD:
            self.out.append("\n\n" + HEAD[tag])
        elif tag == "li":
            self.out.append("\n- ")
        elif tag in ("td", "th"):
            self.out.append(" | ")
        elif tag in BLOCK:
            self.out.append("\n")
        elif tag == "a":
            self.href = dict(attrs).get("href")

    def handle_endtag(self, tag):
        if tag in SKIP:
            self.skip = max(0, self.skip - 1)
            return
        if self.skip:
            return
        if tag in HEAD or tag in BLOCK:
            self.out.append("\n")
        elif tag == "a":
            self.href = None

    def handle_data(self, data):
        if self.skip:
            return
        text = re.sub(r"\s+", " ", data)
        if text.strip():
            self.out.append(text)

    def markdown(self):
        text = "".join(self.out)
        lines = [ln.strip() for ln in text.splitlines()]
        lines = [re.sub(r"^(\|\s*)+", "| ", ln) if ln.startswith("|") else ln for ln in lines]
        text = "\n".join(lines)
        return re.sub(r"\n{3,}", "\n\n", text).strip()


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Language": "zh-TW,zh;q=0.9,en;q=0.8"})
    with urllib.request.urlopen(req, timeout=30) as r:
        raw = r.read()
        charset = r.headers.get_content_charset() or "utf-8"
    return raw.decode(charset, errors="replace")


def cut(text, start, end):
    if start:
        i = text.find(start)
        if i == -1:
            sys.exit(f"找不到 --start 文字：{start!r}")
        text = text[text.rfind("\n", 0, i) + 1:]
    if end:
        j = text.find(end)
        if j == -1:
            sys.exit(f"找不到 --end 文字：{end!r}")
        text = text[:text.rfind("\n", 0, j)]
    return text.strip()


def main():
    sys.stdout.reconfigure(errors="replace")
    ap = argparse.ArgumentParser()
    ap.add_argument("url")
    ap.add_argument("slug")
    ap.add_argument("--title", required=True)
    ap.add_argument("--publisher", required=True)
    ap.add_argument("--type", required=True, choices=["official", "guide", "blog"])
    ap.add_argument("--published", default="unknown")
    ap.add_argument("--start")
    ap.add_argument("--end")
    ap.add_argument("--preview", metavar="FILE", help="只把轉換結果寫到 FILE 預覽，不寫入 raw/")
    a = ap.parse_args()

    dest = RAW / f"{a.slug}.md"
    if dest.exists() and not a.preview:
        sys.exit(f"{dest} 已存在：raw 不可覆寫")

    p = ToMarkdown()
    p.feed(fetch(a.url))
    body = cut(p.markdown(), a.start, a.end)

    if a.preview:
        Path(a.preview).write_text(body + "\n", encoding="utf-8")
        print(f"預覽已寫入 {a.preview}（{len(body)} 字元）")
        return

    fm = (
        "---\n"
        f"title: {a.title}\n"
        f"url: {a.url}\n"
        f"publisher: {a.publisher}\n"
        f"source_type: {a.type}\n"
        f"published: {a.published}\n"
        f"fetched: {date.today().isoformat()}\n"
        "---\n\n"
    )
    RAW.mkdir(parents=True, exist_ok=True)
    dest.write_text(fm + body + "\n", encoding="utf-8")
    print(f"已寫入 {dest.relative_to(ROOT).as_posix()}（{len(body)} 字元）")


if __name__ == "__main__":
    main()
