---
name: instagram-account-analyzer
description: >
  Full audit and content strategy for an Instagram account from a username. First understands the client's stage (zero audience vs working audience) and pins down the exact niche by asking questions, checks topic coherence, proposes 5 sub-niches, finds 5 real competitors in that niche, analyses their last 20 reels (what won, what repeats, with links, formats judged by viewing the video frames), collects real audience questions and objections from competitor comments and web research (Google, Reddit, Quora, forums), and turns them into video ideas. Also audits the account itself (winners, flops, bio) at a depth that matches its stage. Use whenever the user says "analyse this Instagram account", "حلل حساب انستجرام", "حلل الاكونت ده", "audit my Instagram", "find my competitors", "what content should I make", "ايه الفيديوهات اللي بتكسب في النيش بتاعي", or sends an Instagram @username or profile link. Reports in the user's language (Egyptian Arabic by default for this user).
---

# Instagram Account Analyzer

Numbers come from scripts. Judgement (niche, formats, why something won, ideas) comes from you, always grounded in data you can link to.

## Ground rules

- **Language:** Egyptian Arabic (عامية مصرية), technical words in English (hook, reach, CTA, reel).
- **Public data only.** Reach, saves, shares and follower activity are not public; never state estimates of them as facts. Posting times and Supermetrics are out of scope (the user said they are not important); mention timing only if asked, and then as an inference with its sample size.
- **Never fabricate.** Every claim about a competitor, question or objection carries a link. If a source returned nothing, say so. Small samples are "مؤشر مش حقيقة".
- **Comments (consent given by the user, 2026-11-04):** `comments` collects public comment TEXT from competitors' top reels, anonymised (no names/ids/avatars; mentions, links, emails, numbers masked; the competitor's own replies removed). Own-account files keep counts only. Do not collect comments for any other purpose.
- **Open format vocabulary.** The ten formats in `references/content-formats-2026.md` are suggested names. Label what you actually see; invent a new name whenever a reel does not fit.
- **Do not use the IShort connector** (the user said not to rely on it).
- **Costs are real money; measure, quote, ask, then run.** Measured on 2026-11-04:

| Step | Measured cost | Rule |
|---|---|---|
| Own account, 60 posts | about $0.03-0.16 | just run |
| Profile cards | $0.0026 each | just run |
| Competitor reels | about $0.003 per reel (5 accounts x 20 = about $0.2-0.3) | quote, then run |
| Comments on top reels | about $0.02 per reel with 40 comments (24 reels = about $0.5) | quote, then run |
| **Videos stored by Apify (`videos`)** | **about $0.07 per video** (24 = about $1.6) | **always ask first; keep `--top 2-3`; prefer free `--cdn`** |
| Hashtag reels | about $0.0075 per reel; noisy and biased low | not used by default |

  `cost_usd` in saved files is the real spend summed over all runs started during the fetch (an upper bound if other jobs share the Apify account, and **double-counted if two fetches run at the same time**: run them one after the other).
- Never print tokens (`APIFY_API_TOKEN` is read from the environment, or injected by a proxy).

## Files

