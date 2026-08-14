#!/usr/bin/env python3
"""
K-Means behavioural segmentation of mature users, with rule-based B2B/whale
carve-out, skew transforms, winsorization, scaling, PCA whitening, a k-sweep
(3..8) validation suite, final fit, and cluster profiling.

Usage: step3_cluster.py <suffix> [k]
  reads analysis/seg/userfeat_<suffix>.csv
  if k omitted -> only prints the k-sweep; if given -> fits and profiles.
"""
import os, sys, json
import numpy as np, pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score, davies_bouldin_score, calinski_harabasz_score

SEG="analysis/seg"; SUF=sys.argv[1]; K=int(sys.argv[2]) if len(sys.argv)>2 else None
RS=42
df=pd.read_csv(os.path.join(SEG,f"userfeat_{SUF}.csv"))
print("mature users:",len(df))

# ---- rule-based outlier carve (B2B / wholesale / gifting) ----
whale_cut=df["lifetime_orders"].quantile(0.995)
whale=df[(df["lifetime_orders"]>=max(50,whale_cut))|(df["avg_qty"]>=10)].copy()
core=df.drop(whale.index).copy()
print(f"carved B2B/whale: {len(whale)} (lifetime>= {max(50,whale_cut):.0f} or avg_qty>=10); core={len(core)}")

# ---- feature set ----
core["aov_trend"]=core["aov_trend"].fillna(0.0)
core["velocity"]=core["velocity"].fillna(0.0)
core["recency_ratio"]=core["recency_ratio"].replace([np.inf],np.nan)
core["recency_ratio"]=core["recency_ratio"].fillna(core["recency_ratio"].median())
core["avg_disc_rate"]=core["avg_disc_rate"].fillna(0.0)
core["disc_rate_L180"]=core["disc_rate_L180"].fillna(0.0)
for c in ["src_ios","src_web","src_mobile","src_android","cat_hhi"]:
    core[c]=core[c].fillna(0.0)

feats={}
feats["f_freq"]=np.log1p(core["lifetime_orders"])
feats["f_recency"]=np.log1p(core["days_since_last"].clip(lower=0))
feats["f_recency_ratio"]=core["recency_ratio"]
feats["f_orders90"]=core["orders_L90"]
feats["f_orders180"]=core["orders_L180"]
feats["f_tenure"]=np.log1p(core["tenure_days"].clip(lower=0))
feats["f_aov"]=np.log1p(core["aov_life"].clip(lower=0))
feats["f_aov_trend"]=core["aov_trend"].clip(0,5)
feats["f_velocity"]=core["velocity"].clip(0,10)
feats["f_pct_disc"]=core["pct_discounted"]
feats["f_disc_rate"]=core["avg_disc_rate"]
feats["f_cod"]=core["cod_rate"]
feats["f_hhi"]=core["cat_hhi"]
feats["f_ncat"]=np.log1p(core["n_categories"])
feats["f_src_ios"]=core["src_ios"]
feats["f_src_web"]=core["src_web"]
X=pd.DataFrame(feats).replace([np.inf,-np.inf],np.nan).fillna(0.0)

# winsorize 1/99
for c in X.columns:
    lo,hi=X[c].quantile([0.01,0.99]); X[c]=X[c].clip(lo,hi)
Xs=StandardScaler().fit_transform(X)
pca=PCA(n_components=0.90,random_state=RS).fit(Xs)
Xp=pca.transform(Xs)
print(f"PCA: {Xp.shape[1]} comps retain 90% var (from {X.shape[1]} feats)")

def sil(Xp,lab):
    n=len(Xp)
    if n>20000:
        idx=np.random.RandomState(RS).choice(n,20000,replace=False)
        return silhouette_score(Xp[idx],lab[idx])
    return silhouette_score(Xp,lab)

if K is None:
    print("\nk | inertia | silhouette | davies_bouldin | calinski_harabasz")
    for k in range(3,9):
        km=KMeans(n_clusters=k,n_init=10,random_state=RS).fit(Xp)
        l=km.labels_
        print(f"{k} | {km.inertia_:.0f} | {sil(Xp,l):.3f} | {davies_bouldin_score(Xp,l):.3f} | {calinski_harabasz_score(Xp,l):.0f}")
    sys.exit(0)

# ---- final fit ----
km=KMeans(n_clusters=K,n_init=20,random_state=RS).fit(Xp)
core["cluster"]=km.labels_
print(f"\nFinal k={K}  silhouette={sil(Xp,km.labels_):.3f}  DB={davies_bouldin_score(Xp,km.labels_):.3f}")

# ---- profile ----
prof_cols=["lifetime_orders","days_since_last","recency_ratio","orders_L90","orders_L180",
           "tenure_days","aov_life","aov_trend","velocity","pct_discounted","avg_disc_rate",
           "cod_rate","n_categories","cat_hhi"]
ret_cols=[c for c in ["retained_180d","retained_365d"] if c in core.columns]
agg={c:"mean" for c in prof_cols+ret_cols}
prof=core.groupby("cluster").agg(agg)
prof.insert(0,"users",core.groupby("cluster").size())
prof.insert(1,"pct",(100*core.groupby("cluster").size()/len(df)).round(1))
# primary category mode per cluster
prof["top_category"]=core.groupby("cluster")["primary_category"].agg(lambda s:s.value_counts().idxmax() if len(s) else "")
pd.set_option("display.width",240,"display.max_columns",40)
print("\n=== CLUSTER PROFILE (means) ===")
print(prof.round(2).to_string())

# whale summary row
if len(whale):
    w={"users":len(whale),"pct":round(100*len(whale)/len(df),1)}
    for c in prof_cols: w[c]=round(whale[c].mean(),2)
    for c in ret_cols: w[c]=round(whale[c].mean(),3)
    print("\nB2B/WHALE (rule-carved):",json.dumps(w))

# save
out=core[["identity","cluster","lifetime_orders","days_since_last","aov_life",
          "pct_discounted","primary_category","recent_category"]+ret_cols].copy()
out.to_csv(os.path.join(SEG,f"clusters_{SUF}_k{K}.csv"),index=False)
prof.round(3).to_csv(os.path.join(SEG,f"profile_{SUF}_k{K}.csv"))
# persist centroids (registry)
cent=pd.DataFrame(km.cluster_centers_); cent.to_csv(os.path.join(SEG,f"centroids_{SUF}_k{K}.csv"),index=False)
print("\nwrote clusters/profile/centroids for",SUF,"k=",K)
