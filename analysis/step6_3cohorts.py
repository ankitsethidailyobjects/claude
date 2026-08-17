#!/usr/bin/env python3
"""
3-cohort segmentation (Power Users / Deal Seekers / Light Users) on ALL 3+
order customers, using the ENRICHED discount signal (coupon + price-led events).
Category-affinity SCORES (tech/bags spend shares) assigned on top.
K-Means k=3; validated on hold-out forward retention.
Usage: step6_3cohorts.py
"""
import re
import numpy as np, pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
SEG="analysis/seg"; RS=42

def macro(c):
    c=str(c).lower()
    if re.search(r"bag|backpack|wallet|pouch|travel|duffle|luggage|sling|tote",c): return "bags"
    if re.search(r"case|sleeve|accessor|charg|screen|guard|protection|mobile|watch|home office|tablet|station|grip|lanyard|stand|keychain|organis|airtag|airpod|desk|adapter|power",c): return "tech"
    return "other"

en=pd.read_csv(f"{SEG}/orders_enriched.csv",dtype={"order_no":str})
en["date"]=pd.to_datetime(en["date"],errors="coerce")
en=en[(en["paid"]==1)&en["date"].notna()&en["identity"].notna()].copy()
en["identity"]=en["identity"].astype(int)
o=pd.read_csv(f"{SEG}/orders_resolved.csv",dtype={"order_no":str})
oc=pd.read_csv(f"{SEG}/ordercat_resolved.csv",dtype={"order_no":str})
oc["identity"]=oc["identity"].astype(int)
odate=dict(zip(o["order_no"],pd.to_datetime(o["date"],errors="coerce")))
oc["date"]=oc["order_no"].map(odate); oc["macro"]=oc["category"].map(macro); oc["pos"]=oc["cat_gmv"].clip(lower=0)

def snapshot(T0,fut_days):
    T0=pd.Timestamp(T0)
    past=en[en["date"]<=T0]
    fut=en[(en["date"]>T0)&(en["date"]<=T0+pd.Timedelta(days=fut_days))]
    g=past.groupby("identity")
    f=g.agg(lifetime_orders=("order_no","size"),first=("date","min"),last=("date","max"),
            gmv=("gmv","sum"),qty=("order_qty","sum"),
            pct_disc=("discounted_any","mean"),eff_disc=("effective_discount","mean"),
            event_share=("price_discounted","mean")).reset_index()
    f["tenure"]=(T0-f["first"]).dt.days.clip(lower=1)
    f["days_since_last"]=(T0-f["last"]).dt.days
    f["freq_yr"]=f["lifetime_orders"]/(f["tenure"]/365.0)
    f["aov"]=(f["gmv"]/f["lifetime_orders"]).clip(lower=0)
    f=f[f["lifetime_orders"]>=3].copy()
    # category affinity scores as-of T0
    ocp=oc[(oc["date"].notna())&(oc["date"]<=T0)]
    piv=ocp.pivot_table(index="identity",columns="macro",values="pos",aggfunc="sum",fill_value=0)
    for c in ["tech","bags","other"]:
        if c not in piv: piv[c]=0.0
    tb=(piv["tech"]+piv["bags"]).replace(0,np.nan)
    piv["tech_score"]=(piv["tech"]/tb).round(3); piv["bags_score"]=(piv["bags"]/tb).round(3)
    f=f.merge(piv[["tech_score","bags_score"]],on="identity",how="left")
    # forward retention
    fr=fut.groupby("identity").size()
    f["retained"]=f["identity"].map(lambda i:int(fr.get(i,0)>0))
    return f

