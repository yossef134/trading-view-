#!/usr/bin/env python3
"""trader-btc: a 24/7 version of the day-trader pack's entry, exit, sizing and
replay steps, for BTC-USD (long side only, nothing here places an order).

Bitcoin has no opening bell and no closing bell, so the NYSE-session tools
(trader-entry, trader-exit, trader-timemachine) cannot read it. This script
swaps the opening range for a rolling range (the highest high of the last N
closed bars, 24 one-hour bars by default) and the 3:55 p.m. flat-by for a
maximum hold in hours.

    levels   where price sits against its 24h / 7d / 20d ranges and its ATR
    check    waiting / triggered: did a bar CLOSE above the rolling range high
    plan     stop, target, units for your max loss -> trader/btc-plan.json
    sim      10,000 simulated paths + every past breakout, with the odds
    show     print trader/btc-plan.json

Standard library only. Data: Yahoo Finance chart JSON (free, unofficial) or
Coinbase Exchange candles (--source coinbase). Not financial advice.
"""

import argparse
import json
import math
import os
import random
import sys
import time
import urllib.error
import urllib.request

UA = "Mozilla/5.0 (trader-btc)"
SYMBOL = "BTC-USD"
STEP = {"15m": 900, "1h": 3600, "1d": 86400}
YAHOO_RANGE = {"15m": "30d", "1h": "6mo", "1d": "1y"}
DEFAULTS = {"lookback": 24, "fee_pct": 0.1, "max_hold_hours": 24, "min_stop_pct": 0.3}


class BtcError(Exception):
    pass


# ---------------------------------------------------------------- data

def _get(url, timeout=20):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        raise BtcError("%s answered HTTP %d" % (url.split("?")[0], e.code))
    except (urllib.error.URLError, OSError) as e:
        raise BtcError("could not reach %s: %s" % (url.split("/")[2], getattr(e, "reason", e)))


def parse_yahoo(text):
    try:
        res = json.loads(text)["chart"]["result"][0]
        ts = res["timestamp"]
        q = res["indicators"]["quote"][0]
    except (KeyError, IndexError, TypeError, ValueError):
        raise BtcError("Yahoo sent no BTC-USD bars (is the symbol right? is the network open to Yahoo?)")
    bars = []
    for i, t in enumerate(ts):
        o, h, l, c = q["open"][i], q["high"][i], q["low"][i], q["close"][i]
        if None in (o, h, l, c):
            continue
        v = q["volume"][i] or 0
        bars.append({"t": int(t), "o": float(o), "h": float(h), "l": float(l), "c": float(c), "v": float(v)})
    return bars


def parse_coinbase(text):
    rows = json.loads(text)
    bars = [{"t": int(r[0]), "l": float(r[1]), "h": float(r[2]), "o": float(r[3]),
             "c": float(r[4]), "v": float(r[5])} for r in rows]
    bars.sort(key=lambda b: b["t"])
    return bars


def get_bars(interval, source="yahoo", offline=None, symbol=SYMBOL):
    if offline:
        with open(offline, encoding="utf-8") as fh:
            text = fh.read()
        bars = parse_yahoo(text)
    elif source == "coinbase":
        text = _get("https://api.exchange.coinbase.com/products/%s/candles?granularity=%d"
                    % (symbol, STEP[interval]))
        bars = parse_coinbase(text)
    else:
        path = "/v8/finance/chart/%s?range=%s&interval=%s" % (symbol, YAHOO_RANGE[interval], interval)
        last = None
        for host in ("query2", "query1"):
            try:
                bars = parse_yahoo(_get("https://%s.finance.yahoo.com%s" % (host, path)))
                break
            except BtcError as e:
                last = e
        else:
            raise BtcError("%s (tried query2 and query1; try --source coinbase)" % last)
    if not bars:
        raise BtcError("no %s bars came back" % interval)
    return bars


def closed_bars(bars, interval, now):
    """Bars whose interval has fully elapsed at `now` (epoch seconds)."""
    step = STEP[interval]
    return [b for b in bars if b["t"] % step == 0 and b["t"] + step <= now]


# ---------------------------------------------------------------- maths

def atr(bars, n=14):
    """Simple average of the last n true ranges."""
    if len(bars) < 2:
        return None
    trs = []
    for prev, b in zip(bars, bars[1:]):
        trs.append(max(b["h"] - b["l"], abs(b["h"] - prev["c"]), abs(b["l"] - prev["c"])))
    trs = trs[-n:]
    return sum(trs) / len(trs)


