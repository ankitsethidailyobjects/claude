from meta_2026 import JUN, JUL, categorize
from collections import defaultdict
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

def agg(data):
    c=defaultdict(lambda:[0,0,0.0])
    for n,sp,od,rev in data:
        k=categorize(n); c[k][0]+=sp; c[k][1]+=od; c[k][2]+=rev
    return c
jun=agg(JUN); jul=agg(JUL)

# ---- core numbers ----
newT,repT=22727,19411
newCVR,repCVR=0.00620,0.01485
AOV_new,AOV_rep=2450,2700
TARGET=10.5e7
rep_orders=21864; new_orders=18762; tot_orders=rep_orders+new_orders
new_users=2968515; rep_users=1429878
newCVR_aug,repCVR_aug=0.00632,0.01529
new_spend=new_orders*903; rep_spend=round(rep_orders*0.35*865); tot_spend=new_spend+rep_spend
rev=new_orders*AOV_new+rep_orders*AOV_rep
meta_rev=rev*0.76

LTV_TIER={'Power Bank':'HIGH','Stack':'HIGH','Charging Station (Loft)':'HIGH','Node':'MED',
          'Tech Kit (Park)':'MED','Bags / DG':'MED','Desk Organiser (Bar)':'MED','Watch Bands':'LOW'}
newcats={k:v for k,v in jul.items() if k in LTV_TIER}
jsum=sum(v[2] for v in newcats.values())
tilt={'HIGH':1.15,'MED':1.0,'LOW':0.85}
w={k:newcats[k][2]/jsum*tilt[LTV_TIER[k]] for k in newcats}; ws=sum(w.values())
new_rev_pool=new_orders*AOV_new
rep_rev_pool=rep_orders*AOV_rep
# repeat skew (repeat buyers over-index on high-LTV consumables)
rtilt={'HIGH':1.30,'MED':1.0,'LOW':0.70}
rw={k:newcats[k][2]/jsum*rtilt[LTV_TIER[k]] for k in newcats}; rws=sum(rw.values())

cat_rows=[]
for k in sorted(newcats,key=lambda x:-(w[x]/ws)):
    nshare=w[k]/ws; rshare=rw[k]/rws
    nrev=new_rev_pool*nshare; rrev=rep_rev_pool*rshare; trev=nrev+rrev
    roas=jul[k][2]/jul[k][0]; cac=jul[k][0]/jul[k][1]; aov=jul[k][2]/jul[k][1]
    norders=nrev/AOV_new; nusers=norders/newCVR_aug
    cat_rows.append(dict(cat=k,ltv=LTV_TIER[k],julrev=newcats[k][2]/0.76,nrev=nrev,rrev=rrev,
                         trev=trev,roas=roas,cac=cac,norders=norders,nusers=nusers))

# ============ workbook ============
wb=openpyxl.Workbook()
NAVY="1F2A44"; BLUE="2E5AAC"; LBLUE="DCE6F7"; GREY="F2F2F2"; GREEN="2E7D46"; LGREEN="DDF0E1"
AMBER="B8860B"; LAMBER="FBF0D5"; WHITE="FFFFFF"
thin=Side(style='thin',color="C9C9C9")
bd=Border(left=thin,right=thin,top=thin,bottom=thin)
def st(c,bold=False,sz=11,color="000000",fill=None,align='left',wrap=False,border=True,num=None):
    c.font=Font(bold=bold,size=sz,color=color,name='Calibri')
    c.alignment=Alignment(horizontal=align,vertical='center',wrap_text=wrap)
    if fill: c.fill=PatternFill('solid',fgColor=fill)
    if border: c.border=bd
    if num: c.number_format=num
def title(ws,txt,sub,ncol):
    ws.merge_cells(start_row=1,start_column=1,end_row=1,end_column=ncol)
    c=ws.cell(1,1,txt); st(c,True,16,WHITE,NAVY,'left',border=False); ws.row_dimensions[1].height=28
    ws.merge_cells(start_row=2,start_column=1,end_row=2,end_column=ncol)
    c=ws.cell(2,1,sub); st(c,False,10,"555555",align='left',border=False); ws.row_dimensions[2].height=16

RS='"₹"#,##0'; RSCR='"₹"#,##0.00" cr"'; PCT='0.0%'; NUM='#,##0'; ROAS='0.00"x"'

