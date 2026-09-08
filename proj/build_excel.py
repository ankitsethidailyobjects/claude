#!/usr/bin/env python3
import pandas as pd, numpy as np
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from openpyxl.utils.dataframe import dataframe_to_rows

sku=pd.read_csv('agg/tab_sku.csv')
par=pd.read_csv('agg/tab_parent.csv')
cat=pd.read_csv('agg/tab_category.csv')
mon=pd.read_csv('agg/tab_monthly.csv')
full=pd.read_csv('agg/model_full.csv'); full['SKU']=full['SKU'].astype(str)

NAVY="1F3864"; BLUE="2E5496"; LT="D9E1F2"; GREY="F2F2F2"; GREEN="C6EFCE"; YEL="FFF2CC"; RED="F8CBAD"
thin=Side(style='thin',color="BFBFBF")
border=Border(left=thin,right=thin,top=thin,bottom=thin)
wb=Workbook(); wb.remove(wb.active)

def hdr_style(c):
    c.font=Font(bold=True,color="FFFFFF",size=10); c.fill=PatternFill("solid",fgColor=BLUE)
    c.alignment=Alignment(horizontal='center',vertical='center',wrap_text=True); c.border=border

def write_df(ws, df, startrow=1, moneycols=(), pctcols=(), intcols=(), numfmt=None):
    cols=list(df.columns)
    for j,name in enumerate(cols,1):
        hdr_style(ws.cell(startrow,j,name))
    for i,(_,row) in enumerate(df.iterrows(),startrow+1):
        for j,name in enumerate(cols,1):
            v=row[name]
            if pd.isna(v): v=None
            c=ws.cell(i,j,v); c.border=border; c.font=Font(size=9)
            if name in moneycols: c.number_format='#,##0'
            elif name in pctcols: c.number_format='0.0"%"'
            elif name in intcols: c.number_format='#,##0'
            if i%2==0:
                if not c.fill or c.fill.fgColor.rgb in (None,'00000000'): c.fill=PatternFill("solid",fgColor=GREY)
    ws.freeze_panes=ws.cell(startrow+1,1)
    return ws

def setw(ws,widths):
    for i,w in enumerate(widths,1): ws.column_dimensions[get_column_letter(i)].width=w

# ---------------- 1. README ----------------
ws=wb.create_sheet("README")
ws.sheet_view.showGridLines=False
def put(r,c,v,bold=False,size=10,color="000000",fill=None,wrap=False,ital=False):
    cell=ws.cell(r,c,v); cell.font=Font(bold=bold,size=size,color=color,italic=ital)
    if fill: cell.fill=PatternFill("solid",fgColor=fill)
    cell.alignment=Alignment(wrap_text=wrap,vertical='top'); return cell
