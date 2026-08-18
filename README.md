# HCM_interview_20260812

國泰健康管理 技術研發科 TQA 試題作答專案。使用 **Python + Playwright + pytest**
對 https://bookinghub.cathay-hcm.com.tw/ 健檢預約平台進行端對端 UI 自動化驗證。

## 專案結構
```
HCM_interview_20260812/
├── README.md      # 本檔案：整體說明
├── 試題1/          # 正向測試（詳見 試題1/README.md）
└── 試題2/          # 負向測試（詳見 試題2/README.md）
```

兩題各自獨立成一個資料夾，各自有完整的 `requirements.txt`、Page Object
（`pages/booking_flow_page.py`）與測試案例，可以分別進入資料夾安裝、執行，
不需要共用虛擬環境或跨資料夾設定。

## 快速開始
```bash
# 試題1（正向測試）
cd 試題1
pip install -r requirements.txt
python -m playwright install chromium
python -m pytest test_positive_flow.py -v --html=report.html --self-contained-html

# 試題2（負向測試）
cd ../試題2
pip install -r requirements.txt
python -m playwright install chromium
python -m pytest test_negative_flow.py -v --html=report.html --self-contained-html
```

每題執行完成後，於各自資料夾下開啟 `report.html` 即為 pytest-html 產出的驗證報告。

## 技術說明
- **框架**：Playwright（瀏覽器自動化）+ pytest（測試執行與斷言）+
  pytest-playwright（提供 `browser`/`page` fixture）+ pytest-html（產出 HTML 報告）
- **架構**：採用 Page Object Model，兩題共用同一份 `pages/booking_flow_page.py`
  （內容相同、各自一份，讓兩個資料夾各自獨立可執行），將畫面操作（點選檢查地點、
  填寫基本資料、勾選健康背景問卷、選擇方案、加選項目等）封裝成語意化方法，
  測試案例本身只描述「驗證什麼」，不重複寫選取器邏輯
- 每個驗證點各自是一個獨立的 pytest 測試案例（同檔案內按編號循序執行、共用同一
  個瀏覽器分頁以維持預約流程的狀態），方便從報告直接看出是哪一個步驟失敗
- 測試直接對正式環境（正式網址）執行，因此需要網路連線；頁面上的價格、方案內容
  等由後端動態計算，測試斷言鎖定在「特定文字/項目是否出現」而非寫死的金額

## 已知限制
- 測試依賴外部正式網站的即時回應與畫面文字，若網站文案、UI 結構或健檢方案內容
  調整，對應的選取器或斷言文字可能需要同步更新
- 目前僅涵蓋 PDF 試題所要求的驗證點，未涵蓋其餘畫面（如「曾經來過，直接預約」
  流程、企業員工方案等）
