# 試題 1：正向測試

驗證 https://bookinghub.cathay-hcm.com.tw/ 預約流程

「首頁(第一次來) → 檢查地點 → 基本資料 → 方案 → 加選項目 → 確認項目」

在指定病史/方案輸入下，畫面是否出現對應選項。共 5 個獨立驗證點，對應 pytest 的 5 個測試案例（依編號順序執行）。

## 環境需求

- Python 3.10+（開發時使用 3.13）
- 需要網路連線（測試會連到正式的 bookinghub.cathay-hcm.com.tw 網站）

## 安裝步驟

```bash
cd 試題1
pip install -r requirements.txt
python -m playwright install chromium
```

## 執行方式

```bash
python -m pytest test_positive_flow.py -v --html=report.html --self-contained-html
```

- 預設以無頭模式（headless）執行；若想實際看到瀏覽器操作過程方便除錯，加上
  `--headed` 參數即可：
  `python -m pytest test_positive_flow.py --headed`
- 執行完成後，開啟同資料夾下的 `report.html` 即為驗證報告，會列出 5 個驗證點
  各自的通過/失敗狀態。

## 檔案結構

```
試題1/
├── requirements.txt          # 套件需求
├── conftest.py                # 共用 fixture：啟動瀏覽器分頁、包裝成 BookingFlowPage
├── pages/
│   └── booking_flow_page.py   # Page Object：封裝畫面操作與驗證方法
├── test_positive_flow.py      # 測試案例本體
└── report.html                # 執行後產生的 pytest-html 報告
```

## 測試涵蓋的驗證點

1. 個人病史勾選「中耳炎」，家族病史、個人身體狀況皆勾選「以下皆無」，並成功走到方案頁面
2. 方案選擇「安心專屬型」前，驗證卡片上有出現「個人病史」標籤
3. 加選頁面應出現「密閉式純音聽力檢查」
4. 勾選並送出該加選項目後，應跳出「已為您調整檢查項目」提示視窗
5. 關閉提示視窗後，確認檢查內容頁面的加選項目清單應包含「密閉式純音聽力檢查」
