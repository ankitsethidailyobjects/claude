# DailyObjects — Doubling CRM Revenue in 2 Quarters

**A data-backed baseline, problem-statement map, and sized roadmap — built entirely from live MoEngage data.**

Prepared: 2026-08-13 · Horizon: next 2 quarters · Scope: all owned messaging (Push, Email, SMS, WhatsApp, RCS, In-App)

---

## 0. TL;DR

- **Where we are:** CRM drives **≈ ₹10.4M / month** (view-through attribution), a near **50/50 duopoly of Push (~₹5.2M) and Email (~₹5.0M)**. SMS, WhatsApp, RCS and In-App contribute ~zero or are unmeasured.
- **The 2x is a conversion + retention story, not a reach problem.** We already reach 600k–1.2M weekly active users; only **8–13k/week purchase** (1–2%), and only **1 in 8 purchasers buys again the next week**.
- **The prize is real and over-subscribed.** Bottom-up, we've identified **~₹11–15M/month of incremental surface** — more than the **+₹10.4M** needed to double. The constraint is execution capacity and de-duplication, not finding opportunity.
- **Step zero is a blocker:** there are **no dynamic lifecycle segments** in the workspace (all 55 are stale static import lists) and **retention was mis-measured**. Both must be fixed before a compounding program can run — and both are cheap.

---

## 1. Baseline — where we are today

### 1.1 CRM revenue by channel (last 30 days)

| Channel | Campaigns | Sent | Deliv% | CTR% | Conversions | Revenue (view-through) | Rev share |
|---|---|---|---|---|---|---|---|
| **Push** | 20 | 2,160,968 | 73.5%¹ | 1.39% | ~1,920 (est) | **~₹5.2M** (3/20 sampled) | ~51% |
| **Email** | 8 | 798,965 | 99.7% | 0.71% | 1,362 | **₹5.04M** (full census) | ~49% |
| **SMS** | 0 | — | — | — | — | ₹0 | 0% |
| **WhatsApp** | n/a² | — | — | — | — | not measurable via API | — |
| **RCS / In-App** | 0 | — | — | — | — | — | 0% |
| **TOTAL** | 28 | ~2.96M | — | — | ~3,282 | **≈ ₹10.1–10.7M / mo** | 100% |

¹ Push "delivery" = impression render rate. **26% of push never renders** (Android ~67% vs iOS ~76%) — a reachability/opt-in ceiling.
² MoEngage `search_campaigns` in this workspace only accepts EMAIL/PUSH/SMS; **WhatsApp & RCS are rejected by the API** and cannot be enumerated — a measurement blind spot, not a confirmed zero.

> **Attribution note (decide before quoting a public baseline):** figures above use **view-through** (impression) attribution — MoEngage's default. **Click-through revenue is ~13× lower** (Email: ₹5.04M view-through vs ₹0.38M click-through). Pick one basis and standardize. For *relative* 2x goals the basis largely cancels; for a board number it does not.

### 1.2 Retention — the core weakness

Weekly cohort retention (config that works: `retention_type: "last"`; `"first"` returns false zeros — an analytics fix to standardize):

| Weeks after first action | W1 | W4 | W8 | W12 |
|---|---|---|---|---|
| **Repeat-purchase** retention | 12.2% | 7.6% | 3.5% | 0.6% |
| **App-open (engagement)** retention | 26.5% | 13.6% | 7.1% | 1.7% |

**Engagement retention is ~2× purchase retention at every week.** That gap = a large pool of users who keep opening the app/site but don't re-buy — the exact audience a repeat-purchase CRM program is built to convert.

### 1.3 The purchase funnel (last 30 days)

| Step | Users | Step conversion | Users lost |
|---|---|---|---|
| Viewed cart | 212,795 | — | — |
| Began checkout | 69,244 | **32.5%** | **143,551** |
| Purchased | 31,051 | 44.8% | 38,193 |

End-to-end cart→purchase = **14.6%**. The **cart→checkout leak (143.5k users/month)** is the single largest intervention surface; checkout→purchase loses another 38k high-intent users.

### 1.4 Structural state of the CRM stack

