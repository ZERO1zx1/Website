# Browser dashboard smoke findings

Date: 2026-08-16

The protected `/dashboard` route redirected unauthenticated access to `/login?next=%2Fdashboard`. A real local account (`e2e-audit-1786854225@example.com`) successfully logged in and returned to `/dashboard`.

The authenticated dashboard rendered the shared workspace shell, role label, navigation links, course discovery cards, next-lesson focus items, progress report, assessment signal, and the account-specific name. Existing persisted data was reflected in the page: the dashboard showed one completed lesson and three active paths for the audit account.

The browser page displayed a live-study-activity empty state when the account had no completed lesson activity. The backend/API smoke flow independently confirmed that after completing a lesson, the dashboard returns `study_minutes=20`, `current_streak=1`, and a seven-day `daily_activity` array with the current day populated. The activity chart frontend now consumes this response rather than fabricating daily values.

The dashboard was rendered with Mongolian navigation labels while the language selector was visible. The page is one unified authenticated application even though its major experiences are separate routes.
