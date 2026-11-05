"""Writes a synthetic hourly Yahoo-shaped chart (random walk) for the tests."""
import json, random, sys

def make(path, n=900, start_ts=1760000000 - 1760000000 % 3600, seed=3, p0=100000.0):
    rng = random.Random(seed)
    ts, o, h, l, c, v = [], [], [], [], [], []
    px = p0
    for i in range(n):
        ret = rng.gauss(0.0001, 0.004)
        op, cl = px, px * (1 + ret)
        hi = max(op, cl) * (1 + abs(rng.gauss(0, 0.0015)))
        lo = min(op, cl) * (1 - abs(rng.gauss(0, 0.0015)))
        ts.append(start_ts + 3600 * i); o.append(op); h.append(hi); l.append(lo); c.append(cl); v.append(rng.uniform(100, 500))
        px = cl
    doc = {"chart": {"result": [{"timestamp": ts, "indicators": {"quote": [{"open": o, "high": h, "low": l, "close": c, "volume": v}]}}]}}
    with open(path, "w") as fh:
        json.dump(doc, fh)
    return ts

if __name__ == "__main__":
    make(sys.argv[1])