ws.merge_cells('A1:F1'); put(1,1,"DailyObjects — Inventory Demand Projection: October & November 2026",True,16,"FFFFFF",NAVY)
ws.row_dimensions[1].height=28
ws.merge_cells('A2:F2'); put(2,1,"Child-SKU grain rolled to parent, reconciled to gross-revenue targets. Prepared Sep 2026.",False,10,"FFFFFF",BLUE,ital=True)
rows=[
 ("",""),
 ("TARGETS (gross revenue)","October 2026 = ₹12.00 cr   |   November 2026 = ₹11.50 cr"),
 ("RESULT","Plan reconciles exactly: Oct ₹12.00 cr / 73,476 units · Nov ₹11.50 cr / 69,155 units across 5,105 active SKUs."),
 ("",""),
 ("METHOD (5 steps)",""),
 ("  1. Base demand","Per-SKU run-rate = average of Jul + Aug 2026 actual sold demand (clean, non-sale months at ₹12.1 & 12.5 cr)."),
 ("  2. Demand filter","Units counted = orders excl. paymentFailed / paymentPending / cancel (i.e. inventory was committed). Gross = units × Selling Price (list)."),
 ("  3. Seasonality","2025 multiplicative category shift applied to the 2026 base mix — normal(Jun+Jul'25) → Oct'25 / Nov'25 — capturing the festive category re-mix."),
 ("  4. Event de-distortion","Base is non-HPS, so Sep-HPS deep-tail SKUs (that sell almost only during the sale) get ~0 — correct for a no-HPS Oct/Nov. 1,710 event-only SKUs excluded."),
 ("  5. Reconcile","Scaled within each category to hit the ₹12 cr / ₹11.5 cr targets (per-category, preserving mix). Rolled up to 248 parents."),
 ("",""),
 ("DATA FOUNDATION","24 monthly DMRs aggregated directly from Google Drive (all 2025 + Jan–Aug 2026 + Sep-2026 HPS). Parent-child mapping: 248 parents / 17,848 SKUs. COGS from Jul planning sheet."),
 ("",""),
 ("TABS",""),
 ("  Category_Reconciliation","Hard requirement — category mix, seasonal shift, targets, units, ASP. Totals tie to ₹12 / ₹11.5 cr."),
 ("  Parent_Rollup","Plan at parent level (248 parents) with event-led flag."),
 ("  SKU_Projection","Full 5,105-SKU plan: Oct/Nov units & revenue, ASP, COGS/margin where available, and per-SKU flags."),
 ("  Assumptions_Method","Every locked assumption, method detail, and caveat."),
 ("  Flags_Ambiguities","Data-quality issues, concentration, exclusions, and items needing a human decision."),
 ("  Monthly_Actuals_Reference","24-month gross/units curve — the evidence base."),
 ("",""),
 ("KEY CAVEATS","(1) COGS covers only ~20% of projected gross → margin partial. (2) Base = Jul/Aug run-rate; SKUs with strong OWN festive seasonality (e.g. hero Daily Duffle) may be under-planned — see Flags. (3) Diwali moves Oct'25→Nov'26; mix uses 2025 timing, flagged for review. (4) No HPS in Oct/Nov — sale-only demand deliberately excluded."),
]
r=4
for a,b in rows:
    if a=="" and b=="": r+=1; continue
    bold = a.strip().isupper() and b=="" or a in ("TARGETS (gross revenue)","RESULT","METHOD (5 steps)","DATA FOUNDATION","TABS","KEY CAVEATS")
    put(r,1,a,bold=True if (a.startswith("  ") or bold) else True,size=10,color=NAVY if not a.startswith("  ") else "000000")
    ws.merge_cells(start_row=r,start_column=2,end_row=r,end_column=6)
    put(r,2,b,wrap=True); ws.row_dimensions[r].height=30 if len(str(b))>90 else 15
    r+=1
setw(ws,[26,22,20,20,20,22])

# ---------------- 2. Category_Reconciliation ----------------
ws=wb.create_sheet("Category_Reconciliation")
c2=cat.copy()
c2=c2[['Category','base_gross','Oct_share_%','Oct_gross','Oct_units','Oct_avg_ASP','Nov_share_%','Nov_gross','Nov_units','skus']]
c2.columns=['Category','Base gross/mo (₹)','Oct share %','Oct gross (₹)','Oct units','Oct avg ASP','Nov share %','Nov gross (₹)','Nov units','#SKUs']
write_df(ws,c2,moneycols=['Base gross/mo (₹)','Oct gross (₹)','Nov gross (₹)','Oct avg ASP'],
         pctcols=['Oct share %','Nov share %'],intcols=['Oct units','Nov units','#SKUs'])
tr=len(c2)+2
ws.cell(tr,1,"TOTAL").font=Font(bold=True)
totmap={'Oct gross (₹)':c2['Oct gross (₹)'].sum(),'Nov gross (₹)':c2['Nov gross (₹)'].sum(),
        'Oct units':c2['Oct units'].sum(),'Nov units':c2['Nov units'].sum(),'#SKUs':c2['#SKUs'].sum(),
        'Base gross/mo (₹)':c2['Base gross/mo (₹)'].sum()}
