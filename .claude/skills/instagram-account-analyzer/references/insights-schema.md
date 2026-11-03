# `insights.json` - what Claude writes for the dashboard

The scripts produce numbers. The **meaning** (why a post won, what to do next) is written by Claude in the report step and saved as `insights.json` next to `analysis.json`. `build_dashboard.py --insights insights.json` places each piece in the right card. Every key is optional; anything missing is simply not shown (the dashboard falls back to an automatic number-only summary).

All text is Egyptian Arabic unless the user asked otherwise. Plain strings only - no HTML or Markdown (it is rendered as text).

```jsonc
{
  "summary": ["5 short lines: verdict, biggest strength, biggest leak, ..."],
  "first_fix": "The single first change to make",

  // keys are the post URL exactly as in analysis.json (winners[].url / losers[].url)
  "winners_notes": { "https://www.instagram.com/p/XXXX/": "why it worked: hook, topic, length, audio, CTA" },
  "losers_notes":  { "https://www.instagram.com/p/YYYY/": "likely cause + retire / rework / retest" },

  "patterns_notes": ["Each finding with its n, e.g. 'reels of 15-30s beat 30-60s (n=5 vs 4) - indicative only'"],
  "timing_note": "One line that adds to the built-in caveat, e.g. best slot + sample size",

  "bio": {
    "verdict": "Does a stranger understand who it is for, what they get, why trust, what next - in 3 seconds?",
    "rewrite": "Suggested bio, max 150 characters",
    "tips": ["name-field keyword", "link strategy", "highlights"]
  },

  "niche": {
    "name": "specific niche, not a broad category",
    "sub_niche": "optional",
    "notes": "how the account compares with the niche's viral reels",
    "viral_notes": { "https://www.instagram.com/p/ZZZZ/": "why this niche reel hit" }
  },

  "competitors_notes": "what they do better, and the gap this account can own",

  "plan": {
    "cadence": "posts per week and mix",
    "posting_slots": ["Sat 00-02h", "Fri 18-20h"],
    "pillars": [{ "name": "", "format": "", "hook_style": "", "why": "" }],
    "ideas": [{ "hook": "opening line", "format": "reel", "based_on": "winner or niche reel URL", "why": "" }],
    "experiments": [{ "week": 1, "test": "", "metric": "" }]
  },

  "extras": ["Anything noticed outside the checklist"]
}
```

## Rules

- Never put a number in here that is not in `analysis.json`, `niche_reels.json` or `competitors.json`. If you cite a figure, it must be one the scripts computed.
- Label small samples ("n=3, مؤشر مش حقيقة"). The dashboard already shows n on charts; do not contradict it.
- Never invent reach, saves or shares for an account that is not connected through Supermetrics.
- Keep notes short (one or two sentences); the report file carries the long form.
