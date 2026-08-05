import json
from docx import Document
from docx.shared import Pt, RGBColor, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

d=json.load(open('/home/user/claude/delta.json'))
rows=d['rows']; tot=d['tot']; J=d['J']; A=d['A']

NAVY=RGBColor(0x1F,0x2A,0x44); BLUE=RGBColor(0x2E,0x5A,0xAC); GREY=RGBColor(0x55,0x55,0x55)
GREEN=RGBColor(0x2E,0x7D,0x46); RED=RGBColor(0xB0,0x3A,0x2E); WHITE=RGBColor(0xFF,0xFF,0xFF)
doc=Document()
st=doc.styles['Normal']; st.font.name='Calibri'; st.font.size=Pt(10.5)

def shade(cell,hexc):
    tcPr=cell._tc.get_or_add_tcPr(); sh=OxmlElement('w:shd')
    sh.set(qn('w:val'),'clear'); sh.set(qn('w:fill'),hexc); tcPr.append(sh)
def setcell(cell,text,bold=False,color=None,size=9,al='left',fill=None):
    cell.text=""; p=cell.paragraphs[0]
    p.alignment={'left':WD_ALIGN_PARAGRAPH.LEFT,'center':WD_ALIGN_PARAGRAPH.CENTER,'right':WD_ALIGN_PARAGRAPH.RIGHT}[al]
    run=p.add_run(text); run.bold=bold; run.font.size=Pt(size)
    if color: run.font.color.rgb=color
    if fill: shade(cell,fill)
def H(text,size=15,color=NAVY,space_before=10,space_after=4):
    p=doc.add_paragraph(); p.space_before=Pt(space_before)
    r=p.add_run(text); r.bold=True; r.font.size=Pt(size); r.font.color.rgb=color
    p.paragraph_format.space_before=Pt(space_before); p.paragraph_format.space_after=Pt(space_after)
    return p
def eyebrow(text):
    p=doc.add_paragraph(); r=p.add_run(text.upper()); r.bold=True; r.font.size=Pt(8.5)
    r.font.color.rgb=BLUE; r.font.name='Calibri'
    pf=p.paragraph_format; pf.space_after=Pt(1)
    # letter spacing
    return p
def body(text,size=10.5,color=None,bold=False,after=6):
    p=doc.add_paragraph(); r=p.add_run(text); r.font.size=Pt(size); r.bold=bold
    if color:r.font.color.rgb=color
    p.paragraph_format.space_after=Pt(after); return p
def bullet(text,bold_lead=None):
    p=doc.add_paragraph(style='List Bullet')
    if bold_lead:
        r=p.add_run(bold_lead); r.bold=True; r.font.size=Pt(10.5)
        r2=p.add_run(text); r2.font.size=Pt(10.5)
    else:
        r=p.add_run(text); r.font.size=Pt(10.5)
    p.paragraph_format.space_after=Pt(3); return p

def header_row(tbl,headers,fill='1F2A44'):
    hdr=tbl.rows[0].cells
    for i,h in enumerate(headers):
        setcell(hdr[i],h,bold=True,color=WHITE,size=8.5,al='center' if i>0 else 'left',fill=fill)

# ---------------- Title ----------------
eyebrow("Performance Marketing · Monthly Plan")
t=doc.add_paragraph(); r=t.add_run("DailyObjects — August 2026 D2C Revenue Plan")
r.bold=True; r.font.size=Pt(22); r.font.color.rgb=NAVY
sub=doc.add_paragraph(); r=sub.add_run("Hit ₹10.5 cr at maximum ROAS efficiency by shifting the new-vs-repeat mix and tilting spend to high-LTV categories.")
r.font.size=Pt(11); r.font.color.rgb=GREY
meta=doc.add_paragraph(); r=meta.add_run("Prepared 05 Aug 2026   ·   Baseline: Meta + D2C tracker, June/July 2026   ·   ROAS bar to hold: 3.28x (Aug 1–4)")
r.font.size=Pt(9); r.font.color.rgb=GREY
doc.add_paragraph()

# ---------------- 1. Exec summary ----------------
H("1.  The August goal", 15)
body("The plan is a hold-and-optimise month: match July's topline at a better blended ROAS. The lever is mix — "
     "move order share from 54% new / 46% repeat (July) to 46% new / 54% repeat, because repeat traffic converts "
     "2.4× better and needs paid media on only ~35% of orders.")
