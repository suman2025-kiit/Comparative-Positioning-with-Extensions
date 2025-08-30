#!/usr/bin/env python3
"""
NFTBench-25 runner: synthetic now; swap in real chain RPC + tc/netem later.

Usage (synthetic demo, writes CSVs under ./out):
  python nftbench25.py --mode synthetic --chain "Polygon (Amoy)" --concurrency 64 --duration 120
  python nftbench25.py --mode synthetic --chain "Solana (devnet)" --concurrency 64 --duration 120

Usage (real harness, after you implement adapters):
  sudo python nftbench25.py --mode evm --chain "Polygon (Amoy)" \
       --rpc http://127.0.0.1:8545 --iface eth0 --rtt-ms 50 --jitter-ms 5 \
       --concurrency 64 --duration 600

Notes
- `tc netem` needs root; the tool will no-op if tc isn’t available / you don’t pass --iface.
- Closed-loop load: exactly N in-flight requests (constant concurrency).
- Percentiles: p50/p75/p90/p95/p99; throughput (events/s); median KB/update.
"""

from __future__ import annotations
import argparse, asyncio, csv, math, os, sys, time, subprocess, contextlib
from pathlib import Path
from typing import Optional, Dict, Any, List, Tuple
import random

try:
    import numpy as np
except Exception:
    print("numpy required; pip install numpy", file=sys.stderr); raise

# -------- helpers --------

def percentiles(values: List[float]) -> Dict[str, float]:
    arr = np.asarray(values, dtype=float)
    qs = np.percentile(arr, [50, 75, 90, 95, 99])
    return {
        "p50 (s)": float(qs[0]),
        "p75 (s)": float(qs[1]),
        "p90 (s)": float(qs[2]),
        "p95 (s)": float(qs[3]),
        "p99 (s)": float(qs[4]),
    }

def closed_loop_tps(concurrency: int, p50_s: float) -> float:
    # not exact, but a stable, comparable approximation
    return float(concurrency) / max(p50_s, 1e-6)

def now_s() -> float:
    return time.perf_counter()

