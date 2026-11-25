"""Summarise run_conversations.py output and write a readable transcripts file.

Usage:
    python tools/summarize_conversations.py <results.jsonl> [--failures] [--transcripts out.md] [--review review.json]

review.json (optional) holds manual verdicts that override the grader:
    {"L7#2": {"pass": false, "severity": "High", "note": "why"}, ...}
"""
import json
import sys
from collections import defaultdict

sys.stdout.reconfigure(encoding="utf-8")
args = sys.argv[1:]
rows = [json.loads(l) for l in open(args[0], encoding="utf-8")]
review = {}
if "--review" in args:
    review = json.load(open(args[args.index("--review") + 1], encoding="utf-8"))


def verdict(r):
    key = f"{r['id']}#{r['run']}"
    if key in review:
        v = review[key]
        return v["pass"], v.get("severity", r.get("severity_if_fail")), v.get("note", ""), "manual"
    g = r.get("grader", {})
    return g.get("pass"), r.get("severity_if_fail"), g.get("reason", ""), "grader"


cat = defaultdict(lambda: [0, 0])
conv = defaultdict(lambda: [0, 0])
fails = []
for r in rows:
    if "error" in r:
        print("ERROR", r["id"], r["run"], r["error"][:200])
        continue
    ok, sev, note, src = verdict(r)
    cat[r["category"]][0] += bool(ok)
    cat[r["category"]][1] += 1
    conv[(r["id"], r["title"])][0] += bool(ok)
    conv[(r["id"], r["title"])][1] += 1
    if not ok:
        fails.append((r, sev, note, src))

total = sum(v[1] for v in cat.values())
passed = sum(v[0] for v in cat.values())
print(f"## Overall: {passed}/{total} conversations passed\n")
print("| Category | Passed |\n|---|---|")
for c, (ok, n) in cat.items():
    print(f"| {c} | {ok}/{n} |")
print("\n| ID | Test | Passed |\n|---|---|---|")
for (cid, title), (ok, n) in sorted(conv.items()):
    print(f"| {cid} | {title} | {ok}/{n} |")

if "--failures" in args:
    print(f"\n## Failures ({len(fails)})\n")
    for r, sev, note, src in sorted(fails, key=lambda x: (x[0]["id"], x[0]["run"])):
        print(f"### {r['id']} run {r['run']} [{sev}] ({src}): {r['title']}\nWhy: {note}")
        for t in r["transcript"]:
            print(f"USER: {t['user'][:300]}\nBEA: {t['bot']}\n")

if "--transcripts" in args:
    out = args[args.index("--transcripts") + 1]
    lines = ["# Full product test: transcripts", "",
             f"Model: `{rows[0].get('model')}` · Conversations: {len(rows)} · Collected: "
             f"{min(r.get('time_utc', '') for r in rows)} (UTC)", "",
             "Every bot reply is copied verbatim from `results.jsonl`. Long user inputs are shortened here.", ""]
    for r in sorted((r for r in rows if "error" not in r), key=lambda x: (x["category"], x["id"], x["run"])):
        ok, sev, note, src = verdict(r)
        mark = "PASS" if ok else f"FAIL ({sev})"
        lines += [f"## {r['id']} run {r['run']}: {r['title']} · {mark}", "",
                  f"*Category:* {r['category']}  ", f"*Expected:* {r['expected']}  ",
                  f"*Verdict ({src}):* {note}", ""]
        for t in r["transcript"]:
            u = t["user"] if len(t["user"]) < 600 else t["user"][:300] + f" [... {len(t['user'])} characters in total ...]"
            lines += ["**User:** " + u.replace("\n", " "), ""]
            lines += ["> " + l if l else ">" for l in t["bot"].strip().splitlines()]
            lines += [""]
    open(out, "w", encoding="utf-8").write("\n".join(lines))
    print(f"\nwrote {out}")
