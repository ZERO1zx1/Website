# Supabase тохируулах

## Project ба migration

Хоосон Supabase project үүсгээд repository root-оос:

```bash
supabase link --project-ref YOUR_PROJECT_REF
supabase db push
```

Migration-ууд `supabase/migrations` дотор version-оор эрэмбэлэгдэнэ. `profiles.id` болон learner-owned table-ийн `user_id` нь `auth.users.id` UUID-г ашиглана. Trigger шинэ Auth user бүрт profile үүсгэнэ. `updated_at`, FK, index, constraint, `timestamptz`, RLS, Realtime migration-д багтсан.

Clean verification:

```bash
supabase db reset
supabase db lint
```

Production project дээр reset хийхгүй; эхлээд backup авч dry-run diff-ийг шалгана.

## Auth provider

Authentication → Providers хэсэгт Email болон Google-г enable хийнэ. URL Configuration-д deployment-ийн HTTPS Site URL болон `https://YOUR_DOMAIN/api/auth/google/callback` redirect URL-г нэмнэ.

Google client secret болон service-role key-г Git, frontend bundle, log-д хэзээ ч оруулахгүй.

## Server environment

```env
SUPABASE_URL=https://PROJECT.supabase.co
SUPABASE_PUBLISHABLE_KEY=sb_publishable_...
SUPABASE_SERVICE_ROLE_KEY=server-secret-only
```

Publishable key-г `/api/public-config` буцааж болно. Service role зөвхөн Flask process-д байна. Learner API бүр authenticated UUID-г payload-д server-side онооно.

## RLS шалгах

Хоёр student account-аар profile/progress/quiz мөр үүсгээд нэг account нөгөөгийн мөрийг уншиж/шинэчилж чадахгүйг шалгана. Student profile-ийн `role` талбарыг өөрчилж чадахгүй. Teacher/admin ажиллагаа Flask RBAC-аар дамжина.

## Rollback

Production-д schema table drop хийхээс өмнө point-in-time backup ашиглана. Шинэ learner table-ууд backward-compatible тул application image-ийг өмнөх хувилбар руу буцаах эхний rollback-д table устгах шаардлагагүй.