@contextlib.contextmanager
def tc_profile(iface: Optional[str], rtt_ms: Optional[int], jitter_ms: Optional[int], loss_pct: Optional[float]):
    """
    Apply a netem profile to `iface`. Requires sudo. If iface is None → no-op.
    """
    if not iface:
        yield
        return
    # Compose netem args
    parts = []
    if rtt_ms is not None:
        delay = max(int(rtt_ms // 2), 0)  # one-way delay ~ half-RTT
        if jitter_ms and jitter_ms > 0:
            parts += ["delay", f"{delay}ms", f"{jitter_ms}ms", "distribution", "normal"]
        else:
            parts += ["delay", f"{delay}ms"]
    if loss_pct and loss_pct > 0:
        parts += ["loss", f"{loss_pct}%"]
    cmd_add = ["tc", "qdisc", "add", "dev", iface, "root", "netem"] + parts
    cmd_del = ["tc", "qdisc", "del", "dev", iface, "root"]
    try:
        # delete stale first (ignore errors)
        subprocess.run(cmd_del, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        if parts:
            subprocess.run(cmd_add, check=True)
        yield
    except Exception as e:
        print(f"[tc] warning: {e} (continuing without netem)", file=sys.stderr)
        yield
    finally:
        try:
            subprocess.run(cmd_del, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except Exception:
            pass

# -------- adapters (swap synthetic with your real chain RPC) --------

class Adapter:
    chain_name: str
    def __init__(self, chain_name: str):
        self.chain_name = chain_name
    async def prepare(self): ...
    async def event_update(self) -> Tuple[float, float]:
        """
        Perform a single end-to-end event→metadata commit.
        Return (latency_seconds, memory_kb_for_update).
        """
        raise NotImplementedError
    async def teardown(self): ...

class SyntheticAdapter(Adapter):
    """
    Heavy-tailed synthetic generator. Replace with real RPC logic in EVM/Solana adapters.
    """
    def __init__(self, chain_name: str, rtt_min_ms=20, rtt_max_ms=150):
        super().__init__(chain_name)
        self.rng = random.Random(42)
        self.rtt_min = rtt_min_ms; self.rtt_max = rtt_max_ms
        self.commit_medians = {
            "Polygon (Amoy)": 0.60,
            "Arbitrum (Sepolia)": 0.50,
            "Solana (devnet)": 0.30,
            "Flow (testnet)": 0.40,
            "Immutable X (test)": 0.35,
        }
        self.offchain_median = 0.20
        self.consensus_median = 0.05

    def _lognormal(self, median: float, sigma: float) -> float:
        # median = exp(mu)
        mu = math.log(max(median, 1e-9))
        # Python's random.lognormvariate uses mu, sigma of underlying normal
        return float(random.lognormvariate(mu, sigma))

    async def prepare(self): return

    async def event_update(self) -> Tuple[float, float]:
        # Simulate components
        rtt = self.rng.uniform(self.rtt_min, self.rtt_max) / 1000.0 * 2.0
        commit = self._lognormal(self.commit_medians.get(self.chain_name, 0.50), sigma=0.50)
        offchain = self._lognormal(self.offchain_median, sigma=0.35)
        jitter = self._lognormal(self.consensus_median, sigma=0.40)
        latency = rtt + commit + offchain + jitter
        mem_kb = max(0.55, random.gauss(0.75, 0.08))  # ~0.75 KB median
        # No actual work; small sleep to keep event loop fair
        await asyncio.sleep(0)
        return latency, mem_kb

    async def teardown(self): return

# ---- Example stubs for real harness (fill in when ready) ----

class EVMAdapter(Adapter):
    """
    Placeholder for EVM-like chains (Ethereum/Polygon/Arbitrum).
    Implement: connect to RPC, build and send tx, wait for inclusion/finality, update token metadata.
    """
    def __init__(self, chain_name: str, rpc: str, private_key: str | None = None):
        super().__init__(chain_name)
        self.rpc = rpc
        self.private_key = private_key
        self.web3 = None  # lazy

    async def prepare(self):
        # from web3 import Web3  # uncomment when using web3.py
        # self.web3 = Web3(Web3.HTTPProvider(self.rpc, request_kwargs={"timeout": 30}))
        # assert self.web3.is_connected(), "RPC not reachable"
        return

    async def event_update(self) -> Tuple[float, float]:
        t0 = now_s()
        # 1) build tx: call contract method that writes new metadata/URI
        # 2) sign & sendRawTransaction
        # 3) wait for receipt + finality (N blocks if needed)
        # 4) OPTIONAL: off-chain proof verification time (measure separately if your design needs it)
        # PSEUDO:
        # tx = contract.functions.updateTokenMeta(tokenId, newHash).build_transaction({...})
        # signed = self.web3.eth.account.sign_transaction(tx, self.private_key)
        # tx_hash = self.web3.eth.send_raw_transaction(signed.rawTransaction)
        # receipt = self.web3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)
        # finality_wait(...)
        latency = 0.0  # replace with real (now_s() - t0)
        mem_kb = 0.75
        return latency, mem_kb

    async def teardown(self): return

class SolanaAdapter(Adapter):
    """
    Placeholder for Solana devnet. Implement a metadata update tx and wait for confirmation.
    """
    def __init__(self, chain_name: str, rpc: str):
        super().__init__(chain_name); self.rpc = rpc
        # self.client = AsyncClient(rpc)  # from solana.rpc.async_api import AsyncClient

    async def prepare(self): return

    async def event_update(self) -> Tuple[float, float]:
        t0 = now_s()
        # 1) build instruction (e.g., Metaplex token metadata update)
        # 2) send_transaction
        # 3) confirm_transaction (commitment=finalized)
        latency = 0.0  # replace with real
        mem_kb = 0.75
        return latency, mem_kb

    async def teardown(self): return

# -------- runner --------

async def run_bench(adapter: Adapter, duration_s: int, concurrency: int, events_csv: Path) -> Dict[str, Any]:
    await adapter.prepare()
    latencies, mems = [], []
    in_flight = set()

    async def one_task(task_id: int):
        nonlocal latencies, mems
        while not stop[0]:
            lat, mem_kb = await adapter.event_update()
            latencies.append(lat)
            mems.append(mem_kb)
            # backpressure: ensure one request completed before issuing next (closed loop)
            await asyncio.sleep(0)

    stop = [False]
    start = now_s()

    # spawn workers
    for i in range(concurrency):
        in_flight.add(asyncio.create_task(one_task(i)))

    # run for duration
    try:
        while now_s() - start < duration_s:
            await asyncio.sleep(0.1)
    finally:
        stop[0] = True
        await asyncio.gather(*in_flight, return_exceptions=True)
        await adapter.teardown()

    # compute metrics
    if not latencies:
        raise RuntimeError("No events completed; check adapter implementation.")

    # write per-event CSV (optional, can be large)
    events_csv.parent.mkdir(parents=True, exist_ok=True)
    with events_csv.open("w", newline="") as f:
        w = csv.writer(f); w.writerow(["latency_s", "mem_kb"])
        for L, M in zip(latencies, mems): w.writerow([f"{L:.6f}", f"{M:.3f}"])

    pct = percentiles(latencies)
    summary = {
        **pct,
        "TPS (approx)": closed_loop_tps(concurrency, pct["p50 (s)"]),
        "Mem/update (KB, median)": float(np.median(mems)),
        "Tail idx (p99/p50)": pct["p99 (s)"] / max(pct["p50 (s)"], 1e-9),
        "Total events": len(latencies),
        "Duration (s)": duration_s,
        "Concurrency": concurrency,
    }
    return summary

def write_summary_row(out_csv: Path, chain: str, summary: Dict[str, Any]):
    out_csv.parent.mkdir(parents=True, exist_ok=True)
    header = ["Chain", "p50 (s)", "p75 (s)", "p90 (s)", "p95 (s)", "p99 (s)",
              "TPS (approx)", "Mem/update (KB, median)", "Tail idx (p99/p50)",
              "Total events", "Duration (s)", "Concurrency"]
    exists = out_csv.exists()
    with out_csv.open("a", newline="") as f:
        w = csv.writer(f)
        if not exists: w.writerow(header)
        w.writerow([chain] + [summary[k] for k in header[1:]])

def make_adapter(args) -> Adapter:
    if args.mode == "synthetic":
        return SyntheticAdapter(args.chain)
    if args.mode == "evm":
        return EVMAdapter(args.chain, rpc=args.rpc, private_key=args.private_key)
    if args.mode == "solana":
        return SolanaAdapter(args.chain, rpc=args.rpc)
    raise ValueError(f"Unknown mode: {args.mode}")

def main(argv=None):
    p = argparse.ArgumentParser(description="NFTBench-25")
    p.add_argument("--mode", choices=["synthetic","evm","solana"], required=True)
    p.add_argument("--chain", required=True, help='e.g., "Polygon (Amoy)"')
    p.add_argument("--duration", type=int, default=120, help="seconds")
    p.add_argument("--concurrency", type=int, default=64)
    p.add_argument("--out", default="out", help="output directory")
    # real harness options
    p.add_argument("--rpc", help="RPC endpoint (real modes)")
    p.add_argument("--private-key", dest="private_key", help="EVM private key (dev/test only)")
    p.add_argument("--iface", help="network interface for tc/netem (requires sudo), e.g., eth0")
    p.add_argument("--rtt-ms", type=int, help="target RTT (ms)")
    p.add_argument("--jitter-ms", type=int, help="jitter (ms)")
    p.add_argument("--loss-pct", type=float, help="packet loss percent")
    args = p.parse_args(argv)

    out_dir = Path(args.out)
    summary_csv = out_dir / "summary.csv"
    events_csv  = out_dir / f"events_{args.chain.replace(' ','_').replace('(','').replace(')','')}.csv"

    adapter = make_adapter(args)
    with tc_profile(args.iface, args.rtt_ms, args.jitter_ms, args.loss_pct):
        summary = asyncio.run(run_bench(adapter, args.duration, args.concurrency, events_csv))

    write_summary_row(summary_csv, args.chain, summary)

    print(f"\n=== {args.chain} ===")
    for k, v in summary.items(): print(f"{k:>24}: {v}")
    print(f"\nWrote per-event CSV: {events_csv}")
    print(f"Wrote summary CSV  : {summary_csv}")

if __name__ == "__main__":
    main()
