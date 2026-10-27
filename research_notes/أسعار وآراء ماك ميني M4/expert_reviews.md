# Expert reviews of the Apple Mac mini M4 and M4 Pro (as of 27 Oct 2026)

**Method and reliability caveat.** In this session WebFetch and curl were blocked: the egress proxy refused most review hosts (techradar.com, arstechnica.com, notebookcheck.net, tomsguide.com, tomshardware.com, etc.). Every finding below therefore comes from web-search result summaries, not from reading the full review pages. Direct quotes are limited to short phrases that the search results showed in quotation. Numeric scores that came only from aggregator or syndicated pages are labelled. Where I could not verify something, it is in "Gaps". Launch date for the reviews was 7 Nov 2024 (embargo) for the M4 and about 26 Nov 2024 for some M4 Pro reviews. Launch prices were $599 for the M4 and $1,399 for the M4 Pro.

---

## 1. What did reviewers praise (performance, efficiency, size, price, silence, RAM, macOS, ports), with numbers?

### Takeaway
Reviewers praised the M4 mini for value, the much smaller 5x5-inch case, silence under normal loads, strong performance and efficiency (about 3-4 W idle), and 16GB of base RAM. The M4 Pro was praised for Mac Studio-class power in a tiny box and for Thunderbolt 5. The praise is for the launch price; the later price rises (see Q5) changed the value argument.