tbl=doc.add_table(rows=1,cols=4); tbl.style='Table Grid'; tbl.alignment=WD_TABLE_ALIGNMENT.CENTER
header_row(tbl,["Metric","July 2026 actual","August target","Δ vs July"],fill='2E5AAC')
kpi=[("Total D2C revenue","₹10.81 cr","₹10.50 cr","−3%"),
     ("Total orders","42,138","40,626","−4%"),
     ("New orders (users)","22,727  (3.67 M)","18,762  (2.97 M)","−17% ord"),
     ("Repeat orders (users)","19,411  (1.31 M)","21,864  (1.43 M)","+13% ord"),
     ("Order mix new / repeat","54% / 46%","46% / 54%","tilt to repeat"),
     ("Meta spend","₹2.67 cr","₹2.36 cr","−12%"),
     ("Blended Meta ROAS","3.01x","3.39x","+0.38x"),
     ("New CAC / Repeat cost","₹903 / ₹865","₹880 / ₹865","hold")]
for i,(a,b,c,e) in enumerate(kpi):
    cells=tbl.add_row().cells; f='F2F2F2' if i%2 else None
    setcell(cells[0],a,bold=True,size=9.5,fill=f)
    setcell(cells[1],b,size=9.5,al='center',fill=f)
    setcell(cells[2],c,size=9.5,al='center',fill=f)
    setcell(cells[3],e,size=9.5,al='center',color=GREEN,fill=f)

# ---------------- 2. New vs repeat ----------------
H("2.  New vs repeat — the target build", 15)
body("Working backwards from ₹10.5 cr. Users = orders ÷ conversion rate (from the daily new-vs-repeat tracker, web+app).")
tbl=doc.add_table(rows=1,cols=4); tbl.style='Table Grid'
header_row(tbl,["Driver","New","Repeat","Total / blended"])
nr=[("Orders required","18,762","21,864","40,626"),
    ("Segment AOV","₹2,450","₹2,700","₹2,575"),
    ("Revenue","₹4.60 cr","₹5.90 cr","₹10.50 cr"),
    ("Conversion rate","0.63%","1.53%","—"),
    ("Users required","2,968,515","1,429,878","4,398,393"),
    ("Cost per order","₹903","₹865","—"),
    ("Marketing spend","₹1.69 cr","₹0.66 cr","₹2.36 cr"),
    ("Segment ROAS","2.7x","8.9x","4.5x (D2C) / 3.4x (Meta)")]
for i,(a,b,c,e) in enumerate(nr):
    cells=tbl.add_row().cells; f='F2F2F2' if i%2 else None
    setcell(cells[0],a,bold=True,size=9.5,fill=f)
    for j,v in enumerate([b,c,e],1): setcell(cells[j],v,size=9.5,al='center',fill=f)
body("")
body("Repeat is the efficiency engine — same rupee, 2.4× the conversion, higher LTV. Guardrail: keep new intake "
     "≥ ~2.9 M users, or the Sept–Oct repeat pool contracts.", color=NAVY, bold=False)

# ---------------- 3. Category targets ----------------
H("3.  Category-level targets (backward from ₹10.5 cr)", 15)
body("Split tilted to ROAS + LTV. High-LTV categories (Power Bank, Stack, Charging Station) get a share uplift; Watch Bands is dialled down.")
tbl=doc.add_table(rows=1,cols=6); tbl.style='Table Grid'
header_row(tbl,["Category","LTV","Aug target","Share","Baseline ROAS","New CAC"])
cat3=[("Power Bank","HIGH","₹1.22 cr","11.6%","3.29x","₹959"),
      ("Stack","HIGH","₹1.08 cr","10.3%","3.23x","₹708"),
      ("Node","MED","₹0.88 cr","8.4%","3.17x","₹1,039"),
      ("Bags / DG","MED","₹0.43 cr","4.1%","3.18x","₹727"),
      ("Tech Kit (Park)","MED","₹0.30 cr","2.9%","2.79x","₹1,089"),
      ("Charging Station (Loft)","HIGH","₹0.24 cr","2.3%","2.78x","₹1,356"),
      ("Desk Organiser (Bar)","MED","₹0.23 cr","2.2%","3.00x","₹1,035"),
      ("Watch Bands","LOW","₹0.23 cr","2.2%","2.91x","₹959"),
      ("New-acquisition subtotal","","₹4.60 cr","43.8%","3.35x","₹880"),
      ("Repeat / owned pool","","₹5.90 cr","56.2%","8.9x","₹303")]
for i,(a,b,c,e,f2,g) in enumerate(cat3):
    cells=tbl.add_row().cells
    isSub = a.startswith("New-acq") or a.startswith("Repeat /")
    fill='1F2A44' if isSub else ('DDF0E1' if b=='HIGH' else ('FBF0D5' if b=='LOW' else ('F2F2F2' if i%2 else None)))
    col=WHITE if isSub else None
    setcell(cells[0],a,bold=True,size=9,color=col,fill=fill)
    for j,v in enumerate([b,c,e,f2,g],1): setcell(cells[j],v,size=9,al='center',color=col,fill=fill)

