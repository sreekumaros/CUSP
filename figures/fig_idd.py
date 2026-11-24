import json, csv, os, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
exec(open(os.path.join(os.path.dirname(__file__),"figs.py")).read().split("# Fig 2")[0])   # shared style
U=os.path.join(os.path.dirname(__file__),"..","results","idd3d")+"/"
rows=list(csv.DictReader(open(U+"out_idd_test_clean/coverage_by_band.csv")))
get=lambda m,g: next(r for r in rows if r["method"]==m and r["group"]==g)
dv=json.load(open(U+"out_idd_test_dav2_clean/results.json"))["results"]["DAv2 + Split-CP"]
M=[("Gaussian-KF","#eb6834"),("DAv2 + Split-CP","#7a5cc7"),("CUSP","#1baf7a")]
fig,ax=plt.subplots(figsize=(84*MM,52*MM))
w,g=0.26,0.03; bands=["1–10 m","10–30 m","30–60 m"]
for i,(m,col) in enumerate(M):
    vals=[(dv[f"band_{b}"]["cov_range"],dv[f"band_{b}"]["n"]) if m.startswith("DAv2") else (float(get(m,f"band_{b}")["cov_range"]),int(get(m,f"band_{b}")["n"])) for b in range(3)]
    xs=[b+(i-1)*(w+g) for b in range(3)]
    ax.bar(xs,[v for v,_ in vals],w,color=col,label=m.replace("-KF",""),zorder=2)
    for x,(v,_) in zip(xs,vals): ax.text(x,v+1.5,f"{v:.1f}",ha="center",va="bottom",fontsize=6,color=INK)
ns=[int(get("CUSP",f"band_{b}")["n"]) for b in range(3)]
ax.axhline(97.5,color=INK2,lw=0.8,ls=(0,(4,3)),zorder=3,label="Target 97.5%")
ax.set_xticks(range(3)); ax.set_xticklabels([f"{b}\n(n = {n})" for b,n in zip(bands,ns)])
ax.set_ylim(0,112); ax.set_yticks(range(0,101,20)); ax.set_ylabel("Range coverage (%)")
ax.yaxis.grid(True,color=GRID,lw=0.6,zorder=0); ax.set_axisbelow(True)
ax.legend(frameon=False,ncol=4,loc="lower center",bbox_to_anchor=(0.5,1.0),fontsize=6.2,handlelength=1.2,columnspacing=0.7)
fig.savefig("fig_idd_band.pdf",bbox_inches="tight"); fig.savefig("fig_idd_band.png",dpi=200,bbox_inches="tight")
