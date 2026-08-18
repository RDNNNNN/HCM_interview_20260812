"""
第二題：負向測試

驗證情境：首頁(第一次來) -> 檢查地點 -> 基本資料 -> 方案 -> 加選項目 -> 確認項目
    1. 個人病史、家族病史、個人身體狀況皆勾選「以下皆無」
    2. 驗證加選頁面「並無」出現「密閉式純音聽力檢查」

與第一題共用同一份 pages/booking_flow_page.py（Page Object 邏輯完全相同），
差異只在於問卷填寫的選項，以及最後驗證方向是「不應該出現」而非「應該出現」。
"""

TARGET_ITEM = "密閉式純音聽力檢查"
TARGET_PLAN = "安心專屬型"


class TestNegativeFlow:
    def test_01_start_and_fill_history_with_no_history(self, flow):
        """步驟 1：個人病史、家族病史、個人身體狀況皆選擇「以下皆無」。"""
        flow.open_home()
        flow.start_as_first_time_visitor()
        flow.select_location("敦南中心")
        flow.fill_basic_info(gender="男性", birthday="1990/01/01")

        flow.answer_personal_history(["以下皆無"])
        flow.answer_family_history(["以下皆無"])
        flow.answer_symptoms(["以下皆無"])

    def test_02_select_plan(self, flow):
        """走到加選頁面前，選擇「安心專屬型」方案（與第一題相同方案，僅病史不同）。"""
        flow.select_plan(TARGET_PLAN)

    def test_03_addon_page_does_not_show_target_item(self, flow):
        """步驟 2：加選頁面不應出現「密閉式純音聽力檢查」
        （因為未勾選中耳炎，系統不會因此推薦此項目）。
        """
        assert not flow.has_addon_item(TARGET_ITEM), (
            f"未勾選「中耳炎」時，加選頁面不應該出現「{TARGET_ITEM}」，但卻找到了"
        )
