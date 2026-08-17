# DailyObjects — Doubling CRM Revenue in 2 Quarters (v2, click-through basis)

**Data-backed baseline, problem map, sized roadmap, and retention program — built from live MoEngage pulls.**

Prepared 2026-08-13 · Horizon: next 2 quarters · CRM = all owned messaging (Push, Email, SMS, WhatsApp, RCS, In-App)
Attribution basis: **CLICK-THROUGH** (`metric_click`), per stakeholder decision. View-through shown only for reference.

---

## 0. TL;DR

- **CRM click-through revenue ≈ ₹23.8L / month.** Split: **Journeys ₹15.7L (66%)**, Standalone campaigns ₹8.1L (34%).
- **WhatsApp is the #1 channel (~54% of CT revenue)** — overwhelmingly inside journeys. The earlier "Push+Email duopoly" read was wrong on both counts.
- **Attribution matters enormously:** click-through is ~13× smaller than view-through. This doc uses the stricter click-through number throughout; pick one basis before quoting a board figure.
- **Retention is the core problem:** only **~10% of buyers repurchase the next month**, ~5% by month 3. Engagement retention is no better. No repeat-purchase habit is forming.
- **More lifecycle infra exists than first thought** (checkout/payment-recovery journeys are live and top-earning), but the **biggest gap — an automated 2nd-purchase program and dynamic lifecycle segments — is still missing.**

---

## 1. Revenue baseline (click-through, last 30 days)

### 1.1 By source

| Source | CT revenue | Share | Conversions |
|---|---|---|---|
| **Journeys** (42 active flows) | **₹15.68L** | 66% | 549 |
| **Standalone** (29 push/email + 44 WhatsApp) | **₹8.08L** | 34% | 172 |
| **Total CRM (click-through)** | **₹23.77L** | 100% | 721 |

### 1.2 By channel × source (click-through)

| Channel | In journeys | Standalone | **Total** | Share |
|---|---|---|---|---|
| **WhatsApp** | ₹11.45L | ₹1.28L | **₹12.73L** | ~54% |
| **Push** | ₹1.43L | ₹3.01L | **₹4.44L** | ~19% |
| **Email** | ₹0 | ₹3.79L | **₹3.79L** | ~16% |
| **SMS** | ₹1.02L | ₹0 | **₹1.02L** | ~4% |
| Journey tail (flows 11–42, not split) | ₹1.81L | — | ₹1.81L | ~8% |
| **RCS** | not measurable¹ | none | — | — |

¹ RCS is not a queryable channel in this MoEngage workspace (valid: EMAIL/SMS/PUSH/WHATSAPP/IN_APP/ONSITE/CONNECTOR/CARDS/FB_AUDIENCE/GOOGLE_ADS). Flows contain RCS fallback nodes, but the analytics API won't isolate RCS revenue.

**Reads:** Email earns click-through revenue **only as standalone broadcasts** (₹0 in-journey). SMS earns **only inside journeys**. WhatsApp earns across both and leads overall.

> Reference: view-through revenue is ~13× higher (e.g. standalone email ₹3.79L click-through vs ~₹50L view-through). The gap is because most purchases attribute to an impression, not a click.

---

## 2. Trend

### 2.1 Journeys — weekly CT revenue (reliable segment, all 15 revenue flows reporting)

| Week ending | CT revenue | Conversions |
|---|---|---|
| Jul 11 | ₹1.97L | 64 |
| Jul 18 | ₹2.86L | 98 |
| Jul 25 | ₹3.20L | 113 |
| Aug 01 | ₹3.29L | 128 |
| Aug 08 | **₹3.53L** | 109 |
| Aug 15 (partial to 08-13) | ₹2.60L | 102 |

**Journey CRM revenue is growing ~+80% over five weeks.** (Weeks before Jul 5 are undercounted by coverage ramp, not shown as reliable.)

> **Data limitation:** MoEngage's flow-analytics API only serves recent history (anchored to "now", version-dependent depth ~6–13 weeks). A true 6-month monthly journey series is **not retrievable via this API** — use a warehouse/dashboard export for long-range history.

### 2.2 Standalone — send cadence by month (complete enumeration, 419 campaigns)

| Month | Push | Email | WhatsApp | SMS | Total |
|---|---|---|---|---|---|
| Feb | 8 | 1 | 3 | 0 | 12 |
| Mar | 40 | 19 | 42 | 2 | 103 |
| Apr | 19 | 1 | 13 | 1 | 34 |
| May | 23 | 15 | 27 | 3 | 68 |
| Jun | 22 | 19 | 30 | 3 | 74 |
| Jul | 25 | 27 | 45 | 1 | 98 |
| Aug* | 10 | 4 | 16 | 0 | 30 |
| **Total** | **147** | **86** | **176** | **10** | **419** |

**WhatsApp is the most-sent standalone channel every month.** *(Standalone monthly *revenue* by channel is pending — the 419-campaign detailed sweep was interrupted by the account session limit; to be backfilled.)*

---

## 3. Retention baseline (monthly cohorts, user-level)

Config that works: `run_retention_analysis` with `retention_type="last"` (`"first"` returns spurious zeros).

**Repeat-purchase retention** (bought again N months after first purchase):