def cluster3(f):
    X=pd.DataFrame({
        "freq":np.log1p(f["lifetime_orders"]),
        "freq_yr":np.log1p(f["freq_yr"].clip(0,52)),
        "gmv":np.log1p(f["gmv"].clip(lower=0)),
        "aov":np.log1p(f["aov"]),
        "disc":f["pct_disc"],
        "effdisc":f["eff_disc"],
    })
    for c in X:
        lo,hi=X[c].quantile([0.01,0.99]); X[c]=X[c].clip(lo,hi)
    Xs=StandardScaler().fit_transform(X.fillna(0))
    km=KMeans(n_clusters=3,n_init=25,random_state=RS).fit(Xs)
    f=f.copy(); f["cl"]=km.labels_
    sil=silhouette_score(Xs[np.random.RandomState(RS).choice(len(Xs),min(20000,len(Xs)),replace=False)],
                         km.labels_[np.random.RandomState(RS).choice(len(Xs),min(20000,len(Xs)),replace=False)]) if len(Xs)>1000 else np.nan
    # name: highest discount = Deal Seekers; of rest, higher freq*gmv = Power, other = Light
    prof=f.groupby("cl").agg(disc=("pct_disc","mean"),freq=("lifetime_orders","mean"),gmv=("gmv","median"))
    deal=prof["disc"].idxmax(); rest=[c for c in prof.index if c!=deal]
    power=max(rest,key=lambda c:prof.loc[c,"freq"]*prof.loc[c,"gmv"]); light=[c for c in rest if c!=power][0]
    nm={deal:"Deal Seekers",power:"Power Users",light:"Light Users"}
    f["cohort"]=f["cl"].map(nm)
    return f,sil

def profile(f):
    a=f.groupby("cohort").agg(users=("identity","size"),avg_orders=("lifetime_orders","mean"),
        med_gmv=("gmv","median"),aov=("aov","median"),pct_disc=("pct_disc","mean"),
        eff_disc=("eff_disc","mean"),event_share=("event_share","mean"),
        med_recency=("days_since_last","median"),tech_score=("tech_score","mean"),
        retained=("retained","mean"))
    a["pct"]=(100*a["users"]/len(f)).round(1)
    return a.reindex(["Power Users","Deal Seekers","Light Users"]).round(3)

prod=snapshot("2026-07-31",1); dev=snapshot("2025-07-31",365)
pf,sp=cluster3(prod); df_,sd=cluster3(dev)
print(f"PROD mature={len(prod):,} silhouette={sp:.3f}")
print("=== PROD 3-cohort profile (31 Jul 2026) ===")
print(profile(pf).to_string())
print(f"\nDEV mature={len(dev):,} silhouette={sd:.3f}")
print("=== DEV validation — forward 12-mo retention ===")
print(profile(df_)[["users","pct","retained","pct_disc","eff_disc","avg_orders","aov"]].to_string())

# save prod mapping
g=pf["gmv"].clip(lower=0); q=g.quantile([0.3,0.7,0.9])
pf["value_tier"]=np.select([g>=q[0.9],g>=q[0.7],g>=q[0.3]],["VIP","High","Mid"],default="Low")
pf["cat_affinity"]=np.select([pf["tech_score"]>=0.7,pf["tech_score"]<=0.3],["Tech","Designer/Bags"],default="Mixed")
pf["activity_state"]=pd.cut(pf["days_since_last"],[-1,90,270,10**9],labels=["Active","Lapsed","Dormant"])
pf[["identity","cohort","cat_affinity","tech_score","bags_score","value_tier","activity_state",
    "lifetime_orders","gmv","aov","pct_disc","eff_disc","event_share","days_since_last"]].to_csv(f"{SEG}/mapping_3cohort.csv",index=False)
profile(pf).to_csv(f"{SEG}/profile_3cohort_prod.csv"); profile(df_).to_csv(f"{SEG}/profile_3cohort_dev.csv")
pf[["identity","cohort"]].to_csv(f"{SEG}/labels_prod.csv",index=False)
df_[["identity","cohort"]].to_csv(f"{SEG}/labels_dev.csv",index=False)
print("\n=== category affinity (PROD) ==="); print(pf["cat_affinity"].value_counts().to_string())
print("\n=== cohort x affinity (PROD) ==="); print(pd.crosstab(pf["cohort"],pf["cat_affinity"]).reindex(["Power Users","Deal Seekers","Light Users"]).to_string())
print("wrote mapping_3cohort.csv")
