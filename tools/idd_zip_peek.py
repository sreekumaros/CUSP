"""Read the IDD-3D zip directly on the server and download only the files you need.

The server supports byte-range requests (resuming works), so we can
  1. fetch only the zip's table of contents (the central directory, at the end of the file), and
  2. fetch and unpack only selected entries (e.g. labels + calibration + front camera of 2-3 sequences),
instead of downloading all 254 GB.

Login: run idd_download.sh once until it prints "Logged in." (then Ctrl-C); it leaves the cookie file
<out>/.idd_cookies.txt that this script reuses.

Usage:
  # 1) table of contents -> idd3d_index.csv + summary of folders and sizes
  python idd_zip_peek.py list  --out data/idd3d
  # 2) download + unpack only matching entries (substring or glob patterns, any can match)
  python idd_zip_peek.py fetch --out data/idd3d \
        --include "*calib*" "*label*" --dry-run
"""
import argparse, csv, fnmatch, os, struct, subprocess, sys, time, zlib

LINK = "https://idd.insaan.iiit.ac.in/dataset/download/63a4b9f0-189a-41ce-b66a-3b81874b9e1c/"
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"


class Remote:
    def __init__(self, url, jar, tries=30):
        self.url, self.jar, self.tries = url, jar, tries

    def get(self, start, end):
        """Bytes [start, end] inclusive, retrying until complete."""
        want = end - start + 1
        for k in range(self.tries):
            cmd = ["curl", "-sSL", "-A", UA, "--max-time", "900", "-r", f"{start}-{end}", self.url]
            if self.jar and os.path.exists(self.jar):
                cmd[1:1] = ["-b", self.jar, "-c", self.jar]
            p = subprocess.run(cmd, capture_output=True)
            data = p.stdout
            if p.returncode == 0 and len(data) == want:
                return data
            if data[:15].lower().startswith((b"<!doctype", b"<html")):
                sys.exit("Server returned a web page: login expired. Run idd_download.sh until 'Logged in.', then retry.")
            print(f"    range {start}-{end}: got {len(data)}/{want} bytes (curl {p.returncode}), retry {k + 1}")
            time.sleep(min(60, 5 * (k + 1)))
        sys.exit("Giving up on this range; run the command again later.")

    def size(self):
        cmd = ["curl", "-sIL", "-A", UA, self.url]
        if self.jar and os.path.exists(self.jar):
            cmd[1:1] = ["-b", self.jar]
        h = subprocess.run(cmd, capture_output=True, text=True).stdout
        n = [l.split(":", 1)[1].strip() for l in h.splitlines() if l.lower().startswith("content-length:")]
        if not n or "text/html" in h.lower().split("content-type:")[-1][:40]:
            sys.exit("Could not get file size (login expired?). Run idd_download.sh until 'Logged in.'")
        return int(n[-1])


def read_central_directory(r):
    total = r.size()
    tail_len = min(total, 1 << 20)
    tail = r.get(total - tail_len, total - 1)
    i = tail.rfind(b"PK\x05\x06")
    if i < 0:
        sys.exit("End of central directory not found.")
    _, _, _, n_this, n_total, cd_size, cd_off, _ = struct.unpack("<IHHHHIIH", tail[i:i + 22])
    j = tail.rfind(b"PK\x06\x07", 0, i)                     # zip64 locator
    if j >= 0:
        (z64_off,) = struct.unpack("<Q", tail[j + 8:j + 16])
        z = r.get(z64_off, z64_off + 55)
        n_total, cd_size, cd_off = struct.unpack("<QQQ", z[32:56])
    print(f"archive {total / 1e9:.1f} GB, {n_total} entries, central directory {cd_size / 1e6:.1f} MB")
    cd = b"".join(r.get(s, min(s + (64 << 20), cd_off + cd_size) - 1)
                  for s in range(cd_off, cd_off + cd_size, 64 << 20))
    entries, p = [], 0
    while p + 46 <= len(cd) and cd[p:p + 4] == b"PK\x01\x02":
        (flags, method, crc, csize, usize, nlen, elen, clen, lho) = (
            struct.unpack("<H", cd[p + 8:p + 10])[0], struct.unpack("<H", cd[p + 10:p + 12])[0],
            *struct.unpack("<III", cd[p + 16:p + 28]), *struct.unpack("<HHH", cd[p + 28:p + 34]),
            struct.unpack("<I", cd[p + 42:p + 46])[0])
        name = cd[p + 46:p + 46 + nlen].decode("utf-8", "replace")
        extra = cd[p + 46 + nlen:p + 46 + nlen + elen]
        q = 0
        while q + 4 <= len(extra):
            hid, hlen = struct.unpack("<HH", extra[q:q + 4]); body = extra[q + 4:q + 4 + hlen]
            if hid == 0x0001:
                vals, b = [], 0
                for cur in (usize, csize, lho):
                    if cur == 0xFFFFFFFF and b + 8 <= len(body):
                        vals.append(struct.unpack("<Q", body[b:b + 8])[0]); b += 8
                    else:
                        vals.append(cur)
                usize, csize, lho = vals
            q += 4 + hlen
        entries.append(dict(name=name, method=method, csize=csize, usize=usize, offset=lho, crc=crc))
        p += 46 + nlen + elen + clen
    return entries


