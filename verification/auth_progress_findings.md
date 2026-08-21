# Auth & Progress Verification Findings — 2026-08-21

## Confirmed working locally

- The Flask application started in full backend mode on `http://127.0.0.1:5004`.
- `/api/ready` returns `200` with `mode: backend`.
- The updated `/auth?mode=register` UI renders email/password registration, consent, and a Google button.
- `/api/auth/google/start` returns a Supabase-hosted OAuth authorization URL.
- `/api/progress` correctly returns `401` if a bearer token is absent.
- The CodeCraft-owned Supabase tables `profiles`, `course_progress`, and `lesson_progress` exist with RLS enabled.

## Current configuration blocker

- The Supabase Auth settings endpoint is reachable, but it reports that the Google provider is not enabled.
- The Supabase dashboard is open at the Sign In / Providers page for project `rqalizeohjpwtvepltqe`.
- Enabling Google requires a valid Google OAuth Client ID and Client Secret from the project owner. No credentials were fabricated or stored.

## Required owner action for a complete live Google sign-in test

1. Enable the Google provider in Supabase Dashboard → Authentication → Sign In / Providers.
2. Enter the Google OAuth Client ID and Client Secret.
3. In Google Cloud Console, add the Supabase callback URL shown in the provider configuration.
4. Add local redirect URLs such as `http://127.0.0.1:5004/auth?confirmed=1` and `http://127.0.0.1:5004/api/auth/google/callback` in Supabase URL Configuration as appropriate.
5. Re-run `scripts/verify_auth_progress.py` after the provider is enabled.

## Backend API Validation

- The RLS-scoped `/api/progress` endpoints were successfully verified using mock tests.
- Supabase token validation correctly provisions the user profile and attaches the token to the context.
- Progress updates are routed through `user_client(access_token)` ensuring Row Level Security policies are respected.
- The `profiles`, `course_progress`, and `lesson_progress` tables are correctly configured with RLS in the database.
