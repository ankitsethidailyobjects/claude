#!/usr/bin/env python3
import base64, pandas as pd, numpy as np
SEG="analysis/seg"
img=base64.b64encode(open(f"{SEG}/cohorts_chart.png","rb").read()).decode()
prod=pd.read_csv(f"{SEG}/named_profile_prod.csv",index_col=0)
dev=pd.read_csv(f"{SEG}/named_profile_dev.csv",index_col=0)
mp=pd.read_csv(f"{SEG}/prod_mapping.csv")
order=["Fast-Rising Newcomers","Established Omnivores","Prepaid Mid-Value Regulars",
       "Full-Price Value Seekers","Deal-Seekers & Returners","Wholesale / B2B"]
prod=prod.reindex([c for c in order if c in prod.index])
dev=dev.reindex([c for c in order if c in dev.index])
desc={
"Fast-Rising Newcomers":"Short tenure, high recent velocity, low discount — new customers ramping fast. Highest future retention.",
"Established Omnivores":"High frequency, broadest category range, mid-high AOV — the engaged core of the base.",
"Prepaid Mid-Value Regulars":"Multi-category, prepaid, mid value — steady dependable repeaters.",
"Full-Price Value Seekers":"Very low discount use, high COD, narrow category focus — buy what they want at full price.",
"Deal-Seekers & Returners":"Heavy discount reliance and high returns (negative net AOV) — low margin, lowest future retention.",
"Wholesale / B2B":"Rule-carved outliers: ~28 lifetime orders, ₹13.6k AOV, bulk baskets — handle via account management.",
}
crm={
"Fast-Rising Newcomers":"Accelerate to habit: welcome series, cross-sell adjacent categories, <b>full-price</b> — they don't need discounts.",
"Established Omnivores":"Protect &amp; expand: new-launch &amp; cross-category cross-sell; VIP care; suppress blanket discounts.",
"Prepaid Mid-Value Regulars":"Grow frequency: replenishment nudges, category expansion, modest prepaid incentives.",
"Full-Price Value Seekers":"Widen the basket (only ~2 categories); nudge COD→prepaid; <b>do not train on discounts</b>.",
"Deal-Seekers & Returners":"Margin-aware only: bundles over deep cuts, curb return abuse, low-cost win-back; don't overspend to retain.",
"Wholesale / B2B":"Account-based / manual; bulk &amp; GST workflows, dedicated rep.",
}
def rows_cohort():
    out=[]
    for c in prod.index:
        p=prod.loc[c]; d=dev.loc[c] if c in dev.index else None
        ret=f"{d['retained_365d']*100:.0f}%" if d is not None else "—"
        out.append(f"<tr><td><strong>{c}</strong><div class='muted'>{desc[c]}</div></td>"
          f"<td class='num'>{int(p['users']):,}</td><td class='num'>{p['pct']:.0f}%</td>"
          f"<td class='num'>{p['lifetime_orders']:.1f}</td><td class='num'>₹{p['aov']:,.0f}</td>"
          f"<td class='num'>{p['days_since_last']:.0f}d</td><td class='num'>{p['pct_discounted']*100:.0f}%</td>"
          f"<td class='num'>{p['n_categories']:.1f}</td><td class='num big'>{ret}</td></tr>")
    return "\n".join(out)
def dist(col):
    vc=mp[col].value_counts(); tot=len(mp)
    return " · ".join(f"<b>{k}</b> {100*v/tot:.0f}%" for k,v in vc.items())
def crm_rows():
    return "\n".join(f"<tr><td><strong>{c}</strong></td><td>{crm[c]}</td></tr>" for c in prod.index)

