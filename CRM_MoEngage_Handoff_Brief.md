# Handoff Brief — DailyObjects CRM Revenue Analysis via MoEngage MCP

**Purpose:** Give a fresh Claude session (any account) full context to continue this work without re-deriving it. Paste this file into the new session, or attach it, and say: *"Continue this MoEngage CRM analysis — here's the full context."*

**Prereq in the new session:** the **MoEngage MCP connector must be enabled in that chat** (same DailyObjects workspace). Also useful: Shopify (for order-level revenue history) and a repo/GitHub connector if you want to keep committing the strategy doc.

---

## 1. The goal

DailyObjects (ecommerce, Shopify + MoEngage) wants to **double CRM revenue in 2 quarters**. CRM = all owned messaging (Push, Email, SMS, WhatsApp, RCS, In-App). We used the MoEngage MCP to pull journeys ("Flows"), standalone campaigns, retention cohorts, and the purchase funnel; identified problem statements + sized opportunities; and drafted a strategy doc.

**Deliverable in repo:** `CRM_Revenue_2x_Strategy.md` (v2, click-through basis) on branch `claude/moengage-data-extraction-0w66ef`. There is also a `MoEngage_Journey_Analytics_Playbook.md`.

---

## 2. Status — what's DONE vs OPEN

**DONE (all committed):**
- CRM revenue re-based to **click-through** attribution
- WhatsApp revenue method solved; WhatsApp identified as #1 channel
- Journeys vs standalone split + channel matrix
- SMS/RCS resolved; consistency corrections
- Monthly cohort retention + top buckets + what's-set-up/next
- Weekly journeys revenue trend

**OPEN (one item):** the **standalone monthly revenue-by-channel trend** — requires a `get_detailed_campaign_stats` call for each of **419 campaigns**. Repeatedly blocked this session by (a) MoEngage MCP connection flapping, (b) API rate-limit when run in parallel, (c) 9KB-per-call payloads overflowing context, (d) an account session usage limit. **Method to finish it is in §6.** The 419-campaign list is attached as `campaigns.csv`.

---

## 3. Key findings (all click-through / `metric_click`, last 30 days unless noted)

**Revenue by source:**
- Journeys (42 active flows): **₹15.68L** (66%), 549 conversions
- Standalone (29 push/email + 44 WhatsApp): **₹8.08L** (34%), 172 conversions
- **Total CRM click-through ≈ ₹23.77L / month**

**Revenue by channel × source:**

| Channel | In journeys | Standalone | Total | Share |
|---|---|---|---|---|
| WhatsApp | ₹11.45L | ₹1.28L | ₹12.73L | ~54% |
| Push | ₹1.43L | ₹3.01L | ₹4.44L | ~19% |
| Email | ₹0 | ₹3.79L | ₹3.79L | ~16% |
| SMS | ₹1.02L | ₹0 | ₹1.02L | ~4% |
| Journey tail (flows 11–42, unsplit) | ₹1.81L | — | ₹1.81L | ~8% |

- **WhatsApp is #1 (~54%)**, mostly in-journey. Email earns CT revenue only as standalone broadcasts. SMS only inside journeys.
- **View-through revenue is ~13× click-through** — decide one basis before quoting a board number.

**Top journeys (30d CT revenue):** Abandoned Cart3 ₹4.9L · Begin_checkout2 ₹3.0L · Payment_Proceeded2 ₹1.6L · Payment Failed ₹1.5L · Begin checkout post Day-2 ₹1.1L.

**Weekly journeys trend (all 15 revenue flows reporting):** ₹1.97L (wk-end Jul 11) → ₹2.86L → ₹3.20L → ₹3.29L → ₹3.53L (Aug 8); **+80% over 5 weeks.**

**Standalone send cadence by month (complete enumeration, 419 campaigns):**

| Month | Push | Email | WhatsApp | SMS | Total |
|---|---|---|---|---|---|
| Feb | 8 | 1 | 3 | 0 | 12 |
| Mar | 40 | 19 | 42 | 2 | 103 |
| Apr | 19 | 1 | 13 | 1 | 34 |
| May | 23 | 15 | 27 | 3 | 68 |
| Jun | 22 | 19 | 30 | 3 | 74 |
| Jul | 25 | 27 | 45 | 1 | 98 |
| Aug* | 10 | 4 | 16 | 0 | 30 |
| **Total** | 147 | 86 | 176 | 10 | 419 |

**Monthly cohort retention (`retention_type="last"`):** repeat-purchase ~10% M1 → ~6.5% M2 → ~5% M3 → ~2% M5. Engagement (app-open) ≈ 10% M1 → ~3% M3. Purchasers barely stickier than app-openers → no repeat-purchase habit.

**Purchase funnel (30d):** viewed cart 212,795 → began checkout 69,244 (**32.5%**) → purchased 31,051 (**14.6% end-to-end**). Biggest leak: cart→checkout (143.5k users/mo).

**Structural:** ~1.2–3.4M monthly actives, only 8–108k monthly buyers (1–2%). No dynamic lifecycle/RFM segments (all 55 are static import lists). Lever = repeat-purchase + conversion of existing traffic, not acquisition.

**Corrections caught (recheck):**
1. **RCS is NOT a queryable channel** in this workspace (valid: EMAIL/SMS/PUSH/WHATSAPP/IN_APP/ONSITE/CONNECTOR/CARDS/FB_AUDIENCE/GOOGLE_ADS). Flows have RCS fallback nodes but revenue can't be isolated.
2. **Checkout/payment-recovery journeys already exist** and are top earners (Begin_checkout2, Payment_Proceeded2, Payment Failed).
3. **Delivery leaks:** standalone "Phonecase Cross-sell O1" delivered 0/25,219; in-journey "Abandoned Cart post Day-2" WhatsApp node delivered 0/35,453 (template error).

