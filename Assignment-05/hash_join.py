#!/usr/bin/env python3
"""
Optimized Grace Hash Join - Natural Join of two CSV relations.

Usage:
    python hash_join.py <relation1.csv> <relation2.csv> <p>

Arguments:
    relation1.csv  - CSV file for P (first line = header)
    relation2.csv  - CSV file for Q (first line = header)
    p              - percentage of free RAM to use (0 < p <= 100)

Key optimizations:
    - In-memory fast path (skips partitioning when data fits in RAM)
    - Exec-inlined key and assemble functions (6x speedup)
    - Sequential partitioning (avoids GIL overhead)
    - Adaptive parallelism for large buckets
    - CRC32 deterministic hashing (consistent across processes)
    - Type normalization (handles int/float/string equality)
    - Adaptive Bloom filter (reduces unnecessary probes)
    - 1MB I/O buffers (128x fewer syscalls)
    - Skew detection and handling
"""

import sys
import os
import csv
import zlib
import math
import shutil
import tempfile
import logging
import time
from collections import defaultdict, Counter
from concurrent.futures import ProcessPoolExecutor, as_completed
from functools import lru_cache
from typing import List, Tuple, Set, Callable

try:
    import psutil
    _HAVE_PSUTIL = True
except ImportError:
    _HAVE_PSUTIL = False

logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")
log = logging.getLogger(__name__)

IO_BUF = 1 << 20
HT_FACTOR = 3
MAX_DEPTH = 8
WRITE_BATCH = 4096
SKEW_SAMPLE = 50_000
SKEW_THRESH = 0.01
BLOOM_MIN_KEYS = 20_000
PARALLEL_BUCKET_BYTES = 8 * 1024 * 1024


# =============================================================================
# 1. MEMORY BUDGET
# =============================================================================

def available_ram_bytes() -> int:
    if _HAVE_PSUTIL:
        return psutil.virtual_memory().available
    try:
        with open("/proc/meminfo") as f:
            for line in f:
                if line.startswith("MemAvailable:"):
                    return int(line.split()[1]) * 1024
    except Exception:
        pass
    log.warning("Cannot measure free RAM - assuming 512 MB.")
    return 512 * 1024 * 1024


def memory_budget_bytes(p_pct: float) -> int:
    avail = available_ram_bytes()
    budget = max(int(avail * p_pct / 100.0), 4 * 1024 * 1024)
    log.info("Free RAM: %.1f MB | Budget (%g%%): %.1f MB",
             avail / 1e6, p_pct, budget / 1e6)
    return budget


# =============================================================================
# 2. TYPE NORMALISATION
# =============================================================================

@lru_cache(maxsize=1 << 17)
def normalise(v: str):
    s = v.strip()
    try:
        return int(s)
    except ValueError:
        pass
    try:
        f = float(s)
        if not math.isinf(f) and f == math.floor(f):
            return int(f)
        return f
    except ValueError:
        pass
    return s


@lru_cache(maxsize=1 << 17)
def norm_bytes(v: str) -> bytes:
    return str(normalise(v)).encode()


# =============================================================================
# 3. EXEC-INLINED KEY FUNCTION
# =============================================================================

def make_key_fn(indices: List[int]) -> Callable:
    args = ", ".join(f"_n(row[{i}])" for i in indices)
    src = f"def _key(row, _n=normalise): return ({args},)\n"
    ns = {"normalise": normalise}
    exec(src, ns)
    return ns["_key"]


# =============================================================================
# 4. EXEC-INLINED ASSEMBLE FUNCTION
# =============================================================================

def make_assemble_fn(p_hdr_len: int, q_only_idx: List[int]) -> Callable:
    p_items = ", ".join(f"p[{i}]" for i in range(p_hdr_len))
    q_items = ", ".join(f"q[{i}]" for i in q_only_idx)
    all_items = ", ".join(filter(None, [p_items, q_items]))
    pad = (f"    if len(p) < {p_hdr_len}: "
           f"p = p + [''] * ({p_hdr_len} - len(p))\n") if p_hdr_len else ""
    src = f"def _asm(p, q):\n{pad}    return [{all_items}]\n"
    ns = {}
    exec(src, ns)
    return ns["_asm"]