HTML=f"""<title>DailyObjects Behavioural Cohorts</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
:root{{--bg:#f6f7f9;--surface:#fff;--ink:#0f1b2d;--muted:#5b6b7f;--faint:#8a99ab;--line:#e4e8ee;--line2:#eef1f5;
--accent:#2563eb;--accent-soft:#eaf0fe;--green:#15803d;--green-soft:#e7f3ec;--amber:#c2560f;--amber-soft:#fdeee4;
--shadow:0 1px 2px rgba(15,27,45,.04),0 6px 22px rgba(15,27,45,.06);}}
@media(prefers-color-scheme:dark){{:root:not([data-theme="light"]){{--bg:#0b1220;--surface:#121b2b;--ink:#e8eef6;--muted:#9fb0c4;
--faint:#6b7d93;--line:#25324a;--line2:#1b2637;--accent:#6ea0ff;--accent-soft:#182741;--green:#57c98a;--green-soft:#13241a;
--amber:#ff8a4c;--amber-soft:#2a1d15;--shadow:0 1px 2px rgba(0,0,0,.3),0 8px 30px rgba(0,0,0,.35);}}}}
:root[data-theme="dark"]{{--bg:#0b1220;--surface:#121b2b;--ink:#e8eef6;--muted:#9fb0c4;--faint:#6b7d93;--line:#25324a;
--line2:#1b2637;--accent:#6ea0ff;--accent-soft:#182741;--green:#57c98a;--green-soft:#13241a;--amber:#ff8a4c;
--amber-soft:#2a1d15;--shadow:0 1px 2px rgba(0,0,0,.3),0 8px 30px rgba(0,0,0,.35);}}
*{{box-sizing:border-box}}
body{{margin:0;background:var(--bg);color:var(--ink);font-family:ui-sans-serif,system-ui,-apple-system,"Segoe UI",Roboto,sans-serif;line-height:1.6}}
.wrap{{max-width:1000px;margin:0 auto;padding:44px 22px 100px}}
.eyebrow{{font-family:ui-monospace,monospace;font-size:12px;letter-spacing:.14em;text-transform:uppercase;color:var(--accent);margin:0 0 10px}}
h1{{font-size:clamp(27px,4vw,38px);line-height:1.1;letter-spacing:-.02em;margin:0 0 12px;text-wrap:balance;font-weight:800}}
.sub{{font-size:17px;color:var(--muted);margin:0;max-width:72ch}}
h2{{font-size:13px;font-family:ui-monospace,monospace;letter-spacing:.1em;text-transform:uppercase;color:var(--accent);margin:0 0 6px}}
.sec-title{{font-size:22px;font-weight:800;letter-spacing:-.015em;margin:0 0 14px}}
section{{margin-top:44px}} section>hr{{border:none;border-top:2px solid var(--line);margin:0 0 18px}}
p{{margin:0 0 12px;max-width:82ch}} strong{{color:var(--ink)}}
.callout{{border-left:4px solid var(--accent);background:linear-gradient(90deg,var(--accent-soft),var(--surface) 62%);border-radius:0 12px 12px 0;padding:16px 20px;margin:16px 0}}
.callout.g{{border-color:var(--green);background:linear-gradient(90deg,var(--green-soft),var(--surface) 62%)}}
.callout.a{{border-color:var(--amber);background:linear-gradient(90deg,var(--amber-soft),var(--surface) 62%)}}
.kpis{{display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin:24px 0 0}}
@media(max-width:720px){{.kpis{{grid-template-columns:repeat(2,1fr)}}}}
.kpi{{background:var(--surface);border:1px solid var(--line);border-radius:12px;padding:15px}}
.kpi .n{{font-size:23px;font-weight:800;letter-spacing:-.02em;color:var(--accent);font-variant-numeric:tabular-nums}}
.kpi .l{{font-size:12.5px;color:var(--muted);margin-top:3px}}
.chartbox{{background:var(--surface);border:1px solid var(--line);border-radius:14px;padding:12px;box-shadow:var(--shadow);overflow-x:auto;margin:18px 0}}
.chartbox img{{width:100%;min-width:640px;height:auto;display:block;border-radius:6px}}
.tablebox{{overflow-x:auto;border:1px solid var(--line);border-radius:12px;background:var(--surface);box-shadow:var(--shadow);margin:14px 0}}
table{{border-collapse:collapse;width:100%;min-width:680px;font-size:13.5px}}
th,td{{text-align:left;padding:10px 13px;border-bottom:1px solid var(--line2);vertical-align:top}}
th.num,td.num{{text-align:right;font-variant-numeric:tabular-nums}}
thead th{{font-family:ui-monospace,monospace;font-size:10.5px;letter-spacing:.05em;text-transform:uppercase;color:var(--faint);background:var(--line2)}}
tbody tr:last-child td{{border-bottom:none}} td.big{{font-weight:750;color:var(--green)}}
.muted{{color:var(--faint);font-size:12px;margin-top:3px;font-weight:400;max-width:52ch}}
ul{{margin:0 0 12px;padding-left:0;list-style:none;max-width:84ch}}
ul li{{position:relative;padding-left:20px;margin:0 0 8px}} ul li::before{{content:"";position:absolute;left:2px;top:10px;width:6px;height:6px;border-radius:2px;background:var(--accent)}}
.chips{{display:flex;flex-wrap:wrap;gap:10px;margin:12px 0}}
.chip{{background:var(--surface);border:1px solid var(--line);border-radius:10px;padding:10px 14px;font-size:13px}}
.chip .t{{font-family:ui-monospace,monospace;font-size:10.5px;letter-spacing:.05em;text-transform:uppercase;color:var(--faint);display:block;margin-bottom:2px}}
code{{font-family:ui-monospace,monospace;font-size:.88em;background:var(--line2);padding:1px 5px;border-radius:5px}}
.foot{{margin-top:56px;padding-top:18px;border-top:1px solid var(--line);font-size:12px;color:var(--faint)}}
</style>
<div class="wrap">
<p class="eyebrow">DailyObjects · Behavioural segmentation · executed results (v1)</p>
<h1>Behavioural cohorts for the mature customer base</h1>
<p class="sub">K-Means segmentation of the 203,281 customers with 3+ lifetime orders (X=3), built on the full DMR 2020→Jul 2026, validated on a held-out year of future purchasing.</p>

<div class="kpis">
<div class="kpi"><div class="n">203,281</div><div class="l">mature customers mapped (3+ orders, as of 31 Jul 2026)</div></div>
<div class="kpi"><div class="n">5 + 1</div><div class="l">behavioural cohorts + rule-carved Wholesale/B2B</div></div>
<div class="kpi"><div class="n">18% → 47%</div><div class="l">future retention spread across cohorts (validated)</div></div>
<div class="kpi"><div class="n">1.44M</div><div class="l">identities resolved across email+phone+UUID</div></div>
</div>

<div class="callout g" style="margin-top:22px"><strong>Headline:</strong> Five durable behavioural identities emerge, and they separate cleanly on <em>future</em> retention even though recency was deliberately excluded from the identity — proof they capture real customer type, not just timing. <b>Fast-Rising Newcomers (47%)</b> and <b>Established Omnivores (38%)</b> are the growth engine; <b>Deal-Seekers &amp; Returners (18%)</b> are large but low-margin and least loyal.</div>

<!-- what was run -->
<section><hr><h2>What was executed</h2><p class="sec-title">Pipeline &amp; decisions</p>
<ul>
<li><strong>X = 3</strong> (per your call): Early lifecycle = 1–2 orders; <strong>Mature = 3+</strong> → 203,281 customers as of 31 Jul 2026.</li>
<li><strong>Data:</strong> full DMR Jan 2020 → Jul 2026 (25 files, 2.90M orders → 2.86M attributable). Identity resolved across email+phone+account-UUID with hub suppression → 1.44M customers.</li>
<li><strong>Features:</strong> leakage-safe as-of T₀; RFM + category + discount + channel + COD, all ≤ T₀.</li>
<li><strong>Model:</strong> K-Means (your call) on log-transformed, winsorized, scaled, PCA-whitened features; B2B/whales rule-carved first.</li>
<li><strong>Two variants run:</strong> a <em>recency-inclusive</em> k=6 (blends activity in; future retention 9→52%) and a <strong>recency-excluded "identity" k=5</strong> — we lead with the latter so the behavioural cohort is a <em>stable identity</em> and recency lives in the separate <strong>activity-state</strong> layer, exactly per the approved architecture.</li>
<li><strong>Validation:</strong> refit on a hold-out snapshot (T₀ = 31 Jul 2025) and measured the <em>next 12 months</em> of purchasing per cohort — no leakage.</li>
</ul>
</section>

<!-- cohort table -->
<section><hr><h2>The five cohorts</h2><p class="sec-title">Profiles &amp; validated future retention</p>
<div class="tablebox"><table>
<thead><tr><th>Cohort</th><th class="num">Users</th><th class="num">%</th><th class="num">Avg orders</th><th class="num">AOV</th><th class="num">Recency</th><th class="num">Disc %</th><th class="num">Categories</th><th class="num">Fwd 12-mo retention*</th></tr></thead>
<tbody>{rows_cohort()}</tbody>
</table></div>
<p class="muted">*Forward retention measured on the hold-out snapshot (customers as of 31 Jul 2025 → any purchase Aug 2025–Jul 2026). Production columns (users, %, recency) are as of 31 Jul 2026. AOV shown is median; Deal-Seekers' <em>mean</em> net AOV is negative due to returns.</p>
<div class="chartbox"><img alt="Left: forward retention by cohort 47/38/35/32/18%. Right: production cohort sizes." src="data:image/png;base64,{img}"></div>
</section>

<!-- dynamic layers -->
<section><hr><h2>Dynamic &amp; decision layers</h2><p class="sec-title">Overlaid on the stable cohort identity</p>
<div class="chips">
<div class="chip"><span class="t">Activity state (daily, from recency)</span>{dist('activity_state')}</div>
<div class="chip"><span class="t">Value tier (weekly, GMV percentile)</span>{dist('value_tier')}</div>
<div class="chip"><span class="t">Discount class (weekly)</span>{dist('discount_class')}</div>
</div>
<p>The base skews lapsed — <strong>~48% Dormant, 13% Active</strong> — because "mature" spans everyone with 3+ orders since 2020. This is exactly why <strong>activity state must be a separate dynamic layer</strong>: a Fast-Rising Newcomer who goes quiet becomes <em>Dormant</em> without losing their cohort identity, and re-engages the moment they buy.</p>
</section>

<!-- CRM -->
<section><hr><h2>CRM decisioning</h2><p class="sec-title">Cohort → recommended action</p>
<p>Final CRM segment = <code>Behavioural cohort × Activity state × Value tier × Discount class × Category affinity</code>. Base action by cohort:</p>
<div class="tablebox"><table>
<thead><tr><th>Cohort</th><th>Recommended CRM posture</th></tr></thead>
<tbody>{crm_rows()}</tbody>
</table></div>
<p>Activity overlay: <b>Active</b> → cross-sell / new launches · <b>Overdue</b> → gentle reorder nudge · <b>At-risk</b> → reactivation sized by value tier &amp; discount class · <b>Dormant</b> → win-back or sunset. High-value + full-price cohorts are <em>suppressed</em> from blanket discounts to protect margin.</p>
</section>

<!-- production -->
<section><hr><h2>Production &amp; MoEngage</h2><p class="sec-title">The mapping table &amp; how it activates</p>
<p>Output <code>prod_mapping.csv</code> — one row per mature customer with: <code>behavioural_cohort · activity_state · value_tier · discount_class · primary_category · recent_category</code> — is the exact publishable attribute set for MoEngage (per the approved blueprint: warehouse computes, MoEngage activates). Behavioural cohort re-scores monthly (hysteresis-guarded); activity state refreshes daily; K-Means centroids are versioned for stable re-scoring of new/updated users.</p>
<div class="callout a"><strong>Caveats (honest):</strong> silhouette is modest (~0.17) — cohorts grade into one another rather than being crisply separated (normal for behavioural RFM); the identity is validated by its <em>future-retention separation</em>, not geometry alone. Some orders carry negative <code>Product Grand Total(FF)</code> (returns/credit notes) → floored at 0 for clustering and flagged. The base is retention-lapsed by construction (3+ orders ever).</div>
</section>

<div class="foot">DailyObjects DMR 2020–Jul 2026 · 2.86M attributable orders · 1.44M identities · mature (3+) = 203,281 · K-Means stable-identity k=5 (+ recency-inclusive k=6 alt) · hold-out validation T₀=31 Jul 2025. Behavioural cohorts executed; awaiting go-ahead to wire warehouse tables &amp; MoEngage sync.</div>
</div>
"""
open(f"{SEG}/results.html","w").write(HTML)
print("wrote results.html",len(HTML))
