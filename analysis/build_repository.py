#!/usr/bin/env python3
"""
Build the MASTER USER REPOSITORY (one row per resolved customer since 2020),
as of T0=2026-07-31, with everything MoEngage needs:
  contact keys (email/phone/uuid), lifecycle + behavioural cohort, value tier,
  activity state, category affinity (Tech/Bags scores+label), sub-category
  affinity (primary + secondary + share), recency/frequency/monetary, discount.
"""
import glob, re
import numpy as np, pandas as pd
SEG="analysis/seg"; T0=pd.Timestamp("2026-07-31")
def macro(c):
    c=str(c).lower()
    if re.search(r"bag|backpack|wallet|pouch|travel|duffle|luggage|sling|tote",c): return "bags"
    if re.search(r"case|sleeve|accessor|charg|screen|guard|protection|mobile|watch|home office|tablet|station|grip|lanyard|stand|keychain|organis|airtag|airpod|desk|adapter|power",c): return "tech"
    return "other"

# ---- base per-user features from enriched orders (paid, <=T0) ----
en=pd.read_csv(f"{SEG}/orders_enriched.csv",dtype={"order_no":str})
en["date"]=pd.to_datetime(en["date"],errors="coerce")
en=en[(en["paid"]==1)&en["date"].notna()&en["identity"].notna()&(en["date"]<=T0)].copy()
en["identity"]=en["identity"].astype(int)
g=en.groupby("identity")
u=g.agg(lifetime_orders=("order_no","size"),first_order=("date","min"),last_order=("date","max"),
        lifetime_gmv=("gmv","sum"),pct_discounted=("discounted_any","mean"),
        eff_discount=("effective_discount","mean"),event_share=("price_discounted","mean")).reset_index()
u["tenure_days"]=(T0-u["first_order"]).dt.days
u["days_since_last"]=(T0-u["last_order"]).dt.days
u["aov"]=(u["lifetime_gmv"]/u["lifetime_orders"]).round(0)
u["lifetime_gmv"]=u["lifetime_gmv"].round(0)
u["pct_discounted"]=u["pct_discounted"].round(3); u["eff_discount"]=u["eff_discount"].round(3); u["event_share"]=u["event_share"].round(3)
print("customers:",len(u))

# ---- cohort ----
lab=pd.read_csv(f"{SEG}/labels_prod.csv")   # Power/Deal/Light for 3+
u=u.merge(lab,on="identity",how="left")
u["cohort"]=np.where(u["lifetime_orders"]==1,"O1 (New)",np.where(u["lifetime_orders"]==2,"O2",u["cohort"]))
u["order_cohort"]=np.where(u["lifetime_orders"]>=3,"3+ (Mature)",u["lifetime_orders"].astype(str))

# ---- value tier (whole base gmv percentiles) ----
gq=u["lifetime_gmv"].clip(lower=0); q=gq.quantile([0.5,0.8,0.95])
u["value_tier"]=np.select([gq>=q[0.95],gq>=q[0.8],gq>=q[0.5]],["VIP","High","Mid"],default="Low")
# ---- activity ----
u["activity_state"]=pd.cut(u["days_since_last"],[-1,90,270,10**9],labels=["Active","Lapsed","Dormant"]).astype(str)

# ---- category affinity (macro) from ordercat_resolved ----
o=pd.read_csv(f"{SEG}/orders_resolved.csv",dtype={"order_no":str})
o["date"]=pd.to_datetime(o["date"],errors="coerce")
odate=dict(zip(o["order_no"],o["date"])); oident=dict(zip(o["order_no"],o["identity"]))
oc=pd.read_csv(f"{SEG}/ordercat_resolved.csv",dtype={"order_no":str})
oc["identity"]=oc["identity"].astype(int); oc["date"]=oc["order_no"].map(odate)
oc=oc[(oc["date"].notna())&(oc["date"]<=T0)]; oc["macro"]=oc["category"].map(macro); oc["pos"]=oc["cat_gmv"].clip(lower=0)
piv=oc.pivot_table(index="identity",columns="macro",values="pos",aggfunc="sum",fill_value=0)
for c in ["tech","bags"]:
    if c not in piv: piv[c]=0.0