- `scripts/fetch_instagram.py` - Apify: `account`, `profiles`, `reels`, `videos`, `comments` (and optional `hashtag`).
- `scripts/analyze.py` - own account: metrics, winners/losers, timing, bio checks, **stage** -> `analysis.json`.
- `scripts/analyze_competitors.py` - competitor reels vs each account's own median, winners, repeated patterns with links -> `competitors_analysis.json`.
- `scripts/media.py` - `sheets` (contact sheets of frames from reels, needs ffmpeg+Pillow) and `grid` (cover grid of the account's posts).
- `scripts/prep_comments.py` - keeps ONLY audience questions and objections -> `audience_signals.json`.
- `scripts/build_dashboard.py` + `scripts/dashboard_template.html` - offline HTML dashboard (own-account sections today; see Step 9).
- `references/niche-interview.md`, `references/content-formats-2026.md`, `references/research-method.md`, `references/metrics.md`, `references/insights-schema.md`.

Work in `outputs/instagram-analyzer/<username>/<YYYY-MM-DD>/`.

## Step 0. Intake

Accept `@name`, URL or username. Ask only what is missing: is it the user's own account or a client's; timezone for "best time" (default `Africa/Cairo`).

## Step 1. Fetch the account

```bash
python3 -I scripts/fetch_instagram.py account <username> --limit 60 --out <dir>/raw.json
python3 -I scripts/analyze.py --raw <dir>/raw.json --out <dir>/analysis.json
```

Read `analysis.json -> stage` (`zero` / `early` / `working`, with reasons) and **confirm it with the client** in one line. It decides how deep Step 8 goes: at `zero` do not audit own posts beyond bio and what exists; put the effort into Steps 2-7.

## Step 2. Pin down the niche - ask until exact

Follow `references/niche-interview.md`. Do not scrape competitors or research until the client confirms one sentence: "I help [exactly who] get [exactly what] through [how]". If the account already shows it clearly, propose a draft and ask only to confirm. Otherwise ask in rounds of 3-4 questions (use AskUserQuestion). Also capture constraints (on camera? time? editor? dialect?) and the 90-day goal.

## Step 3. Topic coherence (free); visual identity is OFF

The user removed the visual-identity check because it needs many downloads. Do only the free part: read the captions in `raw.json`, label each post on-niche / adjacent / unrelated, report the share and list the unrelated ones with links. Offer `media.py grid` only if the user asks and the CDN is reachable; never guess a visual verdict without seeing the covers.

## Step 4. Five sub-niches

Propose 5 sub-niches (audience slice x problem), each with a one-line reason and the evidence (bio, captions, competitor focus). Let the client pick or edit. Research and ideas are produced per sub-niche.

## Step 5. Competitors: 5, approved before the expensive steps

Find candidates, then verify each with `profiles`. Discovery that works: web search ("best Instagram accounts for <niche>", Arabic and English, `site:instagram.com`), the account's `related_profiles`, accounts the client admires, and owners of top reels in a small hashtag sample if needed. **Apify keyword search does NOT discover accounts (it returned one account), so do not use it.**

Keep a mix: 2 larger accounts to learn from and 3 close to the client's size (0.3x to 5x followers), all public and active in the last 60 days. **English-language accounts are fine** (the user said so); prefer Arabic ones only when dialect matters, and say which language each account uses. Verify with:

```bash
python3 -I scripts/fetch_instagram.py profiles <a> <b> <c> <d> <e> --out <dir>/competitors.json
```

**Audience match is mandatory:** a competitor must speak to the CLIENT'S audience (for a doctor-marketing client: accounts that talk TO doctors/clinic owners, not patient-facing health content). Check bio plus the hooks of the last reels before accepting. Lesson from the first full run: two large English accounts looked right by bio but posted patient entertainment and were removed.

Show the list (link, followers, why chosen, bio line) with the cost of Step 6 and **wait for approval**.

## Step 6. Last 20 reels per competitor: what won and what repeats

```bash
python3 -I scripts/fetch_instagram.py reels <a> <b> <c> <d> <e> --limit 20 --out <dir>/competitor_reels.json
python3 -I scripts/analyze_competitors.py --reels <dir>/competitor_reels.json --out <dir>/competitors_analysis.json
```

Each reel is judged against ITS OWN account's median (winner >= 1.5x, loser <= 0.5x). Accounts with fewer than 4 reels with views are not scored. A pattern is "repeated" only with >= 3 winners, >= 2 accounts, no single account supplying > 60% of them, lift >= 1.3. Report counts ("9 of 18 winners") with links, never a bare claim. Watch for accounts with few reels (their medians are noisy).

**Formats: look at the video.** Quote the price, get a yes, then:

```bash
python3 -I scripts/fetch_instagram.py videos --reels <dir>/competitor_reels.json --top 3 --out <dir>/videos.json   # about $0.07 per video; or add --cdn when fbcdn.net is allowed (free)
python3 -I scripts/media.py sheets --videos <dir>/videos.json --out-dir <dir>/sheets
```

Open each sheet (8 frames with time stamps). Write `format_labels.json` as `{"<shortCode>": {"format": "...", "topic": "...", "note": "..."}}`, free-form names. Note what you can see: who is on camera, text-on-screen, when the hook appears, cuts and b-roll, props, production level. Re-run `analyze_competitors.py --labels <dir>/format_labels.json`. Because only top reels are viewed, format results are **counts among winners, not lift**; the script marks them `counts_only`. Say so.

For each competitor give: top 3 winners (link, views, index, format, hook), the pattern that recurs in its own winners, and where it is weak. Then the cross-competitor repeated patterns, each with example links.

**Audience comments (the user agreed):**

```bash
python3 -I scripts/fetch_instagram.py comments --reels <dir>/competitor_reels.json --top 3 --limit 40 --out <dir>/comments.json
python3 -I scripts/prep_comments.py --comments <dir>/comments.json --out <dir>/audience_signals.json
```

`audience_signals.json` holds ONLY questions and objections (praise, "send the sheet" requests and chatter are counted in `meta.by_kind` and dropped). Read them and cluster by theme. Expect few (first run: about 4 questions and 1 objection out of 185 comments). Never quote a commenter's identity.

## Step 7. Real questions and objections -> video ideas

**Preflight first:** `python3 -I scripts/preflight.py`. If Reddit / Quora / YouTube / Google are BLOCKED, do not launch research agents (they only get search snippets and return thin, unverified results): tell the user which hosts to allow and continue with the rest. **Research only the voice of the client's audience** (for doctor-marketing: doctors and clinic owners), never their customers' voice.

Follow `references/research-method.md`: per approved sub-niche, deep research (Google, Reddit, Quora, forums, YouTube, Arabic and English) plus the comment signals. Every item has a source link and quote. Output the ranked table with hook variants, format, CTA, difficulty and a reference competitor reel. Say which sources returned nothing (Arabic Reddit/Quora are usually thin).

## Step 8. Own-account audit, depth by stage

At `zero`: bio, positioning, coherence, and what little exists. At `early`/`working`: also winners and flops (index >= 1.5x / <= 0.5x of own format median), format mix, caption/hook/CTA/duration patterns (n >= 3 per side), trend (>= 10 mature posts). Compare against Step 6 competitors, not against hashtag samples.

**Lesson from the first run:** a hashtag sample gave a niche median of 448 views, while the five competitors' own medians were 329 to 10,015. Hashtag samples under-represent real accounts; benchmark against competitors' own reels.

## Step 9. Report, insights, dashboard

Write `report.md` (Egyptian Arabic) in this order: الخلاصة · مرحلة العميل والنيش (the confirmed sentence, constraints, stage) · تماسك المواضيع · النيشات الفرعية الخمسة · المنافسين (table + per-competitor winners with links) · الأنماط المتكررة (counts + links) · الفورمات (what appeared, including ones outside the ten) · أسئلة واعتراضات الجمهور (with sources) · أفكار الفيديوهات (ranked table) · تقييم الحساب نفسه · خطة 30 يوم · ما لا يمكن إثباته.

Then `insights.json` (see `references/insights-schema.md`) and:

```bash
python3 -I scripts/build_dashboard.py --analysis <dir>/analysis.json --insights <dir>/insights.json --competitors <dir>/competitors.json --out <dir>/dashboard.html
```

**Not built yet:** dashboard sections for competitor patterns, formats, audience questions and the ideas table. Until they exist, those live in `report.md` and the JSON files; do not promise them in the dashboard. Open the dashboard in a browser before handing it over (no overlapping text, no horizontal scroll at 390px, dark mode readable).

## Optional

- Hand the best reel URLs to `reels-scripting`; use `hook-generator` for hook variants.
- Save `analysis.json` per date to diff progress later.

## When things go wrong

- Private account: say so and stop.
- Fewer than 12 posts: light audit only; say winners/losers/timing need more history.
- CDN 403 on images or video: the environment blocks Instagram's CDN. Tell the user which hosts to allow, offer the paid Apify route with its price, never route around the block.
- Apify errors: report the exact message; no retry loops. A 502 on Apify's sync endpoints is a gateway issue; the scripts use async runs.
