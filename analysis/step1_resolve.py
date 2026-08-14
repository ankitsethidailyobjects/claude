#!/usr/bin/env python3
"""
Load rich feat_*.csv (order-category grain), collapse to orders, resolve
customer identity (email+phone+uuid union-find with hub suppression), and
persist two resolved tables reused by every snapshot:
  out/orders_resolved.csv    : order_no, identity, date, paid, gmv, disc_amt, discounted, payment, source, qty
  out/ordercat_resolved.csv  : order_no, identity, category, cat_gmv, cat_qty  (paid orders only)
"""
import glob, os, sys
import pandas as pd, numpy as np
from collections import defaultdict

FEAT="data/feat"; OUT="analysis/seg"; os.makedirs(OUT, exist_ok=True)
EMAIL_BLOCK={"dummy@cred.club"}
def email_ok(e): return bool(e) and e not in EMAIL_BLOCK and not e.endswith("@dailyobjects.com")

files=sorted(glob.glob(os.path.join(FEAT,"feat_*.csv")))
print("Loading",len(files),"feature files")
df=pd.concat((pd.read_csv(f,dtype={"order_no":str,"email":str,"phone":str,"uuid":str,
             "payment":str,"source":str,"category":str}) for f in files), ignore_index=True)
print("order-category rows:",len(df))
for c in ["email","phone","uuid","payment","source","category"]:
    df[c]=df[c].fillna("").astype(str).str.strip()
df["order_date"]=pd.to_datetime(df["order_date"],errors="coerce")
for c in ["cat_gmv","cat_qty","cat_disc","order_disc"]:
    df[c]=pd.to_numeric(df[c],errors="coerce").fillna(0.0)
for c in ["paid","delivered","coupon"]:
    df[c]=pd.to_numeric(df[c],errors="coerce").fillna(0).astype(int)

# ---- collapse order-category -> order ----
g=df.groupby("order_no",sort=False)
orders=pd.DataFrame({
  "date":g["order_date"].min(),
  "paid":g["paid"].max(),
  "delivered":g["delivered"].max(),
  "gmv":g["cat_gmv"].sum(),
  "qty":g["cat_qty"].sum(),
  "line_disc":g["cat_disc"].sum(),
  "order_disc":g["order_disc"].max(),
  "coupon":g["coupon"].max(),
  "email":g["email"].agg(lambda s:next((x for x in s if x),"")),
  "phone":g["phone"].agg(lambda s:next((x for x in s if x),"")),
  "uuid":g["uuid"].agg(lambda s:next((x for x in s if x),"")),
  "payment":g["payment"].agg(lambda s:next((x for x in s if x),"")),
  "source":g["source"].agg(lambda s:next((x for x in s if x),"")),
}).reset_index()
orders["disc_amt"]=orders[["line_disc","order_disc"]].max(axis=1)
orders["discounted"]=((orders["coupon"]==1)|(orders["disc_amt"]>0)).astype(int)
print("unique orders:",len(orders))

# ---- identity resolution: union-find with hub suppression ----
parent={}
def find(x):
    r=x
    while parent[r]!=r:r=parent[r]
    while parent[x]!=r:parent[x],x=r,parent[x]
    return r
def union(a,b):
    ra,rb=find(a),find(b)
    if ra!=rb:parent[ra]=rb
em=orders["email"].values;ph=orders["phone"].values;uu=orders["uuid"].values
raw=[]
for i in range(len(orders)):
    t=[]
    if email_ok(em[i]):t.append("e:"+em[i])
    if ph[i]:t.append("p:"+ph[i])
    if uu[i]:t.append("u:"+uu[i])
    raw.append(t)
DEG=10
neigh=defaultdict(set)
for t in raw:
    for a in t:
        for b in t:
            if a!=b:neigh[a].add(b)
supp={tk for tk,ns in neigh.items() if len(ns)>DEG}
print("hub identifiers suppressed:",len(supp))
ident=np.empty(len(orders),dtype=object);root2id={};unattr=0
for i,t in enumerate(raw):
    kept=[tk for tk in t if tk not in supp]
    for tk in kept:parent.setdefault(tk,tk)
    for k in range(1,len(kept)):union(kept[0],kept[k])
for i,t in enumerate(raw):
    kept=[tk for tk in t if tk not in supp]
    if not kept:ident[i]=None;unattr+=1;continue
    r=find(kept[0])
    if r not in root2id:root2id[r]=len(root2id)
    ident[i]=root2id[r]
orders["identity"]=ident
print("distinct identities:",len(root2id)," unattributable orders:",unattr)

# ---- persist ----
oo=orders[orders["identity"].notna()].copy()
oo["identity"]=oo["identity"].astype(int)
oo[["order_no","identity","date","paid","gmv","disc_amt","discounted","payment","source","qty"]]\
  .to_csv(os.path.join(OUT,"orders_resolved.csv"),index=False)
print("wrote orders_resolved.csv:",len(oo))

# order-category for paid orders only, with identity
paid_orders=set(oo.loc[oo["paid"]==1,"order_no"])
idmap=dict(zip(oo["order_no"],oo["identity"]))
oc=df[df["order_no"].isin(paid_orders)][["order_no","category","cat_gmv","cat_qty"]].copy()
oc["identity"]=oc["order_no"].map(idmap)
oc=oc[oc["identity"].notna()]
oc["identity"]=oc["identity"].astype(int)
oc.to_csv(os.path.join(OUT,"ordercat_resolved.csv"),index=False)
print("wrote ordercat_resolved.csv:",len(oc))
print("order years:\n", oo["date"].dt.year.value_counts().sort_index().to_string())
