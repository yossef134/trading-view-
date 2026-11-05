# audit_content.json (written by Claude for each audit)

Numbers in the report come from the data files; the words come from here. Egyptian Arabic, simple,
no statistics jargon (index, median), no tool names, no costs. Every claim must be checkable in the data.

```jsonc
{
 "mode": "case_study" | "client",          // the user decides per doctor
 "brand": "@yossef.content2sales",
 "date": "YYYY-MM-DD",
 "doctor": {"name": "", "specialty": "", "handle": ""},
 "opening_quote": "",                        // the doctor's own words from call_notes.md; empty if no call yet
 "diagnosis": "",                            // 2-3 lines: strongest asset + what is missing
 "numbers_intro": "",
 "kpi_notes": {"followers": "", "posts": "", "views": "", "best": ""},
 "best_video": {"url": "", "title": "", "why": "", "lesson": ""},
 "problems": [                               // exactly 3, each with a COMPLETE fix (this is the real value)
  {"title": "", "evidence": "", "fix": "", "example": ""}   // example: ready text such as a rewritten bio
 ],
 "video_intro": "",
 "video_ratings": [{"item": "الإضاءة", "score": 0-10, "note": "", "fix": ""}],  // from the user's video_review.md; scores proposed by Claude from the user's words need the user's OK
 "video_notes": [""],                        // Claude's observations from sheets/transcripts
 "privacy_note": "",                         // patient names/faces/scans without visible consent
 "patterns_intro": "",
 "patterns": [                               // the 3 patterns from scan/summary.md, ALL revealed
  {"title": "", "evidence": "counts", "examples": [{"url": "", "label": "", "views": 0}], "you": ""}
 ],
 "next": {                                   // depends on mode
  "title": "", "intro": "", "bullets": [""],
  "cta": ""                                  // client mode: invitation to work together; case_study: usually empty
 },
 "measure_note": ""                          // baseline date + re-measure at 30/60 days
}
```

Rules
- Do not compare reel VIEWS with image LIKES (different metrics). Images have no public views.
- Keep ratios consistent with the numbers shown in the report itself.
- Sound, delivery and presence come from the user's video review, never from Claude.
- Never praise a CTA like «هشوفك في الحلقات الجاية»: the user wants a CTA that drives comments (question) or a guide file requested in comments/DM.
