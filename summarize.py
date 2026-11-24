#!/usr/bin/env python3
"""Merge several cusp_eval.py output folders into one paper-ready summary.

  python summarize.py out_kitti out_kitti_swap out_kitti_dark out_kitti_noise out_kitti_fog > summary.md
"""
import json, math, os, sys

MAIN = ("Point-KF", "Gaussian-KF", "Split-CP", "CUSP")


def f(x, d=1):
    return "n/a" if x is None or (isinstance(x, float) and math.isnan(x)) else f"{x:.{d}f}"


def label(info, folder):
    c = info.get("corrupt", "none")
    if c != "none":
        return f"Shift: {c}"
    tag = os.path.basename(os.path.normpath(folder))
    if "nooff" in tag:
        return "Clean, no contact offset"
    if "swap" in tag:
        return "Clean, swapped split"
    return "Clean"


def main(folders):
    runs = []
    for d in folders:
        p = os.path.join(d, "results.json")
        if not os.path.exists(p):
            print(f"<!-- skipped {d}: no results.json -->"); continue
        r = json.load(open(p))
        name = label(r["info"], d)
        if any(n == name for n, _, _ in runs):
            name += f" ({os.path.basename(os.path.normpath(d))})"
        runs.append((name, r["info"], r["results"]))
    if not runs:
        sys.exit("no results found")

    print("# CUSP on KITTI Tracking: summary\n")
    print("Own lane = vehicles with true |X| < 1.8 m. Target coverage per bound: 97.5%. "
          "Unsafe = estimated safe speed above the true safe speed.\n")

    print("## Table 1. Own-lane safety per condition\n")
    print("| Condition | Method | Range cov. (%) | Rate cov. (%) | Unsafe caps (%) | Speed given up (% of true cap) | Margin (%) |")
    print("| --- | --- | --- | --- | --- | --- | --- |")
    for name, info, res in runs:
        for m in MAIN:
            c, cap = res[m]["corridor"], res[m]["cap"]
            print(f"| {name} | {m} | {f(c['cov_range'])} | {f(c['cov_rate'])} | {f(cap['unsafe_pct'], 2)} | "
                  f"{f(cap['mean_slack_rel_pct'])} | {f(c['margin_pct'])} |")

    print("\n## Table 2. Effect of online adaptation (CUSP vs static Split-CP)\n")
    print("| Condition | Mean alpha_t | Min alpha_t | Own-lane range cov. Split-CP / CUSP | Unsafe caps Split-CP / CUSP | Margin Split-CP / CUSP |")
    print("| --- | --- | --- | --- | --- | --- |")
    for name, info, res in runs:
        s, u = res["Split-CP"], res["CUSP"]
        print(f"| {name} | {f(info['alpha_mean'], 3)} | {f(info['alpha_min'], 3)} | "
              f"{f(s['corridor']['cov_range'])} / {f(u['corridor']['cov_range'])} | "
              f"{f(s['cap']['unsafe_pct'], 2)} / {f(u['cap']['unsafe_pct'], 2)} | "
              f"{f(s['corridor']['margin_pct'])} / {f(u['corridor']['margin_pct'])} |")

    print("\n## Table 3. CUSP range coverage (%) by distance (own lane) and lateral zone (all vehicles)\n")
    print("| Condition | own 1-10 m | own 10-30 m | own 30-60 m | own lane | adjacent | kerbside |")
    print("| --- | --- | --- | --- | --- | --- | --- |")
    for name, info, res in runs:
        u = res["CUSP"]
        cells = [f(u.get(f"cband_{i}", {}).get("cov_range")) for i in range(3)]
        cells += [f(u.get(f"zone_{i}", {}).get("cov_range")) for i in range(3)]
        print(f"| {name} | " + " | ".join(cells) + " |")

    print("\n## Table 4. Ablation: group-conditional calibration (lateral zone x range)\n")
    print("| Condition | Own-lane range cov. CUSP / CUSP (group) | Unsafe caps CUSP / CUSP (group) | Own-lane margin CUSP / CUSP (group) |")
    print("| --- | --- | --- | --- |")
    for name, info, res in runs:
        u, g = res["CUSP"], res.get("CUSP (group)")
        if g is None:
            continue
        print(f"| {name} | {f(u['corridor']['cov_range'])} / {f(g['corridor']['cov_range'])} | "
              f"{f(u['cap']['unsafe_pct'], 2)} / {f(g['cap']['unsafe_pct'], 2)} | "
              f"{f(u['corridor']['margin_pct'])} / {f(g['corridor']['margin_pct'])} |")

    print("\n## Table 5. Latency per frame (ms) and mounting calibration\n")
    print("| Condition | CUSP mean / p99 | Detector + tracker mean / p99 | End to end mean | Contact offset (m) | Horizon row (px) |")
    print("| --- | --- | --- | --- | --- | --- |")
    for name, info, res in runs:
        L = info["latency"]; c = L.get("CUSP module", {}); d = L.get("Detector + tracker", {}); e = L.get("End to end", {})
        m = info.get("mount_test", {})
        print(f"| {name} | {f(c.get('mean'), 2)} / {f(c.get('p99'), 2)} | {f(d.get('mean'), 1)} / {f(d.get('p99'), 1)} | "
              f"{f(e.get('mean'), 1)} | {f(m.get('delta'), 2)} | {f(m.get('yh'), 1)} |")


if __name__ == "__main__":
    main(sys.argv[1:])
