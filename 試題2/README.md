# 試題 2：負向測試

驗證 [衡好選智能健檢預約平台](https://bookinghub.cathay-hcm.com.tw/) 預約流程

「首頁(第一次來) → 檢查地點 → 基本資料 → 方案 → 加選項目 → 確認項目」

在三項健康背景問卷皆填「以下皆無」時，加選頁面「不應」出現與病史相關聯的檢查項目。

## 環境需求

- Python 3.10+（開發時使用 3.13）
- 需要網路連線（測試會連到正式的 bookinghub.cathay-hcm.com.tw 網站）

## 安裝步驟

```bash
cd 試題2
pip install -r requirements.txt
python -m playwright install chromium
```

## 執行方式

```bash
python -m pytest test_negative_flow.py -v --html=report.html --self-contained-html
```

- 預設以無頭模式（headless）執行；加上 `--headed` 可實際觀察瀏覽器操作過程。
- 執行完成後，開啟同資料夾下的 `report.html` 即為驗證報告。

## 檔案結構

```
試題2/
├── requirements.txt          # 套件需求
├── conftest.py                # 共用 fixture：啟動瀏覽器分頁、包裝成 BookingFlowPage
├── pages/
│   └── booking_flow_page.py   # Page Object，與試題1內容相同（共用同一套操作邏輯）
├── test_negative_flow.py      # 測試案例本體
└── report.html                # 執行後產生的 pytest-html 報告
```

## 測試涵蓋的驗證點

1. 個人病史、家族病史、個人身體狀況皆勾選「以下皆無」，並成功走到方案頁面、
   選擇「安心專屬型」方案
2. 加選頁面不應出現「密閉式純音聽力檢查」（因為未勾選會觸發此建議的「中耳炎」）
