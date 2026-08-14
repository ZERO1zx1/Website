(function () {
    const backendEnabled = document.documentElement.dataset.backend === 'enabled';
    const tokenKey = 'codehaven-access-token';
    const toast = document.getElementById('page-toast');
    const api = {
        async request(path, options = {}) {
            if (!backendEnabled) throw new Error('Backend mode is required for this action.');
            const token = sessionStorage.getItem(tokenKey);
            const response = await fetch(path, {
                credentials: 'include',
                ...options,
                headers: {'Accept': 'application/json', ...(options.body ? {'Content-Type': 'application/json'} : {}), ...(token ? {'Authorization': `Bearer ${token}`} : {}), ...(options.headers || {})}
            });
            const payload = await response.json().catch(() => ({}));
            if (!response.ok) {
                const error = typeof payload.error === 'object' ? payload.error : {message: payload.error || payload.message || `Request failed: ${response.status}`};
                const failure = new Error(error.message || 'Request failed.');
                failure.payload = payload;
                failure.status = response.status;
                throw failure;
            }
            return payload;
        }
    };
    function show(message, type = 'info') {
        if (!toast) return;
        toast.textContent = message;
        toast.dataset.type = type;
        toast.classList.add('is-visible');
        window.clearTimeout(show.timer);
        show.timer = window.setTimeout(() => toast.classList.remove('is-visible'), 3800);
    }
    function message(error, fallback) {
        const detail = error?.payload?.error;
        return document.documentElement.lang === 'mn' ? (detail?.message_mn || fallback) : (detail?.message || error?.message || fallback);
    }
    function saveSession(payload) {
        if (payload?.token) sessionStorage.setItem(tokenKey, payload.token);
        return payload?.user || payload;
    }
    function go(path) { window.location.assign(path); }
    function wireAuthForms() {
        document.querySelectorAll('[data-page-auth]').forEach((form) => form.addEventListener('submit', async (event) => {
            event.preventDefault();
            const submit = form.querySelector('button[type="submit"]');
            if (submit) submit.disabled = true;
            const data = Object.fromEntries(new FormData(form).entries());
            try {
                if (form.dataset.pageAuth === 'login') {
                    const payload = await api.request('/api/auth/login', {method: 'POST', body: JSON.stringify({email: data.email, password: data.password})});
                    saveSession(payload); go('/dashboard'); return;
                }
                if (form.dataset.pageAuth === 'register') {
                    const payload = await api.request('/api/auth/register', {method: 'POST', body: JSON.stringify({name: data.name, email: data.email, password: data.password})});
                    saveSession(payload); go('/dashboard'); return;
                }
                if (form.dataset.pageAuth === 'reset-request') {
                    const payload = await api.request('/api/auth/password-reset/request', {method: 'POST', body: JSON.stringify({email: data.email})});
                    const result = document.querySelector('[data-reset-result]');
                    if (result) {
                        result.hidden = false;
                        result.innerHTML = payload.reset_url ? `Local reset link: <a href="${escapeHtml(payload.reset_url)}">Open password reset form →</a>` : escapeHtml(payload.message || 'If the account exists, recovery instructions were sent.');
                    }
                    show(payload.message || 'Reset instructions requested.', 'success');
                    return;
                }
                if (form.dataset.pageAuth === 'reset-confirm') {
                    await api.request('/api/auth/password-reset/confirm', {method: 'POST', body: JSON.stringify({token: data.token, password: data.password})});
                    show('Password updated. You can sign in now.', 'success');
                    window.setTimeout(() => go('/login'), 700);
                }
            } catch (error) {
                show(message(error, 'Authentication request could not be completed.'), 'error');
            } finally {
                if (submit) submit.disabled = false;
            }
        }));
        document.querySelectorAll('[data-page-google]').forEach((button) => button.addEventListener('click', async () => {
            try {
                const payload = await api.request('/api/auth/google/start');
                if (!payload.url) throw new Error('Google sign-in URL was not returned.');
                go(payload.url);
            } catch (error) { show(message(error, 'Google sign-in is not configured yet.'), 'error'); }
        }));
        document.querySelectorAll('[data-page-otp]').forEach((button) => button.addEventListener('click', () => show('Email code sign-in is available from the main learning workspace.')));
    }
    function wireRecoveryToken() {
        const form = document.querySelector('[data-page-auth="reset-confirm"]');
        if (!form) return;
        const token = new URLSearchParams(window.location.search).get('token');
        if (token) { form.hidden = false; form.querySelector('[name="token"]').value = token; }
    }
    function wireDashboard() {
        const dashboard = document.querySelector('[data-stat="mastery"]');
        if (!dashboard) return;
        if (!sessionStorage.getItem(tokenKey)) { go('/login'); return; }
        Promise.all([api.request('/api/analytics/dashboard'), api.request('/api/courses')]).then(([statsPayload, coursesPayload]) => {
            const stats = statsPayload.stats || {};
            const name = statsPayload.user?.name || statsPayload.name || '';
            const nameNode = document.querySelector('[data-dashboard-name]');
            if (nameNode) nameNode.textContent = name ? `, ${name}` : '';
            document.querySelector('[data-stat="mastery"]').textContent = `${Number(stats.overall_mastery || 0)}%`;
            document.querySelector('[data-stat="solved"]').textContent = String(stats.solved_problems || 0);
            const minutes = Number(stats.study_minutes || 0);
            document.querySelector('[data-stat="study"]').textContent = minutes >= 60 ? `${Math.floor(minutes / 60)}h ${minutes % 60}m` : `${minutes}m`;
            document.querySelector('[data-stat="streak"]').textContent = `${Number(stats.current_streak || 0)} days`;
            const courses = coursesPayload.courses || [];
            const course = courses.find((item) => Number(item.progress || 0) < 100) || courses[0];
            const lessons = (course?.modules || []).flatMap((module) => module.lessons || []);
            const next = lessons.find((lesson) => lesson.status !== 'completed');
            document.querySelector('[data-live-course]').textContent = course?.title || 'Your learning path';
            document.querySelector('[data-live-description]').textContent = course?.description || 'Your next lesson will appear here.';
            document.querySelector('[data-live-progress-bar]').style.width = `${Number(course?.progress || 0)}%`;
            document.querySelector('[data-live-next]').textContent = next?.title || 'Start a lesson';
            const focus = document.querySelector('[data-focus-list]');
            if (focus) focus.innerHTML = lessons.filter((lesson) => lesson.status !== 'completed').slice(0, 3).map((lesson) => `<div><strong>${escapeHtml(lesson.title)}</strong><small>${escapeHtml(lesson.status || 'not_started')}</small></div>`).join('') || '<p class="muted">You are caught up.</p>';
        }).catch((error) => show(message(error, 'Dashboard data could not be loaded.'), 'error'));
        document.querySelector('[data-page-logout]')?.addEventListener('click', () => { sessionStorage.removeItem(tokenKey); go('/login'); });
    }
    function escapeHtml(value) { return String(value ?? '').replace(/[&<>'"]/g, (character) => ({'&':'&amp;','<':'&lt;','>':'&gt;',"'":'&#39;','"':'&quot;'}[character])); }
    function applyProviderNote() { document.querySelectorAll('[data-provider-note]').forEach((node) => { node.textContent = backendEnabled ? '' : 'Sign in and recovery actions require backend mode.'; }); }
    function showCallbackError() {
        const code = new URLSearchParams(window.location.search).get('auth_error');
        if (!code) return;
        show(code === 'google_oauth_failed' ? 'Google sign-in could not be completed. Check the Supabase Google provider and callback URL.' : 'Authentication could not be completed.', 'error');
    }
    wireAuthForms(); wireRecoveryToken(); wireDashboard(); applyProviderNote(); showCallbackError();
})();
