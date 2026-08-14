#!/usr/bin/env python3
"""
Build leakage-safe user-level features as of an observation date T0, for MATURE
customers (lifetime paid orders >= X, default X=3). Optionally attach a forward
retention outcome (orders in (T0, T0+H]) for VALIDATION ONLY (never a feature).

Usage: step2_features.py <T0 YYYY-MM-DD> <out_suffix> [X=3]
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
print(f"T0={T0.date()} paid past-orders={len(past)} future-orders={len(fut)}")

def win(days): return past["date"]>(T0-pd.Timedelta(days=days))
for d in [30,60,90,180,365]:
    past[f"in_{d}"]=(past["date"]>(T0-pd.Timedelta(days=d))).astype(int)

g=past.groupby("identity")
feat=pd.DataFrame({
  "lifetime_orders":g.size(),
  "first_order":g["date"].min(),
  "last_order":g["date"].max(),
  "lifetime_gmv":g["gmv"].sum(),
  "orders_L30":g["in_30"].sum(),"orders_L60":g["in_60"].sum(),
  "orders_L90":g["in_90"].sum(),"orders_L180":g["in_180"].sum(),"orders_L365":g["in_365"].sum(),
  "gmv_L90":g.apply(lambda x:x.loc[x["in_90"]==1,"gmv"].sum(),include_groups=False),
  "gmv_L180":g.apply(lambda x:x.loc[x["in_180"]==1,"gmv"].sum(),include_groups=False),
  "n_discounted":g["discounted"].sum(),
  "sum_disc":g["disc_amt"].sum(),
  "cod_orders":g["payment"].apply(lambda s:(s=="cod").sum()),
  "avg_qty":g["qty"].mean(),
  "disc180_n":g.apply(lambda x:x.loc[x["in_180"]==1,"discounted"].sum(),include_groups=False),
}).reset_index()

# tenure/recency
feat["tenure_days"]=(T0-feat["first_order"]).dt.days
feat["days_since_last"]=(T0-feat["last_order"]).dt.days
feat["avg_inter_order"]=np.where(feat["lifetime_orders"]>1,
        feat["tenure_days"]/(feat["lifetime_orders"]-1), np.nan)
# median inter-order per user
def med_iot(x):
    ds=np.sort(x.values);
    return np.median(np.diff(ds).astype("timedelta64[D]").astype(float)) if len(ds)>1 else np.nan
miot=past.groupby("identity")["date"].apply(med_iot).rename("median_iot")
feat=feat.merge(miot,on="identity",how="left")
feat["recency_ratio"]=feat["days_since_last"]/feat["median_iot"].replace(0,np.nan)
# monetary
feat["aov_life"]=feat["lifetime_gmv"]/feat["lifetime_orders"]
feat["aov_L90"]=np.where(feat["orders_L90"]>0,feat["gmv_L90"]/feat["orders_L90"].replace(0,np.nan),np.nan)
feat["aov_trend"]=feat["aov_L90"]/feat["aov_life"]
# velocity: recent pace vs lifetime baseline (orders per 90d)
base90=(feat["lifetime_orders"]/feat["tenure_days"].replace(0,np.nan))*90
feat["velocity"]=feat["orders_L90"]/base90.replace(0,np.nan)
# discount
feat["pct_discounted"]=feat["n_discounted"]/feat["lifetime_orders"]
feat["avg_disc_rate"]=feat["sum_disc"]/(feat["lifetime_gmv"]+feat["sum_disc"]).replace(0,np.nan)
feat["full_price_rate"]=1-feat["pct_discounted"]
feat["disc_rate_L180"]=feat["disc180_n"]/feat["orders_L180"].replace(0,np.nan)
feat["cod_rate"]=feat["cod_orders"]/feat["lifetime_orders"]
# channel shares
for ch,lbl in [("ios","ios"),("android","android"),("website","web"),("mobile","mobile")]:
    s=past.assign(m=(past["source"]==ch).astype(int)).groupby("identity")["m"].sum()
    feat=feat.merge(s.rename(f"src_{lbl}"),on="identity",how="left")
    feat[f"src_{lbl}"]=feat[f"src_{lbl}"]/feat["lifetime_orders"]

# ---- category features ----
oc=pd.read_csv(os.path.join(SEG,"ordercat_resolved.csv"),dtype={"order_no":str})
oc["identity"]=oc["identity"].astype(int)
odate=dict(zip(o["order_no"],o["date"]))
oc["date"]=oc["order_no"].map(odate)
oc=oc[(oc["date"].notna())&(oc["date"]<=T0)]
catg=oc.groupby(["identity","category"])["cat_gmv"].sum().reset_index()
tot=catg.groupby("identity")["cat_gmv"].transform("sum")
catg["share"]=catg["cat_gmv"]/tot.replace(0,np.nan)
hhi=catg.groupby("identity")["share"].apply(lambda s:(s**2).sum()).rename("cat_hhi")
ndc=catg.groupby("identity")["category"].nunique().rename("n_categories")
prim=catg.sort_values("cat_gmv").groupby("identity").tail(1).set_index("identity")["category"].rename("primary_category")
feat=feat.merge(hhi,on="identity",how="left").merge(ndc,on="identity",how="left").merge(prim,on="identity",how="left")
# recent category = dominant category of the most recent order
last_ord=past.sort_values("date").groupby("identity").tail(1)[["identity","order_no"]]
rc=oc.merge(last_ord,on=["identity","order_no"]).sort_values("cat_gmv").groupby("identity").tail(1)[["identity","category"]]
feat=feat.merge(rc.rename(columns={"category":"recent_category"}),on="identity",how="left")
# cross-category expansion in last 180d (new category vs before)
recent_cats=oc[oc["date"]>(T0-pd.Timedelta(days=180))].groupby("identity")["category"].apply(set)
old_cats=oc[oc["date"]<=(T0-pd.Timedelta(days=180))].groupby("identity")["category"].apply(set)
def expanded(i):
    r=recent_cats.get(i,set()); ol=old_cats.get(i,set())
    return int(len(r-ol)>0 and len(ol)>0)
feat["cat_expansion"]=feat["identity"].map(lambda i:expanded(i))

# ---- mature filter ----
mature=feat[feat["lifetime_orders"]>=X].copy()
print(f"MATURE (>= {X} orders) users: {len(mature):,}  of total-with-orders {len(feat):,}")

# ---- forward outcome (VALIDATION ONLY) ----
for H in [180,365]:
    fw=fut[fut["date"]<=(T0+pd.Timedelta(days=H))].groupby("identity").size()
    mature[f"retained_{H}d"]=mature["identity"].map(lambda i: int(fw.get(i,0)>0))
mature.to_csv(os.path.join(SEG,f"userfeat_{SUF}.csv"),index=False)
print("wrote",f"userfeat_{SUF}.csv","cols",len(mature.columns))
print(mature[["lifetime_orders","days_since_last","aov_life","pct_discounted","n_categories"]].describe().round(1).to_string())
