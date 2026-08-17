import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side, numbers
from openpyxl.utils import get_column_letter

wb = openpyxl.Workbook()

# ---------- styles ----------
H1   = Font(bold=True, size=15, color="FFFFFF")
H2   = Font(bold=True, size=12, color="1F3864")
BOLD = Font(bold=True)
ITAL = Font(italic=True, size=9, color="666666")
WHITE= Font(bold=True, color="FFFFFF")
navy = PatternFill("solid", fgColor="1F3864")
blue = PatternFill("solid", fgColor="2E5496")
lblue= PatternFill("solid", fgColor="D9E1F2")
yell = PatternFill("solid", fgColor="FFF2CC")   # editable input
grey = PatternFill("solid", fgColor="F2F2F2")
green= PatternFill("solid", fgColor="E2EFDA")
red  = PatternFill("solid", fgColor="FCE4D6")
thin = Side(style="thin", color="BFBFBF")
box  = Border(left=thin,right=thin,top=thin,bottom=thin)
RS = "#,##0"; PCT="0.0%"; PCT0="0%"; RS2="#,##0.0"

def cell(ws,c,v,font=None,fill=None,fmt=None,align=None,border=True):
    x=ws[c]; x.value=v
    if font:x.font=font
    if fill:x.fill=fill
    if fmt:x.number_format=fmt
    if align:
        h="left" if align=="wrap" else align
        x.alignment=Alignment(horizontal=h,vertical="center",wrap_text=(align=="wrap"))
    if border:x.border=box
    return x

# ============================================================= INPUTS/DRIVERS sheet
ws = wb.active; ws.title="Drivers & Sources"
ws.sheet_view.showGridLines=False
for col,w in {"A":2,"B":42,"C":16,"D":16,"E":16,"F":40}.items(): ws.column_dimensions[col].width=w
ws.merge_cells("B2:F2"); cell(ws,"B2","DailyObjects · July 2026 · D2C P&L — New vs Repeat (CM2 model)",H1,navy,align="left",border=False)
ws.merge_cells("B3:F3"); cell(ws,"B3","Driver-based model. Yellow cells are editable inputs — change them and the P&L tab recalculates. Directional v1 (see notes).",ITAL,border=False)

r=5
cell(ws,f"B{r}","KEY DRIVERS (editable)",WHITE,blue,align="left"); cell(ws,f"C{r}","Value",WHITE,blue,align="center"); cell(ws,f"D{r}","",WHITE,blue); cell(ws,f"E{r}","",WHITE,blue); cell(ws,f"F{r}","Source / logic",WHITE,blue,align="left")
drivers=[
 ("July TOTAL net revenue (ex-GST, post-returns) ₹", 83000000, RS, "SCALE ANCHOR — estimate. Two methods converge ~₹8.3 Cr: (a) COGS grand-total ÷ ~3 months; (b) July paid media ₹3.53 Cr ÷ 43% ad-to-rev. REPLACE with DMR actual."),
 ("New-user share of net revenue %", 0.506, PCT, "July-31 DMR sample (realized orders). Repeat = 1 − this."),
 ("AOV — New user (gross ₹/order)", 2602, RS, "July-31 DMR sample."),
 ("AOV — Repeat user (gross ₹/order)", 3111, RS, "July-31 DMR sample."),
 ("Net Revenue ÷ Gross Revenue", 0.7477, "0.0000", "COGS file grand total: 247.9M/331.6M (removes ~13% returns + GST)."),
 ("Net COGS % of net revenue", 0.4483, PCT, "COGS file grand total: 111.14M/247.9M."),
 ("Fulfilment cost % of net revenue", 0.0914, PCT, "COGS file grand total: 22.65M/247.9M."),
]
rows={}
for i,(lbl,val,fmt,src) in enumerate(drivers):
    rr=r+1+i
    cell(ws,f"B{rr}",lbl,align="left")
    cell(ws,f"C{rr}",val,BOLD,yell,fmt,"center")
    cell(ws,f"D{rr}","",fill=grey); cell(ws,f"E{rr}","",fill=grey)
    cell(ws,f"F{rr}",src,ITAL,align="wrap")
    rows[lbl]=rr
