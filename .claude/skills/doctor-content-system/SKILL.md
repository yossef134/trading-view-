---
name: doctor-content-system
description: >
  Content system for doctors on Instagram, built step by step with the user. Track 1 is the free audit for a doctor before they become a client (call + quick account analysis + a valuable report that also creates curiosity, plus a baseline snapshot for case studies). Track 2 is the full strategy for a paying doctor (patient avatar, niche topics, patient-voice research, 5-10 competitors with reel scripts, 60-90 funnel-staged ideas, scripts). Track 3 runs Track 2 on the user's own account, where the audience is doctors. Use when the user says "free audit", "اوديت", "حلل حساب الدكتور", "دكتور جديد", "استراتيجية محتوى لدكتور", or sends a doctor's Instagram account. Output: infographic dashboard + Markdown, in Egyptian Arabic.
---

# Doctor Content System

**This skill is being rebuilt step by step with the user. Only the steps marked BUILT exist. Do not improvise the steps marked PLANNED: tell the user they are not built yet.**

## Agreed decisions (2026-11-05)

- Audience depends on the track: Track 1 analyses the doctor's own account; Track 2 targets the doctor's PATIENTS; Track 3 (user's own account) targets DOCTORS.
- Output: infographic dashboard + MD file, in two versions: a **client version** (simple, persuasive, genuinely useful) and an **internal version** (all numbers, links, assumptions, cost).
- Track 1 report must give real value (concrete problems with full fixes), and only hint at the deeper patterns, to create curiosity.
- Every competitor and research finding carries its link.
- Ask the user's approval before every new step, and before any paid step.
- Track 1 saves a baseline snapshot so a before/after case study can be made at 30 and 60 days.
- **Every change agreed in the conversation is written into this skill immediately** (user rule, 2026-11-05).
- Video review scores are **out of 10**, each with a note AND a fix; the user's criteria are in `forms/video_review.md` (hook verbal + visual, pauses/pace, body language, mic + denoise, external light, music, caption placement/style, on-screen title, CTA by question or guide file).

## Track 1 flow (agreed 2026-11-05)

1. Tailored pre-call questions sent to the doctor (Step 1) and his account pulled (Step 2).
2. The user reviews the videos (`video_review.md`), Claude proposes scores /10 from his notes, the user approves.
3. The audit report is built WITHOUT the call (Step 4); `opening_quote` stays empty.
4. **The call happens after the audit.** Before it, Claude writes `<dir>/call_questions.md` for the user (30-40 min, about 27 questions in 7 blocks: reaction to the audit + his first sentence about his problem; specialty and services incl. topics he refuses and employer limits; THE TYPICAL PATIENT (age, life, what she tried, wants, fears, top 5 questions, objections, who decides, how she finds and books him, platforms she uses) adapted from the user's «أنت زمان» form; his personality and script preference; filming logistics, equipment and patient consent; goal and baseline numbers for the case study; done-by-you vs done-for-you). Tailor every block to this doctor and to the audit findings; the generic first version is in the dr. Mostafa example under outputs. The answers feed Track 2.
5. The comprehensive analysis after the call IS Track 2 (the full strategy).

## Free route (tested 2026-11-05)

With `*.fbcdn.net` and `*.cdninstagram.com` allowed, video and covers download for free: `own_reels.py --cdn` (metadata about 0.003 USD per reel instead of 0.07 for an Apify copy) and `media.py grid`. Transcripts are free too since huggingface.co was allowed: `scripts/transcribe.py` (faster-whisper large-v3-turbo on CPU, about 25 s per reel, quality close to Apify's; pass `--vocab` with the specialty's terms and correct obvious term errors from context). Default per doctor: `own_reels.py --cdn --no-transcript` (about 0.01 USD) then `transcribe.py --videos <dir>/own_reels.json --vocab "..."`. Fall back to the Apify transcript (0.10 USD/reel) only if the local run fails. Run `scripts/preflight.py` first.

## Status

| Track | Step | Status |
|---|---|---|
| 1. Free audit | 1. Pre-call message + 15-min call guide + call notes | **BUILT**: `forms/audit_intake.md` |
| 1. Free audit | 2. Pull the account + baseline snapshot + look at 2 best / 1 weakest reel | **BUILT** (see below) |
| 1. Free audit | 3. Quick scan of 3-5 successful doctors in the same specialty | **BUILT** (see below) |
| 1. Free audit | 4. Report: client PDF infographic + client MD + internal MD | **BUILT** (see below) |
| 2. Full strategy | patient avatar (adapted from the user's "أنت زمان" form), niche topics, patient-voice research, competitors with scripts, 60-90 ideas, funnel table, scripts | PLANNED |
| 3. Own account | Track 2 with doctors as the audience | PLANNED |

## Track 1, Step 1: intake (BUILT)

1. **Tailor the pre-call questions to THIS doctor (user rule, 2026-11-05).** `forms/audit_intake.md` part (a) is only the base. Pull the account first (Step 2 commands 1-2), then: drop questions the account already answers (specialty, link, posting status), and add 3-6 questions about what the data shows (e.g. his best video and whether it brought patients, why posting stops, who makes the designs, where the bio link leads and how patients really book, ads history, speak freely vs read). Group them: about your work / about the content / your goal. Give the user the tailored text to send (WhatsApp or Google Forms).
2. The user runs the 15-minute call with part (b).
3. The user fills part (c) and saves it as `call_notes.md` in `outputs/doctors/<instagram-username>/<YYYY-MM-DD>/`, together with the doctor's form answers as `intake_answers.md`.
4. Do not start Step 2 until both files exist, or the user says to go ahead without them.

## Track 1, Step 2: account, baseline, own reels (BUILT, tested 2026-11-05 on a real OB/GYN account)

Work dir: `outputs/doctors/<username>/<YYYY-MM-DD>/`.

```bash
python3 -I scripts/fetch_instagram.py account <username> --limit 60 --out <dir>/raw.json      # about 0.03-0.16 USD
python3 -I scripts/analyze.py --raw <dir>/raw.json --out <dir>/analysis.json
python3 -I scripts/baseline.py snapshot --raw <dir>/raw.json --analysis <dir>/analysis.json --out <dir>/baseline.json
python3 -I scripts/own_reels.py --analysis <dir>/analysis.json --out <dir>/own_reels.json --cdn  # about 0.3 USD (transcripts); drop --cdn if the CDN is blocked (+0.07/video)
python3 -I scripts/media.py sheets --videos <dir>/own_reels.json --out-dir <dir>/sheets
```

**Facebook (optional, when the doctor has an active page; approved 2026-11-05):** `python3 -I scripts/fetch_facebook.py --url https://www.facebook.com/<page> --out <dir>/facebook.json --limit 30` (about 0.17 USD; use the normal page URL, not /share/). Compare followers, typical views and engagement with Instagram, and take address / title / hospital affiliation from the page for the bio. Lesson from the first doctor: his real audience was on Facebook (2,437 followers, about 1,400 typical video views) while Instagram had 115, so the advice became "move what works on Facebook to Instagram reels", not "nobody watches".

Then the USER reviews the same reels himself with `forms/video_review.md` (speaking style, presence, lighting, SOUND, script, editing; 1-5 + concrete notes) and saves `video_review.md` in the doctor's folder. Claude cannot hear audio: the user's judgement leads on sound, delivery and presence; on conflicts the internal report shows both and the doctor's version follows the user.

Claude also LOOKS at each sheet and reads each transcript. Note concretely: when the hook appears, who is on screen, what fills the screen (black frames, template glitches, watermarks), captions, length, ending/CTA, and any patient-privacy or consent risk (patient names, faces, scans). Case-study follow-up at day 30/60: re-run the first three commands into a new dated folder, then `baseline.py compare --before ... --after ... --out compare.md`.

Rules learned in testing:
- A format is only scored when it has >= 3 mature posts AND a median of at least 10; otherwise "11x the usual" can mean 9 likes vs 1.
- Posting under 0.5 posts/week is "rare", whatever the gap spacing.
- Reels with < 0.5 words/second have no speech; their transcript is noise (`has_speech: false`).
- Accounts with fewer than 3 scored reels: skip own_reels.py and say why.
- If the user stops a run, abort the Apify run too (`POST /v2/actor-runs/<id>/abort`), or it keeps charging.

## Track 1, Step 3: quick scan of doctors in the same specialty (BUILT, tested 2026-11-05)

About 0.3 USD. No transcripts or videos in this track (kept cheap).

1. Candidates: the doctor's form answer 7 plus Google through Apify (Instagram is reachable only through Apify here):
   write 4-5 queries like `site:instagram.com دكتور <التخصص>` / `site:instagram.com استشاري <التخصص>` into `<dir>/scan/queries.txt`, then
   `python3 -I scripts/research_fetch.py google --queries-file <dir>/scan/queries.txt --country eg --out <dir>/scan/google.json`
   and pull handles from result URLs and "(@handle)" in titles.
2. Verify: `python3 -I scripts/fetch_instagram.py profiles <handles...> --out <dir>/scan/candidates.json`. Keep same specialty, patient-facing, public, active. Pick 5 with a size mix (2 large to learn from, 3 nearer the doctor).
3. `python3 -I scripts/fetch_instagram.py reels <5 handles> --limit 20 --out <dir>/scan/peer_reels.json`
4. `python3 -I scripts/analyze_competitors.py --reels <dir>/scan/peer_reels.json --out <dir>/scan/peers_analysis.json`
5. Write `<dir>/scan/summary.md` (internal): peers table, top reels with links, repeated patterns with counts, and the comparison with the doctor's own account. Followers alone are not success (one peer had 64K followers and a 220-view median).

## Track 1, Step 4: the report (BUILT, tested 2026-11-05)

Agreed: client version = PDF infographic + MD, calm medical style, branded @yossef.content2sales, all 3 specialty patterns revealed; last section depends on `mode` (`client`: next step + invitation; `case_study`: what we will do together + re-measure at 30/60 days).

0. **HARD RULE (user, 2026-11-05): do not build or send the report until the user's `video_review.md` exists** (his notes on the videos lead). The call is NOT required before the report: the audit is built without it, and the call happens after (see the flow below).
1. Write `<dir>/audit_content.json` following `references/audit-content-schema.md`, using analysis.json, baseline.json, own_reels.json + sheets, scan/summary.md, call_notes.md and the user's video_review.md (when present).
2. `python3 -I scripts/build_audit.py --dir <dir> --content <dir>/audit_content.json`
   -> audit_client.html / audit_client.pdf / audit_client.md / audit_internal.md (Chromium via `scripts/render_pdf.js`).
3. Check every page before sending: `node scripts/render_pdf.js <dir>/audit_client.html /tmp/x.pdf --png <scratch>/p` and look at each PNG (overflow, reversed numbers, empty sections, consistency of numbers).
4. Send the PDF and MD to the user; the user sends to the doctor. Doctors' data stays local (outputs/doctors/ is git-ignored).

## Reusable lessons from the previous skill (`instagram-account-analyzer`)

Judge each reel against its own account's median; benchmark against real competitors, not hashtag samples; competitors must speak to the same audience; view video frames to judge formats; Google `site:reddit.com` then pull thread comments through Apify when the sandbox blocks those hosts; measure and quote costs before running (videos cost about 0.07 USD each).
