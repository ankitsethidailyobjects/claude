#!/usr/bin/env python3
from docx import Document
from docx.shared import Pt, RGBColor, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
SEG="analysis/seg"; OUT=f"{SEG}/DailyObjects_Retention_Strategy.docx"
BLUE=RGBColor(0x1e,0x40,0xaf); INK=RGBColor(0x0f,0x1b,0x2d); GREY=RGBColor(0x5b,0x6b,0x7f)
AMBER=RGBColor(0xc2,0x56,0x0f); GREEN=RGBColor(0x15,0x80,0x3d)
d=Document()
st=d.styles["Normal"]; st.font.name="Calibri"; st.font.size=Pt(10.5); st.font.color.rgb=INK
def H(txt,size=15,color=BLUE,after=6,before=12,bold=True):
    p=d.add_paragraph();p.space_after=Pt(after);p.space_before=Pt(before)
    r=p.add_run(txt);r.bold=bold;r.font.size=Pt(size);r.font.color.rgb=color;return p
def para(txt,size=10.5,color=INK,bold=False,after=6):
    p=d.add_paragraph();p.space_after=Pt(after)
    r=p.add_run(txt);r.font.size=Pt(size);r.bold=bold;r.font.color.rgb=color;return p
def bullet(txt,bold_lead=None):
    p=d.add_paragraph(style="List Bullet");p.space_after=Pt(3)
    if bold_lead:
        r=p.add_run(bold_lead+" ");r.bold=True
    p.add_run(txt);return p
def table(headers,rows,widths=None):
    t=d.add_table(rows=1,cols=len(headers));t.style="Light Grid Accent 1"
    for i,h in enumerate(headers):
        c=t.rows[0].cells[i];c.text="";r=c.paragraphs[0].add_run(h);r.bold=True;r.font.size=Pt(9);r.font.color.rgb=RGBColor(255,255,255)
    for row in rows:
        cells=t.add_row().cells
        for i,v in enumerate(row):
            cells[i].text="";rr=cells[i].paragraphs[0].add_run(str(v));rr.font.size=Pt(9)
    if widths:
        for row in t.rows:
            for i,w in enumerate(widths): row.cells[i].width=Inches(w)
    d.add_paragraph().space_after=Pt(2)
    return t

# ---- title ----
p=d.add_paragraph();p.alignment=WD_ALIGN_PARAGRAPH.LEFT
r=p.add_run("DailyObjects — Customer Retention Strategy");r.bold=True;r.font.size=Pt(22);r.font.color.rgb=INK
sub=d.add_paragraph();rr=sub.add_run("Built on cohort & category-affinity modelling of the full DMR, 2020–Jul 2026");rr.italic=True;rr.font.size=Pt(11);rr.font.color.rgb=GREY
d.add_paragraph()

H("1. Executive summary",16)
para("We resolved 1.38M unique customers across 2.86M orders (2020–Jul 2026), enriched the discount signal to include price-led event drops (HPS, Diwali, etc.) that the DMR hides, and segmented the 203,281 customers with 3+ orders into three behavioural cohorts — Power Users, Deal Seekers, Light Users — with category and sub-category affinity layered on. Retention was measured at monthly, quarterly and yearly grain.")
para("The headline: DailyObjects has a severe leaky bucket at the top of the funnel and an over-dependence on discount events for repeat purchase. 68.6% of customers are one-time buyers and only 8.5% of them return within a year. Repeat behaviour is heavily concentrated around sale events. The single highest-leverage opportunity is converting the 1st order into a 2nd, and moving customers to the ~3-order mark where loyalty compounds (Power Users retain at 48% p.a.).",bold=False)

H("2. What we built",16)
bullet("resolved customer identity across email + phone + account-UUID (fixes 2024 email masking).","Identity —")
bullet("added price-led event discounts detected from weekly ASP dips; discount penetration rises from 21% (coupon-only) to 49% of orders.","Enriched discounts —")
bullet("3 behavioural cohorts on all 3+ order customers (K-Means), validated on held-out future retention.","Cohorts —")
bullet("Tech vs Designer/Bags scores + primary/secondary sub-category per user.","Affinity —")
bullet("monthly / quarterly / yearly return rates per cohort.","Retention —")
bullet("a 1.38M-row user repository with cohort, tiers, affinity and contact keys, ready for MoEngage.","Repository —")

H("3. The base and the leaky bucket",16)
table(["Segment","Customers","% of base","Returns within 1 year"],
     [["O1 — one-time buyers","944,518","68.6%","8.5%"],
      ["O2 — two orders","229,895","16.7%","17.4%"],
      ["3+ — mature","203,281","14.8%","32.3%"],
      ["  · Power Users","55,806","4.1%","48.3%"],
      ["  · Deal Seekers","62,502","4.5%","28.7%"],
      ["  · Light Users","84,973","6.2%","24.8%"]],
     widths=[2.4,1.2,1.0,1.6])
