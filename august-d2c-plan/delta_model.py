from meta_2026 import JUN, JUL, categorize
from collections import defaultdict

def agg(data):
    c=defaultdict(lambda:[0,0,0.0])
    for n,sp,od,rev in data:
        k=categorize(n); c[k][0]+=sp; c[k][1]+=od; c[k][2]+=rev
    return c
jun=agg(JUN)

LTV={'Power Bank':'HIGH','Stack':'HIGH','Charging Station (Loft)':'HIGH','Node':'MED',
     'Tech Kit (Park)':'MED','Bags / DG':'MED','Desk Organiser (Bar)':'MED','Watch Bands':'LOW'}
cats=list(LTV.keys())

# --- topline baseline (June) vs August target (D2C, web+app) ---
J=dict(newU=3934105,repU=1065980,newO=18163,repO=17200)
A=dict(newU=2968515,repU=1429878,newO=18762,repO=21864)
AOV_new,AOV_rep=2450,2700
Jrev=J['newO']*AOV_new+J['repO']*AOV_rep
Arev=A['newO']*AOV_new+A['repO']*AOV_rep
print(f"June D2C rev Rs {Jrev/1e7:.2f}cr | Aug target Rs {Arev/1e7:.2f}cr | delta Rs {(Arev-Jrev)/1e7:+.2f}cr ({(Arev/Jrev-1):+.1%})")
print(f"NEW  orders {J['newO']:,} -> {A['newO']:,} ({A['newO']-J['newO']:+,})  users {J['newU']:,} -> {A['newU']:,} ({A['newU']-J['newU']:+,})")
print(f"REP  orders {J['repO']:,} -> {A['repO']:,} ({A['repO']-J['repO']:+,})  users {J['repU']:,} -> {A['repU']:,} ({A['repU']-J['repU']:+,})")

# --- allocate topline new & repeat orders to categories ---
# June category order weights from Meta prospecting orders
jw={k:jun[k][1] for k in cats}; jws=sum(jw.values())
# August tilt for NEW: high +15% share weight, low -15%
tiltN={'HIGH':1.15,'MED':1.0,'LOW':0.85}
awN={k:jun[k][1]/jws*tiltN[LTV[k]] for k in cats}; awNs=sum(awN.values())
# August tilt for REPEAT: repeat over-indexes high-LTV consumables
tiltR={'HIGH':1.35,'MED':1.0,'LOW':0.65}
awR={k:jun[k][1]/jws*tiltR[LTV[k]] for k in cats}; awRs=sum(awR.values())

cac={k:(jun[k][0]/jun[k][1] if jun[k][1] else 0) for k in cats}
roas={k:(jun[k][2]/jun[k][0] if jun[k][0] else 0) for k in cats}
rep_cost=865; paid_rep=0.35; new_cvr=0.00632; rep_cvr=0.01529

print("\n=== CATEGORY DELTA: June baseline -> August target (orders, users, incremental cost) ===")
print(f"{'Category':24s}{'LTV':5s}| NEW: Jun Aug  d | REP: Jun Aug  d | +NewUsr +RepUsr | +Spend(New) +Spend(Rep)")
tot=defaultdict(float)
rows=[]
for k in sorted(cats,key=lambda x:-awN[x]):
    jN=J['newO']*jw[k]/jws; aN=A['newO']*awN[k]/awNs; dN=aN-jN
    jR=J['repO']*jw[k]/jws; aR=A['repO']*awR[k]/awRs; dR=aR-jR
    dNu=dN/new_cvr; dRu=dR/rep_cvr
    dNspend=dN*cac[k]; dRspend=dR*paid_rep*rep_cost
    rows.append(dict(k=k,ltv=LTV[k],jN=jN,aN=aN,dN=dN,jR=jR,aR=aR,dR=dR,dNu=dNu,dRu=dRu,
                     dNs=dNspend,dRs=dRspend,cac=cac[k],roas=roas[k]))
    tot['dN']+=dN; tot['dR']+=dR; tot['dNu']+=dNu; tot['dRu']+=dRu; tot['dNs']+=dNspend; tot['dRs']+=dRspend
    tot['jN']+=jN; tot['aN']+=aN; tot['jR']+=jR; tot['aR']+=aR
    print(f"{k:24s}{LTV[k]:5s}| {jN:5.0f} {aN:5.0f} {dN:+5.0f} | {jR:5.0f} {aR:5.0f} {dR:+5.0f} | {dNu:+8.0f} {dRu:+8.0f} | Rs{dNspend:+9.0f} Rs{dRspend:+9.0f}")
print(f"{'TOTAL':24s}{'':5s}| {tot['jN']:5.0f} {tot['aN']:5.0f} {tot['dN']:+5.0f} | {tot['jR']:5.0f} {tot['aR']:5.0f} {tot['dR']:+5.0f} | {tot['dNu']:+8.0f} {tot['dRu']:+8.0f} | Rs{tot['dNs']:+9.0f} Rs{tot['dRs']:+9.0f}")
print(f"\nIncremental Meta spend to fund the shift: New Rs {tot['dNs']/1e5:+.1f}L + Repeat Rs {tot['dRs']/1e5:+.1f}L = Rs {(tot['dNs']+tot['dRs'])/1e5:+.1f}L")
print("Note: NEW users fall overall because new CVR normalises to July's 0.63% (June was a depressed 0.46%).")
print("      Same/again more new ORDERS from ~1M fewer sessions. Repeat is the real volume add: +4,664 orders.")

# save rows for doc/xlsx builders
import json
json.dump({'rows':rows,'tot':dict(tot),'J':J,'A':A,'Jrev':Jrev,'Arev':Arev,
           'cac':cac,'roas':roas},open('/home/user/claude/delta.json','w'),default=float)
print("\nsaved delta.json")