# ---------- Sheet 1: Executive Summary ----------
s=wb.active; s.title="1. Exec Summary"
title(s,"DailyObjects — August 2026 D2C Revenue Plan","Target ₹10.5 cr at maximum ROAS efficiency  •  Baseline: Meta June/July 2026 + Daily New-vs-Repeat tracker  •  Prepared "+"05-Aug-2026",6)
r=4
hdr=["Metric","July 2026 (actual)","August (target)","Δ vs July","Basis / lever",""]
for i,h in enumerate(hdr,1): st(s.cell(r,i,h),True,11,WHITE,BLUE,'left' if i in(1,5) else 'center',wrap=True)
rows=[
 ("Total D2C revenue","₹10.81 cr","₹10.50 cr","−3%","Hold-and-optimise month",""),
 ("Total orders","42,138","40,626","−4%","Higher AOV + repeat tilt",""),
 ("New orders","22,727 (54%)","18,762 (46%)","−17%","Trim low-ROAS new, keep high-LTV",""),
 ("Repeat orders","19,411 (46%)","21,864 (54%)","+13%","Cheaper, 2.4× CVR, high LTV",""),
 ("New users required","3.67 M","2.97 M","−19%","@ new CVR 0.63%",""),
 ("Repeat users required","1.31 M","1.43 M","+9%","@ repeat CVR 1.53% (CRM/app)",""),
 ("Meta spend","₹2.67 cr","₹2.36 cr","−12%","Efficiency reallocation",""),
 ("Blended Meta ROAS","3.01x","3.39x","+0.38x","Above Aug1-4 bar of 3.28x",""),
 ("Avg blended CAC (new)","₹903","₹880","−3%","Category re-mix to high ROAS",""),
 ("Cost per repeat order","₹865 (paid nudge)","₹865","flat","Only ~35% of repeat is paid",""),
]
r=5
for row in rows:
    for i,v in enumerate(row,1):
        st(s.cell(r,i,v),i==1,11,fill=GREY if r%2 else WHITE,align='left' if i in(1,5) else 'center',wrap=True)
    r+=1
r+=1
st(s.cell(r,1,"THE ASK TO PERFORMANCE MARKETING (August goal)"),True,12,NAVY); r+=1
asks=[
 "1.  New users: 2.97 M  →  18,762 new orders. Concentrate spend on Power Bank, Stack, Node (ROAS >3.15, high/med LTV).",
 "2.  Repeat users: 1.43 M  →  21,864 repeat orders. Drive via CRM + app push + retargeting; freebie weekends reactivate.",
 "3.  Mix goal: 46% new / 54% repeat orders (was 54/46) — shifts blend to efficiency without losing topline.",
 "4.  Hold blended Meta ROAS ≥ 3.28x (last-4-day bar); plan lands 3.39x.",
 "5.  4 freebie weekends add ~₹0.38 cr incremental at accretive ROAS (see tab 5).",
]
for a in asks:
    s.merge_cells(start_row=r,start_column=1,end_row=r,end_column=6)
    st(s.cell(r,1,a),False,10,align='left',fill=LBLUE,wrap=True); s.row_dimensions[r].height=30; r+=1
widths=[30,20,20,12,34,4]
for i,wd in enumerate(widths,1): s.column_dimensions[get_column_letter(i)].width=wd

# ---------- Sheet 2: New vs Repeat build ----------
s=wb.create_sheet("2. New vs Repeat")
title(s,"New vs Repeat — August target build","Working backwards from ₹10.5 cr. Users = orders ÷ conversion rate.",6)
r=4
for i,h in enumerate(["Driver","New users","Repeat users","Blended / Total","Note",""],1):
    st(s.cell(r,i,h),True,11,WHITE,BLUE,'left' if i in(1,5) else 'center',wrap=True)
data=[
 ("Orders required (Aug)",18762,21864,40626,"46% / 54% split",NUM),
 ("Segment AOV (₹)",2450,2700,2575,"Repeat premium on trust/bundles",RS),
 ("Revenue (₹ cr)",0.46,0.59,1.05,"×10 → ₹4.60cr new + ₹5.90cr repeat = ₹10.5cr",None),
 ("Conversion rate",0.00632,0.01529,None,"Repeat converts 2.4× better",PCT),
 ("USERS REQUIRED",2968515,1429878,4398393,"≈ 141,884 sessions/day",NUM),
 ("Cost per order (₹)",903,865,None,"New via prospecting; repeat via paid nudge",RS),
 ("Marketing spend (₹ cr)",1.69,0.66,2.36,"Repeat only 35% paid-assisted",None),
 ("Segment ROAS",None,None,None,"New 2.7x / Repeat 8.9x incl. owned",None),
]
r=5
for row in data:
    lbl,nv,rv,tv,note,fmt=row
    st(s.cell(r,1,lbl),True,10,align='left',fill=GREY if r%2 else WHITE,wrap=True)
    for i,v in [(2,nv),(3,rv),(4,tv)]:
        c=s.cell(r,i,v if v is not None else "—")
        st(c,False,10,align='center',fill=GREY if r%2 else WHITE)
        if fmt and v is not None: c.number_format=fmt
    st(s.cell(r,5,note),False,9,"555555",align='left',fill=GREY if r%2 else WHITE,wrap=True)
    st(s.cell(r,6,""),border=False)
    r+=1
