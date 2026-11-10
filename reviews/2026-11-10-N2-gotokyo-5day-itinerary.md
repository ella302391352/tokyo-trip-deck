# [N2] Ingest gotokyo-5day-itinerary 第 1 輪

- 日期：2026-11-10
- 檢查類型：人工（先討論、後生成）＋程式（check.py）
- 輸入：raw/papers/gotokyo-5day-itinerary.md
- 結果：通過（check.py 第 2 輪）

## 討論階段（使用者確認的事項）

- 重點 5 點：相近景點分組、至少 5 天、3 天選 Day 1/3/4、五天分區、住宿依目的與區域選
- 地點頁先做一頁總表 `places/tokyo-areas.md`，不拆成每區一頁
- 景點只寫一行，重點放在「怎麼分組」（簡報教的是規劃方法，不是景點導覽）

## 發現的問題

1. **原文內部矛盾**（來源本身）：3 天方案說涵蓋「東部、中部及南部」，但第 4 天被標為「西部」。→ 以 ⚠️ 標記保留兩種說法，不自行改正。
2. **check.py 誤判孤兒頁**（工具 bug，屬 N2 的檢查步驟）：第 1 輪回報 3 個錯誤（accommodation-area 孤兒頁、兩頁未列入 index），但實際上都有連結。原因是腳本邊讀邊判斷，按字母排序 `concepts/` 早於 `index.md`，判斷時後面的頁面還沒被讀到。空 wiki 與單頁測試都無法觸發此 bug。→ 改為先統計全部連結再判斷；用含孤兒頁的測試副本確認仍能抓到真正的孤兒頁。

## 處理方式

- 新增：sources/gotokyo-5day-itinerary、concepts/itinerary-planning、concepts/accommodation-area、places/tokyo-areas
- 更新：overview（行程、住宿、交通三步）、index
- 第 2 輪 check.py：0 錯誤、5 警告（3 頁含（待查）、2 篇 raw 無日期）

## 出錯源頭節點

- 問題 1：N1 取得的來源本身（無法修正，只能標記）
- 問題 2：N2（檢查工具）

## 是否要把檢查往前移

問題 2 說明「檢查工具本身也要被測試」：之後修改 check.py 時，要同時用「應該通過」的真實 wiki 和「應該失敗」的測試副本各跑一次。
