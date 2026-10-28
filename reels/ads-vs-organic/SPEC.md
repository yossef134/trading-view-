# SPEC: الإعلان الممول ضد المحتوى (Storyline B: الرسايل اللي بتوصلك)

GOAL:    A doctor who planned to "just run an ad" ends the reel convinced that consistent content comes first and the ad only amplifies it, then follows Yossef.
OUTPUT:  HyperFrames, 1080 x 1920 (9:16 Reel), 30 fps.
TIME:    the voice is the clock. Two clocks exist:
         - recording clock: assets/voice/voice-norm.wav, 83.95 s = voice-raw.mp3 [7.25–84.10] + [94.85–101.95]
           (the raw file opens with a 6 s "Free Audio Post Production by Auphonic" tag, cut; the CTA was recorded twice, the second take is kept).
         - cut clock: assets/voice/voice-cut.wav, 71.04 s. tools/cut.py shortens every pause (0.12–0.22 s kept, 0.4 s at scene seams,
           10 ms crossfades) and writes assets/voice/cut-map.json, the knots between the two clocks.
         The film runs 73.04 s on the cut clock (the end card holds 2 s after the last word).
         hook, ad, split and stairs were choreographed on the recording clock; build.py injects `retime()`, which moves each tween
         onto the cut (a pause may speed a move up, never past 2x, and nothing spills past its scene). lens, base, claim and
         endcard are written directly on the cut clock. Word stamps on both clocks: assets/voice/words-cut.json.

## Scenes (cut clock)
| Scene | Starts | Length | Anchor words (cut clock) |
|---|---|---|---|
| hook | 0.000 | 6.364 | «إعلان ممول» 4.04 · «صح؟» 5.90 |
| ad | 6.364 | 20.021 | «يضيّع فلوسك» 9.11 · «لناس أكتر، أيوه» 12.10–13.07 · «مليون إعلان» 18.72 |
| split | 26.385 | 13.199 | «باستمرار» 29.80 · «عايز يكشف» 36.32 |
| stairs | 39.584 | 4.914 | «خطوة أخيرة» 42.14 |
| lens | 44.498 | 9.802 | «محتوى قيّم» 45.82 · «هيكبّر» 48.84 · «عروض وخصومات» 51.20 · «هيكبّر» 53.06 |
| base | 54.300 | 2.740 | «فالأساس» 54.44 · «الثقة» 56.74 |
| claim | 57.040 | 7.540 | «أهم» 59.50 · «مليون» 59.82 · «مرة» 60.32 · «هتصرف» 62.90 |
| endcard | 64.580 | 8.460 | «الفولو» 65.48 · «أنا» 66.66 · «يوسف» 66.84 · last word 70.78 |

Whisper puts some word starts inside the pause before them («أنا» landed 0.4 s early in v3); cut.py snaps every start to the end of its pause. Hits are placed on the snapped stamps.

## Copy
Every spoken and on-screen line is Yossef's approved script (2026-10-28), verbatim. On-screen DMs, post titles, sticker labels and the ad label are illustrative props drawn from his own words ("السعر والفصال", "خصم على الكشف", "عايز أحجز", "شكراً يا دكتور"); no metrics, names or results appear anywhere.

## LOOK
Identity A from `DESIGN.md` (the brand file is normative): white graph-paper ground, navy #13213F ink, orange #FF6A13 once per frame as a fill behind navy text, Rubik Medium upright for Arabic, Indie Flower bold for English words. No grain, no gradients, no glow. RTL everywhere.
The caption band (y 1180–1320) stays clear of every object while captions run (ad → lens).

## OBJECTS
- Phone: 540 x 1080 px at (240, 210), 20 px black bezel, 88 px outer radius, a status bar (time 9:41, battery), screen #FFFFFF 500 x 1040. In split screen each phone scales to 0.62 (left centre 317,805 / right centre 702,805).
- Ad post: a feed card with the label «إعلان ممول», an image block and the line «خصم على الكشف». It duplicates into eight copies for «مليون إعلان».
- DM bubbles: ad side «بكام الكشف؟» «فيه خصم؟» «آخر سعر كام؟» «طب ممكن أقل؟» in grey; content side one bubble «عايز أحجز» in orange.
- Content posts: feed cards with the same round avatar (a navy initial «د»), titled «نصيحة»، «معلومة»، «سؤال وجواب».
- People (src/people.js): thirteen flat sticker busts, men and women, five in hijab, four skin tones, white cut-out edge and soft shadow. For «لناس أكتر» the phone steps back to 0.58 and they pop up around it nearest first, 0.1 s apart, as three rings go out from the phone; they nod on «أيوه», go grey on «بس لو مش بتقدّم قيمة», and drop out of frame one by one.
- Magnifier: the stairs' orange block opens into a glass (360 px, 16 px orange rim, navy handle). It rides on the lens scene's paper and blows up whatever it covers (scale 1.3).
- Staircase: three navy blocks rising right to left, «محتوى» «ثقة» «إعلان»; the ad sits on the last step.
- Balance (claim): a navy beam on a stand; the right pan holds five ticked content tiles, the left pan the «إعلان ممول» badge and the bills. The pans counter-rotate so they always hang level.

