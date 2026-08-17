#!/usr/bin/env python3
"""
Retention by cohort at monthly / quarterly / yearly grain.
Anchor T0 = 2025-07-31 (full forward year available to 2026-07-31).
Cohorts: O1 (new/1 order), O2, Power Users, Deal Seekers, Light Users, All 3+.
Metrics: cumulative return within 1 month / 1 quarter / 1 year, plus monthly
(M1..M12) and quarterly (Q1..Q4) return curves.
"""
import numpy as np, pandas as pd
SEG="analysis/seg"; T0=pd.Timestamp("2025-07-31")
en=pd.read_csv(f"{SEG}/orders_enriched.csv",dtype={"order_no":str})
en["date"]=pd.to_datetime(en["date"],errors="coerce")
en=en[(en["paid"]==1)&en["date"].notna()&en["identity"].notna()].copy(); en["identity"]=en["identity"].astype(int)
past=en[en["date"]<=T0]; fut=en[en["date"]>T0]
lc=past.groupby("identity").size().rename("n").reset_index()
lab=pd.read_csv(f"{SEG}/labels_dev.csv")   # Power/Deal/Light at T0
lc=lc.merge(lab,on="identity",how="left")
lc["cohort"]=np.where(lc["n"]==1,"O1 (new)",np.where(lc["n"]==2,"O2",lc["cohort"]))
# forward days per identity (min positive)
fut=fut.assign(dd=(fut["date"]-T0).dt.days)
firstback=fut.groupby("identity")["dd"].min()
lc["days_to_return"]=lc["identity"].map(firstback)
cohorts=["O1 (new)","O2","Power Users","Deal Seekers","Light Users"]
def rate(sub,win): return 100*(sub["days_to_return"]<=win).mean()
rows=[]
for c in cohorts+["ALL 3+"]:
    sub=lc[lc["n"]>=3] if c=="ALL 3+" else lc[lc["cohort"]==c]
    rows.append({"cohort":c,"users":len(sub),
                 "ret_1m":round(rate(sub,30),1),"ret_1q":round(rate(sub,90),1),"ret_1y":round(rate(sub,365),1)})
cum=pd.DataFrame(rows)
print("=== Cumulative return within 1 month / 1 quarter / 1 year (anchor 31-Jul-2025) ===")
print(cum.to_string(index=False))
cum.to_csv(f"{SEG}/retention_cumulative.csv",index=False)

# monthly M1..M12 (each 30-day window) and quarterly Q1..Q4 (90-day)
def period_curve(sub,step,n):
    # fraction ordering AT LEAST once within each period window (any order in (T0+(k-1)*step, T0+k*step])
    ids=set(sub["identity"]); f=fut[fut["identity"].isin(ids)]
    out=[]
    for k in range(1,n+1):
        lo,hi=(k-1)*step,k*step
        act=f[(f["dd"]>lo)&(f["dd"]<=hi)]["identity"].nunique()
        out.append(round(100*act/len(sub),1) if len(sub) else 0)
    return out
mrows=[]; qrows=[]
for c in cohorts+["ALL 3+"]:
    sub=lc[lc["n"]>=3] if c=="ALL 3+" else lc[lc["cohort"]==c]
    mrows.append([c]+period_curve(sub,30,12)); qrows.append([c]+period_curve(sub,90,4))
mdf=pd.DataFrame(mrows,columns=["cohort"]+[f"M{i}" for i in range(1,13)])
qdf=pd.DataFrame(qrows,columns=["cohort"]+[f"Q{i}" for i in range(1,5)])
print("\n=== Monthly return rate (% ordering in each 30-day window) ==="); print(mdf.to_string(index=False))
print("\n=== Quarterly return rate (% ordering in each 90-day window) ==="); print(qdf.to_string(index=False))
mdf.to_csv(f"{SEG}/retention_monthly.csv",index=False); qdf.to_csv(f"{SEG}/retention_quarterly.csv",index=False)

# chart
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter
COL={"O1 (new)":"#94a3b8","O2":"#0e7490","Power Users":"#16a34a","Deal Seekers":"#c2560f","Light Users":"#7c3aed","ALL 3+":"#2563eb"}
fig,(a1,a2)=plt.subplots(1,2,figsize=(14,5),gridspec_kw={"wspace":0.28})
for c in cohorts:
    a1.plot(range(1,13),mdf[mdf.cohort==c].iloc[0,1:].values,marker="o",ms=3,color=COL[c],label=c)
a1.set_xlabel("Months after 31-Jul-2025");a1.set_ylabel("% ordering that month");a1.yaxis.set_major_formatter(PercentFormatter())
a1.set_title("Monthly return rate by cohort",fontsize=12,weight="bold",loc="left");a1.legend(frameon=False,fontsize=9)
x=np.arange(len(cohorts));w=0.26
for j,(lab_,col_) in enumerate([("ret_1m","#16a34a"),("ret_1q","#2563eb"),("ret_1y","#c2560f")]):
    vals=[cum[cum.cohort==c][lab_].iloc[0] for c in cohorts]
    a2.bar(x+(j-1)*w,vals,w,label={"ret_1m":"1 month","ret_1q":"1 quarter","ret_1y":"1 year"}[lab_],color=col_)
a2.set_xticks(x);a2.set_xticklabels([c.split(" ")[0] for c in cohorts],fontsize=9);a2.yaxis.set_major_formatter(PercentFormatter())
a2.set_title("Cumulative return: within 1 month / quarter / year",fontsize=12,weight="bold",loc="left");a2.legend(frameon=False,fontsize=9)
fig.savefig(f"{SEG}/retention_curves.png",dpi=150,bbox_inches="tight",facecolor="white")
print("\nsaved retention_curves.png")
