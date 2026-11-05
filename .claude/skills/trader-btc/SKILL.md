---
name: trader-btc
description: >-
  BTC-USD, 24/7. The crypto version of the day-trader pack's entry timer, exit
  planner, budget manager and time machine in one tool, because Bitcoin has no
  opening bell for trader-entry's opening range and no closing bell for
  trader-exit's flat-by time. Reads free hourly bars (Yahoo, or Coinbase with
  --source coinbase), calls the entry on the first completed bar that CLOSES
  above the rolling range high (the last 24 one-hour bars by default, or a
  level you give it), puts the stop at the range midpoint, the range low, a
  multiple of the ATR, a percent or your price, sets the target at 2R, sizes
  fractional BTC to your max loss with fees included, sets a maximum hold in
  hours instead of a closing time, then replays the trade 10,000 times plus
  every past breakout and prints the odds after fees. Long side only. It never
  places an order. Use when the user says "buy BTC when", "bitcoin entry",
  "where's my stop on BTC", "how much BTC can I buy", "BTC-USD plan", "has
  bitcoin broken out", "replay this BTC trade", "crypto day trade".
argument-hint: "levels | check | plan --risk USD | sim | show"
---

# trader-btc

Bitcoin trades all day, every day, so the NYSE-session tools cannot read it.
This skill keeps the pack's method and swaps the clock: the opening range
becomes a rolling range, "flat by 3:55 p.m." becomes a maximum hold in hours.
Not financial advice: it reads public data and does arithmetic. Bitcoin moves
more than most stocks, most people who day trade lose money, and a stop is a
plan, not a guarantee (a fast move can fill well past it).

`${CLAUDE_SKILL_DIR}` below is this skill's folder (where this SKILL.md lives).

```bash
python3 "${CLAUDE_SKILL_DIR}/btc.py" levels                      # price vs 24h / 7d / 20d ranges, ATR
python3 "${CLAUDE_SKILL_DIR}/btc.py" check --write               # waiting / triggered -> trader/btc-entry.json
python3 "${CLAUDE_SKILL_DIR}/btc.py" plan --risk 50 --capital 2000 --write   # -> trader/btc-plan.json
python3 "${CLAUDE_SKILL_DIR}/btc.py" sim                         # 10,000 paths + past breakouts
python3 "${CLAUDE_SKILL_DIR}/btc.py" show
python3 "${CLAUDE_SKILL_DIR}/../trader-risk/check.py" --btc      # the risk gate: PASS / BLOCK
```

Other flags: `--source coinbase` when Yahoo is blocked, `--interval 15m`
(check only), `--lookback N` bars in the range, `--level PRICE` instead of the
rolling high, `--within N` closed bars to look back for a trigger,
`--min-volume-x 1.2`, `--entry PRICE`, `--stop range-mid|range-low|atr:K|pct:X|price:X`,
`--target 2R|1.5R|price:X`, `--max-hold-hours 24`, `--json`, `--now "YYYY-MM-DD
HH:MM"` (UTC), `--offline FILE` (a saved Yahoo chart JSON).

## How to run it

1. `levels`: see where price sits. Tell the user the numbers, not a guess.
2. `check`: a bar must CLOSE above the level; a wick does not count. Waiting
   says how far away it is. If the warning says price is more than 1 ATR over
   the level, the entry is stale and the stop would be wide: say so and wait.
   Re-run it when the next bar closes (or with `/loop 15m` style polling).
3. `plan`: the stop is set BEFORE the entry. It refuses a stop at or above the
   entry, a stop under 0.3% away (fees and noise), and a target under the
   entry. The units are fractional BTC (6 decimals) so that the loss at the
   stop, fees included, fits `--risk`; `--capital` caps the position.
4. `sim`: read the verdict aloud, including "negative expectancy" or "coin
   flip". If it is negative, do not talk the user into the trade.
5. Risk check: run `python3 "${CLAUDE_SKILL_DIR}/../trader-risk/check.py" --btc`.
   BLOCK is final: say why and change the plan, never argue past it. On PASS,
   give the user the plan as a ticket (buy, units, stop, target, time stop)
   and let them place it themselves, on a paper account first. Once they say
   they took it, log it with `check.py --btc --record`, and when they are out
   `check.py --btc --close`. This skill and `trader-risk` place nothing, and
   `trader-broker` is built for whole-share stocks, so it is not used for BTC.

## What it reads and writes

| file | what |
| --- | --- |
| `trader/config.json` | optional: `lookback` (24), `fee_pct` per side (0.1), `max_hold_hours` (24), `min_stop_pct` (0.3) |
| `trader/btc-entry.json` | with `check --write`: status, level, trigger bar and price |
| `trader/btc-plan.json` | with `plan --write`: entry, stop, target, units, max loss, time stop |

## Rules to hold to

- Free data is unofficial and can lag. Ask the user to check the price on
  their exchange before acting.
- The fee default (0.1% a side) is an assumption: ask for their real fee.
- The replay reuses past bars and cannot know about news, halts or a
  weekend gap. It is a reality check, not a promise.
- Long side only. No leverage, no futures, no margin.