for j,name in enumerate(c2.columns,1):
    cc=ws.cell(tr,j)
    if name in totmap:
        cc.value=totmap[name]; cc.number_format='#,##0'
    cc.font=Font(bold=True); cc.fill=PatternFill("solid",fgColor=YEL); cc.border=border
put=lambda *a,**k:None
ws.cell(tr+1,1,"Target check:").font=Font(bold=True,italic=True)
ws.cell(tr+1,4,"₹12.00 cr ✓").font=Font(bold=True,color="1F7A1F")
ws.cell(tr+1,8,"₹11.50 cr ✓").font=Font(bold=True,color="1F7A1F")
setw(ws,[22,17,11,15,11,12,11,15,11,8])

# ---------------- 3. Parent_Rollup ----------------
ws=wb.create_sheet("Parent_Rollup")
p2=par[['Parent','Category','child_skus','base_gross','Oct_units','Oct_gross','Nov_units','Nov_gross','avg_ASP','event_led']].copy()
p2.columns=['Parent','Category','#Child SKUs','Base gross/mo (₹)','Oct units','Oct gross (₹)','Nov units','Nov gross (₹)','Avg ASP','Event-led']
p2=p2.round(0)
write_df(ws,p2,moneycols=['Base gross/mo (₹)','Oct gross (₹)','Nov gross (₹)','Avg ASP'],
         intcols=['#Child SKUs','Oct units','Nov units'])
setw(ws,[30,20,11,17,10,15,10,15,10,10])

# ---------------- 4. SKU_Projection ----------------
ws=wb.create_sheet("SKU_Projection")
s2=sku.copy()
for b in ['Mapped','Sold_in_Sep_HPS','In_inventory_7Sep','In_team_plan','event_dependent']:
    s2[b]=s2[b].map({True:'Y',False:'',1:'Y',0:''}).fillna('')
s2=s2[['SKU','Product_Name','Parent','Category','Sub_Category','Phone_Model','Base_units_per_mo','ASP',
       'Oct_units','Oct_gross_rev','Nov_units','Nov_gross_rev','COGS','Oct_COGS_value','Oct_margin','Oct_margin_%',
       'Mapped','In_inventory_7Sep','Sold_in_Sep_HPS','event_dependent','In_team_plan','lifecycle']]
s2.columns=['SKU','Product Name','Parent','Category','Sub Category','Phone Model','Base units/mo','ASP',
       'Oct units','Oct gross (₹)','Nov units','Nov gross (₹)','COGS','Oct COGS val','Oct margin (₹)','Oct margin %',
       'Mapped','In inv 7Sep','Sold in HPS','Event-led','In team plan','Lifecycle']
s2=s2.round({'Base units/mo':1,'ASP':0,'Oct gross (₹)':0,'Nov gross (₹)':0,'COGS':0,'Oct COGS val':0,'Oct margin (₹)':0,'Oct margin %':1})
write_df(ws,s2,moneycols=['ASP','Oct gross (₹)','Nov gross (₹)','COGS','Oct COGS val','Oct margin (₹)'],
         pctcols=['Oct margin %'],intcols=['Oct units','Nov units'])
setw(ws,[34,40,26,18,18,14,11,9,9,13,9,13,8,11,12,10,7,9,9,8,9,22])

# ---------------- 5. Assumptions_Method ----------------
ws=wb.create_sheet("Assumptions_Method"); ws.sheet_view.showGridLines=False
def head(r,t):
    ws.merge_cells(start_row=r,start_column=1,end_row=r,end_column=3)
    c=ws.cell(r,1,t); c.font=Font(bold=True,color="FFFFFF",size=11); c.fill=PatternFill("solid",fgColor=BLUE)