---

## 4. MoEngage MCP method cookbook (the transferable know-how)

**Attribution:** click-through revenue = `conversion_goals[0].metrics.metric_click.revenue` (standalone, `get_detailed_campaign_stats`) or `attribution_type="CLICK_THROUGH"` → `...metric_stats.metric_click...` (flows, `get_flow_analytics`). `metric_impression` = view-through (~13× bigger). `metric_default` = default model.

**Journeys = "Flows":** `search_flows(status=["ACTIVE"], limit=100)` to list (42 active). `get_flow_analytics(flow_id, activity_after, activity_before, attribution_type, metric_type="UNIQUE", granularity)` for revenue/drop-off. `get_flow_channel_analytics(flow_id, channel=...)` for per-channel — payloads can be **7,000+ lines** for multi-node flows (delegate parsing / grep the saved file). `get_flow(flow_id)` for structure.

**Standalone campaigns:**
- Enumerate with `get_campaign_meta` (lightweight) — **the channel filter only accepts EMAIL/PUSH/SMS; WhatsApp/RCS are REJECTED as filter values.** To get WhatsApp/FB_AUDIENCE, enumerate **unfiltered** and filter client-side on the `channel` field. (This is why WhatsApp was invisible in the first pass.)
- Revenue: `get_detailed_campaign_stats(campaign_id, start_date, end_date)` — returns ~8–9KB, no field selector, **single campaign, ≤30-day window**. `get_campaign_stats` returns engagement only (NO revenue). `get_click_performance`/`get_delivery_stats` also have NO revenue.

**Retention:** `run_retention_analysis` — **must use `retention_type="last"`** (`"first"` returns spurious all-zeros in this workspace). Events verified: `purchase_moeg`, `MOE_APP_OPENED`, `view_cart_moeg`, `begin_checkout_moeg`. Attribute filters must be empty (`filters:[]`). Funnel: `run_funnel_analysis`.

**Gotchas / limits:**
- **Flow-analytics date window capped at 90 days per call** (split 6 months into two ≤90-day windows).
- **Flow analytics only serves recent history** (anchored to "now", version-dependent depth ~6–13 weeks). A true 6-month monthly journey series is **NOT retrievable** via this API — use Shopify/warehouse for long-range history.
- **`fields=summary` on `get_flow_analytics` silently strips the summary** — omit it.
- **Rate-limit:** running many subagents in parallel trips MoEngage's WAF (nginx **403 Forbidden**) account-wide. Run **single-threaded / small sequential waves**. A 403 is not a permissions issue — back off, don't retry-loop.
- Currency INR. AOV ≈ ₹2,500.

---

## 5. Problem statements & plan (from the strategy doc)

**Ranked problems:** P1 no repeat-purchase/2nd-purchase program (biggest) · P2 cart abandonment under-captured (+46% push personalization failure on flagship flow) · P3 win-back is manual (RNB WhatsApp batch, not triggered) · P4 no dynamic lifecycle segments · P5 WhatsApp under-instrumented + delivery leaks · P6 push reachability ceiling (~26% never renders) · P7 measurement gaps.

**Top buckets:** ① first-time→2nd purchase, ② recently-lapsed (win-back), ③ cart/checkout/payment abandoners (already strong), ④ engaged non-buyers.

**Do next:** (1) build dynamic RFM/lifecycle segments; (2) automated 2nd-purchase journey on first `purchase_moeg`; (3) automate win-back (dormancy-triggered); (4) fix 0-delivered nodes; (5) operationalize monthly cohort retention KPI; (6) pick attribution standard.

---

## 6. How to finish the OPEN item (standalone monthly revenue-by-channel)

1. Confirm MoEngage MCP is enabled in the new chat; test one `get_detailed_campaign_stats` call.
2. Use the attached **`campaigns.csv`** (419 rows: `campaign_id,channel,send_time`) — these IDs are workspace-level, valid for the same MoEngage workspace. (If a different workspace, re-enumerate via unfiltered `get_campaign_meta`, created_date_from 2026-02-14 to 2026-08-13, keeping PUSH/EMAIL/WHATSAPP/SMS.)
3. Process in **batches of ~35 campaigns** via CSV-writing subagents (keeps 9KB payloads out of main context). For each: `get_detailed_campaign_stats(campaign_id, start_date=send_time, end_date=min(send+30d, 2026-08-13))`, extract `metric_click.revenue` + `metric_click.unique`, append `campaign_id,channel,send_time,click_revenue,click_unique` to a per-batch CSV.
4. Run batches in **small sequential waves (≤4)** to avoid the 403 rate-limit; stop a wave on any 403/session-limit and resume later.
5. Aggregate all CSVs → monthly table (Feb–Aug 2026) split by channel. Combine with the weekly journeys trend (§3). Update `CRM_Revenue_2x_Strategy.md` §2.2 and commit.

*Note: expect click-through standalone revenue to be modest (view-through is ~13× higher). WhatsApp "Rain Order late" (order-status) campaigns have no purchase goal → CT revenue 0 (expected, transactional).*

---

## 7. Repo / files
- Branch: `claude/moengage-data-extraction-0w66ef`
- `CRM_Revenue_2x_Strategy.md` — the main deliverable (v2, click-through)
- `MoEngage_Journey_Analytics_Playbook.md` — paste-and-go MoEngage prompt playbook
- `campaigns.csv` (attached to this handoff) — the 419-campaign enumeration for the open sweep

*Prepared 2026-08-13. All figures from live MoEngage pulls that day.*
