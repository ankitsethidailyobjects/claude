#!/usr/bin/env python3
import base64, pandas as pd, numpy as np
SEG="analysis/seg"
img=base64.b64encode(open(f"{SEG}/cohorts_chart.png","rb").read()).decode()
prod=pd.read_csv(f"{SEG}/cohort_profile_prod_v2.csv",index_col=0)
dev=pd.read_csv(f"{SEG}/cohort_profile_dev_v2.csv",index_col=0)
mp=pd.read_csv(f"{SEG}/prod_mapping_v2.csv")
slabs=pd.read_csv(f"{SEG}/slabs_v2.csv")
order=["Power Users","Core Regulars","Full-Price Loyalists","Light Users","Deal Seekers","Wholesale / B2B"]
prod=prod.reindex([c for c in order if c in prod.index]); dev=dev.reindex([c for c in order if c in dev.index])
rule={
"Power Users":"6+ lifetime orders &amp; not discount-dependent (&lt;65% orders discounted)",
"Core Regulars":"4–5 orders, balanced discount use",
"Full-Price Loyalists":"≤20% of orders discounted — buy at full price",
"Light Users":"exactly 3 orders, balanced discount",
"Deal Seekers":"≥65% of orders on discount — promo-dependent",
"Wholesale / B2B":"≥50 orders or ≥10 units/order (rule-carved)",
}
crm={
"Power Users":"<b>Protect &amp; grow.</b> VIP care, early access to launches, full-price cross-sell — especially introduce Designer/Bags to the (mostly Tech) base. Never discount reflexively.",
"Core Regulars":"<b>Increase frequency.</b> Replenishment nudges + category expansion; targeted, not blanket, offers.",
"Full-Price Loyalists":"<b>Do not train on discounts.</b> Widen the basket (only ~2.5 categories), nudge COD→prepaid, cross-sell.",
"Light Users":"<b>Drive the 4th order.</b> Onboarding-style journeys, best-sellers, one modest incentive to build the habit.",
"Deal Seekers":"<b>Margin-aware only.</b> Bundles over deep cuts, wean off discounts; 75% are Dormant → low-cost win-back, sunset the unresponsive. Don't overspend to retain.",
"Wholesale / B2B":"Account-managed; bulk / GST workflows, dedicated rep.",
}
def rows_cohort():
    out=[]
    for c in prod.index:
        p=prod.loc[c]; ret=f"{dev.loc[c,'retained_365d']*100:.0f}%" if c in dev.index else "—"
        out.append(f"<tr><td><strong>{c}</strong><div class='muted'>{rule[c]}</div></td>"
          f"<td class='num'>{int(p['users']):,}</td><td class='num'>{p['pct']:.0f}%</td>"
          f"<td class='num'>{p['avg_orders']:.1f}</td><td class='num'>₹{p['med_gmv']:,.0f}</td>"
          f"<td class='num'>{p['pct_discounted']*100:.0f}%</td><td class='num'>{p['med_recency']:.0f}d</td>"
          f"<td class='num big'>{ret}</td></tr>")
    return "\n".join(out)
def dist(col):
    vc=mp[col].value_counts(); tot=len(mp)
    return " · ".join(f"<b>{k}</b> {100*v/tot:.0f}%" for k,v in vc.items())
aff=pd.crosstab(mp["behavioural_cohort"],mp["cat_affinity"]).reindex([c for c in order if c in mp['behavioural_cohort'].unique()])
def aff_rows():
    out=[]
    for c in aff.index:
        r=aff.loc[c]; tot=r.sum()
        out.append(f"<tr><td>{c}</td><td class='num'>{100*r.get('Tech',0)/tot:.0f}%</td>"
                   f"<td class='num'>{100*r.get('Mixed',0)/tot:.0f}%</td><td class='num'>{100*r.get('Designer/Bags',0)/tot:.0f}%</td></tr>")
    return "\n".join(out)