def floor6(x):
    return math.floor(x * 1e6 + 1e-9) / 1e6


def r2(x):
    return None if x is None else round(x, 2)


def when(ts):
    return time.strftime("%Y-%m-%d %H:%M UTC", time.gmtime(ts))


def money(x):
    return "${:,.2f}".format(x)


# ---------------------------------------------------------------- levels

def levels(hourly, daily, now):
    h = closed_bars(hourly, "1h", now)
    d = closed_bars(daily, "1d", now)
    out = {"symbol": SYMBOL, "now": when(now), "last": r2(hourly[-1]["c"]),
           "last_bar": when(hourly[-1]["t"])}

    def rng(bs, n):
        w = bs[-n:]
        return {"high": r2(max(b["h"] for b in w)), "low": r2(min(b["l"] for b in w)), "bars": len(w)}
    if h:
        out["h24"] = rng(h, 24)
        out["d7"] = rng(h, 168)
        out["atr_1h"] = r2(atr(h))
    if d:
        out["d20"] = rng(d, 20)
        out["atr_1d"] = r2(atr(d))
    return out


# ---------------------------------------------------------------- check

def evaluate(bars, interval, now, lookback=24, level=None, within=4, min_volume_x=None):
    """Pure function: the breakout status from the bars closed at `now`."""
    cb = closed_bars(bars, interval, now)
    res = {"symbol": SYMBOL, "setup": "level" if level is not None else "rolling-high",
           "interval": interval, "lookback": lookback, "now": when(now), "status": "waiting",
           "level": None, "trigger": None, "last": None, "reason": ""}
    if level is None and len(cb) <= lookback:
        res.update(status="no-data", reason="only %d closed %s bars, need more than %d" % (len(cb), interval, lookback))
        return res
    if not cb:
        res.update(status="no-data", reason="no closed bars")
        return res

    def lvl_at(i):
        if level is not None:
            return float(level)
        return max(b["h"] for b in cb[i - lookback:i])

    first = max(len(cb) - within, 0 if level is not None else lookback)
    for i in range(first, len(cb)):
        b, lvl = cb[i], lvl_at(i)
        if b["c"] <= lvl:
            continue
        if min_volume_x and level is None:
            avg = sum(x["v"] for x in cb[i - lookback:i]) / float(lookback)
            if avg and b["v"] < min_volume_x * avg:
                res["thin"] = True
                continue
        res.update(status="triggered", level=r2(lvl), reason="the %s bar closed above the %s" % (
            when(b["t"]).replace(" UTC", ""), "level" if level is not None else "%d-bar range high" % lookback))
        res["trigger"] = {"bar_start": when(b["t"]), "closed": when(b["t"] + STEP[interval]),
                          "price": r2(b["c"]), "pct_over": r2(100.0 * (b["c"] / lvl - 1)),
                          "bars_ago": len(cb) - 1 - i}
        break
    last = cb[-1]
    cur = lvl_at(len(cb) - 1) if res["level"] is None else res["level"]
    if res["level"] is None:
        res["level"] = r2(cur)
    res["last"] = {"bar_start": when(last["t"]), "close": r2(last["c"]),
                   "vs_level_pct": r2(100.0 * (last["c"] / cur - 1))}
    a = atr(cb)
    if a:
        res["atr"] = r2(a)
        res["extension_atr"] = r2((last["c"] - cur) / a)
    if res["status"] == "waiting":
        res["reason"] = "last close %s is %s the level %s (%+.2f%%)" % (
            money(last["c"]), "under" if last["c"] <= cur else "over", money(cur), 100.0 * (last["c"] / cur - 1))
        if res.get("thin"):
            res["reason"] += "; a bar closed above on thin volume (under %.1fx the average)" % min_volume_x
    return res


