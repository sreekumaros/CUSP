#!/usr/bin/env python3
"""Paper figures from cusp_eval.py outputs.

  python make_figures.py out_kitti out_kitti_dark

Writes fig_coverage_by_distance.png/.pdf and fig_alpha_trace.png/.pdf
(PDF for the Springer template, PNG for previews).
"""
import csv, json, os, sys
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

INK, INK2, GRID, SURF = "#0b0b0b", "#52514e", "#e4e3df", "#ffffff"
COLORS = {"Point-KF": "#2a78d6", "Gaussian-KF": "#eb6834", "CUSP": "#1baf7a"}
BANDS = ["1–10 m", "10–30 m", "30–60 m"]

plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 9, "axes.edgecolor": INK2,
                     "axes.labelcolor": INK, "xtick.color": INK2, "ytick.color": INK2,
                     "axes.spines.top": False, "axes.spines.right": False})


def save(fig, name):
    for ext in ("png", "pdf"):
        fig.savefig(f"{name}.{ext}", dpi=300, bbox_inches="tight", facecolor=SURF)
    print("wrote", name + ".png/.pdf")


def fig_coverage(folder):
    res = json.load(open(os.path.join(folder, "results.json")))["results"]
    fig, ax = plt.subplots(figsize=(6.0, 3.0))
    w, gap = 0.26, 0.02
    for i, m in enumerate(COLORS):
        vals = [res[m].get(f"cband_{b}", {}).get("cov_range", float("nan")) for b in range(3)]
        ns = [res[m].get(f"cband_{b}", {}).get("n", 0) for b in range(3)]
        xs = [b + (i - 1) * (w + gap) for b in range(3)]
        ax.bar(xs, vals, w, color=COLORS[m], label=m, zorder=2)
        for x, v in zip(xs, vals):
            ax.text(x, v + 1.2, f"{v:.1f}", ha="center", va="bottom", fontsize=7.5, color=INK, zorder=4,
                    bbox=dict(boxstyle="square,pad=0.1", fc=SURF, ec="none"))
    ax.axhline(97.5, color=INK2, lw=1, ls=(0, (4, 3)), zorder=3)
    ax.text(2.62, 97.5, "target 97.5%", va="center", ha="left", fontsize=7.5, color=INK2)
    ax.set_xticks(range(3))
    ax.set_xticklabels([f"{b}\n(n = {n})" for b, n in zip(BANDS, ns)])
    ax.set_ylim(0, 108); ax.set_yticks(range(0, 101, 20))
    ax.set_ylabel("Own-lane range coverage (%)")
    ax.yaxis.grid(True, color=GRID, lw=0.8, zorder=0); ax.set_axisbelow(True)
    ax.legend(frameon=False, ncol=3, loc="lower center", bbox_to_anchor=(0.5, 1.0), fontsize=8)
    save(fig, "fig_coverage_by_distance")


def read_alpha(folder):
    with open(os.path.join(folder, "alpha_trace.csv")) as fh:
        return [float(r["alpha_t"]) for r in csv.DictReader(fh)]


def fig_alpha(clean, shifted):
    a0, a1 = read_alpha(clean), read_alpha(shifted)
    info = json.load(open(os.path.join(shifted, "results.json")))["info"]
    fig, ax = plt.subplots(figsize=(6.0, 2.4))
    ax.plot(range(len(a0)), a0, color="#9a9890", lw=1.2, label="Clean images")
    ax.plot(range(len(a1)), a1, color=COLORS["Point-KF"], lw=1.4, label=f"Degraded: {info.get('corrupt', 'shift')}")
    ax.axhline(0.05, color=INK2, lw=0.8, ls=(0, (4, 3)))
    ax.text(0, 0.0515, "nominal α = 0.05 (upper limit)", va="bottom", fontsize=7.5, color=INK2)
    ax.set_xlabel("Test frame (KITTI sequences 0011–0020, concatenated)")
    ax.set_ylabel("Working level α$_t$")
    ax.set_ylim(0, 0.058)
    ax.yaxis.grid(True, color=GRID, lw=0.8); ax.set_axisbelow(True)
    ax.legend(frameon=False, ncol=2, loc="lower center", bbox_to_anchor=(0.5, 1.0), fontsize=8)
    save(fig, "fig_alpha_trace")


if __name__ == "__main__":
    clean = sys.argv[1] if len(sys.argv) > 1 else "out_kitti"
    shifted = sys.argv[2] if len(sys.argv) > 2 else "out_kitti_dark"
    fig_coverage(clean)
    if os.path.exists(os.path.join(shifted, "alpha_trace.csv")):
        fig_alpha(clean, shifted)
    else:
        print(f"{shifted}/alpha_trace.csv not found; skipped the alpha figure")
