import unittest
from unittest import mock

from dashboardHelper import economySection as es

# [How To Use]
# Terminal : python -m unittest test_economySection


def _cat(name, budget):
    return {'name': name, 'effectiveBudget': budget}


# 9 月預算快照的實際分類順序(擷取收入區段前後)
SEPTEMBER_CATEGORIES = [
    _cat('待產&月中', 0),
    _cat('每月固定支出', 97256),
    _cat('每年特殊總支出', 240805),
    _cat('收入Memo', 0),
    _cat('項目', 0),
    _cat('生生收入', 200677),
    _cat('老婆收入', 66349),
    _cat('育兒補助', 0),
    _cat('租屋補助', 5600),
    _cat('老婆賣機車', 10000),
    _cat('每月固定收入', 102600),
    _cat('每年特殊總收入', 418526),
]


class IncomeBreakdownTestCase(unittest.TestCase):
    def test_extra_income_row_between_markers_is_counted(self):
        breakdown = es._income_breakdown(SEPTEMBER_CATEGORIES, [], 9)
        totals = {item['name']: item['total'] for item in breakdown}
        self.assertEqual(totals.get('老婆賣機車'), 10000)
        self.assertEqual(sum(totals.values()), 282626)

    def test_fixed_incomes_keep_order_and_extras_follow(self):
        breakdown = es._income_breakdown(SEPTEMBER_CATEGORIES, [], 9)
        self.assertEqual([item['name'] for item in breakdown],
                         ['生生收入', '老婆收入', '租屋補助', '育兒補助', '老婆賣機車'])

    def test_zero_extra_rows_and_summary_rows_are_excluded(self):
        names = [item['name'] for item in es._income_breakdown(SEPTEMBER_CATEGORIES, [], 9)]
        for excluded in ('收入Memo', '項目', '每月固定收入', '每年特殊總收入', '每年特殊總支出'):
            self.assertNotIn(excluded, names)

    def test_fixed_income_with_zero_budget_still_listed(self):
        names = [item['name'] for item in es._income_breakdown(SEPTEMBER_CATEGORIES, [], 9)]
        self.assertIn('育兒補助', names)

    def test_without_income_marker_only_fixed_incomes_counted(self):
        categories = [_cat('生生收入', 53000), _cat('外食餐費', 14000)]
        breakdown = es._income_breakdown(categories, [], 9)
        self.assertEqual(sum(item['total'] for item in breakdown), 53000)

    def test_specials_of_the_month_are_attached(self):
        schedule = [
            {'name': '老婆收入', 'specialMonth': 9, 'specialItem': '中秋禮金半薪', 'specialAmount': 22349},
            {'name': '老婆收入', 'specialMonth': 2, 'specialItem': '年終獎金全薪', 'specialAmount': 44000},
        ]
        breakdown = es._income_breakdown(SEPTEMBER_CATEGORIES, schedule, 9)
        wife = next(item for item in breakdown if item['name'] == '老婆收入')
        self.assertEqual([s['specialItem'] for s in wife['specials']], ['中秋禮金半薪'])


class GenerateHtmlFallbackTestCase(unittest.TestCase):
    def setUp(self):
        es._last_success = None

    def tearDown(self):
        es._last_success = None

    def test_failure_without_previous_success_shows_error(self):
        with mock.patch.object(es, '_generate_html_inner', side_effect=Exception('Read timed out')):
            html = es.generate_html('url')
        self.assertIn('資料載入失敗', html)
        self.assertIn('Read timed out', html)

    def test_failure_after_success_shows_last_result_with_notice(self):
        with mock.patch.object(es, '_generate_html_inner', return_value='<p>九月資料</p>'):
            es.generate_html('url')
        with mock.patch.object(es, '_generate_html_inner', side_effect=Exception('Read timed out')):
            html = es.generate_html('url')
        self.assertIn('<p>九月資料</p>', html)
        self.assertIn('暫時無法取得最新資料', html)
        self.assertNotIn('資料載入失敗', html)

    def test_success_returns_fresh_result_without_notice(self):
        with mock.patch.object(es, '_generate_html_inner', return_value='<p>新資料</p>'):
            html = es.generate_html('url')
        self.assertEqual(html, '<p>新資料</p>')


if __name__ == '__main__':
    unittest.main()
