# REVIEW: v3 (identity A, timed to the voice)

## v3 changes
- Hook: frame 0 is «كلهم بيقولولك:» with three speech bubbles already talking; three more pop in by 0.45 s; the line slams in word by word on the voice; the bubbles are blown out of frame at 3.2 s; «إعلان ممول» lands on an orange block at 4.45 s.
- Every seam is now caused by an object: badge carry (hook→ad), phone move (ad→split), phone into the first step (split→stairs), ad block into the lens (stairs→lens), the content card drops and flattens into the first brick (lens→foundation), the orange flood grows out of the top brick (foundation→claim), the orange field contracts into the follow button (claim→end).
- End card: on «الجميل بتاعك» an orange hand-drawn arrow draws down-left to where Instagram shows the username (aimed at x≈250, y≈1545; adjust if the platform UI sits elsewhere).
- Motion blur on (`data-motion-blur="on"`).

## State
- 86 s, 1080 x 1920, 30 fps. Eight scenes plus one captions track, retimed to `assets/voice/voice-norm.wav` (−16.4 LUFS, −1.5 dBTP).
- Identity A from `DESIGN.md`: white, navy, orange as a fill; Rubik Medium upright; Indie Flower bold for «scaling».
- Captions: 26 groups of 3–5 words, written from what Yossef actually said (corrected spelling), timed by Whisper word stamps. Off where the same words are already big on screen: the hook, the split question, «خطوة أخيرة / في الـ scaling», «الأساس», the claim and the end card.
- Sound: the voice plus 36 effects from the bundled HyperFrames library (pop, whoosh, notification, one bass impact on «أهم مليون مرة»). The b and c takes are pitch-shifted copies, so repeats are not identical.
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
