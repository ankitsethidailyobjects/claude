#!/usr/bin/env python3
"""
Actionable cohort redo:
  Lifecycle slab (1 / 2 / 3+)  ->  [3+] Behavioural cohort (rules, named)
  + Category affinity layer (Tech vs Designer/Bags vs Mixed)
  + Activity layer (Active / Lapsed / Dormant)   <- overlays, not cohorts
Validates behavioural cohorts on held-out forward retention (dev snapshot).
"""
import os, re
import numpy as np, pandas as pd
SEG="analysis/seg"

# ---------- category macro mapping ----------
def macro(cat):
    c=str(cat).lower()
    if re.search(r"bag|backpack|wallet|pouch|travel|duffle|luggage|sling|tote",c): return "bags"
    if re.search(r"case|sleeve|accessor|charg|screen|guard|protection|mobile|watch|"
                 r"home office|tablet|station|grip|lanyard|stand|keychain|organis|airtag|airpod|desk|adapter|power",c): return "tech"
    return "other"

# ---------- behavioural cohort rules (mutually exclusive, priority) ----------
def cohort(row):
    n=row["lifetime_orders"]; disc=row["pct_discounted"]
    if n>=6 and disc<0.65:            return "Power Users"
    if disc>=0.65:                     return "Deal Seekers"
    if disc<=0.20:                     return "Full-Price Loyalists"
    if n>=4:                           return "Core Regulars"
    return "Light Users"

def activity(days):
    if days<=90:  return "Active"
    if days<=270: return "Lapsed"
    return "Dormant"

def affinity(tech,bags):
    t=max(tech,0); b=max(bags,0); s=t+b
    if s<=0: return "No Tech/Bags"
    r=t/s
    if r>=0.70: return "Tech"
    if r<=0.30: return "Designer/Bags"
    return "Mixed"

def build(suf,T0):
    T0=pd.Timestamp(T0)
    m=pd.read_csv(f"{SEG}/userfeat_{suf}.csv")
    # category affinity as-of T0
    o=pd.read_csv(f"{SEG}/orders_resolved.csv",dtype={"order_no":str})
    o["date"]=pd.to_datetime(o["date"],errors="coerce")
    odate=dict(zip(o["order_no"],o["date"]))
    oc=pd.read_csv(f"{SEG}/ordercat_resolved.csv",dtype={"order_no":str})
    oc["date"]=oc["order_no"].map(odate)
    oc=oc[(oc["date"].notna())&(oc["date"]<=T0)].copy()
    oc["macro"]=oc["category"].map(macro)
    oc["pos_gmv"]=oc["cat_gmv"].clip(lower=0)
    piv=oc.pivot_table(index="identity",columns="macro",values="pos_gmv",aggfunc="sum",fill_value=0)
    for col in ["tech","bags"]:
        if col not in piv: piv[col]=0.0
    piv["cat_affinity"]=[affinity(t,b) for t,b in zip(piv["tech"],piv["bags"])]
    piv["tech_share"]=(piv["tech"]/(piv["tech"]+piv["bags"]).replace(0,np.nan)).round(3)
    m=m.merge(piv[["cat_affinity","tech_share"]],on="identity",how="left")
    m["cat_affinity"]=m["cat_affinity"].fillna("No Tech/Bags")
    # cohort + activity
    m["behavioural_cohort"]=m.apply(cohort,axis=1)
    # whales override
    m.loc[(m["lifetime_orders"]>=50)|(m["avg_qty"]>=10),"behavioural_cohort"]="Wholesale / B2B"
    m["activity_state"]=m["days_since_last"].apply(activity)
    return m

order=["Power Users","Core Regulars","Full-Price Loyalists","Light Users","Deal Seekers","Wholesale / B2B"]
def profile(m):
    a=m.groupby("behavioural_cohort").agg(
        users=("identity","size"),
        avg_orders=("lifetime_orders","mean"),
        med_gmv=("lifetime_gmv","median"),
        aov=("aov_life","median"),
        pct_discounted=("pct_discounted","mean"),
        med_recency=("days_since_last","median"),
        n_categories=("n_categories","mean"),
    )
    a["pct"]=(100*a["users"]/len(m)).round(1)
    for c in ["retained_365d"]:
        if c in m.columns: a[c]=m.groupby("behavioural_cohort")[c].mean()
    return a.reindex([c for c in order if c in a.index]).round(2)

prod=build("prod","2026-07-31")
dev =build("dev","2025-07-31")

print("=== PROD behavioural cohort profile (as of 31-Jul-2026) ===")
print(profile(prod).to_string())
print("\n=== DEV validation — forward 12-mo retention by cohort ===")
pd_=profile(dev); print(pd_[["users","pct","retained_365d","aov","pct_discounted","avg_orders"]].to_string())
print("\n=== PROD category affinity (Tech vs Designer/Bags) ===")
print(prod["cat_affinity"].value_counts().to_string())
print("\n=== PROD activity overlay ===")
print(prod["activity_state"].value_counts().to_string())
print("\n=== cohort x affinity (PROD counts) ===")
print(pd.crosstab(prod["behavioural_cohort"],prod["cat_affinity"]).reindex([c for c in order if c in prod['behavioural_cohort'].unique()]).to_string())
print("\n=== cohort x activity (PROD counts) ===")
print(pd.crosstab(prod["behavioural_cohort"],prod["activity_state"]).reindex([c for c in order if c in prod['behavioural_cohort'].unique()]).to_string())

# save mapping + profiles
keep=["identity","behavioural_cohort","activity_state","cat_affinity","tech_share","value_tier" ,
      "lifetime_orders","lifetime_gmv","aov_life","days_since_last","pct_discounted","n_categories",
      "primary_category","recent_category"]
# value tier
g=prod["lifetime_gmv"].clip(lower=0); q=g.quantile([0.30,0.70,0.90])
prod["value_tier"]=np.select([g>=q[0.90],g>=q[0.70],g>=q[0.30]],["VIP","High","Mid"],default="Low")
prod[[c for c in keep if c in prod.columns]].to_csv(f"{SEG}/prod_mapping_v2.csv",index=False)
profile(prod).to_csv(f"{SEG}/cohort_profile_prod_v2.csv")
profile(dev).to_csv(f"{SEG}/cohort_profile_dev_v2.csv")
# slabs
o=pd.read_csv(f"{SEG}/orders_resolved.csv",dtype={"order_no":str}); o["date"]=pd.to_datetime(o["date"],errors="coerce")
lc=o[(o.paid==1)&o.date.notna()&(o.date<=pd.Timestamp("2026-07-31"))].groupby("identity").size()
pd.DataFrame({"slab":["Order 1","Order 2","Order 3+"],
             "users":[(lc==1).sum(),(lc==2).sum(),(lc>=3).sum()]}).to_csv(f"{SEG}/slabs_v2.csv",index=False)
print("\nwrote prod_mapping_v2.csv, profiles, slabs_v2.csv")
