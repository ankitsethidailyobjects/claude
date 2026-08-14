#!/usr/bin/env python3
"""
Resolve customers across email/phone/UUID, then compute 2025 retention by
lifetime-order bucket (cohort frozen at 2024-12-31).

Usage: resolve_and_analyze.py <proc_dir> <out_dir> [paid|delivered]
"""
import glob, os, sys, json
import pandas as pd, numpy as np

PROC = sys.argv[1] if len(sys.argv) > 1 else "data/proc"
OUT  = sys.argv[2] if len(sys.argv) > 2 else "analysis/out"
DEF  = sys.argv[3] if len(sys.argv) > 3 else "paid"
os.makedirs(OUT, exist_ok=True)

# hard blocklist of known non-customer identities (integration/test)
EMAIL_BLOCK = {"dummy@cred.club"}
def email_ok(e):
    if not e or e in EMAIL_BLOCK: return False
    if e.endswith("@dailyobjects.com"): return False   # internal/staff/test
    return True

files = sorted(glob.glob(os.path.join(PROC, "orders_*.csv")))
print("Loading", len(files), "files")
df = pd.concat((pd.read_csv(f, dtype=str) for f in files), ignore_index=True)
print("Per-file order records:", len(df))

for c in ["email","phone","uuid"]:
    df[c] = df[c].fillna("").str.strip()
df["order_date"] = pd.to_datetime(df["order_date"], errors="coerce")
df["paid"] = pd.to_numeric(df["paid"], errors="coerce").fillna(0).astype(int)
df["delivered"] = pd.to_numeric(df["delivered"], errors="coerce").fillna(0).astype(int)

# ---- global dedup to unique orders ----
g = df.groupby("order_no", sort=False)
orders = pd.DataFrame({
    "order_date": g["order_date"].min(),
    "paid": g["paid"].max(),
    "delivered": g["delivered"].max(),
    "email": g["email"].agg(lambda s: next((x for x in s if x), "")),
    "phone": g["phone"].agg(lambda s: next((x for x in s if x), "")),
    "uuid":  g["uuid"].agg(lambda s: next((x for x in s if x), "")),
}).reset_index()
print("Unique orders (global):", len(orders), " collapsed:", len(df)-len(orders))

# ---- identity resolution: union-find over tokens ----
parent = {}
def find(x):
    r = x
    while parent[r] != r: r = parent[r]
    while parent[x] != r: parent[x], x = r, parent[x]
    return r
def union(a, b):
    ra, rb = find(a), find(b)
    if ra != rb: parent[ra] = rb

def tokens(row):
    t = []
    if email_ok(row.email): t.append("e:"+row.email)
    if row.phone:            t.append("p:"+row.phone)
    if row.uuid:             t.append("u:"+row.uuid)
    return t

em = orders["email"].values; ph = orders["phone"].values; uu = orders["uuid"].values

# raw token list per order
raw_tok = []
for i in range(len(orders)):
    t = []
    e = em[i]
    if e and e not in EMAIL_BLOCK and not e.endswith("@dailyobjects.com"): t.append("e:"+e)
    if ph[i]: t.append("p:"+ph[i])
    if uu[i]: t.append("u:"+uu[i])
    raw_tok.append(t)

# --- hub suppression: drop identifiers shared across too many distinct others ---
# A real person uses a few identifiers; a shared COD phone / guest id links thousands.
from collections import defaultdict
DEG = 10
neigh = defaultdict(set)
for t in raw_tok:
    for a in t:
        for b in t:
            if a != b: neigh[a].add(b)
suppressed = {tk for tk, ns in neigh.items() if len(ns) > DEG}
print(f"Hub identifiers suppressed (degree>{DEG}): {len(suppressed)}")

tok_lists = []
for t in raw_tok:
    kept = [tk for tk in t if tk not in suppressed]
    tok_lists.append(kept)
    for tk in kept:
        if tk not in parent: parent[tk] = tk
    for k in range(1, len(kept)):
        union(kept[0], kept[k])

# assign canonical identity id
root_to_id = {}
ident = np.empty(len(orders), dtype=object)
unattributable = 0
for i, t in enumerate(tok_lists):
    if not t:
        ident[i] = None; unattributable += 1; continue
    r = find(t[0])
    if r not in root_to_id: root_to_id[r] = len(root_to_id)
    ident[i] = root_to_id[r]
orders["ident"] = ident
print("Distinct resolved identities:", len(root_to_id))
print("Unattributable orders (no usable id):", unattributable)