def describe_check(r):
    lines = ["BTC-USD  %s  [%s %s bars, %s]" % (r["status"].upper(), r["setup"], r["interval"], r["now"])]
    lines.append("  " + r["reason"])
    if r["trigger"]:
        t = r["trigger"]
        lines.append("  entry %s, level %s, %+.2f%% over, bar closed %s (%d bar(s) ago)" % (
            money(t["price"]), money(r["level"]), t["pct_over"], t["closed"], t["bars_ago"]))
        ext = r.get("extension_atr")
        if ext is not None and ext > 1.0:
            lines.append("  WARNING: price is already %.1f ATR above the level: chasing, the stop will be wide" % ext)
    elif r["level"]:
        lines.append("  waiting for a %s close above %s" % (r["interval"], money(r["level"])))
    return "\n".join(lines)


# ---------------------------------------------------------------- plan

def parse_target(text):
    t = text.strip()
    if t.lower().startswith("price:"):
        return ("price", float(t[6:]))
    if t.upper().endswith("R"):
        return ("R", float(t[:-1]))
    raise BtcError("--target is 2R, 1.5R or price:X")


def parse_stop(text, entry, window, atr_1h):
    t = text.strip().lower()
    if t.startswith("price:"):
        return float(t[6:]), "price"
    if t.startswith("pct:"):
        return entry * (1 - float(t[4:]) / 100.0), "%s%% under the entry" % t[4:]
    if t.startswith("atr:"):
        if not atr_1h:
            raise BtcError("an atr stop needs the hourly bars")
        k = float(t[4:])
        return entry - k * atr_1h, "%sx the 1h ATR (%s) under the entry" % (t[4:], money(atr_1h))
    if t in ("range-low", "range-mid"):
        if not window:
            raise BtcError("%s needs the hourly bars" % t)
        lo, hi = min(b["l"] for b in window), max(b["h"] for b in window)
        return (lo if t == "range-low" else (lo + hi) / 2.0), "%s of the last %d bars" % (t, len(window))
    raise BtcError("--stop is range-mid, range-low, atr:K, pct:X or price:X")


def make_plan(entry, stop, stop_rule, target, risk, capital=None, fee_pct=0.1,
              max_hold_hours=24, min_stop_pct=0.3, entry_time=None):
    """Pure function: stop, target and fractional units for a max loss."""
    if stop >= entry:
        raise BtcError("the stop %s is at or above the entry %s: a long trade's stop goes under it" % (
            money(stop), money(entry)))
    stop_pct = 100.0 * (entry - stop) / entry
    if stop_pct < min_stop_pct:
        raise BtcError("the stop is only %.2f%% under the entry (under %.2f%%): fees and noise would hit it. "
                       "Use a wider stop" % (stop_pct, min_stop_pct))
    rpu = entry - stop
    kind, val = target
    tgt = entry + val * rpu if kind == "R" else val
    if tgt <= entry:
        raise BtcError("the target %s is at or below the entry %s" % (money(tgt), money(entry)))
    k = (tgt - entry) / rpu
    fee = fee_pct / 100.0
    loss_per_unit = rpu + fee * (entry + stop)          # price loss plus fees both ways
    units = floor6(risk / loss_per_unit)
    limit = "max loss"
    if capital is not None and units * entry > capital:
        units = floor6(capital / entry)
        limit = "capital"
    if units <= 0:
        raise BtcError("%s of risk does not buy 0.000001 BTC at this stop" % money(risk))
    notional = units * entry
    plan = {
        "symbol": SYMBOL, "side": "buy", "entry": r2(entry), "stop": r2(stop), "stop_rule": stop_rule,
        "stop_pct": r2(stop_pct), "target": r2(tgt), "target_pct": r2(100.0 * (tgt - entry) / entry),
        "r": r2(rpu), "reward_risk": round(k, 2), "units": units, "notional": r2(notional),
        "max_loss": r2(units * loss_per_unit), "gain_at_target": r2(units * ((tgt - entry) - fee * (entry + tgt))),
        "sized_by": limit, "fee_pct_per_side": fee_pct, "max_hold_hours": max_hold_hours,
    }
    if entry_time:
        plan["entry_time"] = when(entry_time)
        plan["time_stop"] = when(entry_time + max_hold_hours * 3600)
    return plan


