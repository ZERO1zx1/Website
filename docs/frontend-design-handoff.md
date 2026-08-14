# Codehaven frontend design handoff

**Status:** Frontend-first prototype complete; backend integration intentionally deferred.  
**Branch:** `feat/frontend-redesign`

## Product direction

Codehaven is positioned as a calm, focused coding workspace rather than a generic LMS. The student should understand their next action within a few seconds, see progress without interpreting dense analytics, and move from a problem card into a distraction-free editor with minimal context switching.

The core visual language is a dark ink navigation rail, warm neutral learning canvas, indigo primary action, teal success/progress accent, amber attention state, and restrained coral error state. The design avoids decorative gradients except where they support a primary learning action.

## Figma file structure

The recommended Figma file should contain the following pages in order:

| Page | Contents |
|---|---|
| `00 Cover` | Product statement, visual direction, links to prototype and repository |
| `01 Foundations` | Primitive colors, semantic colors, typography, spacing, radius, elevation, motion, accessibility notes |
| `02 Components` | Buttons, nav item, sidebar, avatar, pill, stat card, progress bar, chart, problem card, modal, editor, toast, toggle |
| `03 Patterns` | Dashboard shell, learning path module, practice library, assessment card, profile settings |
| `04 Screens` | Dashboard, learning path, practice library, assessment list, profile/preferences, editor modal |
| `05 Prototype flows` | Continue learning, filter practice, open editor, run code, submit solution, theme toggle, mobile nav |
| `06 Handoff` | CSS variable mapping, API adapter contract, responsive breakpoints, open questions |

## Token naming

Figma variables and CSS custom properties should use the same semantic names. Primitive values are not applied directly to screens; screens use semantic or component tokens.

| Token group | Example names | Current implementation |
|---|---|---|
| Primitive color | `primitive/ink/950`, `primitive/purple/500`, `primitive/teal/600` | `--primitive-ink-950`, `--primitive-purple-500`, `--primitive-teal-600` |
| Semantic surface | `surface/page`, `surface/raised`, `surface/subtle`, `surface/dark` | `--color-surface-page`, `--color-surface-raised`, `--color-surface-subtle`, `--color-surface-dark` |
| Semantic text | `text/primary`, `text/secondary`, `text/muted`, `text/on-dark` | `--color-text-primary`, `--color-text-secondary`, `--color-text-muted`, `--color-text-on-dark` |
| Semantic action | `action/primary`, `action/primary-hover`, `action/soft` | `--color-action-primary`, `--color-action-primary-hover`, `--color-action-soft` |
| Component | `button/primary/background/default`, `card/border/default`, `editor/surface` | Component styles in `style.css` reference semantic tokens |
| Typography | `font/display`, `font/body`, `font/code` | `--font-display`, `--font-body`, `--font-code` |
| Layout | `space/1` through `space/16`, `radius/sm` through `radius/xl` | `--space-*`, `--radius-*` |

Figma should use a light and dark mode for semantic surface, text, border and action variables. The dark code editor remains an intentionally stable dark surface in both application themes to preserve code readability and visual focus.

## Screen acceptance criteria

The dashboard must present the current learning action before secondary analytics. It contains four summary cards, a continue-learning card, today's focus checklist, activity chart, skill map and recent practice. The learning path must show module order, progress state and unlock state. The practice library must expose difficulty filters and a clear solve action. The editor must preserve problem context, provide an example and hint affordance, show code and output in distinct regions, and provide run/submit feedback.

The responsive behavior is as follows:

| Breakpoint | Behavior |
|---|---|
| Desktop, `>1180px` | Fixed 248px sidebar, two-column dashboard, three-column problem/assessment grids |
| Tablet, `821–1180px` | Sidebar remains available, dashboard collapses to one column, cards reduce to two columns |
| Mobile, `≤820px` | Sidebar becomes off-canvas, mobile menu appears, content becomes one column |
| Narrow mobile, `≤620px` | KPI cards become two columns, filters scroll horizontally, editor and profile content stack |

## Backend adapter boundary

The current browser uses `mockAdapter` in `frontend/static/js/app.js`. Presentation code calls adapter methods rather than `fetch` directly. During the integration phase, replace the adapter implementation while preserving the method names and returned object shape.

