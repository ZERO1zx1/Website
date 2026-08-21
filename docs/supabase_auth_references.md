# Supabase Auth and RLS Implementation Notes

## Official sources consulted

1. [Supabase — Login with Google](https://supabase.com/docs/guides/auth/social-login/auth-google)
   - Google OAuth needs a Web application client in Google Cloud.
   - Configure application origin such as `http://127.0.0.1:5000` for local development.
   - Add the Supabase project callback URL shown in the Google provider section as the authorized redirect URI in Google Cloud.
   - Add the application callback URL to the Supabase Auth redirect allow list.
   - Configure the Google client ID and secret on the Supabase Dashboard provider page; do not store the Google client secret in this Flask repository.

2. [Supabase — Password-based Auth](https://supabase.com/docs/guides/auth/passwords)
   - Hosted Supabase projects use email confirmation by default.
   - Password signup can supply an email redirect URL; that URL must be permitted in the Supabase redirect allow list.
   - The Flask server should use Supabase Auth signup/sign-in methods rather than write password hashes to a custom public table.

3. [Supabase — User Management](https://supabase.com/docs/guides/auth/managing-user-data)
   - Application profile data should live in `public` tables, reference `auth.users(id)` by primary key, use `on delete cascade`, and enable RLS.
   - A database trigger can safely create a `public.profiles` row whenever a user registers, after the trigger is thoroughly tested.

4. [Supabase — Row Level Security](https://supabase.com/docs/guides/database/postgres/row-level-security)
   - Every exposed public table must have RLS and policies.
   - Policies should use explicit roles and `auth.uid()` ownership checks.
   - Add indexes for user ID columns used by RLS policies.

## Existing project mapping

- The Supabase project already has `profiles`, `course_progress`, and `lesson_progress` with auth UUID ownership and RLS policies.
- The legacy `public.users` table is separate from Supabase Auth and is currently flagged with RLS disabled. It will not be used for the new CodeCraft Auth or progress flow.
- The implementation will standardize Flask server-side operations on `SUPABASE_SERVICE_ROLE_KEY`, keep the service key server-only, and use the user’s Supabase UUID as the progress owner.
