---
name: broll-shots
description: After the script is locked, gives the user a per-line B-roll shot list for the filming day. Every spoken line gets one quick shot (2 to 3 minutes to film, phone only, no crew) that backs up what the user is saying, tuned to the reel type (storytelling, educational, demonstration). Use when the user says "broll", "b-roll", "بيرول", "اللقطات الداعمة", "هصور ايه مع كل جملة", or after the script is approved and filming is next.
---

# B-roll Shots

Input: the approved script (after the hook is confirmed and the script passes its gate). Output: a shot list the user films once, then lays over the talking head so each line has a visual that proves or shows it.

Write the list in the user's language (Arabic if the script is Arabic). Shot descriptions are plain instructions, no jargon.

## Rules for every shot

- Filmable in 2 to 3 minutes. Phone only, no tripod needed, no actor, no travel, no purchase.
- Uses what is at the user's desk, room, screen, hands, or home/work place. Ask once what they have access to if unknown (place, props, screen), then do not ask again.
- Shows the thing the line names (the noun or action), not a mood. "He opened the drawer" gets a drawer opening, not a sunset.
- 2 to 4 seconds on screen. Say how long to hold it.
- One shot per line or per beat. If two lines share a visual, give one shot for both.
- Skip a line when the face is the stronger visual (the hook if `visual-match` picked the talking head, emotional peaks, the CTA). Mark it `skip: stay on face` with one reason.
- No stock-feel shots (typing on laptop, coffee, city skyline) unless the line literally says it.
- Do not invent facts, numbers, or screens the user does not have. If a shot needs a screen the user may not have, offer an alternative that does not.

## Shots by reel type

Pick the type from the script. A reel can mix two.

- **Storytelling:** the place, the object in the story, hands doing the action, a re-creation of the key moment (reaching, opening, walking in), a screenshot or message the story mentions.
- **Educational:** the thing being explained shown physically (the tool, the product, the page), a screen recording of the step, hand pointing at the part, a quick sketch on paper or whiteboard, before/after side by side.
- **Demonstration:** close-up of each step in order, hands-in-frame over-the-shoulder angle, the result shot, a before/after, the mistake shot (the wrong way) when the script contrasts right and wrong.

## Output

For each line:

| # | Script line (short) | Shot | How to film (2-3 min) | Hold |
|---|---------------------|------|-----------------------|------|

Then:

1. **Shoot order:** group shots by location and setup, so the user films everything in one pass (all desk shots, then all screen recordings, then all other places).
2. **Total filming time:** a sum, kept under 20 minutes. If over, cut the weakest shots first.
3. **Must-have shots:** the 3 shots the reel dies without.
4. **Skipped lines:** which lines stay on face and why.

Then stop. The user films. Do not generate assets.

## Skip conditions

- User says the reel is face-only (no B-roll): skip the whole skill.
- Footage already exists for every line: skip, or only list gaps.
