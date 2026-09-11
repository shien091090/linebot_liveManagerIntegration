import unittest
from datetime import date

from dashboardHelper import stomachSection as ss

# [How To Use]
# Terminal : python -m unittest test_stomachSection


class ParseLevelTestCase(unittest.TestCase):
    def test_all_five_options_map_in_order(self):
        self.assertEqual(ss._parse_level('沒感覺'), 0)
        self.assertEqual(ss._parse_level('幾乎沒感覺'), 1)
        self.assertEqual(ss._parse_level('輕微違和感'), 2)
        self.assertEqual(ss._parse_level('有點不舒服'), 3)
        self.assertEqual(ss._parse_level('非常不舒服'), 4)

    def test_surrounding_blank_is_tolerated(self):
        self.assertEqual(ss._parse_level('  沒感覺 '), 0)

    def test_unknown_text_returns_none(self):
        self.assertIsNone(ss._parse_level('還好'))
        self.assertIsNone(ss._parse_level(''))
        self.assertIsNone(ss._parse_level(None))


class ParseWeightTestCase(unittest.TestCase):
    def test_plain_number_and_numeric_string(self):
        self.assertEqual(ss._parse_weight(250), 250.0)
        self.assertEqual(ss._parse_weight('250'), 250.0)
        self.assertEqual(ss._parse_weight('250.5'), 250.5)

    def test_unit_suffix_is_stripped(self):
        # 表上實際存的是「42 g」這種帶單位的值
        self.assertEqual(ss._parse_weight('42 g'), 42.0)
        self.assertEqual(ss._parse_weight('150g'), 150.0)
        self.assertEqual(ss._parse_weight(' 108 公克 '), 108.0)

    def test_non_numeric_returns_none(self):
        self.assertIsNone(ss._parse_weight('一碗'))
        self.assertIsNone(ss._parse_weight(''))
        self.assertIsNone(ss._parse_weight(None))

    def test_non_positive_returns_none(self):
        self.assertIsNone(ss._parse_weight(0))
        self.assertIsNone(ss._parse_weight(-100))
        self.assertIsNone(ss._parse_weight('0 g'))


class ParseDateTestCase(unittest.TestCase):
    def test_plain_date(self):
        self.assertEqual(ss._parse_date('2026/07/02'), date(2026, 7, 2))

    def test_weekday_suffix_is_tolerated(self):
        # 表上實際存的是「2026/07/02 週四」
        self.assertEqual(ss._parse_date('2026/07/02 週四'), date(2026, 7, 2))
        self.assertEqual(ss._parse_date(' 2026/7/2 週四 '), date(2026, 7, 2))

    def test_unusable_returns_none(self):
        self.assertIsNone(ss._parse_date(''))
        self.assertIsNone(ss._parse_date(None))
        self.assertIsNone(ss._parse_date('2026-07-02'))
        self.assertIsNone(ss._parse_date('週四'))


class ScoreMealTestCase(unittest.TestCase):
    """分數 = 100 x 舒適度 x 食量係數 - 8 x 惡化，只有下限 0、不封頂
       舒適度   = (4 - 餐後) / 4
       惡化     = max(0, 餐後 - 餐前)
       食量係數 = 重量 / 同餐別基準重量（不設上下限）"""

    def test_at_base_weight_with_no_symptom_scores_one_hundred(self):
        # 吃到平常份量且完全沒感覺 = 參考點 100
        self.assertAlmostEqual(
            ss._score_meal(300, '沒感覺', '沒感覺', 300), 100.0)

    def test_eating_more_scores_higher_even_when_both_feel_nothing(self):
        base = 212.5
        normal = ss._score_meal(212.5, '沒感覺', '沒感覺', base)
        more = ss._score_meal(306, '沒感覺', '沒感覺', base)
        self.assertGreater(more, normal)
        self.assertAlmostEqual(more, 100 * (306 / 212.5))

    def test_score_is_not_capped_at_one_hundred(self):
        self.assertAlmostEqual(
            ss._score_meal(1000, '沒感覺', '沒感覺', 300), 100 * (1000 / 300))

    def test_eating_less_scores_lower(self):
        self.assertAlmostEqual(
            ss._score_meal(100, '沒感覺', '沒感覺', 300), 100 * (100 / 300))

    def test_worked_example_from_real_data(self):
        # 7/02 晚餐 108g, 有點不舒服 -> 輕微違和感, 晚餐基準 212.5g
        # 舒適度 (4-2)/4 = 0.5, 惡化 0, 係數 108/212.5
        self.assertAlmostEqual(
            ss._score_meal(108, '有點不舒服', '輕微違和感', 212.5),
            100 * 0.5 * (108 / 212.5))

    def test_worsening_is_penalised(self):
        # 係數 1.0, 餐後3 -> 舒適度0.25, 惡化1 -> 25 - 8 = 17
        self.assertAlmostEqual(
            ss._score_meal(300, '輕微違和感', '有點不舒服', 300), 17.0)

    def test_improvement_is_not_penalised(self):
        # 餐後比餐前好 -> 惡化 = 0，不倒扣
        self.assertAlmostEqual(
            ss._score_meal(300, '有點不舒服', '幾乎沒感覺', 300), 75.0)

    def test_score_floored_at_zero(self):
        # 舒適度0, 惡化4 -> 0 - 32 -> 下限 0
        self.assertAlmostEqual(
            ss._score_meal(300, '沒感覺', '非常不舒服', 300), 0.0)

    def test_unusable_fields_return_none(self):
        self.assertIsNone(ss._score_meal('一碗', '沒感覺', '沒感覺', 300))
        self.assertIsNone(ss._score_meal(300, '還好', '沒感覺', 300))
        self.assertIsNone(ss._score_meal(300, '沒感覺', '還好', 300))
        self.assertIsNone(ss._score_meal(300, '沒感覺', '沒感覺', None))