tb=(piv["tech"]+piv["bags"]).replace(0,np.nan)
piv["tech_score"]=(piv["tech"]/tb).round(3); piv["bags_score"]=(piv["bags"]/tb).round(3)
u=u.merge(piv[["tech_score","bags_score"]],on="identity",how="left")
u["cat_affinity"]=np.select([u["tech_score"]>=0.7,u["tech_score"]<=0.3],["Tech","Designer/Bags"],default="Mixed")
u.loc[u["tech_score"].isna(),"cat_affinity"]="Unknown"

# ---- sub-category affinity ----
sc=pd.concat((pd.read_csv(f,dtype={"order_no":str}) for f in glob.glob("data/subcat/sc_*.csv")),ignore_index=True)
sc["gmv"]=pd.to_numeric(sc["gmv"],errors="coerce").fillna(0).clip(lower=0)
sc["identity"]=sc["order_no"].map(oident); sc["date"]=sc["order_no"].map(odate)
sc=sc[(sc["identity"].notna())&(sc["date"].notna())&(sc["date"]<=T0)]; sc["identity"]=sc["identity"].astype(int)
su=sc.groupby(["identity","sub_category"])["gmv"].sum().reset_index()
tot=su.groupby("identity")["gmv"].transform("sum")
su["share"]=su["gmv"]/tot.replace(0,np.nan)
su=su.sort_values(["identity","gmv"])
top1=su.groupby("identity").tail(1).set_index("identity")
rank2=su.groupby("identity").tail(2).groupby("identity").head(1).set_index("identity")  # 2nd
u=u.merge(top1[["sub_category","share"]].rename(columns={"sub_category":"primary_subcategory","share":"primary_subcat_share"}),on="identity",how="left")
u=u.merge(rank2[["sub_category"]].rename(columns={"sub_category":"secondary_subcategory"}),on="identity",how="left")
u["primary_subcat_share"]=u["primary_subcat_share"].round(3)

# ---- contact keys (latest non-empty per identity) ----
feat=pd.concat((pd.read_csv(f,usecols=["order_no","email","phone","uuid"],dtype=str) for f in glob.glob("data/feat/feat_*.csv")),ignore_index=True)
feat["identity"]=feat["order_no"].map(oident); feat["date"]=feat["order_no"].map(odate)
feat=feat[(feat["identity"].notna())&(feat["date"].notna())].copy(); feat["identity"]=feat["identity"].astype(int)
feat=feat.sort_values("date")
def latest(col):
    s=feat[feat[col].fillna("").str.strip()!=""]
    return s.groupby("identity")[col].last()
for col in ["email","phone","uuid"]:
    u=u.merge(latest(col).rename(f"contact_{col}"),on="identity",how="left")

# ---- write ----
u["first_order"]=u["first_order"].dt.date; u["last_order"]=u["last_order"].dt.date
cols=["identity","contact_email","contact_phone","contact_uuid","cohort","order_cohort","lifetime_orders",
      "value_tier","activity_state","cat_affinity","tech_score","bags_score",
      "primary_subcategory","primary_subcat_share","secondary_subcategory",
      "lifetime_gmv","aov","days_since_last","tenure_days","first_order","last_order",
      "pct_discounted","eff_discount","event_share"]
u=u[cols]
u.to_csv(f"{SEG}/user_repository.csv",index=False)
print("wrote user_repository.csv rows=",len(u),"cols=",len(cols))
print("\ncohort distribution:\n",u["cohort"].value_counts().to_string())
print("\nvalue_tier:\n",u["value_tier"].value_counts().to_string())
print("\ncat_affinity:\n",u["cat_affinity"].value_counts().to_string())
print("\ntop primary_subcategory:\n",u["primary_subcategory"].value_counts().head(12).to_string())
print("\ncontact coverage: email %.1f%% phone %.1f%% uuid %.1f%%"%(
    100*u.contact_email.notna().mean(),100*u.contact_phone.notna().mean(),100*u.contact_uuid.notna().mean()))
print("\nSAMPLE:\n",u.head(4).to_string())