r+=1
st(s.cell(r,1,"Repeat is the efficiency engine: same ₹, 2.4× the conversion, higher LTV. But new intake feeds next quarter's repeat pool —"),False,9,NAVY,align='left'); r+=1
st(s.cell(r,1,"do not starve acquisition below ~2.9 M new users or Sept–Oct repeat base contracts."),False,9,NAVY,align='left')
for i,wd in enumerate([26,16,16,18,40,3],1): s.column_dimensions[get_column_letter(i)].width=wd

# ---------- Sheet 3: Category targets ----------
s=wb.create_sheet("3. Category Targets")
title(s,"Category-level August targets — backward from ₹10.5 cr","Split tilted to ROAS + LTV. High-LTV (Power Bank, Stack, Charging) get share uplift.",10)
r=4
H=["Category","LTV tier","Jul D2C rev (est)","Aug NEW rev","Aug REPEAT rev","Aug TOTAL target","Share","Baseline ROAS","New CAC","New users"]
for i,h in enumerate(H,1): st(s.cell(r,i,h),True,10,WHITE,BLUE,'left' if i<=2 else 'center',wrap=True)
r=5
tot=defaultdict(float)
for cr in cat_rows:
    fill=LGREEN if cr['ltv']=='HIGH' else (LAMBER if cr['ltv']=='LOW' else (GREY if r%2 else WHITE))
    vals=[cr['cat'],cr['ltv'],cr['julrev']/1e7,cr['nrev']/1e7,cr['rrev']/1e7,cr['trev']/1e7,
          cr['trev']/TARGET,cr['roas'],cr['cac'],cr['nusers']]
    fmts=[None,None,RSCR,RSCR,RSCR,RSCR,PCT,ROAS,RS,NUM]
    for i,(v,f) in enumerate(zip(vals,fmts),1):
        c=s.cell(r,i,v); st(c,i==1,10,align='left' if i<=2 else 'center',fill=fill)
        if f: c.number_format=f
    tot['n']+=cr['nrev']; tot['rr']+=cr['rrev']; tot['t']+=cr['trev']; tot['u']+=cr['nusers']
    r+=1
# total row
tv=["TOTAL (acquisition-led)","",sum(c['julrev'] for c in cat_rows)/1e7,tot['n']/1e7,tot['rr']/1e7,tot['t']/1e7,tot['t']/TARGET,3.35,880,tot['u']]
fmts=[None,None,RSCR,RSCR,RSCR,RSCR,PCT,ROAS,RS,NUM]
for i,(v,f) in enumerate(zip(tv,fmts),1):
    c=s.cell(r,i,v); st(c,True,10,WHITE,NAVY,'left' if i<=2 else 'center')
    if f: c.number_format=f
r+=2
st(s.cell(r,1,"HIGH-LTV categories (green) get a share uplift; Watch Bands (amber, low LTV/ROAS) is dialled down. "),False,9,NAVY,align='left'); r+=1
st(s.cell(r,1,"Repeat revenue skews harder to Power Bank / Stack / Charging — these are the re-purchase & upgrade engines."),False,9,NAVY,align='left')
for i,wd in enumerate([24,10,16,14,15,17,9,12,10,12],1): s.column_dimensions[get_column_letter(i)].width=wd

# ---------- Sheet 4: Meta baseline (June/July) ----------
s=wb.create_sheet("4. Meta Baseline")
title(s,"Meta baseline — June & July 2026 by category","Source: Meta Ads (DailyObjects Prepaid). CAC = spend ÷ orders. Retargeting ≈ repeat proxy.",11)
r=4
H=["Category","Jun spend","Jun orders","Jun rev","Jun ROAS","Jun CAC","Jul spend","Jul orders","Jul rev","Jul ROAS","Jul CAC"]
for i,h in enumerate(H,1): st(s.cell(r,i,h),True,10,WHITE,BLUE,'left' if i==1 else 'center',wrap=True)
r=5
allcats=sorted(set(list(jun)+list(jul)),key=lambda k:-(jul.get(k,[0,0,0])[2]))
for k in allcats:
    j=jun.get(k,[0,0,0]); l=jul.get(k,[0,0,0])
    fill=GREY if r%2 else WHITE
    vals=[k,j[0]/1e5,j[1],j[2]/1e5,(j[2]/j[0] if j[0] else 0),(j[0]/j[1] if j[1] else 0),
          l[0]/1e5,l[1],l[2]/1e5,(l[2]/l[0] if l[0] else 0),(l[0]/l[1] if l[1] else 0)]
    LK='"₹"#,##0.0" L"'
    fmts=[None,LK,NUM,LK,ROAS,RS,LK,NUM,LK,ROAS,RS]
    for i,(v,f) in enumerate(zip(vals,fmts),1):
        c=s.cell(r,i,v); st(c,i==1,9,align='left' if i==1 else 'center',fill=fill)
        if f and isinstance(v,(int,float)): c.number_format=f
    r+=1
