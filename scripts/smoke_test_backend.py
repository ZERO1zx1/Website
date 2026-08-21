import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
os.environ['FRONTEND_ONLY'] = 'false'
from app import create_app

app = create_app()
client = app.test_client()
checks = [
    ('/api/health', client.get('/api/health'), 200),
    ('/api/ready', client.get('/api/ready'), (200, 503)),
    ('/api/auth/register invalid', client.post('/api/auth/register', json={'email': 'bad'}), 400),
    ('/api/auth/google/start', client.get('/api/auth/google/start'), (200, 503)),
]
for label, response, expected in checks:
    allowed = expected if isinstance(expected, tuple) else (expected,)
    print(label, response.status_code, response.content_type)
    if response.status_code not in allowed:
        print(response.data.decode('utf-8', errors='replace')[:500])
        raise SystemExit(1)
print('BACKEND_SMOKE_OK')
