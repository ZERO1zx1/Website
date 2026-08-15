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
    function nextAfterAuth() {
        const candidate = new URLSearchParams(window.location.search).get('next') || '/dashboard';
        return candidate.startsWith('/') && !candidate.startsWith('//') ? candidate : '/dashboard';
    }
    function isValidEmail(value) { return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(String(value || '').trim()); }
    function validationCopy(key) {
        const mn = document.documentElement.lang === 'mn';
        const copy = {
            email: mn ? 'Зөв имэйл хаяг оруулна уу.' : 'Enter a valid email address.',
            password: mn ? 'Нууц үг хамгийн багадаа 8 тэмдэгттэй байна.' : 'Password must be at least 8 characters.',
            requiredPassword: mn ? 'Нууц үгээ оруулна уу.' : 'Enter your password.',
            token: mn ? 'Password reset холбоос буруу эсвэл дутуу байна.' : 'This password reset link is missing or invalid.',
            summary: mn ? 'Үргэлжлүүлэхийн өмнө талбаруудыг засна уу.' : 'Please correct the highlighted fields before continuing.'
        };
        return copy[key] || key;
    }
    function clearValidation(form) {
        form.querySelectorAll('[data-field-error]').forEach((node) => { node.textContent = ''; });
        form.querySelectorAll('.is-invalid').forEach((node) => { node.classList.remove('is-invalid'); node.removeAttribute('aria-invalid'); });
        const summary = form.querySelector('[data-validation-summary]');
        if (summary) summary.textContent = '';
    }
    function setValidationError(form, field, text) {
        const input = form.querySelector(`[name="${field}"]`);
        const error = form.querySelector(`[data-field-error="${field}"]`);
        if (input) { input.classList.add('is-invalid'); input.setAttribute('aria-invalid', 'true'); }
        if (error) error.textContent = text;
    }
    function validatePageForm(form, data) {
        const mode = form.dataset.pageAuth;
        if (!['login', 'register', 'reset-request', 'reset-confirm'].includes(mode)) return { valid: true };
        clearValidation(form);
        const errors = [];
        if (!isValidEmail(data.email) && ['login', 'register', 'reset-request'].includes(mode)) { setValidationError(form, 'email', validationCopy('email')); errors.push('email'); }
        if (mode === 'register' && String(data.name || '').trim().length < 2) { setValidationError(form, 'name', document.documentElement.lang === 'mn' ? 'Нэрээ оруулна уу.' : 'Enter your full name.'); errors.push('name'); }
        if (mode === 'register' && String(data.password || '').length < 8) { setValidationError(form, 'password', validationCopy('password')); errors.push('password'); }
        if (mode === 'register' && !data.terms) { setValidationError(form, 'terms', document.documentElement.lang === 'mn' ? 'Үйлчилгээний нөхцөлийг зөвшөөрнө үү.' : 'Accept the Terms of Service to continue.'); errors.push('terms'); }
        if (mode === 'login' && !String(data.password || '').trim()) { setValidationError(form, 'password', validationCopy('requiredPassword')); errors.push('password'); }
        if (mode === 'login' && String(data.password || '').length > 0 && String(data.password || '').length < 8) { setValidationError(form, 'password', validationCopy('password')); errors.push('password'); }
        if (mode === 'reset-confirm' && String(data.token || '').length < 20) { setValidationError(form, 'token', validationCopy('token')); errors.push('token'); }
        if (mode === 'reset-confirm' && String(data.password || '').length < 8) { setValidationError(form, 'password', validationCopy('password')); errors.push('password'); }
        if (errors.length) {
            const summary = form.querySelector('[data-validation-summary]');
            if (summary) summary.textContent = validationCopy('summary');
            form.querySelector('.is-invalid')?.focus();
            return { valid: false };
        }
        return { valid: true };
    }
    function wireValidationInputs() {
        document.querySelectorAll('[data-page-auth] input').forEach((input) => input.addEventListener('input', () => {
            input.classList.remove('is-invalid');
            input.removeAttribute('aria-invalid');
            const error = input.closest('label')?.querySelector(`[data-field-error="${input.name}"]`) || input.form?.querySelector(`[data-field-error="${input.name}"]`);
            if (error) error.textContent = '';
            const summary = input.form?.querySelector('[data-validation-summary]');
            if (summary && !input.form.querySelector('.is-invalid')) summary.textContent = '';
        }));
    }
    function wireAuthForms() {
        document.querySelectorAll('[data-page-auth]').forEach((form) => form.addEventListener('submit', async (event) => {
            event.preventDefault();
            const data = Object.fromEntries(new FormData(form).entries());
            const validation = validatePageForm(form, data);
            if (!validation.valid) return;
            const submit = form.querySelector('button[type="submit"]');
            if (submit) submit.disabled = true;
            try {
                if (form.dataset.pageAuth === 'login') {
                    const payload = await api.request('/api/auth/login', {method: 'POST', body: JSON.stringify({email: data.email, password: data.password})});
                    saveSession(payload); go(nextAfterAuth()); return;
                }
                if (form.dataset.pageAuth === 'register') {
                    const payload = await api.request('/api/auth/register', {method: 'POST', body: JSON.stringify({name: data.name, email: data.email, password: data.password})});
                    saveSession(payload); go(nextAfterAuth()); return;
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
        const requestForm = document.querySelector('[data-page-auth="reset-request"]');
        if (!form) return;
        const token = new URLSearchParams(window.location.search).get('token');
        const hasToken = Boolean(token);
        form.hidden = !hasToken;
        form.style.display = hasToken ? '' : 'none';
        if (requestForm) {
            requestForm.hidden = hasToken;
            requestForm.style.display = hasToken ? 'none' : '';
        }
        if (hasToken) form.querySelector('[name="token"]').value = token;
    }
    function renderDashboardCourses(courses) {
        const grid = document.querySelector('[data-dashboard-courses]');
        if (!grid) return;
        if (!courses.length) { grid.innerHTML = '<p class="muted">Learning paths will appear here when they are available.</p>'; return; }
        grid.innerHTML = courses.slice(0, 3).map((course) => {
            const progress = Number(course.progress || 0);
            const lessons = (course.modules || []).flatMap((module) => module.lessons || []);
            const next = lessons.find((lesson) => lesson.status !== 'completed');
            const status = progress >= 100 ? 'Completed' : progress > 0 ? 'In progress' : 'Not started';
            return `<article class="dashboard-page-course"><div class="dashboard-page-course-top"><span class="course-icon">${escapeHtml(course.icon || 'CO')}</span><span>${status}</span></div><h3>${escapeHtml(course.title || 'Learning path')}</h3><p>${escapeHtml(course.description || 'A practical path for your next skill.')}</p><div class="dashboard-course-progress"><span style="width:${Math.min(100, Math.max(0, progress))}%"></span></div><small>${progress}% complete · ${escapeHtml(next?.title || 'Ready for review')}</small></article>`;
        }).join('');
    }
    function wireDashboard() {
        const dashboard = document.querySelector('[data-stat="mastery"]');
        if (!dashboard) return;
        if (!sessionStorage.getItem(tokenKey)) { go('/login'); return; }
        const statusNode = document.querySelector('[data-dashboard-status]');
        const refreshButton = document.querySelector('[data-dashboard-refresh]');
        const setStatus = (text, type = 'info') => { if (statusNode) { statusNode.textContent = text; statusNode.dataset.state = type; } };
        const setBusy = (busy) => { if (refreshButton) refreshButton.disabled = busy; document.querySelector('.dashboard-page')?.classList.toggle('is-loading', busy); };
        const loadDashboard = async () => {
            setBusy(true);
            setStatus('Loading your private dashboard…');
            try {
                const [mePayload, statsPayload, coursesPayload] = await Promise.all([
                    api.request('/api/auth/me'),
                    api.request('/api/analytics/dashboard'),
                    api.request('/api/courses')
                ]);
                const stats = statsPayload.stats || {};
                const user = mePayload.user || mePayload;
                const name = user?.name || statsPayload.user?.name || '';
                const nameNode = document.querySelector('[data-dashboard-name]');
                if (nameNode) nameNode.textContent = name ? `, ${name}` : '';
                document.querySelector('[data-stat="mastery"]').textContent = `${Number(stats.overall_mastery || 0)}%`;
                document.querySelector('[data-stat="solved"]').textContent = String(stats.solved_problems || 0);
                const minutes = Number(stats.study_minutes || 0);
                document.querySelector('[data-stat="study"]').textContent = minutes >= 60 ? `${Math.floor(minutes / 60)}h ${minutes % 60}m` : `${minutes}m`;
                document.querySelector('[data-stat="streak"]').textContent = `${Number(stats.current_streak || 0)} days`;
                const courses = coursesPayload.courses || [];
                renderDashboardCourses(courses);
                const course = courses.find((item) => Number(item.progress || 0) < 100) || courses[0];
                const lessons = (course?.modules || []).flatMap((module) => (module.lessons || []).map((lesson) => ({...lesson, moduleTitle: module.title})));
                const next = lessons.find((lesson) => lesson.status !== 'completed');
                document.querySelector('[data-live-course]').textContent = course?.title || 'Your learning path';
                document.querySelector('[data-live-description]').textContent = course?.description || 'Your next lesson will appear here.';
                document.querySelector('[data-live-progress-bar]').style.width = `${Number(course?.progress || 0)}%`;
                document.querySelector('[data-live-next]').textContent = next?.title || 'Start a lesson';
                const focus = document.querySelector('[data-focus-list]');
                if (focus) focus.innerHTML = lessons.filter((lesson) => lesson.status !== 'completed').slice(0, 3).map((lesson) => `<div class="focus-item"><span><strong>${escapeHtml(lesson.title)}</strong><small>${escapeHtml(lesson.moduleTitle || 'Lesson')} · ${escapeHtml(lesson.status || 'not_started')}</small></span><span class="focus-arrow">→</span></div>`).join('') || '<p class="muted">You are caught up.</p>';
                setStatus(`Updated ${new Date().toLocaleTimeString([], {hour: '2-digit', minute: '2-digit'})}`, 'success');
            } catch (error) {
                if (error.status === 401) { sessionStorage.removeItem(tokenKey); go('/login'); return; }
                setStatus(message(error, 'Dashboard data could not be loaded.'), 'error');
                show(message(error, 'Dashboard data could not be loaded.'), 'error');
            } finally { setBusy(false); }
        };
        refreshButton?.addEventListener('click', loadDashboard);
        document.querySelector('[data-page-logout]')?.addEventListener('click', () => { sessionStorage.removeItem(tokenKey); go('/login'); });
        loadDashboard();
        window.setInterval(loadDashboard, 15000);
    }
    function escapeHtml(value) { return String(value ?? '').replace(/[&<>'"]/g, (character) => ({'&':'&amp;','<':'&lt;','>':'&gt;',"'":'&#39;','"':'&quot;'}[character])); }
    function applyProviderNote() { document.querySelectorAll('[data-provider-note]').forEach((node) => { node.textContent = backendEnabled ? '' : 'Sign in and recovery actions require backend mode.'; }); }
    function showCallbackError() {
        const code = new URLSearchParams(window.location.search).get('auth_error');
        if (!code) return;
        show(code === 'google_oauth_failed' ? 'Google sign-in could not be completed. Check the Supabase Google provider and callback URL.' : 'Authentication could not be completed.', 'error');
    }
    wireAuthForms(); wireValidationInputs(); wireRecoveryToken(); wireDashboard(); applyProviderNote(); showCallbackError();
})();
