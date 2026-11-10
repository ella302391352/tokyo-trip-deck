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

## [2026-11-10] N2 ingest | gotokyo-5day-itinerary
- 動作：先討論後生成（使用者確認重點與頁面規劃）；新增 sources/gotokyo-5day-itinerary、concepts/itinerary-planning、concepts/accommodation-area、places/tokyo-areas；更新 overview、index
- 檢查：check.py 第 1 輪 3 錯誤（工具誤判）→ 修正 check.py → 第 2 輪 0 錯誤、5 警告
- 出錯：有 — ① 原文內部矛盾（3 天方案「南部」vs 第 4 天「西部」），以 ⚠️ 標記 ② check.py 邊讀邊判斷導致孤兒頁誤判（N2）
- 紀錄：reviews/2026-11-10-N2-gotokyo-5day-itinerary.md

## [2026-11-10] N2 ingest | jnto-useful-tickets-tokyo
- 動作：先討論後生成（使用者決定：只寫成人價；機場交通先放交通頁小節）；新增 sources/jnto-useful-tickets-tokyo、concepts/transit-passes；更新 concepts/accommodation-area（住宿地點影響選票）、overview、index
- 檢查：check.py 第 1 輪 0 錯誤；過期偵測正確觸發（資訊日期 2024-12、來源日期超過 12 個月）。同頁重複警告太多，改為每頁彙總一行；以真實 wiki＋測試副本各跑一次確認
- 出錯：無（內容）。待解：Tokyo Subway Ticket 新價格缺乏可存檔的官方來源，標為可能過期（待查）

## [2026-11-10] N2 ingest | zhgchgli-tokyo-5day-2023
- 動作：先討論後生成（使用者同意新增「新手常見錯誤」「預算與付款」兩頁；景點遊玩細節不收）；新增 sources/zhgchgli-tokyo-5day-2023、concepts/common-mistakes、concepts/budget；更新 transit-passes（機場踩雷、Android 用 Welcome Suica）、itinerary-planning（熱門景點先買票，消掉 1 項待查）、accommodation-area（一間住到底的實例）、overview、index
- 檢查：寫完後自我複查 → check.py 第 1 輪 0 錯誤；log.md 被誤報含過期資訊，check.py 改為不檢查 log
- 出錯：有 — ① 「新手常見錯誤」頁寫進一條來源中沒人犯過、由 AI 自行假設的錯誤（Tokyo Subway Ticket 購買資格），屬「超出來源」，已刪除並在頁首註明只收實際發生的錯誤 ② SIM 卡「$500」原文無幣別，差點被預設幣別，已註明（N2）③ 原文內部矛盾：不能刷卡的地點「東京車站」vs「新橋」，以 ⚠️ 標記
- 紀錄：reviews/2026-11-10-N2-zhgchgli-tokyo-5day-2023.md

## [2026-11-10] N3 lint | 第 1 次（3 篇後）
- 動作：check.py ＋ AI 審查（新 subagent，只給 10 個 wiki 頁與 3 篇 raw）；依規則只回報，修正待使用者確認
- 檢查：check.py 0 錯誤；AI 審查 10 頁中 6 頁需修改，9 個確定問題、4 個不確定
- 出錯：有 — 9 個問題全部源自 N2 生成階段（找不到來源 4、講反 2、語氣改變 1、個人經驗泛化 2），數字與日期抄錄 0 錯誤
- 紀錄：reviews/2026-11-10-N3-lint.md
