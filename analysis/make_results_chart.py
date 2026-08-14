#!/usr/bin/env python3
import numpy as np, pandas as pd
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter
SEG="analysis/seg"
prod=pd.read_csv(f"{SEG}/cohort_profile_prod_v2.csv",index_col=0)
dev=pd.read_csv(f"{SEG}/cohort_profile_dev_v2.csv",index_col=0)
mp=pd.read_csv(f"{SEG}/prod_mapping_v2.csv")
order=["Power Users","Core Regulars","Full-Price Loyalists","Light Users","Deal Seekers"]
prod=prod.reindex(order); dev=dev.reindex(order)
COL={"Power Users":"#16a34a","Core Regulars":"#2563eb","Full-Price Loyalists":"#7c3aed",
     "Light Users":"#0e7490","Deal Seekers":"#c2560f"}
cols=[COL[c] for c in order]
plt.rcParams.update({"font.size":11,"font.family":"DejaVu Sans","axes.spines.top":False,"axes.spines.right":False})
fig,axs=plt.subplots(1,3,figsize=(15,5.2),gridspec_kw={"wspace":0.5})

# 1 forward retention (validation)
y=np.arange(len(order)); ret=dev["retained_365d"].values*100
axs[0].barh(y,ret,color=cols,height=0.66)
for i,v in enumerate(ret): axs[0].text(v+0.7,i,f"{v:.0f}%",va="center",fontsize=10,weight="bold")
axs[0].set_yticks(y); axs[0].set_yticklabels([c.replace(" ","\n",1) for c in order],fontsize=9)
axs[0].invert_yaxis(); axs[0].set_xlim(0,60); axs[0].xaxis.set_major_formatter(PercentFormatter())
axs[0].axvline(32,color="#94a3b8",ls=":",lw=1); axs[0].text(32,-0.72,"base 32%",color="#64748b",fontsize=8,ha="center")
axs[0].set_title("Validated on FUTURE retention\n(hold-out T₀=31 Jul 2025 → next 12 mo)",fontsize=11.5,weight="bold",loc="left")

# 2 sizes
x=np.arange(len(order)); sz=prod["users"].values
axs[1].bar(x,sz/1000,color=cols,width=0.66)
for i,v in enumerate(sz): axs[1].text(i,v/1000+0.6,f"{v/1000:.0f}k\n{prod['pct'].values[i]:.0f}%",ha="center",fontsize=8.5)
axs[1].set_xticks(x); axs[1].set_xticklabels([c.split(" ")[0] for c in order],fontsize=8.5)
axs[1].set_ylabel("Customers (000s)"); axs[1].set_ylim(0,68)
axs[1].set_title("Cohort sizes\n(203,281 mature, 31 Jul 2026)",fontsize=11.5,weight="bold",loc="left")

# 3 activity split stacked per cohort
ct=pd.crosstab(mp["behavioural_cohort"],mp["activity_state"]).reindex(order)[["Active","Lapsed","Dormant"]]
ctp=ct.div(ct.sum(1),axis=0)*100
ACOL={"Active":"#16a34a","Lapsed":"#eab308","Dormant":"#94a3b8"}
bottom=np.zeros(len(order))
for st in ["Active","Lapsed","Dormant"]:
    axs[2].bar(x,ctp[st].values,bottom=bottom,color=ACOL[st],width=0.66,label=st)
    bottom+=ctp[st].values
axs[2].set_xticks(x); axs[2].set_xticklabels([c.split(" ")[0] for c in order],fontsize=8.5)
axs[2].set_ylabel("% of cohort"); axs[2].set_ylim(0,100); axs[2].yaxis.set_major_formatter(PercentFormatter())
axs[2].legend(frameon=False,fontsize=8.5,loc="lower center",ncol=3,bbox_to_anchor=(0.5,-0.22))
axs[2].set_title("Activity overlay per cohort\n(Active ≤90d · Lapsed 90–270 · Dormant >270)",fontsize=11.5,weight="bold",loc="left")
fig.savefig(f"{SEG}/cohorts_chart.png",dpi=150,bbox_inches="tight",facecolor="white")
print("saved cohorts_chart.png")
