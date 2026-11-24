"""Inventory a downloaded driving dataset (IDD Multimodal / IDD-3D / anything) so the
evaluator can be written against its real layout.

Usage:
  python inspect_dataset.py data/idd_multimodal > idd_inventory.txt
Then upload idd_inventory.txt.  The script only reads; it never modifies the dataset.
It also looks inside .zip / .tar archives (listing only, no extraction).
"""
import os, sys, json, struct, zipfile, tarfile, collections

TEXT_HINTS = ("calib", "label", "annot", "meta", "intrinsic", "extrinsic", "pose", "gps", "obd",
              "lidar", "camera", "sensor", "timestamp", "readme", "info", "split", "train", "val", "test")
TEXT_EXT = {".txt", ".json", ".yaml", ".yml", ".csv", ".xml", ".cfg", ".ini", ".md", ".log"}
PC_EXT = {".bin", ".pcd", ".npy", ".npz", ".ply", ".las"}
IMG_EXT = {".png", ".jpg", ".jpeg", ".bmp", ".tif", ".tiff"}


def human(n):
    for u in ("B", "KB", "MB", "GB", "TB"):
        if n < 1024: return f"{n:.1f}{u}"
        n /= 1024
    return f"{n:.1f}PB"


def show_text(path, max_lines=25, max_chars=3000):
    try:
        with open(path, "r", errors="replace") as f:
            s = f.read(max_chars)
        if path.endswith(".json"):
            try:
                obj = json.load(open(path))
                def shape(o, d=0):
                    if d > 3: return "..."
                    if isinstance(o, dict): return {k: shape(v, d + 1) for k, v in list(o.items())[:15]}
                    if isinstance(o, list): return [shape(o[0], d + 1), f"... len={len(o)}"] if o else []
                    return type(o).__name__ + (f"={o!r}"[:60] if not isinstance(o, (dict, list)) else "")
                s = json.dumps(shape(obj), indent=1)[:max_chars]
            except Exception:
                pass
        print("      | " + "\n      | ".join(s.splitlines()[:max_lines]))
    except Exception as e:
        print("      (unreadable:", e, ")")


def show_pointcloud(path):
    ext = os.path.splitext(path)[1].lower(); size = os.path.getsize(path)
    try:
        if ext == ".pcd":
            with open(path, "rb") as f:
                hdr = [f.readline().decode(errors="replace").strip() for _ in range(11)]
            print("      | " + "\n      | ".join(hdr))
        elif ext == ".bin":
            print(f"      size {size} B; /16 = {size / 16:.1f} (float32 x4?), /20 = {size / 20:.1f} (x5?), "
                  f"/24 = {size / 24:.1f} (x6?)")
            with open(path, "rb") as f:
                vals = struct.unpack("<12f", f.read(48))
            print("      first 12 float32:", [round(v, 3) for v in vals])
        elif ext in (".npy", ".npz"):
            import numpy as np
            a = np.load(path, allow_pickle=False)
            if hasattr(a, "files"):
                for k in a.files[:10]: print(f"      {k}: {a[k].shape} {a[k].dtype}")
            else:
                print(f"      shape {a.shape} dtype {a.dtype}; first rows {a[:2].tolist()}")
    except Exception as e:
        print("      (could not parse:", e, ")")


def show_image(path):
    try:
        from PIL import Image
        im = Image.open(path); print(f"      image {im.size[0]}x{im.size[1]} mode {im.mode}")
    except Exception as e:
        print("      (image not read:", e, ")")


def list_archive(path, limit=60):
    try:
        if zipfile.is_zipfile(path):
            names = zipfile.ZipFile(path).namelist()
        elif tarfile.is_tarfile(path):
            names = tarfile.open(path).getnames()
        else:
            return
        print(f"   ARCHIVE {path}: {len(names)} entries")
        dirs = collections.Counter(os.path.dirname(n) for n in names)
        for d, c in list(dirs.most_common())[:limit]:
            print(f"      {d or '.'}/  ({c} entries)")
    except Exception as e:
        print("   archive not listed:", e)


def main(root, max_depth=5, samples_per_dir=2):
    print("ROOT", os.path.abspath(root))
    total, ext_count = 0, collections.Counter()
    shown_text = shown_pc = shown_img = 0
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames.sort(); filenames.sort()
        depth = os.path.relpath(dirpath, root).count(os.sep)
        sizes = [os.path.getsize(os.path.join(dirpath, f)) for f in filenames]
        total += sum(sizes)
        exts = collections.Counter(os.path.splitext(f)[1].lower() or "<none>" for f in filenames)
        ext_count.update(exts)
        if depth <= max_depth:
            rel = os.path.relpath(dirpath, root)
            ex = ", ".join(f"{e}:{c}" for e, c in exts.most_common(6))
            print(f"{'  ' * depth}{rel}/  [{len(filenames)} files, {human(sum(sizes))}] {ex}")
            if filenames:
                print(f"{'  ' * depth}   e.g. {filenames[0]} ... {filenames[-1]}")
        # samples
        n_txt = 0
        for f in filenames:
            p = os.path.join(dirpath, f); e = os.path.splitext(f)[1].lower()
            if e in TEXT_EXT and n_txt < samples_per_dir and shown_text < 40 and \
                    (any(h in p.lower() for h in TEXT_HINTS) or len(filenames) < 5):
                print(f"   TEXT {os.path.relpath(p, root)}"); show_text(p); n_txt += 1; shown_text += 1
        pcs = [f for f in filenames if os.path.splitext(f)[1].lower() in PC_EXT]
        if pcs and shown_pc < 4:
            p = os.path.join(dirpath, pcs[0]); print(f"   POINTCLOUD {os.path.relpath(p, root)}"); show_pointcloud(p); shown_pc += 1
        imgs = [f for f in filenames if os.path.splitext(f)[1].lower() in IMG_EXT]
        if imgs and shown_img < 6:
            p = os.path.join(dirpath, imgs[0]); print(f"   IMAGE {os.path.relpath(p, root)}"); show_image(p); shown_img += 1
        for f in filenames:
            if f.lower().endswith((".zip", ".tar", ".tar.gz", ".tgz")):
                list_archive(os.path.join(dirpath, f))
    print("\nTOTAL", human(total))
    print("EXTENSIONS", dict(ext_count.most_common(20)))


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else ".")
