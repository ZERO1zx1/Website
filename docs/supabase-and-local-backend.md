# Supabase Auth and Local Backend Runbook

This runbook explains how to configure **Email/OTP**, **password recovery**, and **Google sign-in** for Codehaven, then run and test the complete Flask backend locally. Codehaven has two supported modes: credential-free local development with SQLite, and production backend mode with Supabase/PostgreSQL.

> **Important:** Local SQLite mode deliberately supports email/password registration, login, local password reset, learning progress, dashboard data, courses, problems, and submissions. Email OTP and Google OAuth require Supabase Auth because they depend on an external identity or email provider.

## 1. Project environment contract

The application uses the following environment values. Keep real credentials outside Git and never commit `.env`.

| Variable | Local SQLite value | Supabase/production value |
|---|---|---|
| `FLASK_ENV` | `development` | `production` |
| `FRONTEND_ONLY` | `false` | `false` |
| `SECRET_KEY` | Long random development secret | Long random production secret |
| `LOCAL_DB` | `true` | `false` or unset |
| `LOCAL_DB_PATH` | `instance/codehaven.sqlite3` | Not used |
| `SUPABASE_URL` | Unset | `https://<project-ref>.supabase.co` |
| `SUPABASE_KEY` | Unset | Server-side Supabase key from the project settings |
| `FRONTEND_URL` | `http://127.0.0.1:5059` | Public HTTPS application URL |
| `OTP_REDIRECT_URL` | `http://127.0.0.1:5059/` | Public HTTPS callback/landing URL |
| `GOOGLE_OAUTH_REDIRECT_URL` | `http://127.0.0.1:5059/api/auth/google/callback` | Public HTTPS `/api/auth/google/callback` URL |
| `SUBMISSION_QUEUE_MODE` | `thread` | `redis` for the Compose worker stack |
| `REDIS_URL` | Unset for thread mode | `redis://redis:6379/0` or managed Redis URL |
| `SANDBOX_URL` | Unset for local visible-test fallback | Internal sandbox URL |
| `SANDBOX_TOKEN` | Unset unless sandbox is enabled | Strong shared sandbox token |

Supabase Auth uses an allow-list for redirect URLs. The URL passed as `redirectTo` must be included in that allow-list, and the Site URL is the default destination when no explicit redirect is supplied.[1]

## 2. Supabase database setup

Create or select a Supabase project, then apply the migrations in numeric order from the repository:

```text
backend/db/migrations/001_auth_roles.sql
backend/db/migrations/002_learning_platform.sql
backend/db/migrations/003_external_auth_identities.sql
backend/db/migrations/004_learning_progress.sql
```

After the migrations, optionally apply the starter content seed:

```text
backend/db/seed/001_demo_content.sql
```

The seed creates courses, modules, lessons, skills, problems, and test cases. It does **not** create a fake learner account. Every learner must register through the real auth flow.

In Supabase project settings, copy the project URL and the server-side key into the deployment secret store. Do not place the service role key in browser JavaScript or expose it through a public environment variable.

## 3. Configure Email/password and Email OTP

Open the Supabase Dashboard and go to **Authentication → Providers → Email**. Enable email/password authentication. Decide whether email confirmation is required for production accounts; do not disable confirmation as a workaround for delivery failures.

For development exploration, Supabase's built-in email service can be used only for pre-authorized team addresses and has strict rate limits. It is not a production delivery service. For production, configure a custom SMTP provider such as Resend, AWS SES, Postmark, SendGrid, ZeptoMail, or Brevo in **Authentication → SMTP Settings**.[2]

Use a dedicated authentication sender such as `no-reply@auth.example.com`. Configure the sender domain's SPF, DKIM, and DMARC records with the email provider so confirmation, OTP, and recovery messages are deliverable.[2]

For Codehaven Email OTP:

1. Enable the Email provider.
2. Configure custom SMTP for production.
3. Add the exact OTP redirect URL to **Authentication → URL Configuration → Redirect URLs**.
4. In the email OTP template, make sure the six-digit token placeholder `{{ .Token }}` is rendered in the message.
5. Set `OTP_REDIRECT_URL` to the URL where the application should return after the OTP flow.
6. Test `POST /api/auth/otp/request`, then submit the six-digit code to `POST /api/auth/otp/verify`.

If the application reports **“The email code could not be sent”**, first check SMTP credentials, sender verification, provider rate limits, the recipient allow-list in the default Supabase mailer, and the redirect allow-list. Local SQLite mode intentionally returns a clear message telling the user to use email/password instead.

For password recovery:

1. Add the password reset page URL to the redirect allow-list.
2. Keep the Supabase recovery email template linked to the configured redirect URL. When using a custom `redirectTo`, Supabase documents replacing `{{ .SiteURL }}` with `{{ .RedirectTo }}` in relevant templates.[1]
3. In local SQLite mode, Codehaven creates a short-lived, one-time local reset token and shows a local reset URL.
4. In Supabase mode, Supabase Auth owns email delivery and the recovery session. The production email provider must therefore be configured before expecting a recovery email.

## 4. Configure Google sign-in

### 4.1 Create a Google OAuth web client

