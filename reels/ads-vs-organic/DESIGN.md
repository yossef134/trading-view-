---
name: Yossef Massad: identity A ("أبيض نضيف")
colors:
  ground: "#FFFFFF"
  ink: "#13213F"        # navy: every word meant to be read, structural shapes
  accent: "#FF6A13"     # orange: one focus per frame, as a FILL behind navy text, never as text on white
  surface: "#EEF1F6"    # navy-tinted light surface: cards, inactive panels, followed button
  muted: "#7D8597"      # secondary labels (large text only, ≥ 48 px)
  ad-bubble: "#E9ECF2"  # the "ad side" bubbles and props
  ad-ink: "#5A6378"     # text on ad-side bubbles
  device: "#0B1328"     # phone bezel
typography:
  arabic:
    family: Rubik
    weight: 500          # Medium, upright (Rubik's Arabic has no true italic)
    files: [assets/fonts/rubik-arabic.woff2, assets/fonts/rubik-latin.woff2]
  english:
    family: Indie Flower
    weight: bold         # the family ships Regular only; bold is synthesised (font-weight 700 + 1.2 px text stroke)
    files: [assets/fonts/indieflower-latin.woff2]
    use: English words only (e.g. «scaling»), never for Arabic
  sizes:
    hero: 110–150 px
    stamp: 160–230 px
    line: 60–96 px
    caption: 60 px
    floor: 28 px (2.6% of 1080)
spacing:
  safe-band-y: [168, 1330]
  caption-band-y: [1180, 1320]
  margin-x: 80
ground:
  paper: white with a navy graph-paper grid, 60 px cells at 7% navy, a 20% navy dot every 240 px (x 60+240k, y 120+240k)
  paper-on-orange: the orange field carries the same 60 px grid in 16% white
components:
  highlight: orange block behind a navy word, 0 34 px padding, 24 px radius
  bubble-hot: orange bubble, navy text
  phone: device bezel #0B1328, white screen
  sticker: white cut-out edge (7 px) + soft navy shadow (0 12 px 14 px, 20%); people, icons and props
  people: flat busts from src/people.js (men and women, hijab or not, four skin tones), tops and scarves in navy, greys and peach only
  connector: dashed navy arrow (8 px, 4/22 dash) that draws itself and leads the camera to the next idea
---

# Identity A: white, clean

**What it is for.** Yossef talks to doctors and service owners who already have clients. The look should feel like a clean clinic and a trustworthy older brother: white space, one navy voice, and an orange that only shows up where the eye must go.

## Do
- White ground, navy ink. Orange appears once per frame, on the one thing that matters: the stamp word, the booking bubble, the ad step, the follow button, the lens rim.
- Orange behind navy text (a highlight block, a filled bubble). Orange text only sits on navy.
- Rubik Medium for every Arabic word. Hierarchy comes from size and colour, not from weight.
- English words in Indie Flower bold, slightly larger than the Arabic around them (×1.3), as a hand-written aside.
- Arabic reveals run per word or as a right-to-left wipe. Never per letter (it breaks Arabic joining).

## Motion (from Yossef's Pinterest references, adapted, not copied)
- The ground is graph paper so camera moves read: the camera pushes in slowly on holds, pans along a dashed connector to the consequence, and whips (0.35–0.4 s, motion blur) between ideas.
- Things are thrown in as stickers from their own side with an overshoot; landings squash and nudge the frame.
- Kicker + slam: a small line sets up, the key word lands big with a 4-frame stamp and a short frame shake.
- Numbers that matter roll like an odometer and get a hand-drawn scribble around them.
- Every scene hands over through an object the next scene keeps.
- Characters act the line: a pose swap (worried → gasp → hand on chin) or a face that changes (smile turns over) on the spoken word.
- A moving layer is lifted above the others by motion blur: keep an element still while something must be drawn over it.

## Don't
- Orange text on white (2.9:1, unreadable on a phone).
- Gradients, glow, neon, glass, dark voids.
- More than one orange element in a frame.
- Italic or slanted Arabic.
