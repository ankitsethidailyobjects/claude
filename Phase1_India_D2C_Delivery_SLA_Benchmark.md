# Phase 1 — India D2C Delivery SLA & Logistics Benchmarking

**Prepared for:** DailyObjects (Indian D2C — tech/lifestyle accessories: phone cases, bags, tech accessories, desk/lifestyle goods)
**Date compiled:** 11 August 2026
**Scope:** Phase 1 only — external benchmark of delivery SLAs, fulfilment models and logistics players. **This document deliberately does NOT propose a solution.** It establishes facts and frames the Phase 2 internal diagnostic.

---

## ⚠️ Methodology & honesty statement (read first)

This research was conducted from a controlled environment whose **network egress proxy blocked direct access to every commercial brand and provider website** (dailyobjects.com, mokobara.com, delhivery.com, wareiq.com, inc42.com, etc. all returned `EGRESS_BLOCKED`). The practical consequences:

1. **No live PIN-code / checkout delivery-date widget could be triggered for any brand.** The brief's ideal method (visit PDP → enter PIN → record the promised date across 7 cities) was **not technically executable here.** We did not fabricate any per-PIN promised dates.
2. Every brand SLA below is therefore a **stated shipping-policy range or a 2025-26 news-reported claim, synthesised from web-search results** — clearly a **secondary** observation, not a live customer-facing promise. Confidence is capped accordingly.
3. This is the single biggest gap in the benchmark. **Recommended remediation:** a person (or an unrestricted browser/agent) should re-run live checkout checks for the priority brands on the 7 target metros + 2 Tier-2 pincodes. Section 2 flags exactly which rows need this.

We distinguish throughout between three things the brief rightly insists are **not interchangeable**:
- **Marketing claim** (what a brand/provider advertises)
- **Customer-facing promised SLA** (what the checkout actually commits to a buyer)
- **Evidence of actual fulfilment performance** (measured delivery data)

Confidence legend used: **Confirmed** (primary filing/official) · **High** (well-documented, multiple credible 2025-26 sources) · **Medium** (single credible secondary / policy-page extraction) · **Low** (single weak source or inference). Claim labels in case studies: **Confirmed / Strong inference / Hypothesis / Unknown.**

---

# Section 1 — Executive Summary

### What is the current delivery benchmark in Indian D2C?
The market has bifurcated into two regimes:

- **Standard D2C self-fulfilment** (the majority, DailyObjects included): **~1-day dispatch + 2–5 working days delivery** to metros, longer to Tier-2/3 and the North-East/J&K. Most brands ship from **one or two warehouses via national couriers** (Delhivery, Blue Dart, XpressBees, Ecom Express, Shadowfax). This is the honest baseline for a broad-catalogue accessories brand.
- **A fast-delivery vanguard** built on **decentralised inventory** (regional FCs and/or dark stores) plus, increasingly, **quick-commerce**: next-day-to-same-day and, for a thin best-seller assortment, **30-minute to 2-hour** delivery in metros.

### What qualifies as "good", "great", "best-in-class"?
| Tier | Metro promise | What it takes | Representative players |
|---|---|---|---|
| **Table stakes** | 3–5 days | Single central warehouse + national courier | Most D2C incl. DailyObjects, boAt (3–5d), SUGAR (2–5d), Vahdam, XYXX |
| **Good** | 2-day / next-day to major metros | Regional FCs OR a distributed-inventory 3PL; later courier cut-offs | Snitch (48-hr, 7,000+ pins), Wrogn (2–3d metro), Titan express |
| **Great** | Reliable next-day across 100+ cities | 20–45 regional/city FCs + inventory placement + strong last-mile | Nykaa (70% next-day, 44 warehouses), Amazon/Flipkart standard |
| **Best-in-class** | Same-day / 30-min–2-hr on hero SKUs | Dark-store / MFC network (own or rented) or QC listing | Myntra M-Now (30-min, 87+ dark stores), Flipkart Minutes, Blinkit/Zepto D2C, CaratLane Dash (4–6h), Lenskart×Blinkit (10-min) |

### Who appears to be fastest?
On **customer-facing promise**, the fastest are the **quick-commerce/dark-store operators**: Flipkart Minutes (8–16 min), Blinkit/Zepto/Instamart-listed D2C (10–30 min), Myntra M-Now (30 min), NEWME Zip (60–90 min), CaratLane Dash (4–6 hr). Among **pure D2C brands on their own storefront**, Snitch's **48-hour** national promise and Nykaa's **70% next-day** are the strongest broad-catalogue benchmarks. **Lenskart is the most instructive outlier** — it hits **next-day across 58 cities from essentially ONE automated factory**, i.e. speed via automation + air express, not many nodes.

### What operating models enable this?
Speed is bought in this order of leverage: **(1) where the inventory sits**, **(2) how fast the warehouse picks/packs and hands over**, **(3) which courier moves the parcel.** The fast vanguard almost always changed **(1)** — they moved stock closer to the customer (regional FCs, city FCs, or dark stores), or rented someone else's proximity (a distributed-inventory 3PL, or a quick-commerce dark-store network). See Section 3.