## MOTION
- Enter: expo.out 0.5 s or back.out(1.7–2) for stickers thrown in. Exit: power3.in 0.25 s. Camera: power2.inOut 0.6–0.75 s for pans, power3.inOut 0.35–0.42 s for whips, power1.inOut for slow pushes (1.06x).
- Words: per word, rise 40–46 px with scale 1.25 → 1, back.out(2), on their spoken word. Stamps: scale 1.5–1.7 → 1 in 4 f, no ease, then a 0.3 s elastic shake of the frame.
- Landing objects squash (scaleY 0.82, scaleX 1.04, yoyo) and nudge the frame 14 px.
- Motion blur on for the whole film.

## SHOTS
| Scene | Spoken | Hero move | Hands off by |
|---|---|---|---|
| hook | كلهم بيقولولك: مش هتعرف تسوّق لعيادتك صح... غير لما تعمل إعلان ممول. يا ترى الكلام ده صح؟ | Speech bubbles crowd the frame, the line slams in word by word, «إعلان ممول» lands on orange, «صح؟» stamps. | «إعلان ممول» is carried into the post's label |
| ad | وهقولك كمان ليه الإعلان لوحده ممكن يضيّع فلوسك. الإعلان الممول هيوصّلك لناس أكتر، أيوه. بس لو مش بتقدّم قيمة... هتلاقي النتيجة مش عاجباك. اللي هيكلمك... السعر والفصال وخلاص. | Bills fall out of the phone; the crowd of people pops up, nods, greys and walks off; eight copies of the ad; everything greys; the inbox opens on four haggling bubbles. | the phone slides into the left half |
| split | طب إيه فايدة المحتوى الأورجانيك هنا بقى؟ إن المريض بيشوفك باستمرار... عايز يكشف عندك أو يعمل معاك العملية. | Two phones; posts every day on the right; the post grows, «إنت» highlighted, a heart; «عايز أحجز». | the right phone takes the centre |
| stairs | الإعلان الممول مهم، بس بيكون خطوة أخيرة في الـ scaling. | The phone shrinks into the first step; the stairs build; the ad block lands on top. | the ad block rounds into a disc |
| lens | لو الأساس بتاعك محتوى قيّم ومعلومات ونصايح، الإعلان هيكبّر ده للمريض. إنما لو الأساس عروض وخصومات، برضه هيكبّر ده للمريض. | The disc opens into a glass. Three content stickers are thrown in on their words; the glass swoops over them and blows them up; the camera follows a dashed arrow to a patient («شكراً يا دكتور», hearts). Whip down the paper to the offers («عروض» tag, «٪ خصومات» burst): same glass, same blow-up, the arrow leads to a patient asking «بكام؟ فيه خصم؟ آخر سعر كام؟». Whip back home. | the three content stickers stay put |
| base | فالأساس عندك هو المحتوى وبناء الثقة. | The stickers drop and burst into the bottom three bricks, two more bricks fall on top, «الأساس» slams, the top brick turns orange on «الثقة». | orange flood out of the top brick |
| claim | واستمراريتك بقى في المحتوى ده أهم مليون مرة من أي إعلان ممول، حتى لو هتصرف فيه فلوس كتير. | A week of tiles ticks off day by day; «أهم» slams with the impact; a 1,000,000 odometer spins and lands on «مرة» inside a white scribble; the claim steps up and a balance rises: content lands heavy, the ad badge and five bills land on the other pan and it barely moves. | the type clears; the orange field stays |
| endcard | متنساش الفولو الجميل بتاعك. أنا يوسف، وبساعد الدكاترة يعملوا محتوى يبيع ويبني ثقة مع المريض. | The field contracts into «متابعة»; a hand whips in and taps it (ripple, burst) → «متابَع ✓»; the orange arrow draws to the username and nudges twice, then turns ink; «أنا» then «يوسف» slams on its word over an orange marker; the line rises word by word with three stickers (stethoscope, play, heart) on «الدكاترة», «محتوى», «ثقة». | end, 2 s hold |

## Captions
The speech is captioned (most viewers watch muted): 3–5 words a group, RTL, Rubik 500 58 px, centred at y 1196. Off wherever the same words are big on screen: the hook, the split question, «خطوة أخيرة / في الـ scaling», the lens kickers and stickers, the foundation, the claim and the end card.

## SOUND
- Voice: Yossef's recording, pauses cut, normalised to −16 LUFS, peak ≤ −1.5 dBTP.
- No bed yet (HeyGen's catalogue is blocked from this session).
- Effects (tools/sfx.py, bundled library, pitch-shifted b/c takes): pops on every sticker and person, whooshes on camera whips and hand-offs, pings on messages, one impact on «أهم».

## BANNED
Everything in spec.md's default list, plus: Instagram/WhatsApp/Facebook UI branding; any metric, follower count, price or result on screen (the only numerals are the day labels and the spoken «مليون»); doctor or patient names; letter-by-letter effects (they break Arabic joining); LTR word reveals; English words on screen except «scaling» as spoken.

## QA
- 0.0 s: the hook line is readable as a thumbnail.
- 6.36 s: the carry-across of «إعلان ممول» into the post label.
- 12.9 s: the full crowd around the phone.
- 18.9 s: the «مليون إعلان» stack.
- 49.5 s: the glass over the content, the arrow to the patient.
- 60.4 s: «أهم 1,000,000 مرة».
- 61.8 s: the balance down on the content side.
- 66.9 s: «يوسف» on its word.
- 72.9 s: the end card held.
- Every word of copy inside y 168–1330 px.
