# Handoff: PDP and cart widget effectiveness tracker (BYS, CYP, YMAL)

Paste or attach this file in a DMR Files session to continue. Written 6 Oct 2026.

---

## 1. Goal

Track three recommendation widgets every day from go-live, planned vs actual:

| Widget | Placement | MoEngage identifier (`add_to_cart.referer`) | Go-live |
|---|---|---|---|
| **BYS**: Build Your Stack (SKU recommendations added to many PDPs) | PDP | `dp/quick-sell` (inferred: the only referer that jumped after the 1:20 PM launch) | **6 Oct 2026, ~1:20 PM IST** |
| **CYP** | Probably cart / pre-checkout (TBC) | **None yet.** Tech must add a unique referer before launch | **Thu 8 Oct** (Fri 9 Oct fallback) |
| **YMAL**: "You may also like" with new logic | PDP (assumed) | `dp/cross-sell` (assumed, **confirm**) | **~15 Oct 2026** |

**Main job for this session:** replace my placeholder plan numbers with the per-widget sizing from the earlier DMR threads ("Cross-sell work continuation", "Cart 'you may also like' widget logic", "AOV improvement analysis"). That earlier sizing was not reachable from the cloud session.

---

## 2. Files

GitHub repo `ankitsethidailyobjects/claude`, branch **`claude/sleepy-maxwell-9k0bot`**, folder `widget-tracker/`:

- `DailyObjects_Widget_Effectiveness_Tracker.xlsx`: the tracker.
- `build_tracker.py`: rebuilds the workbook from scratch with openpyxl. Edit it, then run `python build_tracker.py`.
- `HANDOFF_Widget_Tracker.md`: this file.

```bash
git fetch origin claude/sleepy-maxwell-9k0bot
git checkout claude/sleepy-maxwell-9k0bot   # or: git show origin/claude/sleepy-maxwell-9k0bot:widget-tracker/<file> > <file>
```

**Paths:** `OUT` in `build_tracker.py` points to `/home/user/claude/widget-tracker/...`. Change it to a local path before running. After building, recalculate with the xlsx skill's `recalc.py` (or open in Excel) so the formulas get values.

---

## 3. Workbook layout

| Tab | What it holds |
|---|---|
| **Summary** | Each widget's actual vs plan, cumulative from go-live, counting only days with actuals. Covers add-to-cart events, users who added, orders, attributed revenue and net incremental revenue; % to plan colour-coded. Also a site before/after table (PDP viewers, orders, revenue, AOV, conversion, revenue per PDP viewer). |
| **Read Me** | How to use the tracker and the colour legend. |
| **Inputs** | Go-live dates (row 9), baseline (rows 13–20, linked to the daily sheets), **plan levers (rows 23–29, yellow)**, planned impact per day (rows 32–41), site baseline (rows 44–49), portfolio total (rows 52–56). |
| **Site Daily** | One row per day, 30 Sep–31 Dec. Blue inputs: D PDP views, E PDP viewers, F all ATC users, G orders, H revenue, S main-PDP ATC events. Planned revenue = baseline + live widgets' planned net incremental revenue. |
| **BYS / CYP / YMAL Daily** | One row per day. Blue inputs: **G** ATC events, **J** ATC users, **O** widget orders (ATC user → purchase within 24h), **Q** widget ATC value in ₹, **W** removals (optional). Plan columns F, I, N, R, U ramp linearly from baseline to target over the ramp-up days. |
| **Plan by Week** | Monday–Sunday totals of plan vs actual per widget, using SUMIFS on the daily sheets. |
| **Metric Dictionary** | Each metric with its tier (primary / diagnostic / guardrail), definition, MoEngage query and why it matters. |

Colours: blue text = input, green = link to another sheet, black = formula, yellow fill = plan lever.

---

## 4. How the plan works (Inputs tab)

For each widget:
- Target ATC users = baseline users × users multiplier. For CYP the target is set directly because it has no baseline.
- Planned ATC events = target users × ATC events per user.
- Planned widget orders = target users × ATC user → order rate (24h).
- Planned attributed revenue = planned orders × value per ATC user.
- **Net incremental revenue = (planned attributed revenue − baseline attributed revenue) × incrementality %.** This is the number each widget is held to.
- AOV uplift = net incremental revenue ÷ baseline orders per day. This assumes widget items attach to orders that would have happened anyway.

**Current placeholder levers. Replace these with the DMR sizing:**

| Lever | BYS | CYP | YMAL |
|---|---|---|---|
| ATC users multiplier | 1.6× | n/a (target 250 users/day) | 1.25× |
| ATC events per user | 1.6 | 1.2 | 1.4 |
| ATC user → order (24h) | 11.25% (held at baseline) | 20% | 5.5% (baseline 4.6%) |
| Value per ATC user | ₹1,800 | ₹700 | ₹1,210 |
| Incrementality | 50% | 60% | 50% |
| Ramp-up days | 3 | 5 | 7 |
| **→ Net incremental revenue / day** | **₹25.5k** | **₹21.0k** | **₹9.9k** |
| → AOV uplift | +₹18 | +₹15 | +₹7 |