jt=[sum(jun[k][i] for k in jun) for i in range(3)]; lt=[sum(jul[k][i] for k in jul) for i in range(3)]
LK='"₹"#,##0.0" L"'
vals=["TOTAL",jt[0]/1e5,jt[1],jt[2]/1e5,jt[2]/jt[0],jt[0]/jt[1],lt[0]/1e5,lt[1],lt[2]/1e5,lt[2]/lt[0],lt[0]/lt[1]]
fmts=[None,LK,NUM,LK,ROAS,RS,LK,NUM,LK,ROAS,RS]
for i,(v,f) in enumerate(zip(vals,fmts),1):
    c=s.cell(r,i,v); st(c,True,9,WHITE,NAVY,'left' if i==1 else 'center')
    if f and isinstance(v,(int,float)): c.number_format=f
for i,wd in enumerate([24]+[11]*10,1): s.column_dimensions[get_column_letter(i)].width=wd

# ---------- Sheet 5: Weekend / Freebie ----------
s=wb.create_sheet("5. Weekend Freebie")
title(s,"Weekend freebie plan — incremental revenue & ROAS lift","Gift-with-purchase above threshold. Lifts AOV, new-CVR and repeat reactivation. Aug 1-2 already ran.",7)
r=4
for i,h in enumerate(["Weekend","Status","Base 2-day rev","Freebie uplift (+14%)","Weekend total","Mechanic","ROAS effect"],1):
    st(s.cell(r,i,h),True,10,WHITE,BLUE,'left' if i in(1,2,6) else 'center',wrap=True)
daily=rev/31
wk=[("Aug 1–2","Ran","Threshold gift ₹1499+ (charging cable / pouch)","+0.38x on wknd, blended 3.28x observed"),
    ("Aug 8–9","Plan","Free power-bank sleeve on Stack/PB > ₹1999","AOV +8%, repeat-reactivation push"),
    ("Aug 15–16 (I-Day)","Plan","Independence combo: free gift + app-only code","Biggest wknd; app CRM blast"),
    ("Aug 22–23","Plan","Mystery freebie > ₹1499, high-LTV cats","Skew to Power Bank / Charging"),
    ("Aug 29–30","Plan","Month-end: free gift + loyalty 2x points","Repeat-heavy close")]
r=5; tot_lift=0
for name,status,mech,eff in wk:
    base=daily*2; lift=base*0.14; tot_lift+=lift
    fill=LAMBER if status=="Ran" else (GREY if r%2 else WHITE)
    st(s.cell(r,1,name),True,10,align='left',fill=fill)
    st(s.cell(r,2,status),False,10,align='left',fill=fill)
    for i,v in [(3,base),(4,lift),(5,base+lift)]:
        c=s.cell(r,i,v); st(c,False,10,align='center',fill=fill); c.number_format='"₹"#,##0.0,,"L"' if False else '"₹"#,##0'
    for i,v in [(3,base),(4,lift),(5,base+lift)]:
        s.cell(r,i).value=round(v); s.cell(r,i).number_format='"₹"#,##0'
    st(s.cell(r,6,mech),False,9,align='left',fill=fill,wrap=True)
    st(s.cell(r,7,eff),False,9,align='left',fill=fill,wrap=True)
    r+=1
st(s.cell(r,1,"TOTAL"),True,10,WHITE,NAVY,'left')
st(s.cell(r,2,"—"),True,10,WHITE,NAVY,'center')
c=s.cell(r,4,round(tot_lift)); st(c,True,10,WHITE,NAVY,'center'); c.number_format='"₹"#,##0'
st(s.cell(r,5,""),fill=NAVY); st(s.cell(r,3,""),fill=NAVY); st(s.cell(r,6,"~₹0.38 cr incremental for the month"),True,9,WHITE,NAVY,'left'); st(s.cell(r,7,"Accretive to blended ROAS"),True,9,WHITE,NAVY,'left')
for i,wd in enumerate([18,8,16,20,16,40,34],1): s.column_dimensions[get_column_letter(i)].width=wd
r+=3
st(s.cell(r,1,"Why freebie helps ROAS: gift cost (₹40–120) is far below the AOV lift (+₹200) and the reactivation of dormant repeat buyers"),False,9,NAVY,align='left'); r+=1
st(s.cell(r,1,"who convert at 1.5% with near-zero media cost. Fund gifts from margin, cap at high-LTV carts to protect contribution."),False,9,NAVY,align='left')

wb.save("/home/user/claude/DailyObjects_August_D2C_Plan.xlsx")
print("saved xlsx with sheets:",wb.sheetnames)
print("cat total check Rs %.2f cr"%((tot['t'])/1e7))