# ---------------- 4. CHANGE VS BASELINE ----------------
doc.add_page_break()
H("4.  Change vs baseline — June 2026 → August target", 15, NAVY)
body("June is the stated baseline month (₹9.09 cr D2C). The August plan is +₹1.41 cr (+15.5%). "
     "Almost all of the growth comes from REPEAT; new stays roughly flat in volume but far more efficient.")

eyebrow("4a · Segment change")
tbl=doc.add_table(rows=1,cols=6); tbl.style='Table Grid'
header_row(tbl,["Segment","June actual","Aug target","Δ orders","Δ %","Δ users (plan CVR)"],fill='2E5AAC')
seg=[("New orders","18,163","18,762","+599","+3.3%","−965,590"),
     ("Repeat orders","17,200","21,864","+4,664","+27.1%","+363,898"),
     ("Total","35,363","40,626","+5,263","+14.9%","−601,692")]
for i,(a,b,c,e,f2,g) in enumerate(seg):
    cells=tbl.add_row().cells; isT=a=="Total"
    fill='1F2A44' if isT else ('F2F2F2' if i%2 else None); col=WHITE if isT else None
    setcell(cells[0],a,bold=True,size=9.5,color=col,fill=fill)
    setcell(cells[1],b,size=9.5,al='center',color=col,fill=fill)
    setcell(cells[2],c,size=9.5,al='center',color=col,fill=fill)
    setcell(cells[3],e,size=9.5,al='center',color=(WHITE if isT else GREEN),fill=fill)
    setcell(cells[4],f2,size=9.5,al='center',color=(WHITE if isT else GREEN),fill=fill)
    setcell(cells[5],g,size=9.5,al='center',color=col,fill=fill)
body("")
bullet(" the plan adds +4,664 repeat orders (+27%) and holds new roughly flat (+599). ~₹1.26 cr of the +₹1.41 cr revenue is repeat.", bold_lead="Repeat is the growth:")
bullet(" total new SESSIONS fall ~0.97 M vs June even though new orders rise — because new CVR normalises from June's depressed 0.46% to July's 0.63%. You get more new orders from ~1 M fewer visits.", bold_lead="New gets more efficient, not bigger:")
bullet(" the entire shift is funded by roughly +₹19 L incremental Meta media (≈ +₹5 L new, +₹14 L repeat). The rest of the repeat volume is owned-channel (CRM, app, direct).", bold_lead="Cheap to fund:")

eyebrow("4b · Category change — where the additional orders & users come from")
body("Read: grow HIGH-LTV (Stack, Power Bank, Charging Station) on both new and repeat; hold MED; cut Watch Bands.")
tbl=doc.add_table(rows=1,cols=7); tbl.style='Table Grid'
header_row(tbl,["Category","LTV","Δ New ord","Δ New users","Δ Rep ord","Δ Rep users","Δ Spend (Meta)"])
for i,x in enumerate(rows):
    cells=tbl.add_row().cells
    fill='DDF0E1' if x['ltv']=='HIGH' else ('FBF0D5' if x['ltv']=='LOW' else ('F2F2F2' if i%2 else None))
    setcell(cells[0],x['k'],bold=True,size=8.5,fill=fill)
    setcell(cells[1],x['ltv'],size=8.5,al='center',fill=fill)
    def sgn(v,cur=False):
        s=('+' if v>=0 else '−'); v=abs(round(v))
        return (('₹' if cur else '')+s+f"{v:,}")
    setcell(cells[2],sgn(x['dN']),size=8.5,al='center',color=(GREEN if x['dN']>=0 else RED),fill=fill)
    setcell(cells[3],sgn(x['dNu']),size=8.5,al='center',color=(GREEN if x['dNu']>=0 else RED),fill=fill)
    setcell(cells[4],sgn(x['dR']),size=8.5,al='center',color=(GREEN if x['dR']>=0 else RED),fill=fill)
    setcell(cells[5],sgn(x['dRu']),size=8.5,al='center',color=(GREEN if x['dRu']>=0 else RED),fill=fill)
    setcell(cells[6],sgn(x['dNs']+x['dRs'],cur=True),size=8.5,al='center',color=(GREEN if (x['dNs']+x['dRs'])>=0 else RED),fill=fill)
cells=tbl.add_row().cells
def sgnT(v,cur=False):
    s=('+' if v>=0 else '−'); return (('₹' if cur else '')+s+f"{abs(round(v)):,}")