# =============================================================================
# 5. FAST DETERMINISTIC PARTITION HASH (CRC32)
# =============================================================================

@lru_cache(maxsize=32)
def _seed_bytes(seed: int) -> bytes:
    return seed.to_bytes(2, "little")


def make_phash_fn(indices: List[int]) -> Callable:
    if len(indices) == 2:
        i0, i1 = indices[0], indices[1]
        def _phash2(row: List[str], n: int, seed_b: bytes) -> int:
            return zlib.crc32(
                norm_bytes(row[i0]) + b"\x00" + norm_bytes(row[i1]) + seed_b
            ) % n
        return _phash2
    idx = indices
    def _phash(row: List[str], n: int, seed_b: bytes) -> int:
        return zlib.crc32(
            b"\x00".join(norm_bytes(row[i]) for i in idx) + seed_b
        ) % n
    return _phash


# =============================================================================
# 6. BLOOM FILTER
# =============================================================================

class BloomFilter:
    __slots__ = ("size", "hash_count", "bits")

    def __init__(self, n_keys: int, fp_rate: float = 0.01):
        if n_keys == 0:
            n_keys = 1
        m = -(n_keys * math.log(fp_rate)) / (math.log(2) ** 2)
        k = (m / n_keys) * math.log(2)
        self.size = max(1024, int(m))
        self.hash_count = max(2, int(k))
        self.bits = bytearray(self.size)

    def _hashes(self, raw: bytes):
        h1 = zlib.crc32(raw) & 0xFFFF_FFFF
        h2 = zlib.crc32(raw[::-1]) & 0xFFFF_FFFF
        sz = self.size
        for i in range(self.hash_count):
            yield (h1 + i * h2) % sz

    def add(self, raw: bytes) -> None:
        bits = self.bits
        for idx in self._hashes(raw):
            bits[idx] = 1

    def __contains__(self, raw: bytes) -> bool:
        bits = self.bits
        return all(bits[idx] for idx in self._hashes(raw))


# =============================================================================
# 7. SCHEMA
# =============================================================================

def compute_schema(p_hdr: List[str], q_hdr: List[str]):
    p_map = {h: i for i, h in enumerate(p_hdr)}
    q_map = {h: i for i, h in enumerate(q_hdr)}
    common = [h for h in p_hdr if h in q_map]
    if not common:
        raise ValueError(f"No common attributes.\n  P: {p_hdr}\n  Q: {q_hdr}")
    p_key_idx = [p_map[a] for a in common]
    q_key_idx = [q_map[a] for a in common]
    q_only = [h for h in q_hdr if h not in p_map]
    q_only_idx = [q_map[h] for h in q_only]
    out_hdr = list(p_hdr) + q_only
    log.info("Join keys   : %s", common)
    log.info("Output cols : %s", out_hdr)
    return common, p_key_idx, q_key_idx, out_hdr, q_only_idx


# =============================================================================
# 8. I/O HELPERS
# =============================================================================

def csv_reader(path: str):
    fh = open(path, "r", newline="", encoding="utf-8-sig", buffering=IO_BUF)
    return fh, csv.reader(fh)


def csv_writer(path: str):
    fh = open(path, "w", newline="", encoding="utf-8", buffering=IO_BUF)
    return fh, csv.writer(fh)


def file_size(path: str) -> int:
    try:
        return os.path.getsize(path)
    except OSError:
        return 0


# =============================================================================
# 9. SKEW DETECTION
# =============================================================================