# capture cell refs
D_NETREV=f"'Drivers & Sources'!C{rows[drivers[0][0]]}"
D_NEWSH =f"'Drivers & Sources'!C{rows[drivers[1][0]]}"
D_AOVN  =f"'Drivers & Sources'!C{rows[drivers[2][0]]}"
D_AOVR  =f"'Drivers & Sources'!C{rows[drivers[3][0]]}"
D_NG    =f"'Drivers & Sources'!C{rows[drivers[4][0]]}"
D_COGS  =f"'Drivers & Sources'!C{rows[drivers[5][0]]}"
D_FUL   =f"'Drivers & Sources'!C{rows[drivers[6][0]]}"

r=rows[drivers[-1][0]]+2
cell(ws,f"B{r}","MARKETING ACTUALS — July 2026 (₹)",WHITE,blue,align="left")
cell(ws,f"C{r}","Total spend",WHITE,blue,align="center"); cell(ws,f"D{r}","% to New",WHITE,blue,align="center"); cell(ws,f"E{r}","% to Repeat",WHITE,blue,align="center"); cell(ws,f"F{r}","Source / allocation logic",WHITE,blue,align="left")
mk=[
 ("Meta — Prospecting / Category / Influencer", 16956520, 1.00, 0.00, "Windsor Meta; non-DPA/non-cross-sell campaigns. Pure acquisition → New."),
 ("Meta — Retargeting / DPA / Cross-sell",       9703144, 0.20, 0.80, "Windsor Meta; DPA_Max_Value, DPA_PDP_Views, Cross_Sell_*. Mostly returning audiences."),
 ("Google — PMax (Search+Display+Video)",        8152672, 0.70, 0.30, "Windsor Google Ads. Acquisition-heavy but captures some returning."),
 ("Google — Brand Search",                        489181, 0.40, 0.60, "Windsor Google Ads. Brand keywords skew to existing-intent/returning."),
 ("CRM — Moengage (platform + comms)",            500000, 0.00, 1.00, "PLACEHOLDER — not in API (broadcast push ≈ free). Put actual Moengage invoice. → Repeat."),
]
mkrows={}
r0=r+1
for i,(lbl,spend,pn,pr,src) in enumerate(mk):
    rr=r0+i
    cell(ws,f"B{rr}",lbl,align="left")
    cell(ws,f"C{rr}",spend,BOLD,yell,RS,"center")
    cell(ws,f"D{rr}",pn,None,yell,PCT0,"center")
    cell(ws,f"E{rr}",pr,None,yell,PCT0,"center")
    cell(ws,f"F{rr}",src,ITAL,align="wrap")
    mkrows[lbl]=rr
tot_r=r0+len(mk)
cell(ws,f"B{tot_r}","TOTAL paid media + CRM",BOLD,lblue,align="left")
cell(ws,f"C{tot_r}",f"=SUM(C{r0}:C{tot_r-1})",BOLD,lblue,RS,"center")
cell(ws,f"D{tot_r}",None,None,lblue); cell(ws,f"E{tot_r}",None,None,lblue); cell(ws,f"F{tot_r}",None,None,lblue)
# new/repeat media sums (SUMPRODUCT of spend*pct)
NEWMEDIA=f"SUMPRODUCT('Drivers & Sources'!C{r0}:C{tot_r-1},'Drivers & Sources'!D{r0}:D{tot_r-1})"
REPMEDIA=f"SUMPRODUCT('Drivers & Sources'!C{r0}:C{tot_r-1},'Drivers & Sources'!E{r0}:E{tot_r-1})"

# ============================================================= P&L sheet
p = wb.create_sheet("P&L — New vs Repeat")
p.sheet_view.showGridLines=False
for col,w in {"A":2,"B":34,"C":16,"D":16,"E":16,"F":11}.items(): p.column_dimensions[col].width=w
p.merge_cells("B2:F2"); cell(p,"B2","July 2026 — D2C P&L to CM2 · New vs Repeat User",H1,navy,align="left",border=False)
p.merge_cells("B3:F3"); cell(p,"B3","₹, unless noted. Structural margins from COGS file; segment mix from July-31 DMR sample; media = July actuals.",ITAL,border=False)