setcell(cells[0],"TOTAL",bold=True,size=8.5,color=WHITE,fill='1F2A44')
setcell(cells[1],"",fill='1F2A44')
setcell(cells[2],sgnT(tot['dN']),bold=True,size=8.5,al='center',color=WHITE,fill='1F2A44')
setcell(cells[3],sgnT(tot['dNu']),bold=True,size=8.5,al='center',color=WHITE,fill='1F2A44')
setcell(cells[4],sgnT(tot['dR']),bold=True,size=8.5,al='center',color=WHITE,fill='1F2A44')
setcell(cells[5],sgnT(tot['dRu']),bold=True,size=8.5,al='center',color=WHITE,fill='1F2A44')
setcell(cells[6],sgnT(tot['dNs']+tot['dRs'],cur=True),bold=True,size=8.5,al='center',color=WHITE,fill='1F2A44')
body("")
body("Δ New/Rep users = additional sessions to acquire for the incremental orders at plan CVR (new 0.63%, repeat 1.53%). "
     "Δ Spend = incremental Meta media only (new = Δord × category CAC; repeat = Δord × 35% paid × ₹865). "
     "Watch Bands is deliberately negative — lowest LTV and ROAS, so we harvest its budget for Stack / Power Bank / Charging.",
     size=9, color=GREY)

# ---------------- 5. Weekend freebie ----------------
H("5.  Weekend freebie plan", 15)
body("Gift-with-purchase above a cart threshold lifts AOV and reactivates dormant repeat buyers at near-zero media cost. ~₹0.38 cr incremental for the month.")
tbl=doc.add_table(rows=1,cols=4); tbl.style='Table Grid'
header_row(tbl,["Weekend","Status","Uplift","Mechanic"])
wk=[("Aug 1–2","Ran","+₹9.5 L","Threshold gift ₹1499+. Drove Aug 1–4 ROAS 3.28x vs Jul 3.01x."),
    ("Aug 8–9","Plan","+₹9.5 L","Free sleeve on Stack / Power Bank > ₹1999; AOV +8%."),
    ("Aug 15–16","Plan","+₹9.5 L","Independence Day combo + app-only code; biggest weekend."),
    ("Aug 22–23","Plan","+₹9.5 L","Mystery freebie > ₹1499, high-LTV skew."),
    ("Aug 29–30","Plan","+₹9.5 L","Month-end: gift + 2× loyalty points, repeat-heavy close.")]
for i,(a,b,c,e) in enumerate(wk):
    cells=tbl.add_row().cells; fill='FBF0D5' if b=='Ran' else ('F2F2F2' if i%2 else None)
    setcell(cells[0],a,bold=True,size=9,fill=fill)
    setcell(cells[1],b,size=9,al='center',fill=fill)
    setcell(cells[2],c,size=9,al='center',fill=fill)
    setcell(cells[3],e,size=9,fill=fill)

# ---------------- 6. The ask ----------------
H("6.  The ask to Performance Marketing", 15)
asks=[("Acquire 2.97 M new users → 18,762 orders. ","Concentrate prospecting on Power Bank, Stack & Node (ROAS >3.15). Cap Watch Bands."),
 ("Drive 1.43 M repeat users → 21,864 orders. ","CRM + app push + retargeting; skew re-engagement to Power Bank / Stack / Charging Station."),
 ("Shift order mix to 46% new / 54% repeat. ","+4,664 repeat vs June, new held flat — improves blend without losing topline."),
 ("Hold blended Meta ROAS ≥ 3.28x. ","Plan lands 3.39x at ₹2.36 cr spend; incremental shift costs only ~₹19 L."),
 ("Run 4 remaining freebie weekends. ","~₹0.38 cr accretive; skew gifts to high-LTV carts to protect margin.")]
for i,(lead,rest) in enumerate(asks,1):
    p=doc.add_paragraph(); r=p.add_run(f"{i}.  "); r.bold=True; r.font.color.rgb=BLUE; r.font.size=Pt(10.5)
    r=p.add_run(lead); r.bold=True; r.font.size=Pt(10.5)
    r=p.add_run(rest); r.font.size=Pt(10.5); p.paragraph_format.space_after=Pt(5)

# footnote
p=doc.add_paragraph(); r=p.add_run("Method & assumptions to validate with Finance: revenue = new×₹2,450 + repeat×₹2,700; users = orders ÷ CVR "
 "(new 0.63%, repeat 1.53%, from web+app tracker). Category economics from Meta Ads Jun/Jul 2026; retargeting used as repeat-cost proxy; "
 "Meta-attributed ≈ 76% of D2C revenue. AOV premiums, LTV tiers and weekend uplift are planning assumptions.")
r.font.size=Pt(8); r.font.color.rgb=GREY

doc.save('/home/user/claude/DailyObjects_August_D2C_Plan.docx')
print("saved docx")
