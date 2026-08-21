-- Allow an authenticated learner to create only their own profile if it predates the Auth trigger.
-- Normal sign-up still provisions profiles through handle_new_codecraft_user.
drop policy if exists "CodeCraft profile insert own" on public.profiles;
create policy "CodeCraft profile insert own"
  on public.profiles for insert to authenticated
  with check ((select auth.uid()) = id);
