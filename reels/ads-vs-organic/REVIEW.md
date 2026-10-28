# REVIEW: v2 (identity A, timed to the voice)

## State
- 86 s, 1080 x 1920, 30 fps. Eight scenes plus one captions track, retimed to `assets/voice/voice-norm.wav` (−16.4 LUFS, −1.5 dBTP).
- Identity A from `DESIGN.md`: white, navy, orange as a fill; Rubik Medium upright; Indie Flower bold for «scaling».
- Captions: 26 groups of 3–5 words, written from what Yossef actually said (corrected spelling), timed by Whisper word stamps. Off where the same words are already big on screen: the hook, the split question, «خطوة أخيرة / في الـ scaling», «الأساس», the claim and the end card.
- Sound: the voice plus 29 effects from the bundled HyperFrames library (pop, whoosh, notification, one bass impact on «أهم مليون مرة»). The b and c takes are pitch-shifted copies, so repeats are not identical.
- No music: HeyGen's catalog is blocked by this session's network policy.

## Not yet done
- Motion and transitions inspired by Yossef's Pinterest references: the pins cannot be opened here (pin.it and pinimg.com are blocked), and the files have not arrived yet.

## Measured
- `check`: 0 errors, 0 lint warnings. Seams (−0.2 s to +0.2 s) checked at every cut.
- Whisper "small" (multilingual, from an npm mirror, since Hugging Face is blocked) was used for the timing only; every caption was checked against the script by hand.
- The sound was measured, not heard.

## Warnings kept on purpose
- `contrast_aa_failure` at 81.2 s: the end card's words not yet spoken are pale (#C5CBD6) on purpose; each turns navy as Yossef says it.

## Notes for next time
- The raw recording opens with a 6 s "Free Audio Post Production by Auphonic" tag: cut it in every future recording, or export from Auphonic without it.
- Audio files are not committed (the repo is public).
