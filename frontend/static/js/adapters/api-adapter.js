/* Codehaven API adapter for authenticated backend mode. */
(function exposeCodehavenApiAdapter() {
    const tokenKey = 'codehaven-access-token';
    const requestTimeoutMs = 15000;

    function consumeOAuthSession() {
        if (!window.location.hash) return;
        const params = new URLSearchParams(window.location.hash.slice(1));
        const token = params.get('auth_token');
        if (!token) return;
        sessionStorage.setItem(tokenKey, token);
        window.history.replaceState({}, document.title, `${window.location.pathname}${window.location.search}`);
    }

    function getToken() {
        consumeOAuthSession();
        const sessionToken = sessionStorage.getItem(tokenKey);
        if (sessionToken) return sessionToken;
        const legacyToken = localStorage.getItem(tokenKey);
        if (legacyToken) {
            sessionStorage.setItem(tokenKey, legacyToken);
            localStorage.removeItem(tokenKey);
            return legacyToken;
        }
        return null;
    }

    function clearSession() {
        sessionStorage.removeItem(tokenKey);
        localStorage.removeItem(tokenKey);
    }

    function saveSession(payload) {
        clearSession();
        if (payload.token) sessionStorage.setItem(tokenKey, payload.token);
        return payload.user || payload.data || payload;
    }

    async function request(path, options = {}) {
        const token = getToken();
        const controller = new AbortController();
        const timeout = window.setTimeout(() => controller.abort(), requestTimeoutMs);
        try {
            const response = await fetch(path, {
                credentials: 'include',
                ...options,
                signal: options.signal || controller.signal,
                headers: {
                    Accept: 'application/json',
                    ...(options.body ? { 'Content-Type': 'application/json' } : {}),
                    ...(token ? { Authorization: `Bearer ${token}` } : {}),
                    ...(options.headers || {})
                }
            });
            const payload = await response.json().catch(() => ({}));
            if (!response.ok) {
                if (response.status === 401) clearSession();
                const serverError = typeof payload.error === 'object' ? payload.error : null;
                const error = new Error(serverError?.message || payload.error || payload.message || `Request failed: ${response.status}`);
                error.status = response.status;
                error.code = serverError?.code;
                error.payload = payload;
                throw error;
            }
            return payload;
        } catch (error) {
            if (error.name === 'AbortError') {
                const timeoutError = new Error('The request timed out. Please retry.');
                timeoutError.code = 'TIMEOUT';
                throw timeoutError;
            }
            throw error;
        } finally {
            window.clearTimeout(timeout);
        }
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
        async requestOtp(email) {
            return request('/api/auth/otp/request', {
                method: 'POST',
                body: JSON.stringify({ email })
            });
        },
        async verifyOtp(email, code) {
            const payload = await request('/api/auth/otp/verify', {
                method: 'POST',
                body: JSON.stringify({ email, code })
            });
            return saveSession(payload);
        },
        async startGoogleLogin() {
            const payload = await request('/api/auth/google/start');
            if (!payload.url) throw new Error('Google sign-in URL was not returned.');
            window.location.assign(payload.url);
        },
        logout() {
            clearSession();
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
            const courses = payload.courses || payload.data || (payload.course ? [payload.course] : []);
            let course = courseId
                ? (payload.course || courses.find((item) => String(item.id) === String(courseId)))
                : (courses[0] || null);
            if (!courseId && course?.id && !(course.modules || []).length) {
                const selectedPayload = await request(`/api/courses/${course.id}`);
                course = selectedPayload.course || course;
            }
            const normalizedCourse = course ? normalizeCourse(course) : null;
            const normalizedCourses = courses.map((item) => String(item.id) === String(normalizedCourse?.id) ? normalizedCourse : normalizeCourse(item));
            return { ...normalizedCourse, courses: normalizedCourses, modules: normalizedCourse?.modules || [] };
        },
        async startLesson(lessonId) {
            return request(`/api/courses/lessons/${lessonId}/start`, { method: 'POST' });
        },
        async completeLesson(lessonId) {
            return request(`/api/courses/lessons/${lessonId}/complete`, { method: 'POST' });
        },
        async getProblems(query = {}) {
            const params = new URLSearchParams(query);
            const payload = await request(`/api/problems${params.toString() ? `?${params}` : ''}`);
            return { problems: (payload.problems || payload.data || []).map(normalizeProblem) };
        },
        async getProblem(problemId) {
            const payload = await request(`/api/problems/${problemId}`);
            return normalizeProblem(payload.problem || payload);
        },
        async runCode(input) {
            return request('/api/submissions/run', { method: 'POST', body: JSON.stringify(input) });
        },
        async submitCode(input) {
            return request('/api/submissions', { method: 'POST', body: JSON.stringify(input) });
        },
        async getSubmission(submissionId) {
            return request(`/api/submissions/${submissionId}`);
        },
        async streamSubmission(submissionId, onUpdate) {
            const token = getToken();
            const response = await fetch(`/api/submissions/${submissionId}/stream`, {
                headers: token ? { Authorization: `Bearer ${token}` } : {},
                credentials: 'include',
            });
            if (!response.ok || !response.body) throw new Error(`Submission stream failed: ${response.status}`);
            const reader = response.body.getReader();
            const decoder = new TextDecoder();
            let buffer = '';
            while (true) {
                const { value, done } = await reader.read();
                if (done) break;
                buffer += decoder.decode(value, { stream: true });
                const chunks = buffer.split(/\n\n/);
                buffer = chunks.pop() || '';
                chunks.forEach((chunk) => {
                    const line = chunk.split(/\n/).find((item) => item.startsWith('data:'));
                    if (!line) return;
                    try { onUpdate(JSON.parse(line.slice(5).trim())); } catch (error) { /* ignore malformed event */ }
                });
            }
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

    function normalizeProblem(problem) {
        return {
            ...problem,
            progress: problem.progress || 'New',
            icon: problem.icon || String(problem.id || 0).padStart(2, '0'),
            topic: problem.topic || problem.language || 'Practice',
            tags: problem.tags || [],
            keywords: problem.keywords || [],
        };
    }

    function normalizeCourse(course) {
        return {
            ...course,
            progress: Number(course.progress || 0),
            tags: course.tags || [],
            keywords: course.keywords || [],
            modules: (course.modules || []).map((module, index) => ({
                ...module,
                number: module.number || String(index + 1).padStart(2, '0'),
                meta: module.meta || module.description || '',
                status: module.status || 'not_started',
                complete: Boolean(module.complete),
                lessons: (module.lessons || []).map((lesson) => ({
                    ...lesson,
                    status: lesson.status || 'not_started',
                    complete: Boolean(lesson.complete || lesson.status === 'completed'),
                })),
            })),
        };
    }
})();
