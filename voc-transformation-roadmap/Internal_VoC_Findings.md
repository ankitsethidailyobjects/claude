# DailyObjects — Internal VoC Findings (locked numbers)

## Data assets
- Reviews Master: 80,303 valid reviews (rating 1-5), Aug'21–Apr'26, 11,771 SKUs, 28,534 with text. Mean rating 3.38, 28.9% one-star.
- Returns raw: 78,947 return/replacement rows, effective window Mar'25–Mar'26. 63,511 refund-Returns + 15,436 Replacements (brand-wide warranty-swap share = 19.6% ≈ 20%).
- Mar-Jun reviews file: 728 recent rows (subset, corroborates).
- **CRITICAL LIMITATION: no sales/units column exists in any sheet → a true return rate (returns ÷ units sold) CANNOT be computed. No figure here is one.** Rank by absolute return VOLUME (valid count) + WARRANTY-SWAP SHARE = replacements ÷ (returns+replacements) for a SKU/category (a composition of returned units vs the ~20% baseline; a defect-intensity signal, NOT a return rate).

## Rating deterioration trend (created month)
- 2024 H1 ~3.6 avg, 23-27% 1★ → 2025 H2 3.23-3.26 avg, 30-32% 1★ → 2026 Apr 3.03 avg, 39% 1★.
- Clear structural decline in perceived quality, accelerating Sep'25–Nov'25 and Apr'26.

## Category cross-reference (returns vol vs review avg)
| Category | Returns | Rev n | Avg | 1★% | Read |
|---|---|---|---|---|---|
| Phone Cases | 21,414 | 11,067 | 3.32 | 30% | durability (yellowing/crack/MagSafe ring), fit |
| Apple Watch Bands | 15,088 | 14,071 | 3.10 | 33% | SIZE/FIT + Solo Loop fixed-size + quality + colour |
| Bags | 11,675 | 9,257 | 3.81 | 19% | LOVED but returned on SIZE/EXPECTATION (not defect) |
| Chargers & Charging | 5,472 | 4,813 | 3.53 | 27% | reliability |
| Wallets & Card Holders | 3,961 | 4,178 | 3.43 | 28% | ergonomics, quality |
| Power Banks | 3,750 | 4,217 | 3.08 | 34% | RELIABILITY CRISIS |
| Screen Protectors | 3,328 | 5,767 | 3.12 | 36% | Apple Watch glass 2.17 avg — product failure |
| Laptop Sleeves & Folios | 2,966 | 1,808 | 3.70 | 22% | model-fit/size |
| AirPods Cases | 2,059 | 1,282 | 2.62 | 50% | WORST — quality/fit/durability |
| Stands & Mounts | 1,994 | 648 | 3.24 | 33% | SILENT (few reviews); Stack ergonomics |
| Cables | 1,664 | 1,987 | 3.44 | 27% | SURGE fraying/reliability |
| Keychains & Lanyards | 1,551 | 806 | 3.41 | 27% | finish (Universal Lanyard Link) |

## CHARGING ECOSYSTEM = HIGHEST DEFECT INTENSITY (not highest volume)
NOTE: all %s below are WARRANTY-SWAP SHARE (replacements ÷ returned units), vs a 20% brand baseline — NOT return rates. Charging is only ~12% of all returns by VOLUME (Power Banks 4.8%, Chargers 6.9%, Cables ~2%); the big VOLUME drivers are Cases 27%, Bands 19%, Bags 15%. Charging's severity is defect-INTENSITY + bad reviews + external corroboration.
- Power Banks + Chargers + Cables: 10,886 returned units, 47% warranty-swap (5,079 replacements vs 5,807 refunds).
- Loop power bank variants: 3,684 returned units, 69% warranty-swap.
- Loop Qi2 MagSafe power bank variants: 71-89% warranty-swap each (across 968, 493, 375, 323, 284, 244 returned units).
- SURGE Kevlar 4-in-1 100W cable: 493 returned units, 76% swap; SURGE 2-in-1: 225 @88%; SURGE 2-in-1 review avg 2.24.
- POP 67W Triple Port GaN Desk Adapter (Blue/Black/White): 79-90% warranty-swap.
- SURGE 3-Port 67W GaN: 147 @80%. SURGE Max Foldaway 3-in-1: 90 @84%.
- Neg review themes: charging/heat/weak-magnet/not-charging/slow (152 mentions power banks).
- Reason coded "as per CX request" masks true defect nature → shows up as warranty swaps.
- Trend: 40-58% warranty-swap share all year; Feb'26 peak 58%. Structural, not one batch.

