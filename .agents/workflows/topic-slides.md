# Workflow：主題 → 教學 HTML 簡報（graph 版）

觸發：使用者說「做簡報」（或 `/topic-slides`）。主題固定為「第一次自由行怎麼規劃？——以東京為例」，對象是沒有自助旅行經驗的人。
所有中間產物都是 `slides/` 底下的檔案，每一關都能單獨打開、放進 git、單獨重跑。

```
[G1 檢索 wiki] ─→ {覆蓋率關卡} ─否→ 停下，回 N1 補來源
       │是
       ▼
[G2 證據卡 cards/*.md]（每篇來源一張，可平行）
       ▼
[G3 大綱 outline.md] ─→ 👤 使用者確認 ─退回→ 改大綱 / 回 G1 補檢索
       ▼
[G4 逐頁稿 drafts/NN.md] ⇄ {忠實度關卡：check.py + AI 審查}  錯→只修那一頁（≤2 輪）；卡片本身錯→回 G2 重抽那張
       ▼
[G5 渲染 deck.html] ⇄ {渲染關卡：render_check.py}  字太多→回 G4 縮短那一頁（≤2 輪）
       ▼
[G6 交件 report.md]
```

## 每一關只能看什麼、不能做什麼

| 節點 | 只能看 | 產出 | 不能做 |
|---|---|---|---|
| G1 檢索 | `wiki/index.md` → 相關 wiki 頁 | `slides/sources.md`：本簡報要用的 wiki 頁清單、每頁一句用途 | 讀 raw、上網、用模型自己的知識 |
| 覆蓋率關卡 | `sources.md` | 判定 | 相關 wiki 頁少於 3 頁，或「預算／入境／交通／住宿／行程」任一步驟沒有對應頁 → 停下 |
| G2 證據卡 | **一篇**來源的 `wiki/sources/<slug>.md`，以及 wiki 中引用該來源的句子 | `slides/cards/<slug>.md` | 混入其他來源；改寫掉原本的標示（個人經驗、資訊日期、原文無日期、整理者推論、⚠️） |
| G3 大綱 | `sources.md`、全部 cards | `slides/outline.md` | 引用卡片以外的內容 |
| G4 逐頁稿 | `outline.md` 中這一頁的段落＋它列出的卡片 | `slides/drafts/NN.md` | 引用該頁卡片以外的內容 |
| G5 渲染 | 已通過的 drafts | `slides/deck.html` | **改任何一個字**（排版時想順手改句子？不行，退回 G4） |
| 檢查關卡 | 成品＋它的來源 | `reviews/` 紀錄 | 自己動手改成品 |

## 檔案格式

**證據卡** `slides/cards/<slug>.md`：每條主張一行、固定編號，供逐頁稿引用。
```markdown
---
source: <slug>
---
- C1：主張內容（保留原標示，例如「資訊日期 2024-12」「個人經驗」）〔wiki: concepts/transit-passes.md〕
```

**大綱** `slides/outline.md`：每頁一個 `## NN 標題`，下面列 `卡片：slug#C1, slug#C3` 與一句教學目的。

**逐頁稿** `slides/drafts/NN.md`：
```markdown
---
slide: 03
title: 頁標題
cards: [jnto-useful-tickets-tokyo#C2, ...]
---
- 要點文字〔jnto-useful-tickets-tokyo#C2〕
- 自己的串場或歸納（整理者推論）
```
每個要點都要有〔卡片編號〕或標「（整理者推論）」；要點裡的數字必須出現在它引用的卡片中。

**簡報** `slides/deck.html`：單一 HTML 檔；每頁 `<section data-draft="03" data-wiki="concepts/x.md ...">`，頁尾小字顯示出處；方向鍵翻頁，手機寬度可讀。

## 關卡規格

- **程式檢查** `python tools/check.py`：卡片引用的 wiki 頁存在；逐頁稿引用的卡片編號存在；數字找得到；大綱、逐頁稿、簡報頁數一致且 **8–15 頁**；每頁有出處；**覆蓋率**（哪張卡片沒被任何一頁用到）。
- **渲染檢查** `python tools/render_check.py`：用 Edge 無頭模式以 1280×720 與 390×844 逐頁開啟，回報溢出的頁並存截圖到 `slides/screenshots/`。
- **AI 審查**（新 subagent，只給逐頁稿＋它引用的卡片）：忠實度（有沒有講反、語氣改強、個人經驗被寫成通則）與初學者可讀性；G6 前再做一次**覆蓋率審查**（給 deck＋sources.md，看有無重要內容沒用到）。

## 剎車

- G4、G5 每一頁最多修 2 輪；整體最多 3 輪，超過就停下回報。
- 每一輪**只修檢查報告列出的問題**，其他頁不動。
- 退回路線（錯在哪一關就回哪一關）：某頁講錯 → 只修那一頁；卡片本身錯 → 回 G2 重抽那張；字太多 → 回 G4 縮短；大綱缺子題 → 回 G1 補檢索。

## 交件 `slides/report.md`

列出每一關的檢查結果、跑了幾輪、退回過哪裡，以及對照組（B0）的比較。

## 對照組 B0（一句話生成）

在 G1 之前，用新的 subagent 只下一句提示：「根據 wiki/ 的內容，做一份給第一次自由行新手、以東京為例的教學 HTML 簡報，存成 slides/baseline/deck.html」。不經任何關卡，事後用同一套檢查跑一次，結果記入 `reviews/` 作為對照。
