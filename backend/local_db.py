"""SQLite persistence used for local development when Supabase is not configured.

This is a real backend database, not a frontend fixture. Production deployments
continue to use Supabase; local development uses a file-backed SQLite database
so registration, login, courses, problems, dashboard data, and submissions are
persisted across requests and restarts.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
import hashlib
import json
import secrets
import os
from pathlib import Path
import sqlite3
from typing import Any

from werkzeug.security import generate_password_hash


class LocalResponse:
    def __init__(self, data=None):
        self.data = data or []


class LocalQuery:
    def __init__(self, database: "LocalDB", table: str, operation: str = "select"):
        self.database = database
        self.table_name = table
        self.operation = operation
        self.columns = "*"
        self.payload = None
        self.filters: list[tuple[str, Any]] = []
        self.ordering: tuple[str, bool] | None = None
        self.range_values: tuple[int, int] | None = None
        self.limit_value: int | None = None

    def select(self, columns="*"):
        self.operation = "select"
        self.columns = columns
        return self

    def insert(self, payload):
        self.operation = "insert"
        self.payload = payload
        return self

    def update(self, payload):
        self.operation = "update"
        self.payload = payload
        return self

    def delete(self):
        self.operation = "delete"
        return self

    def upsert(self, payload):
        self.operation = "upsert"
        self.payload = payload
        return self

    def eq(self, column, value):
        self.filters.append((column, value))
        return self

    def order(self, column, desc=False):
        self.ordering = (column, bool(desc))
        return self

    def range(self, start, end):
        self.range_values = (int(start), int(end))
        return self

    def limit(self, value):
        self.limit_value = int(value)
        return self

    def execute(self):
        if self.operation == "select":
            return LocalResponse(self._select())
        if self.operation == "insert":
            return LocalResponse(self._insert())
        if self.operation == "update":
            return LocalResponse(self._update())
        if self.operation == "delete":
            return LocalResponse(self._delete())
        if self.operation == "upsert":
            return LocalResponse(self._upsert())
        raise ValueError(f"Unsupported local query operation: {self.operation}")

    def _where(self):
        if not self.filters:
            return "", []
        return " WHERE " + " AND ".join(f'"{column}" = ?' for column, _ in self.filters), [value for _, value in self.filters]

    def _select(self):
        where, params = self._where()
        columns = self.columns.strip()
        join_problem = self.table_name == "submissions" and "problems(" in columns
        if join_problem:
            sql_columns = "submissions.*"
            qualified_where = ""
            if self.filters:
                qualified_where = " WHERE " + " AND ".join(f'submissions."{column}" = ?' for column, _ in self.filters)
            sql = f"SELECT {sql_columns} FROM submissions LEFT JOIN problems ON problems.id = submissions.problem_id{qualified_where}"
        else:
            sql = f"SELECT {columns if columns != '*' else '*'} FROM \"{self.table_name}\"{where}"
        if self.ordering:
            column, desc = self.ordering
            sql += f' ORDER BY "{column}" {"DESC" if desc else "ASC"}'
        if self.limit_value is not None:
            sql += f" LIMIT {self.limit_value}"
        if self.range_values:
            start, end = self.range_values
            sql += f" LIMIT {max(0, end - start + 1)} OFFSET {max(0, start)}"
        rows = [dict(row) for row in self.database.connection().execute(sql, params).fetchall()]
        if join_problem:
            for row in rows:
                problem = self.database.connection().execute(
                    "SELECT title, difficulty FROM problems WHERE id = ?", (row.get("problem_id"),)
                ).fetchone()
                row["problems"] = dict(problem) if problem else {}
        return rows

    def _insert(self):
        records = self.payload if isinstance(self.payload, list) else [self.payload]
        inserted = []
        connection = self.database.connection()
        for record in records:
            record = dict(record)
            columns = list(record)
            values = [json.dumps(record[column]) if self.table_name == "exam_questions" and column == "options" and not isinstance(record[column], str) else record[column] for column in columns]
            placeholders = ", ".join("?" for _ in columns)
            quoted = ", ".join(f'"{column}"' for column in columns)
            cursor = connection.execute(
                f'INSERT INTO "{self.table_name}" ({quoted}) VALUES ({placeholders})', values
            )
            row = connection.execute(
                f'SELECT * FROM "{self.table_name}" WHERE id = ?', (cursor.lastrowid,)
            ).fetchone() if self.database.has_id_column(self.table_name) else None
            inserted.append(dict(row) if row else record)
        connection.commit()
        return inserted

    def _update(self):
        where, params = self._where()
        record = dict(self.payload or {})
        if not record:
            return self._select()
        assignments = ", ".join(f'"{column}" = ?' for column in record)
        values = list(record.values()) + params
        connection = self.database.connection()
        connection.execute(f'UPDATE "{self.table_name}" SET {assignments}{where}', values)
        connection.commit()
        return self._select()

    def _delete(self):
        where, params = self._where()
        connection = self.database.connection()
        connection.execute(f'DELETE FROM "{self.table_name}"{where}', params)
        connection.commit()
        return []

    def _upsert(self):
        record = dict(self.payload or {})
        conflict_columns = {
            "mastery_snapshots": ("user_id", "skill_id"),
            "problem_skills": ("problem_id", "skill_id"),
            "lesson_progress": ("user_id", "lesson_id"),
            "exam_answers": ("attempt_id", "question_id"),
        }.get(self.table_name)
        connection = self.database.connection()
        if conflict_columns and all(column in record for column in conflict_columns):
            existing = connection.execute(
                f'SELECT id FROM "{self.table_name}" WHERE ' + " AND ".join(f'"{column}" = ?' for column in conflict_columns),
                [record[column] for column in conflict_columns],
            ).fetchone()
            if existing:
                self.filters = [("id", existing["id"])]
                return self._update_payload(record)
        return self._insert_payload(record)

    def _insert_payload(self, record):
        self.payload = record
        return self._insert()

    def _update_payload(self, record):
        self.payload = record
        return self._update()


class LocalClient:
    def __init__(self, database: "LocalDB"):
        self.database = database

    def table(self, name):
        return LocalQuery(self.database, name)


class LocalDB:
    def __init__(self, path: str | None = None):
        default_path = Path(__file__).resolve().parents[1] / "instance" / "codehaven.sqlite3"
        self.path = Path(path or os.getenv("LOCAL_DB_PATH", str(default_path)))
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._initialized = False
        self.client = LocalClient(self)
        self._ensure_schema()

    def connection(self):
        connection = sqlite3.connect(self.path, timeout=10)
        connection.row_factory = sqlite3.Row
        return connection

    def has_id_column(self, table):
        return table not in {"problem_skills"}

    def _ensure_schema(self):
        if self._initialized:
            return
        connection = self.connection()
        connection.executescript(
            """
            PRAGMA foreign_keys = ON;
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT NOT NULL UNIQUE,
                name TEXT NOT NULL,
                password_hash TEXT,
                role TEXT NOT NULL DEFAULT 'student',
                requested_role TEXT,
                teacher_approval_status TEXT NOT NULL DEFAULT 'approved',
                auth_user_id TEXT UNIQUE,
                auth_provider TEXT,
                avatar_url TEXT,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );
            CREATE TABLE IF NOT EXISTS password_reset_tokens (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                token_hash TEXT NOT NULL UNIQUE,
                expires_at TEXT NOT NULL,
                used_at TEXT,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );
            CREATE TABLE IF NOT EXISTS courses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL UNIQUE,
                description TEXT NOT NULL DEFAULT '',
                created_by INTEGER,
                is_published INTEGER NOT NULL DEFAULT 1,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );
            CREATE TABLE IF NOT EXISTS modules (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                course_id INTEGER NOT NULL REFERENCES courses(id) ON DELETE CASCADE,
                title TEXT NOT NULL,
                description TEXT NOT NULL DEFAULT '',
                position INTEGER NOT NULL DEFAULT 1,
                status TEXT NOT NULL DEFAULT 'published',
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(course_id, position)
            );
            CREATE TABLE IF NOT EXISTS lessons (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                module_id INTEGER NOT NULL REFERENCES modules(id) ON DELETE CASCADE,
                title TEXT NOT NULL,
                content TEXT NOT NULL DEFAULT '',
                position INTEGER NOT NULL DEFAULT 1,
                estimated_minutes INTEGER NOT NULL DEFAULT 15,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(module_id, position)
            );
            CREATE TABLE IF NOT EXISTS classes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                course_id INTEGER NOT NULL REFERENCES courses(id) ON DELETE CASCADE,
                teacher_id INTEGER NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
                name TEXT NOT NULL,
                enrollment_code TEXT NOT NULL UNIQUE,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );
            CREATE TABLE IF NOT EXISTS enrollments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                class_id INTEGER NOT NULL REFERENCES classes(id) ON DELETE CASCADE,
                user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                enrollment_role TEXT NOT NULL DEFAULT 'student',
                joined_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(class_id, user_id)
            );
            CREATE TABLE IF NOT EXISTS skills (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                description TEXT NOT NULL DEFAULT '',
                category TEXT,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );
            CREATE TABLE IF NOT EXISTS problems (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL UNIQUE,
                description TEXT NOT NULL DEFAULT '',
                difficulty TEXT NOT NULL,
                starter_code TEXT NOT NULL DEFAULT '',
                explanation TEXT NOT NULL DEFAULT '',
                language TEXT NOT NULL DEFAULT 'python',
                created_by INTEGER,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );
            CREATE TABLE IF NOT EXISTS test_cases (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                problem_id INTEGER NOT NULL REFERENCES problems(id) ON DELETE CASCADE,
                input TEXT NOT NULL DEFAULT '',
                expected_output TEXT NOT NULL DEFAULT '',
                is_hidden INTEGER NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(problem_id, input, expected_output, is_hidden)
            );
            CREATE TABLE IF NOT EXISTS hints (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                problem_id INTEGER NOT NULL REFERENCES problems(id) ON DELETE CASCADE,
                level INTEGER NOT NULL,
                content TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(problem_id, level)
            );
            CREATE TABLE IF NOT EXISTS problem_versions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                problem_id INTEGER NOT NULL REFERENCES problems(id) ON DELETE CASCADE,
                version_number INTEGER NOT NULL,
                content_hash TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(problem_id, version_number)
            );
            CREATE TABLE IF NOT EXISTS problem_skills (
                problem_id INTEGER NOT NULL REFERENCES problems(id) ON DELETE CASCADE,
                skill_id INTEGER NOT NULL REFERENCES skills(id) ON DELETE CASCADE,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY(problem_id, skill_id)
            );
            CREATE TABLE IF NOT EXISTS exams (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                class_id INTEGER REFERENCES classes(id) ON DELETE CASCADE,
                title TEXT NOT NULL,
                description TEXT NOT NULL DEFAULT '',
                duration_minutes INTEGER NOT NULL DEFAULT 20,
                max_attempts INTEGER NOT NULL DEFAULT 3,
                starts_at TEXT,
                ends_at TEXT,
                status TEXT NOT NULL DEFAULT 'published',
                created_by INTEGER REFERENCES users(id) ON DELETE SET NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );
            CREATE TABLE IF NOT EXISTS exam_questions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                exam_id INTEGER NOT NULL REFERENCES exams(id) ON DELETE CASCADE,
                problem_id INTEGER REFERENCES problems(id) ON DELETE SET NULL,
                position INTEGER NOT NULL DEFAULT 1,
                question_type TEXT NOT NULL DEFAULT 'multiple_choice',
                prompt TEXT NOT NULL,
                options TEXT NOT NULL DEFAULT '[]',
                correct_answer TEXT,
                points REAL NOT NULL DEFAULT 1,
                explanation TEXT NOT NULL DEFAULT '',
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(exam_id, position)
            );
            CREATE TABLE IF NOT EXISTS exam_attempts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                exam_id INTEGER NOT NULL REFERENCES exams(id) ON DELETE CASCADE,
                user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                status TEXT NOT NULL DEFAULT 'in_progress',
                score REAL NOT NULL DEFAULT 0,
                earned_points REAL NOT NULL DEFAULT 0,
                total_points REAL NOT NULL DEFAULT 0,
                started_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                submitted_at TEXT,
                graded_at TEXT
            );
            CREATE TABLE IF NOT EXISTS exam_answers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                attempt_id INTEGER NOT NULL REFERENCES exam_attempts(id) ON DELETE CASCADE,
                question_id INTEGER NOT NULL REFERENCES exam_questions(id) ON DELETE CASCADE,
                answer TEXT NOT NULL DEFAULT '',
                is_correct INTEGER,
                earned_points REAL NOT NULL DEFAULT 0,
                feedback TEXT NOT NULL DEFAULT '',
                updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(attempt_id, question_id)
            );
            CREATE TABLE IF NOT EXISTS submissions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                problem_id INTEGER NOT NULL REFERENCES problems(id) ON DELETE RESTRICT,
                assignment_id INTEGER,
                exam_id INTEGER,
                code TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'pending',
                score REAL NOT NULL DEFAULT 0,
                evaluated_at TEXT,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );
            CREATE TABLE IF NOT EXISTS submission_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                submission_id INTEGER NOT NULL REFERENCES submissions(id) ON DELETE CASCADE,
                test_number INTEGER NOT NULL,
                status TEXT NOT NULL DEFAULT 'pending',
                passed INTEGER NOT NULL DEFAULT 0,
                actual_output TEXT,
                expected_output TEXT,
                error TEXT,
                is_hidden INTEGER NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(submission_id, test_number)
            );
            CREATE TABLE IF NOT EXISTS mastery_snapshots (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                skill_id INTEGER NOT NULL REFERENCES skills(id) ON DELETE CASCADE,
                mastery_score REAL NOT NULL DEFAULT 0,
                first_attempt_success_rate REAL,
                retry_recovery_rate REAL,
                hint_usage_count INTEGER NOT NULL DEFAULT 0,
                updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(user_id, skill_id)
            );
            CREATE TABLE IF NOT EXISTS lesson_progress (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                lesson_id INTEGER NOT NULL REFERENCES lessons(id) ON DELETE CASCADE,
                status TEXT NOT NULL DEFAULT 'in_progress',
                started_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                completed_at TEXT,
                UNIQUE(user_id, lesson_id)
            );
            CREATE TABLE IF NOT EXISTS teacher_feedback (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                submission_id INTEGER NOT NULL REFERENCES submissions(id) ON DELETE CASCADE,
                teacher_id INTEGER NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
                feedback TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );
            """
        )
        columns = {row[1] for row in connection.execute("PRAGMA table_info(lesson_progress)").fetchall()}
        if 'status' not in columns:
            connection.execute("ALTER TABLE lesson_progress ADD COLUMN status TEXT NOT NULL DEFAULT 'completed'")
        if 'started_at' not in columns:
            connection.execute("ALTER TABLE lesson_progress ADD COLUMN started_at TEXT")
            connection.execute("UPDATE lesson_progress SET started_at = COALESCE(completed_at, CURRENT_TIMESTAMP)")
        # Older local databases were created before test_cases had a unique
        # constraint. Remove duplicate seed rows before creating the index so
        # restarts remain deterministic without touching distinct user data.
        connection.execute(
            """
            DELETE FROM test_cases
            WHERE id NOT IN (
                SELECT MIN(id)
                FROM test_cases
                GROUP BY problem_id, input, expected_output, is_hidden
            )
            """
        )
        connection.execute(
            """
            CREATE UNIQUE INDEX IF NOT EXISTS test_cases_unique_case_idx
            ON test_cases (problem_id, input, expected_output, is_hidden)
            """
        )
        # The original local seed used INSERT OR IGNORE without a uniqueness
        # constraint on exams, so every app restart could create an empty copy.
        # Keep the canonical seeded exam (the first one with questions), move
        # any existing attempts to it, and remove only empty seed duplicates.
        seed_exam_rows = connection.execute(
            """
            SELECT e.id,
                   (SELECT COUNT(*) FROM exam_questions q WHERE q.exam_id = e.id) AS question_count
            FROM exams e
            WHERE e.title = 'Python foundations checkpoint' AND e.created_by IS NULL
            ORDER BY e.id
            """
        ).fetchall()
        canonical_exam = next((row for row in seed_exam_rows if row['question_count'] > 0), None)
        if canonical_exam is None and seed_exam_rows:
            canonical_exam = seed_exam_rows[0]
        if canonical_exam:
            for row in seed_exam_rows:
                if row['id'] == canonical_exam['id'] or row['question_count'] > 0:
                    continue
                connection.execute(
                    "UPDATE exam_attempts SET exam_id = ? WHERE exam_id = ?",
                    (canonical_exam['id'], row['id']),
                )
                connection.execute("DELETE FROM exams WHERE id = ?", (row['id'],))
        connection.execute(
            """
            CREATE UNIQUE INDEX IF NOT EXISTS exams_seed_title_idx
            ON exams (title)
            WHERE created_by IS NULL
            """
        )
        connection.commit()
        self._seed(connection)
        connection.close()
        self._initialized = True

    def _seed(self, connection):
        now = datetime.now(timezone.utc).isoformat()
        courses = [
            ("Python foundations", "Learn Python syntax, data structures, functions and practical problem solving."),
            ("HTML & CSS responsive web", "Build semantic, accessible and responsive pages with modern HTML and CSS."),
            ("Flask backend services", "Build secure APIs, authentication, roles, databases, and production-ready Flask services."),
        ]
        for title, description in courses:
            connection.execute("INSERT OR IGNORE INTO courses (title, description) VALUES (?, ?)", (title, description))
        course_ids = {row["title"]: row["id"] for row in connection.execute("SELECT id, title FROM courses")}
        modules = [
            (course_ids["Python foundations"], "Python essentials", "Variables, types and control flow.", 1),
            (course_ids["Python foundations"], "Functions and clean code", "Scope, arguments and reusable patterns.", 2),
            (course_ids["HTML & CSS responsive web"], "Semantic HTML", "Use meaningful landmarks, headings and labels.", 1),
            (course_ids["Flask backend services"], "Flask API foundations", "Routes, blueprints, validation and JSON responses.", 1),
            (course_ids["Flask backend services"], "Auth and data services", "JWT, role permissions and persistent data.", 2),
        ]
        for course_id, title, description, position in modules:
            connection.execute(
                "INSERT OR IGNORE INTO modules (course_id, title, description, position) VALUES (?, ?, ?, ?)",
                (course_id, title, description, position),
            )
        module_ids = {row["title"]: row["id"] for row in connection.execute("SELECT id, title FROM modules")}
        lessons = [
            (module_ids["Python essentials"], "Variables and control flow", "Learn the core building blocks of Python programs.", 1),
            (module_ids["Functions and clean code"], "List comprehensions", "Write concise transformations while preserving clarity.", 1),
            (module_ids["Semantic HTML"], "Accessible page structure", "Use landmarks, headings, labels and meaningful content.", 1),
            (module_ids["Flask API foundations"], "Routes and JSON contracts", "Build predictable API endpoints with validation.", 1),
        ]
        for module_id, title, content, position in lessons:
            connection.execute(
                "INSERT OR IGNORE INTO lessons (module_id, title, content, position, estimated_minutes) VALUES (?, ?, ?, ?, 20)",
                (module_id, title, content, position),
            )
        for name, description, category in [
            ("Python", "Python programming fundamentals.", "programming"),
            ("Problem solving", "Reasoning and algorithmic decomposition.", "programming"),
            ("Web fundamentals", "Semantic HTML and responsive CSS.", "frontend"),
            ("Flask APIs", "Secure backend services and REST APIs.", "backend"),
        ]:
            connection.execute("INSERT OR IGNORE INTO skills (name, description, category) VALUES (?, ?, ?)", (name, description, category))
        problems = [
            ("Even number filter", "Return only the even numbers from a list while keeping the original order.", "easy", 'import json\nimport sys\n\ndef even_numbers(values):\n    return [value for value in values if value % 2 == 0]\n\nvalues = json.loads(sys.stdin.read() or "[]")\nprint(even_numbers(values))', "python"),
            ("First unique character", "Find the first character that occurs exactly once in a string.", "medium", "def first_unique(value):\n    return None", "python"),
            ("Build a JSON response", "Return a predictable JSON object with a status and message.", "easy", "def build_response(message):\n    return {}", "python"),
        ]
        for title, description, difficulty, starter_code, language in problems:
            connection.execute(
                "INSERT OR IGNORE INTO problems (title, description, difficulty, starter_code, language) VALUES (?, ?, ?, ?, ?)",
                (title, description, difficulty, starter_code, language),
            )
        problem_ids = {row["title"]: row["id"] for row in connection.execute("SELECT id, title FROM problems")}
        # Keep the built-in learning problem executable after upgrades to the
        # local seed while leaving teacher-authored problems untouched.
        connection.execute(
            "UPDATE problems SET starter_code = ? WHERE title = ? AND (starter_code IS NULL OR starter_code LIKE 'def even_numbers%')",
            (problems[0][3], "Even number filter"),
        )
        even_problem_id = problem_ids["Even number filter"]
        connection.execute(
            """
            DELETE FROM test_cases
            WHERE problem_id = ?
              AND expected_output = '[]'
              AND id NOT IN (
                  SELECT MIN(id) FROM test_cases
                  WHERE problem_id = ? AND expected_output = '[]'
              )
            """,
            (even_problem_id, even_problem_id),
        )
        connection.execute(
            "UPDATE test_cases SET input = ? WHERE problem_id = ? AND expected_output = ?",
            ("[1, 2, 3, 4]", even_problem_id, "[2, 4]"),
        )
        connection.execute(
            "UPDATE test_cases SET input = ? WHERE problem_id = ? AND expected_output = ?",
            ("[]", even_problem_id, "[]"),
        )
        test_cases = [
            (problem_ids["Even number filter"], "[1, 2, 3, 4]", "[2, 4]", 0),
            (problem_ids["Even number filter"], "[]", "[]", 1),
            (problem_ids["First unique character"], "", "a", 0),
            (problem_ids["Build a JSON response"], "", "{\"status\": \"ok\"}", 0),
        ]
        for problem_id, input_data, expected_output, is_hidden in test_cases:
            connection.execute(
                "INSERT OR IGNORE INTO test_cases (problem_id, input, expected_output, is_hidden) VALUES (?, ?, ?, ?)",
                (problem_id, input_data, expected_output, is_hidden),
            )
        connection.execute(
            "INSERT OR IGNORE INTO exams (title, description, duration_minutes, max_attempts, status) VALUES (?, ?, ?, ?, ?)",
            ("Python foundations checkpoint", "A short checkpoint covering variables, functions, and practical problem solving.", 20, 3, "published"),
        )
        exam = connection.execute("SELECT id FROM exams WHERE title = ?", ("Python foundations checkpoint",)).fetchone()
        if exam:
            exam_id = exam["id"]
            exam_questions = [
                (exam_id, 1, "multiple_choice", "Which value is immutable in Python?", json.dumps(["list", "dictionary", "tuple", "set"]), "tuple", 1, "Tuples cannot be changed after creation."),
                (exam_id, 2, "multiple_choice", "What does a function return when it has no return statement?", json.dumps(["0", "False", "None", "An error"]), "None", 1, "Python functions return None by default."),
                (exam_id, 3, "short_answer", "Write the name of the built-in function used to get the length of a sequence.", json.dumps([]), "len", 1, "The len() function returns the number of items."),
            ]
            for question in exam_questions:
                connection.execute(
                    "INSERT OR IGNORE INTO exam_questions (exam_id, position, question_type, prompt, options, correct_answer, points, explanation) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                    question,
                )
        skills = {row["name"]: row["id"] for row in connection.execute("SELECT id, name FROM skills")}
        for problem_title, skill_name in [("Even number filter", "Python"), ("First unique character", "Problem solving"), ("Build a JSON response", "Flask APIs")]:
            connection.execute(
                "INSERT OR IGNORE INTO problem_skills (problem_id, skill_id) VALUES (?, ?)",
                (problem_ids[problem_title], skills[skill_name]),
            )
        connection.commit()


def _local_request_password_reset(self, email: str):
    normalized = str(email or '').strip().lower()
    user = next(iter(self.client.table('users').select('*').eq('email', normalized).execute().data), None)
    if not user:
        return None
    token = secrets.token_urlsafe(32)
    token_hash = hashlib.sha256(token.encode('utf-8')).hexdigest()
    expires_at = (datetime.now(timezone.utc) + timedelta(minutes=30)).isoformat()
    connection = self.connection()
    connection.execute('DELETE FROM password_reset_tokens WHERE user_id = ? AND used_at IS NULL', (user['id'],))
    connection.execute('INSERT INTO password_reset_tokens (user_id, token_hash, expires_at) VALUES (?, ?, ?)', (user['id'], token_hash, expires_at))
    connection.commit()
    return token


def _local_consume_password_reset(self, token: str, password_hash: str):
    token_hash = hashlib.sha256(str(token or '').encode('utf-8')).hexdigest()
    connection = self.connection()
    row = connection.execute('SELECT id, user_id, expires_at, used_at FROM password_reset_tokens WHERE token_hash = ?', (token_hash,)).fetchone()
    if not row or row['used_at']:
        return None
    expires_at = datetime.fromisoformat(row['expires_at'])
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)
    if expires_at <= datetime.now(timezone.utc):
        return None
    connection.execute('UPDATE users SET password_hash = ? WHERE id = ?', (password_hash, row['user_id']))
    connection.execute('UPDATE password_reset_tokens SET used_at = ? WHERE id = ?', (datetime.now(timezone.utc).isoformat(), row['id']))
    connection.commit()
    return _record(connection.execute('SELECT * FROM users WHERE id = ?', (row['user_id'],)).fetchone())


def _record(row):
    return dict(row) if row else None


# Convenience methods used by the Flask APIs and evaluator.
def _method(name, query):
    setattr(LocalDB, name, query)


LocalDB.request_password_reset = _local_request_password_reset
LocalDB.consume_password_reset = _local_consume_password_reset
LocalDB.create_user = lambda self, email, password, name, role="student": _record(self.client.table("users").insert({"email": email, "name": name, "password_hash": generate_password_hash(password), "role": role, "requested_role": None, "teacher_approval_status": "approved"}).execute().data[0])
LocalDB.get_user = lambda self, user_id: _record(self.client.table("users").select("*").eq("id", user_id).execute().data[0] if self.client.table("users").select("*").eq("id", user_id).execute().data else None)
LocalDB.get_user_by_email = lambda self, email: next(iter(self.client.table("users").select("*").eq("email", email).execute().data), None)
LocalDB.get_user_by_auth_id = lambda self, auth_user_id: next(iter(self.client.table("users").select("*").eq("auth_user_id", auth_user_id).execute().data), None)
LocalDB.update_user = lambda self, user_id, data: next(iter(self.client.table("users").update(data).eq("id", user_id).execute().data), None)
LocalDB.get_pending_teacher_requests = lambda self: self.client.table("users").select("*").eq("requested_role", "teacher").eq("teacher_approval_status", "pending").execute().data
LocalDB.create_course = lambda self, title, description, created_by: next(iter(self.client.table("courses").insert({"title": title, "description": description, "created_by": created_by}).execute().data), None)
LocalDB.get_courses = lambda self, limit=100, offset=0: self.client.table("courses").select("*").range(offset, offset + limit - 1).execute().data
LocalDB.get_course = lambda self, course_id: self._course(course_id)
LocalDB.create_class = lambda self, course_id, teacher_id, name, enrollment_code: next(iter(self.client.table("classes").insert({"course_id": course_id, "teacher_id": teacher_id, "name": name, "enrollment_code": enrollment_code}).execute().data), None)
LocalDB.get_class = lambda self, class_id: next(iter(self.client.table("classes").select("*").eq("id", class_id).execute().data), None)
LocalDB.get_teacher_classes = lambda self, teacher_id: self.client.table("classes").select("*").eq("teacher_id", teacher_id).execute().data
LocalDB.get_all_classes = lambda self: self.client.table("classes").select("*").execute().data
LocalDB.create_problem = lambda self, title, description, difficulty, starter_code, created_by, language="python": next(iter(self.client.table("problems").insert({"title": title, "description": description, "difficulty": difficulty, "starter_code": starter_code, "created_by": created_by, "language": language}).execute().data), None)
LocalDB.get_problem = lambda self, problem_id: next(iter(self.client.table("problems").select("*").eq("id", problem_id).execute().data), None)
LocalDB.get_problems = lambda self, limit=100, offset=0: self.client.table("problems").select("*").range(offset, offset + limit - 1).execute().data
LocalDB.create_submission = lambda self, user_id, problem_id, code, assignment_id=None, exam_id=None: next(iter(self.client.table("submissions").insert({"user_id": user_id, "problem_id": problem_id, "code": code, "assignment_id": assignment_id, "exam_id": exam_id, "status": "pending"}).execute().data), None)
LocalDB.get_submission = lambda self, submission_id: next(iter(self.client.table("submissions").select("*").eq("id", submission_id).execute().data), None)
LocalDB.get_user_submissions = lambda self, user_id, limit=5: self.client.table("submissions").select("*, problems(title, difficulty)").eq("user_id", user_id).order("created_at", desc=True).limit(limit).execute().data
LocalDB.update_submission_status = lambda self, submission_id, status, score=None: next(iter(self.client.table("submissions").update({"status": status, **({"score": score} if score is not None else {})}).eq("id", submission_id).execute().data), None)
LocalDB.create_test_case = lambda self, problem_id, input_data, expected_output, is_hidden=False: next(iter(self.client.table("test_cases").insert({"problem_id": problem_id, "input": input_data, "expected_output": expected_output, "is_hidden": int(is_hidden)}).execute().data), None)
LocalDB.get_test_cases = lambda self, problem_id, include_hidden=False: (self.client.table("test_cases").select("*").eq("problem_id", problem_id).execute().data if include_hidden else self.client.table("test_cases").select("*").eq("problem_id", problem_id).eq("is_hidden", 0).execute().data)
LocalDB.create_skill = lambda self, name, description, category=None: next(iter(self.client.table("skills").insert({"name": name, "description": description, "category": category}).execute().data), None)
LocalDB.get_skills = lambda self: self.client.table("skills").select("*").execute().data
LocalDB.get_user_mastery = lambda self, user_id, skill_id=None: (self.client.table("mastery_snapshots").select("*").eq("user_id", user_id).eq("skill_id", skill_id).execute().data if skill_id else self.client.table("mastery_snapshots").select("*").eq("user_id", user_id).execute().data)
LocalDB.start_lesson = lambda self, user_id, lesson_id: next(iter(self.client.table("lesson_progress").upsert({"user_id": user_id, "lesson_id": lesson_id, "status": "in_progress"}).execute().data), None)
LocalDB.complete_lesson = lambda self, user_id, lesson_id: next(iter(self.client.table("lesson_progress").upsert({"user_id": user_id, "lesson_id": lesson_id, "status": "completed", "completed_at": datetime.now(timezone.utc).isoformat()}).execute().data), None)
LocalDB.get_user_lesson_progress = lambda self, user_id: self.client.table("lesson_progress").select("*").eq("user_id", user_id).execute().data
LocalDB.update_mastery = lambda self, user_id, skill_id, mastery_score, first_attempt_success_rate=None, retry_recovery_rate=None, hint_usage_count=None: next(iter(self.client.table("mastery_snapshots").upsert({"user_id": user_id, "skill_id": skill_id, "mastery_score": mastery_score, **({"first_attempt_success_rate": first_attempt_success_rate} if first_attempt_success_rate is not None else {}), **({"retry_recovery_rate": retry_recovery_rate} if retry_recovery_rate is not None else {}), **({"hint_usage_count": hint_usage_count} if hint_usage_count is not None else {})}).execute().data), None)


def _course(self, course_id):
    course = next(iter(self.client.table("courses").select("*").eq("id", course_id).execute().data), None)
    if not course:
        return None
    modules = self.client.table("modules").select("*").eq("course_id", course_id).order("position").execute().data
    for module in modules:
        module["lessons"] = self.client.table("lessons").select("*").eq("module_id", module["id"]).order("position").execute().data
    course["modules"] = modules
    return course


LocalDB._course = _course
