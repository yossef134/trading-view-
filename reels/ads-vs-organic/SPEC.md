# SPEC: الإعلان الممول ضد المحتوى (Storyline B: الرسايل اللي بتوصلك)

GOAL:    A doctor who planned to "just run an ad" ends the reel convinced that consistent content comes first and the ad only amplifies it, then follows Yossef.
OUTPUT:  HyperFrames, 1080 x 1920 (9:16 Reel), 30 fps.
TIME:    ~73 s x 30 = ~2190 frames, estimated from the script at ~2.3 words/s.
         Yossef's recorded voiceover is the clock: once it arrives, every shot is retimed to its anchor word from the transcript.

## Copy
Every spoken and on-screen line is Yossef's approved script (2026-10-28), verbatim. On-screen DMs, post titles and the ad label are illustrative props drawn from his own words ("السعر والفصال", "خصم على الكشف", "عايز أحجز"); no metrics, names or results appear anywhere.

## LOOK
- Ground: solid #F3EEE7 (warm plaster, the colour of a clinic wall), 2% monochrome noise. No gradients across the full frame.
- Ink: #14213D (deep navy). Every word meant to be read, every outline.
- Accent: #FF5A4E (coral). One focus per shot only: «صح؟», the «عايز أحجز» DM, the magnifier rim, «مليون مرة», the follow button.
- The ad side: desaturated #9AA0A8 grey for bubbles, the duplicated ads and the haggling.
- Display face: Alexandria 800 (Arabic), sized 66–112 px, line height 1.3, tracking 0, one line per row (`nowrap`). Stamps 150–230 px. Alexandria runs wide: a 112 px line holds about 8 Arabic letters per 860 px.
- Body face: Alexandria 500, 44–56 px. Captions: Alexandria 700, 64 px base / 46 px min, ink on a #F3EEE7 card at 92% when over phones.
- Medium: the product UI of a phone. A generic messaging app and feed (no Instagram/WhatsApp branding).
- Light and depth: one soft contact shadow under each phone, 0 40px 80px rgba(20,33,61,0.18). No glow, no blur halos, no vignette.
- Direction: RTL everywhere (`dir="rtl"`). Word-by-word reveals run right to left.

## OBJECTS
- Phone: 540 x 1080 px at (240, 210), 20 px black bezel, 88 px outer radius, a status bar (time 9:41, battery), screen #FFFFFF 500 x 1040. In split screen each phone scales to 0.62 (left centre 317,805 / right centre 702,805), so text inside a phone is at least 46 px.
- Ad post: a feed card with the label «ممول», an image block in #E4DCD2, and the line «خصم على الكشف». In the ad world it is grey; it duplicates into a stack for «مليون إعلان».
- DM bubbles: received bubbles with a real tail, 40 px radius, 48 px text. Ad side: «بكام الكشف؟» «فيه خصم؟» «آخر سعر كام؟» «طب ممكن أقل؟» in grey. Content side: one bubble «عايز أحجز» in coral.
- Content posts: feed cards with the same round avatar (a navy initial «د»), headed with a day name (السبت، الحد، الاتنين، التلات) and titles «نصيحة»، «معلومة»، «سؤال وجواب».
- People: small round avatars (initials, 64 px) that flow into the ad phone for «لناس أكتر». These are objects, not decoration.
- Magnifier: a glass lens 360 px across, a 14 px coral rim, a navy handle at 45°. Whatever sits under it is drawn at 1.8x.
- Staircase: three navy blocks rising right to left, labelled «محتوى» «ثقة» «إعلان». The ad sits on the last step.

## MOTION
- Enter: expo.out 0.5 s (15 f). Exit: power3.in 0.25 s (8 f). Camera/colour: power2.inOut 0.6 s (18 f).
- Springs on bubbles and the follow button only: back.out(1.4), scale 0.75 → 1 in 0.12 s from the sender's corner.
- Title entrances vary: per word grey → ink 0.08 s apart (S1), whole line blur 8 → 0 px in 0.18 s (S6), a slot roll of one word (S11), stamp scale 1.3 → 1 in 4 f with no ease (S1 «صح؟», S13).
- Staggers: words 0.08 s, bubbles 0.35 s apart, matched to the voice.
- Landed titles hold dead still until they leave.