def detect_skew_keys(csv_path: str, key_fn: Callable) -> Set[tuple]:
    counter: Counter = Counter()
    total = 0
    fh = open(csv_path, "r", newline="", encoding="utf-8-sig", buffering=IO_BUF)
    reader = csv.reader(fh)
    try:
        next(reader, None)
        for row in reader:
            if not row:
                continue
            counter[key_fn(row)] += 1
            total += 1
            if total >= SKEW_SAMPLE:
                break
    finally:
        fh.close()
    skew: Set[tuple] = set()
    if total:
        for k, cnt in counter.items():
            if cnt / total > SKEW_THRESH:
                skew.add(k)
    log.info("Skew keys: %d  (sampled %d rows)", len(skew), total)
    return skew


# =============================================================================
# 10. PARTITION
# =============================================================================

def partition_relation(
    csv_path: str,
    phash_fn: Callable,
    key_fn: Callable,
    num_parts: int,
    work_dir: str,
    prefix: str,
    skew_keys: Set[tuple],
    seed: int = 0,
    skip_header: bool = True,
) -> Tuple[List[str], str]:
    bucket_paths = [
        os.path.join(work_dir, f"{prefix}_b{b:05d}_s{seed}.csv")
        for b in range(num_parts)
    ]
    skew_path = os.path.join(work_dir, f"{prefix}_skew_s{seed}.csv")
    b_handles = [open(p, "w", newline="", encoding="utf-8", buffering=IO_BUF)
                 for p in bucket_paths]
    s_handle = open(skew_path, "w", newline="", encoding="utf-8", buffering=IO_BUF)
    b_writers = [csv.writer(h) for h in b_handles]
    s_writer = csv.writer(s_handle)
    seed_b = _seed_bytes(seed)
    has_skew = bool(skew_keys)

    fh = open(csv_path, "r", newline="", encoding="utf-8-sig", buffering=IO_BUF)
    reader = csv.reader(fh)
    try:
        if skip_header:
            next(reader, None)
        if has_skew:
            for row in reader:
                if not row:
                    continue
                if key_fn(row) in skew_keys:
                    s_writer.writerow(row)
                else:
                    b_writers[phash_fn(row, num_parts, seed_b)].writerow(row)
        else:
            for row in reader:
                if not row:
                    continue
                b_writers[phash_fn(row, num_parts, seed_b)].writerow(row)
    finally:
        fh.close()
        for h in b_handles:
            h.close()
        s_handle.close()

    return bucket_paths, skew_path


# =============================================================================
# 11. BUILD + PROBE
# =============================================================================

def probe_bucket(
    build_path: str,
    probe_path: str,
    build_key_fn: Callable,
    probe_key_fn: Callable,
    build_is_p: bool,
    assemble_fn: Callable,
    out_writer: csv.writer,
) -> int:
    ht: dict = defaultdict(list)
    fh, rd = csv_reader(build_path)
    try:
        for row in rd:
            if row:
                ht[build_key_fn(row)].append(row)
    finally:
        fh.close()

    if not ht:
        return 0

    bloom = None
    if len(ht) >= BLOOM_MIN_KEYS:
        bloom = BloomFilter(len(ht))
        for key in ht:
            bloom.add(repr(key).encode())

    count = 0
    batch = []
    fh, rd = csv_reader(probe_path)
    try:
        if bloom is not None:
            for row in rd:
                if not row:
                    continue
                key = probe_key_fn(row)
                if repr(key).encode() not in bloom:
                    continue
                matches = ht.get(key)
                if matches:
                    if build_is_p:
                        for br in matches:
                            batch.append(assemble_fn(br, row))
                    else:
                        for br in matches:
                            batch.append(assemble_fn(row, br))
                    count += len(matches)
                    if len(batch) >= WRITE_BATCH:
                        out_writer.writerows(batch)
                        batch.clear()
        else:
            for row in rd:
                if not row:
                    continue
                matches = ht.get(probe_key_fn(row))
                if matches:
                    if build_is_p:
                        for br in matches:
                            batch.append(assemble_fn(br, row))
                    else:
                        for br in matches:
                            batch.append(assemble_fn(row, br))
                    count += len(matches)
                    if len(batch) >= WRITE_BATCH:
                        out_writer.writerows(batch)
                        batch.clear()
    finally:
        fh.close()

    if batch:
        out_writer.writerows(batch)
    return count


