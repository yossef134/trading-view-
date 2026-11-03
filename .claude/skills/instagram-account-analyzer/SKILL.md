---
name: instagram-account-analyzer
description: >
  Full audit of any public Instagram account from just a username. Pulls the profile and recent posts/reels through Apify, then reports which videos worked and which flopped (and why), best posting days and hours, bio quality, hooks, captions, hashtags, CTAs, posting consistency and trend. Detects the account's niche, finds the viral reels in that niche and benchmarks the account against them and against competitors, and ends with a concrete 30-day plan. Use whenever the user says "analyse this Instagram account", "حلل حساب انستجرام", "حلل الاكونت ده", "audit my Instagram", "why are my reels flopping", "best time to post", "is my bio good", or just sends an Instagram @username or profile link and wants to know how it is doing. Reports in the user's language (Egyptian Arabic by default for this user).
---

# Instagram Account Analyzer

Give it an account, get a full diagnosis. All numbers come from scripts, not from guessing. Your job is to run them, read the results like a strategist, and explain them plainly.

## Ground rules

- **Language:** write the report in Egyptian Arabic (عامية مصرية) unless the user writes in another language. Keep technical terms in English where Egyptians use them (hook, reach, CTA, reel, carousel).
- **Only public data.** Instagram does not expose reach, saves, shares or follower activity to outsiders. Never present an estimate of those as a fact. "Best time to post" for an account that is not the user's is **inferred from past post performance** and must be labelled that way with its sample size.
- **Comments:** analyse comment *counts* only. The Apify post actors return comment text anyway; `fetch_instagram.py` drops it in memory before saving. Do not go looking for it, do not run a comments scrape.
- **Costs:** Apify is pay-per-result (measured: about $0.0026 per post, so 60 posts is roughly $0.16, plus a few cents for niche reels). Tell the user the expected cost before a run larger than the default, and report the real `cost_usd` afterwards.
- **Never fabricate.** If a step failed or a sample is too small, say so. Under about 25 scored posts, mark timing and pattern findings as "مؤشر مش حقيقة".
- Never print tokens. `APIFY_API_TOKEN` is read from the environment by the scripts (or injected by the proxy in cloud sessions).

## Files

- `scripts/fetch_instagram.py` — Apify fetcher (`account`, `hashtag`, `profiles`).
- `scripts/analyze.py` — all metrics → `analysis.json`.
- `references/metrics.md` — what every metric means and its limits. Read it before explaining a number you are unsure about.

Work in `outputs/instagram-analyzer/<username>/<YYYY-MM-DD>/` inside the project (create it). Keep `raw.json`, `analysis.json`, `niche_reels.json` and the final report there.

## Step 1. Get the target

Accept `@name`, a profile URL, or a bare username. Ask only what is missing:

1. Is this the user's **own** account? (If yes and Supermetrics has an Instagram source connected, Step 7 adds real insights.)
2. Depth: default 60 posts (about 2 months for an active account). Offer 100 for more reliable timing.
3. Timezone for "best time": default `Africa/Cairo`; ask if the audience is elsewhere (e.g. Gulf → `Asia/Riyadh`).

## Step 2. Fetch

```bash
python3 -I scripts/fetch_instagram.py account <username> --limit 60 --out outputs/instagram-analyzer/<username>/<date>/raw.json
```

Stops with a clear message for private/missing accounts. A run takes about 40–90 seconds. If Apify returns a validation error, re-check the actor input schema (`GET https://api.apify.com/v2/acts/<actor>/builds/default`) rather than guessing inputs.

## Step 3. Detect the niche, then fetch the niche's viral reels

Read the bio, `top_hashtags`, hooks and captions in `raw.json`. Decide, and show the user:

- **Niche** (specific: "fitness coaching for Arab women", not "fitness") and **sub-niche**.
- **3–5 niche hashtags** that real creators in this niche use (prefer the account's own tags that are neither huge generic ones like `#love` nor private brand tags).

Confirm with the user in one line if the niche is ambiguous; otherwise proceed.

```bash
python3 -I scripts/fetch_instagram.py hashtag <tag1> <tag2> <tag3> --limit 40 --out outputs/instagram-analyzer/<username>/<date>/niche_reels.json
```

## Step 4. Analyse

```bash
python3 -I scripts/analyze.py --raw .../raw.json --niche .../niche_reels.json --tz Africa/Cairo --out .../analysis.json
```

Read `analysis.json` fully. Skip `--niche` only if Step 3 was skipped.

## Step 5. Competitors (optional but recommended)

`analysis.json → related_profiles` are Instagram's own "similar accounts". Pick 3–4 that truly match the niche (drop celebrities and unrelated brands), then:

```bash
python3 -I scripts/fetch_instagram.py profiles <a> <b> <c> --out .../competitors.json
```

Compare followers, bio positioning and link strategy. For a deeper comparison run Step 2 on one or two of them with `--limit 30`.

## Step 6. Write the report

Use these sections, in order. Be specific: quote actual hooks, name actual posts with their URLs, give numbers with their sample size. Every "problem" gets a "so do this".

1. **الخلاصة في 5 أسطر** — verdict, biggest strength, biggest leak, the one thing to change first.
2. **صحة الحساب** — followers, median engagement rate vs the rule-of-thumb band (`health`; say the band is a rough heuristic), followers/following ratio, trend (`trend.direction`, `change_pct`), cadence and consistency.
3. **الفيديوهات الناجحة** — `winners` (index ≥ 1.5× the median of their own format). For each: what it is, why it likely worked (hook, topic, length, format, audio, CTA), what pattern repeats across winners.
4. **الفيديوهات الفاشلة** — `losers` (≤ 0.5×). Same treatment: likely cause and whether to retire, rework or retest the idea. Be fair: a low index on a post under 48 h old is excluded for that reason (`excluded.immature`).
5. **أنماط المحتوى** — from `patterns`: format mix vs results, reel duration sweet spot, caption length, hashtag count, CTA vs none, question hooks, number hooks, original vs trending audio, carousel slide count. Only call something a pattern when each side has n ≥ 3, and say n.
6. **أحسن أوقات النشر** — `timing`: best weekdays and 3-hour blocks, where the winners were posted, confidence and sample size, and the caveat line. For the user's own account, replace with Supermetrics data if Step 7 ran.
7. **البايو واللينك** — start from `bio` (mechanical checks), then judge it yourself: does a stranger understand *who it is for, what they get, why trust you, what to do next* in 3 seconds? Give a rewritten bio (max 150 chars) and a name-field tip (keyword in the name field is searchable).
8. **النيش والترند** — the niche you detected, `niche` summary (median and 90th-percentile views, typical duration, top hashtags), the top viral reels with URLs and *why they hit* (hook structure, payoff speed, format), and how the account's reels compare. Remind that hashtag results favour big accounts.
9. **المنافسين** — comparison table and what each does better; what gap the account can own.
10. **خطة 30 يوم** — weekly cadence, 3–4 content pillars with the format and hook style that suits each, 10 concrete video ideas drawn from winners and viral niche reels (with a hook line each), posting slots, one experiment per week with a success metric.
11. **حاجات تانية لاحظتها** — anything outside the checklist you noticed: pinned posts strategy, repeated topics that die, collaboration/paid-partnership effect, hidden likes, comments disabled, posting gaps, language mix, thumbnail/cover consistency, first-line hook habits.

Save as `report.md` next to the data and give the user the path.

## Step 7. Optional extras

- **Own account + Supermetrics:** load the Supermetrics tools (`data_source_discovery`, `field_discovery`, `instagram_insights`) and pull reach, impressions, saves, shares, profile visits and follower online times. Use `field_discovery` for real field ids; never invent them. Then correct the timing and "what worked" sections with real reach and saves.
- **Scripts for new ideas:** hand the best viral reel URLs to `reels-scripting`; use `hook-generator` for hook variants (adapt to Instagram/Arabic if asked).
- **Dashboard:** *(next build step — not implemented yet.)* Do not promise an HTML dashboard until `scripts/build_dashboard.py` exists.
- **Content calendar or repeat audit in 30 days:** save `analysis.json` per date so progress can be diffed.

## When things go wrong

- Private account: say so and stop. Do not try workarounds.
- Fewer than 12 posts: give a light audit (bio, health, format mix) and say that winners/losers/timing need more history.
- Hidden likes (`likes: null`): rely on views for reels and say engagement rate is unavailable for those posts.
- Apify quota/payment error: report the exact message and the console link; do not retry in a loop.