hr=5
for c,t,al in [("B","P&L line","left"),("C","New user","center"),("D","Repeat user","center"),("E","Total","center"),("F","% net rev","center")]:
    cell(p,f"{c}{hr}",t,WHITE,blue,align=al)

def prow(r,label,new_f,rep_f,fill=None,fmt=RS,pctcol=True,bold=False,indent=True):
    fnt=BOLD if bold else None
    cell(p,f"B{r}",("   " if indent else "")+label,fnt,fill,align="left")
    cell(p,f"C{r}",new_f,fnt,fill,fmt,"right")
    cell(p,f"D{r}",rep_f,fnt,fill,fmt,"right")
    cell(p,f"E{r}",f"=C{r}+D{r}",fnt,fill,fmt,"right")
    if pctcol:
        cell(p,f"F{r}",f"=IFERROR(E{r}/$E${NETREV_R},\"\")",fnt,fill,PCT,"center")
    else:
        cell(p,f"F{r}","",fnt,fill)
    return r

# Net revenue row
NETREV_R=6
cell(p,f"B{NETREV_R}","Net Revenue (ex-GST, post-returns)",BOLD,lblue,align="left")
cell(p,f"C{NETREV_R}",f"={D_NETREV}*{D_NEWSH}",BOLD,lblue,RS,"right")
cell(p,f"D{NETREV_R}",f"={D_NETREV}*(1-{D_NEWSH})",BOLD,lblue,RS,"right")
cell(p,f"E{NETREV_R}",f"=C{NETREV_R}+D{NETREV_R}",BOLD,lblue,RS,"right")
cell(p,f"F{NETREV_R}","100%",BOLD,lblue,None,"center")

r=7
prow(r,"Gross revenue (memo, incl GST+returns)",f"=C{NETREV_R}/{D_NG}",f"=D{NETREV_R}/{D_NG}",grey,RS,True); GROSS_R=r; r+=1
prow(r,"Orders (derived = gross ÷ AOV)",f"=C{GROSS_R}/{D_AOVN}",f"=D{GROSS_R}/{D_AOVR}",grey,RS,False); ORD_R=r; r+=1
prow(r,"Less: Net COGS",f"=-C{NETREV_R}*{D_COGS}",f"=-D{NETREV_R}*{D_COGS}",None,RS,True); r+=1
PM_R=r; cell(p,f"B{r}","= Product Margin",BOLD,green,align="left")
cell(p,f"C{r}",f"=C{NETREV_R}+C{r-1}",BOLD,green,RS,"right"); cell(p,f"D{r}",f"=D{NETREV_R}+D{r-1}",BOLD,green,RS,"right")
cell(p,f"E{r}",f"=C{r}+D{r}",BOLD,green,RS,"right"); cell(p,f"F{r}",f"=E{r}/E{NETREV_R}",BOLD,green,PCT,"center"); r+=1
prow(r,"Less: Fulfilment / logistics",f"=-C{NETREV_R}*{D_FUL}",f"=-D{NETREV_R}*{D_FUL}",None,RS,True); r+=1
CM1_R=r; cell(p,f"B{r}","= CM1 (post-fulfilment)",BOLD,green,align="left")
cell(p,f"C{r}",f"=C{PM_R}+C{r-1}",BOLD,green,RS,"right"); cell(p,f"D{r}",f"=D{PM_R}+D{r-1}",BOLD,green,RS,"right")
cell(p,f"E{r}",f"=C{r}+D{r}",BOLD,green,RS,"right"); cell(p,f"F{r}",f"=E{r}/E{NETREV_R}",BOLD,green,PCT,"center"); r+=1
# marketing
prow(r,"Less: Performance media (Meta+Google)",
     f"=-({NEWMEDIA}-'Drivers & Sources'!C{mkrows[mk[4][0]]}*'Drivers & Sources'!D{mkrows[mk[4][0]]})",
     f"=-({REPMEDIA}-'Drivers & Sources'!C{mkrows[mk[4][0]]}*'Drivers & Sources'!E{mkrows[mk[4][0]]})",
     None,RS,True); MED_R=r; r+=1
