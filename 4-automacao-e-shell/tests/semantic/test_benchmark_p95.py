import pytest
import time
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from semantic_resolver import SemanticResolver

@pytest.fixture
def resolver():
    return SemanticResolver()

def test_p95_resolution_benchmark(resolver):
    # Cache warm-up
    warmup_queries = ["audite", "1", "/destrava-o-git", "reconhecimento", "mapeie"]
    for q in warmup_queries:
        resolver.resolve(q)

    # 1.000 resoluções com amostra variada de comandos
    queries = [
        "audite",
        "faça um reconhecimento",
        "mapeie",
        "1",
        "2",
        "3",
        "porta 3000",
        "audite mas não altere",
        "modo silencioso",
        "reconheça o projeto, audite e depois me mostre os problemas"
    ] * 100

    latencies_ms = []
    for q in queries:
        t0 = time.perf_counter()
        resolver.resolve(q)
        lat = (time.perf_counter() - t0) * 1000
        latencies_ms.append(lat)

    latencies_ms.sort()
    p50 = latencies_ms[int(len(latencies_ms) * 0.50)]
    p95 = latencies_ms[int(len(latencies_ms) * 0.95)]
    p99 = latencies_ms[int(len(latencies_ms) * 0.99)]

    print(f"\n📊 Benchmark Real (1.000 resoluções): P50={p50:.3f}ms, P95={p95:.3f}ms, P99={p99:.3f}ms")
    assert p95 < 50.0, f"P95 excedeu 50ms: {p95:.3f}ms"
