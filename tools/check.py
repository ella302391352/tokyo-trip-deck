"""Wiki / 簡報程式檢查（AGENTS.md 6.1、.agents/workflows/topic-slides.md）。

用法：在專案根目錄執行 `python tools/check.py`
     只檢查某個簡報資料夾：`python tools/check.py --slides slides/baseline`
有 ERROR 時 exit code = 1。
"""
import re
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
WIKI = ROOT / "wiki"
RAW = ROOT / "raw" / "papers"
SLIDES = ROOT / "slides"

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
        stale = [f"{y}-{m}" for y, m in INFO_DATE.findall(text) if months_ago(int(y), int(m)) > STALE_MONTHS]
        if stale and p.name != "log.md":  # log 是歷史紀錄，提到舊日期是正常的
            warnings.append(f"{rel(p)}: {len(stale)} 處時效資訊可能過期（資訊日期 {', '.join(sorted(set(stale)))}）")

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


CARD_LINE = re.compile(r"^- (C\d+)：(.+?)〔wiki: ([^〕]+)〕\s*$")
CITE = re.compile(r"〔([a-z0-9-]+)#(C\d+)〕")
NUM = re.compile(r"\d[\d,]*(?:\.\d+)?")
SLIDE_MIN, SLIDE_MAX = 8, 15


def nums(text):
    return {n.replace(",", "") for n in NUM.findall(text) if len(n.replace(",", "")) >= 2}


def check_slides(sdir: Path, baseline=False):
    """簡報 graph（.agents/workflows/topic-slides.md）各關產物的檢查。"""
    source_slugs = {p.stem for p in (WIKI / "sources").glob("*.md")}
    claims = {}  # (slug, Cn) -> text
    cards_dir = sdir / "cards"
    for p in sorted(cards_dir.glob("*.md")) if cards_dir.exists() else []:
        text = p.read_text(encoding="utf-8-sig")
        fm = frontmatter(text) or {}
        slug = fm.get("source", "")
        if slug != p.stem or slug not in source_slugs:
            errors.append(f"{rel(p)}: source 應為檔名且存在於 wiki/sources/（目前 {slug!r}）")
        for line in text.splitlines():
            if not line.startswith("- "):
                continue
            m = CARD_LINE.match(line)
            if not m:
                errors.append(f"{rel(p)}: 卡片行格式錯誤（需「- Cn：…〔wiki: 路徑〕」）：{line[:40]}")
                continue
            claims[(p.stem, m[1])] = m[2]
            for w in m[3].split():
                if not (WIKI / w).exists():
                    errors.append(f"{rel(p)} {m[1]}: 指向不存在的 wiki/{w}")

    n_outline = None
    outline = sdir / "outline.md"
    if outline.exists():
        heads = re.findall(r"^## (\d+)", outline.read_text(encoding="utf-8-sig"), re.M)
        n_outline = len(heads)
        for line in outline.read_text(encoding="utf-8-sig").splitlines():
            if line.startswith("卡片："):
                for ref in re.findall(r"([a-z0-9-]+)#(C\d+)", line):
                    if ref not in claims:
                        errors.append(f"{rel(outline)}: 引用不存在的卡片 {ref[0]}#{ref[1]}")

    used = set()
    drafts = sorted((sdir / "drafts").glob("*.md")) if (sdir / "drafts").exists() else []
    for p in drafts:
        text = p.read_text(encoding="utf-8-sig")
        # 不用 frontmatter()：它會把 # 之後當註解切掉，而卡片編號正好含 #
        m = re.search(r"^cards:\s*\[(.*?)\]", text, re.M)
        allowed = set(re.findall(r"([a-z0-9-]+)#(C\d+)", m[1])) if m else set()
        if not m:
            errors.append(f"{rel(p)}: frontmatter 缺少 cards 清單")
        for line in text.splitlines():
            if not line.lstrip().startswith("- "):
                continue
            refs = CITE.findall(line)
            if not refs and "（整理者推論）" not in line:
                errors.append(f"{rel(p)}: 要點沒有卡片出處也沒標（整理者推論）：{line.strip()[:40]}")
            cited_text = ""
            for ref in refs:
                if ref not in claims:
                    errors.append(f"{rel(p)}: 引用不存在的卡片 {ref[0]}#{ref[1]}")
                elif ref not in allowed:
                    errors.append(f"{rel(p)}: 引用了這頁 cards 清單以外的卡片 {ref[0]}#{ref[1]}")
                else:
                    cited_text += claims[ref]
                    used.add(ref)
            if refs:
                missing = nums(CITE.sub("", line)) - nums(cited_text)
                if missing:
                    errors.append(f"{rel(p)}: 數字在引用卡片中找不到 {sorted(missing)}：{line.strip()[:40]}")

    deck = sdir / "deck.html"
    n_deck = None
    if deck.exists():
        text = deck.read_text(encoding="utf-8-sig")
        sections = SECTION.findall(text)
        n_deck = len(sections)
        for i, attrs in enumerate(sections, 1):
            m = DATA_WIKI.search(attrs)
            paths = m[1].split() if m else []
            if not paths:
                errors.append(f"{rel(deck)}: 第 {i} 頁沒有 data-wiki 出處")
            for w in paths:
                if not (WIKI / w).exists():
                    errors.append(f"{rel(deck)}: 第 {i} 頁 data-wiki 指向不存在的 wiki/{w}")
            if not baseline and not re.search(r'data-draft\s*=\s*"\d+"', attrs):
                errors.append(f"{rel(deck)}: 第 {i} 頁沒有 data-draft")

    counts = {k: v for k, v in (("大綱", n_outline), ("逐頁稿", len(drafts) or None), ("簡報", n_deck)) if v}
    for k, v in counts.items():
        if not SLIDE_MIN <= v <= SLIDE_MAX:
            errors.append(f"{rel(sdir)}: {k}共 {v} 頁，應為 {SLIDE_MIN}–{SLIDE_MAX} 頁")
    if len(set(counts.values())) > 1:
        errors.append(f"{rel(sdir)}: 各關頁數不一致 {counts}")

    if drafts and claims:
        unused = sorted({s for s, _ in claims} - {s for s, _ in used})
        if unused:
            warnings.append(f"{rel(sdir)}: 覆蓋率——這些來源的卡片沒有任何一頁用到：{', '.join(unused)}")


def main():
    sys.stdout.reconfigure(errors="replace")
    if len(sys.argv) == 3 and sys.argv[1] == "--slides":
        # 只檢查某個簡報資料夾，例如對照組：python tools/check.py --slides slides/baseline
        check_slides((ROOT / sys.argv[2]).resolve(), baseline=True)
        for w in warnings:
            print(f"WARN  {w}")
        for e in errors:
            print(f"ERROR {e}")
        print(f"結果：{len(errors)} 個錯誤、{len(warnings)} 個警告")
        sys.exit(1 if errors else 0)
    n = check_wiki()
    check_raw()
    check_slides(SLIDES)

    print(f"檢查 {n} 個 wiki 頁、{len(list(RAW.glob('*.md'))) if RAW.exists() else 0} 個 raw 來源")
    for w in warnings:
        print(f"WARN  {w}")
    for e in errors:
        print(f"ERROR {e}")
    print(f"結果：{len(errors)} 個錯誤、{len(warnings)} 個警告")
    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    sys.exit(main())
