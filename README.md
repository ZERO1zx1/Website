# CodeCraft Academy

CodeCraft Academy бол HTML, CSS, JavaScript болон Python хэлүүдийг анхан шатнаас бодит бүтээгдэхүүн хүртэл алхамчлан сургах зорилготой нээлттэй эх бүхий сургалтын платформ юм.

Энэхүү төсөл нь өмнөх хоёр тусдаа репозиторыг нэгтгэн бүтээгдсэн ба олон хуудаст (multi-page) архитектуртай, CodeCraft брэндийн өнгө төрх бүхий UI/UX дизайнтай, Flask + Supabase технологийн стек дээр суурилсан.

## Онцлог боломжууд

* **Олон хуудаст (Multi-page) Frontend:** `index.html`-д баригдалгүй, нүүр хуудас, хөтөлбөр, хичээл, кодын лаборатори, профайл болон нэвтрэх хэсгүүд тусдаа хуудас болон задарсан.
* **Бүрэн хөтөлбөр:** Python, HTML, CSS, JavaScript хэлүүдийн 57+ хичээл бүхий 4 чиглэлийн модулиудтай.
* **Интерактив кодын лаборатори:** Хичээл дээр үзсэн ойлголтоо шууд хөтөч дээрээ турших боломжтой код бичих талбар (workspace).
* **Баталгаажсан Backend:** Flask-аар дамжуулан хэрэглэгчийн нэвтрэлт, бүртгэл болон мэдээллийг Supabase өгөгдлийн сантай холбож ажилладаг.
* **Google болон Имэйл нэвтрэлт:** Хэрэглэгч Gmail/Google эрхээрээ эсвэл имэйл хаягаар бүртгэл үүсгэж ахицаа хадгалах боломжтой.
* **Аюулгүй байдал (CSP):** Inline script болон гадны хандалтыг зохицуулсан Content-Security-Policy тохируулагдсан.

## Технологийн стек

* **Frontend:** HTML5, CSS3 (Custom properties, CSS Grid/Flexbox), Vanilla JavaScript (ES6+)
* **Backend:** Python 3, Flask
* **Өгөгдлийн сан & Auth:** Supabase (PostgreSQL), Supabase Auth (JWT, Google OAuth)
* **Тохиргоо:** `.env` болон YAML
* **Бусад:** Gunicorn (Production server), Redis (Submission queue - optional)

## Ажиллуулах заавар

Төслийг өөрийн компьютер дээрээ ажиллуулахын тулд дараах алхмуудыг дагана уу.

### 1. Шаардлагатай програмууд
* Python 3.10 буюу түүнээс дээш хувилбар
* Git

### 2. Төслийг татаж авах
```bash
git clone <repository-url>
cd Website
```

### 3. Орчин бэлтгэх
Python виртуал орчин үүсгэж, шаардлагатай сангуудыг суулгах:
```bash
python3 -m venv venv
source venv/bin/activate  # Windows дээр: venv\Scripts\activate
pip install -r requirements.txt
```

### 4. Тохиргооны файл үүсгэх
Төслийн хавтаст байгаа `.env.example` файлыг хуулж `.env` нэртэйгээр үүсгэнэ.
Мөн танд өгөгдсөн бодит тохиргооны `.env` файлыг ашиглаж болно.

```bash
cp .env.example .env
```

`.env` дотор дор хаяж дараах утгууд байх шаардлагатай:
```env
FLASK_ENV=development
FRONTEND_ONLY=false
SECRET_KEY=your-secret-key
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key
```

### 5. Төслийг ажиллуулах
Flask серверийг асаах:
```bash
python3 -m flask --app app:create_app run --host 0.0.0.0 --port 5000
```

Үүний дараа хөтөч дээрээ `http://127.0.0.1:5000` хаягаар орж шалгана уу.

## Төслийн бүтэц

```
Website/
├── app.py                 # Flask application factory болон routes
├── requirements.txt       # Python сангуудын жагсаалт
├── .env                   # Орчны тохиргоо (нууц үг, API түлхүүрүүд)
├── backend/               # Backend логик
│   ├── api/               # API endpoints (auth, courses, problems, гэх мэт)
│   ├── db/                # Supabase өгөгдлийн сантай харилцах хэсэг
│   └── rbac.py            # Role-based access control
├── frontend/              # Frontend хэсэг
│   ├── static/            # CSS болон JavaScript файлууд
│   │   ├── css/style.css  # Үндсэн загвар
│   │   └── js/app.js      # Үндсэн логик
│   └── templates/         # HTML хуудсууд (Jinja2 templates)
│       ├── base.html      # Ерөнхий суурь бүтэц
│       ├── index.html     # Нүүр хуудас
│       ├── curriculum.html# Сургалтын хөтөлбөр
│       ├── course.html    # Хичээлийн дэлгэрэнгүй
│       ├── lesson.html    # Нэг хичээл үзэх хэсэг
│       ├── workspace.html # Кодын лаборатори
│       ├── dashboard.html # Ахицын самбар
│       ├── auth.html      # Нэвтрэх/Бүртгүүлэх
│       └── profile.html   # Хэрэглэгчийн тохиргоо
└── scripts/               # Туслах скриптүүд (Smoke tests)
```

## Хөгжүүлэлт хийх

* **Frontend өөрчлөлт:** `frontend/templates/` доторх HTML болон `frontend/static/` доторх CSS/JS файлуудыг засна.
* **Шинэ хичээл нэмэх:** Одоогоор `app.py` доторх `COURSE_CATALOG` хувьсагчид хадгалагдаж байгаа бөгөөд цаашид YAML эсвэл өгөгдлийн сангаас уншдаг болгох боломжтой.
* **Backend өөрчлөлт:** `backend/api/` доторх Blueprint-үүдийг ашиглан шинэ API нэмнэ.

## Зохиогчийн эрх

© 2026 CodeCraft Academy. Нээлттэй эх бүхий сургалтын платформ.
