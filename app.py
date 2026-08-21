"""
Programming Learning Intelligence Platform
Flask Application Factory
"""

import os
from flask import Flask, render_template, request
from flask_cors import CORS
from flask_login import LoginManager
from dotenv import load_dotenv


class FlaskSessionUser:
    """Minimal Flask-Login user wrapper for the JWT-backed database record."""

    def __init__(self, record):
        self.record = record
        self.id = record.get('id')
        self.name = record.get('name')
        self.email = record.get('email')
        self.role = record.get('role', 'student')

    @property
    def is_authenticated(self):
        return True

    @property
    def is_active(self):
        return True

    @property
    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.id)

# Load environment variables
load_dotenv()

COURSE_CATALOG = {
    'python': {
        'id': 'python', 'title': 'Python foundations', 'icon': 'Py', 'color': 'purple',
        'eyebrow': 'Програмчлалын сэтгэлгээ', 'duration': '6 долоо хоног', 'level': 'Анхан шат',
        'description': 'Код хэрхэн ажилладгийг ойлгож, логик сэтгэлгээ болон асуудал задлах сууриа тавина.',
        'modules': [
            {'title': '01 · Эхлэл', 'summary': 'Орчин, өгөгдөл, гаралт', 'lessons': [
                {'id': 'py-start', 'title': 'Python гэж юу вэ?', 'outcome': 'Код, програм, interpreter-ийн ялгааг ойлгоно.', 'task': 'print() ашиглан анхны програмаа ажиллуул.', 'minutes': 20, 'language': 'python', 'code': "name = 'CodeCraft'\\nprint(f'Сайн уу, {name}!')"},
                {'id': 'py-values', 'title': 'Хувьсагч ба өгөгдлийн төрөл', 'outcome': 'string, integer, float, boolean утгыг зөв сонгоно.', 'task': 'Өөрийн танилцуулга хадгалах 4 хувьсагч үүсгэ.', 'minutes': 20, 'language': 'python', 'code': "name = 'Суралцагч'\\nage = 18\\nis_ready = True\\nprint(name, age, is_ready)"},
                {'id': 'py-input', 'title': 'Оролт, гаралт', 'outcome': 'input, print болон type conversion ашиглана.', 'task': 'Нас асуугаад дараа жилийн насыг хэвлэ.', 'minutes': 20, 'language': 'python', 'code': "age = int(input('Насаа оруул: '))\\nprint(age + 1)"}
            ]},
            {'title': '02 · Логик', 'summary': 'Нөхцөл, давталт, алдаа', 'lessons': [
                {'id': 'py-if', 'title': 'Нөхцөл шалгах', 'outcome': 'if, elif, else ашиглан шийдвэр гаргана.', 'task': 'Оноог үсгэн үнэлгээнд хөрвүүл.', 'minutes': 20, 'language': 'python', 'code': "score = 86\\nif score >= 80:\\n    print('A')\\nelse:\\n    print('Keep going')"},
                {'id': 'py-loop', 'title': 'for ба while', 'outcome': 'Давтагдах ажлыг богино бичнэ.', 'task': '1–100 хоорондох тэгш тооны нийлбэрийг ол.', 'minutes': 20, 'language': 'python', 'code': "total = 0\\nfor number in range(2, 101, 2):\\n    total += number\\nprint(total)"},
                {'id': 'py-debug', 'title': 'Алдаа уншиж засах', 'outcome': 'Syntax, runtime, logic алдааг ялгана.', 'task': 'Эвдэрхий тооны машинд 3 алдаа ол.', 'minutes': 20, 'language': 'python', 'code': "value = 10\\nprint(value / 2)"}
            ]},
            {'title': '03 · Өгөгдөл', 'summary': 'List, dictionary, function', 'lessons': [
                {'id': 'py-list', 'title': 'List ба collection', 'outcome': 'Олон утгыг хадгалж, шүүж, эрэмбэлнэ.', 'task': 'Хичээлийн онооны дундаж бод.', 'minutes': 20, 'language': 'python', 'code': "scores = [80, 92, 75, 88]\\naverage = sum(scores) / len(scores)\\nprint(round(average, 1))"},
                {'id': 'py-dict', 'title': 'Dictionary', 'outcome': 'key/value өгөгдлийг загварчилна.', 'task': 'Сурагчийн profile dictionary үүсгэ.', 'minutes': 20, 'language': 'python', 'code': "student = {'name': 'Nara', 'track': 'Frontend'}\\nprint(student['track'])"},
                {'id': 'py-function', 'title': 'Function', 'outcome': 'Параметр, return ашиглан кодоо хэсэгчлэнэ.', 'task': 'Хөнгөлөлт боддог function бич.', 'minutes': 20, 'language': 'python', 'code': "def discounted(price, percent):\\n    return price * (1 - percent / 100)\\nprint(discounted(100, 10))"}
            ]},
            {'title': '04 · Мини төсөл', 'summary': 'CLI бүтээгдэхүүн', 'lessons': [
                {'id': 'py-files', 'title': 'Файлтай ажиллах', 'outcome': 'Текст өгөгдөл уншиж, хадгална.', 'task': 'Тэмдэглэлээ файлд хадгал.', 'minutes': 20, 'language': 'python', 'code': "notes = ['read', 'practice']\\nwith open('notes.txt', 'w') as file:\\n    file.write('\\n'.join(notes))"},
                {'id': 'py-project', 'title': 'Төсөл: Task tracker', 'outcome': 'Бүх ойлголтоо нэг урсгалд нэгтгэнэ.', 'task': 'Нэмэх, харах, дуусгах CLI app бүтээ.', 'minutes': 25, 'language': 'python', 'code': "tasks = []\\ntasks.append('Build a project')\\nprint(tasks)"},
                {'id': 'py-review', 'title': 'Шалгалт ба рефактор', 'outcome': 'Кодоо уншигдахуйц болгож edge case шалгана.', 'task': 'Төслөө function-уудаар хуваа.', 'minutes': 20, 'language': 'python', 'code': "def clean_title(title):\\n    return title.strip().title()\\nprint(clean_title('  codecraft  '))"}
            ]}
        ]
    },
    'html': {'id': 'html', 'title': 'HTML essentials', 'icon': '<>', 'color': 'orange', 'eyebrow': 'Вэбийн утга ба бүтэц', 'duration': '4 долоо хоног', 'level': 'Анхан шат', 'description': 'Хүртээмжтэй, хайлтын системд ойлгомжтой веб хуудсыг зөв бүтцээр байгуулна.', 'modules': [{'title': '01 · Вэбийн суурь', 'summary': 'Browser ба document', 'lessons': [{'id': 'html-web', 'title': 'Вэб хэрхэн ажилладаг вэ?', 'outcome': 'Browser, server, URL, request-ийн үүргийг ойлгоно.', 'task': 'Нэг web request-ийн урсгалыг зур.', 'minutes': 18, 'language': 'html', 'code': '<main>\\n  <h1>Миний анхны вэб</h1>\\n  <p>Semantic HTML ашиглаж байна.</p>\\n</main>'}, {'id': 'html-doc', 'title': 'HTML document', 'outcome': 'doctype, head, body, metadata-г зөв бичнэ.', 'task': 'Стандарт хангасан page үүсгэ.', 'minutes': 18, 'language': 'html', 'code': '<!doctype html>\\n<html lang="mn">\\n  <head><title>CodeCraft</title></head>\\n</html>'}, {'id': 'html-text', 'title': 'Текст ба холбоос', 'outcome': 'Heading, paragraph, list, link ашиглана.', 'task': 'Хувийн танилцуулга хий.', 'minutes': 18, 'language': 'html', 'code': '<h1>Намайг танилцуулъя</h1>\\n<p>Би frontend сурч байна.</p>'}]}, {'title': '02 · Semantic HTML', 'summary': 'Утгатай бүтэц', 'lessons': [{'id': 'html-semantic', 'title': 'Page landmark', 'outcome': 'header, nav, main, section, footer сонгоно.', 'task': 'Div page-ийг semantic болго.', 'minutes': 18, 'language': 'html', 'code': '<header>Logo</header>\\n<main><section>Content</section></main>'}, {'id': 'html-media', 'title': 'Зураг ба медиа', 'outcome': 'Responsive image, figure, alt ашиглана.', 'task': 'Тайлбартай gallery хий.', 'minutes': 18, 'language': 'html', 'code': '<figure>\\n  <img src="project.png" alt="Төслийн дэлгэц" />\\n  <figcaption>Миний төсөл</figcaption>\\n</figure>'}, {'id': 'html-table', 'title': 'Хүснэгт', 'outcome': 'caption, scope бүхий table байгуулна.', 'task': '7 хоногийн хуваарь хий.', 'minutes': 18, 'language': 'html', 'code': '<table>\\n  <caption>Суралцах хуваарь</caption>\\n  <tr><th scope="col">Өдөр</th></tr>\\n</table>'}]}, {'title': '03 · Form ба accessibility', 'summary': 'Оролт, keyboard, screen reader', 'lessons': [{'id': 'html-form', 'title': 'Form-ийн үндэс', 'outcome': 'label, input, textarea, button холбоно.', 'task': 'Бүртгэлийн form үүсгэ.', 'minutes': 18, 'language': 'html', 'code': '<label for="email">Имэйл</label>\\n<input id="email" type="email" required />'}, {'id': 'html-validation', 'title': 'Browser validation', 'outcome': 'Input type, required, constraint ашиглана.', 'task': 'Алдааны төлөвүүдийг шалга.', 'minutes': 18, 'language': 'html', 'code': '<input type="password" minlength="8" required />'}, {'id': 'html-a11y', 'title': 'Accessibility', 'outcome': 'Keyboard ба accessible name шалгана.', 'task': 'Mouse-гүйгээр page-аа турш.', 'minutes': 18, 'language': 'html', 'code': '<button aria-label="Цэс нээх">☰</button>'}]}, {'title': '04 · Төсөл', 'summary': 'Portfolio бүтэц', 'lessons': [{'id': 'html-plan', 'title': 'Контент төлөвлөх', 'outcome': 'Wireframe-ийг outline болгоно.', 'task': 'Landing page heading map гарга.', 'minutes': 20, 'language': 'html', 'code': '<main>\\n  <h1>Portfolio</h1>\\n  <section><h2>Work</h2></section>\\n</main>'}, {'id': 'html-build', 'title': 'Төсөл: Portfolio', 'outcome': 'Бодит portfolio-ийн контентыг тэмдэглэнэ.', 'task': 'Hero, work, about, contact хий.', 'minutes': 25, 'language': 'html', 'code': '<section class="hero"><h1>Би бүтээдэг.</h1></section>'}, {'id': 'html-audit', 'title': 'HTML аудит', 'outcome': 'Semantic ба accessibility алдааг засна.', 'task': 'Checklist-ээр төслөө шалга.', 'minutes': 20, 'language': 'html', 'code': '<a href="/work" aria-label="Ажлууд харах">Work</a>'}]}]}
}
for _course in COURSE_CATALOG.values():
    _course['lesson_count'] = sum(len(module['lessons']) for module in _course['modules'])
    _course['first_lesson'] = _course['modules'][0]['lessons'][0]['id']


