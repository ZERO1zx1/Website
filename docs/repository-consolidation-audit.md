# Repository consolidation audit

`Website` is the canonical CodeCraft Academy repository. It retains the Flask
application factory, Jinja multi-page frontend, RBAC, courses, problems,
submissions, Docker sandbox, and Redis worker. `Code_Craft_Academy` remains a
reference repository; its FastAPI server and SPA router are not imported.

| Source | Destination | Reason | Risk | Verification |
|---|---|---|---|---|
| Website Flask/Jinja | canonical runtime | complete product surface | route regression | template/API smoke tests |
| Code_Craft profile/progress/quiz | Flask + Supabase migration | UUID learner persistence | direct-role escalation | RLS negative tests |
| Code_Craft Realtime patterns | user-owned progress tables | cross-device state | publication drift | migration re-run test |
| Website bigint users schema | `auth.users.id` UUID identity | single auth source | existing-data cutover | migration/backfill audit |
| Website sandbox/Redis | hardened retained subsystem | isolated execution | unavailable dependency | degraded-mode tests |
| Code_Craft FastAPI/SPA | not ported | one backend/frontend source | duplicate runtime | repository scan |

The pre-consolidation schema did not create `public.users` on a clean project,
used bigint identity, and had no RLS for Website public tables. The Code_Craft
profile update policy must not be copied because it permits a user to mutate
their own role through the Data API. Canonical migrations use explicit grants,
RLS ownership predicates, UUID foreign keys, and server-only role management.

Before deployment: take a database backup, reconcile legacy users to Supabase
Auth UUIDs, run clean/re-run migration tests, verify RLS under authenticated
and service roles, and keep execute endpoints disabled when sandbox/Redis is
unhealthy. Roll back code via the previous image/commit; do not disable RLS as
a rollback shortcut.