| Capability | Status today |
|---|---|
| Dynamic lifecycle / RFM segments | **None** — all 55 segments are static one-off import lists |
| Retention measurement | Was broken (mis-configured); now fixed — needs to be operationalized |
| Live marketing channels | 2 (Push, Email); SMS = operational recalls only |
| WhatsApp | Present but **unmeasurable via API** — governance/measurement gap |
| Attribution standard | Undefined (view-through vs click-through differ ~13×) |

---

## 2. Problem statements (ranked)

Each maps to a lever in **CRM Revenue = Reach × Deliverability × Engagement × Conversion × AOV × Frequency**.

| # | Problem statement | Lever | Type |
|---|---|---|---|
| **P1** | **No lifecycle segmentation or repeat-purchase program.** Repeat-purchase retention halves to ~7.6% by W4; engagement retention is 2× purchase retention (large un-monetized "opens-but-doesn't-rebuy" pool). Nothing targets it. | Frequency / Retention | Structural (foundational) |
| **P2** | **Cart abandonment is under-captured.** 143.5k users/month drop cart→checkout. The flagship Abandoned-Cart flow reaches them push-first and **silently drops ~46% of push sends** on `abandonedcart product-set unmatched`. | Conversion / Deliverability | Leak + optimization |
| **P3** | **No checkout / payment-failure recovery.** 38k/month high-intent users abandon post-checkout-start; `payment-failed` / `rzp_checkout_abandoned` events exist but no recovery journey fires on them. | Conversion | New program |
| **P4** | **Email is under-sent and has deliverability drag.** Drives ₹5.0M from 8 sends, but cadence collapsed from ~23/mo to 8/mo; ~9% of attempts throttled at send; bimodal opens (largest broadcasts open 10–12% vs 26–28%). | Frequency / Deliverability | Quick win |
| **P5** | **Channel concentration risk.** ~100% of CRM revenue is Push+Email. SMS is operational-only, WhatsApp is unmeasured, RCS/In-App unused — no diversification and no high-intent conversational channel active. | Reach / Mix | Structural |
| **P6** | **Push reachability ceiling.** 26% of push never renders (Android ~67%). Opt-in/token health caps the largest channel's ROI. | Deliverability | Optimization |
| **P7** | **Measurement gaps.** Retention `retention_type` mis-set, WhatsApp API blind spot, no standard attribution basis — leadership can't trust a single baseline number. | (Enablement) | Prerequisite |

---

## 3. Size of the prize

Conservative, bottom-up. AOV ≈ **₹2,500** (observed on the Abandoned-Cart flow). Ranges reflect recovery-rate assumptions; **the sum deliberately exceeds the +₹10.4M needed to 2x** — because opportunities overlap (a user can be in cart *and* checkout *and* lifecycle audiences) and view-through attribution is generous. Realistic net capture is a fraction of the gross; the point is there is **more than enough identified surface to double**.

| # | Opportunity | Sizing logic | Monthly incremental (mid) |
|---|---|---|---|
| P2 | **Cart abandonment program** (fix 46% push failure + add Email/WhatsApp arms) | 143.5k abandoners × ~1.5% incremental recovery × ₹2,500 | **~₹3.0M** (range 2.5–3.6M) |
| P3 | **Checkout + payment-failure recovery** (new trigger on high-intent) | 38k abandoners × ~3% × ₹2,500 | **~₹2.5M** (range 1.9–3.8M) |
| P1 | **Repeat-purchase / lifecycle program** (win-back, replenishment, cross-sell) | Close part of the 2× engagement-vs-purchase retention gap; ramps over the 2 quarters | **~₹2.5M** (range 2.0–4.0M) |
| P4 | **Email re-ramp + deliverability fix** (restore cadence, fix throttle/opens) | +8–12 quality sends/mo at ~half marginal efficiency (~₹300k each) | **~₹2.0M** (range 1.5–2.5M) |
| P5 | **WhatsApp activation** (close measurement gap, launch commerce templates) | New channel; India commerce benchmark. Unsized precisely until measurable | **~₹1.5M** (range 1.0–2.0M) |
| P6 | **Push reachability + AC-flow render fix** | Lift render 73.5%→85% at constant CTR + recover flow push | **~₹1.0M** (range 0.8–1.2M) |
| | **Total identified surface** | | **≈ ₹12.5M / mo** (range 9.7–17.1M) |