HTML=f"""<title>DailyObjects Customer Cohorts</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
:root{{--bg:#f6f7f9;--surface:#fff;--ink:#0f1b2d;--muted:#5b6b7f;--faint:#8a99ab;--line:#e4e8ee;--line2:#eef1f5;
--accent:#2563eb;--accent-soft:#eaf0fe;--green:#15803d;--green-soft:#e7f3ec;--amber:#c2560f;--amber-soft:#fdeee4;--shadow:0 1px 2px rgba(15,27,45,.04),0 6px 22px rgba(15,27,45,.06);}}
@media(prefers-color-scheme:dark){{:root:not([data-theme="light"]){{--bg:#0b1220;--surface:#121b2b;--ink:#e8eef6;--muted:#9fb0c4;--faint:#6b7d93;--line:#25324a;--line2:#1b2637;--accent:#6ea0ff;--accent-soft:#182741;--green:#57c98a;--green-soft:#13241a;--amber:#ff8a4c;--amber-soft:#2a1d15;--shadow:0 1px 2px rgba(0,0,0,.3),0 8px 30px rgba(0,0,0,.35);}}}}
:root[data-theme="dark"]{{--bg:#0b1220;--surface:#121b2b;--ink:#e8eef6;--muted:#9fb0c4;--faint:#6b7d93;--line:#25324a;--line2:#1b2637;--accent:#6ea0ff;--accent-soft:#182741;--green:#57c98a;--green-soft:#13241a;--amber:#ff8a4c;--amber-soft:#2a1d15;--shadow:0 1px 2px rgba(0,0,0,.3),0 8px 30px rgba(0,0,0,.35);}}
*{{box-sizing:border-box}} body{{margin:0;background:var(--bg);color:var(--ink);font-family:ui-sans-serif,system-ui,-apple-system,"Segoe UI",Roboto,sans-serif;line-height:1.6}}
.wrap{{max-width:1000px;margin:0 auto;padding:44px 22px 100px}}
.eyebrow{{font-family:ui-monospace,monospace;font-size:12px;letter-spacing:.14em;text-transform:uppercase;color:var(--accent);margin:0 0 10px}}
h1{{font-size:clamp(27px,4vw,38px);line-height:1.1;letter-spacing:-.02em;margin:0 0 12px;text-wrap:balance;font-weight:800}}
.sub{{font-size:17px;color:var(--muted);margin:0;max-width:74ch}}
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
.chartbox{{background:var(--surface);border:1px solid var(--line);border-radius:14px;padding:12px;box-shadow:var(--shadow);overflow-x:auto;margin:18px 0}}
.chartbox img{{width:100%;min-width:720px;height:auto;display:block;border-radius:6px}}
.tablebox{{overflow-x:auto;border:1px solid var(--line);border-radius:12px;background:var(--surface);box-shadow:var(--shadow);margin:14px 0}}
table{{border-collapse:collapse;width:100%;min-width:640px;font-size:13.5px}}
th,td{{text-align:left;padding:10px 13px;border-bottom:1px solid var(--line2);vertical-align:top}}
th.num,td.num{{text-align:right;font-variant-numeric:tabular-nums}}
thead th{{font-family:ui-monospace,monospace;font-size:10.5px;letter-spacing:.05em;text-transform:uppercase;color:var(--faint);background:var(--line2)}}
tbody tr:last-child td{{border-bottom:none}} td.big{{font-weight:750;color:var(--green)}}
.muted{{color:var(--faint);font-size:12px;margin-top:3px;font-weight:400;max-width:60ch}}
.chips{{display:flex;flex-wrap:wrap;gap:10px;margin:12px 0}}
.chip{{background:var(--surface);border:1px solid var(--line);border-radius:10px;padding:10px 14px;font-size:13px}}
.chip .t{{font-family:ui-monospace,monospace;font-size:10.5px;letter-spacing:.05em;text-transform:uppercase;color:var(--faint);display:block;margin-bottom:2px}}
.flow{{display:flex;flex-wrap:wrap;align-items:center;gap:8px;font-size:13px;margin:10px 0 4px}}
.flow .b{{background:var(--accent-soft);color:var(--accent);border-radius:8px;padding:6px 11px;font-weight:650}}
.flow .l{{background:var(--amber-soft);color:var(--amber);border-radius:8px;padding:6px 11px}}
.flow .s{{color:var(--faint)}}
code{{font-family:ui-monospace,monospace;font-size:.88em;background:var(--line2);padding:1px 5px;border-radius:5px}}
.foot{{margin-top:56px;padding-top:18px;border-top:1px solid var(--line);font-size:12px;color:var(--faint)}}
</style>
<div class="wrap">
<p class="eyebrow">DailyObjects · Customer cohort system · v2 (actionable)</p>
<h1>Customer cohorts: Power Users to Deal Seekers</h1>
<p class="sub">Full base 2020 → Jul 2026. Lifecycle slabs for everyone; five actionable behavioural cohorts for the 3+ order base; category-affinity and activity states layered on top.</p>

<div class="flow">
<span class="b">User</span><span class="s">→</span><span class="b">Lifecycle slab (1 / 2 / 3+)</span><span class="s">→</span>
<span class="b">Behavioural cohort</span><span class="s">→</span><span class="l">Category affinity</span><span class="s">+</span>
<span class="l">Activity state</span><span class="s">+</span><span class="l">Value tier</span><span class="s">→</span><span class="b">CRM action</span>
</div>

<div class="kpis">
<div class="kpi"><div class="n">1.38M</div><div class="l">customers; 203,281 mature (3+ orders)</div></div>
<div class="kpi"><div class="n">5 tiers</div><div class="l">Power · Core · Full-Price · Light · Deal (+B2B)</div></div>
<div class="kpi"><div class="n">25% → 53%</div><div class="l">future retention, Deal Seekers → Power Users</div></div>
<div class="kpi"><div class="n">74% Tech</div><div class="l">affinity vs 8% Designer/Bags → cross-sell gap</div></div>
</div>

<section><hr><h2>Layer 1</h2><p class="sec-title">Lifecycle slabs — the whole base (31 Jul 2026)</p>
<p>Threshold confirmed as <strong>≥ 3 orders (3-and-more, inclusive)</strong> — not "more than 3". Deterministic and updates on every order.</p>
<div class="tablebox"><table><thead><tr><th>Lifecycle slab</th><th class="num">Customers</th><th class="num">% of base</th><th>Treatment</th></tr></thead><tbody>
<tr><td><strong>Order 1</strong> (exactly 1)</td><td class="num">{int(slabs.iloc[0].users):,}</td><td class="num">68.6%</td><td>Rule-based: drive the 2nd order (biggest retention jump)</td></tr>
<tr><td><strong>Order 2</strong> (exactly 2)</td><td class="num">{int(slabs.iloc[1].users):,}</td><td class="num">16.7%</td><td>Rule-based: drive the 3rd order</td></tr>
<tr><td><strong>Order 3+</strong> (mature)</td><td class="num">{int(slabs.iloc[2].users):,}</td><td class="num">14.8%</td><td><strong>Enters behavioural cohorting ↓</strong></td></tr>
</tbody></table></div></section>

<section><hr><h2>Layer 2</h2><p class="sec-title">Five behavioural cohorts (mature 3+)</p>
<p>Transparent, rule-based tiers (validated against the ML structure and on hold-out retention) — each has a one-line definition a marketer can reason about.</p>
<div class="tablebox"><table>
<thead><tr><th>Cohort</th><th class="num">Users</th><th class="num">%</th><th class="num">Avg orders</th><th class="num">Med GMV</th><th class="num">Disc%</th><th class="num">Recency</th><th class="num">Fwd retention*</th></tr></thead>
<tbody>{rows_cohort()}</tbody></table></div>
<p class="muted">*Forward 12-month retention on the hold-out snapshot (mature as of 31 Jul 2025 → any purchase in the next 12 months). Cohorts separate 25%→53% — validated.</p>
<div class="chartbox"><img alt="Cohort retention, sizes, and activity split" src="data:image/png;base64,{img}"></div>
<div class="callout a"><strong>Biggest finding:</strong> <b>Deal Seekers are the largest cohort (29%)</b> — 82% of their orders are discounted, median recency 714 days, and <b>75% are Dormant</b>. They have the <em>lowest</em> future retention (25%). A third of the "mature" base is a low-margin, largely-lapsed promo audience — a clear signal to stop over-discounting and shift spend toward Power/Core growth.</div>
</section>

<section><hr><h2>Layer 3a</h2><p class="sec-title">Category affinity overlay — Tech vs Designer/Bags</p>
<p>Macro affinity from spend share (Tech ≥70% → Tech; ≤30% → Designer/Bags; else Mixed). Top-level today; <strong>sub-category affinity is the planned next iteration.</strong></p>
<div class="chips"><div class="chip"><span class="t">Base affinity</span>{dist('cat_affinity')}</div></div>
<div class="tablebox"><table><thead><tr><th>Cohort</th><th class="num">Tech</th><th class="num">Mixed</th><th class="num">Designer/Bags</th></tr></thead><tbody>{aff_rows()}</tbody></table></div>
<p>The base is overwhelmingly <strong>Tech (74%)</strong>; only <strong>8% skew Designer/Bags</strong>. Since bags carry higher AOV, the <em>Tech-heavy Power &amp; Core cohorts are the prime cross-sell pool into Designer/Bags</em>. Affinity is a personalization layer — it selects <em>content/offer</em>, it does not change the cohort.</p></section>

<section><hr><h2>Layer 3b</h2><p class="sec-title">Activity overlay — Active / Lapsed / Dormant</p>
<p>A <strong>rule layer on top of every cohort</strong> (not a separate cohort): <b>Active</b> ≤90d since last order · <b>Lapsed</b> 90–270d · <b>Dormant</b> &gt;270d. A Power User who goes quiet becomes <em>Power User · Dormant</em> — same identity, different play.</p>
<div class="chips"><div class="chip"><span class="t">Base activity</span>{dist('activity_state')}</div></div>
<p>The mature base is <strong>59% Dormant / 27% Lapsed / 13% Active</strong> (it spans everyone with 3+ orders since 2020). Activity varies sharply by cohort — Power Users are 22% Active, Deal Seekers only 9% (75% Dormant) — see the third chart panel.</p></section>

<section><hr><h2>Layer 4</h2><p class="sec-title">CRM decisioning</p>
<p>Segment = <code>Cohort × Activity × Affinity × Value tier</code>. Base action by cohort:</p>
<div class="tablebox"><table><thead><tr><th>Cohort</th><th>Recommended CRM posture</th></tr></thead><tbody>
{"".join(f"<tr><td><strong>{c}</strong></td><td>{crm[c]}</td></tr>" for c in prod.index)}
</tbody></table></div>
<p><strong>Activity overlay:</strong> Active → cross-sell &amp; new launches · Lapsed → reorder reminder + reactivation (offer strength scaled by cohort &amp; value tier) · Dormant → win-back or sunset. <strong>Affinity overlay:</strong> picks the creative — Tech vs Designer/Bags, soon at sub-category level. <em>Example:</em> Power User · Lapsed · Tech-affinity → "your next upgrade" win-back on new tech launches at full price; Deal Seeker · Dormant → single low-cost bundle, then sunset.</p></section>

<section><hr><h2>Production</h2><p class="sec-title">Mapping &amp; MoEngage</p>
<p><code>prod_mapping_v2.csv</code> — one row per mature customer: <code>behavioural_cohort · activity_state · cat_affinity · value_tier · primary/recent category</code> — the publishable MoEngage attribute set. Cohort re-scores monthly (hysteresis); activity daily; affinity on order. Warehouse computes, MoEngage activates.</p>
<div class="callout a"><strong>Data-quality flags:</strong> category taxonomy differs across years and some labels (e.g. "Designer Cases") carry large negative GMV (returns/sign) — affinity uses keyword-mapped macros with GMV floored at 0. Cohort thresholds (6+ for Power, 65%/20% discount cuts) are transparent config and tunable.</div></section>

<div class="foot">DailyObjects DMR 2020–Jul 2026 · 2.86M attributable orders · 1.44M identities · mature (≥3) = 203,281 · rule-based cohorts validated on hold-out T₀=31 Jul 2025 forward retention · category affinity Tech vs Designer/Bags (sub-category next). v2 — actionable redo.</div>
</div>
"""
open(f"{SEG}/results.html","w").write(HTML); print("wrote results.html",len(HTML))