### Is the market moving to next-day or same-day?
**Both, in two layers.** Next-day-to-metros is becoming **table stakes** for scaled D2C (Nykaa, Snitch, marketplaces). Same-day/instant is a **separate, thinner layer** reserved for **hero SKUs** because dark stores can only economically hold a narrow best-seller assortment. For a broad accessories catalogue, "same-day on everything" is **not** economically realistic; "next-day on most metro demand + instant on a few hero SKUs" is the achievable frontier.

### Can changing the logistics partner alone materially improve SLA? — **The central finding**
**No — not on its own, and this is the most important conclusion of Phase 1.** A courier can only compress first-mile, line-haul, last-mile and cut-off time. It **cannot** overcome the fact that the inventory is physically far from the customer. If DailyObjects ships nationally from one warehouse, the *fastest courier in India cannot make that next-day everywhere* — the **SLA floor is set by inventory architecture.** The fast brands changed *where the stock lives*; the courier was the enabler, not the cause. (Corroborated independently across Nykaa's regionalisation case, Lenskart, and multiple logistics sources — Section 6.)

**A DailyObjects-specific reframe:** our current partner **ElasticRun is not a metro D2C express courier at all** — it is a **rural / semi-urban e-B2B kirana-distribution** network (see Sections 4–5). So the "should we switch logistics partner?" question is partly mis-specified: the more accurate questions are *"do we have the right kind of partner for metro D2C parcels, and is our inventory in the right places?"* — which is exactly what Phase 2 must measure.

---

# Section 2 — Brand SLA Benchmark

**Basis:** stated shipping-policy ranges + 2025-26 news (secondary; see methodology note). **No live PIN-code checks were possible.** SLA bucket = metro (SD = same-day, ND = next-day).

## 2.1 Master benchmark table (32 brands)

| # | Brand | Category | Stated dispatch | Stated delivery SLA (metro) | Metro bucket | Express option & fee | Free-ship threshold | COD | Quick-commerce presence | Conf. | Source |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | **DailyObjects** | Tech accessories/lifestyle | ~1 day | ~2–3 working days after ship; ~1 wk total | 3-day / 4–5 | None stated | ₹1,199 (prepaid) | Yes (flat ₹79) | None found | Med | dailyobjects.com policy |
| 2 | **Mokobara** | Luggage/bags | 24–48 hrs | 3–5 days (up to 3–7) | 3-day / 4–5 | None stated | Free (all orders) | Select pins | None | Med | mokobara.com/pages/shipping-policy |
| 3 | **Nasher Miles** | Luggage/bags | up to 7 wkg days | 2–5 wkg days (1–7) | 4–5 / 5+ | None | ₹500 prepaid; else ₹99 | Yes (+₹99–199) | None | Med | nashermiles.com/pages/faq-page |
| 4 | **The Souled Store** | Apparel/accessories | MTO 3–4 days | 7–8 wkg days | 5+ | None | ₹495; else ₹50 | via site | Myntra M-Now, KNOT (30-min) | Med | v1.thesouledstore.com/shipping-policy |
| 5 | **Bewakoof** | Apparel/accessories | on confirmation | 7–8 wkg days | 5+ | TriBe free standard | ~₹499–999 | Yes | Myntra M-Now, KNOT | Med | bewakoof.com/contact-us |
| 6 | **Snitch** | Menswear/fashion | ~24 hrs | 2–5 business days | 2-day/3-day | **48-hr, 7,000+ pins (2025)** | Free (prepaid) | Yes (+₹100) | Own 48-hr; KNOT | Med-High | snitch.co.in/pages/faq + news |
| 7 | **NEWME** | Fast fashion/accessories | own dark stores | Std 3–7d; **Zip 60–90 min** (Del-NCR, Blr) | SD / <2h | Zip 60–90 min | varies | Yes | **Own QC (60–90 min)** | Med-High | indianretailer / afaqs |
| 8 | **Urbanic** | Fast fashion | 3–5 business days | +2–6 days; 3–10 total | 5+ | None | ₹500; else ₹60 | courier-dep | None | Med | in.urbanic.com/policy/shipping |
| 9 | **BlissClub** | Activewear | ~3 days | 3–7 (up to 1–10) days | 4–5 / 5+ | None | fee at checkout | Yes (+fee) | None | Low-Med | blissclub.com/pages/shipping-policy |
| 10 | **Zouk** | Bags/accessories | 24–48 hrs (MTO 10d) | 2–5 days | 3-day / 4–5 | **Express 1–2d** select cities | Free (prepaid) | Yes (+1–2d) | Express (own) | Med | zouk.co.in/pages/shipping |
| 11 | **Lenskart** | Eyewear | 24-hr (lenses) | Next-day in 58 cities; std historically 8–10d | ND / SD via QC | **Blinkit 10-min glasses** (7 metros) | varies | Yes | **Blinkit 10-min** | Med-High | IPO notes; blinkit news |
| 12 | **Titan/Fastrack** | Watches/jewellery | on confirmation | 5–7 wkg days | 5+ | **Express next-day** 5 metros (order by 12PM) | Free | via checkout | None | Med-High | titan.co.in/shipping-policy |
| 13 | **CaratLane** | Jewellery | SD ship if <1PM | **"Dash" 4–6 hr** pilot; Amazon 48-hr tie-up | SD / few-hrs | Dash 4–6h; Amazon 48h (7 cities) | varies | Yes (≤₹49k) | **Own 4–6h QC + Amazon 48h** | Med-High | retailjewellerindia |
| 14 | **boAt** | Audio/electronics | on confirmation | **3–5 business days** after ship | 4–5 | SD category (select) | ₹499 | via courier | Blinkit/Zepto (3P sellers) | Med | boat-lifestyle.com/faqs |
| 15 | **Noise** | Wearables/electronics | within 3 wkg days (2PM cutoff) | 7–10 business days | 5+ | None | Free >₹100 (prepaid) | Yes (+₹100) | QC via 3P (unconfirmed) | Med | support.gonoise.com |
| 16 | **Nykaa** | Beauty | 24–48 hrs | Std 4–5d post-dispatch; **70% next-day** | 4–5 / ND | **Express 2–3d (paid)**; Now 30min–2h | ₹299 (free prepaid); else ₹70 | Yes | **Nykaa Now 30min–2h pilot** | Med-High | nykaa.com + Inc42/BS |
| 17 | **Myntra** | Fashion platform | n/a | Std 3–7d; **M-Now 30 min** (10 cities) | SD / 30-min | **M-Now 30-min (free)** | via checkout | Yes | **Own M-Now (30-min)** | High | TechCrunch / IndianRetailer |
| 18 | **Ajio** | Fashion platform | on confirmation | 3–7 business days | 4–5 | SD/ND premium metros (extra) | above min | Yes (+fee) | Limited express | Med | ajio.com/deliverypolicy |
| 19 | **Amazon India** | Marketplace | n/a | Prime **SD/ND**; 4-hr on 20k+ SKUs | SD / ND / <4h | Free SD for Prime; **Amazon Now** (mins) | ₹499 (non-Prime std) | Yes | **Amazon Now** | High | aboutamazon.in |
| 20 | **Flipkart** | Marketplace | n/a | Std multi-day; **Minutes 8–16 min** | SD / 10-16 min | Minutes ₹5 fee; 1,000+ MFCs, 130+ cities | varies | Yes | **Flipkart Minutes** | High | Inc42 / BS |
| 21 | **Croma** | Electronics retail | SD if <4PM | **Same-day (Express)** select SKUs | SD (express) | Express SD + "Zip" (hours) | fees apply | Yes | Own Express/Zip SD | Med-High | croma.com/lp-express-delivery |
| 22 | **SUGAR Cosmetics** | Beauty | 24–48 wkg hrs | 2–5 working days | 3-day / 4–5 | None (own site) | Free >₹699; else ₹99 | Yes | **Blinkit/Zepto/Instamart (10-min)** | Med-High | sugarcosmetics.com/faqs |
| 23 | **Mamaearth** | Beauty/personal care | within 48 hrs | 3–4 days post-ship (up to 5–6) | 4–5 | None (own site) | varies | Yes | **Blinkit/Instamart (10-min)** | Med | mamaearth.com/pages/shipping-policy |
| 24 | **Wakefit** | Furniture/mattress | on confirmation | Mattress 2–5d; furniture 5–10d | 4–5 / 5+ | None | Free | via checkout | None | Med | wakefit.co |
| 25 | **Pepperfry** | Furniture | varies | **24-hr furniture (Mumbai select)**; else wk+ | ND (Mum) / 5+ | 24-hr Mumbai (select SKUs) | zone-based | Yes | Own 24-hr (Mumbai) | Med | pepperfry press release |
| 26 | **Bombay Shirt Co.** | Custom apparel | 7–9 days (MTO) | 7–14 days + shipping | 5+ (MTO) | None (MTO) | Free (all-India) | via checkout | None (MTO) | Med-High | bombayshirts.com/pages/shipping-policy |
| 27 | **Wrogn** | Menswear | 1–2 days | **2–3 days metro**; 3–5 rest | 2-day/3-day | None | Free (all-India) | Yes (band) | None | Med | wrogn.com/pages/shipping-and-handling |
| 28 | **Vahdam** | Tea/F&B | within 48 hrs | 5–7 days post-dispatch | 5+ | None | ₹599 (prepaid) | Yes (+₹25–50) | None | Med-High | vahdam.in/pages/shipping-delivery |
| 29 | **Bombay Shaving Co.** | Grooming | on confirmation | 3–4 days after ship | 4–5 | None | Free >₹299 | Yes | Blinkit/Zepto (grooming) | Med | bombayshavingcompany.com policy |
| 30 | **Beardo** | Grooming | on confirmation | not clearly stated (few days) | 4–5 (inferred) | None | Free >₹399/₹499 | Yes (₹49–99) | QC (grooming) | Low-Med | beardo.in/policies/shipping-policy |
| 31 | **Sirona** | FemCare/personal care | on confirmation | 6–8 working days | 5+ | None | Free >₹300; else ₹99 | Yes | Blinkit/Zepto | Med | thesirona.com/shipping |
| 32 | **XYXX** | Innerwear/apparel | 3–4 days | 5–7 wkg days (up to 10) | 5+ | None | Free >₹749/₹799; else ₹99 | likely | None confirmed | Med | xyxxcrew.com/pages/shipping-policy |

## 2.2 Delivery-speed landscape (Part B classification)

**By metro promise bucket:**
- **Same-day / instant (30 min – few hrs):** Flipkart Minutes, Amazon Now, Myntra M-Now, NEWME Zip, CaratLane Dash, Lenskart×Blinkit, Croma Express, SUGAR/Mamaearth via QC, Nykaa Now (pilot).
- **Next-day / 2-day:** Snitch (48-hr), Wrogn (metro 2–3d), Titan express, Nykaa (70% next-day), Amazon/Flipkart standard Prime/Plus, Zouk express.
- **3-day:** DailyObjects, Mokobara, SUGAR (own site), Ajio.
- **4–5 day:** boAt, Mamaearth, Bombay Shaving Co., Nasher Miles, Wakefit.
- **5+ day:** The Souled Store, Bewakoof, Urbanic, Noise, Vahdam, Sirona, XYXX, Bombay Shirt Co. (MTO), BlissClub (worst case).

**Approximate median own-storefront metro SLA:** ~**3–5 working days** (excluding QC channels). The QC layer is a **separate distribution channel**, not the brand's own-site logistics — an important distinction.

**Geographic pattern (from policies):** almost every brand's SLA **degrades from metro → Tier-2/3 → North-East/J&K** (often +2–4 days, sometimes air-only surcharges). Fast promises (M-Now, Rapid Commerce, dark-store models) are **metro-and-a-few-Tier-2-first**; the long tail of India stays multi-day.

**Category pattern:**
- **Beauty/grooming/FMCG-like** → fastest via **quick-commerce** (thin SKU, high frequency): SUGAR, Mamaearth, boAt hero SKUs.
- **Fashion/apparel** → **dark-store fashion QC** emerging (M-Now, NEWME, KNOT) but standard own-site still 3–8 days.
- **High-value/considered (jewellery, eyewear, watches, luggage)** → mostly multi-day, but notable **instant pilots on hero SKUs** (CaratLane Dash, Lenskart×Blinkit, Titan express).
- **Furniture** → inherently slow (2–10 days) except localised 24-hr pilots (Pepperfry Mumbai).

**Brands that recently improved (2025–26), with evidence:** Snitch (48-hr launch), NEWME (Zip 60–90 min), Lenskart (Blinkit 10-min), CaratLane (Dash 4–6h + Amazon 48h), Myntra (M-Now, Dec 2024→10 cities), Amazon (fastest Prime year, +40% SD/ND items), Flipkart (Minutes to 1,000+ MFCs), Nykaa (30min–2h pilot). Sources embedded in Section 2.1 / research appendix.

**Brands charging for expedited delivery:** Nykaa (Express 2–3d paid), Ajio (SD/ND premium), Nasher Miles (COD/express fees), Zouk (express in select cities). Most QC (Flipkart Minutes ₹5, Blinkit/Zepto delivery fees).

**Brands with inventory-location-dependent SLAs:** Nykaa (regional FC nearest wins), Myntra (M-Now dark store vs national FC), Amazon/Flipkart (FBA/Assured seller stock location), Pepperfry (Mumbai-only 24-hr). This is the tell-tale signature of **decentralised inventory** driving speed.

**Marketing claim vs promise vs performance — caution:** e.g. boAt is *marketed* as fast and *listed* on QC, but its **own-site promise is 3–5 days** and we have **no measured performance data**. Treat all three layers separately; only Section 2.1's "stated SLA" column is a (secondary) promise, and **none** of this table is measured performance.

---

# Section 3 — Fulfilment Model Benchmark

Speed is a function of **where inventory sits** far more than **which courier carries it.** The models below are ordered from slowest/cheapest to fastest/most-complex.

| # | Model | Typical SLA | Inventory need | Infra | Op. complexity | Economics | Best for | Key limitation | Brands using it | Enabling partners |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | **Central single warehouse** | 1d same-zone; 2–5+d cross-country; 5–8d NE/J&K | Lowest (one pool, no duplication) | 1 DC + national courier | Lowest | Lowest working capital; **highest freight & RTO on long lanes** | Early-stage, long-tail catalogues, high-value/low-volume | Cannot do national next-day | **Lenskart** (Bhiwadi factory), most early D2C, likely **DailyObjects today** | Delhivery, Blue Dart, XpressBees, Ecom, Ekart |
| 2 | **Regional warehouses (multi-zone)** | Next-day most metros+T2; same-day in-region | Moderate (fast-movers replicated 3–6 zones) | 3–8 regional DCs | Medium-high | **Nykaa: −19% fulfilment cost, −24% split shipments, OTD 4→2.3d** | Scaled D2C (₹100 Cr+), predictable regional demand | Split-shipment risk; per-node forecasting | **Nykaa (18→44 warehouses)**, boAt (hybrid) | WareIQ, Eshopbox, Prozo, Mahindra Logistics |
| 3 | **City-level FCs** | Same-day in city; next-day belt | High duplication of top SKUs | City DCs | High | High fixed real-estate/labour per node | High-volume in a few dense metros | Uneconomic in low-density cities | Nykaa Express (320+ stores as nodes) | 3PLs; ship-from-store tech |
| 4 | **Dark stores / MFCs** | **10–30 min to ~2 hr** | Narrow best-seller assortment; very high duplication | Dense 2–5k sq ft dark-store grid + riders | Very high (100s–1000s of nodes) | Real-estate heavy; **fragile unit economics** at low AOV | High-frequency, low-consideration hero SKUs | **Cannot hold a broad catalogue per store** | Myntra M-Now (87+), Flipkart Minutes, Nykaa Now | Ekart, third-party dark-store ops, Delhivery Rapid |
| 5 | **3PL distributed inventory** | Same/next-day where a node holds stock | Brand stock **placed across provider network** via AI | **None owned** (uses provider FCs) | Medium (outsourced) | **Variable cost** (per-order/storage); zone-freight savings | D2C wanting multi-node speed **without capex** | Margin shared; placement quality = provider's | brands on **WareIQ/Eshopbox/Delhivery FaaS** | **WareIQ (20+ FCs), Eshopbox, Prozo, Delhivery (85 FCs)** |
| 6 | **Quick-commerce inventory** | 10–30 min | Thin consignment in platform dark stores | Platform-owned | Low ops / high commercial | **18–30% all-in take-rate** (commission 15–25% + storage/fulfilment fees) | Impulse best-sellers, beauty/FMCG, availability play | Thin assortment; margin compression | SUGAR, boAt, Mamaearth on Blinkit/Zepto/Instamart | Blinkit, Zepto, Instamart, Flipkart Minutes |
| 7 | **Hybrid (SKU-segmented)** | Tiered: mins (hero) / next-day (bulk) / 2–5d (tail) | A-items→dark store, B→regional, C→central | All tiers + routing brain | **Highest** | Optimises speed/cost/working-capital | **Large multi-category; the likely DailyObjects target** | Needs mature OMS/routing | **Nykaa, Myntra, Amazon, Flipkart** | Full 3PL + OMS/WMS (Increff, Unicommerce) |
| + | **Marketplace fulfilment (FBA / Seller Flex / Assured)** | Prime/Assured SD/ND | Ship into or store-and-badge | Marketplace network | Medium | Marketplace fees vs. fast-badge conversion | Brands selling heavily on Amazon/Flipkart | Channel-specific, not own-site | Most marketplace D2C | Amazon FBA, Flipkart, Seller-Flex-ready 3PLs (WareIQ, Eshopbox) |

**Cross-cutting facts:**
- India's **courier zone system (A same-city → E remote NE/J&K)** governs Model-1 SLAs; distance is destiny.
- **RTO dividend:** orders delivered in **≤2 days show ~30–40% lower RTO** than 5+ day orders — speed is a margin lever, not just CX (Strong inference, industry data).
- **For DailyObjects' broad accessories catalogue, Models 4/6 (dark store / QC) can only ever hold hero SKUs.** The realistic fast architecture is **Model 5 (distributed 3PL) → maturing into Model 7 (hybrid)**, with QC as an *additional sales channel* for hero SKUs. Nykaa is the closest analogue for what "getting faster" looks like operationally.

---

# Section 4 — Logistics Partner Landscape

## 4.1 Longlist (categorised)

| Player | Category | Speed tiers | Warehousing | Coverage | D2C fit | Conf. |
|---|---|---|---|---|---|---|
| **Delhivery** | Express national + FaaS + Rapid Commerce | economy→NDD→SDD→**sub-2hr** | 85 FCs, 158 processing, 20.1M sq ft (FY25) | ~18,850 pins; 31k+ ecom cust. | **High** | Confirmed (AR FY25) |
| **Ecom Express** (now Delhivery sub.) | Express national | SDD/SDD+/NDD (MFC-backed) | in-city MFCs | 27,000+ pins | Med-High | High |
| **XpressBees** | Express + D2C fulfilment | same-day 51 cities; NDD 1,000+ towns | own D2C stock pool | 20,000+ pins, 3M+ shpmts/day | High | Med (some data 2022) |
| **Blue Dart (DHL)** | Premium express | 1–2d time-definite | 85+ warehouses | 56,400+ locations | Med (premium price) | Med |
| **DTDC / Gati / Professional** | Express national | standard | franchise | 15,300–25,000 pins | Low-Med | Med |
| **Shadowfax** | Hyperlocal + express + QC | **30-min→same-day→next-day** | fulfilment offered | 2,500+ cities, 14k+ pins hyperlocal, 1M+ riders | **High** (SD/hyperlocal) | Med-High |
| **Porter / Loadshare** | Intracity/hyperlocal | intracity same-day | some warehousing | pan-India intracity | Med | Med |
| **Zippee** | Same-day QC-for-D2C (own site) | **60-min/120-min/same-day** | 125–150 dark stores | 21 cities; 150+ D2C brands | **High** | Med-High |
| **Blitz (ex-Grow Simplee)** | Same-day QC-for-D2C | 60-min/2-hr/same-day(3PM cutoff)/NDD | dark stores 7 cities | Blr, Del, Ggn, Noida, Mum, Hyd, Jaipur | **High** | Med |
| **Pidge** | Delivery OS (SaaS) | hyperlocal + national via 3PL | asset-light | 15k+ businesses | Med (tooling) | Med |
| **Shiprocket** | Aggregator + FaaS + QC | standard; same-day 5 metros; QC ~4h | fulfilment + dark stores | ~24–27k pins; ~35–40% D2C share | **High** | Med-High |
| **NimbusPost / iThink / Clickpost / Shyplite** | Aggregators | standard→NDD | some FCs (Nimbus 10) | 26k–29k pins | Med to Med-High | Med |
| **WareIQ** | FaaS / distributed warehousing | same/next-day | 20+ FCs, 13+ cities | 27,000+ pins; claims 99% OT | **High** | Med-High |
| **Eshopbox** | FaaS + aggregator | same/next-day | FCs in 5 cities | 29,000+ pins | **High** | Med-High |
| **Emiza / Holisol / Stockone** | FaaS (multi-client 3PL) | standard→MFC-fast | 27+ FCs (Emiza) | 12+ cities | Med-High | Med |
| **Increff / Unicommerce / Vinculum** | OMS/WMS software | enable routing/splitting | software only | omnichannel | Med-High (brain, not fleet) | Med |
| **Blinkit / Zepto / Instamart / Flipkart Minutes** | QC marketplaces | 10–30 min | their dark stores | metro-heavy | Med (channel, 15–25% commission) | Med |
| **ElasticRun** (current) | Rural e-B2B/kirana → pivoting to D2C QC | historically next-day rural; **claims** SD/30-min metro (new) | 1,000+ rural FCs; ~800 dark stores; ~150 QC-format | 22 states, 600+ towns, ~60% pins (rural-weighted) | **Low-Med for metro D2C express** | Med |
| Dunzo | Hyperlocal | — | — | **Shut down Jan 2025** | N/A | High |
| ShipBob | Global FaaS | regional 2-day (US/EU) | global FCs | weak India | Low (India) | Low |

## 4.2 Shortlist — 7 strongest candidates for a fast-SLA accessories D2C

Each separates **Advertised → Network → Evidence of SLA delivery.**

1. **Delhivery (HIGH)** — Best single national partner. Largest FC footprint (85 FCs / 20.1M sq ft), pan-India ~18,850 pins, full FaaS + reverse + COD + mature APIs. **Rapid Commerce (sub-2-hr)** explicitly targets *electronics & accessories* — directly relevant — live in Bengaluru/Hyderabad/Chennai, expanding. Now also **owns Ecom Express (99.4%)**. *Evidence:* national SD/ND is proven; Rapid Commerce is **real but small/early** (~₹80–100 Cr FY25 revenue, low hundreds of orders/day at launch).
2. **Shiprocket (HIGH)** — Best **orchestration/aggregation** layer: one API over 40+ couriers, no volume minimums, plus fulfilment and a nascent same-day/QC layer (5 metros). *Evidence:* huge proven parcel throughput (~$3.5B GMV, ~35–40% D2C share); owns little physical last-mile so speed derives from underlying carriers; QC still nascent.
3. **WareIQ (HIGH)** — Best **distributed-inventory FaaS** to convert metro orders to next/same-day without capex: 20+ FCs across 13+ cities, 27,000+ pins, claims 99% on-time. *Evidence:* FC/city counts corroborated by third-party 3PL profiles; on-time figure self-reported.
4. **Eshopbox (HIGH)** — Distributed FCs (5 cities) + multi-courier shipping; strong for lifestyle/home D2C; claims up to 45% shipping-cost cut. *Evidence:* self-reported speed/cost, structurally sound.
5. **Shadowfax (HIGH for same-day/hyperlocal)** — Genuine large crowdsourced fleet (1M+ riders, 14k+ hyperlocal pins), ~6 lakh QC orders/day. *Evidence:* the **most independently substantiated** fast-SLA execution among pure last-mile players (earnings-backed volumes).
6. **XpressBees / Ecom Express same-day (HIGH/MED)** — Additional national SD/ND capacity + dedicated D2C platforms; deep Tier-2/3 reach (Ecom). *Caveat:* XpressBees same-day city counts trace to 2022 — **re-verify**; Ecom under Delhivery-integration uncertainty.
7. **Same-day D2C specialists — Zippee & Blitz (HIGH, small footprint)** — Purpose-built to give **60-min-to-same-day on a brand's OWN website** via their dark stores. Zippee 125–150 dark stores/21 cities/150+ brands; Blitz 7 cities. *Evidence:* capability real but **early-stage and geographically limited**.

**Not shortlisted but useful:** Blue Dart (premium 1–2d, most expensive, light on FaaS/QC); OMS/WMS software (Increff/Unicommerce — the routing "brain," needed alongside any physical partner); QC platforms (a channel, not own-site logistics).

---

# Section 5 — ElasticRun Competitive Benchmark

## 5.1 What ElasticRun actually is (critical to the whole exercise)

**ElasticRun is a rural / semi-urban e-B2B distribution & kirana-network logistics company**, not a metro D2C last-mile express courier. It connects FMCG/consumer brands to **~12 lakh (1.2M) kirana stores** across **19,000+ villages / 600+ towns / 22 states** (~60% of pincodes, **rural-weighted**), using an **asset-light crowdsourced** model (aggregating idle trucks/warehouses/people). SoftBank-backed unicorn (2022).

- **Financial context:** GMV/revenue roughly **halved** — FY24 revenue **₹2,434.8 Cr (−49%)**, net loss ₹359.6 Cr; FY25 revenue **₹2,653 Cr (+8%)**, loss narrowed ~60% to **₹145 Cr**. Bulk of revenue is still **traded FMCG goods** (₹2,172 Cr FY25); services only ~₹477 Cr. It is **retrenching to core** while trying to stand up a capital-intensive D2C/QC dark-store layer.
- **The D2C/QC pivot (2025–26):** reportedly ~800–850 dark stores + ~150 QC-format stores across ~95 cities, **claiming** same-day/30-min/10-min for D2C brands and a Shipway (Unicommerce) same/next-day partnership. **This is announcement-stage/advertised, not independently evidenced at metro-D2C-express scale.**

**Implication:** if DailyObjects uses ElasticRun today, it is most plausibly leveraging (a) **rural/Tier-2-3 distribution reach**, or (b) the **new, unproven QC pilot** — *not* a mature metro parcel-express network. This must be confirmed in Phase 2 by looking at *what ElasticRun actually does for our orders and where.*

## 5.2 Scorecard (out of 5) — ElasticRun vs 6 alternatives

Scores reflect **capability for fast METRO D2C parcel delivery for a broad-catalogue accessories brand** (not general logistics strength). ⚠️ = advertised/early, not yet performance-proven.

| Dimension | ElasticRun | Delhivery | Shiprocket | WareIQ | Eshopbox | Shadowfax | XpressBees |
|---|---|---|---|---|---|---|---|
| Delivery speed (metro) | 2 | 4 | 4 | 4 | 4 | 4 | 4 |
| Same-day capability | 2 ⚠️ | 4 (Rapid, early) | 3 (5 metros) | 4 | 3 | **5** | 3 ⚠️ |
| Next-day capability | 3 | **5** | 4 | 4 | 4 | 4 | 4 |
| Geographic coverage | 4 (rural-heavy) | **5** | 5 (via carriers) | 4 | 4 | 4 | 4 |
| Metro performance | 2 | **5** | 4 | 4 | 4 | **5** | 4 |
| Tier-1/Tier-2 coverage | 4 | **5** | 4 | 3 | 3 | 4 | 4 |
| Rural / deep Tier-3 reach | **5** | 4 | 3 | 2 | 2 | 3 | 4 (Ecom 5) |
| Warehousing network | 3 (rural FCs) | **5** | 3 | 4 | 4 | 2 | 3 |
| Distributed-inventory capability | 2 | 4 | 3 | **5** | **5** | 2 | 3 |
| Hyperlocal capability | 2 ⚠️ | 3 | 3 | 2 | 2 | **5** | 2 |
| Technology / API integration | 2 | 4 | **5** | **5** | **5** | 3 | 3 |
| Reverse logistics | 3 | **5** | 4 | 4 | 4 | 4 | 4 |
| COD support | 4 | **5** | **5** | 4 | 4 | 4 | 4 |
| Scalability | 3 | **5** | **5** | 4 | 4 | 4 | 4 |
| D2C suitability (metro) | 2 | **5** | **5** | **5** | 4 | 4 | 4 |
| Cost transparency/structure | 2 (opaque) | 3 | **5** (self-serve slabs) | 3 | 3 | 3 | 4 |
| Proof points / evidence quality | 2 (D2C unproven) | **5** (filings) | 4 | 3 | 3 | 4 (earnings) | 3 (dated) |

**Advantages of ElasticRun vs alternatives:** unmatched **rural/deep Tier-3-4 distribution reach**; asset-light; existing relationship. **Disadvantages:** weak/unproven for **fast metro D2C parcel**, opaque cost, financial strain, D2C/QC capability nascent and mostly advertised, thinner metro last-mile density and tech/API maturity than Delhivery/Shiprocket/WareIQ.

**Verdict:** For **materially faster metro delivery**, ElasticRun is **not** the lever. It is worth retaining **only** if its rural/Tier-2-3 reach is strategically valuable to our order base, or as a *contractually SLA-verified* pilot of its emerging QC layer. This must be tested against our actual order geography in Phase 2 — **do not assume a switch fixes speed, and do not assume ElasticRun is the bottleneck until the data says so.**

**Caveat on the whole scorecard:** these mix **advertised** and **network** capability; several load-bearing numbers (XpressBees same-day cities, ElasticRun QC SLAs, all pricing) rest on secondary sources and must be validated via live provider docs / RFP responses before any decision.

---

# Section 6 — Implications for DailyObjects (framing Phase 2)

**No solution is proposed here — by design.** Phase 1 establishes that **delivery speed is set primarily by inventory architecture, secondarily by fulfilment execution, and only lastly by courier choice.** Phase 2 must therefore diagnose which of three problems DailyObjects actually has.

## 6.1 The three-problem diagnostic

1. **Courier problem** — *Can another last-mile/logistics partner move the parcel faster?* Fixable by partner. Levers: courier selection, cut-off time, first-mile pickup frequency, line-haul, last-mile density.
2. **Fulfilment problem** — *Can we pick, pack and hand over faster?* Fixable by our own ops/tech. Levers: pick-pack time, order-routing logic, handover time, cut-off alignment.
3. **Inventory-architecture problem** — *Is the stock simply too far from the customer for fast delivery to be physically possible?* Fixable only by changing our node network / stock placement. Levers: warehouse location, number of nodes, inventory placement, SKU assortment per node, in-stock availability.

The benchmark strongly suggests the fast brands solved **#3 first** (Nykaa 18→44 warehouses; Myntra/Flipkart dark stores; Amazon FBA placement), used **#2** as the enabler (Lenskart's automated Bhiwadi pick), and treated **#1** (courier) as necessary but not sufficient. **We cannot know which problem dominates for DailyObjects without our own data.**

## 6.2 Questions Phase 2 must answer (internal data to pull)

**Fulfilment / dispatch:**
- Current **order-to-dispatch SLA** (median + P90), by warehouse, by category/SKU.
- Current **dispatch-to-delivery SLA** (median + P90), by courier, by lane.
- **Pick-pack time** and **courier handover time**; **cut-off times** per courier and % of daily orders missing today's cut-off.
- First-mile **pickup frequency** per warehouse.

**Geography & inventory (the decisive lens):**
- **SLA by destination PIN code / city**, bucketed metro / Tier-1 / Tier-2 / Tier-3 / NE-J&K.
- **Order concentration by city** — what % of demand sits in the top 5–8 metros?
- **Inventory concentration** — how many warehouses/nodes today, and where?
- **% of orders deliverable next-day from *existing* inventory locations** (the single most important number — it tells us whether this is an inventory problem).
- **SKU assortment per node** and **in-stock rate** at the node nearest each order; **split-shipment rate**.

**Courier & cost:**
- **SLA by courier** (incl. ElasticRun) and **what ElasticRun actually does for our orders and where** (rural vs metro; parcel vs distribution).
- **RTO rate by delivery-speed bucket** (test the ≤2-day RTO dividend on our own data).
- Current **cost per shipment** by lane/courier, to baseline the economics of any faster model.

## 6.3 Closing question for Phase 2

> **What internal data should DailyObjects analyse in Phase 2 to determine which external operating model would work best?**

Concretely: overlay **(a) our order concentration by city** against **(b) our current inventory locations** to compute **the % of orders that are next-day-deliverable from where our stock sits today.**
- If that number is **high but our SLA is still slow** → it is a **courier/fulfilment problem** (fix cut-offs, handover, courier mix — e.g. Delhivery/Shiprocket/Shadowfax).
- If that number is **low** → it is an **inventory-architecture problem**, and no courier switch will fix it — we would need **regional FCs or a distributed-inventory 3PL (Model 5→7, e.g. WareIQ/Eshopbox/Delhivery FaaS)**, with **quick-commerce (Blinkit/Zepto/M-Now-type)** considered only as an *additional channel for hero SKUs.*

That single overlay — demand geography vs inventory geography — is the pivot on which the entire Phase 3 improvement plan should turn.

---

## Appendix — Source quality & key references

Confidence is capped at Medium/Medium-High for policy-derived and secondary-extracted claims (primary sites were egress-blocked). Highest-quality (Confirmed) sources include:
- **Delhivery FY25 Annual Report** (Aug 2025) — network figures — delhivery.com/uploads/2025/08/Annual_Report_FY25.pdf
- **Lenskart IPO notes** (Way2Wealth / Axis Capital, Oct 2025) — Bhiwadi automation, 58-city next-day
- **Amazon India** official Prime Day 2025 fulfilment releases — FC/sortation expansion
- **ElasticRun financials** — Entrackr (FY24), Inc42 & Business Standard (FY25)
Strong secondary (news/industry) sources: Inc42, Business Standard, TechCrunch, Medianama, YourStory, Indian Retailer, Forbes India, The Ken, Entrackr — for Myntra M-Now, Nykaa regionalisation, Flipkart Minutes, Shadowfax earnings, Snitch/NEWME/CaratLane launches. Provider capability figures (WareIQ, Eshopbox, XpressBees, Shiprocket, Zippee, Blitz) are largely **advertised/self-reported** and flagged as such.

**Single most important remediation before Phase 2 decisions:** run **live checkout PIN-code delivery-promise checks** for the priority brands (and DailyObjects itself) across Delhi-NCR, Mumbai, Bengaluru, Hyderabad, Chennai, Pune, Kolkata + 2 Tier-2 pincodes, from an environment with unrestricted browser access, to convert this benchmark's *stated policies* into *verified customer-facing promises.*
