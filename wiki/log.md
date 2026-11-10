# 變更紀錄（append-only）

## [2026-11-10] setup | 建立專案骨架
- 動作：建立 AGENTS.md、CLAUDE.md、wiki/index.md、wiki/overview.md、wiki/log.md、tools/check.py 與資料夾結構
- 檢查：check.py 執行通過（空 wiki）
- 出錯：無

## [2026-11-10] setup | 來源資料夾改為 raw/papers/
- 動作：AGENTS.md 與 tools/check.py 的 raw 路徑改為 raw/papers/；新增 reviews/_template.md
- 檢查：check.py 通過
- 出錯：無

## [2026-11-10] N1 sources | 第 1 批 6 篇
- 動作：搜尋 5 組關鍵字，提出 6 篇候選，使用者全數核准；新增 tools/fetch_raw.py；存入 raw/papers/ 6 篇（boca-japan-entry、funjapan-visit-japan-web、jnto-useful-tickets-tokyo、jnto-budget-guide、gotokyo-5day-itinerary、gotokyo-accommodations）
- 檢查：check.py 0 錯誤、2 警告（2 篇原文無日期）
- 出錯：有 — ① WebFetch 回傳摘要而非原文 ② shell 管線造成亂碼 ③ 英文網址回傳中文內容 ④ 東京地鐵官網 403、VJW 官方頁為 JS 動態頁（N1）
- 紀錄：reviews/2026-11-10-N1-source-collection.md

## [2026-11-10] N1 sources | 遊記 zhgchgli-tokyo-5day-2023
- 動作：搜尋遊記，提出 4 篇候選（B1–B4），使用者核准 B1；存入 raw/papers/zhgchgli-tokyo-5day-2023.md
- 檢查：check.py 0 錯誤
- 出錯：有 — 標題以「[」開頭，frontmatter 未加引號會被 YAML 解析成清單；修正 fetch_raw.py 一律為 title 加引號，刪除剛建立（尚未被引用）的檔案後以同一原文重抓（N1）。另 Dcard 候選抓取失敗已排除
