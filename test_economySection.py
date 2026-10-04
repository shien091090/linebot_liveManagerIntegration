import os
import tempfile
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


class CachedGenerateHtmlTestCase(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.path_patch = mock.patch.object(es, 'CACHE_PATH', os.path.join(self.tmp.name, 'cache.json'))
        self.path_patch.start()

    def tearDown(self):
        self.path_patch.stop()
        self.tmp.cleanup()

    def test_no_cache_and_fetch_fails_shows_error(self):
        with mock.patch.object(es, '_generate_html_inner', side_effect=Exception('Read timed out')):
            html = es.generate_html('url')
        self.assertIn('資料載入失敗', html)
        self.assertIn('Read timed out', html)

    def test_no_cache_fetches_now_and_shows_data_time(self):
        with mock.patch.object(es, '_generate_html_inner', return_value='<p>新資料</p>'):
            html = es.generate_html('url')
        self.assertIn('<p>新資料</p>', html)
        self.assertIn('資料時間', html)

    def test_cached_result_is_served_without_fetching(self):
        with mock.patch.object(es, '_generate_html_inner', return_value='<p>九月資料</p>'):
            es.refresh_cache('url')
        with mock.patch.object(es, '_generate_html_inner', side_effect=AssertionError('不該即時抓')):
            html = es.generate_html('url')
        self.assertIn('<p>九月資料</p>', html)
        self.assertIn('資料時間', html)

    def test_refresh_replaces_cached_result(self):
        with mock.patch.object(es, '_generate_html_inner', return_value='<p>舊</p>'):
            es.refresh_cache('url')
        with mock.patch.object(es, '_generate_html_inner', return_value='<p>新</p>'):
            es.refresh_cache('url')
        self.assertIn('<p>新</p>', es.generate_html('url'))

    def test_failed_refresh_keeps_previous_result(self):
        with mock.patch.object(es, '_generate_html_inner', return_value='<p>舊</p>'):
            es.refresh_cache('url')
        with mock.patch.object(es, '_generate_html_inner', side_effect=Exception('Read timed out')):
            with self.assertRaises(Exception):
                es.refresh_cache('url')
        self.assertIn('<p>舊</p>', es.generate_html('url'))

    def test_cache_is_stale_only_after_interval(self):
        self.assertTrue(es._is_cache_stale())
        with mock.patch.object(es, '_generate_html_inner', return_value='<p>x</p>'):
            es.refresh_cache('url')
        self.assertFalse(es._is_cache_stale())


if __name__ == '__main__':
    unittest.main()