def create_app(config_name='development'):
    """Application factory function"""
    app = Flask(
        __name__,
        template_folder='frontend/templates',
        static_folder='frontend/static',
    )
    
    # Configuration
    environment = os.getenv('FLASK_ENV', config_name or 'development').lower()
    secret_key = os.getenv('SECRET_KEY')
    if environment == 'production' and not secret_key:
        raise RuntimeError('SECRET_KEY must be set when FLASK_ENV=production')
    app.config['ENVIRONMENT'] = environment
    app.config['SECRET_KEY'] = secret_key or 'dev-secret-key-change-in-production'
    app.config['JSON_SORT_KEYS'] = False
    app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True
    app.config['MAX_CONTENT_LENGTH'] = int(os.getenv('MAX_CONTENT_LENGTH', 256 * 1024))
    frontend_only = os.getenv('FRONTEND_ONLY', 'false').lower() == 'true'
    app.config['FRONTEND_ONLY'] = frontend_only
    
    # CORS is explicit and environment-controlled; wildcard is not used by default.
    cors_origins = [
        origin.strip()
        for origin in os.getenv('CORS_ORIGINS', 'http://localhost:5000,http://127.0.0.1:5000').split(',')
        if origin.strip()
    ]
    app.config['CORS_ORIGINS'] = cors_origins
    CORS(app, resources={
        r"/api/*": {
            "origins": cors_origins,
            "methods": ["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization", "Accept-Language"]
        }
    })
    
    if not frontend_only:
        # Initialize Flask-Login and register backend blueprints only when
        # backend credentials are intentionally available.
        login_manager = LoginManager()
        login_manager.init_app(app)
        login_manager.login_view = 'auth.login'

        from backend.db import db

        @login_manager.user_loader
        def load_user(user_id):
            try:
                record = db.get_user(int(user_id))
            except Exception:
                return None
            return FlaskSessionUser(record) if record else None

        from backend.api.auth import auth_bp
        from backend.api.courses import courses_bp
        from backend.api.problems import problems_bp
        from backend.api.submissions import submissions_bp
        from backend.api.teacher import teacher_bp
        from backend.api.analytics import analytics_bp

        app.register_blueprint(auth_bp, url_prefix='/api/auth')
        app.register_blueprint(courses_bp, url_prefix='/api/courses')
        app.register_blueprint(problems_bp, url_prefix='/api/problems')
        app.register_blueprint(submissions_bp, url_prefix='/api/submissions')
        app.register_blueprint(teacher_bp, url_prefix='/api/teacher')
        app.register_blueprint(analytics_bp, url_prefix='/api/analytics')
    
    # Multi-page CodeCraft frontend. Each learning surface has a dedicated template.
    @app.context_processor
    def inject_frontend_context():
        return {'backend_enabled': not frontend_only}

    @app.route('/', methods=['GET'])
    def frontend_shell():
        return render_template('index.html', page='home', backend_enabled=not frontend_only)

    @app.route('/<page>', methods=['GET'])
    def frontend_page(page):
        allowed = {'home', 'dashboard', 'curriculum', 'course', 'lesson', 'workspace', 'auth', 'profile'}
        if page not in allowed:
            return {'error': 'Not found'}, 404
        if page == 'home':
            return render_template('index.html', page='home', backend_enabled=not frontend_only)
        if page == 'course':
            course = COURSE_CATALOG.get(request.args.get('id', 'python'), COURSE_CATALOG['python'])
            return render_template('course.html', page='course', course=course, backend_enabled=not frontend_only)
        if page == 'lesson':
            course = COURSE_CATALOG.get(request.args.get('course', 'python'), COURSE_CATALOG['python'])
            lesson_id = request.args.get('lesson', course['first_lesson'])
            lesson = next((item for module in course['modules'] for item in module['lessons'] if item['id'] == lesson_id), course['modules'][0]['lessons'][0])
            lesson = dict(lesson)
            lesson['unit'] = next((module['title'] for module in course['modules'] if any(item['id'] == lesson['id'] for item in module['lessons'])), 'Module')
            return render_template('lesson.html', page='lesson', course=course, lesson=lesson, backend_enabled=not frontend_only)
        if page == 'workspace':
            starters = {'python': "name = 'CodeCraft'\\nfor step in range(1, 4):\\n    print(f'{step}. Сайн уу, {name}!')", 'html': '<main>\\n  <h1>Миний анхны вэб</h1>\\n  <p>Semantic HTML ашиглаж байна.</p>\\n</main>', 'css': ':root {\\n  --brand: #6d5dfc;\\n}\\n.card {\\n  padding: 24px;\\n  border-radius: 18px;\\n  background: var(--brand);\\n}', 'javascript': "const button = document.querySelector('button');\\nlet count = 0;\\nbutton?.addEventListener('click', () => {\\n  count += 1;\\n  button.textContent = `Даралт: ${count}`;\\n});"}
            return render_template('workspace.html', page='workspace', starters=starters, backend_enabled=not frontend_only)
        return render_template(f'{page}.html', page=page, backend_enabled=not frontend_only)

    @app.route('/api/public-config', methods=['GET'])
    def public_config():
        return {'supabase_url': os.getenv('SUPABASE_URL', ''), 'supabase_publishable_key': os.getenv('SUPABASE_KEY', '')}, 200

    # Health check endpoint
    @app.route('/api/health', methods=['GET'])
    def health_check():
        return {'status': 'healthy', 'version': '1.0.0'}, 200

    @app.route('/api/ready', methods=['GET'])
    def readiness_check():
        if frontend_only:
            return {'status': 'ready', 'mode': 'frontend-only'}, 200
        required = ['SECRET_KEY', 'SUPABASE_URL', 'SUPABASE_KEY']
        queue_mode = os.getenv('SUBMISSION_QUEUE_MODE', 'thread').lower()
        if queue_mode == 'redis':
            required.append('REDIS_URL')
        if os.getenv('SANDBOX_URL'):
            required.append('SANDBOX_TOKEN')
        missing = [name for name in required if not os.getenv(name)]
        if missing:
            return {'status': 'not_ready', 'missing': missing}, 503
        return {'status': 'ready', 'mode': 'backend'}, 200
    
    @app.after_request
    def add_security_headers(response):
        response.headers.setdefault('X-Content-Type-Options', 'nosniff')
        response.headers.setdefault('X-Frame-Options', 'SAMEORIGIN')
        response.headers.setdefault('Referrer-Policy', 'strict-origin-when-cross-origin')
        response.headers.setdefault('Permissions-Policy', 'camera=(), microphone=(), geolocation=()')
        response.headers.setdefault('Content-Security-Policy', "default-src 'self'; connect-src 'self' https://*.supabase.co; font-src 'self' https://fonts.gstatic.com; img-src 'self' data:; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; frame-ancestors 'self'; base-uri 'self'; form-action 'self'")
        if request.is_secure:
            response.headers.setdefault('Strict-Transport-Security', 'max-age=31536000; includeSubDomains')
        return response

    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return {'error': 'Not found'}, 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return {'error': 'Internal server error'}, 500
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(
        host=os.getenv('HOST', '0.0.0.0'),
        port=int(os.getenv('PORT', 5000)),
        debug=os.getenv('FLASK_DEBUG', 'false').lower() == 'true'
    )
