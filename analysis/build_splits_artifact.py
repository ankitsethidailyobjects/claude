#!/usr/bin/env python3
import base64, pandas as pd
SEG="analysis/seg"
img=base64.b64encode(open(f"{SEG}/cohort_splits_chart.png","rb").read()).decode()
r=pd.read_csv(f"{SEG}/cohort_splits.csv")
cohorts=["O1 (New)","O2","Power Users","Deal Seekers","Light Users"]
COL={"O1 (New)":"#94a3b8","O2":"#0e7490","Power Users":"#16a34a","Deal Seekers":"#c2560f","Light Users":"#7c3aed"}
def heat(v,vmax=65):
    import colorsys
    t=max(0,min(1,v/vmax)); # green scale
    return f"background:rgba(22,163,74,{0.08+0.55*t});"
dimlabel={"ALL":"Overall","Activity":"Activity / dormancy","Value":"Value tier","Affinity":"Category affinity","SubCategory":"Primary sub-category"}
def cohort_block(c):
    sub=r[r.cohort==c]
    allrow=sub[sub.dimension=="ALL"].iloc[0]
    h=f'<div class="cblock"><div class="chead" style="border-color:{COL[c]}"><span class="cn">{c}</span>'\
      f'<span class="cs">{int(allrow.users):,} users · overall retention {allrow.ret_1m:.0f}% / {allrow.ret_1q:.0f}% / {allrow.ret_1y:.0f}% (M/Q/Y)</span></div>'
    for dim in ["Activity","Value","Affinity","SubCategory"]:
        dd=sub[sub.dimension==dim]
        if not len(dd): continue
        h+=f'<div class="dim"><div class="dt">{dimlabel[dim]}</div><table><thead><tr><th>Bucket</th><th class="n">Users</th><th class="n">1-month</th><th class="n">1-quarter</th><th class="n">1-year</th></tr></thead><tbody>'
        for _,row in dd.iterrows():
            h+=f'<tr><td>{row.bucket}</td><td class="n">{int(row.users):,}</td><td class="n">{row.ret_1m:.1f}%</td><td class="n">{row.ret_1q:.1f}%</td><td class="n" style="{heat(row.ret_1y)}">{row.ret_1y:.1f}%</td></tr>'
        h+='</tbody></table></div>'
    h+='</div>'
    return h
body="\n".join(cohort_block(c) for c in cohorts)
HTML=f"""<title>Cohort × Attribute Retention</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
:root{{--bg:#f6f7f9;--surface:#fff;--ink:#0f1b2d;--muted:#5b6b7f;--faint:#8a99ab;--line:#e4e8ee;--line2:#eef1f5;--accent:#2563eb;--accent-soft:#eaf0fe;--shadow:0 1px 2px rgba(15,27,45,.04),0 6px 22px rgba(15,27,45,.06);}}
@media(prefers-color-scheme:dark){{:root:not([data-theme="light"]){{--bg:#0b1220;--surface:#121b2b;--ink:#e8eef6;--muted:#9fb0c4;--faint:#6b7d93;--line:#25324a;--line2:#1b2637;--accent:#6ea0ff;--accent-soft:#182741;--shadow:0 1px 2px rgba(0,0,0,.3),0 8px 30px rgba(0,0,0,.35);}}}}
:root[data-theme="dark"]{{--bg:#0b1220;--surface:#121b2b;--ink:#e8eef6;--muted:#9fb0c4;--faint:#6b7d93;--line:#25324a;--line2:#1b2637;--accent:#6ea0ff;--accent-soft:#182741;--shadow:0 1px 2px rgba(0,0,0,.3),0 8px 30px rgba(0,0,0,.35);}}
*{{box-sizing:border-box}} body{{margin:0;background:var(--bg);color:var(--ink);font-family:ui-sans-serif,system-ui,-apple-system,"Segoe UI",Roboto,sans-serif;line-height:1.55}}
.wrap{{max-width:1000px;margin:0 auto;padding:40px 20px 90px}}
.eyebrow{{font-family:ui-monospace,monospace;font-size:12px;letter-spacing:.14em;text-transform:uppercase;color:var(--accent);margin:0 0 8px}}
h1{{font-size:clamp(24px,3.6vw,34px);line-height:1.1;letter-spacing:-.02em;margin:0 0 10px;font-weight:800;text-wrap:balance}}
.sub{{font-size:16px;color:var(--muted);margin:0 0 6px;max-width:80ch}}
.chartbox{{background:var(--surface);border:1px solid var(--line);border-radius:14px;padding:12px;box-shadow:var(--shadow);overflow-x:auto;margin:18px 0}}
.chartbox img{{width:100%;min-width:720px;height:auto;display:block;border-radius:6px}}
.cblock{{background:var(--surface);border:1px solid var(--line);border-radius:14px;box-shadow:var(--shadow);padding:16px 18px;margin:16px 0}}
.chead{{border-left:5px solid;padding-left:12px;margin-bottom:10px}}
.chead .cn{{font-size:20px;font-weight:800;display:block}}
.chead .cs{{font-size:13px;color:var(--muted)}}
.dim{{margin:10px 0}}
.dt{{font-family:ui-monospace,monospace;font-size:11px;letter-spacing:.05em;text-transform:uppercase;color:var(--faint);margin:8px 0 4px}}
table{{border-collapse:collapse;width:100%;font-size:13px}}
th,td{{text-align:left;padding:6px 12px;border-bottom:1px solid var(--line2)}}
th.n,td.n{{text-align:right;font-variant-numeric:tabular-nums}}
thead th{{font-size:11px;color:var(--faint);background:var(--line2);text-transform:uppercase;letter-spacing:.03em}}
.callout{{border-left:4px solid var(--accent);background:linear-gradient(90deg,var(--accent-soft),var(--surface) 62%);border-radius:0 12px 12px 0;padding:14px 18px;margin:16px 0}}
.foot{{margin-top:40px;padding-top:16px;border-top:1px solid var(--line);font-size:12px;color:var(--faint)}}
</style>
<div class="wrap">
<p class="eyebrow">DailyObjects · Cohort deep-dive</p>
<h1>Cohort × attribute — user split &amp; retention</h1>
<p class="sub">For each cohort, the user count and monthly / quarterly / yearly return rate in every bucket (activity, value, category affinity, sub-category). Anchor 31 Jul 2025 → forward 12 months. Yearly cells are heat-shaded.</p>
<div class="chartbox"><img alt="Yearly retention by cohort and attribute" src="data:image/png;base64,{img}"></div>
<div class="callout"><strong>Biggest levers in the data:</strong> (1) <b>Activity dominates</b> — an Active Power User returns at 62% vs 32% if Dormant; the same 3–4× gap holds in every cohort. (2) <b>Sub-category stickiness</b> — Wireless Charger, Organisers, Desks &amp; Backpacks buyers retain far better than "Sale", "Mobile Accessories" and "Bags & Sleeves" buyers, who are near one-and-done. (3) <b>Designer/Bags buyers retain slightly below Tech</b> in most cohorts — a reason to cross-sell bags to sticky Tech buyers rather than acquire bags-only.</div>
{body}
<div class="foot">Buckets with &lt;50 users are suppressed. Anchor 31 Jul 2025; retention = share placing ≥1 order within 30 / 90 / 365 days. Attributes measured as-of the anchor (leakage-safe).</div>
</div>
"""
open(f"{SEG}/cohort_splits.html","w").write(HTML); print("wrote cohort_splits.html",len(HTML))