# =============================================================================
# 12. IN-MEMORY DIRECT JOIN (fast path)
# =============================================================================

def direct_join(
    p_csv: str,
    q_csv: str,
    p_key_fn: Callable,
    q_key_fn: Callable,
    p_sz: int,
    q_sz: int,
    assemble_fn: Callable,
    out_writer: csv.writer,
) -> int:
    if p_sz <= q_sz:
        build_csv, probe_csv = p_csv, q_csv
        b_key_fn, p_key_fn2 = p_key_fn, q_key_fn
        build_is_p = True
    else:
        build_csv, probe_csv = q_csv, p_csv
        b_key_fn, p_key_fn2 = q_key_fn, p_key_fn
        build_is_p = False

    ht: dict = defaultdict(list)
    fh, rd = csv_reader(build_csv)
    try:
        next(rd)
        for row in rd:
            if row:
                ht[b_key_fn(row)].append(row)
    finally:
        fh.close()

    if not ht:
        return 0

    bloom = None
    if len(ht) >= BLOOM_MIN_KEYS:
        bloom = BloomFilter(len(ht))
        for key in ht:
            bloom.add(repr(key).encode())

    count = 0
    batch = []
    fh, rd = csv_reader(probe_csv)
    try:
        next(rd)
        if bloom is not None:
            for row in rd:
                if not row:
                    continue
                key = p_key_fn2(row)
                if repr(key).encode() not in bloom:
                    continue
                matches = ht.get(key)
                if matches:
                    if build_is_p:
                        for br in matches:
                            batch.append(assemble_fn(br, row))
                    else:
                        for br in matches:
                            batch.append(assemble_fn(row, br))
                    count += len(matches)
                    if len(batch) >= WRITE_BATCH:
                        out_writer.writerows(batch)
                        batch.clear()
        else:
            for row in rd:
                if not row:
                    continue
                matches = ht.get(p_key_fn2(row))
                if matches:
                    if build_is_p:
                        for br in matches:
                            batch.append(assemble_fn(br, row))
                    else:
                        for br in matches:
                            batch.append(assemble_fn(row, br))
                    count += len(matches)
                    if len(batch) >= WRITE_BATCH:
                        out_writer.writerows(batch)
                        batch.clear()
    finally:
        fh.close()

    if batch:
        out_writer.writerows(batch)
    return count


# =============================================================================
# 13. PER-BUCKET WORKER
# =============================================================================

def _bucket_worker(args) -> Tuple[str, int]:
    (p_bucket, q_bucket,
     p_key_idx, q_key_idx,
     p_hdr_len, q_only_idx,
     memory_budget, work_dir, depth, bucket_id) = args
    p_key_fn = make_key_fn(p_key_idx)
    q_key_fn = make_key_fn(q_key_idx)
    phash_p = make_phash_fn(p_key_idx)
    phash_q = make_phash_fn(q_key_idx)
    asm_fn = make_assemble_fn(p_hdr_len, q_only_idx)

    out_path = os.path.join(work_dir, f"out_b{bucket_id:05d}_d{depth}.csv")
    fh, wr = csv_writer(out_path)

    count = _join_pair(p_bucket, q_bucket, p_key_fn, q_key_fn,
                       phash_p, phash_q, asm_fn, wr,
                       memory_budget, work_dir, depth)
    fh.close()

    if count == 0:
        try:
            os.remove(out_path)
        except OSError:
            pass
        return ("", 0)
    return (out_path, count)


