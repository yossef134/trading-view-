#!/usr/bin/env python3
"""Build the free-audit report: client PDF infographic + client MD + internal MD.

usage: build_audit.py --dir <doctor dir> --content audit_content.json [--no-pdf]

Inputs in <dir>: analysis.json, baseline.json, own_reels.json (optional), scan/peers_analysis.json (optional),
and audit_content.json written by Claude (schema: references/audit-content-schema.md).
Outputs in <dir>: audit_client.html, audit_client.pdf, audit_client.md, audit_internal.md.

Numbers in the client version come from the data files; words come from audit_content.json.
No costs, tool names or statistics jargon in the client version.
"""
import argparse
import html
import json
import os
import subprocess

E = html.escape


def load(path, default=None):
    return json.load(open(path, encoding="utf-8")) if os.path.exists(path) else default


def n(v):
    if v is None:
        return "—"
    v = float(v)
    if v >= 1e6:
        return f"{v / 1e6:.1f}M".replace(".0M", "M")
    if v >= 1e4:
        return f"{v / 1e3:.0f}K"
    if v >= 1e3:
        return f"{v / 1e3:.1f}K".replace(".0K", "K")
    return f"{v:.0f}"


def dots(score):
    """Score out of 10, drawn as 10 small segments plus the number."""
    s = max(0, min(10, int(score or 0)))
    segs = "".join('<span class="dot on"></span>' if i < s else '<span class="dot"></span>' for i in range(10))
    return f'{segs} <b dir="ltr">{s}/10</b>'


