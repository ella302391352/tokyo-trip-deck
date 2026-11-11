# [N2] Ingest gotokyo-haneda-airport

- 日期：2026-11-11
- 檢查類型：人工（先討論、後生成）＋程式（check.py）＋ AI 審查（新 subagent）
- 結果：通過（AI 審查第 2 輪）

## 討論階段（使用者確認的事項）

- 網路（Wi-Fi／SIM）資訊不多，先放在交通頁羽田小節，不另開頁
- 羽田至成田、航廈、餐廳、購物、貴賓室、周邊飯店只放來源頁或不收

## AI 審查第 1 輪：需修改（1 個輕微問題）

| 頁面 | 位置 | 類型 | 說明 |
|---|---|---|---|
| sources/gotokyo-haneda-airport | 「成田特快 N'EX」 | 引文不逐字 | raw 為「成田特快N'EX」，多了一個空格 |

## AI 審查第 2 輪：通過

check.py：0 錯誤。

## 觀察

本篇是第一次沒有出現「找不到來源／語氣改變／N1 資訊滲入」的 ingest，唯一問題是引文空格。對照 N2 各篇的問題數與類型：

| 篇 | 第 1 輪問題 | 類型 |
|---|---|---|
| （第 1 次 lint，3 篇合計） | 9 | 找不到來源、講反、語氣、個人經驗泛化 |
| boca-japan-entry | 2＋1 | 語氣、N1 資訊滲入 |
| funjapan-visit-japan-web | 1 | N1 資訊滲入 |
| jnto-budget-guide | 1 | 範圍擴大 |
| gotokyo-accommodations | 1 | 漏標日期 |
| boca-japan-entry-main | 1 | N1 資訊滲入 |
| gotokyo-haneda-airport | 1 | 引文空格 |