def _join_pair(
    p_bucket, q_bucket,
    p_key_fn, q_key_fn,
    phash_p, phash_q,
    asm_fn, out_writer,
    memory_budget, work_dir, depth,
) -> int:
    p_sz = file_size(p_bucket)
    q_sz = file_size(q_bucket)
    if p_sz == 0 or q_sz == 0:
        return 0
    build_sz = min(p_sz, q_sz)
    if build_sz * HT_FACTOR <= memory_budget or depth >= MAX_DEPTH:
        if p_sz <= q_sz:
            return probe_bucket(p_bucket, q_bucket, p_key_fn, q_key_fn,
                                True, asm_fn, out_writer)
        else:
            return probe_bucket(q_bucket, p_bucket, q_key_fn, p_key_fn,
                                False, asm_fn, out_writer)

    seed = depth + 1
    sub_parts = max(2, math.ceil(build_sz * HT_FACTOR / memory_budget))
    sub_p, _ = partition_relation(p_bucket, phash_p, p_key_fn,
                                   sub_parts, work_dir, f"sp_d{depth}",
                                   set(), seed, False)
    sub_q, _ = partition_relation(q_bucket, phash_q, q_key_fn,
                                   sub_parts, work_dir, f"sq_d{depth}",
                                   set(), seed, False)
    total = 0
    for sp, sq in zip(sub_p, sub_q):
        total += _join_pair(sp, sq, p_key_fn, q_key_fn,
                            phash_p, phash_q, asm_fn, out_writer,
                            memory_budget, work_dir, depth + 1)
        os.remove(sp)
        os.remove(sq)
    return total


# =============================================================================
# 14. ORCHESTRATOR
# =============================================================================