CSS = """
@page { size: A4; margin: 0; }
:root { --teal:#0f7c86; --teal2:#14a3a0; --navy:#12324a; --ink:#1f2d3a; --muted:#5d6b78;
        --bg:#f4f9f9; --card:#ffffff; --line:#d9e7e8; --warn:#c77d12; --good:#1f8a5b; --soft:#e6f3f3; }
* { box-sizing:border-box; }
html, body { margin:0; background:var(--bg); color:var(--ink);
  font-family:"IBM Plex Sans Arabic","DejaVu Sans",sans-serif; font-size:13.5px; line-height:1.7; }
.page { width:210mm; min-height:297mm; padding:16mm 15mm 14mm; position:relative; page-break-after:always;
  background:var(--bg); }
.page:last-child { page-break-after:auto; }
.top { display:flex; justify-content:space-between; align-items:center; color:var(--muted); font-size:11px;
  border-bottom:1px solid var(--line); padding-bottom:6px; margin-bottom:14px; }
.brand { color:var(--teal); font-weight:700; direction:ltr; }
.foot { position:absolute; bottom:8mm; left:15mm; right:15mm; font-size:10.5px; color:var(--muted);
  display:flex; justify-content:space-between; }
h1 { font-size:30px; color:var(--navy); margin:0 0 6px; line-height:1.3; }
h2 { font-size:20px; color:var(--navy); margin:0 0 4px; }
h2 .num { display:inline-flex; width:30px; height:30px; border-radius:50%; background:var(--teal); color:#fff;
  align-items:center; justify-content:center; font-size:15px; margin-inline-end:8px; }
.lead { color:var(--muted); margin:0 0 14px; }
.cover { display:flex; flex-direction:column; justify-content:center; min-height:255mm; }
.cover .pill { display:inline-block; background:var(--soft); color:var(--teal); border-radius:999px;
  padding:4px 14px; font-weight:600; margin-bottom:18px; }
.cover .who { font-size:18px; color:var(--ink); margin:4px 0 26px; }
.diag { background:var(--card); border-inline-start:5px solid var(--teal); border-radius:10px; padding:16px 18px;
  font-size:16px; box-shadow:0 1px 3px rgba(18,50,74,.06); }
.quote { margin-top:18px; color:var(--navy); font-size:15px; font-style:italic; }
.quote small { display:block; color:var(--muted); font-style:normal; font-size:11.5px; }
.grid { display:grid; gap:10px; }
.g4 { grid-template-columns:repeat(4,1fr); } .g2 { grid-template-columns:repeat(2,1fr); } .g3 { grid-template-columns:repeat(3,1fr); }
.card { background:var(--card); border:1px solid var(--line); border-radius:12px; padding:12px 14px; }
.kpi .v { font-size:24px; font-weight:700; color:var(--navy); line-height:1.2; }
.kpi .l { color:var(--muted); font-size:11.5px; }
.kpi .s { font-size:11.5px; margin-top:4px; }
.bars { display:flex; align-items:flex-end; gap:6px; height:120px; padding:6px 4px 0; direction:ltr;
  border-bottom:1px solid var(--line); }
.bar { flex:1; background:#b9dcdc; border-radius:4px 4px 0 0; position:relative; min-height:2px; }
.bar.hi { background:var(--teal); }
.bar span { position:absolute; top:-17px; left:50%; transform:translateX(-50%); font-size:10px; color:var(--muted); white-space:nowrap; }
.bar.hi span { color:var(--navy); font-weight:700; }
.cap { font-size:11px; color:var(--muted); margin-top:4px; }
.prob { display:grid; grid-template-columns:34px 1fr; gap:10px; margin-bottom:10px; }
.prob .ic { width:34px; height:34px; border-radius:10px; background:#fdf1e0; color:var(--warn); font-weight:700;
  display:flex; align-items:center; justify-content:center; font-size:16px; }
.prob h3 { margin:0; font-size:15px; color:var(--navy); }
.prob .why { color:var(--muted); font-size:12.5px; margin:2px 0 6px; }
.fix { background:var(--soft); border-radius:8px; padding:8px 10px; font-size:13px; }
.fix b { color:var(--teal); }
.example { margin-top:6px; background:#fff; border:1px dashed var(--teal2); border-radius:8px; padding:8px 10px;
  white-space:pre-wrap; font-size:13px; }
.rate { display:grid; grid-template-columns:110px 130px 1fr; gap:8px; align-items:start; padding:6px 0;
  border-bottom:1px solid var(--line); font-size:12.5px; }
.dot { display:inline-block; width:6px; height:9px; border-radius:2px; background:#d6e2e3; margin-inline-start:3px; }
.dot.on { background:var(--teal); }
.note { background:#fff8ec; border:1px solid #f1dcb5; border-radius:10px; padding:10px 12px; font-size:12.5px; margin-top:10px; }
.pat { margin-bottom:10px; }
.pat h3 { margin:0 0 2px; font-size:15px; color:var(--navy); }
.pat .ev { color:var(--muted); font-size:12px; }
.pat ul { margin:6px 0 0; padding-inline-start:18px; font-size:12.5px; }
.pat .you { margin-top:6px; font-size:12.5px; background:var(--soft); border-radius:8px; padding:6px 10px; }
a { color:var(--teal); text-decoration:none; }
table { width:100%; border-collapse:collapse; font-size:12px; }
th, td { text-align:start; padding:5px 6px; border-bottom:1px solid var(--line); }
th { color:var(--muted); font-weight:600; }
.next li { margin:4px 0; }
.cta { margin-top:14px; background:var(--teal); color:#fff; border-radius:12px; padding:14px 16px; font-size:15px; font-weight:600; }
.measure { margin-top:10px; font-size:12.5px; color:var(--muted); }
.wl { border-radius:10px; padding:9px 11px; margin-bottom:7px; font-size:12px; }
.wl.win { background:#eaf7f1; border-inline-start:4px solid var(--good); }
.wl.lose { background:#fdf0ea; border-inline-start:4px solid var(--warn); }
.wl .idx { font-weight:700; } .wl .hk { color:var(--navy); margin:2px 0; } .wl .mt { color:var(--muted); font-size:11px; }

"""


