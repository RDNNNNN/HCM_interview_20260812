"""
共用 pytest fixture。

`browser` fixture 由 pytest-playwright 套件提供，作用範圍是整個測試 session
（瀏覽器只會啟動一次）。

這裡自訂的 `flow` fixture 是 module 範圍：同一個測試檔案（同一題）內的所有測試
案例，會共用同一個瀏覽器分頁與同一個 BookingFlowPage 實例，因此可以把「首頁
第一次來 -> 檢查地點 -> 基本資料 -> 方案 -> 加選項目 -> 確認項目」拆成多個獨立
的 test_xxx 案例（每個驗證點各自在報告中顯示成功/失敗），而不需要每個案例都
重新跑一次前面的步驟。不同測試檔案（試題）之間則會各自建立新的分頁，互不影響。
"""

import pytest

from pages.booking_flow_page import BookingFlowPage


@pytest.fixture(scope="module")
def flow(browser):
    context = browser.new_context(viewport={"width": 1280, "height": 1600})
    page = context.new_page()
    yield BookingFlowPage(page)
    context.close()
