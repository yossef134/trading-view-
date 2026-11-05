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

## Status

| Track | Step | Status |
|---|---|---|
| 1. Free audit | 1. Pre-call message + 15-min call guide + call notes | **BUILT**: `forms/audit_intake.md` |
| 1. Free audit | 2. Pull the account + baseline snapshot | PLANNED |
| 1. Free audit | 3. Quick scan of 3-5 successful doctors in the same specialty | PLANNED |
| 1. Free audit | 4. Report (client + internal), dashboard | PLANNED |
| 2. Full strategy | patient avatar (adapted from the user's "أنت زمان" form), niche topics, patient-voice research, competitors with scripts, 60-90 ideas, funnel table, scripts | PLANNED |
| 3. Own account | Track 2 with doctors as the audience | PLANNED |

## Track 1, Step 1: intake (BUILT)

1. Send the doctor part (a) of `forms/audit_intake.md` (WhatsApp or Google Forms).
2. The user runs the 15-minute call with part (b).
3. The user fills part (c) and saves it as `call_notes.md` in `outputs/doctors/<instagram-username>/<YYYY-MM-DD>/`, together with the doctor's form answers as `intake_answers.md`.
4. Do not start Step 2 until both files exist, or the user says to go ahead without them.

## Reusable lessons from the previous skill (`instagram-account-analyzer`)

Judge each reel against its own account's median; benchmark against real competitors, not hashtag samples; competitors must speak to the same audience; view video frames to judge formats; Google `site:reddit.com` then pull thread comments through Apify when the sandbox blocks those hosts; measure and quote costs before running (videos cost about 0.07 USD each).
