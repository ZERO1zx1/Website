import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
os.environ['FRONTEND_ONLY'] = 'true'
os.environ['FLASK_ENV'] = 'development'
from app import create_app

app = create_app()
client = app.test_client()
paths = ['/', '/curriculum', '/course?id=python', '/lesson?course=python&lesson=py-list', '/workspace', '/dashboard', '/profile', '/auth', '/api/health', '/api/public-config']
for path in paths:
    response = client.get(path)
    print(path, response.status_code, response.content_type, len(response.data))
    if response.status_code >= 400:
        print(response.data.decode('utf-8', errors='replace')[:500])
        raise SystemExit(1)
print('FRONTEND_SMOKE_OK')
