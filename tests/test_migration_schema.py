from pathlib import Path

MIGRATION = Path("supabase/migrations/20260821150000_identity_and_learning_progress.sql")


def test_canonical_migration_contains_uuid_learning_identity_and_rls():
    sql = MIGRATION.read_text(encoding="utf-8").lower()

    for table in ("profiles", "course_progress", "lesson_progress", "quiz_attempts"):
        assert f"create table if not exists public.{table}" in sql
        assert f"alter table public.{table} enable row level security" in sql
    assert "references auth.users(id)" in sql
    assert "security definer" in sql
    assert "revoke all on schema private" in sql
    assert "auth.uid()" in sql
    assert "supabase_realtime" in sql


def test_migration_never_grants_profile_role_updates_to_learners():
    sql = MIGRATION.read_text(encoding="utf-8").lower()

    assert "revoke update (role, id, email)" in sql
    assert "update (display_name, locale, theme)" in sql
    assert "password_hash" not in sql
