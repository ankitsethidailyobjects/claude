#!/usr/bin/env python3
import pandas as pd, numpy as np

A=pd.read_csv('agg/all_months_long.csv'); A['SKU']=A['SKU'].astype(str)
g=pd.read_csv('agg/model_sku.csv'); g['SKU']=g['SKU'].astype(str)
cogs=pd.read_csv('agg/cogs.csv'); cogs['SKU']=cogs['SKU'].astype(str)
xl=pd.ExcelFile("raw/mapping.xlsx"); m=xl.parse("Parent-Child Mapping"); m['SKU']=m['SKU'].astype(str)
meta=m.set_index('SKU')[['Product_Name','Phone_Model','Sub_Category','Brand']]; meta=meta[~meta.index.duplicated()]

# Sep-2026 HPS gross per SKU (event dependence)
hps=A[A.label=='2026-09hps'].groupby('SKU')['gross_rev'].sum().rename('sep_hps_gross')

g=g.join(cogs.set_index('SKU')['COGS'],on='SKU')
g=g.join(meta,on='SKU')
g=g.join(hps,on='SKU')
g['sep_hps_gross']=g['sep_hps_gross'].fillna(0)
g['Product_Name']=g['Product_Name'].fillna('')
g['Sub_Category']=g['Sub_Category'].fillna(g['cat'])

# margins
g['oct_cogs_value']=np.where(g['COGS'].notna(), g['oct_units']*g['COGS'], np.nan)
g['nov_cogs_value']=np.where(g['COGS'].notna(), g['nov_units']*g['COGS'], np.nan)
g['oct_margin']=g['oct_gross']-g['oct_cogs_value']
g['oct_margin_pct']=np.where(g['oct_gross']>0, g['oct_margin']/g['oct_gross']*100, np.nan)

# lifecycle proxy: sold in Jul or Aug 2026 => Active/Continue (all base SKUs qualify)
g['lifecycle']='Continue (active Jul/Aug26)'
# event-dependence: HPS gross >> base -> event-led
g['event_ratio']=np.where(g['base_gross']>0, g['sep_hps_gross']/(g['base_gross']), np.nan)
g['event_dependent']=np.where((g['sep_hps_gross']>0)&((g['base_gross']*3)<g['sep_hps_gross']),True,False)

# ---------- SKU tab ----------
sku=g[['SKU','Product_Name','parent','cat','Sub_Category','Phone_Model',
       'base_units','asp','oct_units','oct_gross','nov_units','nov_gross',
       'COGS','oct_cogs_value','oct_margin','oct_margin_pct',
       'is_mapped','Sold_in_event','In_inventory_7Sep','In_projection_sheet','event_dependent','lifecycle']].copy()
sku=sku.rename(columns={'parent':'Parent','cat':'Category','base_units':'Base_units_per_mo',
       'asp':'ASP','oct_units':'Oct_units','oct_gross':'Oct_gross_rev','nov_units':'Nov_units',
       'nov_gross':'Nov_gross_rev','is_mapped':'Mapped','Sold_in_event':'Sold_in_Sep_HPS',
       'In_inventory_7Sep':'In_inventory_7Sep','In_projection_sheet':'In_team_plan',
       'oct_cogs_value':'Oct_COGS_value','oct_margin':'Oct_margin','oct_margin_pct':'Oct_margin_%'})
sku=sku.sort_values('Oct_gross_rev',ascending=False)
sku.to_csv('agg/tab_sku.csv',index=False)

# ---------- Parent rollup ----------
par=g.groupby(['parent','cat']).agg(
    child_skus=('SKU','nunique'),
    base_units=('base_units','sum'), base_gross=('base_gross','sum'),
    Oct_units=('oct_units','sum'), Oct_gross=('oct_gross','sum'),
    Nov_units=('nov_units','sum'), Nov_gross=('nov_gross','sum'),
    sep_hps_gross=('sep_hps_gross','sum'),
    event_dep_skus=('event_dependent','sum')).reset_index()
par['avg_ASP']=np.where(par['Oct_units']>0,par['Oct_gross']/par['Oct_units'],0)
par['event_led']=np.where(par['base_gross']*3<par['sep_hps_gross'],'YES','')
par=par.rename(columns={'parent':'Parent','cat':'Category'}).sort_values('Oct_gross',ascending=False)
par.to_csv('agg/tab_parent.csv',index=False)

# ---------- Category reconciliation ----------
cat=g.groupby('cat').agg(base_gross=('base_gross','sum'),
    Oct_units=('oct_units','sum'),Oct_gross=('oct_gross','sum'),
    Nov_units=('nov_units','sum'),Nov_gross=('nov_gross','sum'),
    skus=('SKU','nunique')).reset_index().rename(columns={'cat':'Category'})
cat['Oct_share_%']=(cat['Oct_gross']/cat['Oct_gross'].sum()*100)
cat['Nov_share_%']=(cat['Nov_gross']/cat['Nov_gross'].sum()*100)
cat['Oct_avg_ASP']=np.where(cat['Oct_units']>0,cat['Oct_gross']/cat['Oct_units'],0)
cat=cat.sort_values('Oct_gross',ascending=False)
cat.to_csv('agg/tab_category.csv',index=False)

# ---------- Monthly actuals reference ----------
mt=A.groupby('label').agg(gross=('gross_rev','sum'),units=('demand_units','sum'),skus=('SKU','nunique')).reset_index()
mt['gross_cr']=(mt['gross']/1e7).round(2); mt=mt.sort_values('label')
mt.to_csv('agg/tab_monthly.csv',index=False)

# ---------- summary numbers for flags ----------
oct_tot=g['oct_gross'].sum();
covered=g.loc[g['COGS'].notna(),'oct_gross'].sum()
print("Oct gross Rs%.2fcr Nov Rs%.2fcr"%(g['oct_gross'].sum()/1e7,g['nov_gross'].sum()/1e7))
print("COGS coverage of Oct gross: %.1f%%"%(covered/oct_tot*100))
print("SKUs:",len(g)," unmapped:",(~g['is_mapped']).sum()," event_dependent:",g['event_dependent'].sum())
top10=sku.nlargest(10,'Oct_gross_rev')['Oct_gross_rev'].sum()
print("Top-10 SKU concentration (Oct): %.1f%%"%(top10/oct_tot*100))
# excluded deep tail: mapping Sold_in_event True but not projected
proj=set(g['SKU']); ev=set(m.loc[m['Sold_in_event']==True,'SKU'])
print("Event SKUs NOT projected (deep tail, no-HPS excl):",len(ev-proj))
inv=set(m.loc[m['In_inventory_7Sep']==True,'SKU'])
print("Projected SKUs not in 7Sep inventory (procure):",len(proj-inv))
g.to_csv('agg/model_full.csv',index=False)
print("saved tabs.")
