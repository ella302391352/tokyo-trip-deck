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

## [2026-11-11] N3 lint | 第 1 次修正（第 2 輪）
- 動作：使用者確認後修正 13 處（overview、3 個 sources 頁、itinerary-planning、accommodation-area、budget、common-mistakes、tokyo-areas）
- 檢查：check.py 0 錯誤；AI 複審 13 處全部已修正、無新問題 → 通過
- 出錯：無

## [2026-11-11] workflow | 把 AI 審查往前移到 N2
- 動作：使用者同意修改 AGENTS.md：N2 完成標準新增「每篇 ingest 後，對本次新增／修改頁面做忠於來源的 AI 審查」；N3 改為著重跨頁問題
- 原因：N3 第 1 次 lint 發現 9 個問題全部在 N2 產生，check.py 與 N2 自我複查都抓不到；累積 3 篇才審，錯誤已擴散到多頁（例如同一個「熱門景點先買票」泛化同時出現在 overview、itinerary-planning、common-mistakes）
- 出錯：無

## [2026-11-11] N2 ingest | boca-japan-entry
- 動作：先討論後生成（不收打工／留學；海關只寫三件事；黃金與遭拒入境案例不放常見錯誤）；新增 sources/boca-japan-entry、concepts/entry-requirements；更新 overview（入境準備）、index
- 檢查：check.py 0 錯誤；AI 審查（新流程）第 1 輪 2 問題＋1 不確定 → 修正 → 第 2 輪通過
- 出錯：有 — ① 討論時把「出境申請表（ED 卡）」說成「入境卡」，寫入前改回原文用語 ② 語氣改變 2 處（「請務必」→「建議」、「原則上僅適用」→「僅限」）③ 把 N1 網頁摘要看到的「最後更新」帶進來，raw 中沒有（N2）
- 紀錄：reviews/2026-11-11-N2-boca-japan-entry.md

## [2026-11-11] N2 ingest | funjapan-visit-japan-web
- 動作：先討論後生成（免稅與機場設備細節只放來源頁；兩種紙本表格名稱各依原文；無出處說法標「未附官方出處」）；新增 sources/funjapan-visit-japan-web；更新 concepts/entry-requirements（新增第 6 節 Visit Japan Web，消掉 1 項待查）、overview、index
- 檢查：check.py 0 錯誤；AI 審查第 1 輪 1 問題 → 修正 → 第 2 輪通過
- 出錯：有 — 把 N1 網頁摘要中的「著作權屬 JTB」帶進來源頁，raw 中沒有（N2）。與上一篇「頁面最後更新」為同一模式：N1 看過、但沒存進 raw 的資訊滲入 wiki
- 紀錄：reviews/2026-11-11-N2-funjapan-visit-japan-web.md
