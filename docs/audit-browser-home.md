# Browser home smoke findings

Date: 2026-08-16

The canonical `/` route now renders the public marketing home page rather than the old all-in-one workspace. Browser output showed the public navigation, registration/login CTAs, learning-platform copy, and feature callouts. It did not render the old authenticated dashboard shell or preset learner account.

The home illustration contains static marketing copy such as `68% complete` and `74% overall mastery`; these are presentation-only marketing values and are not presented as the signed-in user's account statistics. Authenticated dashboard metrics are loaded separately from `/api/analytics/dashboard` and show empty states until the account has saved activity.
