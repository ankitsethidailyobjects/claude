#!/usr/bin/env python3
import glob, os, sys
import pandas as pd, numpy as np
from collections import defaultdict, Counter
PROC="data/proc"
EMAIL_BLOCK={"dummy@cred.club"}
def email_ok(e): return bool(e) and e not in EMAIL_BLOCK and not e.endswith("@dailyobjects.com")
df=pd.concat((pd.read_csv(f,dtype=str) for f in glob.glob(os.path.join(PROC,"orders_*.csv"))),ignore_index=True)
for c in ["email","phone","uuid"]: df[c]=df[c].fillna("").str.strip()
df["order_date"]=pd.to_datetime(df["order_date"],errors="coerce")
df["paid"]=pd.to_numeric(df["paid"],errors="coerce").fillna(0).astype(int)
g=df.groupby("order_no",sort=False)
o=pd.DataFrame({"paid":g["paid"].max(),"order_date":g["order_date"].min(),
  "email":g["email"].agg(lambda s:next((x for x in s if x),"")),
  "phone":g["phone"].agg(lambda s:next((x for x in s if x),"")),
  "uuid":g["uuid"].agg(lambda s:next((x for x in s if x),""))}).reset_index()
parent={}
def find(x):
    r=x
    while parent[r]!=r: r=parent[r]
    while parent[x]!=r: parent[x],x=r,parent[x]
    return r
def union(a,b):
    ra,rb=find(a),find(b)
    if ra!=rb: parent[ra]=rb
em=o["email"].values; ph=o["phone"].values; uu=o["uuid"].values
toks=[]
for i in range(len(o)):
    t=[]
    if email_ok(em[i]): t.append("e:"+em[i])
    if ph[i]: t.append("p:"+ph[i])
    if uu[i]: t.append("u:"+uu[i])
    toks.append(t)
    for tk in t:
        parent.setdefault(tk,tk)
    for k in range(1,len(t)): union(t[0],t[k])
root=np.empty(len(o),dtype=object)
for i,t in enumerate(toks):
    root[i]=find(t[0]) if t else None
o["root"]=root
val=o[(o.paid==1)&o.order_date.notna()&o.root.notna()]
pre=val[val.order_date<=pd.Timestamp("2024-12-31")]
sz=pre.groupby("root").size().sort_values(ascending=False)
print("clusters with >1000 lifetime:",int((sz>1000).sum()),
      " >500:",int((sz>500).sum())," >200:",int((sz>200).sum())," >100:",int((sz>100).sum()))
# tokens per top cluster
tokmap=defaultdict(list)
for i,t in enumerate(toks):
    if t: tokmap[find(t[0])].extend(t)
for r in sz.head(6).index:
    ts=tokmap[r]; kinds=Counter(x[0] for x in set(ts))
    print(f"\ncluster size(thru2024)={sz[r]} : distinct tokens e/p/u ="
          f"{kinds.get('e',0)}/{kinds.get('p',0)}/{kinds.get('u',0)}")
    print("  sample tokens:", list(set(ts))[:6])