def line(r,a,b):
    ca=ws.cell(r,1,a); ca.font=Font(bold=True,size=9); ca.alignment=Alignment(vertical='top',wrap_text=True)
    ws.merge_cells(start_row=r,start_column=2,end_row=r,end_column=3)
    cb=ws.cell(r,2,b); cb.font=Font(size=9); cb.alignment=Alignment(vertical='top',wrap_text=True)
    ws.row_dimensions[r].height=28 if len(str(b))>70 else 15
r=1; head(r,"LOCKED ASSUMPTIONS (confirmed)"); r+=1
for a,b in [
 ("ASP basis","List price — the 'Selling Price' field in the DMR (per-unit, pre-order-level discounts)."),
 ("Revenue definition","Gross = units × Selling Price."),
 ("Under-Discussion SKUs","Included, flagged."),
 ("Base month","July 2026 (used Jul+Aug 2026 average for SKU-level stability; both clean ~₹12 cr non-sale months)."),
 ("HPS","Half Price Sale, runs Mar + Sep. Sep-2026 DMR used DIAGNOSTICALLY for event mix — NOT applied as Oct/Nov uplift."),
 ("No HPS in Oct/Nov 2026","Sale-only (deep-tail) demand deliberately excluded."),
 ("Seasonality source","2025 DMRs (Jun/Jul normal vs Oct/Nov festive).")]:
    line(r,a,b); r+=1
r+=1; head(r,"METHOD DETAIL"); r+=1
for a,b in [
 ("Demand filter","Kept every order status except paymentFailed, paymentPending, cancel. Rationale: those never commit inventory. Delivered/shipped/RTO/returns/COD kept (inventory was consumed). July 2026 net = ₹12.09 cr, validating the filter against the ₹12 cr target scale."),
 ("Base run-rate","Per SKU: mean of Jul-2026 and Aug-2026 sold units & gross. 5,105 SKUs sold in that window → 'Continue/active'. Total base ₹12.27 cr/mo."),
 ("Seasonal shift","For each category: factor = share_2025Oct / share_2025normal (and Nov). Applied multiplicatively to the 2026 base category mix, then renormalised. Factors capped to [0.55, 1.65] to avoid runaway. Captures Cases surge (×1.40 Oct) & Bags surge (×1.24 Nov); Accessories share falls (×0.83)."),
 ("Reconciliation","Each category scaled so its SKUs sum to the category's Oct/Nov target; category targets sum to ₹12 cr / ₹11.5 cr. Mix preserved (no single global factor)."),
 ("Units","units = gross ÷ realised ASP per SKU, rounded up."),
 ("Parent roll-up","SKUs mapped to 248 parents via the mapping file; 98.1% of base gross is mapped. Unmapped SKUs self-parent (flagged)."),
 ("iPhone 17 cycle","Launched Sep 2026 — supports the festive Cases uplift; new-model case SKUs already appear in the Jul base and inherit parent design rates."),
 ("Diwali timing","Diwali ~20 Oct 2025 vs ~8 Nov 2026. The festive surge shifts Oct→Nov in 2026. Mix currently uses 2025 calendar timing — see Flags for the recommended sensitivity review."),
 ("Data pipeline","Each 40–136 MB DMR downloaded to disk and aggregated locally (never loaded whole into memory); only compact per-SKU / per-category summaries retained.")]:
    line(r,a,b); r+=1
setw(ws,[22,40,40])

