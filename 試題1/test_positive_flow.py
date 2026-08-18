"""
第一題：正向測試

驗證情境：首頁(第一次來) -> 檢查地點 -> 基本資料 -> 方案 -> 加選項目 -> 確認項目
    1. 個人病史勾選「中耳炎」，家族病史、個人身體狀況皆勾選「以下皆無」
    2. 方案選擇「安心專屬型」，並驗證是否出現「個人病史」標籤
    3. 驗證加選頁面出現「密閉式純音聽力檢查」
    4. 加選「密閉式純音聽力檢查」並送出，驗證是否出現調整檢查項目的提示視窗
    5. 點選「我知道了」，驗證加選項目是否出現「密閉式純音聽力檢查」

每個驗證點各自獨立成一個測試案例，執行順序由編號前綴 (test_01_xxx) 保證，
方便從 pytest-html 報告直接看出是「哪一個驗證點」失敗。
"""

TARGET_ITEM = "密閉式純音聽力檢查"
TARGET_PLAN = "安心專屬型"


class TestPositiveFlow:
    """
    使用 class 是為了讓同一組步驟（首頁 -> ... -> 加選項目）依序往下執行，
    而不必在每一個測試案例裡都重新跑一次前面的步驟；
    以 pytest 的執行順序（同檔案內由上到下）驅動同一個瀏覽器分頁。
    """

    def test_01_start_and_fill_history(self, flow):
        """步驟 1：走到加選頁面之前，填入個人病史=中耳炎、家族病史/身體狀況=以下皆無。"""
        flow.open_home()
        flow.start_as_first_time_visitor()
        flow.select_location("敦南中心")
        flow.fill_basic_info(gender="男性", birthday="1990/01/01")

        flow.answer_personal_history(["中耳炎"])
        flow.answer_family_history(["以下皆無"])
        flow.answer_symptoms(["以下皆無"])

        # 走到這裡代表成功抵達方案頁面（wait_for_url 已在 answer_symptoms 內完成驗證）

    def test_02_select_plan_shows_personal_history_tag(self, flow):
        """步驟 2：方案選「安心專屬型」前，先驗證卡片上有「個人病史」標籤，再點選此方案。"""
        assert flow.plan_card_has_personal_history_tag(TARGET_PLAN), (
            f"「{TARGET_PLAN}」方案卡片應該要出現「個人病史」標籤，但沒有找到"
        )
        flow.select_plan(TARGET_PLAN)

    def test_03_addon_page_shows_target_item(self, flow):
        """步驟 3：加選頁面應出現「密閉式純音聽力檢查」。"""
        assert flow.has_addon_item(TARGET_ITEM), (
            f"加選頁面應該要出現「{TARGET_ITEM}」，但沒有找到"
        )

    def test_04_submit_addon_shows_adjustment_dialog(self, flow):
        """步驟 4：勾選並送出加選項目後，應跳出「已為您調整檢查項目」提示視窗。"""
        flow.select_addon_item(TARGET_ITEM)
        flow.submit_addon_selection()
        assert flow.adjustment_dialog_is_visible(), (
            "送出加選項目後，應該要出現「已為您調整檢查項目」提示視窗"
        )

    def test_05_confirm_dialog_and_verify_overview(self, flow):
        """步驟 5：關閉提示視窗後，確認檢查內容頁面的加選項目應包含目標項目。"""
        flow.dismiss_adjustment_dialog()
        assert flow.overview_has_addon_item(TARGET_ITEM), (
            f"確認檢查內容頁面的加選項目清單應包含「{TARGET_ITEM}」，但沒有找到"
        )