para("Two-thirds of the customer base has bought exactly once and almost never comes back. Value and loyalty are concentrated in the ~4% who become Power Users.",color=GREY,size=10)

H("4. Key findings",16)
bullet("68.6% of customers buy once; their 1-year return is 8.5%. The 1st→2nd order is the biggest retention lever in the business.","Leaky top of funnel —")
bullet("31% of mature customers are Deal Seekers — 80% of their orders are on discount (54% during price-led events), they spend less and go dormant between sales. Low margin, low loyalty (29% annual return).","Discount dependence —")
bullet("Monthly return rates spike in ~March 2026 (the next HPS) across every cohort — repeat purchase is event-triggered, not habitual. BAU repeat is weak.","Event-only repurchase —")
bullet("74% of customers are Tech-affinity; only ~15% skew Designer/Bags despite bags carrying higher AOV — a large cross-sell gap.","Category concentration —")
bullet("59% of mature customers are Dormant (>270 days since last order); only 13% are Active.","Dormancy —")
bullet("Power Users (27% of mature) retain at 48% p.a. and convert in BAU without deep discounts — the profile to grow the base toward.","The bright spot —")

H("5. Where the gaps are",16)
table(["Gap","Evidence","Business impact"],
     [["1. One-time buyers don't return","O1 = 68.6% of base, 8.5% annual return","Largest leak; most acquisition spend wasted"],
      ["2. O2→O3 drop-off","O2 returns 17% p.a. vs 48% for Power","Customers stall before the loyalty inflection"],
      ["3. Discount addiction","Deal Seekers 31% of mature, 80% orders discounted","Margin erosion; fragile, event-only loyalty"],
      ["4. Event-dependence","Return spikes only around HPS","No habitual BAU repeat; revenue lumpy"],
      ["5. Category concentration","74% Tech, 15% Bags","Under-monetised higher-AOV bags line"],
      ["6. Dormancy","59% of mature Dormant","Large reactivatable but decaying pool"]],
     widths=[2.0,2.4,2.2])

H("6. The strategy — priorities",16)
para("Sequenced by leverage. Each play maps to a cohort/lifecycle state and a clear metric.",color=GREY,size=10)
table(["Priority","Target","Play","Primary metric"],
     [["P1 — Win the 2nd order","O1 (new)","Structured 0–60 day onboarding: category education, best-seller in affinity sub-category, ONE first-repeat incentive, replenishment reminder for consumables (screen guards, chargers).","O1→O2 conversion; 90-day repeat"],
      ["P2 — Push to the 3rd","O2","Cross-category nudge + reorder timing; get them to the loyalty inflection.","O2→O3 conversion"],
      ["P3 — Protect & grow Power","Power Users","VIP care, early launch access, full-price cross-sell into Designer/Bags (they're 78% Tech). Suppress blanket discounts.","Power retention; bags cross-sell rate"],
      ["P4 — De-risk Deal Seekers","Deal Seekers","Event-timed but margin-guarded: bundles over deep cuts, raise basket AOV, migrate to full-price with loyalty perks. Event-triggered reactivation.","Discount rate; margin per order"],
      ["P5 — Reduce event-dependence","All mature","Build BAU repeat triggers: personalised replenishment cycles by sub-category; always-on reorder journeys decoupled from sales.","BAU (non-event) repeat share"],
      ["P6 — Reactivate / sunset","Dormant, Light","Sized win-back by value tier & affinity; sunset the unresponsive to protect deliverability.","Reactivation rate; list health"],
      ["P7 — Cross-sell Tech→Bags","Tech-affinity Power/Core","Introduce higher-AOV Designer/Bags via affinity-matched recommendations.","Bags penetration; AOV"]],
     widths=[1.7,1.3,3.2,1.6])

H("7. Measurement & next steps",16)
bullet("Run holdout A/B on each play; measure INCREMENTAL retention/revenue vs business-as-usual, not raw response.")
bullet("Guardrail on discount cost per incremental order and margin, so retention isn't bought unprofitably.")
bullet("Track cohort migration monthly (O1→O2→O3, Deal→Power) as the north-star of the framework.")
bullet("Next analytics iteration: sub-category-level affinity in campaigns, and a propensity-to-repeat model to prioritise P1/P2 spend.")
para("")
foot=d.add_paragraph();fr=foot.add_run("Source: DailyObjects DMR 2020–Jul 2026 · 2.86M attributable orders · 1.38M resolved customers · discount enriched with price-led event detection · cohorts validated on hold-out forward retention (anchor 31 Jul 2025).");fr.italic=True;fr.font.size=Pt(8);fr.font.color.rgb=GREY
d.save(OUT); print("saved",OUT)
