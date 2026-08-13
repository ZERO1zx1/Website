# Backend audit checkpoint

**Execution mode:** AgentCore-style incremental execution
**Repository:** `ZERO1zx1/Website`
**Current branch:** `feat/frontend-redesign`

## Completed foundation

The repository now separates backend code under `backend/`, with Flask API blueprints in `backend/api/`, services in `backend/services/`, the Supabase gateway in `backend/db.py`, and frontend adapters under `frontend/static/js/adapters/`. The frontend can still run under `FRONTEND_ONLY=true`, while normal mode registers the backend blueprints.

## Audit findings

| Priority | Finding | Impact | Planned response |
|---|---|---|---|
| P0 | Login compares stored password directly with submitted password | Credential compromise risk | Replace with a password hashing/verifier boundary; never return or log password data |
| P0 | `SECRET_KEY` falls back to a development value | JWT forgery risk if deployed incorrectly | Fail fast in normal production mode; use explicit environment configuration |
| P1 | CORS allows all origins | Cross-origin abuse risk | Make origins YAML/environment controlled and deny wildcard in production |
| P1 | RBAC has student/teacher/admin but no website owner role | Owner cannot control platform-level operations | Add `owner` as the highest platform role and explicit permission matrix |
| P1 | `role_required()` accepts only one exact role | Reuse is limited and owner/admin hierarchy is unclear | Add permission-based decorator with role-to-permission mapping |
| P1 | Student can be changed to teacher before admin approval | A pending teacher can receive teacher role semantics too early | Keep requested role and effective role separate; only approved teacher receives teacher permissions |
| P1 | Pending teacher endpoint returns a placeholder list | Admin panel cannot operate real approvals | Add database query method and normalized response |
| P1 | Supabase client is eagerly initialized at module import | Tests and CLI tooling fail without credentials | Introduce lazy/configured database gateway with clear backend-only failure |
| P2 | API errors are mostly English-only and unstructured | Frontend cannot provide consistent bilingual feedback | Add stable error codes, English message and Mongolian message fields |
| P2 | Teacher dashboard has placeholder aggregates | Panel cannot show useful class analytics | Add service-level aggregation contract before wiring UI |
| P2 | CORS, app settings and Docker limits are split across code | Deployment drift | Centralize settings and provide YAML/Markdown runbook |

## Execution units

**P0:** secure password and secret handling; preserve frontend-only preview.
**P1:** owner role, permission matrix, approval workflow, pending teacher query, settings boundary.
**P2:** bilingual errors, dashboard service contracts, Docker/YAML runbook and expanded regression tests.

## Important terminology

`role = үүрэг`; `permission = зөвшөөрөл`; `owner = эзэмшигч`; `admin = администратор`; `teacher = багш`; `student = суралцагч`; `dashboard = хяналтын самбар`; `teacher panel = багшийн самбар`; `approval = баталгаажуулалт`; `request = хүсэлт`; `submission = илгээлт`; `course = сургалт`; `lesson = хичээл`; `problem = бодлого`; `mastery = эзэмшил`.

## Resume point

The next atomic unit is to create the role/permission specification and bilingual glossary before changing the authentication and authorization code. This avoids inconsistent names across Flask responses, frontend labels, Markdown documentation and future YAML configuration.

## Implementation checkpoint

The role/permission specification is now stored in `docs/role-permission-spec.md`, with machine-readable configuration in `config/roles.yml`. The backend has a central `backend/rbac.py` loader, bilingual error response contract, owner role, permission grants, and scoped permission matching.

Authentication now uses password hashes through Werkzeug, rejects weak passwords, does not accept client-supplied roles during registration, keeps teacher requests pending until approval, and exposes owner-only role management. Supabase initialization is lazy so credential-free module imports and frontend-only tests remain possible.

The backend foundation also includes `Dockerfile`, `docker-compose.yml`, `config/app.yml`, PyYAML dependency, explicit CORS origins, production SECRET_KEY fail-fast behavior, student dashboard endpoint, and owner/admin/teacher-aware teacher dashboard endpoints.

Validation checkpoint: 9 tests passed; YAML files parse; JavaScript syntax and Python compile passed; owner and dashboard routes registered under normal backend mode with test credentials. Docker Compose validation was skipped because the sandbox does not have the Docker CLI installed.

## Security validation checkpoint

The authentication schema migration is prepared at `backend/db/migrations/001_auth_roles.sql`. It adds password hash and teacher approval fields, constrains supported roles, and explicitly requires password reset for legacy plaintext-password accounts.

The latest regression run passed **15 tests** across app configuration, authentication security, RBAC, frontend shell and code executor. JavaScript syntax, Python compilation and diff checks also passed. Docker Compose YAML parses successfully; actual Docker validation remains blocked only because the sandbox does not include the Docker CLI.