# ---- valid orders & per-user aggregation ----
flag = "paid" if DEF == "paid" else "delivered"
valid = orders[(orders[flag]==1) & orders["order_date"].notna() & orders["ident"].notna()].copy()
valid["year"] = valid["order_date"].dt.year
print(f"Valid orders ({DEF}) attributable:", len(valid))
print("By year:\n", valid["year"].value_counts().sort_index().to_string())

CUT = pd.Timestamp("2024-12-31")
valid["pre2025"] = valid["order_date"] <= CUT
valid["in2025"]  = valid["year"] == 2025
pu = valid.groupby("ident").agg(
    lifetime_2024=("pre2025","sum"),
    ordered_2025=("in2025","max"),
).reset_index()
cohort = pu[pu["lifetime_2024"] >= 1].copy()
cohort["ordered_2025"] = cohort["ordered_2025"].astype(int)
print("Cohort identities (>=1 order thru 2024):", len(cohort))
print("Identities first-seen in 2025 (excluded):", int((pu["lifetime_2024"]==0).sum()))

# top clusters sanity + token composition (verify no over-merge)
top = cohort.sort_values("lifetime_2024", ascending=False).head(15)
print("Top lifetime counts:", top["lifetime_2024"].tolist())
id_to_tokens = defaultdict(list)
for i, t in enumerate(tok_lists):
    if ident[i] is not None: id_to_tokens[ident[i]].extend(t)
from collections import Counter as _C
for idv in top["ident"].head(6):
    ts = set(id_to_tokens[idv]); k = _C(x[0] for x in ts)
    print(f"  id={idv} lifetime={int(cohort.loc[cohort.ident==idv,'lifetime_2024'].iloc[0])}"
          f" distinct e/p/u={k.get('e',0)}/{k.get('p',0)}/{k.get('u',0)}")

def bucket_table(c):
    t = c.groupby("lifetime_2024").agg(users=("ident","count"),
            retained=("ordered_2025","sum")).reset_index().rename(columns={"lifetime_2024":"orders"})
    t["retention_pct"] = (100*t["retained"]/t["users"]).round(2)
    t["incr_pp"] = t["retention_pct"].diff().round(2)
    z=1.96; p=t["retained"]/t["users"]; n=t["users"]
    t["ci95_pp"] = (100*(z*np.sqrt((p*(1-p)+z*z/(4*n))/n))/(1+z*z/n)).round(2)
    return t

tbl = bucket_table(cohort)
tbl.to_csv(os.path.join(OUT, f"buckets_{DEF}.csv"), index=False)
print(f"\n=== BUCKET TABLE ({DEF}) — buckets 1..20 ===")
print(tbl.head(20).to_string(index=False))

# consolidated tail: cap at 12, group >=12
cap = 12
cc = cohort.copy()
cc["bucket"] = np.where(cc["lifetime_2024"]>=cap, f"{cap}+", cc["lifetime_2024"].astype(str))
order_key = lambda b: (cap if b==f"{cap}+" else int(b))
con = cc.groupby("bucket").agg(users=("ident","count"), retained=("ordered_2025","sum")).reset_index()
con["orders"] = con["bucket"]
con = con.sort_values("bucket", key=lambda s: s.map(order_key))
con["retention_pct"] = (100*con["retained"]/con["users"]).round(2)
con["incr_pp"] = con["retention_pct"].diff().round(2)
con.to_csv(os.path.join(OUT, f"buckets_{DEF}_consolidated.csv"), index=False)
print(f"\n=== CONSOLIDATED (>= {cap} grouped) ===")
print(con[["orders","users","retained","retention_pct","incr_pp"]].to_string(index=False))

summary = {
  "definition": DEF,
  "unique_orders_global": int(len(orders)),
  "unattributable_orders": int(unattributable),
  "valid_attributable_orders": int(len(valid)),
  "resolved_identities_total": int(len(root_to_id)),
  "cohort_users": int(len(cohort)),
  "excluded_first_seen_2025": int((pu["lifetime_2024"]==0).sum()),
  "overall_cohort_retention_pct": round(100*cohort["ordered_2025"].mean(),2),
}
with open(os.path.join(OUT, f"summary_{DEF}.json"),"w") as f: json.dump(summary,f,indent=2)
print("\nSUMMARY:", json.dumps(summary, indent=2))
# persist cohort for plotting/reuse
cohort.to_csv(os.path.join(OUT, f"cohort_{DEF}.csv"), index=False)
