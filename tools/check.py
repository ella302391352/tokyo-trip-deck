"""Wiki / 簡報程式檢查（AGENTS.md 6.1）。

用法：在專案根目錄執行 `python tools/check.py`
有 ERROR 時 exit code = 1。
"""
import re
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
WIKI = ROOT / "wiki"
RAW = ROOT / "raw" / "papers"
OUTLINE = ROOT / "slides" / "outline.md"
DECK = ROOT / "slides" / "deck.html"

SPECIAL = {"index.md", "log.md", "overview.md"}
TYPES = {"source", "concept", "place", "synthesis"}
STALE_MONTHS = 12

LINK = re.compile(r"\]\(([^)\s]+?\.md)(?:#[^)]*)?\)")
SECTION = re.compile(r"<section\b([^>]*)>", re.I)
DATA_WIKI = re.compile(r'data-wiki\s*=\s*"([^"]*)"', re.I)
INFO_DATE = re.compile(r"資訊日期\s*(\d{4})-(\d{1,2})")

errors, warnings = [], []


def rel(p: Path) -> str:
    return p.relative_to(ROOT).as_posix()


def frontmatter(text: str):
    if not text.startswith("---"):
        return None
    end = text.find("\n---", 3)
    if end == -1:
        return None
    fm = {}
    for line in text[3:end].splitlines():
        if ":" in line and not line.startswith(" "):
            k, v = line.split(":", 1)
            fm[k.strip()] = v.split("#", 1)[0].strip()
    return fm


def parse_list(v: str):
    v = v.strip().strip("[]")
    return [x.strip().strip("'\"") for x in v.split(",") if x.strip()]


def months_ago(y: int, m: int) -> int:
    t = date.today()
    return (t.year - y) * 12 + (t.month - m)


def links_in(path: Path, text: str):
    """回傳 (連結字串, 解析後路徑)，只處理相對 .md 連結。"""
    out = []
    for target in LINK.findall(text):
        if "://" in target:
            continue
        out.append((target, (path.parent / target).resolve()))
    return out


def check_wiki():
    pages = sorted(WIKI.rglob("*.md")) if WIKI.exists() else []
    source_slugs = {p.stem for p in (WIKI / "sources").glob("*.md")}
    texts = {p: p.read_text(encoding="utf-8-sig") for p in pages}
    inbound = {p.resolve(): 0 for p in pages}
    index_links = set()

    # 先統計全部連結，再逐頁判斷孤兒頁／index 遺漏（否則排在 index.md 前面的頁面會誤判）
    for p, text in texts.items():
        for target, resolved in links_in(p, text):
            if not resolved.exists():
                errors.append(f"{rel(p)}: 斷鏈 → {target}")
            elif resolved in inbound and resolved != p.resolve():
                inbound[resolved] += 1
                if p.name == "index.md" and p.parent == WIKI:
                    index_links.add(resolved)

    for p, text in texts.items():
        for y, m in INFO_DATE.findall(text):
            if months_ago(int(y), int(m)) > STALE_MONTHS:
                warnings.append(f"{rel(p)}: 時效資訊可能過期（資訊日期 {y}-{m}）")

        if p.parent == WIKI and p.name in SPECIAL:
            continue

        fm = frontmatter(text)
        if fm is None:
            errors.append(f"{rel(p)}: 缺少 frontmatter")
            continue
        if fm.get("type") not in TYPES:
            errors.append(f"{rel(p)}: type 應為 {sorted(TYPES)} 之一，目前是 {fm.get('type')!r}")
        if not fm.get("updated"):
            errors.append(f"{rel(p)}: 缺少 updated")
        srcs = parse_list(fm.get("sources", ""))
        if not srcs:
            errors.append(f"{rel(p)}: sources 為空（每頁都要有依據）")
        for s in srcs:
            if s not in source_slugs:
                errors.append(f"{rel(p)}: sources 中的 {s!r} 在 wiki/sources/ 找不到")

        if fm.get("type") == "source":
            for k in ("url", "source_date", "raw"):
                if not fm.get(k):
                    errors.append(f"{rel(p)}: source 頁缺少 {k}")
            if not (RAW / f"{p.stem}.md").exists():
                errors.append(f"{rel(p)}: 找不到對應的 raw/papers/{p.stem}.md")
            m = re.match(r"(\d{4})-(\d{1,2})", fm.get("source_date", ""))
            if m and months_ago(int(m[1]), int(m[2])) > STALE_MONTHS:
                warnings.append(f"{rel(p)}: 來源日期 {fm['source_date']} 已超過 {STALE_MONTHS} 個月")

        if inbound[p.resolve()] == 0:
            errors.append(f"{rel(p)}: 孤兒頁（沒有任何頁面連到它）")
        if p.resolve() not in index_links:
            errors.append(f"{rel(p)}: 未列入 wiki/index.md")

        if "（待查）" in text:
            warnings.append(f"{rel(p)}: 含 {text.count('（待查）')} 處（待查）")

    return len(pages)


def check_raw():
    for p in sorted(RAW.glob("*.md")) if RAW.exists() else []:
        fm = frontmatter(p.read_text(encoding="utf-8-sig"))
        if fm is None:
            errors.append(f"{rel(p)}: 缺少 frontmatter")
            continue
        for k in ("title", "url", "publisher", "source_type", "published", "fetched"):
            if not fm.get(k):
                errors.append(f"{rel(p)}: 缺少 {k}")
        if fm.get("published") == "unknown":
            warnings.append(f"{rel(p)}: 原文日期不明")


def check_outline():
    if not OUTLINE.exists():
        return
    text = OUTLINE.read_text(encoding="utf-8-sig")
    slides = re.split(r"^## ", text, flags=re.M)[1:]
    if not slides:
        errors.append(f"{rel(OUTLINE)}: 找不到任何 `## ` 投影片")
    for i, body in enumerate(slides, 1):
        title = body.splitlines()[0].strip()
        wiki_links = [(t, r) for t, r in links_in(OUTLINE, body) if WIKI.resolve() in r.parents]
        if not wiki_links:
            errors.append(f"{rel(OUTLINE)}: 第 {i} 張「{title}」沒有 wiki 出處")
        for t, r in wiki_links:
            if not r.exists():
                errors.append(f"{rel(OUTLINE)}: 第 {i} 張「{title}」斷鏈 → {t}")


def check_deck():
    if not DECK.exists():
        return
    text = DECK.read_text(encoding="utf-8-sig")
    sections = SECTION.findall(text)
    if not sections:
        errors.append(f"{rel(DECK)}: 找不到任何 <section>")
    for i, attrs in enumerate(sections, 1):
        m = DATA_WIKI.search(attrs)
        paths = m[1].split() if m else []
        if not paths:
            errors.append(f"{rel(DECK)}: 第 {i} 張投影片沒有 data-wiki 出處")
        for w in paths:
            if not (WIKI / w).exists():
                errors.append(f"{rel(DECK)}: 第 {i} 張 data-wiki 指向不存在的 wiki/{w}")


def main():
    sys.stdout.reconfigure(errors="replace")
    n = check_wiki()
    check_raw()
    check_outline()
    check_deck()

    print(f"檢查 {n} 個 wiki 頁、{len(list(RAW.glob('*.md'))) if RAW.exists() else 0} 個 raw 來源")
    for w in warnings:
        print(f"WARN  {w}")
    for e in errors:
        print(f"ERROR {e}")
    print(f"結果：{len(errors)} 個錯誤、{len(warnings)} 個警告")
    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    sys.exit(main())
