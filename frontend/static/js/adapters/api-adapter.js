/* Codehaven API adapter. It is loaded in both modes; app.js selects it only when the Flask shell enables backend mode. */
(function exposeCodehavenApiAdapter() {
    const tokenKey = 'codehaven-access-token';

    function getToken() {
        return localStorage.getItem(tokenKey);
    }

    function saveSession(payload) {
        if (payload.token) localStorage.setItem(tokenKey, payload.token);
        return payload.user || payload.data || payload;
    }

    async function request(path, options = {}) {
        const token = getToken();
        const response = await fetch(path, {
            credentials: 'include',
            headers: {
                'Content-Type': 'application/json',
                ...(token ? { Authorization: `Bearer ${token}` } : {}),
                ...(options.headers || {})
            },
            ...options
        });
        const payload = await response.json().catch(() => ({}));
        if (!response.ok) {
            const serverError = typeof payload.error === 'object' ? payload.error : null;
            const error = new Error(serverError?.message || payload.error || payload.message || `Request failed: ${response.status}`);
            error.status = response.status;
            error.payload = payload;
            throw error;
        }
        return payload;
    }

    window.codehavenApiAdapter = {
        async getUser() {
            if (!getToken()) return null;
            const payload = await request('/api/auth/me');
            return payload.user || payload.data || payload;
        },
        async login(email, password) {
            const payload = await request('/api/auth/login', {
                method: 'POST',
                body: JSON.stringify({ email, password })
            });
            return saveSession(payload);
        },
        async register(name, email, password) {
            const payload = await request('/api/auth/register', {
                method: 'POST',
                body: JSON.stringify({ name, email, password })
            });
            return saveSession(payload);
        },
        logout() {
            localStorage.removeItem(tokenKey);
        },
        async getDashboard() {
            const user = await this.getUser();
            const dashboard = await request('/api/analytics/dashboard');
            return normalizeDashboard({ ...dashboard, user });
        },
        async getLearningPath(courseId) {
            const payload = courseId
                ? await request(`/api/courses/${courseId}`)
                : await request('/api/courses');
            const course = payload.course || payload.data?.[0] || payload.courses?.[0] || payload;
            return { ...course, modules: course.modules || [] };
        },
        async getProblems(query = {}) {
            const params = new URLSearchParams(query);
            const payload = await request(`/api/problems${params.toString() ? `?${params}` : ''}`);
            return { problems: payload.problems || payload.data || [] };
        },
        async submitCode(input) {
            return request('/api/submissions', { method: 'POST', body: JSON.stringify(input) });
        }
    };

    function normalizeDashboard(payload) {
        return {
            ...payload,
            recentPractice: payload.recentPractice || payload.recent_practice || [],
            activity: payload.activity || [],
            skills: payload.skills || payload.mastery || []
        };
    }
})();