prow(r,"Less: CRM (Moengage)",
     f"=-'Drivers & Sources'!C{mkrows[mk[4][0]]}*'Drivers & Sources'!D{mkrows[mk[4][0]]}",
     f"=-'Drivers & Sources'!C{mkrows[mk[4][0]]}*'Drivers & Sources'!E{mkrows[mk[4][0]]}",
     None,RS,True); CRM_R=r; r+=1
CM2_R=r; cell(p,f"B{r}","= CM2 (post-marketing)",WHITE,navy,align="left")
cell(p,f"C{r}",f"=C{CM1_R}+C{MED_R}+C{CRM_R}",WHITE,navy,RS,"right")
cell(p,f"D{r}",f"=D{CM1_R}+D{MED_R}+D{CRM_R}",WHITE,navy,RS,"right")
cell(p,f"E{r}",f"=C{r}+D{r}",WHITE,navy,RS,"right")
cell(p,f"F{r}",f"=E{r}/E{NETREV_R}",WHITE,navy,PCT,"center"); r+=2

# memo metrics
cell(p,f"B{r}","MEMO — unit economics",WHITE,blue,align="left")
cell(p,f"C{r}","New",WHITE,blue,align="center");cell(p,f"D{r}","Repeat",WHITE,blue,align="center");cell(p,f"E{r}","Blended",WHITE,blue,align="center");cell(p,f"F{r}","",WHITE,blue); r+=1
cell(p,f"B{r}","Marketing per order (CAC / retention ₹)",align="left")
cell(p,f"C{r}",f"=-(C{MED_R}+C{CRM_R})/C{ORD_R}",None,None,RS,"right")
cell(p,f"D{r}",f"=-(D{MED_R}+D{CRM_R})/D{ORD_R}",None,None,RS,"right")
cell(p,f"E{r}",f"=-(E{MED_R}+E{CRM_R})/E{ORD_R}",None,None,RS,"right"); cell(p,f"F{r}","",border=False); r+=1
cell(p,f"B{r}","CM1 per order ₹",align="left")
for cc in "CDE": cell(p,f"{cc}{r}",f"={cc}{CM1_R}/{cc}{ORD_R}",None,None,RS,"right")
cell(p,f"F{r}","",border=False); r+=1
cell(p,f"B{r}","CM2 per order ₹",BOLD,align="left")
for cc in "CDE": cell(p,f"{cc}{r}",f"={cc}{CM2_R}/{cc}{ORD_R}",BOLD,None,RS,"right")
cell(p,f"F{r}","",border=False); r+=2

cell(p,f"B{r}","Read: New users are typically CM2-negative (acquisition cost > first-order contribution); repeat users",ITAL,border=False); r+=1
cell(p,f"B{r}","are strongly CM2-positive. Blended CM2 should tie to the COGS file's ~2.6%. LTV justifies new-user loss.",ITAL,border=False)

# ============================================================= COGS reference
cr = wb.create_sheet("COGS Reference")
cr.sheet_view.showGridLines=False
for col,w in {"A":2,"B":26,"C":15,"D":15,"E":13,"F":13}.items(): cr.column_dimensions[col].width=w
cell(cr,"B2","COGS / CM file — grand total (all months, all platforms)",H2,border=False)
cell(cr,"B3","Source: Web_Updated_cogs_CMFile.xlsx · Sheet2 pivot (Grand Total row). Ratios drive the P&L.",ITAL,border=False)
gt=[("Revenue",331557725),("Return Sales",43246094),("Net Sales",288311631),("Net Revenue",247899469),
    ("Net COGS",111138979),("Product Margin",136760490),("Est. fulfilment cost",22651338),
    ("CM1",114109152),("CM2",6509793),("Ad Spends",107599359),("QTY",207715)]
rr=5
cell(cr,f"B{rr}","Metric",WHITE,blue,align="left");cell(cr,f"C{rr}","Value ₹",WHITE,blue,align="center");cell(cr,f"D{rr}","% of Net Rev",WHITE,blue,align="center"); rr+=1
nrv=247899469
for lbl,val in gt:
    cell(cr,f"B{rr}",lbl,align="left"); cell(cr,f"C{rr}",val,None,None,RS,"right")
    if lbl not in ("QTY",): cell(cr,f"D{rr}",val/nrv,None,None,PCT,"center")
    else: cell(cr,f"D{rr}","",border=True)
    rr+=1
