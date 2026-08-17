#!/usr/bin/env python3
import base64, pandas as pd, numpy as np
SEG="analysis/seg"
def b64(p): return base64.b64encode(open(p,"rb").read()).decode()
ch_cohort=b64(f"{SEG}/cohorts_chart.png"); ch_event=b64(f"{SEG}/events_2025.png")
prod=pd.read_csv(f"{SEG}/profile_3cohort_prod.csv",index_col=0)
dev=pd.read_csv(f"{SEG}/profile_3cohort_dev.csv",index_col=0)
mp=pd.read_csv(f"{SEG}/mapping_3cohort.csv")
order=["Power Users","Deal Seekers","Light Users"]
prod=prod.reindex(order); dev=dev.reindex(order)
crm={
"Power Users":"<b>Protect &amp; grow.</b> They already convert in BAU. Early access to launches, full-price cross-sell — especially into Designer/Bags (they're 78% Tech). VIP care; suppress reflexive deep discounts.",
"Deal Seekers":"<b>Margin-aware, event-timed.</b> 80% of their orders are on discount and they mostly go quiet between sales. Concentrate contact around events they already respond to, but push <em>bundles / higher-AOV</em> to lift margin and nudge toward full price. Event-triggered reactivation.",
"Light Users":"<b>Low-cost activation.</b> Low frequency, low value, most lapsed. Cheap nudges toward a 4th order + one well-timed event offer; don't over-invest — sunset the unresponsive.",
}
def rows():
    out=[]
    for c in order:
        p=prod.loc[c]; d=dev.loc[c]
        out.append(f"<tr><td><strong>{c}</strong></td><td class='num'>{int(p['users']):,}</td><td class='num'>{p['pct']:.0f}%</td>"
          f"<td class='num'>{p['avg_orders']:.1f}</td><td class='num'>₹{p['med_gmv']:,.0f}</td>"
          f"<td class='num'>{p['pct_disc']*100:.0f}%</td><td class='num'>{p['eff_disc']*100:.0f}%</td>"
          f"<td class='num'>{p['med_recency']:.0f}d</td><td class='num big'>{d['retained']*100:.0f}%</td></tr>")
    return "\n".join(out)
def dist(col):
    vc=mp[col].value_counts();tot=len(mp)
    return " · ".join(f"<b>{k}</b> {100*v/tot:.0f}%" for k,v in vc.items())

