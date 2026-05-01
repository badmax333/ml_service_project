from prometheus_client import Counter, Histogram, Gauge

# HTTP метрики
REQUESTS = Counter('http_requests_total', 'Total HTTP requests', ['method', 'endpoint', 'status'])
REQUESTS_LATENCY = Histogram('http_request_duration_seconds', 'HTTP request latency', ['method', 'endpoint'])
ACTIVE_REQUESTS = Gauge('http_requests_active', 'Active HTTP requests')

# Бизнес метрики
USERS_TOTAL = Gauge('users_total', 'Total number of registered users')
TRANSCRIPTIONS_TOTAL = Counter('transcriptions_total', 'Total transcriptions', ['model_size', 'status'])
CREDITS_SPENT = Counter('credits_spent_total', 'Total credits spent')