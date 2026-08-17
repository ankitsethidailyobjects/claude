#!/usr/bin/env python3
"""
For each cohort (O1, O2, Power, Deal, Light) break users down by
activity/dormancy, value tier, category affinity and primary sub-category,
and compute users + monthly/quarterly/yearly retention in each bucket.
Anchor T0=2025-07-31 (full forward year available).
"""
import glob, re
import numpy as np, pandas as pd
SEG="analysis/seg"; T0=pd.Timestamp("2025-07-31")
def macro(c):
    c=str(c).lower()
    if re.search(r"bag|backpack|wallet|pouch|travel|duffle|luggage|sling|tote",c): return "bags"
    if re.search(r"case|sleeve|accessor|charg|screen|guard|protection|mobile|watch|home office|tablet|station|grip|lanyard|stand|keychain|organis|airtag|airpod|desk|adapter|power",c): return "tech"
    return "other"

en=pd.read_csv(f"{SEG}/orders_enriched.csv",dtype={"order_no":str})
en["date"]=pd.to_datetime(en["date"],errors="coerce")
en=en[(en["paid"]==1)&en["date"].notna()&en["identity"].notna()].copy(); en["identity"]=en["identity"].astype(int)
past=en[en["date"]<=T0]; fut=en[en["date"]>T0].assign(dd=lambda x:(x["date"]-T0).dt.days)
u=past.groupby("identity").agg(n=("order_no","size"),gmv=("gmv","sum"),last=("date","max")).reset_index()
u["days_since_last"]=(T0-u["last"]).dt.days
lab=pd.read_csv(f"{SEG}/labels_dev.csv")
u=u.merge(lab,on="identity",how="left")
u["cohort"]=np.where(u["n"]==1,"O1 (New)",np.where(u["n"]==2,"O2",u["cohort"]))
# attributes as-of T0
u["activity_state"]=pd.cut(u["days_since_last"],[-1,90,270,10**9],labels=["Active","Lapsed","Dormant"]).astype(str)
g=u["gmv"].clip(lower=0);q=g.quantile([0.5,0.8,0.95])
u["value_tier"]=np.select([g>=q[0.95],g>=q[0.8],g>=q[0.5]],["VIP","High","Mid"],default="Low")
# affinity
o=pd.read_csv(f"{SEG}/orders_resolved.csv",dtype={"order_no":str}); o["date"]=pd.to_datetime(o["date"],errors="coerce")
odate=dict(zip(o["order_no"],o["date"])); oident=dict(zip(o["order_no"],o["identity"]))
oc=pd.read_csv(f"{SEG}/ordercat_resolved.csv",dtype={"order_no":str}); oc["identity"]=oc["identity"].astype(int)
oc["date"]=oc["order_no"].map(odate); oc=oc[(oc["date"].notna())&(oc["date"]<=T0)]
oc["macro"]=oc["category"].map(macro); oc["pos"]=oc["cat_gmv"].clip(lower=0)
piv=oc.pivot_table(index="identity",columns="macro",values="pos",aggfunc="sum",fill_value=0)
for c in ["tech","bags"]:
    if c not in piv:piv[c]=0.0
tb=(piv["tech"]+piv["bags"]).replace(0,np.nan)
piv["cat_affinity"]=np.select([(piv["tech"]/tb)>=0.7,(piv["tech"]/tb)<=0.3],["Tech","Designer/Bags"],default="Mixed")
u=u.merge(piv[["cat_affinity"]],on="identity",how="left"); u["cat_affinity"]=u["cat_affinity"].fillna("Unknown")
# primary subcat
sc=pd.concat((pd.read_csv(f,dtype={"order_no":str}) for f in glob.glob("data/subcat/sc_*.csv")),ignore_index=True)
sc["gmv"]=pd.to_numeric(sc["gmv"],errors="coerce").fillna(0).clip(lower=0)
sc["identity"]=sc["order_no"].map(oident); sc["date"]=sc["order_no"].map(odate)
sc=sc[(sc["identity"].notna())&(sc["date"].notna())&(sc["date"]<=T0)]; sc["identity"]=sc["identity"].astype(int)
su=sc.groupby(["identity","sub_category"])["gmv"].sum().reset_index().sort_values("gmv").groupby("identity").tail(1)
u=u.merge(su.set_index("identity")["sub_category"].rename("primary_subcategory"),on="identity",how="left")
# forward return
fb=fut.groupby("identity")["dd"].min(); u["dtr"]=u["identity"].map(fb)
def ret(sub,w): return round(100*(sub["dtr"]<=w).mean(),1) if len(sub) else 0.0

cohorts=["O1 (New)","O2","Power Users","Deal Seekers","Light Users"]
rows=[]
def add(cohort,dim,bucket,sub):
    if len(sub)<50: return
    rows.append([cohort,dim,bucket,len(sub),ret(sub,30),ret(sub,90),ret(sub,365)])
for c in cohorts:
    cc=u[u["cohort"]==c]
    add(c,"ALL","(all)",cc)
    for dim,col,order_ in [("Activity","activity_state",["Active","Lapsed","Dormant"]),
                           ("Value","value_tier",["VIP","High","Mid","Low"]),
                           ("Affinity","cat_affinity",["Tech","Designer/Bags","Mixed"])]:
        for b in order_:
            add(c,dim,b,cc[cc[col]==b])
    # top 6 sub-categories within cohort
    top=cc["primary_subcategory"].value_counts().head(6).index
    for b in top:
        add(c,"SubCategory",b,cc[cc["primary_subcategory"]==b])
res=pd.DataFrame(rows,columns=["cohort","dimension","bucket","users","ret_1m","ret_1q","ret_1y"])
res.to_csv(f"{SEG}/cohort_splits.csv",index=False)
print("wrote cohort_splits.csv rows=",len(res))
for c in cohorts:
    print(f"\n===== {c} =====")
    print(res[res.cohort==c][["dimension","bucket","users","ret_1m","ret_1q","ret_1y"]].to_string(index=False))
