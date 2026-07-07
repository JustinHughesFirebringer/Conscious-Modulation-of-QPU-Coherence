import json
from pathlib import Path
import re
import base64, zlib, io
import numpy as np
from typing import Optional, Tuple

# ---- helpers for classic counts ----
_BIT_RE = re.compile(r'^[01 ]+$', re.ASCII)

def _hex_to_bin(key: str, width: int) -> str:
    if key.startswith("0x"):
        return bin(int(key, 16))[2:].zfill(width)
    if key.startswith("0b"):
        return key[2:].zfill(width)
    if _BIT_RE.match(key):
        return key.replace(" ", "").zfill(width)
    try:
        return bin(int(key))[2:].zfill(width)
    except Exception:
        return key

# ---- Runtime PrimitiveResult decoding ----
def _decode_runtime_primitive_bitarrays(d: dict) -> Optional[Tuple[str, int]]:
    """
    Robust decode of Qiskit Runtime Sampler BitArray payloads (packed integers per shot).
    Tries a permissive traversal first, then the exact path we verified.
    Returns (raw_bitstring, shots) or None.
    """
    def _build_from_fields(fields: dict) -> Optional[Tuple[str,int]]:
        pref = [("c_central", 1), ("c_inner", 5), ("c_middle", 5), ("c_outer", 5)]
        if not all(name in fields for name, _ in pref):
            return None
        regs, widths, shots = [], [], None
        for name, expected_bits in pref:
            f = fields[name]
            fv = f.get("__value__", f)                 # tolerate both shapes
            arr_info = fv.get("array", {})             # {"__type__":"ndarray","__value__": "..."}
            b64 = arr_info.get("__value__")
            if b64 is None:
                return None
            raw = base64.b64decode(b64)
            arr = np.load(io.BytesIO(zlib.decompress(raw)), allow_pickle=False).reshape(-1)
            regs.append(arr)
            widths.append(int(fv.get("num_bits", expected_bits)))
            shots = len(arr) if shots is None else min(shots, len(arr))
        parts = []
        for i in range(shots):
            seg = ''.join(format(int(regs[j][i]), f'0{widths[j]}b') for j in range(4))
            parts.append(seg)
        return ''.join(parts), shots

    # Attempt 1: permissive traversal (handles missing "__type__" wrappers)
    root = d.get("__value__", d)
    pubs = root.get("pub_results") or []
    if pubs and isinstance(pubs, list) and pubs[0]:
        pub_val = pubs[0].get("__value__", pubs[0])
        data_bin = pub_val.get("data", {})
        dv = data_bin.get("__value__", data_bin)
        if isinstance(dv, dict) and "fields" in dv:
            out = _build_from_fields(dv["fields"])
            if out is not None:
                print("  Runtime decode: permissive path OK")
                return out
            else:
                print("  Runtime decode: permissive path found fields but key mismatch")

    # Attempt 2: exact path (the one your one-off test used)
    try:
        dv = d["__value__"]["pub_results"][0]["__value__"]["data"]["__value__"]
        if isinstance(dv, dict) and "fields" in dv:
            out = _build_from_fields(dv["fields"])
            if out is not None:
                print("  Runtime decode: exact path OK")
                return out
            else:
                print("  Runtime decode: exact path found fields but key mismatch")
    except Exception:
        print("  Runtime decode: exact path not present")

    return None

def _decode_counts_like(d: dict) -> Optional[Tuple[str, int]]:
    # Root-level counts
    counts = d.get("counts")
    if counts and isinstance(counts, dict) and counts:
        width = max(len(_hex_to_bin(k, 1)) for k in counts)
        bits = []
        total = 0
        for bit, cnt in sorted(counts.items()):
            b = _hex_to_bin(bit, width)
            bits.extend([b] * cnt)
            total += cnt
        return (''.join(bits), total) if bits else None

    # Qiskit "results[0].data.counts"
    results = d.get("results") or []
    if results and isinstance(results[0], dict):
        data = results[0].get("data") or {}
        c = data.get("counts") or {}
        if c:
            width = max(len(_hex_to_bin(k, 1)) for k in c)
            bits = []
            total = 0
            for bit, cnt in sorted(c.items()):
                b = _hex_to_bin(bit, width)
                bits.extend([b] * cnt)
                total += cnt
            return (''.join(bits), total) if bits else None

    return None

def extract_raw_bitstrings(result_file_path: str, output_file: Optional[str] = None) -> Optional[int]:
    """
    Extract raw bitstrings. Writes to output_file if provided.
    Returns number of shots if successful, else None.
    """
    p = Path(result_file_path)
    try:
        data = json.loads(Path(p).read_text(encoding="utf-8"))

        out = _decode_runtime_primitive_bitarrays(data)
        if out is not None:
            raw, shots = out
            raw = ''.join(raw.split())
            if output_file:
                outp = Path(output_file)
                outp.parent.mkdir(parents=True, exist_ok=True)
                outp.write_text(raw, encoding="utf-8")
            print(f"  OK (Runtime): shots={shots}, bits={shots*16}")
            return shots

        # Classic counts fallback
        out = _decode_counts_like(data)
        if out is not None:
            raw, shots = out
            raw = ''.join(raw.split())
            if output_file:
                outp = Path(output_file)
                outp.parent.mkdir(parents=True, exist_ok=True)
                outp.write_text(raw, encoding="utf-8")
            print(f"  OK (Counts): shots≈{shots}, bits≈{len(raw)}")
            return shots

        print(f"  No results found in {p.name}")
        return None

    except Exception as e:
        print(f"Error processing {p.name}: {e}")
        return None

def process_directory(input_dir: str, output_dir: Optional[str] = None) -> None:
    in_path = Path(input_dir)
    out_path = Path(output_dir) if output_dir else (in_path / "raw_bitstrings")
    out_path.mkdir(parents=True, exist_ok=True)

    # match common shapes
    files = sorted(set(list(in_path.rglob("job-*-result.json")) + list(in_path.rglob("job-*-metrics.json"))))
    print(f"Found {len(files)} result files")

    # job id from 'job-<id>-result.json'
    job_re = re.compile(r"job-([^-\s]+)-(?:result|metrics)\.json$", re.IGNORECASE)

    for f in files:
        print(f"Processing {f.name}...")
        m = job_re.search(f.name)
        job_id = m.group(1) if m else f.stem
        out_file = out_path / f"raw_bitstring_{job_id}.txt"

        shots = extract_raw_bitstrings(str(f), str(out_file))
        if shots:
            print(f"  OK: shots={shots}, bits={shots*16}, -> {out_file.name}")

# ---- CLI ----
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Extract raw bitstrings from IBM/Qiskit results")
    parser.add_argument("--input-dir", required=True, help="Directory containing job result files")
    parser.add_argument("--output-dir", help="Directory to write raw bitstring txt files")
    args = parser.parse_args()
    process_directory(args.input_dir, args.output_dir)