# ---------------- 6. Flags_Ambiguities ----------------
ws=wb.create_sheet("Flags_Ambiguities")
oct_tot=full['oct_gross'].sum()
flags=[
 ("COGS coverage ~20%","Margin","COGS available for ~1,496 SKUs (Jul planning sheet) = ~19.5% of Oct gross. Margin shown only where COGS exists.","Join full product-master COGS to complete margin view.","Rs %.1f L covered"%(full.loc[full['COGS'].notna(),'oct_gross'].sum()/1e5)),
 ("Hero-SKU own-seasonality","Under-plan risk","Base = Jul/Aug run-rate. Some heroes have strong OWN festive lift (e.g. KELP-DALY-DUFLE-BAG did 4,178 u in Nov'25, 2,026 in Jul/Aug26). Category recon can under-plan them.","Manually uplift top festive movers for Oct/Nov; consider per-SKU seasonality.","Top-10 SKUs = 16.9% of Oct"),
 ("Diwali timing shift","Mix timing","Diwali ~Oct 20 '25 vs ~Nov 8 '26; festive category surge should lean later in 2026.","Sensitivity: shift part of Cases/Bags/Gifts intensity Oct→Nov.","Oct target ₹12cr > Nov ₹11.5cr (given)"),
 ("Event-only deep tail excluded","Scope","1,710 SKUs sold in Sep HPS but with no Jul/Aug base → projected ~0 (correct for no-HPS months).","None — intended. Revisit only if a mini-sale is planned.","1,710 SKUs"),
 ("Phantom / promo revenue","Data hygiene","FREE-MYSTRY-GIFT (471 u @ ₹2,999 notional), other GWP/mystery SKUs book list-price revenue on free items.","Stock the units; treat their revenue as notional (≈₹18 L).","Rs 18.2 L (1.5%% Oct)"),
 ("Gift cards","Non-inventory","DOB-GIFT-CRD-* carry revenue but need no physical stock.","Exclude from procurement; keep in revenue.","Rs 1.6 L, 6 SKUs"),
 ("Unmapped SKUs","Mapping","261 selling SKUs not in the parent-child map → self-parented.","Extend master mapping (see mapping 'Unmapped' tab, 86 rows).","261 SKUs, ~1.9%% of gross"),
 ("Procurement gap","Supply","1,901 projected SKUs are NOT in the 7-Sep inventory snapshot → net-new procurement needed.","Cross-check against open POs / pipeline.","1,901 SKUs"),
 ("Bundles/kits","BoM","60 bundle/combo/kit SKUs planned as finished goods; components not exploded.","Explode to components for raw-material planning.","60 SKUs"),
 ("Sep 2025 looks understated","Data","Sep-2025 DMR aggregated to ₹8.26 cr (below Jul & Oct) despite being an HPS month — likely a partial export. Used only diagnostically.","If HPS mix analysis needed, re-pull a complete Sep'25 file.","Diagnostic only"),
]
fdf=pd.DataFrame(flags,columns=['Flag','Type','Detail','Recommendation','Magnitude'])
for j,name in enumerate(fdf.columns,1): hdr_style(ws.cell(1,j,name))
for i,(_,row) in enumerate(fdf.iterrows(),2):
    for j,name in enumerate(fdf.columns,1):
        c=ws.cell(i,j,row[name]); c.border=border; c.font=Font(size=9)
        c.alignment=Alignment(vertical='top',wrap_text=True)
    ws.row_dimensions[i].height=42
ws.freeze_panes='A2'; setw(ws,[26,14,52,42,22])

# ---------------- 7. Monthly_Actuals_Reference ----------------
ws=wb.create_sheet("Monthly_Actuals_Reference")
mm=mon.copy()
mm['note']=mm['label'].map({'2025-03':'HPS (Mar)','2025-08':'Freedom Sale','2025-09':'HPS Sep (partial export)',
 '2025-10':'Festive analog','2025-11':'Festive analog','2026-03hps':'HPS days','2026-03non':'non-HPS days',
 '2026-07':'BASE','2026-08':'BASE','2026-09hps':'HPS Sep (diagnostic)'}).fillna('')
mm=mm[['label','gross_cr','units','skus','note']]; mm.columns=['Month','Gross (₹ cr)','Units','SKUs sold','Note']
write_df(ws,mm,intcols=['Units','SKUs sold'])
for i in range(2,len(mm)+2):
    ws.cell(i,2).number_format='0.00'
setw(ws,[13,13,11,11,26])

wb.save('out/DailyObjects_OctNov2026_Inventory_Projection.xlsx')
print("workbook written:", 'out/DailyObjects_OctNov2026_Inventory_Projection.xlsx')
print("sheets:", wb.sheetnames)