## SHOTS (estimated; retimed to the voice)
| # | Time (s) | Spoken | Hero move | Hands off by |
|---|---|---|---|---|
| S1 | 0–6.5 | كلهم بيقولولك: مش هتعرف تسوّق لعيادتك صح... غير لما تعمل إعلان ممول. يا ترى الكلام ده صح؟ | Frame 0 already shows «مش هتعرف تسوّق لعيادتك صح» in navy, 130 px. «غير لما تعمل إعلان ممول» lands word by word. «صح؟» stamps in coral, 220 px. Hit on the stamp. | «إعلان ممول» shrinks into the «ممول» label of a post (carry across) |
| S2 | 6.5–10 | وهقولك كمان ليه الإعلان لوحده... ممكن يضيّع فلوسك. | The badge holds, the ad post builds around it, then the phone around the post. Two paper bills slide out of the phone's edge and drop out of frame. | camera holds on the phone |
| S3 | 10–14 | الإعلان الممول هيوصّلك لناس أكتر، أيوه. | Avatars stream into the phone from both sides, 3 at a time. | the stream stops on «بس» |
| S4 | 14–21 | بس لو مش بتقدّم قيمة، ولا المريض حس إنك فعلاً تستاهل الثقة دي، حتى لو صرفت مليون إعلان، هتلاقي النتيجة مش عاجباك. | The people fade one by one, unconvinced. On «مليون إعلان» eight copies of the ad pop up around the phone. On «مش عاجباك» everything greys out and drops 40 px. | inbox opens (iris from the DM icon) |
| S5 | 21–27 | اللي هيكلمك في الغالب هيكون مش جاد، وهيركّز على السعر والفصال وخلاص. | Four grey haggling bubbles arrive 0.35 s apart, each with a muted ping. | the phone slides to the left half |
| S6 | 27–30 | طب إيه فايدة المحتوى الأورجانيك هنا بقى؟ | Split screen: the grey phone at the left at 0.62, a white phone arrives at the right. The question blurs in across the top, 110 px. | the right phone takes focus |
| S7 | 30–35 | إن المريض بيشوفك باستمرار. | On the right phone, posts arrive one per day name, the same avatar each time. | the latest post scales up |
| S8 | 35–40 | بيحس إنك فعلاً بتحل مشكلته، وإن الحل ده بيكلمه هو بس. | The post («لو إنت بتعاني...») grows toward the camera to 1.75x. A coral highlighter marks «إنت», then a navy heart pops on the card. The left phone dims to 40%. | a DM notification drops on the right phone |
| S9 | 40–44 | وده فعلاً اللي بيجيب لك واحد عايز يكشف عندك أو يعمل معاك العملية. | The coral «عايز أحجز» bubble lands, with a clean ping. The split collapses: the left phone exits left, the right phone moves to centre. | the phone shrinks onto the top step of a staircase |
| S10 | 44–49 | الإعلان الممول مهم، بس بيكون خطوة أخيرة في الـ scaling. | The staircase builds right to left: «محتوى» → «ثقة» → «إعلان». The ad block lands on the last step. | the ad block becomes the magnifier (morph) |
| S11 | 49–58 | لو الأساس محتوى قيّم ومعلومات ونصايح، الإعلان هيكبّر ده للمريض أكتر. إنما لو الأساس عروض وخصومات، برضه هيكبّر ده. | The magnifier passes over a content card (it reads 1.8x), then over the «خصم على الكشف» tag and the haggling bubbles (they grow too). | the lens pulls back |
| S12 | 58–62 | فالأساس عندك هو المحتوى وبناء الثقة. | The content cards stack as a foundation, with «الأساس» in navy. | colour flood to coral |
| S13 | 62–67 | واستمراريتك بقى في المحتوى ده... أهم مليون مرة من أي إعلان ممول، حتى لو هتصرف فيه فلوس كتير. | Coral flood from the centre (0.45 s). «أهم / مليون مرة» stamps in navy, 150 px, then holds 2 s. A riser into an impact, once in the film. | the type clears; the coral field stays |
| S14 | 67–73 | متنساش الفولو الجميل بتاعك. أنا يوسف، وبساعد الدكاترة يعملوا محتوى يبيع ويبني ثقة مع المريض. | The coral field contracts into a «متابعة» button, which flips to «متابَع ✓» on «الفولو». «يوسف» wipes in right to left (never per letter: it breaks Arabic joining), and the line turns ink word by word. Holds 2.5 s. | end |

## Captions
The speech is captioned (most viewers watch muted). 3–5 words a group, RTL, Alexandria 700, centred inside the band at y 1180–1300 px. Captions are off in S1 and S13, where the big type is the spoken line.

## SOUND
- Voice: Yossef's recording, the clock. Normalised to −16 LUFS, peak ≤ −1 dBTP.
- Bed: a soft, warm minimal pulse at ~100 bpm at 0.14 under the voice. Held back in S4–S5 (near silence on the haggling), it opens in S9 on «عايز أحجز».
- Effects (sample files only, 2–3 takes rotated): message ping on each bubble, a whoosh on the S6 split, a pop on the staircase blocks, one riser into an impact on «مليون مرة».

## BANNED
Everything in spec.md's default list, plus: Instagram/WhatsApp/Facebook UI branding; any number, follower count, price or result on screen; doctor or patient names; letter-by-letter scramble effects (they break Arabic joining); LTR word reveals; English words on screen except «scaling» if spoken.

## QA
- 0.0 s: the hook line is readable as a thumbnail.
- 6.5 s: the carry-across of «إعلان ممول» into the post label.
- 18 s: the «مليون إعلان» stack.
- 25 s: four grey bubbles readable.
- 29 s: split screen, both phones inside 168–1330 px.
- 42 s: the coral «عايز أحجز» bubble.
- 53 s: the magnifier over the content card, 1.8x.
- 64 s: «أهم مليون مرة» held.
- 72 s: the end card held.
- Every word of copy inside y 168–1330 px, none under the right-hand rail (x > 960).
