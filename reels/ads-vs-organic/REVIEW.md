# REVIEW: draft v1 (estimated timing, no audio)

## State
- Built from SPEC.md, storyline B. 8 scenes (`compositions/`), 73 s, 1080 x 1920, 30 fps.
- Timing is an estimate (~2.3 words/s). It waits on Yossef's voiceover: once it arrives, transcribe it (`--model small --language ar`, or `medium` if it is noisy), then move every beat to its anchor word.
- No audio yet: no voice, no music, no effects. HeyGen (music catalog) is blocked by this session's network policy (api.heygen.com, static.heygen.ai and api.openverse.org are not allowed), so only the 21 bundled offline effects are reachable today.
- No captions yet: they are built from the transcript's word timings, not from guesses.

## Creative calls
- Storyline B (two phones, split to one). A and C were not built (`STORYLINES.md`).
- S2: the phone builds around the carried badge instead of rising from below, so the hook's «إعلان ممول» lands inside the ad without a cut.
- S4: the people who arrived fade out one by one on «ولا المريض حس إنك تستاهل الثقة», which fills a 5 s stretch that had nothing moving.
- S8: the lifted post reads «لو إنت بتعاني...» (shortened so it holds one line), with a highlighter on «إنت» and a heart.
- S11: a real magnifier. A 1.8x copy of the stage is cut to the lens, driven by `--lx/--ly`.
- Every Arabic reveal is per word or a right-to-left wipe. Per-letter effects break Arabic joining.

## Measured
- `npx hyperframes check`: 0 errors, 0 lint warnings, contrast 88/88 passed.
- Seams checked frame by frame (−0.2 s to +0.2 s) at all 7 cuts: hook→ad (badge carry), ad→split (phone move), split→stairs, stairs→lens (coral disc) all continue without a jump.
- Phone-width sheet (360 px): every line meant to be read is legible. The phone status bars and avatar initials are texture (`data-layout-ignore`).

## Warnings kept on purpose
- `film_silent`: no audio until the voice and music land.
- `line_unread` at 26.5 s on the inbox bubbles: a false positive at the ad→split seam. The same bubbles continue in the split's left phone, so they are on screen from 22 s to 41 s.

## Weakest shots, and what I would change next
- S12 «الأساس» (58–62 s) is the plainest frame: five navy bricks under a word. It could build as a real foundation under the staircase from S10.
- S2's bills are flat; they read as money, but are the least crafted object.
- The lens rim drops a soft shadow at 49.1 s that the coral disc before it does not have (a 1-frame change at the seam).
