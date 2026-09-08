#!/usr/bin/env python3
"""Build Oct/Nov 2026 inventory demand projections.
Method: Jul+Aug 2026 base run-rate -> 2025 multiplicative seasonal category shift
        -> reconcile to Oct Rs12cr / Nov Rs11.5cr by category -> SKU & parent roll-up."""
import pandas as pd, numpy as np

OCT_TARGET=12.0e7; NOV_TARGET=11.5e7
CAP_LO,CAP_HI=0.55,1.65   # cap seasonal shift factors

A=pd.read_csv('agg/all_months_long.csv')
A['SKU']=A['SKU'].astype(str)
xl=pd.ExcelFile("raw/mapping.xlsx"); m=xl.parse("Parent-Child Mapping")
flags=m.set_index(m['SKU'].astype(str))[['Sold_in_event','In_inventory_7Sep','In_projection_sheet','In_master']]
flags=flags[~flags.index.duplicated()]

# ---------- 1. SKU base = mean of Jul+Aug 2026 (clean non-sale months) ----------
base_months=['2026-07','2026-08']
b=A[A.label.isin(base_months)].copy()
# per SKU: sum then /2 (months present may be 1 or 2 -> average over the 2 base months)
g=b.groupby(['SKU','parent','cat']).agg(
      gross=('gross_rev','sum'), units=('demand_units','sum'),
      deliv=('delivered_units','sum'), days=('days_sold','sum'),
      is_mapped=('is_mapped','max')).reset_index()
g['base_gross']=g['gross']/len(base_months)
g['base_units']=g['units']/len(base_months)
g['asp']=np.where(g['base_units']>0, g['base_gross']/g['base_units'], np.nan)
print(f"Base SKUs (sold in Jul/Aug 2026): {len(g)}  base gross Rs{g['base_gross'].sum()/1e7:.2f}cr/mo")

# ---------- 2. base category shares ----------
def cat_gross(labels):
    d=A[A.label.isin(labels)].groupby('cat')['gross_rev'].sum(); return d
base_cat=g.groupby('cat')['base_gross'].sum()
base_share=base_cat/base_cat.sum()

# ---------- 3. seasonal shift from 2025 (normal=Jun+Jul; Oct; Nov) ----------
norm25=cat_gross(['2025-06','2025-07']); norm25=norm25/norm25.sum()
oct25 =cat_gross(['2025-10']); oct25=oct25/oct25.sum()
nov25 =cat_gross(['2025-11']); nov25=nov25/nov25.sum()
cats=base_share.index
def shift(season):
    s={}
    for c in cats:
        n=norm25.get(c,np.nan); v=season.get(c,np.nan)
        if pd.isna(n) or n<=0 or pd.isna(v): s[c]=1.0
        else: s[c]=min(max(v/n,CAP_LO),CAP_HI)
    return pd.Series(s)
shift_oct=shift(oct25); shift_nov=shift(nov25)

# ---------- 4. Oct/Nov 2026 category target shares ----------
def target_shares(sh):
    raw=base_share*sh; return raw/raw.sum()
sh_oct=target_shares(shift_oct); sh_nov=target_shares(shift_nov)
cat_tgt_oct=sh_oct*OCT_TARGET; cat_tgt_nov=sh_nov*NOV_TARGET

recon=pd.DataFrame({'base_share%':(base_share*100).round(1),
    'shift_Oct':shift_oct.round(3),'Oct_share%':(sh_oct*100).round(1),'Oct_target_cr':(cat_tgt_oct/1e7).round(2),
    'shift_Nov':shift_nov.round(3),'Nov_share%':(sh_nov*100).round(1),'Nov_target_cr':(cat_tgt_nov/1e7).round(2)})
recon=recon.sort_values('Oct_target_cr',ascending=False)
pd.set_option('display.width',180)
print("\n=== CATEGORY RECONCILIATION ===")
print(recon.to_string())
print(f"\nOct sum {cat_tgt_oct.sum()/1e7:.2f}cr  Nov sum {cat_tgt_nov.sum()/1e7:.2f}cr")

# ---------- 5. scale SKUs within category to category target ----------
g['cat_base']=g['cat'].map(base_cat)
g['f_oct']=g['cat'].map(cat_tgt_oct)/g['cat_base']
g['f_nov']=g['cat'].map(cat_tgt_nov)/g['cat_base']
g['oct_gross']=g['base_gross']*g['f_oct']
g['nov_gross']=g['base_gross']*g['f_nov']
g['oct_units']=np.where(g['asp']>0, g['oct_gross']/g['asp'], g['base_units']*g['f_oct'])
g['nov_units']=np.where(g['asp']>0, g['nov_gross']/g['asp'], g['base_units']*g['f_nov'])
g['oct_units']=np.ceil(g['oct_units']).astype(int)
g['nov_units']=np.ceil(g['nov_units']).astype(int)
# attach flags
for col in ['Sold_in_event','In_inventory_7Sep','In_projection_sheet']:
    g[col]=g['SKU'].map(flags[col]).fillna(False)
g.to_csv('agg/model_sku.csv',index=False)
print(f"\nSKU projection rows: {len(g)}  Oct Rs{g['oct_gross'].sum()/1e7:.2f}cr  Nov Rs{g['nov_gross'].sum()/1e7:.2f}cr")
print("Oct units", f"{g['oct_units'].sum():,}", " Nov units", f"{g['nov_units'].sum():,}")
