import sys
F = "/home/user/trading-view-/reels/ads-vs-organic/assets/fonts/"
NAVY, ORANGE, WHITE = "#13213F", "#FF6A13", "#FFFFFF"

def frame(c, kind):
    g, ink, mute, surf, acc_fill, acc_text = c["ground"], c["ink"], c["mute"], c["surf"], c["fill"], c["acc_text"]
    st = f"background:{g};color:{ink};"
    if kind == "hook":
        body = f'''
        <div class="t" style="top:300px;font-size:60px;color:{mute}">كلهم بيقولولك:</div>
        <div class="t" style="top:400px;font-size:104px;line-height:1.3">مش هتعرف تسوّق<br>لعيادتك صح</div>
        <div class="t" style="top:720px;font-size:104px">غير لما تعمل إعلان ممول</div>
        <div class="t" style="top:930px;font-size:64px">يا ترى الكلام ده</div>
        <div class="t" style="top:1020px"><span class="stamp" style="font-size:230px;{acc_text}">صح؟</span></div>'''
    elif kind == "split":
        def phone(x, scr, bubs, hot):
            b = "".join(f'<div class="bub" style="background:{surfb};color:{inkb}">{t}</div>' for t in bubs) if bubs else ""
            h = f'<div class="bub" style="background:{ORANGE};color:{NAVY};font-size:60px">عايز أحجز</div>' if hot else ""
            return f'''<div class="ph" style="left:{x}px"><div class="scr" style="background:{scr}"><div class="pt" style="color:{NAVY}">رسايل</div>{b}{h}</div></div>'''
        surfb, inkb = "#E9ECF2", "#5A6378"
        body = f'''
        <div class="t" style="top:300px;font-size:72px;line-height:1.35">طب إيه فايدة المحتوى<br>الأورجانيك هنا بقى؟</div>
        <div class="lab" style="left:100px;color:{mute}">إعلان</div><div class="lab" style="left:560px">محتوى</div>
        {phone(80, "#FFFFFF", ["بكام الكشف؟","فيه خصم؟","آخر سعر كام؟"], False)}
        {phone(560, "#FFFFFF", [], True)}'''
    elif kind == "stairs":
        s_ad = c.get("step_ad", acc_fill)
        s_ad_ink = c.get("step_ad_ink", NAVY)
        body = f'''
        <div class="t" style="top:300px;font-size:120px">خطوة أخيرة</div>
        <div class="t" style="top:470px;font-size:64px">في الـ <span style="font-family:IndieF;font-style:normal;font-size:84px;color:{c.get('en', ink)}">scaling</span></div>
        <div class="step" style="left:660px;top:1030px;height:240px;background:{c['step']};color:{c['step_ink']}">محتوى</div>
        <div class="step" style="left:390px;top:830px;height:440px;background:{c['step']};color:{c['step_ink']}">ثقة</div>
        <div class="step" style="left:120px;top:630px;height:640px;background:{s_ad};color:{s_ad_ink}">إعلان</div>'''
    else:
        body = f'''
        <div class="t" style="top:470px;font-size:62px">واستمراريتك في المحتوى ده</div>
        <div class="t" style="top:580px;font-size:150px;line-height:1.25">أهم<br><span class="stamp" style="{acc_text}">مليون مرة</span></div>
        <div class="t" style="top:1010px;font-size:64px">من أي إعلان ممول</div>'''
    return f'<div class="fr"><div class="cv" style="{st}">{body}</div></div>'

def row(name, desc, frames):
    return f'<div class="row"><div class="rh"><b>{name}</b><span>{desc}</span></div><div class="frs">{"".join(frames)}</div></div>'

A = dict(ground=WHITE, ink=NAVY, mute="#8A93A6", surf="#EEF1F6", fill=ORANGE,
         acc_text=f"background:{ORANGE};color:{NAVY};padding:0 34px;border-radius:24px;", step=NAVY, step_ink=WHITE, en=ORANGE)
