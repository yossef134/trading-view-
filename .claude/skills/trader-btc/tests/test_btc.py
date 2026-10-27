import importlib.util
import os
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from make_fixture import make  # noqa: E402

spec = importlib.util.spec_from_file_location("btc", os.path.join(os.path.dirname(HERE), "btc.py"))
btc = importlib.util.module_from_spec(spec)
spec.loader.exec_module(btc)

START = 1760000000 - 1760000000 % 3600


def bars_from(prices, start=START):
    """Hourly bars from (open, high, low, close) tuples."""
    return [{"t": start + 3600 * i, "o": o, "h": h, "l": l, "c": c, "v": 100.0}
            for i, (o, h, l, c) in enumerate(prices)]


class Check(unittest.TestCase):
    def flat(self, n, hi=101.0, lo=99.0):
        return [(100.0, hi, lo, 100.0)] * n

    def test_waiting_under_the_range_high(self):
        bars = bars_from(self.flat(30))
        now = START + 3600 * 30
        r = btc.evaluate(bars, "1h", now, lookback=24)
        self.assertEqual(r["status"], "waiting")
        self.assertEqual(r["level"], 101.0)

    def test_triggers_on_a_close_above_not_a_wick(self):
        wick = self.flat(29) + [(100.0, 105.0, 99.0, 100.5)]     # wick over, close under
        r = btc.evaluate(bars_from(wick), "1h", START + 3600 * 30, lookback=24)
        self.assertEqual(r["status"], "waiting")
        close = self.flat(29) + [(100.0, 103.0, 99.0, 102.0)]
        r = btc.evaluate(bars_from(close), "1h", START + 3600 * 30, lookback=24)
        self.assertEqual(r["status"], "triggered")
        self.assertEqual(r["trigger"]["price"], 102.0)

    def test_the_forming_bar_does_not_count(self):
        close = self.flat(29) + [(100.0, 103.0, 99.0, 102.0)]
        r = btc.evaluate(bars_from(close), "1h", START + 3600 * 29 + 1800, lookback=24)
        self.assertEqual(r["status"], "waiting")

    def test_no_data_when_too_few_bars(self):
        r = btc.evaluate(bars_from(self.flat(10)), "1h", START + 3600 * 10, lookback=24)
        self.assertEqual(r["status"], "no-data")

    def test_fixed_level(self):
        r = btc.evaluate(bars_from(self.flat(30)), "1h", START + 3600 * 30, level=100.5)
        self.assertEqual(r["status"], "waiting")
        r = btc.evaluate(bars_from(self.flat(30)), "1h", START + 3600 * 30, level=99.5, within=1)
        self.assertEqual(r["status"], "triggered")


class Plan(unittest.TestCase):
    def test_units_fit_the_max_loss_with_fees(self):
        p = btc.make_plan(100000.0, 99000.0, "price", ("R", 2.0), risk=100.0, fee_pct=0.1)
        self.assertEqual(p["target"], 102000.0)
        self.assertEqual(p["reward_risk"], 2.0)
        self.assertLessEqual(p["max_loss"], 100.0)
        self.assertGreater(p["max_loss"], 99.0)

    def test_capital_caps_the_position(self):
        p = btc.make_plan(100000.0, 99000.0, "price", ("R", 2.0), risk=1000.0, capital=5000.0)
        self.assertEqual(p["sized_by"], "capital")
        self.assertLessEqual(p["notional"], 5000.0)

    def test_refusals(self):
        with self.assertRaises(btc.BtcError):
            btc.make_plan(100.0, 101.0, "x", ("R", 2.0), risk=10)           # stop above entry
        with self.assertRaises(btc.BtcError):
            btc.make_plan(100000.0, 99950.0, "x", ("R", 2.0), risk=10)      # stop 0.05% away
        with self.assertRaises(btc.BtcError):
            btc.make_plan(100000.0, 99000.0, "x", ("price", 99500.0), risk=10)   # target under entry

    def test_stop_rules(self):
        bars = bars_from([(100.0, 110.0, 90.0, 100.0)] * 24)
        self.assertEqual(btc.parse_stop("range-low", 105.0, bars, 2.0)[0], 90.0)
        self.assertEqual(btc.parse_stop("range-mid", 105.0, bars, 2.0)[0], 100.0)
        self.assertAlmostEqual(btc.parse_stop("atr:1.5", 105.0, bars, 2.0)[0], 102.0)
        self.assertAlmostEqual(btc.parse_stop("pct:2", 100.0, None, None)[0], 98.0)


class Sim(unittest.TestCase):
    def test_walk_stop_wins_a_tie(self):
        self.assertEqual(btc._walk(100, 99, 101, [(101.5, 98.5, 100)])[0], "stop")
        self.assertEqual(btc._walk(100, 99, 101, [(101.5, 99.5, 100)])[0], "target")
        self.assertEqual(btc._walk(100, 99, 101, [(100.5, 99.5, 100.2)]), ("time", 100.2))

    def test_sim_is_repeatable_and_adds_up(self):
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "h.json")
            make(path)
            bars = btc.get_bars("1h", offline=path)
        plan = btc.make_plan(100000.0, 99000.0, "price", ("R", 2.0), risk=100.0)
        a = btc.sim(bars, plan, runs=2000, seed=1)
        b = btc.sim(bars, plan, runs=2000, seed=1)
        self.assertEqual(a, b)
        self.assertAlmostEqual(a["target_first"] + a["stop_first"] + a["neither"], 100.0, delta=0.2)
        self.assertGreater(a["history"]["signals"], 0)

    def test_history_rewards_a_trend_and_punishes_a_drop(self):
        up = bars_from([(100 + i, 101 + i, 99.5 + i, 100.5 + i) for i in range(120)])
        down = bars_from([(300 - i, 300.5 - i, 299 - i, 299.2 - i) for i in range(120)])
        up_r = btc.history(up, 100.0, 99.0, 102.0, 24, 12)
        self.assertTrue(up_r and all(r == "target" for r, _ in up_r))
        self.assertEqual(btc.history(down, 100.0, 99.0, 102.0, 24, 12), [])


class Offline(unittest.TestCase):
    def test_levels_and_atr(self):
        bars = bars_from([(100.0, 102.0, 98.0, 100.0)] * 40)
        self.assertEqual(btc.atr(bars), 4.0)
        lv = btc.levels(bars, bars, START + 3600 * 40)
        self.assertEqual(lv["h24"]["high"], 102.0)


if __name__ == "__main__":
    unittest.main()