Portfolio total: **about ₹56k/day (about ₹17L per 30 days), +₹41 AOV (+2%)**.

If the earlier sizing is in a different shape (for example incremental revenue or AOV uplift directly), either back-solve the levers to match, or add a "DMR plan" override row on the Inputs tab and point the daily plan formulas at it.

---

## 5. Baseline (MoEngage, 30 Sep – 5 Oct 2026, per day)

**Site:** PDP views 129,516 · PDP viewers 35,392 · all ATC users 12,281 · orders 1,384 · revenue ₹27.92L · **AOV ₹2,018**.

| | BYS (`dp/quick-sell`) | YMAL (`dp/cross-sell`) |
|---|---|---|
| ATC events/day | 566.5 | 946.3 |
| ATC users/day | 419.2 | 706.3 |
| ATC value/day | ₹7.53L | ₹8.56L |
| Value per ATC user | ₹1,796 | ₹1,212 |
| ATC user → order (24h) | 11.25% | 4.55% |
| Widget orders/day | 47.2 | 32.2 |
| Attributed revenue/day | ₹84.7k | ₹39.0k |

Daily values are already filled in for 30 Sep–5 Oct on each sheet.

> **Tracking break:** `add_to_cart` and `begin_checkout` events roughly tripled from **30 Sep**, while PDP views stayed flat and orders rose only about 15%. This looks like a change in how the events are fired. **Do not compare against data before 30 Sep.** If the warehouse has clean add-to-cart data, check this break against it.

---

## 6. Early read on BYS (6 Oct, the launch day)

- In the 2–3 PM IST hour, BYS add-to-carts were **92 vs 31** the day before (3×). Unique users went from 22 to 25, so it was mostly the same users adding more items.
- From 1 to 4 PM IST: site orders per PDP view rose from 1.18% to 1.37%, but revenue was flat (₹4.53L → ₹4.43L) and AOV fell from ₹1,951 to ₹1,861. Widget users who went on to order: 8 yesterday vs 6 today (24h window, 2h for the latest hour).
- Verdict: more add-to-carts are not yet showing up as revenue. One hour of data is too thin to conclude. Recheck on full days.

---

## 7. How to pull actuals (MoEngage MCP)

- **Events:** PDP view = `view_item`, ATC = `add_to_cart`, order = `purchase` (revenue = SUM of `purchase.value`, in ₹). Ignore `Purchase`, which is always 0. `purchase_moeg` is close to `purchase` but slightly lower.
- **Widget filter** on `add_to_cart`: `{"filter_type":"action_attributes","name":"referer","data_type":"string","operator":"in","value":["dp/quick-sell"],"negate":false,"case_sensitive":false}`.
- **Other `referer` values:** `dp` (main PDP button), `dp/addon`, `configurator`, `bundle`, `bp`, `snackbar`, `dp/quick-sell`, `dp/cross-sell`, `quick-sell`, `ecosystem/quick-sell`, `ppup`, `recentlyViewedBP`, `dpCrossSell`.
- **Column G** (ATC events): behavior analysis, `analysis_type: events`, granularity `d`. **Column J** (ATC users): same with `analysis_type: users`. **Column Q** (ATC value): `analysis_type: aggregation`, `{"operation":"sum","attr":{"attr_type":"event","column_name":"value","data_type":"double"}}`.
- **Column O** (widget orders): funnel, step 1 `add_to_cart` with the referer filter → step 2 `purchase`, `funnel_window: 86400`, chart `line`, granularity `d`, grouped by `referer` on step 1.
- **Gotchas:**
  - The time-of-day part of a custom timerange is ignored; it snaps to whole days. Use granularity `h` for intraday reads. Buckets are in IST.
  - Today's numbers lag by roughly 30–60 minutes, so fill only closed days.
  - Big responses get saved to a file; parse them with Python.

---

## 8. Open items

1. **Load the DMR plan numbers** into the Inputs levers (rows 23–29), or add an override row (section 4).
2. **CYP:** get a unique `referer` value from tech before the 8 Oct launch and put it in Inputs!D8. Confirm CYP's full name and placement.
3. **Confirm YMAL = `dp/cross-sell`.** Today it is the busiest PDP recommendation tag.
4. **Use the local warehouse to:**
   - Replace the "attributed revenue" proxy with actual order-line revenue from widget-added SKUs, if the warehouse has a source or line-level tag.
   - Add "% of orders containing a widget SKU" and "units per order".
   - Check the 30 Sep tracking break.
5. **Ask tech for widget impression and click events**, so coverage can be told apart from relevance.
6. **Consider a 10–20% holdout per widget.** It would replace the incrementality assumption with a measured number, which matters because Diwali (8 Nov) will distort before/after comparisons.
7. **Optional:** automate the daily fill with a script that calls the MoEngage queries above and writes the blue cells.