def describe_plan(p):
    lines = ["BTC-USD long plan",
             "  buy    %s BTC at about %s  (%s)" % (("%.6f" % p["units"]).rstrip("0"), money(p["entry"]), money(p["notional"])),
             "  stop   %s  (%.2f%% under, %s)" % (money(p["stop"]), p["stop_pct"], p["stop_rule"]),
             "  target %s  (%.2f%% over, %.2fR)" % (money(p["target"]), p["target_pct"], p["reward_risk"]),
             "  loss at the stop %s incl. fees; gain at the target %s; sized by %s" % (
                 money(p["max_loss"]), money(p["gain_at_target"]), p["sized_by"])]
    if p.get("time_stop"):
        lines.append("  out by %s whether or not stop or target hit (max hold %dh)" % (p["time_stop"], p["max_hold_hours"]))
    else:
        lines.append("  out within %d hours of entry whether or not stop or target hit" % p["max_hold_hours"])
    lines.append("  A stop is a plan, not a guarantee: a fast move can fill past it.")
    return "\n".join(lines)


# ---------------------------------------------------------------- sim

def _walk(entry, stop, target, steps):
    """steps: iterable of (high, low, close). Returns (outcome, exit_price)."""
    last = entry
    for h, l, c in steps:
        if l <= stop:                       # both in one bar: assume the stop came first
            return "stop", stop
        if h >= target:
            return "target", target
        last = c
    return "time", last


def history(bars, entry, stop, target, lookback, horizon):
    """Re-run the rule on every past breakout (non-overlapping). Percentages
    of the entry are reused so an old $30k signal tests a $100k plan fairly."""
    sp, tp = (entry - stop) / entry, (target - entry) / entry
    out, i, n = [], lookback, len(bars)
    while i < n - 1:
        lvl = max(b["h"] for b in bars[i - lookback:i])
        if bars[i]["c"] <= lvl:
            i += 1
            continue
        e = bars[i]["c"]
        s, t = e * (1 - sp), e * (1 + tp)
        window = bars[i + 1:i + 1 + horizon]
        res, px = _walk(e, s, t, [(b["h"], b["l"], b["c"]) for b in window])
        if res == "time" and len(window) < horizon:
            break                            # the tail has not played out yet
        out.append((res, (px - e) / (e - s)))
        i += _resolved_len(window, s, t) + 1
    return out


def _resolved_len(window, s, t):
    for k, b in enumerate(window, 1):
        if b["l"] <= s or b["h"] >= t:
            return k
    return len(window)


def monte_carlo(bars, entry, stop, target, horizon, runs=10000, seed=7):
    tri = [(b["h"] / p["c"], b["l"] / p["c"], b["c"] / p["c"]) for p, b in zip(bars, bars[1:])]
    rng = random.Random(seed)
    counts = {"target": 0, "stop": 0, "time": 0}
    rs, closes = [], []
    rpu = entry - stop
    for _ in range(runs):
        price, res, px = entry, "time", None
        for _s in range(horizon):
            rh, rl, rc = tri[rng.randrange(len(tri))]
            if price * rl <= stop:
                res, px = "stop", stop
                break
            if price * rh >= target:
                res, px = "target", target
                break
            price *= rc
        px = price if px is None else px
        counts[res] += 1
        rs.append((px - entry) / rpu)
    return counts, sum(rs) / len(rs)


def fee_r(entry, stop, fee_pct):
    return 2.0 * fee_pct / 100.0 * entry / (entry - stop)


def sim(bars, plan, lookback=24, horizon=None, runs=10000, seed=7, fee_pct=0.1):
    entry, stop, target = plan["entry"], plan["stop"], plan["target"]
    horizon = horizon or plan.get("max_hold_hours", 24)
    counts, mc_r = monte_carlo(bars, entry, stop, target, horizon, runs, seed)
    hist = history(bars, entry, stop, target, lookback, horizon)
    fr = fee_r(entry, stop, fee_pct)
    res = {"runs": runs, "seed": seed, "horizon_bars": horizon,
           "target_first": round(100.0 * counts["target"] / runs, 1),
           "stop_first": round(100.0 * counts["stop"] / runs, 1),
           "neither": round(100.0 * counts["time"] / runs, 1),
           "avg_r_gross": round(mc_r, 2), "avg_r_net": round(mc_r - fr, 2), "fee_r": round(fr, 2),
           "history": {"signals": len(hist),
                       "target": sum(1 for r, _ in hist if r == "target"),
                       "stop": sum(1 for r, _ in hist if r == "stop"),
                       "time": sum(1 for r, _ in hist if r == "time"),
                       "avg_r_net": round(sum(x for _, x in hist) / len(hist) - fr, 2) if hist else None}}
    h = res["history"]
    net = res["avg_r_net"]
    if h["signals"] < 20:
        verdict = "too few past breakouts (%d) to trust the history; the simulation says %s" % (
            h["signals"], "positive" if net > 0.1 else "close to a coin flip" if net >= -0.1 else "negative")
    elif net > 0.1 and h["avg_r_net"] is not None and h["avg_r_net"] > 0.1:
        verdict = "both the simulation and the history show a small positive edge after fees; it is still a bet"
    elif net < -0.1 or (h["avg_r_net"] is not None and h["avg_r_net"] < -0.1):
        verdict = "negative expectancy after fees: skip it or change the stop and target"
    else:
        verdict = "close to a coin flip after fees"
    res["verdict"] = verdict
    return res