HTML=f"""<title>DailyObjects 3-Cohort Model</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
:root{{--bg:#f6f7f9;--surface:#fff;--ink:#0f1b2d;--muted:#5b6b7f;--faint:#8a99ab;--line:#e4e8ee;--line2:#eef1f5;--accent:#2563eb;--accent-soft:#eaf0fe;--green:#15803d;--green-soft:#e7f3ec;--amber:#c2560f;--amber-soft:#fdeee4;--shadow:0 1px 2px rgba(15,27,45,.04),0 6px 22px rgba(15,27,45,.06);}}
@media(prefers-color-scheme:dark){{:root:not([data-theme="light"]){{--bg:#0b1220;--surface:#121b2b;--ink:#e8eef6;--muted:#9fb0c4;--faint:#6b7d93;--line:#25324a;--line2:#1b2637;--accent:#6ea0ff;--accent-soft:#182741;--green:#57c98a;--green-soft:#13241a;--amber:#ff8a4c;--amber-soft:#2a1d15;--shadow:0 1px 2px rgba(0,0,0,.3),0 8px 30px rgba(0,0,0,.35);}}}}
:root[data-theme="dark"]{{--bg:#0b1220;--surface:#121b2b;--ink:#e8eef6;--muted:#9fb0c4;--faint:#6b7d93;--line:#25324a;--line2:#1b2637;--accent:#6ea0ff;--accent-soft:#182741;--green:#57c98a;--green-soft:#13241a;--amber:#ff8a4c;--amber-soft:#2a1d15;--shadow:0 1px 2px rgba(0,0,0,.3),0 8px 30px rgba(0,0,0,.35);}}
*{{box-sizing:border-box}} body{{margin:0;background:var(--bg);color:var(--ink);font-family:ui-sans-serif,system-ui,-apple-system,"Segoe UI",Roboto,sans-serif;line-height:1.6}}
.wrap{{max-width:1000px;margin:0 auto;padding:44px 22px 100px}}
.eyebrow{{font-family:ui-monospace,monospace;font-size:12px;letter-spacing:.14em;text-transform:uppercase;color:var(--accent);margin:0 0 10px}}
h1{{font-size:clamp(26px,4vw,38px);line-height:1.1;letter-spacing:-.02em;margin:0 0 12px;text-wrap:balance;font-weight:800}}
.sub{{font-size:17px;color:var(--muted);margin:0;max-width:76ch}}
h2{{font-size:13px;font-family:ui-monospace,monospace;letter-spacing:.1em;text-transform:uppercase;color:var(--accent);margin:0 0 6px}}
.sec-title{{font-size:22px;font-weight:800;letter-spacing:-.015em;margin:0 0 14px}}
section{{margin-top:44px}} section>hr{{border:none;border-top:2px solid var(--line);margin:0 0 18px}}
p{{margin:0 0 12px;max-width:84ch}} strong{{color:var(--ink)}}
.callout{{border-left:4px solid var(--accent);background:linear-gradient(90deg,var(--accent-soft),var(--surface) 62%);border-radius:0 12px 12px 0;padding:16px 20px;margin:16px 0}}
.callout.g{{border-color:var(--green);background:linear-gradient(90deg,var(--green-soft),var(--surface) 62%)}}
.callout.a{{border-color:var(--amber);background:linear-gradient(90deg,var(--amber-soft),var(--surface) 62%)}}
.kpis{{display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin:24px 0 0}} @media(max-width:720px){{.kpis{{grid-template-columns:repeat(2,1fr)}}}}
.kpi{{background:var(--surface);border:1px solid var(--line);border-radius:12px;padding:15px}}
.kpi .n{{font-size:22px;font-weight:800;letter-spacing:-.02em;color:var(--accent);font-variant-numeric:tabular-nums}} .kpi .l{{font-size:12.5px;color:var(--muted);margin-top:3px}}
.chartbox{{background:var(--surface);border:1px solid var(--line);border-radius:14px;padding:12px;box-shadow:var(--shadow);overflow-x:auto;margin:16px 0}}
.chartbox img{{width:100%;min-width:700px;height:auto;display:block;border-radius:6px}}
.tablebox{{overflow-x:auto;border:1px solid var(--line);border-radius:12px;background:var(--surface);box-shadow:var(--shadow);margin:14px 0}}
table{{border-collapse:collapse;width:100%;min-width:620px;font-size:13.5px}}
th,td{{text-align:left;padding:10px 13px;border-bottom:1px solid var(--line2);vertical-align:top}}
th.num,td.num{{text-align:right;font-variant-numeric:tabular-nums}}
thead th{{font-family:ui-monospace,monospace;font-size:10.5px;letter-spacing:.05em;text-transform:uppercase;color:var(--faint);background:var(--line2)}}
tbody tr:last-child td{{border-bottom:none}} td.big{{font-weight:750;color:var(--green)}}
.chips{{display:flex;flex-wrap:wrap;gap:10px;margin:12px 0}}
.chip{{background:var(--surface);border:1px solid var(--line);border-radius:10px;padding:10px 14px;font-size:13px}}
.chip .t{{font-family:ui-monospace,monospace;font-size:10.5px;letter-spacing:.05em;text-transform:uppercase;color:var(--faint);display:block;margin-bottom:2px}}
.foot{{margin-top:56px;padding-top:18px;border-top:1px solid var(--line);font-size:12px;color:var(--faint)}}
code{{font-family:ui-monospace,monospace;font-size:.88em;background:var(--line2);padding:1px 5px;border-radius:5px}}
</style>
<div class="wrap">
<p class="eyebrow">DailyObjects · 3-cohort model · v3 (discount-enriched)</p>
<h1>Power Users, Deal Seekers &amp; Light Users</h1>
<p class="sub">Three actionable cohorts across all 203,281 customers with 3+ orders — now using a <strong>discount signal that includes price-led event drops</strong> (HPS, Diwali, etc.), not just coupons. Category-affinity scores layered on top.</p>

<div class="kpis">
<div class="kpi"><div class="n">203,281</div><div class="l">customers with 3+ orders (all sliced together)</div></div>
<div class="kpi"><div class="n">21% → 49%</div><div class="l">orders on discount: coupon-only vs enriched (incl. events)</div></div>
<div class="kpi"><div class="n">3 cohorts</div><div class="l">Power (28%) · Deal Seeker (31%) · Light (42%)</div></div>
<div class="kpi"><div class="n">48% vs 25%</div><div class="l">future retention: Power vs Light</div></div>
</div>

<div class="callout a" style="margin-top:22px"><strong>Why this changes the picture:</strong> the DMR only stores the final price paid, so a customer who buys only during HPS/Diwali price drops looked "full-price" before. Detecting event price-drops from weekly ASP nearly <strong>doubles</strong> the measured discount footprint (coupon-only 21% → 49% of orders) and reclassifies many quiet "full-price" buyers as <strong>Deal Seekers</strong>.</div>

<section><hr><h2>Step 1</h2><p class="sec-title">Price-led discount detection (validated on 2025)</p>
<p>Weekly category ASP (avg selling price) from the DMR dips sharply during sale events — matching the elasticity sheet's event weeks. Reference (list) price per category = 65th-percentile weekly ASP; an order's <em>price-led discount depth</em> = how far below that reference its category's price sat that week.</p>
<div class="chartbox"><img alt="2025 weekly ASP with shaded event windows" src="data:image/png;base64,{ch_event}"></div>
<div class="tablebox"><table><thead><tr><th>2025 event</th><th>Weeks</th><th>Typical price drop*</th></tr></thead><tbody>
<tr><td>Republic Day</td><td>W3–5 (late Jan)</td><td>Tech ~10% · Bags ~6–9%</td></tr>
<tr><td><strong>HPS — End-FY (March)</strong></td><td>W12–14</td><td><strong>Tech 30–48% · Bags 20–35%</strong> (deepest)</td></tr>
<tr><td><strong>HPS — Aug/Sep</strong></td><td>W35–39</td><td>Tech 29–54% · Bags 12–34%</td></tr>
<tr><td>Diwali / Festive</td><td>W42–43 (Oct)</td><td>Tech ~7–37% · Bags ~7–15%</td></tr>
<tr><td>Black Friday / Nov</td><td>W46–47</td><td>~8%</td></tr>
<tr><td>Year-end</td><td>W50–52 (Dec)</td><td>Tech 14–35% · Bags 10–26%</td></tr>
</tbody></table></div>
<p class="sub" style="font-size:13.5px">*Depths from the elasticity sheet (sub-category ASP %Δ) — corroborated by the DMR ASP dips above. The same detector runs on <strong>all years 2020–2026</strong>; per-order discount = <code>max(coupon/DMR discount, price-led event depth)</code>.</p>
<div class="callout"><strong>Data-quality note:</strong> DMR coupon fields are unreliable in older years (2020/21 over-populated, 2022 absent), so coupon counts only from 2023; the <em>price-led signal is the consistent cross-year method</em>. Enriched discount penetration by year: 2023 69% · 2024 48% · 2025 49% · 2026 59%.</div>
</section>

<section><hr><h2>Step 2</h2><p class="sec-title">The three cohorts (all 3+ orders)</p>
<p>K-Means (k=3) on frequency + value + <strong>enriched</strong> discount reliance. Everyone with 3+ orders is clustered together — behaviour, not an order-count cut, defines the cohort.</p>
<div class="tablebox"><table>
<thead><tr><th>Cohort</th><th class="num">Users</th><th class="num">%</th><th class="num">Avg orders</th><th class="num">Med GMV</th><th class="num">% disc (enriched)</th><th class="num">Eff. disc</th><th class="num">Recency</th><th class="num">Fwd retention*</th></tr></thead>
<tbody>{rows()}</tbody></table></div>
<div class="chartbox"><img alt="Cohort retention, sizes, discount reliance" src="data:image/png;base64,{ch_cohort}"></div>
<p class="sub" style="font-size:13.5px">*Forward 12-month retention on the hold-out snapshot (mature as of 31 Jul 2025 → next 12 months). Separates 48% / 29% / 25% — validated.</p>
<div class="callout g"><strong>Read:</strong> <b>Power Users</b> (28%) are frequent, high-value and convert in BAU — retention 48%. <b>Deal Seekers</b> (31%) place 80% of orders on discount (54% during price-led events), spend less and go quiet between sales. <b>Light Users</b> (42%) are low-frequency, low-value, largely lapsed — the activation challenge.</div>
</section>

<section><hr><h2>Step 3</h2><p class="sec-title">Category-affinity scores (Tech vs Designer/Bags)</p>
<p>Each customer gets a continuous <code>tech_score</code> and <code>bags_score</code> (share of spend), plus a label. Base is overwhelmingly Tech; Designer/Bags (higher AOV) is a small pool → cross-sell headroom for Power/Core.</p>
<div class="chips"><div class="chip"><span class="t">Affinity label</span>{dist('cat_affinity')}</div><div class="chip"><span class="t">Activity overlay</span>{dist('activity_state')}</div><div class="chip"><span class="t">Value tier</span>{dist('value_tier')}</div></div>
<p class="sub" style="font-size:13.5px">Affinity is a per-user <em>score</em> (0–1), not a cohort — it selects the creative/offer. Sub-category-level affinity is the planned next iteration.</p>
</section>

<section><hr><h2>Step 4</h2><p class="sec-title">CRM decisioning</p>
<div class="tablebox"><table><thead><tr><th>Cohort</th><th>Recommended posture</th></tr></thead><tbody>
{"".join(f"<tr><td><strong>{c}</strong></td><td>{crm[c]}</td></tr>" for c in order)}
</tbody></table></div>
<p>Final CRM segment = <code>Cohort × Activity (Active/Lapsed/Dormant) × Affinity (Tech/Bags) × Value tier</code>. The mapping table <code>mapping_3cohort.csv</code> carries all of these per customer — the MoEngage-ready attribute set.</p>
</section>

<div class="foot">DailyObjects DMR 2020–Jul 2026 · 2.86M attributable orders · 1.44M identities · mature (≥3 orders) = 203,281 · discount enriched with price-led event detection (validated vs elasticity sheet) · K-Means k=3 · hold-out validation T₀=31 Jul 2025. Category affinity at top level (sub-category next). v3.</div>
</div>
"""
open(f"{SEG}/results.html","w").write(HTML); print("wrote results.html",len(HTML))