def platform_card(c):
    pc = c.get("platform_compare")
    if not pc:
        return ""
    rows = "".join(f"<tr><td>{E(r[0])}</td><td>{E(r[1])}</td><td><b>{E(r[2])}</b></td></tr>" for r in pc["rows"])
    return (f'<div class="card" style="margin-top:12px"><h3 style="margin:0 0 6px;color:var(--navy)">{E(pc["title"])}</h3>'
            f'<table><tr><th></th><th>إنستجرام</th><th>فيسبوك</th></tr>{rows}</table>'
            f'<div class="fix" style="margin-top:8px">{E(pc["note"])}</div></div>')


def win_lose_card(items, cls, platform_label):
    if not items:
        return f'<div class="card"><div class="why">لسه مفيش {E(cls)} كفاية على {E(platform_label)} نحكم عليهم.</div></div>'
    out = ""
    for it in items[:5]:
        val = n(it.get("views")) + " مشاهدة" if it.get("views") else n((it.get("likes") or 0) + (it.get("comments") or 0) + (it.get("shares") or 0)) + " تفاعل"
        out += (f'<div class="wl {cls}"><div class="idx" dir="ltr">{it["index"]}×</div>'
                f'<div class="hk"><a href="{E(it.get("url",""))}">{E((it.get("hook") or "")[:70] or "بدون نص")}</a></div>'
                f'<div class="mt">{val}</div></div>')
    return f'<div class="card">{out}</div>'


CONSISTENCY_AR = {"regular": "منتظم", "irregular": "غير منتظم", "rare": "نادر"}
LRI, PDI = "\u2066", "\u2069"  # isolate LTR text (phone numbers, English ratings) inside RTL flow


def facebook_section(fb):
    """Full Facebook page, mirroring the Instagram winners/losers page (parity, agreed 2026-11-05)."""
    if not fb:
        return None
    ps = fb["page_signals"]
    kpis = [("متابعين فيسبوك", n(fb["page"]["followers"]), ""),
            ("بوستات/أسبوع", str(fb["cadence"].get("posts_per_week", "—")),
             CONSISTENCY_AR.get(fb["cadence"].get("consistency"), "")),
            ("مشاهدات الفيديو المعتادة", n(fb["format_medians"].get("video")), ""),
            ("معدل التفاعل", (f'{fb["health"]["median_er"]*100:.1f}%' if fb["health"].get("median_er") else "—"), "")]
    tiles = "".join(f'<div class="card kpi"><div class="l">{E(l)}</div><div class="v">{v}</div><div class="s">{E(s)}</div></div>' for l, v, s in kpis)
    info_rows = "".join(f'<div class="rate" style="grid-template-columns:90px 1fr"><b>{E(l)}</b><span>{LRI if ltr else ""}{E(str(v) or "—")}{PDI if ltr else ""}</span></div>'
                        for l, v, ltr in (('التليفون', ps.get("phone"), True), ('العنوان', ps.get("address"), False),
                                         ('التقييم', ps.get("rating"), True)) if v)
    cols = (f'<div class="grid g2" style="margin-top:12px">'
            f'<div><h3 style="color:var(--navy);font-size:14px;margin:0 0 6px">أقوى بوستات فيسبوك</h3>{win_lose_card(fb["winners"], "win", "فيسبوك")}</div>'
            f'<div><h3 style="color:var(--navy);font-size:14px;margin:0 0 6px">أضعف بوستات فيسبوك</h3>{win_lose_card(fb["losers"], "lose", "فيسبوك")}</div></div>')
    return (f'<h2>حسابك على فيسبوك: الناجح والفاشل</h2>'
            f'<p class="lead">نفس طريقة التحليل بالظبط: كل بوست بيتقارن بمعتاد نوعه هو (فيديو مع فيديو، بوست مع بوست).</p>'
            f'<div class="grid g4">{tiles}</div>{cols}'
            + (f'<div class="card" style="margin-top:12px"><b style="color:var(--navy)">بيانات الصفحة</b>{info_rows}</div>' if info_rows else ""))


def page(inner, brand, date, num, total, header):
    return (f'<section class="page"><div class="top"><span>{E(header)}</span>'
            f'<span class="brand">{E(brand)}</span></div>{inner}'
            f'<div class="foot"><span>{E(date)}</span><span dir="ltr">{num} / {total}</span></div></section>')


