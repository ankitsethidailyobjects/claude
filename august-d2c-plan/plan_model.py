from meta_2026 import JUN, JUL, categorize
from collections import defaultdict

def agg(data):
    c=defaultdict(lambda:[0,0,0.0])
    for name,sp,od,rev in data:
        k=categorize(name); c[k][0]+=sp; c[k][1]+=od; c[k][2]+=rev
    return c

jul=agg(JUL)
web_jul=dict(newU=3645614, repU=1046558, newT=18997, repT=12901)
app_jul=dict(newU=22158,   repU=260981,  newT=3730,  repT=6510)
newU=web_jul['newU']+app_jul['newU']; repU=web_jul['repU']+app_jul['repU']
newT=web_jul['newT']+app_jul['newT']; repT=web_jul['repT']+app_jul['repT']
totT=newT+repT
newCVR=newT/newU; repCVR=repT/repU
print("=== JULY D2C ACTUALS (web+app) ===")
print(f"New users {newU:,} -> orders {newT:,} | New CVR {newCVR:.3%}")
print(f"Rep users {repU:,} -> orders {repT:,} | Rep CVR {repCVR:.3%}")
print(f"Total orders {totT:,} | Repeat share of orders {repT/totT:.1%}")

AOV_new=2450; AOV_rep=2700
d2c_jul_rev=newT*AOV_new+repT*AOV_rep
print(f"Implied July D2C revenue @AOV(new {AOV_new}/rep {AOV_rep}) = Rs {d2c_jul_rev/1e7:.2f} cr")

TARGET=10.5e7; holdROAS=3.28
print("\n=== AUGUST TARGET BUILD ===  Target Rs %.2f cr | Hold Meta ROAS >= %.2f"%(TARGET/1e7,holdROAS))
rep_growth=1.08; freebie_rep_lift=900
rep_orders=round(repT*rep_growth+freebie_rep_lift)
new_orders=round((TARGET-rep_orders*AOV_rep)/AOV_new)
tot_orders=new_orders+rep_orders
rev=new_orders*AOV_new+rep_orders*AOV_rep
print(f"Repeat orders (target): {rep_orders:,}  ({rep_orders/tot_orders:.0%} of orders)")
print(f"New   orders (target): {new_orders:,}  ({new_orders/tot_orders:.0%} of orders)")
print(f"Total orders: {tot_orders:,} | Revenue Rs {rev/1e7:.2f} cr")

newCVR_aug=newCVR*1.02; repCVR_aug=repCVR*1.03
new_users=round(new_orders/newCVR_aug); rep_users=round(rep_orders/repCVR_aug)
print(f"\nNEW users required : {new_users:,}  (@CVR {newCVR_aug:.3%})")
print(f"REPEAT users required: {rep_users:,}  (@CVR {repCVR_aug:.3%})")
print(f"Total users/sessions: {new_users+rep_users:,} | avg/day {(new_users+rep_users)/31:,.0f}")

CAC_new=903; cost_rep_order=865; paid_rep_share=0.35
new_spend=new_orders*CAC_new
rep_spend=rep_orders*paid_rep_share*cost_rep_order
tot_spend=new_spend+rep_spend
meta_rev=rev*0.76
print(f"\n=== SPEND & EFFICIENCY ===")
print(f"New acq spend  : Rs {new_spend/1e7:.2f} cr")
print(f"Repeat nudge spend (35% paid): Rs {rep_spend/1e7:.2f} cr")
print(f"Total Meta spend: Rs {tot_spend/1e7:.2f} cr")
print(f"Blended ROAS (D2C rev/spend): {rev/tot_spend:.2f}")
print(f"Blended ROAS (Meta-attr rev/spend): {meta_rev/tot_spend:.2f}  (hold>= {holdROAS})")

print("\n=== CATEGORY-LEVEL AUGUST TARGETS (July mix, tilted to ROAS+LTV) ===")
LTV_TIER={'Power Bank':'HIGH','Stack':'HIGH','Charging Station (Loft)':'HIGH',
          'Node':'MED','Tech Kit (Park)':'MED','Bags / DG':'MED',
          'Desk Organiser (Bar)':'MED','Watch Bands':'LOW'}
newcats={k:v for k,v in jul.items() if k in LTV_TIER}
jsum=sum(v[2] for v in newcats.values())
tilt={'HIGH':1.15,'MED':1.0,'LOW':0.85}
weights={k:newcats[k][2]/jsum*tilt[LTV_TIER[k]] for k in newcats}
wsum=sum(weights.values())
new_rev_pool=new_orders*AOV_new
print(f"New-acquisition revenue pool: Rs {new_rev_pool/1e7:.2f} cr")
for k in sorted(newcats,key=lambda x:-weights[x]):
    share=weights[k]/wsum; catrev=new_rev_pool*share
    julrev=newcats[k][2]/0.76
    roas=jul[k][2]/jul[k][0]; cac=jul[k][0]/jul[k][1]; aov=jul[k][2]/jul[k][1]
    cat_orders=catrev/aov
    print(f"{k:24s} LTV={LTV_TIER[k]:4s} JulD2C~Rs{julrev/1e7:4.2f}cr -> AugTgt Rs{catrev/1e7:4.2f}cr ({share:4.1%}) ROAS{roas:4.2f} CAC~Rs{cac:.0f} newOrders~{cat_orders:,.0f}")
rep_rev=rep_orders*AOV_rep
print(f"\nRepeat/CRM/app revenue pool: Rs {rep_rev/1e7:.2f} cr")
print(f"GRAND TOTAL: Rs {(new_rev_pool+rep_rev)/1e7:.2f} cr")

print("\n=== FREEBIE WEEKEND MODEL ===")
weekends=[('Aug 1-2','DONE (Aug1-4 ROAS 3.28 vs Jul 3.01)'),('Aug 8-9',''),('Aug 15-16 I-Day',''),('Aug 22-23',''),('Aug 29-30','')]
daily=rev/31
for w,note in weekends:
    base=daily*2; lift=base*0.14
    print(f"{w:18s} base Rs{base/1e5:5.1f}L +freebie Rs{lift/1e5:4.1f}L -> Rs{(base+lift)/1e5:5.1f}L  {note}")
