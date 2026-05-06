from src.core import metrics


def test_metrics_objects_exposed():
    # Smoke test to ensure metric objects exist and can be used.
    metrics.ACTIVE_REQUESTS.inc()
    metrics.ACTIVE_REQUESTS.dec()

    metrics.REQUESTS.labels(method="GET", endpoint="/health", status=200).inc()
    metrics.REQUESTS_LATENCY.labels(method="GET", endpoint="/health").observe(0.01)

