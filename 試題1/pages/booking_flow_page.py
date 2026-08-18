"""
Page Object：封裝「衡好選智能健檢預約平台」從首頁到確認檢查內容的操作流程。

畫面流程（breadcrumb 五步驟）：
    選擇檢查地點 -> 填寫資料 -> 選擇健檢方案 -> 添加檢查項目 -> 確認檢查內容

其中「填寫資料」實際上包含 4 個子頁面：
    基本資料(性別/生日) -> 個人病史(1/3) -> 家族病史(2/3) -> 個人身體狀況(3/3)

所有選取器皆為對照 https://bookinghub.cathay-hcm.com.tw/ 實際畫面確認過的真實結構
（網站使用 Angular Material，多數勾選為 <mat-checkbox>，多數按鈕為文字按鈕，
因此優先以「可見文字」定位，穩定性較 CSS class 高）。
"""

from __future__ import annotations

from playwright.sync_api import Locator, Page, TimeoutError as PlaywrightTimeoutError, expect

BASE_URL = "https://bookinghub.cathay-hcm.com.tw/"


class BookingFlowPage:
    def __init__(self, page: Page):
        self.page = page

    # ---------------------------------------------------------------
    # 首頁
    # ---------------------------------------------------------------
    def open_home(self) -> None:
        """開啟首頁，並等待畫面主要內容載入完成。"""
        self.page.goto(BASE_URL, wait_until="networkidle")
        expect(self.page.get_by_text("第一次來，了解方案", exact=False).first).to_be_visible()

    def start_as_first_time_visitor(self) -> None:
        """點擊「第一次來，了解方案 →」，進入預約流程第一步（選擇檢查地點）。"""
        self.page.get_by_text("第一次來，了解方案", exact=False).first.click()
        self.page.wait_for_load_state("networkidle")
        expect(self.page).to_have_url(f"{BASE_URL}healthcheck/reserve/location")

    # ---------------------------------------------------------------
    # 檢查地點
    # ---------------------------------------------------------------
    def select_location(self, location_name: str = "敦南中心") -> None:
        """在「請選擇檢查地點」頁面點選指定中心，預設為敦南中心。"""
        expect(self.page.get_by_text("請選擇檢查地點")).to_be_visible()
        self.page.get_by_text(location_name, exact=False).first.click()
        self.page.wait_for_load_state("networkidle")
        expect(self.page).to_have_url(f"{BASE_URL}healthcheck/reserve/personalinfo")

    # ---------------------------------------------------------------
    # 基本資料
    # ---------------------------------------------------------------
    def fill_basic_info(self, gender: str = "男性", birthday: str = "1990/01/01") -> None:
        """填寫生理性別與生日，並點擊下一步進入個人病史問卷。"""
        self.page.get_by_text(gender, exact=True).first.click()

        date_input = self.page.locator("input[placeholder='YYYY/MM/DD']").first
        date_input.click()
        date_input.fill(birthday)
        self.page.keyboard.press("Escape")  # 收起日期選擇器

        self._click_next()
        expect(self.page).to_have_url(f"{BASE_URL}healthcheck/reserve/personalhistory")

    # ---------------------------------------------------------------
    # 健康背景 (1/3) 個人病史 / (2/3) 家族病史 / (3/3) 個人身體狀況
    # 三頁的勾選 UI 完全相同（皆為 mat-checkbox 清單 + 上一步/下一步），
    # 因此共用同一個私有方法即可。
    # ---------------------------------------------------------------
    def _check_options(self, options: list[str]) -> None:
        for option in options:
            self.page.locator("mat-checkbox", has_text=option).first.click()

    def answer_personal_history(self, options: list[str]) -> None:
        """健康背景 1/3：個人病史。options 例如 ["中耳炎"] 或 ["以下皆無"]。"""
        expect(self.page.get_by_text("健康背景(1/3)")).to_be_visible()
        self._check_options(options)
        self._click_next()
        expect(self.page).to_have_url(f"{BASE_URL}healthcheck/reserve/familyhistory")

    def answer_family_history(self, options: list[str]) -> None:
        """健康背景 2/3：家族病史。"""
        expect(self.page.get_by_text("健康背景(2/3)")).to_be_visible()
        self._check_options(options)
        self._click_next()
        expect(self.page).to_have_url(f"{BASE_URL}healthcheck/reserve/symptoms")

    def answer_symptoms(self, options: list[str]) -> None:
        """健康背景 3/3：個人身體狀況（自覺症狀）。填完後會進入「方案演算中」畫面。"""
        expect(self.page.get_by_text("健康背景(3/3)")).to_be_visible()
        self._check_options(options)
        self._click_next()
        self._wait_for_plan_calculation()

    def _wait_for_plan_calculation(self, timeout_ms: int = 20000) -> None:
        """健康背景填寫完成後會先進入「方案演算中」的過場頁，等待其導向方案頁。"""
        self.page.wait_for_url(
            f"{BASE_URL}healthcheck/reserve/personalplan", timeout=timeout_ms
        )
        self.page.wait_for_load_state("networkidle")

    # ---------------------------------------------------------------
    # 選擇健檢方案
    # ---------------------------------------------------------------
    def _plan_card(self, plan_name: str):
        """回傳指定方案卡片的容器 locator（範圍限定在該卡片內，避免跨卡片誤判）。"""
        heading = self.page.get_by_text(plan_name, exact=True).first
        return heading.locator("xpath=ancestor::div[contains(@class,'reserve-plan-card')][1]")

    def plan_card_has_personal_history_tag(self, plan_name: str = "安心專屬型") -> bool:
        """驗證指定方案卡片內，是否出現「個人病史」標籤。"""
        card = self._plan_card(plan_name)
        return self._wait_visible(card.get_by_text("個人病史", exact=True))

    def select_plan(self, plan_name: str = "安心專屬型") -> None:
        """點選指定方案的「選此方案」按鈕，進入添加檢查項目頁面。"""
        card = self._plan_card(plan_name)
        select_button = card.get_by_text("選此方案", exact=True)
        select_button.scroll_into_view_if_needed()
        # 頁面右下角有浮動小圖示偶爾會遮住按鈕，force=True 確保仍可點擊到目標按鈕本身
        select_button.click(force=True)
        self.page.wait_for_load_state("networkidle")
        expect(self.page).to_have_url(f"{BASE_URL}healthcheck/reserve/additem")
        # 加選項目清單為非同步渲染，等待搜尋框文字出現代表清單已經畫出，
        # 這樣後續「驗證某項目不存在」的檢查才不會因為清單還沒渲染完而誤判。
        expect(self.page.get_by_text("尋找檢查項目").first).to_be_visible()

    # ---------------------------------------------------------------
    # 添加檢查項目
    # ---------------------------------------------------------------
    def _addon_item_row(self, item_name: str):
        item_text = self.page.get_by_text(item_name, exact=True).first
        return item_text.locator("xpath=ancestor::div[contains(@class,'reserve-plan-card')][1]")

    def has_addon_item(self, item_name: str) -> bool:
        """驗證加選頁面是否有出現指定的檢查項目。"""
        # 加選頁項目清單為非同步渲染，用 _wait_visible 而非立即 count()，
        # 避免頁面剛切換、DOM 尚未畫出項目時就誤判為「不存在」。
        return self._wait_visible(self.page.get_by_text(item_name, exact=True))

    def select_addon_item(self, item_name: str) -> None:
        """勾選指定的加選檢查項目。"""
        row = self._addon_item_row(item_name)
        row.locator("mat-checkbox").first.click(force=True)

    def submit_addon_selection(self) -> None:
        """加選頁面點擊下一步，送出所選的加選項目，進入確認檢查內容頁面。"""
        self._click_next()
        expect(self.page).to_have_url(f"{BASE_URL}healthcheck/reserve/overview")

    # ---------------------------------------------------------------
    # 確認檢查內容（含「已為您調整檢查項目」提示視窗）
    # ---------------------------------------------------------------
    def adjustment_dialog_is_visible(self) -> bool:
        """驗證加選送出後，是否跳出「已為您調整檢查項目」提示視窗。"""
        return self._wait_visible(self.page.get_by_text("已為您調整檢查項目", exact=True))

    def dismiss_adjustment_dialog(self) -> None:
        """點擊提示視窗中的「我知道了」關閉視窗。"""
        self.page.get_by_role("button", name="我知道了").click()

    def overview_has_addon_item(self, item_name: str) -> bool:
        """驗證確認檢查內容頁面的「加選項目」清單是否包含指定項目。"""
        return self._wait_visible(self.page.get_by_text(item_name, exact=True))

    # ---------------------------------------------------------------
    # 共用小工具
    # ---------------------------------------------------------------
    def _click_next(self) -> None:
        self.page.get_by_role("button", name="下一步").click()
        self.page.wait_for_load_state("networkidle")

    def _wait_visible(self, locator: Locator, timeout_ms: int = 8000) -> bool:
        """對「畫面是否有出現某元素」做具備自動重試的等待，取代立即 count()。
        找不到時回傳 False（而不是丟例外），讓呼叫端能用一般 assert 檢查。
        """
        try:
            locator.first.wait_for(state="visible", timeout=timeout_ms)
            return True
        except PlaywrightTimeoutError:
            return False
