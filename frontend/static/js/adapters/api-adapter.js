/* Codehaven API adapter. It is loaded in both modes; app.js selects it only when the Flask shell enables backend mode. */
(function exposeCodehavenApiAdapter() {
    async function request(path, options = {}) {
        const response = await fetch(path, {
            credentials: 'include',
            headers: { 'Content-Type': 'application/json', ...(options.headers || {}) },
            ...options
        });
        const payload = await response.json().catch(() => ({}));
        if (!response.ok) {
            const error = new Error(payload.error || payload.message || `Request failed: ${response.status}`);
            error.status = response.status;
            error.payload = payload;
            throw error;
        }
        return payload;
    }

    window.codehavenApiAdapter = {
        async getUser() {
            const payload = await request('/api/auth/me');
            return payload.user || payload.data || payload;
        },
        async getDashboard() {
            const user = await this.getUser();
            const mastery = await request(`/api/analytics/mastery/${user.id}`);
            return normalizeDashboard(mastery);
        },
        async getLearningPath(courseId) {
            const payload = await request(`/api/courses/${courseId || 'current'}`);
            return payload.data || payload.course || payload;
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