def build(d, c):
    an, base = d["analysis"], d["baseline"]
    peers, own, fb = d.get("peers"), d.get("own"), d.get("facebook")
    brand, date = c.get("brand", ""), c.get("date", base["taken_at"][:10])
    doc = c["doctor"]
    pages = []

    # 1 cover
    q = ""
    if c.get("opening_quote"):
        q = f'<div class="quote">«{E(c["opening_quote"])}»<small>{E(doc["name"])}</small></div>'
    pages.append(f'''<div class="cover"><div><span class="pill">تحليل مبدئي</span></div>
<h1>تحليل حسابك على {"إنستجرام وفيسبوك" if fb else "إنستجرام"}</h1>
<div class="who">{E(doc["name"])} · {E(doc["specialty"])} · <span dir="ltr">@{E(doc["handle"])}</span></div>
<div class="diag">{E(c["diagnosis"])}</div>{q}</div>''')

    # 2 numbers
    reels = [p for p in an["posts"] if p["format"] == "reel" and p.get("views")]
    last10 = sorted(reels, key=lambda p: p["timestamp"] or "")[-10:]
    mx = max([p["views"] for p in last10] or [1])
    best_i = max(range(len(last10)), key=lambda i: last10[i]["views"]) if last10 else -1
    bars = "".join(f'<div class="bar{" hi" if i == best_i else ""}" style="height:{max(2, p["views"] / mx * 100):.0f}%">'
                   f'<span>{n(p["views"])}</span></div>' for i, p in enumerate(last10))
    k = c.get("kpi_notes", {})
    kpis = [("المتابعين", n(base["followers"]), k.get("followers", "")),
            ("بوستات آخر 30 يوم", n(base["posts_last_30d"]), k.get("posts", "")),
            ("المشاهدات المعتادة للريل", n(base["median_views_last10_reels"]), k.get("views", "")),
            ("أعلى ريل", n(max([p["views"] for p in reels] or [0])), k.get("best", ""))]
    tiles = "".join(f'<div class="card kpi"><div class="l">{E(l)}</div><div class="v">{v}</div>'
                    f'<div class="s">{E(s)}</div></div>' for l, v, s in kpis)
    bv = c.get("best_video", {})
    best = (f'<div class="card" style="margin-top:12px"><h3 style="margin:0;color:var(--navy)">أنجح فيديو عندك</h3>'
            f'<div><a href="{E(bv.get("url", ""))}">{E(bv.get("title", ""))}</a></div>'
            f'<div class="why" style="color:var(--muted);font-size:12.5px">{E(bv.get("why", ""))}</div>'
            f'<div class="fix"><b>الدرس: </b>{E(bv.get("lesson", ""))}</div></div>') if bv else ""
    pages.append(f'''<h2>حسابك بالأرقام</h2><p class="lead">{E(c.get("numbers_intro", ""))}</p>
<div class="grid g4">{tiles}</div>
<div class="card" style="margin-top:12px"><b style="color:var(--navy)">مشاهدات آخر {len(last10)} ريلز</b>
<div class="bars" style="margin-top:22px">{bars}</div><div class="cap">من الأقدم للأحدث · الغامق = الأعلى</div></div>{best}{platform_card(c)}''')

    # 3 problems
    probs = ""
    for i, p in enumerate(c["problems"], 1):
        ex = f'<div class="example">{E(p["example"])}</div>' if p.get("example") else ""
        probs += (f'<div class="card prob"><div class="ic">{i}</div><div><h3>{E(p["title"])}</h3>'
                  f'<div class="why">{E(p["evidence"])}</div><div class="fix"><b>الحل: </b>{E(p["fix"])}</div>{ex}</div></div>')
    pages.append(f'<h2>3 حاجات لو اتصلحت هتفرق معاك</h2><p class="lead">كل نقطة معاها حلها كامل، تقدر تبدأ فيه النهارده.</p>{probs}')

    fb_page = facebook_section(fb)
    if fb_page:
        pages.append(fb_page)

    # 4 videos (only if the user's review or notes exist)
    if c.get("video_ratings") or c.get("video_notes") or c.get("privacy_note"):
        rows = "".join(f'<div class="rate"><b>{E(r["item"])}</b><span>{dots(r.get("score"))}</span><span>{E(r.get("note", ""))}'
                       + (f'<br><span style="color:var(--teal)"><b>الحل: </b>{E(r["fix"])}</span>' if r.get("fix") else "") + '</span></div>'
                       for r in c.get("video_ratings", []))
        notes = "".join(f"<li>{E(x)}</li>" for x in c.get("video_notes", []))
        priv = f'<div class="note"><b>تنبيه مهم: </b>{E(c["privacy_note"])}</div>' if c.get("privacy_note") else ""
        pages.append(f'<h2>ملاحظات على فيديوهاتك</h2><p class="lead">{E(c.get("video_intro", ""))}</p>'
                     f'<div class="card">{rows}{"<ul>" + notes + "</ul>" if notes else ""}</div>{priv}')

    # 4b posting time (always framed as an experiment, never as a fact)
    pt = c.get("posting_time")
    if pt:
        src = "من إحصائيات حسابك (أوقات تواجد متابعينك)" if pt.get("source") == "insights" else "من أداء بوستاتك اللي فاتت"
        pages.append(f'<h2>أحسن وقت للنشر: تجربة نقترحها</h2><p class="lead">{E(pt.get("basis", ""))}</p>'
                     f'<div class="card"><div class="fix"><b>جرّب: </b>{E(pt["experiment"])}</div>'
                     f'<p style="margin:8px 0 0;font-size:12px;color:#667">{src}. هنقارن بعد شهر ونثبّت اللي ينجح.</p></div>')

    # 5 specialty patterns
    pats = ""
    for i, p in enumerate(c.get("patterns", []), 1):
        exs = "".join(f'<li><a href="{E(x["url"])}">{E(x["label"])}</a>'
                      f'{(" · " + n(x["views"]) + " مشاهدة") if x.get("views") else ""}</li>' for x in p.get("examples", []))
        you = f'<div class="you"><b>عندك: </b>{E(p["you"])}</div>' if p.get("you") else ""
        pats += (f'<div class="card pat"><h3><span class="num" style="display:inline-flex;width:24px;height:24px;border-radius:50%;'
                 f'background:var(--teal2);color:#fff;align-items:center;justify-content:center;font-size:12px;margin-inline-end:6px">{i}</span>'
                 f'{E(p["title"])}</h3><div class="ev">{E(p["evidence"])}</div><ul>{exs}</ul>{you}</div>')
    ptab = ""
    if peers:
        rows = "".join(f'<tr><td dir="ltr" style="text-align:right">@{E(a["username"])}</td><td>{n(a["followers"])}</td>'
                       f'<td>{n(a["median_views"])}</td></tr>' for a in sorted(peers["accounts"], key=lambda a: -(a["followers"] or 0)))
        ptab = (f'<div class="card" style="margin-top:6px"><table><tr><th>الدكتور</th><th>المتابعين</th>'
                f'<th>المشاهدات المعتادة للريل</th></tr>{rows}<tr><td><b>انت</b></td><td>{n(base["followers"])}</td>'
                f'<td>{n(base["median_views_last10_reels"])}</td></tr></table></div>')
    pages.append(f'<h2>إيه اللي شغال في تخصصك</h2><p class="lead">{E(c.get("patterns_intro", ""))}</p>{pats}{ptab}')

    # 6 next
    nx = c["next"]
    lis = "".join(f"<li>{E(x)}</li>" for x in nx.get("bullets", []))
    cta = f'<div class="cta">{E(nx["cta"])}</div>' if nx.get("cta") else ""
    meas = f'<div class="measure">{E(c["measure_note"])}</div>' if c.get("measure_note") else ""
    pages.append(f'<h2>{E(nx["title"])}</h2><p class="lead">{E(nx.get("intro", ""))}</p>'
                 f'<div class="card next"><ul>{lis}</ul></div>{cta}{meas}')

    total = len(pages)
    header = "تحليل حساب إنستجرام وفيسبوك" if fb else "تحليل حساب إنستجرام"
    body = "".join(page(x, brand, date, i + 1, total, header) for i, x in enumerate(pages))
    return ('<!doctype html><html lang="ar" dir="rtl"><head><meta charset="utf-8">'
            f'<title>{E(header)}: {E(doc["name"])}</title>'
            '<link rel="preconnect" href="https://fonts.googleapis.com">'
            '<link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans+Arabic:wght@400;600;700&display=swap" rel="stylesheet">'
            f'<style>{CSS}</style></head><body>{body}</body></html>')


