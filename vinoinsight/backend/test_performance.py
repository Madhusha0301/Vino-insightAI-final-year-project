"""
Performance / load test for the VinoInsight AI backend (project audit,
'Should-complete' cleanup task: no performance testing existed before this).

This is a standalone script (not part of the pytest suite, since pytest's
Flask test client bypasses the real WSGI server and network stack, which
would make latency numbers meaningless). Run it against a REAL running
instance of the backend:

    cd backend
    python3 app.py &          # start the real server
    python3 test_performance.py

It measures:
  1. Single-request latency for /api/predict (the most expensive endpoint —
     it runs 5 model inferences + SHAP explanation + rule-based
     recommendations per call) over N sequential requests.
  2. Throughput under light concurrency (simulates multiple users hitting
     Predict at roughly the same time, which is the realistic worst case
     for a small deployed demo, not a production load test).

This does not replace a proper load-testing tool (e.g. Locust/k6) for a
production system — it is scoped to what is reasonable to report in an
academic FYP Testing chapter: "does the system respond within an
acceptable time for interactive use, and does it stay stable under a
handful of concurrent users."
"""
import time
import statistics
import concurrent.futures
import requests

BASE = "http://127.0.0.1:5000"

SAMPLE_WINE = {
    "fixed_acidity": 7.4, "volatile_acidity": 0.70, "citric_acid": 0.0,
    "residual_sugar": 1.9, "chlorides": 0.076, "free_sulfur_dioxide": 11.0,
    "total_sulfur_dioxide": 34.0, "density": 0.9978, "ph": 3.51,
    "sulphates": 0.56, "alcohol": 9.4, "is_red": 1,
}


def check_server():
    try:
        r = requests.get(f"{BASE}/api/health", timeout=3)
        return r.status_code == 200
    except Exception:
        return False


def single_request():
    t0 = time.perf_counter()
    r = requests.post(f"{BASE}/api/predict", json=SAMPLE_WINE, timeout=10)
    t1 = time.perf_counter()
    return (t1 - t0) * 1000, r.status_code


def sequential_test(n=30):
    print(f"\n--- Sequential /api/predict latency ({n} requests) ---")
    latencies = []
    for i in range(n):
        ms, status = single_request()
        assert status == 200, f"request {i} failed with status {status}"
        latencies.append(ms)
    latencies.sort()
    print(f"min={min(latencies):.1f}ms  max={max(latencies):.1f}ms  "
          f"mean={statistics.mean(latencies):.1f}ms  "
          f"median={statistics.median(latencies):.1f}ms  "
          f"p95={latencies[int(len(latencies)*0.95)]:.1f}ms")
    return latencies


def concurrency_test(n_workers=10, requests_per_worker=3):
    total = n_workers * requests_per_worker
    print(f"\n--- Concurrent /api/predict test ({n_workers} workers x "
          f"{requests_per_worker} requests = {total} total) ---")
    t0 = time.perf_counter()
    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=n_workers) as ex:
        futures = [ex.submit(single_request) for _ in range(total)]
        for f in concurrent.futures.as_completed(futures):
            results.append(f.result())
    t1 = time.perf_counter()
    statuses = [s for _, s in results]
    latencies = [ms for ms, _ in results]
    success = sum(1 for s in statuses if s == 200)
    wall_time = (t1 - t0) * 1000
    print(f"wall_time={wall_time:.1f}ms  success={success}/{total}  "
          f"mean_latency={statistics.mean(latencies):.1f}ms  "
          f"max_latency={max(latencies):.1f}ms  "
          f"throughput={total / (wall_time / 1000):.1f} req/s")
    return results


if __name__ == "__main__":
    if not check_server():
        print("ERROR: backend is not reachable at "
              f"{BASE}/api/health — start it first with `python3 app.py`.")
        raise SystemExit(1)

    print("VinoInsight AI — Performance Test")
    print("=" * 50)
    seq = sequential_test(n=30)
    conc = concurrency_test(n_workers=10, requests_per_worker=3)

    print("\n--- Summary for report ---")
    print(f"Sequential mean latency: {statistics.mean(seq):.1f}ms per prediction")
    print(f"Concurrent (10 users) success rate: "
          f"{sum(1 for _, s in conc if s == 200)}/{len(conc)}")
