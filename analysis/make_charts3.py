#!/usr/bin/env python3
import numpy as np, pandas as pd, re
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter
SEG="analysis/seg"
prod=pd.read_csv(f"{SEG}/profile_3cohort_prod.csv",index_col=0)
dev=pd.read_csv(f"{SEG}/profile_3cohort_dev.csv",index_col=0)
order=["Power Users","Deal Seekers","Light Users"]
prod=prod.reindex(order); dev=dev.reindex(order)
COL={"Power Users":"#16a34a","Deal Seekers":"#c2560f","Light Users":"#64748b"}
cols=[COL[c] for c in order]
plt.rcParams.update({"font.size":11,"font.family":"DejaVu Sans","axes.spines.top":False,"axes.spines.right":False})

# ---- FIG 1: cohorts ----
fig,axs=plt.subplots(1,3,figsize=(15,4.8),gridspec_kw={"wspace":0.42})
y=np.arange(3); ret=dev["retained"].values*100
axs[0].barh(y,ret,color=cols,height=0.6)
for i,v in enumerate(ret):axs[0].text(v+0.7,i,f"{v:.0f}%",va="center",weight="bold")
axs[0].set_yticks(y);axs[0].set_yticklabels(order);axs[0].invert_yaxis();axs[0].set_xlim(0,58)
axs[0].xaxis.set_major_formatter(PercentFormatter());axs[0].set_title("Forward 12-mo retention\n(hold-out validation)",fontsize=12,weight="bold",loc="left")
sz=prod["users"].values
axs[1].bar(y,sz/1000,color=cols,width=0.62)
for i,v in enumerate(sz):axs[1].text(i,v/1000+1,f"{v/1000:.0f}k\n{prod['pct'].values[i]:.0f}%",ha="center",fontsize=9)
axs[1].set_xticks(y);axs[1].set_xticklabels([c.split(" ")[0] for c in order]);axs[1].set_ylabel("Customers (000s)");axs[1].set_ylim(0,95)
axs[1].set_title("Cohort sizes\n(203,281 mature, 3+ orders)",fontsize=12,weight="bold",loc="left")
w=0.38
axs[2].bar(y-w/2,prod["pct_disc"].values*100,w,color=cols,label="% orders discounted")
axs[2].bar(y+w/2,prod["event_share"].values*100,w,color=cols,alpha=0.5,label="% via price-led events")
for i in range(3):
    axs[2].text(i-w/2,prod["pct_disc"].values[i]*100+1,f"{prod['pct_disc'].values[i]*100:.0f}",ha="center",fontsize=8)
    axs[2].text(i+w/2,prod["event_share"].values[i]*100+1,f"{prod['event_share'].values[i]*100:.0f}",ha="center",fontsize=8)
axs[2].set_xticks(y);axs[2].set_xticklabels([c.split(" ")[0] for c in order]);axs[2].set_ylim(0,95)
axs[2].yaxis.set_major_formatter(PercentFormatter());axs[2].legend(frameon=False,fontsize=8.5,loc="upper right")
axs[2].set_title("Discount reliance (enriched)\ncoupon + price-led events",fontsize=12,weight="bold",loc="left")
fig.savefig(f"{SEG}/cohorts_chart.png",dpi=150,bbox_inches="tight",facecolor="white");print("saved cohorts_chart.png")

# ---- FIG 2: 2025 event windows ----
o=pd.read_csv(f"{SEG}/orders_resolved.csv",dtype={"order_no":str}); o["date"]=pd.to_datetime(o["date"],errors="coerce")
oc=pd.read_csv(f"{SEG}/ordercat_resolved.csv",dtype={"order_no":str}).merge(o[["order_no","date"]],on="order_no")
oc=oc[(oc["date"]>=pd.Timestamp("2025-01-01"))&(oc["date"]<=pd.Timestamp("2025-12-31"))]
oc["pos"]=oc["cat_gmv"].clip(lower=0);oc["wk"]=oc["date"].dt.isocalendar().week.astype(int)
wk=oc.groupby("wk").apply(lambda x:x.pos.sum()/x.cat_qty.clip(lower=0).sum(),include_groups=False)
med=wk.median()
fig2,ax=plt.subplots(figsize=(13,4.2))
ax.plot(wk.index,wk.values,color="#2563eb",lw=2,marker="o",ms=3)
ax.axhline(med,color="#94a3b8",ls="--",lw=1);ax.text(52,med+8,f"BAU median ₹{med:.0f}",color="#64748b",ha="right",fontsize=9)
events={"Republic":(3,5),"HPS March":(12,14),"HPS Aug/Sep":(35,39),"Diwali":(42,43),"Black Fri/Nov":(46,47),"Year-end":(50,52)}
ax.set_ylim(wk.min()*0.93, wk.max()*1.03)
for nm,(a,b) in events.items():
    ax.axvspan(a-0.5,b+0.5,color="#c2560f",alpha=0.12)
    ax.text((a+b)/2,wk.min()*0.955,nm,ha="center",fontsize=8,color="#c2560f")
ax.set_xlabel("2025 ISO week");ax.set_ylabel("Weekly ASP (₹)");ax.set_xlim(0,53)
ax.set_title("Price-led discount events detected from DMR ASP dips — 2025 (validated vs elasticity sheet)",fontsize=12,weight="bold",loc="left")
fig2.savefig(f"{SEG}/events_2025.png",dpi=150,bbox_inches="tight",facecolor="white");print("saved events_2025.png")