def describe_sim(r):
    h = r["history"]
    lines = ["Replay: %d simulated paths of %d bars each (seed %d), built from BTC-USD's own bars" % (
                 r["runs"], r["horizon_bars"], r["seed"]),
             "  target first %.1f%%   stop first %.1f%%   neither by the end %.1f%%" % (
                 r["target_first"], r["stop_first"], r["neither"]),
             "  average %+.2fR after fees (%+.2fR before; fees cost %.2fR)" % (r["avg_r_net"], r["avg_r_gross"], r["fee_r"]),
             "  history: the same rule fired %d times: %d hit the target, %d the stop, %d neither%s" % (
                 h["signals"], h["target"], h["stop"], h["time"],
                 "; average %+.2fR after fees" % h["avg_r_net"] if h["avg_r_net"] is not None else ""),
             "  verdict: " + r["verdict"],
             "  A simulation is not a prediction: it reuses past bars and cannot know about tomorrow's news."]
    return "\n".join(lines)


# ---------------------------------------------------------------- cli

def write_json(path, doc):
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(doc, fh, indent=2)
        fh.write("\n")
    os.replace(tmp, path)


def read_json(path):
    try:
        with open(path, encoding="utf-8") as fh:
            return json.load(fh)
    except FileNotFoundError:
        return None
    except ValueError:
        raise BtcError("%s is not valid JSON" % path)


def read_config(path):
    cfg = dict(DEFAULTS)
    cfg.update({k: v for k, v in (read_json(path) or {}).items() if k in DEFAULTS})
    return cfg


def now_ts(a):
    if a.now:
        try:
            return int(time.mktime(time.strptime(a.now, "%Y-%m-%d %H:%M")) - time.timezone)
        except ValueError:
            raise BtcError('--now is "YYYY-MM-DD HH:MM" in UTC')
    return int(time.time())


def bars_for(a, interval, offline=None):
    return get_bars(interval, a.source, offline)


def cmd_levels(a):
    hourly = bars_for(a, "1h", a.offline)
    daily = bars_for(a, "1d", a.offline_daily)
    r = levels(hourly, daily, now_ts(a))
    if a.json:
        print(json.dumps(r, indent=2))
        return 0
    print("BTC-USD  last %s  (%s)" % (money(r["last"]), r["last_bar"]))
    for key, name in (("h24", "24h"), ("d7", "7d"), ("d20", "20d")):
        if key in r:
            print("  %-4s high %s   low %s" % (name, money(r[key]["high"]), money(r[key]["low"])))
    for key, name in (("atr_1h", "1h"), ("atr_1d", "1d")):
        if key in r:
            print("  ATR(14) %s: %s (%.2f%% of price)" % (name, money(r[key]), 100.0 * r[key] / r["last"]))
    return 0


def cmd_check(a):
    cfg = read_config(a.config)
    bars = bars_for(a, a.interval, a.offline)
    r = evaluate(bars, a.interval, now_ts(a), a.lookback or cfg["lookback"], a.level, a.within, a.min_volume_x)
    if a.write:
        write_json(a.entry_file, r)
    print(json.dumps(r, indent=2) if a.json else describe_check(r))
    return {"triggered": 0, "waiting": 1, "no-data": 2}[r["status"]]


