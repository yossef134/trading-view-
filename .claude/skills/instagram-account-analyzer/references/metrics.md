# Metric definitions and limits

| Metric | Definition | Limit |
|---|---|---|
| `value` | Reels/videos: public play count. Images/carousels: likes + comments | Plays include replays; carousels/images have no public view count |
| `index` | `value` ÷ median `value` of the same format, pinned and posts younger than 48 h excluded | Needs ≥ 3 mature posts of that format, else `null` |
| win / lose | index ≥ 1.5 / ≤ 0.5 | Thresholds are conventions, tune in `analyze.py` (`WIN`, `LOSE`) |
| `er` | (likes + comments) ÷ current followers | Uses today's follower count for old posts, so older posts are slightly flattered |
| `view_rate` | plays ÷ followers | >1 means the reel left the follower base (good sign) |
| `health.er_vs_benchmark` | Compared with rough tier bands | Heuristic, not an Instagram figure; say so |
| `timing.*` | Median index by weekday and by 3-hour block (in `--tz`) | Inference from past results; `confidence` is low under 25 scored posts, medium under 60 |
| `trend` | Median ER of older half vs newer half of mature posts | Needs ≥ 10 posts; ±10% treated as flat |
| `cadence` | Posts per week, gaps between posts | Pinned posts have old dates but are included in cadence |
| `patterns.*` | Median index per group | Only trust groups with n ≥ 3; correlation, not proof |
| `niche` | Stats over reels returned for the chosen hashtags | Biased to big accounts; use for patterns not targets |

## What the public API cannot give

Reach, impressions, saves, shares, profile visits, follower demographics, follower online times, story data, link clicks. For the user's own account these come from Instagram Insights via Supermetrics, never from scraping.

## Why the median

One viral reel can lift the mean 10×. The median shows what a *typical* post does, so "win" means "beat your normal", which is the useful question.
