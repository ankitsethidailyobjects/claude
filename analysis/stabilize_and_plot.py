#!/usr/bin/env python3
import sys, json
import numpy as np, pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter

OUT = "analysis/out"
t = pd.read_csv(f"{OUT}/buckets_paid.csv")
td = pd.read_csv(f"{OUT}/buckets_delivered.csv")

REL_MIN = 300  # min users for a bucket to be "reliable"
rel = t[t["users"] >= REL_MIN].copy().reset_index(drop=True)
maxrel = int(rel["orders"].max())
print(f"Reliable buckets (users>={REL_MIN}): orders 1..{maxrel}")

x = rel["orders"].values.astype(float)
y = rel["retention_pct"].values.astype(float)
inc = np.concatenate([[np.nan], np.diff(y)])
rel["incr_pp"] = inc
rel["incr_ma2"] = pd.Series(inc).rolling(2).mean().values
rel["rel_gain_%"] = np.concatenate([[np.nan], np.diff(y)/y[:-1]*100])

# ceiling estimate = mean retention of top reliable buckets (>=10 orders)
ceiling = y[x >= 10].mean()
rel["pct_of_ceiling"] = (y / ceiling * 100)

# Kneedle-style elbow on reliable concave curve
xn = (x - x.min())/(x.max()-x.min())
yn = (y - y.min())/(y.max()-y.min())
dist = yn - xn            # concave increasing: max positive dist = elbow
elbow = int(x[int(np.argmax(dist))])

# stabilization criteria
thr = 3.0  # pp
below = rel[(rel["orders"]>1) & (rel["incr_pp"] < thr)]
first_below = int(below["orders"].iloc[0]) if len(below) else None
# sustained: first order where incr_ma2 < thr and stays (within reliable range)
sustained = None
for i in range(2, len(rel)):
    if rel["incr_ma2"].iloc[i:].max() < thr:
        sustained = int(rel["orders"].iloc[i]); break

print("\n== Per-order detail (reliable range) ==")
print(rel[["orders","users","retention_pct","incr_pp","incr_ma2","rel_gain_%","pct_of_ceiling"]].round(2).to_string(index=False))
print(f"\nCeiling (mean retention, >=10 orders): {ceiling:.1f}%")
print(f"Kneedle elbow (max curvature): {elbow} orders")
print(f"First order with incremental < {thr}pp: {first_below}")
print(f"First order where remaining increments stay < {thr}pp (2-pt MA): {sustained}")
# where does curve reach 90% of ceiling
reach90 = int(x[np.argmax(y >= 0.9*ceiling)]) if (y >= 0.9*ceiling).any() else None
reach80 = int(x[np.argmax(y >= 0.8*ceiling)]) if (y >= 0.8*ceiling).any() else None
print(f"Reaches 80% of ceiling at: {reach80} orders; 90% at: {reach90} orders")

# ---------------- CHART ----------------
plt.rcParams.update({"font.size": 11, "font.family": "DejaVu Sans",
                     "axes.spines.top": False, "axes.spines.right": False})
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(11, 8.6), height_ratios=[2.3, 1],
                               gridspec_kw={"hspace": 0.28})
BLUE="#2563eb"; GREY="#94a3b8"; ORANGE="#ea580c"; GREEN="#16a34a"

# use full curve but shade unreliable tail
full = t.copy()
xf = full["orders"].values; yf = full["retention_pct"].values
ci = full["ci95_pp"].values

# sample-size bars (background, log scale on twin axis)
axb = ax1.twinx()
axb.bar(xf, full["users"].values, width=0.62, color="#e5e7eb", zorder=0)
axb.set_yscale("log"); axb.set_ylabel("Users in bucket (log)", color=GREY)
axb.tick_params(axis="y", colors=GREY); axb.set_ylim(1, full["users"].max()*3)
axb.spines["top"].set_visible(False)

# retention line + CI (reliable solid, tail dashed)
ax1.errorbar(x, y, yerr=rel["ci95_pp"].values, fmt="o-", color=BLUE, lw=2.4, ms=6,
             capsize=3, zorder=5, label="2025 retention % (95% CI)")
tail = full[full["orders"] > maxrel]
ax1.plot(tail["orders"], tail["retention_pct"], "o--", color=GREY, ms=4, lw=1.2,
         zorder=4, label=f"Sparse tail (<{REL_MIN} users)")
ax1.axvline(elbow, color=ORANGE, ls=":", lw=1.8, zorder=3)
ax1.annotate(f"Diminishing-returns elbow ≈ {elbow} orders", xy=(elbow, np.interp(elbow,x,y)),
             xytext=(elbow+1.2, 22), color=ORANGE, fontsize=10,
             arrowprops=dict(arrowstyle="->", color=ORANGE))
ax1.axhline(ceiling, color=GREEN, ls="--", lw=1.2, zorder=2)
ax1.text(19.5, ceiling+1.5, f"≈{ceiling:.0f}% plateau (10+ orders)", color=GREEN, ha="right", fontsize=10)
ax1.set_ylabel("2025 retention %"); ax1.set_ylim(0, 90)
ax1.yaxis.set_major_formatter(PercentFormatter())
ax1.set_xlim(0.3, 20.7); ax1.set_xticks(range(1,21))
ax1.set_title("DailyObjects — 2025 retention by lifetime order count as of 31 Dec 2024",
              fontsize=13, weight="bold", loc="left")
ax1.legend(loc="lower right", frameon=False, fontsize=9.5)
ax1.set_zorder(axb.get_zorder()+1); ax1.patch.set_visible(False)

# incremental panel
colors = [BLUE if v>=thr else GREY for v in rel["incr_pp"].fillna(0)]
ax2.bar(x, rel["incr_pp"].values, width=0.62, color=colors)
ax2.axhline(thr, color=ORANGE, ls=":", lw=1.5)
ax2.text(20.5, thr+0.3, f"{thr:.0f}pp threshold", color=ORANGE, ha="right", fontsize=9)
ax2.set_ylabel("Δ retention vs\nprevious bucket (pp)")
ax2.set_xlabel("Lifetime paid orders as of 31 Dec 2024")
ax2.set_xlim(0.3, 20.7); ax2.set_xticks(range(1,21)); ax2.set_ylim(0, 10)
for xi, vi in zip(x, rel["incr_pp"].values):
    if not np.isnan(vi): ax2.text(xi, vi+0.15, f"{vi:.1f}", ha="center", fontsize=7.5, color="#334155")

fig.savefig(f"{OUT}/retention_curve.png", dpi=150, bbox_inches="tight", facecolor="white")
print(f"\nSaved chart -> {OUT}/retention_curve.png")

# export a tidy summary
summ = {"ceiling_pct": round(float(ceiling),1), "elbow_orders": elbow,
        "first_below_3pp": first_below, "sustained_below_3pp": sustained,
        "reach80_ceiling": reach80, "reach90_ceiling": reach90,
        "reliable_max_bucket": maxrel}
json.dump(summ, open(f"{OUT}/stabilization.json","w"), indent=2)
print("STAB:", json.dumps(summ))