## SKU-level failure list
- Tempered Glass Apple Watch Screen Protector (multiple variants): 1.70-2.18 avg, ~1,436 reviews avg 2.17. Adhesion/bubble on curved face, touch, size cut. #1 worst product.
- Solo Loop bands (Braided + silicone, all colours): 2,405 reviews, 2.56 avg, 47% 1★. Fixed-size fit failure (Olive 2.40/322, Blue 2.35/203, Red 2.30/111).
- Poppy Leather Link bands (Brown 2.47/306, Dark Cherry 2.36, Evergreen 2.30): leather/magnet.
- AirPods cases (Coast, Poncho, Leatherite, Leather Pro2): 2.1-2.5.
- Beam MagSafe iPhone case: 2.31; finish defects (18+10+9 "Bad Finishing" iPhone16 Pro/Max/16).
- Rose Gold Magnetic Milanese Loop: COLOUR MISMATCH #1 (135 + 38 = 173 "Color is Different").
- Stack Phone Wallet Stand / Grip & Stand family (Slate 2.35, Carbon, Tangerine): ERGONOMICS "uncomfortable" (92,45,43,35).
- Universal Lanyard Link: finish + ergonomics (63 uncomfortable, 19 bad finishing).
- Kelp Daily Duffle Bag: #1 returned bag (1,329); uncomfortable (128) + colour (50) + finish (19) — but bags category loved overall.

## Return root-cause mix (Mar'25+, n=78,591)
Unspecified/Blank 17,371 | Preference/Expectation 10,846 | CX-Initiated(ops) 10,634 | Size/Fit 9,293 | Ergonomics 4,846 | Material 4,106 | Content/PDP gap 3,685 | Buyer remorse 3,065 | Quality(perceived) 2,802 | Colour mismatch 2,736 | Functional defect 1,555 | Wrong item shipped 1,441 | Finish defect 1,378 | Durability/breakage 1,190 | Pricing/competitor 559 | Cosmetic damage 428 | Missing 314.

## Company-fault return share by category (defect+durability+finish+wrong+damage+missing)
AirPods 16.6% | Phone Cases 12.5% (2,669 units) | Keychains 11.3% | Screen Protectors 9.4% | Wallets 9.1% | Stands 7.7% | Watch Bands 6.6% | Cables 5.8% | Chargers 5.2% | Bags 4.1% | Power Banks 3.8% (but 69% of those returns are replacements = defect via warranty channel).

## What customers LOVE (5★ themes)
- Bags: design/look (267), quality (224), material (161) — DESIGN IS THE HERO.
- Phone Cases: protection (337), quality (303), design (205).
- Watch Bands: quality (260), fit (156), design (118).
- Chargers: quality (113), design (83) — loved WHEN they work.
- Cross-brand equity: premium DESIGN, aesthetics, materials, giftability, packaging.

## Strategic read
Brand superpower = DESIGN/AESTHETICS. Achilles heel = QUALITY/DURABILITY/RELIABILITY + SIZING/EXPECTATION-SETTING. The premium-design promise is outrunning quality delivery — and the gap is widening (rating decline). Electronics line (charging) is the acute reliability liability; bags/sleeves are a "content & sizing" fix (product is good); screen protectors & AirPods cases & Solo Loop are product-redesign/discontinue candidates.