| Frontend method | Future endpoint | Expected responsibility |
|---|---|---|
| `getUser()` | `GET /api/auth/me` | Return authenticated user and role |
| `getDashboard()` | `GET /api/analytics/mastery/:userId` plus activity/submission summary | Return recent practice, mastery and activity data |
| `getLearningPath()` | `GET /api/courses/:courseId` | Return modules, lessons and progress state |
| `getProblems()` | `GET /api/problems` | Return problem cards and filters |
| `submitCode()` | `POST /api/submissions` | Submit code and return evaluation status/result |

No Supabase credentials are needed for frontend preview. Start it with:

```bash
FRONTEND_ONLY=true PYTHONPATH=. python -m flask --app 'app:create_app()' run --host 0.0.0.0 --port 5000
```

The `FRONTEND_ONLY` switch prevents backend blueprints from loading when credentials are intentionally unavailable. It does not remove or alter the API blueprints used in the normal backend mode.

For the expanded theme/i18n/auth preview, use the sidebar `Preview login / register` action, the topbar `EN/MN` selector and the theme toggle. The UI can be reviewed entirely without a Supabase connection.

## Theme, localization and authentication

The semantic theme contract covers page surfaces, raised panels, subtle surfaces, navigation, cards, form controls, native selects, input placeholders, checkbox states, segmented tabs, modal surfaces, chart backgrounds and focus rings. The code editor remains a stable dark work surface in both themes so syntax and output stay readable. Theme preference is persisted in local storage and is available from the topbar or Preferences.

The frontend includes an English and Mongolian dictionary layer. The language selector is available in the topbar and Preferences, and the selected language is persisted in local storage. Static labels use `data-i18n`, placeholders use `data-i18n-placeholder`, and dynamic mock cards pass through the same translation layer. The language contract is intentionally frontend-only until the backend user profile can persist locale.

The supplied Login/SignUp reference was used for the split-panel authentication direction, tabbed sign-in/create-account flow, social action row and responsive stacking pattern. The current auth preview adds accessible labels, password visibility control, remember-me and terms checkboxes, forgot-password affordance, demo continuation, EN/MN copy and dark mode support. The form submission remains mock-only and is ready to call the future auth adapter.

## Accessibility checklist

All primary navigation is keyboard-operable through native buttons. The editor modal has a dialog role, `aria-modal`, a labelled heading, Escape close behavior and focus restoration. The chart includes a text alternative through `role="img"` and an accessible label. Status is communicated with text and shape in addition to color. Focus-visible states, reduced-motion behavior and responsive reflow are included in the CSS.

## Research references

The token hierarchy follows Figma's guidance on primitive, semantic and component-specific tokens, which establishes a shared source of truth between design and code [1]. The accessibility acceptance criteria are based on WCAG 2.2 requirements for contrast, keyboard operation, focus visibility and reflow [2]. Dashboard information hierarchy, orientation, loading/empty states and action prioritization were cross-checked against dashboard UX practice guidance [3].

[1]: https://help.figma.com/hc/en-us/articles/18490793776023-Update-1-Tokens-variables-and-styles "Figma Learn — Tokens, variables, and styles"
[2]: https://www.w3.org/TR/WCAG22/ "W3C Web Content Accessibility Guidelines 2.2"
[3]: https://www.pencilandpaper.io/articles/ux-pattern-analysis-data-dashboards "Pencil & Paper — Dashboard Design UX Patterns"

## Final frontend verification addendum

The final frontend pass covers dynamic localization rather than only static shell labels. Practice cards, Learning path modules, editor modal, Assessments cards, Profile metadata and Preferences controls now use the same EN/MN translation layer. Editor output and success feedback also follow the selected language.

The browser verification sequence covered Dashboard, Practice, code editor Run flow, Login/Register, Learning path, Assessments, Profile and Preferences. A 390px mobile screenshot confirmed collapsed navigation, two-column KPI cards, full-width learning card and no horizontal clipping. HTML accessibility checks cover the main landmark, dialog state, language selector, auth inputs, code editor and live toast region.

Final frontend acceptance status: 15 regression tests passed, JavaScript syntax passed, Python compile passed, HTML structure checks passed and frontend-only Flask preview returned HTTP 200.