def client_md(d, c):
    base, doc = d["baseline"], c["doctor"]
    L = [f"# تحليل حسابك على إنستجرام: {doc['name']}", "",
         f"{doc['specialty']} · @{doc['handle']} · {c.get('date', base['taken_at'][:10])} · {c.get('brand', '')}", ""]
    if c.get("opening_quote"):
        L += [f"> «{c['opening_quote']}»", ""]
    L += [f"**{c['diagnosis']}**", "", "## حسابك بالأرقام", "",
          f"- المتابعين: {n(base['followers'])}", f"- بوستات آخر 30 يوم: {base['posts_last_30d']}",
          f"- المشاهدات المعتادة للريل (آخر 10): {n(base['median_views_last10_reels'])}"]
    if c.get("best_video"):
        b = c["best_video"]
        L += ["", f"**أنجح فيديو:** [{b['title']}]({b['url']}). {b['why']} **الدرس:** {b['lesson']}"]
    if c.get("platform_compare"):
        pc = c["platform_compare"]
        L += ["", f"### {pc['title']}", "| | إنستجرام | فيسبوك |", "|---|---|---|"]
        L += [f"| {r[0]} | {r[1]} | {r[2]} |" for r in pc["rows"]] + ["", pc["note"]]
    L += ["", "## 3 حاجات لو اتصلحت هتفرق معاك", ""]
    for i, p in enumerate(c["problems"], 1):
        L += [f"### {i}. {p['title']}", p["evidence"], "", f"**الحل:** {p['fix']}"]
        if p.get("example"):
            L += ["", "```", p["example"], "```"]
        L += [""]
    if c.get("video_ratings") or c.get("video_notes") or c.get("privacy_note"):
        L += ["## ملاحظات على فيديوهاتك", ""]
        L += [f"- **{r['item']}** ({r.get('score', '-')}/10): {r.get('note', '')}" + (f" **الحل:** {r['fix']}" if r.get('fix') else "") for r in c.get("video_ratings", [])]
        L += [f"- {x}" for x in c.get("video_notes", [])]
        if c.get("privacy_note"):
            L += ["", f"> **تنبيه مهم:** {c['privacy_note']}"]
        L += [""]
    if c.get("posting_time"):
        pt = c["posting_time"]
        src = "من إحصائيات حسابك (أوقات تواجد متابعينك)" if pt.get("source") == "insights" else "من أداء بوستاتك اللي فاتت"
        L += ["## أحسن وقت للنشر: تجربة نقترحها", "", pt.get("basis", ""), "",
              f"**جرّب:** {pt['experiment']}", "", f"_{src}. هنقارن بعد شهر ونثبّت اللي ينجح._", ""]
    L += ["## إيه اللي شغال في تخصصك", "", c.get("patterns_intro", ""), ""]
    for i, p in enumerate(c.get("patterns", []), 1):
        L += [f"### {i}. {p['title']}", p["evidence"]]
        L += [f"- [{x['label']}]({x['url']})" + (f" · {n(x['views'])} مشاهدة" if x.get("views") else "") for x in p.get("examples", [])]
        if p.get("you"):
            L += [f"- **عندك:** {p['you']}"]
        L += [""]
    nx = c["next"]
    L += [f"## {nx['title']}", nx.get("intro", ""), ""] + [f"- {x}" for x in nx.get("bullets", [])]
    if nx.get("cta"):
        L += ["", f"**{nx['cta']}**"]
    if c.get("measure_note"):
        L += ["", c["measure_note"]]
    return "\n".join(L) + "\n"


