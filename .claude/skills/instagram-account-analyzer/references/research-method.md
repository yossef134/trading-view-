# Research method: real questions and objections -> video ideas

Run once per approved sub-niche (5). Use the `anthropic-skills:deep-research` skill with one subagent per
sub-niche when the Agent tool exists; otherwise do it directly with web search and fetch. Always add the
audience comments from `audience_signals.json`.

## Whose voice

Only the client's audience (for a doctor-marketing client: doctors and clinic owners asking about patients, content, pricing, ads, rules). Patients' complaints about doctors are a different audience and are excluded.

## The one rule

**Every question, objection or claim in the output carries a source link and a short verbatim or close-paraphrased
quote.** If no source exists, it does not go in. Never invent a question "people probably ask". If a source
returns nothing, report that it returned nothing.

## What counts as a real signal

- A person asks something in their own words (forum thread, Q&A site, comment, review).
- A person objects, doubts or complains (price, trust, "does it work", legal limits, time).
- The same question appears in several places (frequency is the strongest evidence).

Not signals: SEO listicles, agency blog posts, competitor sales copy (use them only to see what competitors claim).

## Sources and honest expectations

| Source | How | Expect |
|---|---|---|
| Google | search the sub-niche + question words (Arabic AND English), read "People also ask" / related searches / forum results when shown | Best general coverage |
| Reddit | `site:reddit.com` + niche terms, English first | **Thin for Arabic niches** |
| Quora | `site:quora.com` + niche terms | Often blocked or thin in Arabic |
| Arabic forums / syndicate or professional groups / review sites | search by profession + problem | Varies; worth trying |
| YouTube | titles and top comments of niche videos | Good for objections |
| Instagram comments | `fetch_instagram.py comments` on the competitors' top reels | Few real questions per reel; lead-magnet requests are common (e.g. "send the sheet"), which is itself a signal |
| TikTok / Facebook | only if search surfaces public pages | Mostly not reachable |

Search in the client's dialect and in English, then translate. State at the end which sources produced signals
and which produced none.

## Query templates (adapt per sub-niche)

- `<sub-niche> أكبر مشكلة` / `<sub-niche> ليه مش بيجيب` / `<sub-niche> غالي` / `<sub-niche> هل ينفع`
- `<sub-niche> how to`, `<sub-niche> worth it`, `<sub-niche> mistakes`, `<sub-niche> vs`
- `site:reddit.com <english term> "is it worth"` / `"how do I"` / `"why is my"`
- Legal and regulatory limits in the client's country (e.g. what a profession may advertise), because
  these show up as real objections

## Output per sub-niche

Table, ranked by (how many independent sources) then (how painful):

| # | Question / objection (their words) | Type | Sources (links + quote) | Seen in N sources | Video idea | Hook (2 variants) | Format (see content-formats-2026.md, open vocabulary) | CTA | Reference competitor reel |
|---|---|---|---|---|---|---|---|---|---|

Rules for the ideas:
- The hook answers the question or voices the objection in the viewer's words, in the first line.
- Pick the format from what actually won for competitors AND what the client can produce (on camera? time? editor?).
- Give each idea a difficulty (easy / medium / hard) and a one-line reason it fits the stage.
- Objections become "myth vs reality", "why X is not the problem", or "the cost of not doing X" videos; questions become
  explainers, walkthroughs or ranked lists. Say which.
- Keep at most 8 ideas per sub-niche; cut weaker ones instead of padding.

## Closing

End with: sources that worked, sources that returned nothing, the three highest-frequency questions overall,
and what could not be verified.