def cmd_plan(a):
    cfg = read_config(a.config)
    lookback = a.lookback or cfg["lookback"]
    t = now_ts(a)
    entry, entry_time, window, a1 = a.entry, t, None, None
    if entry is None:
        doc = read_json(a.entry_file)
        if doc and doc.get("status") == "triggered":
            entry = doc["trigger"]["price"]
        else:
            raise BtcError("no entry price: pass --entry PRICE, or run `check --write` and wait for a trigger")
    needs_bars = a.stop.lower().startswith(("range", "atr"))
    if needs_bars:
        cb = closed_bars(bars_for(a, "1h", a.offline), "1h", t)
        window, a1 = cb[-lookback:], atr(cb)
    stop, rule = parse_stop(a.stop, entry, window, a1)
    p = make_plan(entry, stop, rule, parse_target(a.target), a.risk, a.capital,
                  cfg["fee_pct"], a.max_hold_hours or cfg["max_hold_hours"], cfg["min_stop_pct"], entry_time)
    if a.write:
        write_json(a.plan_file, p)
    print(json.dumps(p, indent=2) if a.json else describe_plan(p))
    return 0


def cmd_sim(a):
    cfg = read_config(a.config)
    p = read_json(a.plan_file)
    if not p:
        raise BtcError("no plan: run `plan --write` first (%s)" % a.plan_file)
    r = sim(bars_for(a, "1h", a.offline), p, a.lookback or cfg["lookback"], a.horizon, a.runs, a.seed, cfg["fee_pct"])
    print(json.dumps(r, indent=2) if a.json else describe_sim(r))
    return 0


def cmd_show(a):
    p = read_json(a.plan_file)
    if not p:
        raise BtcError("no plan yet (%s)" % a.plan_file)
    print(json.dumps(p, indent=2) if a.json else describe_plan(p))
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(prog="btc.py", description="BTC-USD, 24/7: levels, entry, exit plan, replay.")
    sub = ap.add_subparsers(dest="cmd", required=True)

    def common(p):
        p.add_argument("--source", choices=("yahoo", "coinbase"), default="yahoo")
        p.add_argument("--offline", help="a saved Yahoo chart JSON (hourly) instead of the network")
        p.add_argument("--now", help='"YYYY-MM-DD HH:MM" UTC (default: now)')
        p.add_argument("--lookback", type=int, help="bars in the rolling range (default 24)")
        p.add_argument("--config", default="trader/config.json")
        p.add_argument("--entry-file", default="trader/btc-entry.json")
        p.add_argument("--plan-file", default="trader/btc-plan.json")
        p.add_argument("--json", action="store_true")

    p = sub.add_parser("levels")
    common(p)
    p.add_argument("--offline-daily", help="a saved Yahoo chart JSON (daily)")
    p.set_defaults(fn=cmd_levels)

    p = sub.add_parser("check")
    common(p)
    p.add_argument("--interval", choices=("15m", "1h"), default="1h")
    p.add_argument("--level", type=float, help="a fixed price to beat instead of the rolling range high")
    p.add_argument("--within", type=int, default=4, help="look for a trigger in the last N closed bars")
    p.add_argument("--min-volume-x", type=float, help="trigger bar volume vs the range's average (e.g. 1.2)")
    p.add_argument("--write", action="store_true", help="write trader/btc-entry.json")
    p.set_defaults(fn=cmd_check)

    p = sub.add_parser("plan")
    common(p)
    p.add_argument("--entry", type=float, help="entry price (default: the trigger in trader/btc-entry.json)")
    p.add_argument("--stop", default="range-mid", help="range-mid|range-low|atr:K|pct:X|price:X")
    p.add_argument("--target", default="2R", help="2R|1.5R|price:X")
    p.add_argument("--risk", type=float, required=True, help="max loss in USD, fees included")
    p.add_argument("--capital", type=float, help="cap the position at this many USD")
    p.add_argument("--max-hold-hours", type=int)
    p.add_argument("--write", action="store_true", help="write trader/btc-plan.json")
    p.set_defaults(fn=cmd_plan)

    p = sub.add_parser("sim")
    common(p)
    p.add_argument("--runs", type=int, default=10000)
    p.add_argument("--seed", type=int, default=7)
    p.add_argument("--horizon", type=int, help="bars to simulate (default: the plan's max hold in hours)")
    p.set_defaults(fn=cmd_sim)

    p = sub.add_parser("show")
    common(p)
    p.set_defaults(fn=cmd_show)

    a = ap.parse_args(argv)
    try:
        return a.fn(a)
    except BtcError as e:
        print("btc: %s" % e, file=sys.stderr)
        return 3


if __name__ == "__main__":
    sys.exit(main())