Open the [Google Auth Platform console](https://console.cloud.google.com/auth/overview) and create or select a Google Cloud project. Configure the OAuth consent screen branding and the minimum scopes required by Supabase: `openid`, profile, and email.[3]

Create an OAuth client under **Google Auth Platform → Clients → Create client → Web application**. Configure:

| Google field | Local value | Production value |
|---|---|---|
| Authorized JavaScript origins | `http://127.0.0.1:5059`, `http://localhost:5059` | `https://your-domain.example` |
| Authorized redirect URI | `https://<project-ref>.supabase.co/auth/v1/callback` | `https://<project-ref>.supabase.co/auth/v1/callback` |

The Supabase project-specific callback URI is available on the Supabase **Authentication → Providers → Google** page. Google sends the provider response to Supabase first; Supabase then redirects to Codehaven's application callback.

### 4.2 Enable the provider in Supabase

Open **Supabase Dashboard → Authentication → Providers → Google**, enable Google, and paste the Google client ID and client secret. Then add the application callback URL to Supabase **Authentication → URL Configuration → Redirect URLs**:

```text
http://127.0.0.1:5059/api/auth/google/callback
http://localhost:5059/api/auth/google/callback
https://your-domain.example/api/auth/google/callback
```

Set the corresponding application environment variable:

```env
GOOGLE_OAUTH_REDIRECT_URL=http://127.0.0.1:5059/api/auth/google/callback
```

For production, replace the local URL with the public HTTPS URL. The Codehaven flow is:

```text
Login/Register page
  → GET /api/auth/google/start
  → Supabase Auth
  → Google consent screen
  → Supabase callback
  → Codehaven /api/auth/google/callback
  → Codehaven app JWT
  → /dashboard
```

If the UI reports **“Google sign-in is not configured yet”**, verify that Google is enabled in Supabase, the client ID/secret are correct, the Google callback URI is exact, the Supabase redirect allow-list contains the application callback, and `GOOGLE_OAUTH_REDIRECT_URL` matches the deployed host.

## 5. Complete local backend setup

From a clean checkout:

```bash
git clone https://github.com/ZERO1zx1/Website.git
cd Website
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m pip install pytest pip-audit
```

Start credential-free local backend mode. This uses real SQLite persistence and does not require Supabase:

```bash
export PYTHONPATH=.
export FLASK_ENV=development
export FRONTEND_ONLY=false
export LOCAL_DB=true
export LOCAL_DB_PATH="$PWD/instance/codehaven.sqlite3"
export SECRET_KEY='replace-with-a-long-local-secret'
export READINESS_PROBE=true
python -m flask --app 'app:create_app()' run --host 0.0.0.0 --port 5059
```

Open the application pages:

```text
http://127.0.0.1:5059/home
http://127.0.0.1:5059/login
http://127.0.0.1:5059/register
http://127.0.0.1:5059/password-reset
http://127.0.0.1:5059/dashboard
http://127.0.0.1:5059/
```

Check service health in a second terminal:

```bash
curl http://127.0.0.1:5059/api/health
curl http://127.0.0.1:5059/api/ready
```

Register a real local learner and verify the backend token:

```bash
curl -X POST http://127.0.0.1:5059/api/auth/register \
  -H 'Content-Type: application/json' \
  -d '{"name":"Local Learner","email":"local@example.com","password":"password123"}'
```

Use the returned token to test current user, dashboard, and course APIs:

```bash
export TOKEN='paste-the-returned-token'
curl http://127.0.0.1:5059/api/auth/me -H "Authorization: Bearer $TOKEN"
curl http://127.0.0.1:5059/api/analytics/dashboard -H "Authorization: Bearer $TOKEN"
curl http://127.0.0.1:5059/api/courses -H "Authorization: Bearer $TOKEN"
```

Test the local password reset flow:

```bash
curl -X POST http://127.0.0.1:5059/api/auth/password-reset/request \
  -H 'Content-Type: application/json' \
  -d '{"email":"local@example.com"}'
```

Open the returned `reset_url`, set a new password, then verify that the new password can log in. The local token is hashed in SQLite, expires after 30 minutes, and can be consumed only once.

## 6. Run the full project checks

The repository's canonical local CI command is:

```bash
bash ci/check.sh
pip-audit -r requirements.txt --progress-spinner off
```

This covers Python compilation, all tests, JavaScript syntax, frontend structure, workflow contract, Compose topology, repository hygiene, and dependency vulnerabilities. The current backend regression suite covers registration, password hashing, JWT login, role isolation, dashboard metrics, lesson completion, reset tokens, and provider endpoint contracts.

## 7. Optional full Docker Compose backend

Use the Compose stack only when Docker, Redis, Supabase, and the sandbox are configured:

```bash
cp .env.example .env
# Edit .env with strong SECRET_KEY, SUPABASE_URL, SUPABASE_KEY,
# SANDBOX_TOKEN, SANDBOX_URL, REDIS_URL, and production callback URLs.
docker compose config
docker compose up --build
```

The Compose stack runs `web`, `worker`, `redis`, and `sandbox`. Redis and sandbox remain internal-only. The web service handles HTTP/API requests, the worker consumes Redis submissions, and the sandbox runs isolated code. Do not publish Redis or sandbox ports to the public network.

## References

[1]: https://supabase.com/docs/guides/auth/redirect-urls "Supabase Redirect URLs"
[2]: https://supabase.com/docs/guides/auth/auth-smtp "Supabase Custom SMTP"
[3]: https://supabase.com/docs/guides/auth/social-login/auth-google "Supabase Login with Google"
