# Codehaven Demo V1 — Frontend Scope

## Goal

Demo V1 is a complete frontend-only learning website for practical programming education. It uses plain HTML, CSS, and JavaScript with local mock data. Backend, Supabase, authentication providers, roles, and live persistence are deliberately deferred until the frontend prototype is reviewed and approved.

## Learning catalog

| Track | Primary topics | Example tags | Example keywords |
|---|---|---|---|
| Python foundations | Syntax, data structures, functions, files, OOP | `python`, `programming`, `backend` | variables, functions, lists, dictionaries, OOP |
| HTML and CSS responsive web | Semantic markup, forms, layout, responsive design, accessibility | `html`, `css`, `frontend`, `web` | semantic HTML, Flexbox, Grid, responsive, accessibility |
| JavaScript interactive web | DOM, events, async requests, browser APIs, modules | `javascript`, `frontend`, `web` | DOM, events, fetch, async, modules |
| Python Flask backend | APIs, authentication concepts, roles, databases, Docker | `python`, `flask`, `backend`, `api` | Flask, REST API, JWT, Supabase, Docker |
| Full-stack developer path | Architecture, testing, security, deployment, observability | `full-stack`, `frontend`, `backend`, `deployment` | architecture, testing, security, Docker, deployment |

## Demo V1 functionality

The frontend must provide a public landing page, course catalog, course cards, tag filtering, keyword search, selected learning path, modules, lesson progress states, practice problem filtering, code editor mock flow, assessments, profile, preferences, EN/MN localization, dark/light theme, responsive mobile layout, keyboard focus states, accessible labels, and explicit demo mode.

The demo uses local state and mock responses. A user can navigate through the interface without a database. Any login, Gmail OTP, Google OAuth, role permission, course creation, submission persistence, or teacher management control is shown only as a clearly labeled preview interaction and is not treated as a live backend feature in Demo V1.

## Content rules

Every course has a stable identifier, bilingual title and description, level, duration, progress percentage, tags, keywords, and ordered modules. Every module has a number, bilingual title, bilingual metadata, completion state, and status. Tags are short lowercase filter values; keywords are searchable concepts and may contain spaces. The same vocabulary is used by course search, course filtering, practice topics, and future backend seed data.

## Deferred backend phase

After Demo V1 approval, the frontend adapters will be connected to Flask and Supabase. The backend phase will add real course and lesson records, tags and keywords tables, authentication, user progress, submissions, assessments, teacher management, and owner/admin/teacher/student permissions without changing the approved frontend information architecture.