class BaseWeightsTestCase(unittest.TestCase):
    """基準重量以「同餐別」分別計算，避免早餐永遠被當成吃太少"""

    def _record(self, meal_type, weight):
        return {'mealType': meal_type, 'weight': weight}

    def test_median_per_meal_type(self):
        records = [
            self._record('早餐', 60), self._record('早餐', 80),
            self._record('早餐', 100),
            self._record('晚餐', 200), self._record('晚餐', 300),
        ]
        bases = ss._base_weights(records)
        self.assertEqual(bases['早餐'], 80)
        self.assertEqual(bases['晚餐'], 250)

    def test_dirty_weights_are_ignored(self):
        records = [
            self._record('早餐', 60), self._record('早餐', '一碗'),
            self._record('早餐', ''), self._record('早餐', 100),
        ]
        self.assertEqual(ss._base_weights(records)['早餐'], 80)

    def test_meal_type_without_usable_weight_is_absent(self):
        records = [self._record('早餐', '一碗')]
        self.assertNotIn('早餐', ss._base_weights(records))

    def test_empty_records_give_empty_bases(self):
        self.assertEqual(ss._base_weights([]), {})


class DailyScoresTestCase(unittest.TestCase):
    def _record(self, d, meal_type, weight, before, after):
        return {'date': d, 'mealType': meal_type, 'weight': weight,
                'before': before, 'after': after}

    def test_meals_on_same_day_are_averaged(self):
        records = [
            self._record('2026/09/01 週二', '早餐', 100, '沒感覺', '沒感覺'),
            self._record('2026/09/01 週二', '早餐', 100, '沒感覺', '非常不舒服'),
        ]
        # 早餐基準 = 100 -> 係數1.0 -> 100 與 0 平均
        self.assertEqual(ss._daily_scores(records), [(date(2026, 9, 1), 50.0)])

    def test_each_meal_type_is_scored_against_its_own_baseline(self):
        # 早餐吃到早餐的基準、晚餐吃到晚餐的基準，兩者都該拿 100
        records = [
            self._record('2026/09/01', '早餐', 80, '沒感覺', '沒感覺'),
            self._record('2026/09/02', '早餐', 80, '沒感覺', '沒感覺'),
            self._record('2026/09/01', '晚餐', 220, '沒感覺', '沒感覺'),
            self._record('2026/09/02', '晚餐', 220, '沒感覺', '沒感覺'),
        ]
        for _, score in ss._daily_scores(records):
            self.assertAlmostEqual(score, 100.0)

    def test_results_are_sorted_by_date(self):
        records = [
            self._record('2026/09/03', '早餐', 100, '沒感覺', '沒感覺'),
            self._record('2026/09/01', '早餐', 100, '沒感覺', '沒感覺'),
        ]
        self.assertEqual([d for d, _ in ss._daily_scores(records)],
                         [date(2026, 9, 1), date(2026, 9, 3)])

    def test_single_meal_day_still_produces_a_point(self):
        records = [self._record('2026/09/01', '早餐', 100, '沒感覺', '沒感覺')]
        self.assertEqual(len(ss._daily_scores(records)), 1)

    def test_rows_with_unusable_fields_are_skipped(self):
        records = [
            self._record('2026/09/01 週二', '早餐', 100, '沒感覺', '沒感覺'),
            self._record('2026/09/01 週二', '早餐', 100, '沒感覺', '還好'),
            self._record('2026/09/01 週二', '早餐', '一碗', '沒感覺', '沒感覺'),
            self._record('', '早餐', 100, '沒感覺', '沒感覺'),
            self._record('2026-09-01', '早餐', 100, '沒感覺', '沒感覺'),
        ]
        self.assertEqual(ss._daily_scores(records), [(date(2026, 9, 1), 100.0)])

    def test_returns_empty_when_nothing_usable(self):
        self.assertEqual(ss._daily_scores([]), [])
        self.assertEqual(
            ss._daily_scores([self._record('2026/09/01', '早餐', '一碗',
                                           '沒感覺', '沒感覺')]),
            [])


if __name__ == '__main__':
    unittest.main()