| Cohort | Buyers | M1 | M2 | M3 | M4 | M5 |
|---|---|---|---|---|---|---|
| Feb 2026 | 16,692 | 20.2% | 11.4% | 9.4% | 6.5% | 3.8% |
| Mar 2026 | 107,627 | 9.9% | 8.0% | 5.2% | 3.2% | 0.8% |
| Apr 2026 | 29,980 | 11.4% | 7.0% | 4.2% | — | — |
| May 2026 | 39,496 | 8.5% | 4.7% | — | — | — |
| **Typical** | — | **~10%** | **~6.5%** | **~5%** | ~4% | ~2% |

**Engagement (app-open) retention** ≈ 10% M1 → ~3–5% M3 — i.e. purchasers are no stickier than casual app-openers.

**Purchase funnel (30d):** viewed cart 212,795 → began checkout 69,244 (**32.5%**) → purchased 31,051 (**14.6% end-to-end**). Biggest leak: cart→checkout (143.5k users lost/mo).

**Diagnosis:** ~1.2–3.4M monthly actives, only 8–108k monthly buyers (1–2%), and only ~10% of buyers return next month. Severe leaky bucket; the 2x lever is repeat-purchase + conversion of existing traffic, not acquisition.

---

## 4. Problem statements (ranked)

| # | Problem | Lever | Type |
|---|---|---|---|
| **P1** | **No repeat-purchase habit / no 2nd-purchase program.** ~90% of first-time buyers don't return M1. | Retention | Structural (biggest) |
| **P2** | **Cart abandonment under-captured.** 143.5k/mo drop cart→checkout; flagship flow drops ~46% of push on `product-set unmatched`. | Conversion / Deliverability | Leak + optimize |
| **P3** | **Win-back is manual.** RNB WhatsApp earns ₹0.9L+ CT/mo but runs as batch sends, not a triggered dormancy journey. | Frequency | Automate |
| **P4** | **No dynamic lifecycle segments.** All 55 segments are static import lists — nothing to trigger repeatable programs on. | Enablement | Prerequisite |
| **P5** | **WhatsApp runs under-instrumented & leaks.** #1 channel, but a 25,219-send campaign delivered 0, and an in-journey WA node delivered 0/35,453 (template error). | Reach / Ops | Fix + scale |
| **P6** | **Push reachability ceiling.** ~26% of push never renders (Android worst). | Deliverability | Optimize |
| **P7** | **Measurement gaps.** Attribution basis undefined (13× swing); flow history shallow; RCS unmeasurable; retention config was wrong. | Enablement | Prerequisite |

---

## 5. What's already set up (mapped to lifecycle)

| Stage | Live in MoEngage | Health |
|---|---|---|
| Cart abandonment | Abandoned Cart3 (top journey earner), Abandoned Cart post Day-2, Nitro variants | ✅ strong (1 WA node delivers 0 — fix) |
| **Checkout / payment recovery** | Begin_checkout2, Payment_Proceeded2, Payment Failed, Begin checkout post Day-2 | ✅ **live & top-earning** |
| Cross-sell / upsell | Extensive WhatsApp + FB_AUDIENCE grid by category; cross-sell flows | ✅ broad |
| Win-back (lapsed) | RNB WhatsApp campaigns | ⚠️ manual batch, not triggered |
| Loyalty | Redeem Points, Nectar Coins Expiry | ✅ present |
| **2nd-purchase / repeat activation** | Nothing | ❌ biggest gap |
| Lifecycle segmentation | 55 static import lists | ❌ no dynamic RFM |

---

## 6. Top buckets to focus + next steps

**Top buckets (by leverage):** ①  First-time buyers → 2nd purchase (steepest cliff, biggest population); ②  Recently-lapsed buyers (win-back — already proven via RNB WhatsApp); ③  Cart/checkout/payment abandoners (already strong — optimize); ④  Engaged non-buyers (volume play, later).

**Do next (sequenced):**
1. **Build dynamic RFM / lifecycle segments** (P4) — prerequisite for everything.
2. **Launch an automated 2nd-purchase journey** triggered on first `purchase_moeg` (bucket ①, the biggest structural lever).
3. **Automate win-back** — convert manual RNB WhatsApp into a dormancy-triggered journey (bucket ②).
4. **Fix delivery leaks** — the 0-delivered WhatsApp nodes (real money to dead ends).
5. **Operationalize monthly cohort retention** (M1/M3 repeat-purchase) as the north-star KPI, using `retention_type="last"`.
6. **Pick an attribution standard** (click vs view) before publishing a baseline.

---

## 7. Method & caveats

- All figures from live MoEngage pulls (2026-08-13). Attribution = click-through (`metric_click`) unless noted.
- WhatsApp revenue via `get_detailed_campaign_stats` (engagement-only endpoints lack revenue). Standalone WhatsApp enumerated via *unfiltered* `get_campaign_meta` (channel filter rejects WhatsApp).
- Journey vs standalone are attributed independently — a user touched by both is counted in both; no net-dedup possible.
- Flow-analytics: 90-day window cap per call; shallow history (see §2.1); `fields=summary` silently strips output (omit it).
- RCS not a queryable channel here. Retention: `retention_type="last"` required.
- **Open data item:** standalone monthly revenue-by-channel (419-campaign detailed sweep) — interrupted by account session limit; backfill after reset.