def summarise(entries, depth=3):
    agg = {}
    for e in entries:
        parts = e["name"].rstrip("/").split("/")
        for d in range(1, min(depth, len(parts) - 1) + 1):
            k = "/".join(parts[:d]) + "/"
            n, s = agg.get(k, (0, 0)); agg[k] = (n + 1, s + e["csize"])
    for k in sorted(agg):
        n, s = agg[k]
        print(f"{'  ' * (k.count('/') - 1)}{k:60s} {n:8d} files {s / 1e9:8.2f} GB")


def matches(name, pats):
    return any(fnmatch.fnmatch(name, p) or (not any(c in p for c in "*?[") and p in name) for p in pats)


def fetch(r, entries, out, include, exclude, dry):
    sel = [e for e in entries if not e["name"].endswith("/") and matches(e["name"], include)
           and not (exclude and matches(e["name"], exclude))]
    sel.sort(key=lambda e: e["offset"])
    tot = sum(e["csize"] for e in sel)
    print(f"selected {len(sel)} files, {tot / 1e9:.2f} GB compressed")
    for e in sel[:15]:
        print("   ", e["name"])
    if len(sel) > 15:
        print("    ...")
    if dry or not sel:
        return
    # group neighbouring entries into ranges of <= 256 MB (fewer requests for many small files)
    groups, cur = [], []
    for e in sel:
        end = e["offset"] + 30 + len(e["name"].encode()) + 1024 + e["csize"]
        if cur and (e["offset"] - cur[-1][1] > (1 << 20) or end - cur[0][0]["offset"] > (256 << 20)):
            groups.append(cur); cur = []
        cur.append((e, end))
    if cur:
        groups.append(cur)
    done_bytes = 0
    for gi, g in enumerate(groups):
        todo = [(e, end) for e, end in g if not os.path.exists(os.path.join(out, e["name"]))
                or os.path.getsize(os.path.join(out, e["name"])) != e["usize"]]
        if not todo:
            done_bytes += sum(e["csize"] for e, _ in g); continue
        a = todo[0][0]["offset"]; b = max(end for _, end in todo)
        blob = r.get(a, b)
        for e, _ in todo:
            o = e["offset"] - a
            if blob[o:o + 4] != b"PK\x03\x04":
                print("  bad local header for", e["name"]); continue
            nlen, elen = struct.unpack("<HH", blob[o + 26:o + 30])
            d0 = o + 30 + nlen + elen
            raw = blob[d0:d0 + e["csize"]]
            if len(raw) < e["csize"]:                       # header extra was longer than our slack
                raw = r.get(a + d0, a + d0 + e["csize"] - 1)
            data = raw if e["method"] == 0 else zlib.decompressobj(-15).decompress(raw) if e["method"] == 8 else None
            if data is None:
                print("  unsupported compression", e["method"], e["name"]); continue
            if (zlib.crc32(data) & 0xFFFFFFFF) != e["crc"]:
                print("  CRC mismatch, skipped:", e["name"]); continue
            path = os.path.join(out, e["name"]); os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, "wb") as f:
                f.write(data)
        done_bytes += sum(e["csize"] for e, _ in g)
        print(f"  group {gi + 1}/{len(groups)}  {done_bytes / 1e9:.2f}/{tot / 1e9:.2f} GB")
    print("done ->", out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["list", "fetch"])
    ap.add_argument("--out", default="data/idd3d")
    ap.add_argument("--link", default=LINK)
    ap.add_argument("--include", nargs="+", default=[])
    ap.add_argument("--exclude", nargs="+", default=[])
    ap.add_argument("--depth", type=int, default=3)
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    r = Remote(a.link, os.path.join(a.out, ".idd_cookies.txt"))
    idx = os.path.join(a.out, "idd3d_index.csv")
    if a.cmd == "list" or not os.path.exists(idx):
        entries = read_central_directory(r)
        with open(idx, "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=list(entries[0])); w.writeheader(); w.writerows(entries)
        print("index ->", idx)
        summarise(entries, a.depth)
        if a.cmd == "list":
            return
    entries = [dict(name=d["name"], method=int(d["method"]), csize=int(d["csize"]), usize=int(d["usize"]),
                    offset=int(d["offset"]), crc=int(d["crc"])) for d in csv.DictReader(open(idx))]
    if not a.include:
        sys.exit("give --include patterns, e.g. --include '*calib*' '*label*'")
    fetch(r, entries, a.out, a.include, a.exclude, a.dry_run)


if __name__ == "__main__":
    main()
