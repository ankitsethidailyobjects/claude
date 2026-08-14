#!/usr/bin/env python3
"""
Assemble the final customer mapping from the STABLE behavioural clusters:
  - name the 5 behavioural cohorts deterministically by profile
  - overlay dynamic layers: activity_state, value_tier, discount_class
  - emit prod_mapping.csv (one row per mature user) + profile table
  - validate: forward 365d retention by named cohort on the DEV snapshot
Usage: step4_assign.py
"""
import os
import numpy as np, pandas as pd
SEG="analysis/seg"; K=5

def name_clusters(prof):
    """prof: DataFrame indexed by cluster with mean features. Return {cluster:name}."""
    remaining=set(prof.index); names={}
    # 1 deal-seekers/returners: most negative aov / highest disc rate
    c=prof.loc[list(remaining)].assign(score=prof["avg_disc_rate"]-prof["aov_life"]/1e5)["score"].idxmax()
    names[c]="Deal-Seekers & Returners"; remaining.discard(c)
    # 2 fast-rising newcomers: shortest tenure
    c=prof.loc[list(remaining)]["tenure_days"].idxmin(); names[c]="Fast-Rising Newcomers"; remaining.discard(c)
    # 3 full-price value seekers: lowest discount usage
    c=prof.loc[list(remaining)]["pct_discounted"].idxmin(); names[c]="Full-Price Value Seekers"; remaining.discard(c)
    # 4 established omnivores: most categories
    c=prof.loc[list(remaining)]["n_categories"].idxmax(); names[c]="Established Omnivores"; remaining.discard(c)
    # 5 remainder
    for c in remaining: names[c]="Prepaid Mid-Value Regulars"
    return names

def activity_state(days):
    if days<=90: return "Active"
    if days<=180: return "Overdue"
    if days<=365: return "At-risk"
    return "Dormant"

def build(suffix):
    feat=pd.read_csv(f"{SEG}/userfeat_{suffix}.csv")
    cl=pd.read_csv(f"{SEG}/clusters_{suffix}_stable_k{K}.csv")
    prof=pd.read_csv(f"{SEG}/profile_{suffix}_stable_k{K}.csv",index_col=0)
    names=name_clusters(prof)
    cl["behavioural_cohort"]=cl["cluster"].map(names)
    m=feat.merge(cl[["identity","cluster","behavioural_cohort"]],on="identity",how="left")
    # whales
    m["behavioural_cohort"]=m["behavioural_cohort"].fillna("Wholesale / B2B")
    # activity
    m["activity_state"]=m["days_since_last"].apply(activity_state)
    # value tier by lifetime_gmv percentile (floor gmv at 0)
    g=m["lifetime_gmv"].clip(lower=0)
    q=g.quantile([0.30,0.70,0.90])
    m["value_tier"]=np.select([g>=q[0.90],g>=q[0.70],g>=q[0.30]],["VIP","High","Mid"],default="Low")
    m.loc[m["behavioural_cohort"]=="Wholesale / B2B","value_tier"]="VIP"
    # discount class
    m["discount_class"]=np.select([m["pct_discounted"]<0.25,m["pct_discounted"]<=0.60],
                                   ["Full-price","Mixed"],default="Discount-led")
    return m,names

prod,names=build("prod")
prod[["identity","behavioural_cohort","activity_state","value_tier","discount_class",
      "lifetime_orders","lifetime_gmv","aov_life","days_since_last","pct_discounted",
      "n_categories","primary_category","recent_category"]].to_csv(f"{SEG}/prod_mapping.csv",index=False)
print("PROD cohort names:",names)
print("\n=== PROD behavioural cohort sizes ===")
print(prod["behavioural_cohort"].value_counts().to_string())
print("\n=== activity_state ===");print(prod["activity_state"].value_counts().to_string())
print("\n=== value_tier ===");print(prod["value_tier"].value_counts().to_string())
print("\n=== discount_class ===");print(prod["discount_class"].value_counts().to_string())

# rich profile with names
def profile(m):
    a=m.groupby("behavioural_cohort").agg(
        users=("identity","size"),
        lifetime_orders=("lifetime_orders","mean"),
        aov=("aov_life","median"),
        days_since_last=("days_since_last","median"),
        pct_discounted=("pct_discounted","mean"),
        n_categories=("n_categories","mean"),
        cod_rate=("cod_rate","mean"),
    )
    a["pct"]=(100*a["users"]/len(m)).round(1)
    for c in ["retained_180d","retained_365d"]:
        if c in m.columns: a[c]=m.groupby("behavioural_cohort")[c].mean()
    a["top_category"]=m.groupby("behavioural_cohort")["primary_category"].agg(lambda s:s.value_counts().idxmax())
    return a.round(2)
print("\n=== PROD PROFILE (named) ===")
print(profile(prod).to_string())

# DEV validation with forward retention
dev,_=build("dev")
prof_dev=profile(dev)
print("\n=== DEV VALIDATION — forward retention by named cohort ===")
print(prof_dev[["users","pct","retained_180d","retained_365d","aov","pct_discounted","days_since_last"]].to_string())
prof_dev.to_csv(f"{SEG}/named_profile_dev.csv")
profile(prod).to_csv(f"{SEG}/named_profile_prod.csv")
# cross tab cohort x activity (prod)
print("\n=== PROD cohort x activity_state (counts) ===")
print(pd.crosstab(prod["behavioural_cohort"],prod["activity_state"]).to_string())