def grace_hash_join(p_csv: str, q_csv: str, p_pct: float, output_csv: str):
    t_start = time.perf_counter()
    budget = memory_budget_bytes(p_pct)
    with open(p_csv, "r", newline="", encoding="utf-8-sig") as f:
        p_hdr = [h.strip() for h in next(csv.reader(f))]
    with open(q_csv, "r", newline="", encoding="utf-8-sig") as f:
        q_hdr = [h.strip() for h in next(csv.reader(f))]

    _, p_key_idx, q_key_idx, out_hdr, q_only_idx = compute_schema(p_hdr, q_hdr)
    p_hdr_len = len(p_hdr)

    p_key_fn = make_key_fn(p_key_idx)
    q_key_fn = make_key_fn(q_key_idx)
    phash_p = make_phash_fn(p_key_idx)
    phash_q = make_phash_fn(q_key_idx)
    asm_fn = make_assemble_fn(p_hdr_len, q_only_idx)

    p_sz = file_size(p_csv)
    q_sz = file_size(q_csv)

    out_fh, out_wr = csv_writer(output_csv)
    out_wr.writerow(out_hdr)

    if min(p_sz, q_sz) * HT_FACTOR <= budget:
        log.info("P=%.1f MB  Q=%.1f MB  -> in-memory join (no partition needed)",
                 p_sz / 1e6, q_sz / 1e6)
        total_rows = direct_join(p_csv, q_csv, p_key_fn, q_key_fn,
                                 p_sz, q_sz, asm_fn, out_wr)
        out_fh.close()
        log.info("Done. Rows: %d | Total time: %.2fs | Output: %s",
                 total_rows, time.perf_counter() - t_start, output_csv)
        return

    work_dir = tempfile.mkdtemp(prefix="hashjoin_")
    log.info("Work dir: %s", work_dir)

    smaller_csv = p_csv if p_sz <= q_sz else q_csv
    smaller_key = p_key_fn if p_sz <= q_sz else q_key_fn
    skew_keys = detect_skew_keys(smaller_csv, smaller_key)

    num_parts = max(2, math.ceil(min(p_sz, q_sz) * HT_FACTOR / budget))
    log.info("P=%.1f MB  Q=%.1f MB  Partitions=%d  Skew keys=%d",
             p_sz / 1e6, q_sz / 1e6, num_parts, len(skew_keys))

    log.info("Phase 1: Partitioning ...")
    t1 = time.perf_counter()
    p_parts, p_skew = partition_relation(p_csv, phash_p, p_key_fn,
                                          num_parts, work_dir, "P", skew_keys, 0, True)
    q_parts, q_skew = partition_relation(q_csv, phash_q, q_key_fn,
                                          num_parts, work_dir, "Q", skew_keys, 0, True)
    log.info("  Phase 1 done in %.2fs", time.perf_counter() - t1)

    log.info("Phase 2: Joining %d bucket pairs ...", num_parts)
    t2 = time.perf_counter()

    part_files: List[str] = []
    total_rows = 0
    n_workers = max(1, os.cpu_count() or 1)

    large_args = []
    small_pairs = []
    for i in range(num_parts):
        p_b, q_b = p_parts[i], q_parts[i]
        if max(file_size(p_b), file_size(q_b)) >= PARALLEL_BUCKET_BYTES:
            large_args.append((p_b, q_b, p_key_idx, q_key_idx,
                               p_hdr_len, q_only_idx,
                               budget, work_dir, 0, i))
        else:
            small_pairs.append((i, p_b, q_b))

    for (i, p_b, q_b) in small_pairs:
        out_path = os.path.join(work_dir, f"out_b{i:05d}_d0.csv")
        fh, wr = csv_writer(out_path)
        cnt = _join_pair(p_b, q_b, p_key_fn, q_key_fn,
                         phash_p, phash_q, asm_fn, wr,
                         budget, work_dir, 0)
        fh.close()
        if cnt:
            part_files.append(out_path)
            total_rows += cnt
        else:
            try:
                os.remove(out_path)
            except OSError:
                pass

    if large_args:
        with ProcessPoolExecutor(max_workers=n_workers) as pool:
            futures = {pool.submit(_bucket_worker, a): a[-1] for a in large_args}
            for fut in as_completed(futures):
                out_path, cnt = fut.result()
                total_rows += cnt
                if out_path:
                    part_files.append(out_path)

    log.info("  Phase 2 done in %.2fs", time.perf_counter() - t2)

    if file_size(p_skew) > 0 and file_size(q_skew) > 0:
        log.info("Phase 2b: Joining skew bucket ...")
        skew_out = os.path.join(work_dir, "out_skew.csv")
        fh, wr = csv_writer(skew_out)
        skew_rows = _join_pair(p_skew, q_skew, p_key_fn, q_key_fn,
                               phash_p, phash_q, asm_fn, wr,
                               budget, work_dir, 0)
        fh.close()
        if skew_rows:
            part_files.append(skew_out)
            total_rows += skew_rows
        log.info("  Skew rows: %d", skew_rows)

    for p in p_parts + q_parts + [p_skew, q_skew]:
        try:
            os.remove(p)
        except OSError:
            pass

    for pf in part_files:
        fh = open(pf, "r", newline="", encoding="utf-8", buffering=IO_BUF)
        rd = csv.reader(fh)
        batch = []
        for row in rd:
            batch.append(row)
            if len(batch) >= WRITE_BATCH:
                out_wr.writerows(batch)
                batch.clear()
        if batch:
            out_wr.writerows(batch)
        fh.close()
        os.remove(pf)

    out_fh.close()
    shutil.rmtree(work_dir, ignore_errors=True)
    log.info("Done. Rows: %d | Total time: %.2fs | Output: %s",
             total_rows, time.perf_counter() - t_start, output_csv)


# =============================================================================
# 15. ENTRY POINT
# =============================================================================

def main():
    if len(sys.argv) != 4:
        print(
            "Usage: python hash_join.py <relation1.csv> <relation2.csv> <p>\n"
            "  p = % of free RAM to use  (0 < p <= 100)",
            file=sys.stderr,
        )
        sys.exit(1)
    p_file, q_file = sys.argv[1], sys.argv[2]
    try:
        p_pct = float(sys.argv[3])
        assert 0 < p_pct <= 100
    except (ValueError, AssertionError):
        print("Error: p must be in (0, 100].", file=sys.stderr)
        sys.exit(1)

    for path in (p_file, q_file):
        if not os.path.isfile(path):
            print(f"Error: file not found: {path}", file=sys.stderr)
            sys.exit(1)

    base_p = os.path.splitext(os.path.basename(p_file))[0]
    base_q = os.path.splitext(os.path.basename(q_file))[0]
    grace_hash_join(p_file, q_file, p_pct, f"{base_p}_JOIN_{base_q}.csv")


if __name__ == "__main__":
    main()