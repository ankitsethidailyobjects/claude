#!/usr/bin/env python3
import base64, pandas as pd, json

OUT="analysis/out"
img=base64.b64encode(open(f"{OUT}/retention_curve.png","rb").read()).decode()
paid=pd.read_csv(f"{OUT}/buckets_paid.csv")
con=pd.read_csv(f"{OUT}/buckets_paid_consolidated.csv")
deld=pd.read_csv(f"{OUT}/buckets_delivered_consolidated.csv")
summ=json.load(open(f"{OUT}/summary_paid.json"))
stab=json.load(open(f"{OUT}/stabilization.json"))

def rows_paid():
    out=[]
    for _,r in paid.head(13).iterrows():
        n=int(r.users); rel_=n>=300
        cls="" if rel_ else ' class="dim"'
        incr="—" if pd.isna(r.incr_pp) else f"{r.incr_pp:+.1f}"
        out.append(f"<tr{cls}><td>{int(r.orders)}</td><td>{n:,}</td><td>{int(r.retained):,}</td>"
                   f"<td class='big'>{r.retention_pct:.1f}%</td><td>{incr}</td><td>±{r.ci95_pp:.1f}</td></tr>")
    # 12+ consolidated row from con
    c=con[con.orders=='12+'].iloc[0]
    out.append(f"<tr class='cons'><td>12+</td><td>{int(c.users):,}</td><td>{int(c.retained):,}</td>"
               f"<td class='big'>{c.retention_pct:.1f}%</td><td>{c.incr_pp:+.1f}</td><td>—</td></tr>")
    return "\n".join(out)

def rows_deliv():
    out=[]
    for _,r in deld.iterrows():
        incr="—" if pd.isna(r.incr_pp) else f"{r.incr_pp:+.1f}"
        out.append(f"<tr><td>{r.orders}</td><td>{int(r.users):,}</td><td>{r.retention_pct:.1f}%</td><td>{incr}</td></tr>")
    return "\n".join(out)

