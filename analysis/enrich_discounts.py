#!/usr/bin/env python3
"""
Enrich each order with a PRICE-LED discount signal (event price drops that the
DMR hides because it only stores final price), then combine with coupon/DMR
discounts to get the true 'did this customer buy on discount' signal.

Method (category-level ASP, consistent with the elasticity exercise):
  * weekly category ASP = sum(positive cat_gmv)/sum(cat_qty)
  * BAU reference price per (category, year) = 65th pctile of weekly ASP
    (sale weeks pull ASP down, so upper pctiles approximate the list/BAU level)
  * price_depth(cat,week) = max(0, 1 - ASP_week / ref)   -> event discount depth
  * an order is price-discounted if its PRIMARY category's week depth >= 6%
Outputs orders_enriched.csv and prints the 2025 event calendar + validation.
"""
import pandas as pd, numpy as np
SEG="analysis/seg"
o=pd.read_csv(f"{SEG}/orders_resolved.csv",dtype={"order_no":str})
o["date"]=pd.to_datetime(o["date"],errors="coerce")
o=o[o["date"].notna()].copy()
oc=pd.read_csv(f"{SEG}/ordercat_resolved.csv",dtype={"order_no":str})
oc=oc.merge(o[["order_no","date"]],on="order_no",how="inner")
oc["pos_gmv"]=oc["cat_gmv"].clip(lower=0); oc["qty"]=oc["cat_qty"].clip(lower=0)
iso=oc["date"].dt.isocalendar()
oc["yr"]=iso["year"].astype(int); oc["wk"]=iso["week"].astype(int)

# weekly category ASP
g=oc.groupby(["category","yr","wk"]).agg(gmv=("pos_gmv","sum"),qty=("qty","sum")).reset_index()
g=g[g["qty"]>=30]                       # ignore thin category-weeks
g["asp"]=g["gmv"]/g["qty"]
# BAU reference per category-year = 65th pctile of weekly ASP
ref=g.groupby(["category","yr"])["asp"].quantile(0.65).rename("ref").reset_index()
g=g.merge(ref,on=["category","yr"],how="left")
g["depth"]=(1-g["asp"]/g["ref"]).clip(lower=0,upper=0.7)
depth_map=g.set_index(["category","yr","wk"])["depth"].to_dict()

# ---- 2025 event calendar / validation ----
ov=oc[oc["yr"]==2025].groupby("wk").agg(gmv=("pos_gmv","sum"),qty=("qty","sum"))
ov["asp"]=ov["gmv"]/ov["qty"]; med=ov["asp"].median()
ov["dip%"]=((ov["asp"]/med-1)*100).round(1)
evweeks=ov[ov["dip%"]<=-7].index.tolist()
name={4:"Republic Day",12:"HPS-March",13:"HPS-March",14:"HPS-March",35:"HPS-Aug/Sep",36:"HPS-Aug/Sep",
      38:"Sep sale",39:"Sep sale",42:"Diwali",43:"Diwali",46:"Black Friday/Nov"}
print(f"=== 2025 detected event weeks (overall ASP >=7pct below median {med:.0f}) ===")
for w in evweeks: print(f"  W{w}: {ov.loc[w,'dip%']:.1f}%  {name.get(w,'')}")

# ---- per-order primary category + week + price depth ----
prim=oc.sort_values("pos_gmv").groupby("order_no").tail(1)[["order_no","category","yr","wk"]]
prim["price_depth"]=[depth_map.get((c,y,w),0.0) for c,y,w in zip(prim["category"],prim["yr"],prim["wk"])]
prim=prim.rename(columns={"category":"primary_category"})
oq=oc.groupby("order_no")["qty"].sum().rename("order_qty").reset_index()

e=o.merge(prim[["order_no","primary_category","price_depth"]],on="order_no",how="left").merge(oq,on="order_no",how="left")
e["price_depth"]=e["price_depth"].fillna(0.0)
e["price_discounted"]=(e["price_depth"]>=0.08).astype(int)
e["dmr_rate"]=(e["disc_amt"]/(e["gmv"].clip(lower=1)+e["disc_amt"])).clip(0,0.9)
# coupon/DMR flag only where reliable (2020/21 over-populated, 2022 field missing)
e["yr"]=e["date"].dt.year
e["coupon_or_dmr"]=((e["discounted"]==1)&(e["yr"]>=2023)).astype(int)
e["discounted_any"]=((e["coupon_or_dmr"]==1)|(e["price_discounted"]==1)).astype(int)
e["effective_discount"]=e[["dmr_rate","price_depth"]].max(axis=1)
e.loc[e["yr"]<2023,"effective_discount"]=e.loc[e["yr"]<2023,"price_depth"]
e[["order_no","identity","date","paid","gmv","order_qty","primary_category",
   "coupon_or_dmr","price_discounted","discounted_any","effective_discount"]].to_csv(f"{SEG}/orders_enriched.csv",index=False)

paid=e[e["paid"]==1]
print("\n=== Discount signal on PAID orders (all years) ===")
print(f"orders: {len(paid):,}")
print(f"  coupon/DMR discount only:      {100*paid['coupon_or_dmr'].mean():.1f}%")
print(f"  price-led (event) discount:    {100*paid['price_discounted'].mean():.1f}%")
print(f"  ANY discount (enriched):       {100*paid['discounted_any'].mean():.1f}%")
print(f"  mean effective discount:       {100*paid['effective_discount'].mean():.1f}%")
print("\nShare of PAID orders discounted, by year (coupon-only vs enriched):")
for yr,grp in paid.assign(yr=paid['date'].dt.year).groupby("yr"):
    print(f"  {yr}: coupon-only {100*grp['coupon_or_dmr'].mean():4.1f}%   enriched {100*grp['discounted_any'].mean():4.1f}%")
print("\nwrote orders_enriched.csv")
