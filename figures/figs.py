import os, pandas as pd, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
MM=1/25.4
INK, INK2, GRID = "#0b0b0b", "#52514e", "#e4e3df"
plt.rcParams.update({"font.family":"Liberation Sans","font.size":8,"axes.edgecolor":INK2,
 "axes.labelcolor":INK,"xtick.color":INK2,"ytick.color":INK2,"axes.spines.top":False,
 "axes.spines.right":False,"pdf.fonttype":42,"mathtext.fontset":"custom","mathtext.rm":"Liberation Sans","mathtext.it":"Liberation Sans:italic","mathtext.bf":"Liberation Sans:bold"})
COL={"Point-KF":"#2a78d6","Gaussian-KF":"#eb6834","CUSP":"#1baf7a"}
# Fig 2
d=pd.read_csv(os.path.join(os.path.dirname(os.path.abspath(__file__)),"..","results","kitti","out_kitti","coverage_by_band.csv"))
fig,ax=plt.subplots(figsize=(84*MM,52*MM))
w,g=0.26,0.03; bands=["1–10 m","10–30 m","30–60 m"]
for i,m in enumerate(COL):
    r=[d[(d.method==m)&(d.group==f"cband_{b}")].iloc[0] for b in range(3)]
    xs=[b+(i-1)*(w+g) for b in range(3)]
    ax.bar(xs,[x.cov_range for x in r],w,color=COL[m],label=m,zorder=2)
    for x,v in zip(xs,r): ax.text(x,v.cov_range+1.5,f"{v.cov_range:.1f}",ha="center",va="bottom",fontsize=6.5,color=INK)
    ns=[int(x.n) for x in r]
ax.axhline(97.5,color=INK2,lw=0.8,ls=(0,(4,3)),zorder=3,label="Target 97.5%")
ax.set_xticks(range(3)); ax.set_xticklabels([f"{b}\n(n = {n})" for b,n in zip(bands,ns)])
ax.set_ylim(0,112); ax.set_yticks(range(0,101,20)); ax.set_ylabel("Own-lane range coverage (%)")
ax.yaxis.grid(True,color=GRID,lw=0.6,zorder=0); ax.set_axisbelow(True)
ax.legend(frameon=False,ncol=4,loc="lower center",bbox_to_anchor=(0.5,1.0),fontsize=6.5,handlelength=1.2,columnspacing=0.8)
fig.savefig("fig2.pdf",bbox_inches="tight"); fig.savefig("fig2.png",dpi=200,bbox_inches="tight")
# Fig 1 architecture
fig,ax=plt.subplots(figsize=(174*MM,56*MM)); ax.set_xlim(0,174); ax.set_ylim(0,64); ax.axis("off")
def box(x,y,w,h,t,fc="#ffffff",ec=INK2,b=False):
    ax.add_patch(FancyBboxPatch((x,y),w,h,boxstyle="round,pad=0,rounding_size=1.5",fc=fc,ec=ec,lw=0.8))
    ax.text(x+w/2,y+h/2,t,ha="center",va="center",fontsize=7,weight="bold" if b else "normal",linespacing=1.25)
def arr(x0,y0,x1,y1,t=None,dy=1.6):
    ax.annotate("",(x1,y1),(x0,y0),arrowprops=dict(arrowstyle="-|>",lw=0.7,color=INK2,mutation_scale=7,shrinkA=0,shrinkB=0))
    if t: ax.text((x0+x1)/2,(y0+y1)/2+dy,t,ha="center",va="bottom",fontsize=6,color=INK2)
G="#eaf6f0"
ax.text(83,53.5,r"ego odometry $v_e,\ a_e$",ha="center",fontsize=6,color=INK2)
ax.annotate("",(83,48),(83,53),arrowprops=dict(arrowstyle="-|>",lw=0.7,color=INK2,mutation_scale=7))
box(1,30,22,18,"Monocular\ncamera\n(20–47 fps)")
box(28,30,24,18,"Detector and\ntracker\n(YOLO26s,\nByteTrack)")
ax.add_patch(FancyBboxPatch((61,2),88,60,boxstyle="round,pad=0,rounding_size=2",fc="none",ec="#1baf7a",lw=1.0,ls=(0,(4,2))))
ax.text(105,58.6,"CUSP module  (O(N) per frame, 0.12 ms on KITTI)",ha="center",fontsize=7,color="#127a55",weight="bold")
box(65,30,36,18,"1  Log-range $\\tau$-filter\n$x=[\\ln Z,\\ \\dot Z/Z,\\ \\ln fW]$\ncontact offset $\\delta$",fc=G)
box(65,6,36,18,"3  Lateral filter\n$[X,\\dot X]$ → corridor-entry\nprobability $p_i$",fc=G)
box(109,30,36,18,"2  Conformal bounds\n$Z^-,\\ \\dot s^-$ at level $\\alpha_t$\none-sided label-free ACI",fc=G)
box(109,6,36,18,"4  Safe speed\nclosed-form $v_i^\\star$, risk-\nweighted cap, governor",fc=G)
box(153,15,20,18,"Longitudinal\nactuator\n$a_k$")
arr(23,39,28,39); arr(52,39,65,39,r"$y_b,\ w$"); 
ax.annotate("",(65,15),(56,39),arrowprops=dict(arrowstyle="-|>",lw=0.7,color=INK2,mutation_scale=7,connectionstyle="angle,angleA=-90,angleB=180"))
ax.text(54.2,22,r"$u$",fontsize=6,color=INK2)
arr(101,42,109,42,r"$\hat s,\ \sigma_s$"); arr(101,35,109,35,r"$|\nu|$",dy=-4.2)
arr(127,30,127,24,None); ax.text(128,26.3,r"$Z^-,\ \dot s^-$",fontsize=6,color=INK2)
arr(101,15,109,15,r"$p_i$"); arr(145,24,153,24,r"$v_{\rm cap}$",dy=-4.5)
fig.savefig("fig1.pdf",bbox_inches="tight"); fig.savefig("fig1.png",dpi=200,bbox_inches="tight")