HTML=f"""<title>Order Count &amp; Retention Stabilization</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
:root{{
  --bg:#f6f7f9; --surface:#ffffff; --ink:#0f1b2d; --muted:#5b6b7f; --faint:#8a99ab;
  --line:#e4e8ee; --line2:#eef1f5; --accent:#2563eb; --accent-soft:#eaf0fe;
  --amber:#ea580c; --green:#15803d; --amber-soft:#fdeee4; --green-soft:#e7f3ec;
  --shadow:0 1px 2px rgba(15,27,45,.04),0 6px 24px rgba(15,27,45,.06);
}}
@media (prefers-color-scheme:dark){{:root:not([data-theme="light"]){{
  --bg:#0b1220; --surface:#121b2b; --ink:#e8eef6; --muted:#9fb0c4; --faint:#6b7d93;
  --line:#25324a; --line2:#1b2637; --accent:#6ea0ff; --accent-soft:#182741;
  --amber:#ff8a4c; --green:#57c98a; --amber-soft:#2a1d15; --green-soft:#13241a;
  --shadow:0 1px 2px rgba(0,0,0,.3),0 8px 30px rgba(0,0,0,.35);
}}}}
:root[data-theme="dark"]{{
  --bg:#0b1220; --surface:#121b2b; --ink:#e8eef6; --muted:#9fb0c4; --faint:#6b7d93;
  --line:#25324a; --line2:#1b2637; --accent:#6ea0ff; --accent-soft:#182741;
  --amber:#ff8a4c; --green:#57c98a; --amber-soft:#2a1d15; --green-soft:#13241a;
  --shadow:0 1px 2px rgba(0,0,0,.3),0 8px 30px rgba(0,0,0,.35);
}}
*{{box-sizing:border-box}}
body{{margin:0;background:var(--bg);color:var(--ink);
  font-family:ui-sans-serif,system-ui,-apple-system,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;
  line-height:1.6;-webkit-font-smoothing:antialiased}}
.wrap{{max-width:940px;margin:0 auto;padding:48px 24px 96px}}
.mono{{font-family:ui-monospace,SFMono-Regular,"SF Mono",Menlo,Consolas,monospace}}
.eyebrow{{font-family:ui-monospace,monospace;font-size:12px;letter-spacing:.14em;text-transform:uppercase;color:var(--accent);margin:0 0 10px}}
h1{{font-size:clamp(28px,4.4vw,42px);line-height:1.1;letter-spacing:-.02em;margin:0 0 14px;text-wrap:balance;font-weight:800}}
.sub{{font-size:18px;color:var(--muted);margin:0 0 8px;max-width:64ch}}
h2{{font-size:13px;font-family:ui-monospace,monospace;letter-spacing:.12em;text-transform:uppercase;color:var(--faint);
  margin:0 0 18px;padding-bottom:10px;border-bottom:1px solid var(--line)}}
h3{{font-size:19px;letter-spacing:-.01em;margin:26px 0 8px;font-weight:700}}
section{{margin-top:52px}}
p{{margin:0 0 14px;max-width:70ch}}
.lead b,strong{{color:var(--ink)}}
.card{{background:var(--surface);border:1px solid var(--line);border-radius:14px;padding:22px 24px;box-shadow:var(--shadow)}}
.answer{{border-left:4px solid var(--accent);background:linear-gradient(90deg,var(--accent-soft),var(--surface) 60%)}}
.answer .q{{font-family:ui-monospace,monospace;font-size:12px;letter-spacing:.06em;color:var(--muted);margin-bottom:6px}}
.answer .a{{font-size:22px;font-weight:750;letter-spacing:-.01em;line-height:1.32;text-wrap:balance}}
.answer .a em{{font-style:normal;color:var(--accent)}}
.kpis{{display:grid;grid-template-columns:repeat(4,1fr);gap:14px;margin:26px 0 0}}
@media(max-width:680px){{.kpis{{grid-template-columns:repeat(2,1fr)}}}}
.kpi{{background:var(--surface);border:1px solid var(--line);border-radius:12px;padding:16px 16px 14px}}
.kpi .n{{font-size:26px;font-weight:800;letter-spacing:-.02em;font-variant-numeric:tabular-nums}}
.kpi .l{{font-size:12.5px;color:var(--muted);margin-top:3px;line-height:1.35}}
.kpi.b .n{{color:var(--accent)}} .kpi.o .n{{color:var(--amber)}} .kpi.g .n{{color:var(--green)}}
figure{{margin:22px 0 0}}
.chartbox{{background:var(--surface);border:1px solid var(--line);border-radius:14px;padding:14px;box-shadow:var(--shadow);overflow-x:auto}}
.chartbox img{{width:100%;min-width:640px;height:auto;display:block;border-radius:6px}}
figcaption{{font-size:13px;color:var(--muted);margin-top:10px}}
.tablebox{{overflow-x:auto;border:1px solid var(--line);border-radius:12px;background:var(--surface);box-shadow:var(--shadow)}}
table{{border-collapse:collapse;width:100%;min-width:520px;font-variant-numeric:tabular-nums}}
th,td{{text-align:right;padding:10px 16px;font-size:14.5px;border-bottom:1px solid var(--line2)}}
th:first-child,td:first-child{{text-align:left}}
thead th{{font-family:ui-monospace,monospace;font-size:11.5px;letter-spacing:.06em;text-transform:uppercase;color:var(--faint);background:var(--line2)}}
tbody tr:last-child td{{border-bottom:none}}
td.big{{font-weight:750;color:var(--accent)}}
tr.dim td{{color:var(--faint)}} tr.dim td.big{{color:var(--faint)}}
tr.cons td{{border-top:2px solid var(--line);font-style:normal;background:var(--line2)}}
ul{{margin:0 0 14px;padding-left:0;list-style:none;max-width:72ch}}
ul li{{position:relative;padding-left:22px;margin:0 0 10px}}
ul li::before{{content:"";position:absolute;left:2px;top:11px;width:7px;height:7px;border-radius:2px;background:var(--accent)}}
ol{{max-width:72ch;padding-left:20px}} ol li{{margin:0 0 12px}}
.tag{{display:inline-block;font-family:ui-monospace,monospace;font-size:11px;padding:2px 8px;border-radius:6px;background:var(--accent-soft);color:var(--accent);letter-spacing:.03em}}
.note{{font-size:13.5px;color:var(--muted);border-left:3px solid var(--line);padding:2px 0 2px 16px;margin:16px 0}}
.dq{{display:grid;grid-template-columns:1fr 1fr;gap:12px}}
@media(max-width:680px){{.dq{{grid-template-columns:1fr}}}}
.dq .item{{background:var(--surface);border:1px solid var(--line);border-radius:10px;padding:13px 15px;font-size:14px}}
.dq .item b{{display:block;font-size:12.5px;color:var(--amber);font-family:ui-monospace,monospace;letter-spacing:.03em;margin-bottom:3px}}
.foot{{margin-top:64px;padding-top:20px;border-top:1px solid var(--line);font-size:12.5px;color:var(--faint)}}
hr.rule{{border:none;border-top:1px solid var(--line);margin:0}}
</style>

<div class="wrap">
<p class="eyebrow">DailyObjects · Platform retention analysis · DMR 2020–2025</p>
<h1>When does a customer become a repeat customer?</h1>
<p class="sub">2025 retention measured against every customer's lifetime order count as of 31 December 2024, across 2.43&nbsp;million orders and 926,863 customers.</p>

<div class="card answer" style="margin-top:26px">
  <div class="q">THE QUESTION → “Once a customer has made X orders, does their likelihood of returning become stable — and what is X?”</div>
  <div class="a">Retention climbs steeply and monotonically with every early order, then bends into diminishing returns at roughly <em>7 lifetime orders</em> (~48% retention). It keeps drifting up to a soft plateau of <em>~60–66%</em> by 10–12 orders — there is no razor-sharp flattening, but the big gains are essentially banked by the 7th order.</div>
</div>

<div class="kpis">
  <div class="kpi"><div class="n">926,863</div><div class="l">customers in the Dec-2024 cohort (≥1 paid order)</div></div>
  <div class="kpi b"><div class="n">8.3% → 66%</div><div class="l">retention from 1 → 12 lifetime orders</div></div>
  <div class="kpi o"><div class="n">≈ 7</div><div class="l">diminishing-returns elbow (max curvature)</div></div>
  <div class="kpi g"><div class="n">+9.2 pp</div><div class="l">biggest single jump: the 1st → 2nd order</div></div>
</div>

<!-- A -->
<section>
<h2>A · Data quality &amp; methodology</h2>
<p><b>Data.</b> DailyObjects Daily-MIS-Report (DMR) order exports covering <b>Jan 2020 → Dec 2025</b> — five annual workbooks (2020–2024) plus twelve monthly files for 2025 (17 files, ~1.8&nbsp;GB), pulled from Google Drive. Each file is at <b>SKU/order-line grain</b> (one row per item), so an order spanning several products appears as several rows.</p>
<p><b>Order identifier &amp; de-duplication.</b> Orders are counted by unique <span class="tag">Order No.</span>, never by rows or SKUs. After collapsing lines to orders and de-duplicating globally, the dataset holds <b>2,434,191 unique orders</b>.</p>
<p><b>Customer identifier — resolved, not naïve.</b> Email alone is unreliable here: the 2024 file masks <b>27% of emails</b> to the literal string <span class="mono">“userEmail”</span>, and 2020–21 use <span class="mono">“na”</span> for missing emails. Every masked 2024 row, however, still carries a stable <b>account UUID</b> and <b>mobile number</b>. Customers are therefore resolved by linking <b>email + mobile + account-UUID</b> (union-find). Shared “hub” identifiers — e.g. a COD/call-centre phone appearing across thousands of guest orders — are suppressed before linking (1,998 removed) so they can't merge unrelated people. This yields <b>1,245,335 distinct customers</b>.</p>
<p><b>What counts as an order (primary = “paid”).</b> An order is valid if at least one line reached a paid state; <b>abandoned/failed checkouts</b> (<span class="mono">paymentPending</span>, <span class="mono">paymentFailed</span>) are excluded. Cancellations, refunds, RTO and returns <em>were</em> paid, so they stay in. A stricter <b>“delivered/fulfilled”</b> definition is shown as a sensitivity check in §D — it barely moves the shape.</p>
<p><b>Exclusions.</b> Internal <span class="mono">@dailyobjects.com</span> staff/test accounts, the <span class="mono">dummy@cred.club</span> integration bucket, and <b>42,139 orders (1.7%)</b> with no usable identifier.</p>
<p><b>Cohort frozen at 31 Dec 2024.</b> Each customer's bucket = their <b>lifetime paid orders from 2020 through 31 Dec 2024</b>. 2025 orders never change the bucket — they only decide the binary <b>retained / not-retained</b> flag (≥1 purchase anywhere in 2025). Customers whose first-ever order fell in 2025 (262,772) have no pre-2025 history and are correctly excluded from the cohort.</p>
<div class="dq" style="margin-top:18px">
  <div class="item"><b>SKU-line inflation</b>Feb-25 alone: 52,981 lines → 37,426 orders. Counted as orders.</div>
  <div class="item"><b>Email masking (2024)</b>133k orders "userEmail" — recovered via UUID/phone, not dropped.</div>
  <div class="item"><b>Layout drift</b>Column names &amp; sheet names differ every year (Order No. vs Order_No_, hidden pivot sheets) — auto-detected.</div>
  <div class="item"><b>Over-merge guard</b>Before suppression, one phone chained 14,320 emails into a single fake "customer" — fixed.</div>
</div>
</section>

<!-- B -->
<section>
<h2>B · Bucket-level retention table</h2>
<p>Lifetime paid orders as of 31 Dec 2024 vs. share of those customers who bought again in 2025. Grey rows have fewer than 300 customers and are statistically thin; the <b>12+</b> row consolidates the whole sparse tail.</p>
<div class="tablebox">
<table>
<thead><tr><th>Lifetime orders</th><th>Customers</th><th>Retained 2025</th><th>Retention %</th><th>Δ vs prev (pp)</th><th>95% CI</th></tr></thead>
<tbody>
{rows_paid()}
</tbody>
</table>
</div>
<p class="note">Confidence intervals are Wilson 95%. Buckets 1–8 each have thousands of customers (CI ≤ ±2pp) — the curve's shape there is not noise. Precision decays past ~13 orders.</p>
</section>

<!-- C -->
<section>
<h2>C · Retention curve</h2>
<figure>
<div class="chartbox"><img alt="Retention rises from 8% at 1 lifetime order to ~66% at 12, bending at ~7 orders; lower panel shows per-order incremental gains shrinking from +9pp to ~3pp." src="data:image/png;base64,{img}"></div>
<figcaption><b>Top:</b> 2025 retention by lifetime-order bucket with 95% CIs (blue = statistically reliable, grey dashed = sparse tail); grey bars are customers per bucket on a log scale. <b>Bottom:</b> incremental retention gained from each additional order — the deceleration is the whole story.</figcaption>
</figure>
</section>

<!-- D -->
<section>
<h2>D · Stabilization analysis</h2>
<h3>Where the curve bends</h3>
<p>The relationship is <b>monotonic and strongly concave</b>. The gains are front-loaded:</p>
<ul>
<li>The <b>1st → 2nd order</b> is the single largest lever: retention <b>more than doubles</b>, 8.3% → 17.5% (<b>+9.2pp</b>).</li>
<li>By the <b>4th order</b> retention has <b>quadrupled</b> to 31.8%; orders 2–4 each add 6–9pp.</li>
<li>Marginal gain then <b>roughly halves</b>: orders 5–7 add ~5pp each, and from the 8th order onward increments fall to a noisy ~1–5pp.</li>
</ul>
<h3>Quantitative stabilization point</h3>
<ul>
<li><b>Curvature elbow (Kneedle): {stab['elbow_orders']} orders</b> — the objective point of maximum bend, at ~48% retention.</li>
<li>Retention reaches <b>80%</b> of its reliable-range plateau by <b>{stab['reach80_ceiling']} orders</b> and <b>90%</b> by <b>{stab['reach90_ceiling']} orders</b>.</li>
<li>Plateau level within reliable data ≈ <b>{stab['ceiling_pct']:.0f}%</b> (10+ orders), edging toward ~70% in the thin tail.</li>
</ul>
<p><b>Honest verdict:</b> stabilization is <b>soft, not sharp</b>. Additional orders keep adding a few points even at 10–12, so the curve never becomes truly flat inside the statistically reliable range — but the <b>economically meaningful</b> gains are banked by the <b>~7th order</b>, after which each extra order moves the needle far less than the first few did.</p>
<h3>Sensitivity — “delivered/fulfilled” definition</h3>
<p>Restricting to orders with a fulfilled line reproduces the same curve and the same elbow (~7), confirming the pattern isn't an artifact of how cancellations are treated:</p>
<div class="tablebox" style="max-width:560px">
<table>
<thead><tr><th>Lifetime orders</th><th>Customers</th><th>Retention %</th><th>Δ (pp)</th></tr></thead>
<tbody>
{rows_deliv()}
</tbody>
</table>
</div>
</section>

<!-- E -->
<section>
<h2>E · Executive takeaway</h2>
<ol>
<li><b>Retention improves dramatically with lifetime orders.</b> A one-time buyer has an <b>8%</b> chance of returning in 2025; a 12-order customer, <b>66%</b> — an 8× spread driven almost entirely by the first several orders.</li>
<li><b>The stabilization threshold is ≈ 7 lifetime orders.</b> That's the objective curvature elbow; by then ~80% of the achievable retention lift is already captured.</li>
<li><b>Post-stabilization retention ≈ 50% at the elbow, settling ~60–66%</b> for customers with 10–12+ orders.</li>
<li><b>Analytically convincing for the shape, with an honest caveat.</b> Buckets 1–8 hold thousands of customers with tight CIs, so the steep early curve is real. The "plateau," though, is a <b>gentle deceleration</b>, not a hard ceiling — improvement continues slowly beyond order 7.</li>
<li><b>Low-sample caveat at the top.</b> Beyond ~13 orders each bucket has &lt;300 customers, CIs widen to ±5–10pp, and the tail is noisy — hence the consolidated <b>12+</b> view. ~262k customers whose first order was in 2025 are excluded by design.</li>
</ol>
<div class="card" style="margin-top:22px;border-left:4px solid var(--green);background:linear-gradient(90deg,var(--green-soft),var(--surface) 60%)">
<p style="margin:0"><b>So what?</b> The retention flywheel is won early. The highest-leverage CRM/lifecycle goal is pushing new buyers toward their <b>2nd, 3rd and 4th purchase</b> — where each order buys 6–9pp of future retention — and getting customers to the <b>~7-order</b> mark, past which loyalty is largely self-sustaining. Converting the very first repeat order (1→2) is the single biggest win available.</p>
</div>
</section>

<div class="foot">
Source: DailyObjects DMR order-line exports, Jan 2020 – Dec 2025 · 2,434,191 unique orders · 1,993,897 valid paid attributable orders · cohort 926,863 customers · retention window: full calendar 2025 · primary order definition: paid (excl. payment-pending/failed) · customer identity resolved across email + mobile + account-UUID with hub suppression.
</div>
</div>
"""
open(f"{OUT}/report.html","w").write(HTML)
print("wrote", f"{OUT}/report.html", len(HTML), "bytes; img b64", len(img))
