#!/usr/bin/env python3
"""Fase 5: sincroniza el visor web con el nucleo afinado y corrige el etiquetado.
Uso: python scripts/patch_viewer.py   (idempotente; informa cada cambio)"""
import os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PATH = os.path.join(ROOT, "web", "index.html")
src = open(PATH, encoding="utf-8").read()
orig = src
changes = []

old = "L0:9500,L1:3500,omL:800"
new = "L0:8000,L1:6000,omL:4000"
if old in src:
    src = src.replace(old, new); changes.append("preset Pb-Sn -> L0=8000,L1=6000,omL=4000")
elif new in src:
    changes.append("preset Pb-Sn ya sincronizado")
else:
    print("AVISO: no se encontro el preset Pb-Sn original"); sys.exit(1)

old_bcat = "const BCAT={'α|α+L':'solidus','α+L|α':'solidus','α+L|L':'liquidus','L|α+L':'liquidus','L|L+β':'liquidus','L+β|β':'solidus','α|α+β':'solvus','α+β|β':'solvus'};"
new_bcat = "const BCAT={'α|α+L':'solidus','α+L|α':'solidus','L+β|β':'solidus','β|β+L':'solidus','L+α|α':'solidus','α+L|L':'liquidus','L|α+L':'liquidus','L|L+β':'liquidus','L|L+α':'liquidus','β+L|L':'liquidus','α|α+β':'solvus','α+β|β':'solvus'};"
if old_bcat in src:
    src = src.replace(old_bcat, new_bcat); changes.append("BCAT + claves espejo (Cu-Ni liquidus/solidus)")
elif new_bcat in src:
    changes.append("BCAT ya corregido")
else:
    print("AVISO: no se encontro BCAT original"); sys.exit(1)

NEW_FN = r"""function computeBinary(){
  const p=state.params,m=makeModel(p);
  const Tmin=Math.min(p.TmA,p.TmB)*0.55,Tmax=Math.max(p.TmA,p.TmB)*1.15;
  const rows=300,N=320,dx=1/N,dT=(Tmax-Tmin)/(rows-1);
  const dual=p.L0>2*R*Tmin;
  const B={solidus:[],liquidus:[],solvus:[]},spots={},spinL=[],spinR=[],rowsOut=[];
  let eut=null,prevL=null;
  for(let r=0;r<rows;r++){
    const T=Tmax-r*dT;
    const pts=[];
    for(let i=0;i<=N;i++){
      const x=i/N,gS=m.G(0,x,T),gL=m.G(1,x,T);
      pts.push(gS<=gL?{x,g:gS,p:0}:{x,g:gL,p:1});
    }
    const hull=[];
    for(const q of pts){
      while(hull.length>=2){
        const o=hull[hull.length-2],a=hull[hull.length-1];
        if((a.x-o.x)*(q.g-o.g)-(a.g-o.g)*(q.x-o.x)<=0)hull.pop();else break;
      }
      hull.push(q);
    }
    const raw=[];
    for(let i=0;i<hull.length-1;i++){
      const a=hull[i],b=hull[i+1];
      if(b.x-a.x<1e-12)continue;
      raw.push({x0:a.x,x1:b.x,p0:a.p,p1:b.p,tie:(b.x-a.x>2.5*dx)||(a.p!==b.p)});
    }
    const segs=[];
    for(const s of raw){
      const last=segs[segs.length-1];
      if(!s.tie&&last&&!last.tie&&last.p0===s.p0)last.x1=s.x1;
      else segs.push(s);
    }
    for(const s of segs){
      if(s.tie)continue;
      if(s.p0===1)s.key='L';
      else if(!dual)s.key='α';
      else s.key=(s.x0<=1e-9)?'α':(s.x1>=1-1e-9?'β':'α');
    }
    for(let i=0;i<segs.length;i++){
      const s=segs[i];if(!s.tie)continue;
      if(s.p0===0&&s.p1===0)s.key='α+β';
      else{
        let lab=null;const pv=segs[i-1],nx=segs[i+1];
        if(pv&&!pv.tie&&pv.p0===0)lab=pv.key;
        else if(nx&&!nx.tie&&nx.p0===0)lab=nx.key;
        if(!lab)lab=(s.x0+s.x1)/2<0.5?'α':'β';
        s.key=s.p0===0?lab+'+L':'L+'+lab;
      }
      refineTie(m,s,T);
    }
    for(let i=0;i<segs.length;i++){
      const s=segs[i];if(s.tie)continue;
      if(i>0&&segs[i-1].tie&&segs[i-1].x1<=s.x1)s.x0=segs[i-1].x1;
      if(i+1<segs.length&&segs[i+1].tie&&segs[i+1].x0>=s.x0)s.x1=segs[i+1].x0;
    }
    for(const s of segs){s.g0=m.G(s.p0,s.x0,T);s.g1=m.G(s.p1,s.x1,T);}
    for(let i=0;i<segs.length-1;i++){
      const cat=BCAT[segs[i].key+'|'+segs[i+1].key];
      if(cat)B[cat].push([segs[i].x1,T]);
    }
    for(const s of segs){
      const w=s.x1-s.x0,sp=spots[s.key];
      if(!sp||w>sp.w)spots[s.key]={x:(s.x0+s.x1)/2,T,w};
    }
    const Lseg=segs.find(s=>!s.tie&&s.key==='L');
    if(prevL&&!Lseg&&dual){
      const ab=segs.find(s=>s.tie&&s.key==='α+β');
      eut={T:T+dT/2,xE:(prevL.x0+prevL.x1)/2,xa:ab?ab.x0:0,xb:ab?ab.x1:1};
    }
    prevL=Lseg||null;
    let pl=null,pr=null,pg=m.G2(0,dx/2,T);
    for(let i=1;i<200;i++){
      const x=i/200,g2=m.G2(0,x,T);
      if(pg>0&&g2<=0)pl=x;else if(pg<=0&&g2>0)pr=x;
      pg=g2;
    }
    if(pl!=null)spinL.push([pl,T]);
    if(pr!=null)spinR.push([pr,T]);
    rowsOut.push({T,segs});
  }
  return {model:m,Tmin,Tmax,dT,rows:rowsOut,B,spots,eut,spinL,spinR,dual};
}
"""
i = src.find("function computeBinary(){")
j = src.find("function binaryState(){")
if i != -1 and j != -1 and j > i:
    src = src[:i] + NEW_FN.rstrip() + "\n" + src[j:]
    changes.append("computeBinary: dedupe + fusion de regiones + etiquetas alpha/beta correctas")
else:
    print("AVISO: no se encontraron las anclas computeBinary/binaryState"); sys.exit(1)

if src != orig:
    open(PATH, "w", encoding="utf-8").write(src)
for c in changes:
    print("OK:", c)
print("Visor actualizado:", PATH)