**2x math:** Baseline **₹10.4M/mo → target ₹20.8M/mo** = **+₹10.4M/mo** needed. Identified gross surface **≈ ₹12.5M/mo (mid)**. Even at ~55–65% net realization after overlap/attribution discounting, the target is reachable — but only if P1/P7 foundations are built early so the retention and lifecycle prizes have time to compound within the window.

---

## 4. Roadmap — sequenced across 2 quarters

Ordered so foundations unblock the compounding prizes, and quick wins fund momentum.

### Quarter 1 — Foundations + leak-fixes (fast, high-confidence)

| Wk | Workstream | Problem | Prize unlocked |
|---|---|---|---|
| 1–2 | **Fix measurement (P7):** standardize `retention_type: "last"`; pick attribution basis; open a WhatsApp measurement path | P7 | Trustworthy baseline |
| 1–3 | **Build dynamic lifecycle/RFM segments (P1):** new / active / dormant / churn-risk / high-value — replace static lists | P1 | Targeting for every program below |
| 2–4 | **Fix Abandoned-Cart flow (P2):** resolve `product-set unmatched` personalization (recover ~46% of push); add an Email arm | P2 | ~₹3.0M/mo |
| 3–6 | **Re-ramp Email (P4):** restore ~20+/mo cadence; fix 9% send throttle; A/B the bimodal-open broadcasts | P4 | ~₹2.0M/mo |
| 4–6 | **Launch checkout/payment-failure recovery (P3)** on `begin_checkout` / `payment-failed` / `rzp_checkout_abandoned` | P3 | ~₹2.5M/mo |

### Quarter 2 — Structural bets (compounding)

| Wk | Workstream | Problem | Prize unlocked |
|---|---|---|---|
| 7–10 | **Repeat-purchase lifecycle program (P1):** win-back (dormant), replenishment (post-purchase timing), cross-sell (category affinity) on the new segments | P1 | ~₹2.5M/mo, compounding |
| 8–11 | **Activate WhatsApp (P5):** commerce templates for cart/checkout/order-update; measure and scale | P5 | ~₹1.5M/mo |
| 9–12 | **Push reachability program (P6):** opt-in prompts, token hygiene, Android render diagnosis | P6 | ~₹1.0M/mo |
| 10–13 | **Cross-sell journey expansion:** extend the existing category cross-sell flows to more segments; retire fatigued late-stage nodes | P1/P2 | Incremental |

---

## 5. Baseline → target scorecard

The single table to track the program against.

| Metric | Now | 2-Quarter target |
|---|---|---|
| **CRM revenue / month** (view-through) | ₹10.4M | **₹20.8M** |
| Repeat-purchase retention (W4) | 7.6% | 12–15% |
| Cart → checkout conversion | 32.5% | 45%+ |
| Checkout → purchase conversion | 44.8% | 55%+ |
| Email cadence (sends/mo) | 8 | 20+ |
| Active dynamic lifecycle segments | 0 | 8–12 |
| Live marketing channels | 2 | 4+ (add WhatsApp, SMS) |
| Abandoned-Cart flow push render | ~54% (46% fail) | 90%+ |
| Push impression-render rate | 73.5% | 85%+ |

---

## 6. Method & caveats (for the analytics team)

- **All figures pulled live from MoEngage** via the connected MCP server (flows, campaigns, funnel, retention, segments) on 2026-08-13.
- **Sampling:** Push revenue extrapolated from 3/20 campaigns (engagement full-census); Email revenue full-census; campaign leak-scan capped at 62 campaigns (page limits noted). Per-journey revenue ranking is being finalized (Section 7, appended).
- **Attribution:** view-through unless stated; click-through floor is ~13× lower — standardize before publishing a baseline.
- **Blind spots:** WhatsApp/RCS not enumerable via the current API filter; In-App not a searchable campaign channel. Closing these is part of P5/P7.
- **Retention config:** use `retention_type: "last"`; `"first"` returns spurious all-zeros in this workspace.

---

## 7. Appendix — Journey portfolio *(finalizing)*

Full per-journey table (all 25+ active flows: entries, drops, conversions, revenue, 6-week trend) is being compiled and will be appended here. Worked example already validated — **Abandoned Cart3** (last 30d): 166,482 entries, 46 drops, 186 click-attributed conversions, **₹482,447 revenue**, 1.42% CVR — with the 46% push personalization failure quantified in P2.
