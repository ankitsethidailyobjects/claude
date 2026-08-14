#!/usr/bin/env python3
import numpy as np, pandas as pd
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter
SEG="analysis/seg"
dev=pd.read_csv(f"{SEG}/named_profile_dev.csv",index_col=0)
prod=pd.read_csv(f"{SEG}/named_profile_prod.csv",index_col=0)
order=["Fast-Rising Newcomers","Established Omnivores","Prepaid Mid-Value Regulars",
       "Full-Price Value Seekers","Deal-Seekers & Returners"]
dev=dev.reindex(order); prod=prod.reindex(order)
COL={"Fast-Rising Newcomers":"#16a34a","Established Omnivores":"#2563eb",
     "Prepaid Mid-Value Regulars":"#0e7490","Full-Price Value Seekers":"#7c3aed",
     "Deal-Seekers & Returners":"#c2560f"}
cols=[COL[c] for c in order]
plt.rcParams.update({"font.size":11,"font.family":"DejaVu Sans","axes.spines.top":False,"axes.spines.right":False})
fig,(ax1,ax2)=plt.subplots(1,2,figsize=(13,5.6),gridspec_kw={"wspace":0.42})

# Panel 1: forward 365d retention by cohort (validation, DEV)
y=np.arange(len(order))
ret=dev["retained_365d"].values*100
ax1.barh(y,ret,color=cols,height=0.66)
for i,v in enumerate(ret): ax1.text(v+0.6,i,f"{v:.0f}%",va="center",fontsize=10,weight="bold")
ax1.set_yticks(y); ax1.set_yticklabels([c.replace(" ","\n",1) for c in order],fontsize=9.5)
ax1.invert_yaxis(); ax1.set_xlim(0,55); ax1.xaxis.set_major_formatter(PercentFormatter())
ax1.set_xlabel("Forward 12-month retention")
ax1.set_title("Cohorts validate on FUTURE retention\n(hold-out: T₀=31 Jul 2025 → next 12 mo)",
              fontsize=12,weight="bold",loc="left")
ax1.axvline(32,color="#94a3b8",ls=":",lw=1); ax1.text(32,-0.7,"base 32%",color="#64748b",fontsize=8.5,ha="center")

# Panel 2: production cohort sizes + activity mix
prod_sizes=prod["users"].values
xt=np.arange(len(order))
ax2.bar(xt,prod_sizes/1000,color=cols,width=0.66)
for i,v in enumerate(prod_sizes): ax2.text(i,v/1000+1,f"{v/1000:.0f}k\n{prod['pct'].values[i]:.0f}%",ha="center",fontsize=8.5)
ax2.set_xticks(xt); ax2.set_xticklabels([c.split(" ")[0]+("…" if len(c.split(" "))>1 else "") for c in order],fontsize=9,rotation=0)
ax2.set_ylabel("Customers (000s)"); ax2.set_ylim(0,75)
ax2.set_title("Production base — 203,281 mature (3+) customers\nas of 31 Jul 2026",fontsize=12,weight="bold",loc="left")
fig.savefig(f"{SEG}/cohorts_chart.png",dpi=150,bbox_inches="tight",facecolor="white")
print("saved",f"{SEG}/cohorts_chart.png")