rr+=1
cell(cr,f"B{rr}","Derived ratios used in model",H2,border=False); rr+=1
for lbl,val,fmt in [("Net Rev ÷ Gross Rev",0.7477,"0.0000"),("Net COGS % of Net Rev",0.4483,PCT),
    ("Product Margin % of Net Rev",0.5517,PCT),("Fulfilment % of Net Rev",0.0914,PCT),
    ("CM1 % of Net Rev",0.4603,PCT),("CM2 % of Net Rev (blended actual)",0.0263,PCT)]:
    cell(cr,f"B{rr}",lbl,align="left"); cell(cr,f"C{rr}",val,BOLD,grey,fmt,"center"); rr+=1

# ============================================================= Method & caveats
mt = wb.create_sheet("Method & Caveats")
mt.sheet_view.showGridLines=False
mt.column_dimensions["B"].width=110
cell(mt,"B2","Method, sources & caveats",H1,navy,align="left",border=False)
notes=[
 "PURPOSE — July 2026 D2C P&L to CM2, split New vs Repeat users. Built as a driver model so actuals can be dropped in.",
 "",
 "DATA SOURCES",
 "• Structural margins (COGS%, Product Margin%, Fulfilment%, CM1/CM2%) — Web_Updated_cogs_CMFile.xlsx, Sheet2 grand total (all-month blend).",
 "• New-vs-Repeat mix (rev share, AOV, coupon rate, category mix) — july_DMR_unmasked.csv, 'New User' flag (TRUE=new / FALSE=repeat).",
 "• Meta & Google spend — Windsor.ai (facebook + google_ads), July 2026 actuals, by campaign.",
 "• CRM — Moengage (broadcast push ≈ zero marginal cost; platform fee is an input, not API-exposed).",
 "",
 "KEY CAVEAT — the July DMR is 47MB and cannot be fully aggregated through available tools (10MB download cap; text",
 "extraction truncates to only July-31 rows as the file is date-sorted). So the new/repeat SPLIT ratios (rev share 50.6/49.4,",
 "AOV ₹2,602/₹3,111, coupon rates) come from the JULY-31 SAMPLE (816 realized orders) — directionally sound but 1 day,",
 "month-end. The TOTAL SCALE (₹8.3 Cr net rev) is an estimate. Both are yellow inputs — replace with full-month DMR actuals.",
 "",
 "TO FINALISE (makes every number exact): a July DMR pivot — Rows: New User × Category; Values: Sum of Product Grand",
 "Total(FF), Sum of Order Discount + Product Discount, Sum of Qty, Distinct Order No. — split by Last Status (to separate",
 "delivered / returned / cancelled). Drop that in and the model is final.",
 "",
 "MARKETING TRIANGULATION — Meta split into prospecting (→New) vs DPA/retargeting/cross-sell (→mostly Repeat);",
 "Google PMax mostly acquisition, Brand Search mostly returning; CRM → Repeat. All allocation %s are editable inputs.",
 "",
 "COUPONS — Product Grand Total(FF) is already net of coupon, so discounts are captured ABOVE CM1 (in net revenue).",
 "They are NOT re-subtracted in CM2. Sample discount intensity: New ~19% / Repeat ~26% of realized revenue.",
 "",
 "VALIDATION — bottom-up blended CM2 (~2–3% of net rev) ties to the COGS file's blended CM2 of 2.6%, a good cross-check.",
]
rr=4
for n in notes:
    f=BOLD if (n.isupper() and n) or n.startswith(("DATA","KEY","TO ","MARKETING","COUPONS","VALIDATION","PURPOSE")) else ITAL
    cell(mt,f"B{rr}",n,f,border=False); rr+=1

path="/home/user/claude/out/DailyObjects_July2026_PnL_New_vs_Repeat.xlsx"
wb.save(path)
print("saved",path)
