import datetime
import importlib.util
import json
import os
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("risk", os.path.join(os.path.dirname(HERE), "check.py"))
risk = importlib.util.module_from_spec(spec)
spec.loader.exec_module(risk)

NOW = datetime.datetime(2026, 10, 27, 3, 0, 0)       # naive UTC, 23:00 the day before in New York (market closed)
CFG = {"budget": 5000, "max_loss_per_trade_usd": 50, "max_daily_loss_usd": 150, "max_trades_per_day": 3,
       "min_reward_risk": 1.0, "max_order_usd": 4000, "min_order_usd": 5, "max_position_pct": 75,
       "cash_buffer_pct": 10}


def plan(**kw):
    p = {"symbol": "BTC-USD", "side": "buy", "entry": 100000.0, "stop": 99000.0, "target": 102000.0,
         "units": 0.03, "max_hold_hours": 24, "fee_pct_per_side": 0.1}
    p.update(kw)
    return p


def run(p, cfg=None, **kw):
    return risk.check_btc(p, dict(CFG, **(cfg or {})), now=NOW, **kw)


def reasons(res):
    return " | ".join(res["results"][0]["reasons"])


class BtcRisk(unittest.TestCase):
    def test_a_good_plan_passes_even_with_the_market_closed(self):
        res = run(plan())
        self.assertEqual(res["results"][0]["verdict"], "PASS", reasons(res))
        self.assertEqual(res["results"][0]["max_loss"], 35.97)      # 0.03 x (1000 + 0.001 x 199000)

    def test_loss_over_the_cap_blocks(self):
        res = run(plan(units=0.045))
        self.assertIn("loss:", reasons(res))

    def test_stop_rules(self):
        self.assertIn("stop: no stop", reasons(run(plan(stop=None))))
        self.assertIn("must be below", reasons(run(plan(stop=100500.0))))
        self.assertIn("minimum", reasons(run(plan(stop=99900.0))))

    def test_target_and_reward_risk(self):
        self.assertIn("target:", reasons(run(plan(target=99500.0))))
        self.assertIn("reward:risk", reasons(run(plan(target=100500.0))))

    def test_time_stop_is_required_and_capped(self):
        self.assertIn("time stop", reasons(run(plan(max_hold_hours=None))))
        self.assertIn("btc_max_hold_hours", reasons(run(plan(max_hold_hours=72))))
        self.assertEqual(run(plan(max_hold_hours=72), {"btc_max_hold_hours": 96})["pass"], 1)

    def test_long_only_no_leverage_symbol(self):
        self.assertIn("short", reasons(run(plan(side="sell"))))
        self.assertIn("leverage", reasons(run(plan(leverage=3))))
        self.assertIn("symbol", reasons(run(plan(symbol="ETH-USD"))))

    def test_size_limits(self):
        res = run(plan(units=0.05, stop=98000.0), {"max_loss_per_trade_usd": 500})
        self.assertIn("size:", reasons(res))                         # $5,000 over the $4,000 max order
        res = run(plan(), {"max_order_usd": 1000, "max_loss_per_trade_usd": 500})
        self.assertIn("size:", reasons(res))
        res = run(plan(), {"max_position_pct": 50})
        self.assertIn("position:", reasons(res))

    def test_daily_loss_and_trades_count_stocks_and_btc_together(self):
        today = "2026-10-26"
        broker = {"orders": [{"status": "placed", "date": today, "symbol": "TSLA", "side": "buy",
                              "kind": "entry", "max_loss": 120.0}]}
        self.assertIn("daily loss", reasons(run(plan(), state=broker)))
        btc = {"entries": [{"date": today, "status": "closed", "max_loss": 50.0}] * 3}
        self.assertIn("trades:", reasons(run(plan(), btc_state=btc)))

    def test_an_open_btc_entry_blocks_a_second(self):
        btc = {"entries": [{"date": "2026-10-25", "status": "open", "max_loss": 10.0}]}
        self.assertIn("duplicate", reasons(run(plan(), btc_state=btc)))

    def test_fresh_higher_price_raises_the_risk(self):
        res = run(plan(), prices={"BTC-USD": 101000.0}, price_times={"BTC-USD": NOW})
        self.assertEqual(res["results"][0]["entry_ref_from"], "the latest price")
        self.assertIn("loss:", reasons(res))                          # 0.03 x 2200 > $50
        res = run(plan(), prices={"BTC-USD": 101000.0},
                  price_times={"BTC-USD": NOW - datetime.timedelta(hours=2)})
        self.assertEqual(res["results"][0]["entry_ref_from"], "plan")

    def test_blocked_list(self):
        self.assertIn("blocked", reasons(run(plan(), {"blocked": ["btc"]})))

    def test_record_and_close(self):
        res = run(plan())
        st = risk.btc_record(None, res, plan(), res["date"], NOW)
        self.assertEqual(st["entries"][0]["status"], "open")
        self.assertIn("duplicate", reasons(run(plan(), btc_state=st)))
        st, n = risk.btc_close(st)
        self.assertEqual(n, 1)
        self.assertNotIn("duplicate", reasons(run(plan(), btc_state=st)))

    def test_cli_end_to_end(self):
        with tempfile.TemporaryDirectory() as d:
            def path(n):
                return os.path.join(d, n)
            json.dump(plan(), open(path("plan.json"), "w"))
            json.dump(CFG, open(path("config.json"), "w"))
            base = ["--btc", "--plan", path("plan.json"), "--config", path("config.json"),
                    "--portfolio", path("none.json"), "--prices", path("none.json"), "--state", path("none.json"),
                    "--btc-state", path("btc.json"), "--btc-out", path("out.json"), "--now", "2026-10-26 23:00"]
            self.assertEqual(risk.main(base + ["--record"]), 0)
            self.assertEqual(json.load(open(path("btc.json")))["entries"][0]["status"], "open")
            self.assertEqual(json.load(open(path("out.json")))["pass"], 1)
            self.assertEqual(risk.main(base), 1)                      # second entry while one is open
            self.assertEqual(risk.main(base + ["--close"]), 0)
            self.assertEqual(risk.main(base), 0)


if __name__ == "__main__":
    unittest.main()