B = dict(ground=NAVY, ink=WHITE, mute="#7F8AA3", surf="#1E2E55", fill=ORANGE,
         acc_text=f"color:{ORANGE};", step="#FFFFFF", step_ink=NAVY, en=ORANGE)
C1 = dict(B); C1.update(ground=NAVY)
C2 = dict(A); C2.update(ground=WHITE)
C3 = dict(ground=ORANGE, ink=NAVY, mute="#7A2E05", surf="#FFE1CF", fill=WHITE, acc_text="", step=NAVY, step_ink=WHITE, step_ad=WHITE, step_ad_ink=NAVY, en=WHITE)
C4 = dict(B); C4.update(ground=NAVY)

html = f'''<!doctype html><html lang="ar"><head><meta charset="utf-8"><style>
@font-face{{font-family:Rubik;font-style:italic;font-weight:300 900;src:url("{F}rubik-italic-arabic.woff2") format("woff2");unicode-range:U+0600-06FF,U+0750-077F,U+0870-08FF,U+200C-200E,U+FB50-FDFF,U+FE70-FEFC;}}
@font-face{{font-family:Rubik;font-style:italic;font-weight:300 900;src:url("{F}rubik-italic-latin.woff2") format("woff2");unicode-range:U+0000-00FF,U+2000-206F;}}
@font-face{{font-family:IndieF;src:url("{F}indieflower-latin.woff2") format("woff2");}}
body{{margin:0;background:#D9DDE5;font-family:Rubik;font-style:italic;font-weight:500;width:1232px;padding:30px 0}}
.row{{margin:0 40px 34px}}.rh{{direction:rtl;display:flex;gap:18px;align-items:baseline;margin-bottom:12px;color:#13213F}}
.rh b{{font-size:34px;font-weight:500}}.rh span{{font-size:22px;opacity:.75}}
.frs{{display:flex;gap:24px;direction:rtl}}.fr{{position:relative;direction:ltr;width:270px;height:480px;overflow:hidden;border-radius:14px;box-shadow:0 6px 18px rgba(19,33,63,.18)}}
.cv{{position:absolute;left:0;top:0;width:1080px;height:1920px;transform:scale(.25);transform-origin:0 0}}
.t{{position:absolute;left:60px;width:960px;text-align:center;direction:rtl;white-space:nowrap}}
.stamp{{display:inline-block;line-height:1.15}}
.lab{{position:absolute;top:610px;width:440px;text-align:center;font-size:58px;direction:rtl}}
.ph{{position:absolute;top:720px;width:440px;height:880px;border-radius:70px;background:#0B1328;padding:16px}}
.scr{{width:100%;height:100%;border-radius:56px;padding:90px 22px 0;box-sizing:border-box;direction:rtl}}
.pt{{position:absolute;top:56px;right:56px;font-size:44px}}
.bub{{display:table;margin:0 0 22px 0;font-size:44px;padding:12px 26px;border-radius:30px;border-top-right-radius:8px}}
.step{{position:absolute;width:260px;border-radius:22px;text-align:center;font-size:60px;padding-top:26px;box-sizing:border-box;direction:rtl}}
</style></head><body>
{row("أ · أبيض نضيف", "أرضية بيضا، الكلام كحلي، والبرتقالي خلفية للكلمة المهمة بس", [frame(A,k) for k in ["hook","split","stairs","claim"]])}
{row("ب · كحلي جريء", "أرضية كحلي، الكلام أبيض، والبرتقالي لون الكلمة المهمة", [frame(B,k) for k in ["hook","split","stairs","claim"]])}
{row("ج · بلوكات ألوان", "كل جملة على لوح لون مختلف: كحلي ← أبيض ← برتقالي", [frame(C1,"hook"),frame(C2,"split"),frame(C3,"stairs"),frame(C4,"claim")])}
</body></html>'''
open(sys.argv[1], "w").write(html)
