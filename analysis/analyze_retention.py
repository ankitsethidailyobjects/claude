#!/usr/bin/env python3
"""
Platform retention by lifetime order count (cohort frozen at 2024-12-31).

Input : proc/orders_*.csv  (order_no, email, order_date, year, paid, delivered)
Steps :
  1. Concatenate all per-file order records.
  2. Global dedup by order_no  (order = one unique Order No.).
       email = first non-empty seen; date = min; paid/delivered = max (OR).
  3. Keep only valid orders (paid==1) for the primary view.
  4. Per user (email): lifetime orders with date <= 2024-12-31, and whether
     they placed >=1 order during 2025.
  5. Bucket users by lifetime-through-2024 count; compute 2025 retention %.
Outputs a JSON + CSV of the bucket table and per-user summary sizes.
"""
import glob, os, sys
import pandas as pd
import numpy as np

PROC = sys.argv[1] if len(sys.argv) > 1 else "/home/user/claude/data/proc"
OUT  = sys.argv[2] if len(sys.argv) > 2 else "/home/user/claude/analysis/out"
os.makedirs(OUT, exist_ok=True)
DEF  = sys.argv[3] if len(sys.argv) > 3 else "paid"   # "paid" or "delivered"

files = sorted(glob.glob(os.path.join(PROC, "orders_*.csv")))
print("Loading:", [os.path.basename(f) for f in files])
df = pd.concat((pd.read_csv(f, dtype={"order_no": str, "email": str}) for f in files),
               ignore_index=True)
print("Raw order-records (per file):", len(df))

# --- global dedup by order_no ---
df["order_date"] = pd.to_datetime(df["order_date"], errors="coerce")
df["email"] = df["email"].fillna("").str.strip().str.lower()
df["paid"] = df["paid"].fillna(0).astype(int)
df["delivered"] = df["delivered"].fillna(0).astype(int)

g = df.groupby("order_no", sort=False)
orders = pd.DataFrame({
    "order_date": g["order_date"].min(),
    "paid": g["paid"].max(),
    "delivered": g["delivered"].max(),
    # first non-empty email
    "email": g["email"].agg(lambda s: next((x for x in s if x), "")),
}).reset_index()
print("Unique orders (global):", len(orders))
dup_removed = len(df) - len(orders)
print("Duplicate order-records collapsed:", dup_removed)

# data quality
n_no_date = orders["order_date"].isna().sum()
n_no_email = (orders["email"] == "").sum()
print(f"Orders missing date: {n_no_date}; missing email: {n_no_email}")

flag = "paid" if DEF == "paid" else "delivered"
valid = orders[(orders[flag] == 1) & (orders["order_date"].notna()) & (orders["email"] != "")].copy()
print(f"Valid orders ({DEF}, with date & email): {len(valid)}")
valid["year"] = valid["order_date"].dt.year
print("Valid orders by year:\n", valid["year"].value_counts().sort_index())

CUTOFF = pd.Timestamp("2024-12-31")
valid["pre2025"] = valid["order_date"] <= CUTOFF
valid["in2025"]  = valid["year"] == 2025

per_user = valid.groupby("email").agg(
    lifetime_2024=("pre2025", "sum"),
    ordered_2025=("in2025", "max"),
    total_valid=("order_no", "count"),
).reset_index()

# cohort: users with >=1 valid order through 2024-12-31
cohort = per_user[per_user["lifetime_2024"] >= 1].copy()
cohort["ordered_2025"] = cohort["ordered_2025"].astype(int)
print("\nCohort users (>=1 order through 2024):", len(cohort))
print("Users first-seen in 2025 (excluded from cohort):",
      (per_user["lifetime_2024"] == 0).sum())

# --- bucket table (raw, per exact count) ---
tbl = cohort.groupby("lifetime_2024").agg(
    users=("email", "count"),
    retained=("ordered_2025", "sum"),
).reset_index().rename(columns={"lifetime_2024": "orders"})
tbl["retention_pct"] = 100 * tbl["retained"] / tbl["users"]
tbl["incr_pp"] = tbl["retention_pct"].diff().round(2)
# Wilson 95% CI half-width for retention
z = 1.96
p = tbl["retained"] / tbl["users"]
n = tbl["users"]
tbl["ci95_pp"] = (100 * (z*np.sqrt((p*(1-p)+z*z/(4*n))/n))/(1+z*z/n)).round(2)
tbl["retention_pct"] = tbl["retention_pct"].round(2)

tbl.to_csv(os.path.join(OUT, f"buckets_{DEF}.csv"), index=False)
print(f"\n=== BUCKET TABLE ({DEF}) ===")
with pd.option_context("display.max_rows", 200, "display.width", 160):
    print(tbl.to_string(index=False))

# summary numbers for interpretation
summary = {
    "definition": DEF,
    "unique_orders_global": int(len(orders)),
    "valid_orders": int(len(valid)),
    "cohort_users": int(len(cohort)),
    "excluded_first_seen_2025": int((per_user["lifetime_2024"] == 0).sum()),
    "orders_missing_email": int(n_no_email),
    "orders_missing_date": int(n_no_date),
}
import json
with open(os.path.join(OUT, f"summary_{DEF}.json"), "w") as f:
    json.dump(summary, f, indent=2)
print("\nSUMMARY:", json.dumps(summary, indent=2))
