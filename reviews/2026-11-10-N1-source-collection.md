# [N1] 找來源 第 1 批

- 日期：2026-11-10
- 檢查類型：程式（check.py、fetch_raw.py 預覽）＋人工（使用者挑選）
- 輸入：WebSearch 5 組查詢（入境、Visit Japan Web、地鐵票券、住宿區域、預算）
- 結果：通過，6 篇存入 raw/papers/

## 候選與篩選結果

| slug | 類型 | 原文日期 | 結果 |
|---|---|---|---|
| boca-japan-entry | official | 2022-06-21 | 收錄（偏舊，含疫情期間用語） |
| funjapan-visit-japan-web | guide | 2026-08-28 | 收錄（含聯盟行銷連結；2030 廢止紙本、免稅新制未附官方出處） |
| jnto-useful-tickets-tokyo | official | 2024-12-24（資料基準日） | 收錄 |
| jnto-budget-guide | official | unknown | 收錄（無日期） |
| gotokyo-5day-itinerary | official | 2026-03-05 | 收錄 |
| gotokyo-accommodations | official | unknown | 收錄（無日期） |
| tokyometro.jp 票券頁 | official | — | 排除：HTTP 403，無法取得原文 |
| vjw-lp.digital.go.jp | official | — | 排除：轉址後頁面由 JavaScript 載入，只抓到標題 |
| *.pages.dev 預算文章 | — | — | 排除：疑似 AI 量產／內容農場，數字無出處 |

## 發現的問題

1. **抓取工具會改寫內容**（N1）：WebFetch 回傳的是模型整理後的摘要，不是原文；若直接存成 raw 會違反「raw 不改寫」。→ 新增 `tools/fetch_raw.py`，直接下載 HTML 轉 markdown。
2. **編碼亂碼**（N1）：fetch_raw.py 的輸出經 PowerShell 管線轉手後變成亂碼（Big5/UTF-8 混用）。→ 加 `--preview` 選項，由 Python 直接寫 UTF-8 檔，不經過 shell。
3. **語言版本與網址不符**（N1）：jnto-budget-guide 用英文網址抓取，但因 Accept-Language 為繁中，伺服器回傳中文內容。→ 改用官方繁中網址 `/tw/guide/...`，讓 url 與實際內容一致。
4. **官方最新價格無法取得**（N1）：Tokyo Subway Ticket 價格，JNTO（2024-12）寫 24h 800 円；搜尋摘要顯示東京地鐵官網為 1,000 円，但官網 403 無法存成 raw。→ wiki 只能依 raw 寫 800 円並標資訊日期，在 ingest 時標記為（待查）／可能過期。

## 處理方式

- 每篇先 `--preview` 檢查內容，再用 `--start/--end` 切掉導覽列與頁尾，最後才正式寫入。
- check.py：0 錯誤，2 警告（2 篇原文日期不明）。

## 出錯源頭節點

N1（4 個問題都在取得來源階段發生）

## 是否要把檢查往前移

是。把「內容完整性預覽」放在寫入 raw 之前（fetch_raw.py `--preview`），而不是存完才發現是導覽列或亂碼。因 raw 不可修改，存錯就只能留著，所以檢查必須在寫入前。
