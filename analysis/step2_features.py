#!/usr/bin/env python3
"""
Build leakage-safe user-level features as of observation date T0, for MATURE
customers (lifetime paid orders >= X, default 3). Optional forward retention
outcome in (T0, T0+H] for VALIDATION ONLY (never a clustering feature).
Vectorized for speed on ~2.8M orders.

Usage: step2_features.py <T0 YYYY-MM-DD> <suffix> [X=3]
"""
import os, sys
import pandas as pd, numpy as np

SEG="analysis/seg"
T0=pd.Timestamp(sys.argv[1]); SUF=sys.argv[2]; X=int(sys.argv[3]) if len(sys.argv)>3 else 3

o=pd.read_csv(os.path.join(SEG,"orders_resolved.csv"),dtype={"order_no":str})
o["date"]=pd.to_datetime(o["date"],errors="coerce")
o=o[(o["paid"]==1)&o["date"].notna()&o["identity"].notna()].copy()
o["identity"]=o["identity"].astype(int)
past=o[o["date"]<=T0].copy()
fut =o[o["date"]>T0].copy()
print(f"T0={T0.date()} paid past={len(past)} future={len(fut)}")

for d in [30,60,90,180,365]:
    past[f"in_{d}"]=(past["date"]>(T0-pd.Timedelta(days=d))).astype(int)
past["gmv90"]=past["gmv"]*past["in_90"]
past["gmv180"]=past["gmv"]*past["in_180"]
past["disc180"]=past["discounted"]*past["in_180"]
past["is_cod"]=(past["payment"]=="cod").astype(int)
for ch in ["ios","android","website","mobile"]:
    past[f"s_{ch}"]=(past["source"]==ch).astype(int)

g=past.groupby("identity",sort=False)
feat=g.agg(
    lifetime_orders=("order_no","size"),
    first_order=("date","min"),
    last_order=("date","max"),
    lifetime_gmv=("gmv","sum"),
    orders_L30=("in_30","sum"),orders_L60=("in_60","sum"),orders_L90=("in_90","sum"),
    orders_L180=("in_180","sum"),orders_L365=("in_365","sum"),
    gmv_L90=("gmv90","sum"),gmv_L180=("gmv180","sum"),
    n_discounted=("discounted","sum"),sum_disc=("disc_amt","sum"),
    disc180_n=("disc180","sum"),cod_orders=("is_cod","sum"),avg_qty=("qty","mean"),
    s_ios=("s_ios","sum"),s_android=("s_android","sum"),s_web=("s_website","sum"),s_mobile=("s_mobile","sum"),
).reset_index()

# vectorized median inter-order gap
ps=past.sort_values(["identity","date"])
gap=ps["date"].diff().dt.days
same=ps["identity"].eq(ps["identity"].shift())
ps=ps.assign(gap=gap.where(same))
miot=ps.groupby("identity")["gap"].median().rename("median_iot")
feat=feat.merge(miot,on="identity",how="left")

feat["tenure_days"]=(T0-feat["first_order"]).dt.days
feat["days_since_last"]=(T0-feat["last_order"]).dt.days
feat["avg_inter_order"]=np.where(feat["lifetime_orders"]>1,feat["tenure_days"]/(feat["lifetime_orders"]-1),np.nan)
feat["recency_ratio"]=feat["days_since_last"]/feat["median_iot"].replace(0,np.nan)
feat["aov_life"]=feat["lifetime_gmv"]/feat["lifetime_orders"]
feat["aov_L90"]=np.where(feat["orders_L90"]>0,feat["gmv_L90"]/feat["orders_L90"].replace(0,np.nan),np.nan)
feat["aov_trend"]=feat["aov_L90"]/feat["aov_life"]
base90=(feat["lifetime_orders"]/feat["tenure_days"].replace(0,np.nan))*90
feat["velocity"]=feat["orders_L90"]/base90.replace(0,np.nan)
feat["pct_discounted"]=feat["n_discounted"]/feat["lifetime_orders"]
feat["avg_disc_rate"]=feat["sum_disc"]/(feat["lifetime_gmv"]+feat["sum_disc"]).replace(0,np.nan)
feat["full_price_rate"]=1-feat["pct_discounted"]
feat["disc_rate_L180"]=feat["disc180_n"]/feat["orders_L180"].replace(0,np.nan)
feat["cod_rate"]=feat["cod_orders"]/feat["lifetime_orders"]
for c in ["ios","android","web","mobile"]:
    feat[f"src_{c}"]=feat[f"s_{c}"]/feat["lifetime_orders"]

# ---- category features (vectorized) ----
oc=pd.read_csv(os.path.join(SEG,"ordercat_resolved.csv"),dtype={"order_no":str})
oc["identity"]=oc["identity"].astype(int)
oc=oc.merge(o[["order_no","date"]],on="order_no",how="left")
oc=oc[(oc["date"].notna())&(oc["date"]<=T0)]
catg=oc.groupby(["identity","category"],sort=False)["cat_gmv"].sum().reset_index()
tot=catg.groupby("identity")["cat_gmv"].transform("sum")
catg["share"]=catg["cat_gmv"]/tot.replace(0,np.nan)
catg["sh2"]=catg["share"]**2
hhi=catg.groupby("identity")["sh2"].sum().rename("cat_hhi")
ndc=catg.groupby("identity")["category"].nunique().rename("n_categories")
prim=catg.sort_values("cat_gmv").groupby("identity").tail(1).set_index("identity")["category"].rename("primary_category")
feat=feat.merge(hhi,on="identity",how="left").merge(ndc,on="identity",how="left").merge(prim,on="identity",how="left")
# recent category (dominant cat of most-recent order)
last_ord=past.sort_values("date").groupby("identity").tail(1)[["identity","order_no"]]
rc=oc.merge(last_ord,on=["identity","order_no"]).sort_values("cat_gmv").groupby("identity").tail(1)[["identity","category"]]
feat=feat.merge(rc.rename(columns={"category":"recent_category"}),on="identity",how="left")

# ---- mature filter FIRST, then expensive expansion only on mature ----
mature=feat[feat["lifetime_orders"]>=X].copy()
print(f"MATURE (>= {X}): {len(mature):,} of {len(feat):,} customers-with-orders")
mset=set(mature["identity"])
ocm=oc[oc["identity"].isin(mset)]
rec=ocm[ocm["date"]>(T0-pd.Timedelta(days=180))].groupby("identity")["category"].agg(set)
old=ocm[ocm["date"]<=(T0-pd.Timedelta(days=180))].groupby("identity")["category"].agg(set)
def expanded(i):
    r=rec.get(i,set()); ol=old.get(i,set()); return int(len(r-ol)>0 and len(ol)>0)
mature["cat_expansion"]=mature["identity"].map(expanded)

# forward outcome (validation only)
for H in [180,365]:
    fw=fut[fut["date"]<=(T0+pd.Timedelta(days=H))].groupby("identity").size()
    mature[f"retained_{H}d"]=mature["identity"].map(lambda i:int(fw.get(i,0)>0))
mature.to_csv(os.path.join(SEG,f"userfeat_{SUF}.csv"),index=False)
print("wrote",f"userfeat_{SUF}.csv",len(mature.columns),"cols")
print(mature[["lifetime_orders","days_since_last","aov_life","pct_discounted","n_categories","retained_365d"]].describe().round(2).to_string())
