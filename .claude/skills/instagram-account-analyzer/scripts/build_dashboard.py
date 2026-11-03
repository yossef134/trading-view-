#!/usr/bin/env python3
"""Build a single-file, offline HTML dashboard from analysis.json.

usage: build_dashboard.py --analysis analysis.json --out dashboard.html
                          [--insights insights.json] [--competitors competitors.json]

The page needs no network and no libraries. All text coming from the data is
inserted with textContent (never innerHTML), and the data blob is escaped so a
caption containing "</script>" cannot break out of the page.

insights.json (optional, written by Claude in the report step) - every key is
optional; see references/insights-schema.md. Without it the dashboard still
renders every number and an auto-generated summary.
"""
import argparse
import json
from pathlib import Path


def load(path):
    return json.loads(Path(path).read_text(encoding="utf-8")) if path else None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--analysis", required=True)
    ap.add_argument("--insights")
    ap.add_argument("--competitors")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()

    data = {"analysis": load(a.analysis), "insights": load(a.insights), "competitors": load(a.competitors)}
    blob = (json.dumps(data, ensure_ascii=False)
            .replace("</", "<\\/").replace("<!--", "<\\!--")
            .replace("\u2028", "\\u2028").replace("\u2029", "\\u2029"))
    tpl = Path(__file__).with_name("dashboard_template.html").read_text(encoding="utf-8")
    if "__DATA_JSON__" not in tpl:
        raise SystemExit("template placeholder __DATA_JSON__ missing")
    html = tpl.replace("__DATA_JSON__", blob, 1)
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    Path(a.out).write_text(html, encoding="utf-8")
    print(f"dashboard -> {a.out} ({len(html)//1024} KB)")


if __name__ == "__main__":
    main()