### Cited Findings
**Size and design**
- TechRadar: the case is less than half the size of the previous version, and it adds front USB-C ports and a headphone jack — [TechRadar summary via search](https://www.techradar.com/computing/macbooks/apple-mac-mini-m4-2024).
- A review quoted in a search result said the mini shed "2.7 inches on each side" and gained about 0.6 inches in height, making it "much more backpack-friendly" — [How-To Geek (Google Translate copy)](https://translate.google.com/translate?u=https%3A%2F%2Fwww.howtogeek.com%2Fapple-mac-mini-m4-review%2F&hl=ar&sl=en&tl=ar&client=srp). I could not see the quote in the original page.
- MacRumors calls it more than two inches smaller than the prior generation and measures it at 5 x 5 inches — [MacRumors, 3 Jan 2025](https://www.macrumors.com/2025/01/03/m4-mac-mini-review/).
- MacRumors' headline: "Apple's M4 Mac Mini is the Best Desktop Mac". Its intro says the base $599 model (M4, 16GB RAM) is the best deal for a desktop Mac, and that performance is more than enough for day-to-day tasks and even gaming, photo editing and video editing — [MacRumors review, 3 Jan 2025](https://www.macrumors.com/2025/01/03/m4-mac-mini-review/).

**Performance numbers**
- The Verge's Geekbench 6 multi-core result for the M4 mini was 14,756, about 50% above the M2 model's 9,801 (as reported by Cult of Mac, not seen on The Verge's page) — [Cult of Mac](https://www.cultofmac.com/?p=874301).
- Engadget tested the M4 Pro with 48GB RAM and recorded 22,850 on Geekbench 6 multi-core (same Cult of Mac source) — [Cult of Mac](https://www.cultofmac.com/?p=874301); [Engadget M4 Pro review](https://www.engadget.com/computing/apple-mac-mini-review-m4-pro-2024-shockingly-small-incredibly-powerful-140042432.html).
- A third review listed M4 Geekbench at 3,899 single-core and 15,012 multi-core versus the M2's 2,642 and 9,799 — [How-To Geek (Google Translate copy)](https://translate.google.com/translate?u=https%3A%2F%2Fwww.howtogeek.com%2Fapple-mac-mini-m4-review%2F&hl=ar&sl=en&tl=ar&client=srp).
- Apple claims up to 1.8x faster CPU and 2.2x faster GPU than the M1 mini, plus hardware ray tracing on the mini for the first time — [MacDailyNews quoting Ars Technica](https://macdailynews.com/2024/11/07/ars-technica-m4-mac-mini-is-easily-the-fastest-most-capable-mac-that-apple-has-sold-for-599/); [Apple press text as quoted in How-To Geek copy](https://translate.google.com/translate?u=https%3A%2F%2Fwww.howtogeek.com%2Fapple-mac-mini-m4-review%2F&hl=ar&sl=en&tl=ar&client=srp).
- Ars Technica headline: "M4 Mac mini is easily the fastest, most capable Mac that Apple has sold for $599". Search summaries of the Ars review say the $599 model handles basic office work, casual photo/video editing and multi-monitor setups, and that the M4 Pro offers CPU performance, display support and RAM capacity that once needed an M1 Ultra Mac Studio. Another summary said the review found the gain minimal for most tasks, mainly useful for intensive prolonged work — [MacDailyNews repost](https://macdailynews.com/2024/11/07/ars-technica-m4-mac-mini-is-easily-the-fastest-most-capable-mac-that-apple-has-sold-for-599/); [Ars review summary at Apple Community](https://discussions.apple.com/thread/255835540). Original Ars URL not retrieved.
- Notebookcheck's M4 Pro chip analysis says it is extremely fast but "not as efficient" as its predecessors because Apple raised maximum power — [Notebookcheck M4 Pro analysis](https://www.notebookcheck.net/Apple-M4-Pro-analysis-Extremely-fast-but-not-as-efficient.915270.0.html).
- Notebookcheck noted solid gaming and emulation results for the entry-level mini — [Notebookcheck news](https://www.notebookcheck.net/Entry-level-2024-Apple-Mac-mini-impresses-with-solid-gaming-and-emulation-performance.916665.0.html). TechRadar, in contrast, listed "struggles with modern games" as a con.

**Power efficiency (the strongest quantified praise)**
- Jeff Geerling: the M4 mini idles at 3-4 W (about the same as a Raspberry Pi); he called it the most efficient CPU he had tested. In HPL it reached 6.74 Gflops/W, about 32% ahead of his M1 Max Mac Studio — [Jeff Geerling blog, Nov 2024](https://www.jeffgeerling.com/blog/2024/m4-mac-minis-efficiency-incredible/).
- Geerling's later test log: 299.93 Gflops at 7.57 Gflops/W, Geekbench 6 multi-core 14,678, and 13.60 tokens/s on llama2:13b for a 10-core, 32GB, 10GbE unit — [GitHub sbc-reviews #57](https://github.com/geerlingguy/sbc-reviews/issues/57).
- A power database records 4.1 W idle at the wall, 36 W in Geekbench multi-core and 39.6 W in HPL for the M4 (third-party, low authority) — [TPCDB](https://www.tpcdb.com/product.php?id=7755).
- Notebookcheck on the M4 Pro: uses minimal energy at idle and does not become power-hungry under higher load — [Notebookcheck M4 Pro review](https://www.notebookcheck.net/Apple-Mac-Mini-M4-Pro-review-The-compact-and-frugal-desktop-PC-with-top-performance-and-expensive-upgrades.946883.0.html).

**Noise and thermals**
- Tom's Hardware (M4 Pro hands-on): fan effectively silent in automatic power mode, audible in High Power mode. Average fan speed about 3,035 RPM (default) versus about 4,549 RPM (High Power). Temperatures were 65.5 C default versus 62 C in High Power — [Tom's Hardware, "Tiny titan"](https://www.tomshardware.com/desktops/mini-pcs/mac-mini-m4-pro-hands-on).
- Notebookcheck on the M4 Pro: virtually silent even under average load because the fan is seldom active. Its M4 review title, though, is "Smaller, faster and louder" — [M4 Pro](https://www.notebookcheck.net/Apple-Mac-Mini-M4-Pro-review-The-compact-and-frugal-desktop-PC-with-top-performance-and-expensive-upgrades.946883.0.html); [M4](https://www.notebookcheck.net/Apple-Mac-Mini-M4-review-Smaller-faster-and-louder.918832.0.html).
- TechRadar found the machine nearly silent while handling video editing easily — [TechRadar summary via search](https://www.techradar.com/computing/macbooks/apple-mac-mini-m4-2024). Engadget praised how quiet the M4 Pro stayed under heavy workloads (via [Cult of Mac](https://www.cultofmac.com/?p=874301)).
- Forum users (not reviewers) with the 14-core M4 Pro reported a maximum of about 82 C in a 10-minute Cinebench R23 run, and some heard the fan at about 3,150 RPM; others could not. Low authority — [MacRumors forum thermals thread](https://forums.macrumors.com/threads/mac-mini-m4-thermals.2442671/); [fan noise thread](https://forums.macrumors.com/threads/first-review-about-sound-fan-noise.2442219/page-20).
- A blog review reported idle noise below 20 dB, rising to 35-40 dB at full load, and a CPU peak around 95 C (single blog, unverified methodology) — [thinkdifferent.blog](https://www.thinkdifferent.blog/blog/review-mac-mini-m4-pro-as-the-best-home-server-for-creatives-and-devs/).

**Ports, RAM, value**
- The base M4 has three Thunderbolt 4 ports; the M4 Pro has Thunderbolt 5 for the first time; both have Gigabit Ethernet and HDMI — [MacDailyNews quoting Ars](https://macdailynews.com/2024/11/07/ars-technica-m4-mac-mini-is-easily-the-fastest-most-capable-mac-that-apple-has-sold-for-599/). The Tom's Guide verdict praises the "beautifully designed" mini PC with ports at front and back; The Verge reportedly praised the cooling system and front ports (second-hand excerpt) — [The Verge/Tom's Guide via search](https://www.tomsguide.com/computing/desktop-computers/mac-mini-m4-review).
- 9to5Mac (Nov 2025): 16GB RAM as standard was previously a $200 upgrade; the SSD is removable but you must open the machine to swap it — [9to5Mac, 22 Nov 2025](https://9to5mac.com/2025/11/22/apple-m4-mac-mini-great-value-black-friday-deal/).
- The Verge's Chris Welch said the mini would be his recommendation for anyone who wants a dependable desktop Mac (see Q3 for caveat) — summary via [search result](https://www.macrumors.com/review/mac-mini-with-m4-and-m4-pro/); original Verge URL not retrieved.

### Inferences
- The most defensible performance-per-watt statement is Geerling's: 3-4 W idle and about 36-40 W at full CPU load (the latter from a third-party database). The M4 Pro draws more under load (Notebookcheck).
- Fan noise findings are split by mode and by reviewer. The safest summary is "silent at idle and normal loads, audible under sustained all-core loads, especially in High Power mode."

### Gaps
- No Thunderbolt 5 specific benchmark or bandwidth testing from reviewers appeared in results.
- Original Ars Technica, The Verge, Engadget and Tom's Guide pages were not readable here, so exact quotes and benchmarks (e.g. Cinebench, GPU, Blender, SSD speed in MB/s) are missing.
- Exact Notebookcheck noise (dB) and wattage figures were not retrievable.

---

## 2. What did reviewers criticise?

### Takeaway
The recurring complaints: power button on the underside, front ports slower than rear, no USB-A, expensive Apple RAM/SSD upgrades, memory soldered and storage not practically user-upgradable, 256GB base SSD, no discrete-class GPU for gaming, and a high price for a loaded M4 Pro.

### Cited Findings
- Power button on the bottom: Notebookcheck calls it a clear design mistake — [Notebookcheck M4](https://www.notebookcheck.net/Apple-Mac-Mini-M4-review-Smaller-faster-and-louder.918832.0.html). Tom's Hardware: "I think it was a poor choice" — [Tom's Hardware](https://www.tomshardware.com/desktops/mini-pcs/mac-mini-m4-pro-hands-on). TechRadar lists awkward power-button placement as a con — [TechRadar](https://www.techradar.com/computing/macbooks/apple-mac-mini-m4-2024). Tom's Guide later wrote a piece titled "I hated the Mac mini M4's power button — until I accidentally proved Apple was right" — [Tom's Guide](https://www.tomsguide.com/computing/mini-pcs/i-hated-the-mac-mini-m4s-power-button-until-i-accidentally-proved-apple-was-right).
- Front ports slower than rear: TechRadar cons list includes front USB-C ports slower than the rear ones — [TechRadar](https://www.techradar.com/computing/macbooks/apple-mac-mini-m4-2024). The exact speeds were not shown in results (commonly USB 3, 10 Gbps; not verified here).
- No USB-A: Expert Reviews lists lack of USB-A as a con — [Expert Reviews](https://www.expertreviews.co.uk/technology/pcs/apple-mac-mini-2024-review). 9to5Mac's year-long user cited the lack of USB-A and an SD card reader on the front — [9to5Mac, 11 Nov 2025](https://9to5mac.com/2025/11/11/the-m4-mac-mini-has-completely-changed-how-i-view-all-other-desktops-video/).
- Upgrade pricing: Macworld verdict, "a great computer at a great price - just as long as you don't buy the upgrades" (the search summary attributed this to Macworld's review; could be from its base-M4 review rather than the M4 Pro one) — [Macworld M4 Pro review](https://www.macworld.com/article/2512911/m4-pro-mac-mini-review-remarkably-small-and-incredibly-powerful.html). How-To Geek (9/10): "incredibly overpriced storage upgrades" — [How-To Geek (Google Translate copy)](https://translate.google.com/translate?u=https%3A%2F%2Fwww.howtogeek.com%2Fapple-mac-mini-m4-review%2F&hl=ar&sl=en&tl=ar&client=srp). A roundup attributes to Engadget's Brian Tong that 32GB on the base mini costs +$400 and 1TB SSD another +$400 (attribution uncertain; roundup page not verified) — [iClarified roundup](https://www.iclarified.com/95457/new-m4-mac-mini-review-roundup-video).
- Upgradeability: Notebookcheck says memory is soldered and cannot be upgraded; the SSD can be swapped, but it is a proprietary module that raises the config price. Buyers should choose RAM and storage up front — [Notebookcheck M4 Pro](https://www.notebookcheck.net/Apple-Mac-Mini-M4-Pro-review-The-compact-and-frugal-desktop-PC-with-top-performance-and-expensive-upgrades.946883.0.html). Pickr: you cannot upgrade it yourself — [Pickr](https://www.pickr.com.au/reviews/2024/apple-m4-mac-mini/). 9to5Mac: the SSD is removable but you have to open the machine — [9to5Mac](https://9to5mac.com/2025/11/22/apple-m4-mac-mini-great-value-black-friday-deal/).
- 256GB base SSD: described as insufficient for many users — [MinIPC-Review / MacRumors-related search result](https://minipc-review.com/en/apple-mac-mini-m4); [AppleInsider on 2026 M6 model still having a too-small SSD](https://appleinsider.com/articles/26/10/02/m6-mac-mini-review-excellent-hardware-badly-hampered-by-too-small-ssd).
- Gaming/GPU: TechRadar con "struggles with modern games"; Creative Bloq caveat of no high-power discrete graphics — [Creative Bloq](https://www.creativebloq.com/tech/computers/apple-mac-mini-m4-review-the-humble-mini-pc-remains-apples-greatest-hit).
- M4 Pro price: The Verge's Chris Welch found it hard to justify a fully loaded M4 Pro at $2,199 — [MacRumors review roundup](https://www.macrumors.com/review/mac-mini-with-m4-and-m4-pro/) (second-hand). Tom's Hardware questioned a $2,299 config "when the Mac Studio exists" — [Tom's Hardware](https://www.tomshardware.com/desktops/mini-pcs/mac-mini-m4-pro-hands-on). PCMag's tested M4 Pro (14-core, 48GB, 1TB) was $2,199 — [PCMag review via Yahoo](https://tech.yahoo.com/computing/articles/apple-mac-mini-2024-m4-140000092.html).
- No display, keyboard or mouse in the box, so the real cost is higher — [How-To Geek (Google Translate copy)](https://translate.google.com/translate?u=https%3A%2F%2Fwww.howtogeek.com%2Fapple-mac-mini-m4-review%2F&hl=ar&sl=en&tl=ar&client=srp).
- Notebookcheck's M4 title "louder" suggests it measured more noise than the predecessor; the numbers were not seen.

### Inferences
- The upgrade-price complaint is the single most universal criticism across outlets, ahead of the power button.
- "Non-upgradable storage" is imprecise: reviewers describe a removable proprietary SSD module (third-party modules exist) but RAM is soldered. Later (2026) models reportedly move to soldered NAND (MacRumors sidebar, unverified).

### Gaps
- Front-port speed (e.g. USB 3 at 10 Gbps vs. Thunderbolt at rear) not confirmed from a review page.
- No reviewer-cited SSD speeds (MB/s) for the 256GB model versus larger ones (smaller NAND configs can be slower) were found.

---

## 3. Final verdicts and scores by outlet

### Takeaway
Scores are overwhelmingly high (about 4.5-5/5 or 9/10). TechRadar 5/5; Pickr 4.7/5; AppleInsider 4.5/5; Macworld 4/5 (M4 Pro); How-To Geek 9/10; PCMag Editors' Choice for the M4 Pro. Several scores for Wired, CNET and Engadget are known only from aggregator pages.

### Cited Findings
**Verified or near-verified scores**
| Outlet | Model | Date | Score / award | URL |
|---|---|---|---|---|
| TechRadar | M4 | Nov 2024 | 5/5, Editor's Choice; "best small form factor PC" | https://www.techradar.com/computing/macbooks/apple-mac-mini-m4-2024 |
| PCMag | M4 Pro | Nov 2024 (Yahoo copy dated 2025) | Editors' Choice (no numeric score seen) | https://tech.yahoo.com/computing/articles/apple-mac-mini-2024-m4-140000092.html |
| Macworld | M4 Pro | Nov 2024 | 4/5 (structured data) | https://www.macworld.com/article/2512911/m4-pro-mac-mini-review-remarkably-small-and-incredibly-powerful.html |
| AppleInsider | M4 (3-month follow-up) | 22 Jan 2025 | 4.5/5, "the best desktop Mac for most people" (as summarised); "near perfect" | https://appleinsider.com/articles/25/01/22/m4-mac-mini-review-three-months-later-the-perfect-headless-mac |
| AppleInsider | M4 Pro | 26 Nov 2024 | Score not seen; title "Mac Studio power, miniaturized" | https://appleinsider.com/articles/24/11/26/mac-mini-m4-pro-review-mac-studio-power-miniaturized |
| Pickr (AU) | M4 | 2024 | 4.7/5, "Highly recommended" | https://www.pickr.com.au/reviews/2024/apple-m4-mac-mini/ |
| How-To Geek | M4 | Nov 2024 | 9/10 | https://tech.yahoo.com/computing/articles/apple-m4-mac-mini-review-110014412.html |
| Croma Unboxed | M4 | 2024/25 | 4.5/5 | https://www.croma.com/unboxed/apple-mac-mini-m4-review |
| Vivid Repairs (UK, low authority) | M4 | 2026 | 9/10 | https://www.vividrepairs.co.uk/apple-mac-mini-m4-desktop-uk-review |

**Scores only from aggregator pages (treat with caution)**
- Engadget M4 Pro, "Shockingly small, incredibly powerful": page text showed "90"; likely 90/100 but unlabelled — [Engadget](https://www.engadget.com/computing/apple-mac-mini-review-m4-pro-2024-shockingly-small-incredibly-powerful-140042432.html).
- TechSpot's aggregator lists Wired 90/100 (7 Nov 2024), CNET 90 (video review "Apple's M4 Mac Mini Is a Big Surprise") and PCMag 80, with the page layout ambiguous so CNET/PCMag may be swapped — [TechSpot](https://www.techspot.com/products/desktop-pcs/apple-mac-mini-m4-m4-pro.300596/). Do not publish those without checking.

**Outlets without a score found**
- Notebookcheck M4: verdict "The Mac Mini M4 is a good everyday computer"; no number seen — [Notebookcheck](https://www.notebookcheck.net/Apple-Mac-Mini-M4-review-Smaller-faster-and-louder.918832.0.html). It also ran an editorial titled "The M4 Mac Mini is the best desktop for most people" — [Notebookcheck](https://www.notebookcheck.net/The-M4-Mac-Mini-is-the-best-desktop-for-most-people.919251.0.html). M4 Pro review: "compact and frugal desktop PC with top performance and expensive upgrades" (64GB/2TB tested, about $2,600) — [Notebookcheck M4 Pro](https://www.notebookcheck.net/Apple-Mac-Mini-M4-Pro-review-The-compact-and-frugal-desktop-PC-with-top-performance-and-expensive-upgrades.946883.0.html).
- The Verge (Chris Welch): recommends it for anyone wanting a dependable desktop Mac; M4 Pro at $2,199 hard to justify — no score seen (Verge does not usually show a number on this format; unverified).
- Ars Technica: positive; "probably" Apple's best Mac minis ever — [Apple Community summary](https://discussions.apple.com/thread/255835540).
- MacRumors: "Best Desktop Mac" — [MacRumors, 3 Jan 2025](https://www.macrumors.com/2025/01/03/m4-mac-mini-review/); [reviews roundup](https://www.macrumors.com/review/mac-mini-with-m4-and-m4-pro/).
- Tom's Guide: very positive ("I tried the new Mac mini M4 and this tiny mini PC is an absolute powerhouse — even if you don't get the pro model"); score not seen — [Tom's Guide](https://tomsguide.com/computing/desktop-computers/mac-mini-m4-review). Later said "my go-to Mac" — [Tom's Guide](https://www.tomsguide.com/computing/desktop-computers/the-mac-mini-m4-is-my-go-to-mac-and-its-selling-at-its-lowest-price-to-date).
- Creative Bloq: "as close to the perfect computer for most people as any computer can get" (paraphrased by search tool; no number) — [Creative Bloq](https://www.creativebloq.com/tech/computers/apple-mac-mini-m4-review-the-humble-mini-pc-remains-apples-greatest-hit). MusicRadar: headline "I could see it lasting a decade or more" — [MusicRadar](https://www.musicradar.com/music-tech/laptops-computers/apple-mac-mini-m4-review). Digital Trends M4 Pro: "a silver box of magic" with an Editors' Choice badge — [Digital Trends](https://www.digitaltrends.com/computing/apple-mac-mini-m4-pro-review/). Gear Patrol: "Almost Perfect. It's Only Missing One Thing" — [Gear Patrol](https://www.gearpatrol.com/tech/apple-m4-mac-mini-review/).
- 9to5Mac, one-year (video, 11 Nov 2025): ran the base M4 as main desktop for a year; "shattered expectations"; complaint: no USB-A or front SD reader — [9to5Mac](https://9to5mac.com/2025/11/11/the-m4-mac-mini-has-completely-changed-how-i-view-all-other-desktops-video/). 22 Nov 2025: "unbeatable value, even a year after its debut" — [9to5Mac](https://9to5mac.com/2025/11/22/apple-m4-mac-mini-great-value-black-friday-deal/).
- AppleInsider three-month: "the perfect headless Mac".
- Mark Ellis (blog) 3-month M4 Pro review: fan silent in video, Logic, Lightroom exports — [Mark Ellis Reviews](https://markellisreviews.com/reviews/m4-pro-mac-mini-my-first-impressions/).

**YouTubers**
- Jeff Geerling: efficiency-focused (see Q1) — [blog](https://www.jeffgeerling.com/blog/2024/m4-mac-minis-efficiency-incredible/).
- Linus Tech Tips: video "Finally a Mac for This Economy - Mac Mini M4" (Dec 2024). Forum commenters criticised its benchmark choices; I did not see the verdict — [LTT forum](https://linustechtips.com/topic/1591845-finally-a-mac-for-this-economy-mac-mini-m4/); [X post](https://x.com/LinusTech/status/1866192941288759686).
- MKBHD: video description opens "The new $599 M4 Mac Mini is really good" (per search summary, which could not tell me which of these two videos is MKBHD's versus Dave2D's: [video 1](https://www.youtube.com/watch?v=z19HM7ANZlo), [video 2](https://www.youtube.com/watch?v=qExcc92zHfo) - titles "The M4 Mac mini is Incredible!" and "M4 Mac Mini Review - Apple NAILED It.").
- Dave2D: only a video page found, description "My review of the M4 Mac Mini from Apple." No verdict content.
- A roundup attributes to MKBHD that the redesign makes the most of Apple silicon's small footprint and the mini "should remain a zippy, reliable computer for years to come". The same roundup's attribution of other quotes was inconsistent, so treat as unverified — [iClarified](https://www.iclarified.com/95457/new-m4-mac-mini-review-roundup-video).

### Inferences
- Consensus: 9/10-ish. The only sub-5-star pattern is on the M4 Pro (Macworld 4/5) where price drives the lower score.

### Gaps
- Arabic-language reviewers: my Arabic query returned no Arabic reviews (only English results and Google-Translated English pages). No Arabic outlet scores found.
- Numeric scores for The Verge, Engadget (confirmed label), Tom's Guide, Wired, CNET not confirmed from primary pages. Original Ars Technica URL not obtained.
- Dave2D and LTT verdicts not retrievable (video content).

---

## 4. Who is it recommended for / not recommended for?

### Takeaway
Recommended for office, general productivity, programming/dev, light-to-moderate photo/video editing, home server and headless uses; the M4 Pro for heavy creative work and local AI. Not recommended for demanding gaming, anyone needing lots of storage on the base model, or anyone who wants upgradeability.

### Cited Findings
- Office/general: Ars says the $599 model handles basic office work, casual photo/video editing and multi-monitor — [MacDailyNews (Ars)](https://macdailynews.com/2024/11/07/ars-technica-m4-mac-mini-is-easily-the-fastest-most-capable-mac-that-apple-has-sold-for-599/). A one-year retrospective says the base model suits browsing, office, light photo and occasional video editing — [MacMyths](https://macmyths.com/the-499-m4-mac-mini-1-year-later-has-it-shattered-expectations/) (low authority).
- Creative/video: TechRadar found video editing handled with ease. PetaPixel title: "M4 Pro Mac mini Review: Pro Performance in a Tiny, Affordable Package" — [PetaPixel, 7 Nov 2024](https://petapixel.com/2024/11/07/m4-pro-mac-mini-review-pro-performance-in-a-tiny-affordable-package). MusicRadar: could see it lasting "a decade or more" (music production) — [MusicRadar](https://www.musicradar.com/music-tech/laptops-computers/apple-mac-mini-m4-review).
- Replacing older Macs: Ars saw the M4 Pro as a strong replacement for aging Intel iMacs (summary above).
- Headless/home server: AppleInsider, "the perfect headless Mac" — [AppleInsider, 22 Jan 2025](https://appleinsider.com/articles/25/01/22/m4-mac-mini-review-three-months-later-the-perfect-headless-mac). Geerling's 3-4 W idle supports always-on use. Blog: M4 Pro "best home server for creatives and devs" — [thinkdifferent.blog](https://www.thinkdifferent.blog/blog/review-mac-mini-m4-pro-as-the-best-home-server-for-creatives-and-devs/).
- Local LLM / AI (all blogs, rough, methodology often missing): M4 Pro 24GB about 30 tokens/s on Llama 3.1 8B Q4, about 20 on 13B, about 12 on 32B — [compute-market.com](https://www.compute-market.com/blog/mac-mini-m4-for-ai-apple-silicon-2026). 70B Q4 on 64GB M4 Pro about 8-12 tokens/s — [daviesmeyer.com](https://ai-solutions.daviesmeyer.com/en/blog/mac-mini-m4-pro-lokale-ki-inferenz); another says about 18 tokens/s — [kunalganglani.com](https://www.kunalganglani.com/blog/mac-mini-m4-vs-mac-mini-m4-pro) (conflicting). Memory bandwidth about 273 GB/s on M4 Pro versus about 120 GB/s on M4 (Apple's published figure for the M4 is 120 GB/s). MLX/LM Studio about 20-30% faster than Ollama — [Medium](https://medium.com/@tentenco/mac-mini-m4-vs-amd-mini-pcs-for-local-ai-a-hardware-buyers-guide-by-budget-tier-46955a45b4c5). DeepSeek R1 about 11 tokens/s Ollama vs 14 LM Studio on 64GB M4 Pro — [like2byte](https://like2byte.com/mac-mini-m4-deepseek-r1-ai-benchmarks/). Geerling: 13.60 tokens/s llama2:13b on base-class M4 32GB.
- Gaming: not recommended as a gaming machine (TechRadar, Creative Bloq), although Notebookcheck found "solid" gaming and emulation for the entry-level model.
- Not recommended for: anyone needing lots of storage without paying for upgrades, those wanting USB-A ports without a dock, or those wanting user upgrades (Notebookcheck, Expert Reviews, Pickr above). Users who already own a monitor/peripherals are the ideal buyers (MacMyths).

### Inferences
- For local LLMs, memory capacity and bandwidth matter more than CPU cores; the 48-64GB M4 Pro was the sweet spot, and Apple later cut those RAM options (Q5).

### Gaps
- No reputable outlet (as opposed to blogs) with controlled LLM benchmarks was found.
- Programming/dev workloads (Xcode compile times) have no specific reviewer numbers in my results.

---

## 5. Known issues since launch (to Oct 2026) and comparison with the successor

### Takeaway
Known issues: USB-C peripheral dropouts (Jan 2025), Wi-Fi/Bluetooth weakness when external drives or cables sit near the antenna in the base, and, most importantly for buyers in 2026, an AI-driven memory shortage that removed the $599 config, cut 32GB/64GB options and raised prices. The successor line is an M6 base mini and an M5 Pro mini, both reviewed as faster but significantly more expensive.

### Cited Findings
**Hardware/software issues**
- USB-C connectivity: users reported keyboards disconnecting, docks/hubs/KVMs failing after sleep, and an external drive disconnecting under heavy I/O; mostly on rear ports. Cause not confirmed; no Apple acknowledgement found — [AppleInsider, 15 Jan 2025](https://appleinsider.com/articles/25/01/15/m4-mac-mini-may-have-a-usb-c-connectivity-problem); [Notebookcheck](https://www.notebookcheck.net/Apple-M4-Mac-mini-users-are-reporting-problems-with-USB-C-connectivity.948588.0.html); [TechRadar](https://www.techradar.com/computing/macs/apples-m4-mac-mini-might-be-one-of-the-best-macs-ever-but-it-has-a-serious-issue-that-needs-fixing-right-now).
- Wi-Fi: speeds drop when a drive/dock is placed against the mini; the antenna is likely in the plastic base — [Michael Tsai, 10 Mar 2025](https://mjtsai.com/blog/2025/03/10/weak-m4-mac-mini-wi-fi/); [Apple Community](https://discussions.apple.com/thread/255860420). Bluetooth dropouts reported on MacRumors forums — [MacRumors forum](https://forums.macrumors.com/threads/m4-mac-mini-issues.2447593/).

**Supply, pricing and configurations (2026)**
- 9to5Mac, 22 Apr 2026: the $599 base model (256GB) was completely out of stock at Apple, tied to memory/storage shortages — [9to5Mac](https://9to5mac.com/2026/04/22/more-mac-mini-out-of-stock/).
- MacRumors, 5 May 2026: Apple removed the 32GB and 64GB mini options; M4 Pro capped at 48GB and base M4 at 16/24GB — [MacRumors](https://www.macrumors.com/2026/05/05/apple-mac-studio-mac-mini-ram-cuts/). Per a search summary, the $599 configuration was dropped and the entry point became $799; later the 16GB/256GB option was reinstated at $799 (per search summary of other sources; Apple's own page not checked).
- MacRumors, 25 Jun 2026: M4 Pro mini starting price raised $200 to $1,599. Apple quote to WSJ: "We have now reached a point where we need to begin raising prices" — [MacRumors](https://www.macrumors.com/2026/06/25/apple-hikes-m4-pro-mac-mini-starting-price/).
- Cult of Mac: M4 Pro 64GB wait times of 16-18 weeks — [Cult of Mac](https://www.cultofmac.com/news/mac-mini-shortage-price-hikes-2026). MacRumors buyer's guide says the M4 is discontinued — [MacRumors guide](https://www.macrumors.com/guide/2024-vs-2026-mac-mini/).

**Successor comparison (M6 base mini, M5 Pro mini)**
- Prices: M6 mini starts at $899 (16GB/256GB); M5 Pro at $1,699, $100 above the M4 Pro's final $1,599 — [iClarified](https://www.iclarified.com/101892/m6-mac-mini-vs-m4-mac-mini-whats-new-and-should-you-upgrade).
- Engadget (Devindra Hardawar), M6 review: 8.7/10, "The best compact desktop is no longer a great deal"; cons: higher price, bottom power button, expensive memory/storage upgrades — [Engadget](https://www.engadget.com/2263471/apple-mac-mini-m6-review/).
- AppleInsider M6 review: "Excellent hardware badly hampered by too-small SSD"; Geekbench multi-core 22,594 (M6) vs 15,337 (M4), about +47% — [AppleInsider, 2 Oct 2026](https://appleinsider.com/articles/26/10/02/m6-mac-mini-review-excellent-hardware-badly-hampered-by-too-small-ssd). Max RAM rose from 24GB (M4) to 32GB — [Gizmodo](https://gizmodo.com/m6-mac-mini-review-a-better-tiny-desktop-with-or-without-ai-2000813947).
- Notebookcheck M6 review: system performance chart 49.3 vs 47.2 for the M4 Pro — [Notebookcheck](https://www.notebookcheck.net/Compact-powerhouse-with-the-2-nm-M6-SoC-Apple-Mac-mini-2026-Review.1401148.0.html). Six Colors: "Tiny, pricey, and powerful" — [Six Colors](https://sixcolors.com/post/2026/09/m6-mac-mini-review-tiny-pricey-and-powerful/).
- M5 Pro: AppleInsider 4/5, "a great computer, but it's hard to recommend when you start adding upgrades" — [AppleInsider, 5 Oct 2026](https://appleinsider.com/articles/26/10/05/mac-mini-m5-pro-review-mini-gets-serious-with-one-caveat). Macworld ("Killer performance at a lethal price"): base 50% more expensive; tested config $2,899 versus $2,299 for the equivalent M4 Pro two years earlier — [Macworld](https://www.macworld.com/article/3239233/mac-mini-m5-pro-review-killer-performance-at-a-lethal-price.html). Apple claims Blender rendering 1.4x faster on the M5 Pro versus the M4 Pro — [AppleInsider comparison](https://appleinsider.com/articles/26/09/22/m5-pro-mac-mini-vs-m4-pro-mac-mini-compared-specs-hardware-price). A blog test found M5 Pro single-core only about 2% behind the M4 Pro (wording as summarised; likely an error or a specific test) — [adamtalks.tech](https://adamtalks.tech/reviews/m5-pro-vs-m4-pro-mac-mini-tested/). Tom's Hardware review of the late-2026 mini: "Strong performance, but losing its grip on value" — [Tom's Hardware](https://www.tomshardware.com/desktops/mini-pcs/apple-mac-mini-late-2026-review). Ars Technica reportedly called the M4 model "one of Apple's best values ever" and the newer one "not so much" — [AppleInsider forum roundup](https://forums.appleinsider.com/discussion/245746/mac-mini-review-roundup-m6-and-m5-pro-make-this-a-marvel-but-a-costly-one).
- MacRumors sidebar (unverified): the newer M6/M5 Pro minis solder the NAND, so no aftermarket storage upgrades.

### Inferences
- Reviewers now frame the M4 mini as the "last great-value mini": its launch pricing ($599/$1,399) is gone from Apple's store, while used or leftover retail stock (e.g. Amazon deals around $479-$499) may be the only way to match launch value. Retailer pricing should be checked.
- The M6 gain is large for CPU (about +47% multi-core) but reviewers weigh it against about $300 higher launch-to-launch prices.

### Gaps
- No confirmed Apple fix or acknowledgement for the USB-C/Wi-Fi issues.
- Exact current Apple store prices of the M4 minis were taken from news reports, not from Apple.
- Exact sale/discount history for M4 mini after discontinuation was not checked.
- "M5" base mini: I found only one low-authority blog on an "M5 Mac mini"; results indicate Apple went M4 to M6 for the base chip and M5 Pro for the high end — worth confirming with Apple's newsroom.