def internal_md(d, c, dirp):
    an, base, own, peers = d["analysis"], d["baseline"], d.get("own"), d.get("peers")
    L = [f"# داخلي: تحليل @{c['doctor']['handle']} ({c.get('mode')})", "",
         "## لقطة البداية (للـCase Study)", "```json", json.dumps(base, ensure_ascii=False, indent=1), "```", "",
         "## صحة الحساب", f"- المرحلة: {an['stage']['code']} ({'، '.join(an['stage']['reasons'])})",
         f"- النشر: {an['cadence']}", f"- الاتجاه: {an['trend']}",
         "- الفورمات: " + "، ".join(f"{k}: n={v['n']}, views={v['median_views']}, likes={v['median_likes']}"
                                   for k, v in an["patterns"]["format"].items()), "", "## الناجح والضعيف (مقارنة بمعتاد حسابه)"]
    L += [f"- ناجح {w['format']} [{w['url']}]({w['url']}) {w['views']} مشاهدة، {w['index']}×: {w['hook']}" for w in an["winners"][:5]]
    L += [f"- ضعيف {w['format']} [{w['url']}]({w['url']}) {w['views']} مشاهدة، {w['index']}×: {w['hook']}" for w in an["losers"][:5]]
    if own:
        L += ["", "## سكريبتات الريلز المختارة"]
        for v in own["videos"]:
            L += [f"### {v['role']}: [{v['shortCode']}]({v['url']}) · {v['views']} مشاهدة · {v['index']}×",
                  v["transcript"] or "(مفيش كلام في الفيديو)", ""]
        L += [f"تكلفة السكريبتات والفيديو: حوالي {own.get('cost_usd')} دولار"]
    s = os.path.join(dirp, "scan", "summary.md")
    if os.path.exists(s):
        L += ["", "## مسح التخصص (من scan/summary.md)", open(s, encoding="utf-8").read()]
    L += ["", "## المحتوى اللي اتكتب للعميل (audit_content.json)", "```json",
          json.dumps(c, ensure_ascii=False, indent=1), "```"]
    return "\n".join(L) + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", required=True)
    ap.add_argument("--content", required=True)
    ap.add_argument("--no-pdf", action="store_true")
    a = ap.parse_args()
    d = {"analysis": load(os.path.join(a.dir, "analysis.json")), "baseline": load(os.path.join(a.dir, "baseline.json")),
             "facebook": load(os.path.join(a.dir, "analysis_facebook.json")),
         "own": load(os.path.join(a.dir, "own_reels.json")), "peers": load(os.path.join(a.dir, "scan", "peers_analysis.json"))}
    if not d["analysis"] or not d["baseline"]:
        raise SystemExit("analysis.json and baseline.json are required (run Step 2 first)")
    c = load(a.content)
    out = lambda name: os.path.join(a.dir, name)
    open(out("audit_client.html"), "w", encoding="utf-8").write(build(d, c))
    open(out("audit_client.md"), "w", encoding="utf-8").write(client_md(d, c))
    open(out("audit_internal.md"), "w", encoding="utf-8").write(internal_md(d, c, a.dir))
    print("written: audit_client.html, audit_client.md, audit_internal.md")
    if not a.no_pdf:
        js = os.path.join(os.path.dirname(os.path.abspath(__file__)), "render_pdf.js")
        env = dict(os.environ)
        r = subprocess.run(["node", js, os.path.abspath(out("audit_client.html")), os.path.abspath(out("audit_client.pdf"))],
                           capture_output=True, text=True, env=env)
        print(r.stdout.strip() or r.stderr.strip())


if __name__ == "__main__":
    main()
