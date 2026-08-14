/* Codehaven frontend prototype. Replace mockAdapter with apiAdapter in the integration phase. */

const curriculumData = window.CodehavenCurriculum || { recentPractice: [], courses: [], problems: [] };
const mockData = {
    user: { id: 7, name: 'Nara Sukh', initials: 'NS', role: 'Student', focus: 'Python & problem solving' },
    recentPractice: curriculumData.recentPractice,
    courses: curriculumData.courses,
    problems: curriculumData.problems
};

const mockAdapter = {
    async getUser() { return mockData.user; },
    async getDashboard() { return { recentPractice: mockData.recentPractice }; },
    async getLearningPath() {
        const firstCourse = mockData.courses[0] || { modules: [] };
        return { modules: firstCourse.modules || [], courses: mockData.courses };
    },
    async getProblems() { return { problems: mockData.problems }; }
};

// This interface matches the backend contract planned for phase two.
const apiAdapterContract = {
    getUser: 'GET /api/auth/me',
    getDashboard: 'GET /api/analytics/dashboard',
    getLearningPath: 'GET /api/courses/:courseId',
    getProblems: 'GET /api/problems',
    submitCode: 'POST /api/submissions'
};

const backendEnabled = document.documentElement.dataset.backend === 'enabled';
const hasOAuthSession = Boolean(new URLSearchParams(window.location.hash.slice(1)).get('auth_token'));
const hasBackendSession = Boolean(sessionStorage.getItem('codehaven-access-token') || localStorage.getItem('codehaven-access-token') || hasOAuthSession);
const demoMode = !backendEnabled && sessionStorage.getItem('codehaven-demo-mode') === 'true';
const selectedAdapter = backendEnabled && hasBackendSession && window.codehavenApiAdapter ? window.codehavenApiAdapter : mockAdapter;
const app = {
    dataAdapter: selectedAdapter,
    user: null,
    isDemoMode: demoMode,
    currentView: 'auth',
    activeFilter: 'all',
    problems: mockData.problems,
    courses: mockData.courses,
    curriculumTag: 'all',
    curriculumQuery: '',
    selectedCourseId: 'python',
    lastFocusedElement: null,
    theme: localStorage.getItem('codehaven-theme') || 'light',
    language: localStorage.getItem('codehaven-language') || 'en',
    authMode: 'login',
    realtimeTimer: null
};

const viewLabels = {
    home: ['Home', 'Welcome'],
    dashboard: ['Overview', 'Dashboard'],
    learn: ['Learning', 'Learning path'],
    practice: ['Practice', 'Practice library'],
    assessments: ['Assessments', 'Assessments'],
    profile: ['Your space', 'Profile'],
    settings: ['Your space', 'Preferences'],
    auth: ['Account', 'Sign in']
};

window.addEventListener('DOMContentLoaded', initializeApp);

async function initializeApp() {
    document.documentElement.dataset.theme = app.theme;
    bindNavigation();
    bindInteractions();
    if (app.isDemoMode) {
        app.user = mockData.user;
        app.dataAdapter = mockAdapter;
    } else if (hasBackendSession && window.codehavenApiAdapter) {
        try {
            app.user = await window.codehavenApiAdapter.getUser();
        } catch (error) {
            window.codehavenApiAdapter.logout?.();
            app.user = null;
            app.dataAdapter = window.codehavenApiAdapter;
            showToast(app.language === 'mn' ? 'Нэвтрэлт хүчингүй болсон. Дахин нэвтэрнэ үү.' : 'Your session is no longer valid. Please sign in again.', 'error');
        }
    }
    hydrateUser(app.user || { name: app.language === 'mn' ? 'Зочин' : 'Guest' });
    bindAuthentication();
    applyLanguage();
    if (app.user) {
        await refreshDataViews();
        startRealtimeRefresh();
    }
    applyLanguage();
    showView(app.user ? 'dashboard' : 'home');
}

function bindNavigation() {
    document.querySelectorAll('[data-view]').forEach((control) => {
        control.addEventListener('click', () => {
            if (control.dataset.authTarget) setAuthMode(control.dataset.authTarget);
            showView(control.dataset.view);
        });
    });
}

function bindInteractions() {
    document.getElementById('theme-toggle')?.addEventListener('click', toggleTheme);
    document.getElementById('language-select')?.addEventListener('change', (event) => setLanguage(event.target.value));
    document.getElementById('settings-language-select')?.addEventListener('change', (event) => setLanguage(event.target.value));
    document.getElementById('landing-language-select')?.addEventListener('change', (event) => setLanguage(event.target.value));
    document.getElementById('curriculum-search')?.addEventListener('input', (event) => {
        app.curriculumQuery = event.target.value.trim().toLowerCase();
        renderCourseCards(app.courses);
    });
    document.querySelectorAll('[data-curriculum-tag]').forEach((tag) => tag.addEventListener('click', () => {
        app.curriculumTag = tag.dataset.curriculumTag;
        document.querySelectorAll('[data-curriculum-tag]').forEach((item) => item.classList.toggle('is-active', item === tag));
        renderCourseCards(app.courses);
        const selected = app.courses.find((course) => course.id === app.selectedCourseId);
        renderSelectedCourse(selected);
    }));
    document.getElementById('close-lesson-preview')?.addEventListener('click', () => document.getElementById('lesson-preview')?.classList.add('is-hidden'));
    document.getElementById('complete-lesson')?.addEventListener('click', completeLessonPreview);
    document.getElementById('open-auth-screen')?.addEventListener('click', () => { setAuthMode('login'); showView('auth'); });
    document.querySelectorAll('[data-logout]').forEach((control) => control.addEventListener('click', logoutUser));
    document.querySelectorAll('[data-theme-choice]').forEach((button) => {
        button.addEventListener('click', () => setTheme(button.dataset.themeChoice));
    });
    const mobileMenu = document.getElementById('mobile-menu');
    const sidebar = document.querySelector('.sidebar');
    const sidebarScrim = document.getElementById('sidebar-scrim');
    const setSidebarOpen = (isOpen) => {
        sidebar?.classList.toggle('is-open', isOpen);
        sidebarScrim?.classList.toggle('is-visible', isOpen);
        sidebarScrim?.setAttribute('aria-hidden', String(!isOpen));
        mobileMenu?.setAttribute('aria-expanded', String(isOpen));
    };
    mobileMenu?.addEventListener('click', () => setSidebarOpen(!sidebar?.classList.contains('is-open')));
    sidebarScrim?.addEventListener('click', () => setSidebarOpen(false));
    document.querySelectorAll('[data-open-editor]').forEach((button) => button.addEventListener('click', openEditor));
    document.querySelectorAll('[data-close-editor]').forEach((button) => button.addEventListener('click', closeEditor));
    document.getElementById('run-code')?.addEventListener('click', runCode);
    document.getElementById('submit-code')?.addEventListener('click', submitCode);
    document.querySelectorAll('.filter-tab').forEach((tab) => tab.addEventListener('click', () => {
        app.activeFilter = tab.dataset.filter;
        document.querySelectorAll('.filter-tab').forEach((item) => item.classList.toggle('is-active', item === tab));
        renderProblemCards(app.problems);
    }));
    document.getElementById('global-search')?.addEventListener('input', (event) => {
            const query = event.target.value.trim().toLowerCase();
        if (query.length > 0) {
            showView('practice');
            renderProblemCards(app.problems.filter((problem) => `${localizeContent(problem.title)} ${localizeContent(problem.description)} ${problem.topic} ${(problem.tags || []).join(' ')} ${(problem.keywords || []).join(' ')}`.toLowerCase().includes(query)));
        } else {
            renderProblemCards(app.problems);
        }
    });
    document.addEventListener('keydown', (event) => {
        if ((event.metaKey || event.ctrlKey) && event.key.toLowerCase() === 'k') {
            event.preventDefault();
            document.getElementById('global-search')?.focus();
        }
        if (event.key === 'Escape') {
            closeEditor();
            document.querySelector('.sidebar')?.classList.remove('is-open');
            document.getElementById('sidebar-scrim')?.classList.remove('is-visible');
            document.getElementById('sidebar-scrim')?.setAttribute('aria-hidden', 'true');
            document.getElementById('mobile-menu')?.setAttribute('aria-expanded', 'false');
        }
        if ((event.metaKey || event.ctrlKey) && event.key === 'Enter' && document.getElementById('editor-modal')?.classList.contains('is-open')) runCode();
    });
}

function hydrateUser(user) {
    document.querySelectorAll('#sidebar-user-name').forEach((node) => { node.textContent = user.name || 'Learner'; });
    document.querySelectorAll('.sidebar-user > .avatar, .user-avatar').forEach((node) => {
        const initials = String(user.name || user.email || 'L').split(/\s+/).filter(Boolean).slice(0, 2).map((part) => part[0].toUpperCase()).join('');
        node.textContent = initials || 'L';
    });
    document.querySelectorAll('.sidebar-user > div > span').forEach((node) => {
        node.textContent = user.role ? capitalize(user.role) : 'Student';
    });
    document.querySelectorAll('[data-profile-name]').forEach((node) => { node.textContent = user.name || 'Account holder'; });
    document.querySelectorAll('[data-profile-email]').forEach((node) => { node.textContent = user.email || 'Signed in account'; });
    document.querySelectorAll('[data-profile-role]').forEach((node) => { node.textContent = String(user.role || 'student').toUpperCase(); });
    document.querySelectorAll('[data-profile-level]').forEach((node) => { node.textContent = user.role ? capitalize(user.role) : 'Student'; });
    document.querySelectorAll('[data-profile-avatar]').forEach((node) => { node.textContent = initials(user.name || user.email); });
}

function initials(value) {
    return String(value || 'Learner').split(/\s+/).filter(Boolean).slice(0, 2).map((part) => part[0].toUpperCase()).join('') || 'L';
}

function logoutUser() {
    window.codehavenApiAdapter?.logout?.();
    if (app.realtimeTimer) window.clearInterval(app.realtimeTimer);
    app.realtimeTimer = null;
    app.user = null;
    app.dataAdapter = window.codehavenApiAdapter || mockAdapter;
    setAuthMode('login');
    showView('auth');
    showToast(app.language === 'mn' ? 'Та аккаунтаас гарлаа.' : 'You have been signed out.', 'success');
}

function showView(viewName) {
    if (!viewLabels[viewName]) return;
    const protectedViews = new Set(['dashboard', 'learn', 'practice', 'assessments', 'profile', 'settings']);
    if (protectedViews.has(viewName) && !app.user) {
        setAuthMode('login');
        viewName = 'auth';
    }
    app.currentView = viewName;
    const isPublicView = !app.user && (viewName === 'home' || viewName === 'auth');
    document.body.classList.toggle('public-view', isPublicView);
    document.querySelectorAll('.view').forEach((view) => view.classList.toggle('is-visible', view.dataset.page === viewName));
    document.querySelectorAll('.nav-item').forEach((item) => {
        const active = item.dataset.view === viewName;
        item.classList.toggle('is-active', active);
        if (active) item.setAttribute('aria-current', 'page'); else item.removeAttribute('aria-current');
    });
    const [root, current] = viewLabels[viewName];
    document.getElementById('breadcrumb-root').textContent = root;
    document.getElementById('breadcrumb-current').textContent = current;
    document.querySelector('.sidebar')?.classList.remove('is-open');
    document.getElementById('sidebar-scrim')?.classList.remove('is-visible');
    document.getElementById('sidebar-scrim')?.setAttribute('aria-hidden', 'true');
    document.getElementById('mobile-menu')?.setAttribute('aria-expanded', 'false');
    if (viewName === 'practice') void renderProblems().catch(() => renderProblemCards(app.problems));
    if (viewName === 'auth') document.querySelector('.auth-card input')?.focus();
    applyLanguage();
}

async function startRealtimeRefresh() {
    if (app.realtimeTimer) window.clearInterval(app.realtimeTimer);
    app.realtimeTimer = window.setInterval(async () => {
        if (!app.user || document.hidden) return;
        try {
            await renderDashboard();
            if (app.currentView === 'learn') await renderLearningPath();
        } catch (error) {
            // Keep the current user view stable; the next interval retries live data.
        }
    }, 15000);
}

async function renderDashboard() {
    const container = document.getElementById('recent-practice-list');
    if (!container) return;
    renderDataState(container, 'loading');
    let dashboard;
    try {
        dashboard = await app.dataAdapter.getDashboard();
    } catch (error) {
        renderDataState(container, 'error', app.language === 'mn' ? 'Dashboard мэдээллийг ачаалж чадсангүй.' : 'Dashboard data could not be loaded.');
        throw error;
    }
    const recentPractice = Array.isArray(dashboard?.recentPractice) ? dashboard.recentPractice : [];
    const stats = dashboard?.stats || {};
    let livePath = null;
    try { livePath = await app.dataAdapter.getLearningPath(); } catch (error) { livePath = null; }
    const mastery = Number(stats.overall_mastery || 0);
    const solved = Number(stats.solved_problems || 0);
    const studyMinutes = Number(stats.study_minutes || 0);
    const streak = Number(stats.current_streak || 0);
    const masteryNode = document.getElementById('stat-mastery');
    const solvedNode = document.getElementById('stat-solved');
    const studyNode = document.getElementById('stat-study-time');
    const streakNode = document.getElementById('stat-streak');
    if (masteryNode) masteryNode.innerHTML = `${mastery}<span>%</span>`;
    if (solvedNode) solvedNode.textContent = String(solved);
    if (studyNode) studyNode.innerHTML = studyMinutes >= 60 ? `${Math.floor(studyMinutes / 60)}<span>h</span> ${studyMinutes % 60}<span>m</span>` : `${studyMinutes}<span>m</span>`;
    if (streakNode) streakNode.innerHTML = `${streak}<span> ${streak === 1 ? 'day' : 'days'}</span>`;
    const continueCourse = livePath?.courses?.find((course) => Number(course.progress || 0) < 100) || livePath?.courses?.[0];
    const continueLesson = continueCourse?.modules?.flatMap((module) => module.lessons || []).find((lesson) => lesson.status !== 'completed');
    const continueTitle = document.getElementById('continue-course-title');
    const continueDescription = document.getElementById('continue-course-description');
    const continueProgress = document.getElementById('continue-course-progress');
    const continueProgressBar = document.getElementById('continue-course-progress-bar');
    const continueNext = document.getElementById('continue-course-next');
    if (continueTitle) continueTitle.textContent = localizeContent(continueCourse?.title || 'Your learning path');
    if (continueDescription) continueDescription.textContent = localizeContent(continueCourse?.description || 'Your next lesson will appear here from your learning path.');
    if (continueProgress) continueProgress.textContent = `${continueCourse?.progress || 0}% complete`;
    if (continueProgressBar) continueProgressBar.style.width = `${continueCourse?.progress || 0}%`;
    if (continueNext) continueNext.textContent = localizeContent(continueLesson?.title || 'Start a lesson');
    const titleNode = document.getElementById('dashboard-title');
    const dateNode = document.getElementById('dashboard-date');
    if (titleNode) titleNode.textContent = app.user?.name ? `Keep your momentum, ${app.user.name}.` : 'Keep your momentum.';
    if (dateNode) dateNode.textContent = new Intl.DateTimeFormat(app.language === 'mn' ? 'mn-MN' : 'en-US', { weekday: 'long', month: 'long', day: 'numeric', year: 'numeric' }).format(new Date());
    const chartSummary = document.querySelector('.chart-summary');
    const chart = document.getElementById('activity-chart');
    if (chartSummary) chartSummary.innerHTML = `<strong>${studyMinutes >= 60 ? `${Math.floor(studyMinutes / 60)}h ${studyMinutes % 60}m` : `${studyMinutes}m`}</strong><span class="trend neutral">No comparison yet</span><span>from your account</span>`;
    if (chart) chart.innerHTML = studyMinutes === 0
        ? '<p class="empty-state">No study activity recorded yet. Complete a lesson to start your timeline.</p>'
        : `<p class="empty-state">${studyMinutes} minutes of learning activity are saved to your account. Daily activity detail will appear as you complete more lessons.</p>`;
    const skillPanel = document.querySelector('.skills-panel');
    const skills = Array.isArray(dashboard?.skills) ? dashboard.skills : [];
    if (skillPanel && skills.length === 0) skillPanel.innerHTML = '<div class="panel-heading"><div><p class="eyebrow">Skill map</p><h3>Where you’re growing</h3></div></div><p class="empty-state">Your skill map will appear after your first completed activity.</p>';
    container.innerHTML = recentPractice.length ? recentPractice.map((item) => `
        <div class="practice-row">
            <div class="practice-title"><span class="practice-symbol">${escapeHtml(item.icon || '01')}</span><div><strong>${escapeHtml(localizeContent(item.title || 'Practice'))}</strong><small>${escapeHtml(localizeContent(item.category || 'Practice'))}</small></div></div>
            <span class="practice-meta"><span class="status-dot"></span>${escapeHtml(localizeContent(item.status || 'New'))}</span>
            <span class="practice-score">${escapeHtml(item.score || '—')}</span>
            <button class="text-button" data-open-editor data-problem-id="${escapeHtml(item.problem_id || item.id || '')}">Review <span aria-hidden="true">→</span></button>
        </div>`).join('') : `<div class="empty-state">${app.language === 'mn' ? 'Одоогоор дадлагын түүх алга.' : 'No practice history yet.'}</div>`;
    container.querySelectorAll('[data-open-editor]').forEach((button) => button.addEventListener('click', openEditor));
    applyLanguage();
}

async function renderLearningPath() {
    const courseGrid = document.getElementById('course-grid');
    const moduleList = document.getElementById('module-list');
    if (courseGrid) renderDataState(courseGrid, 'loading');
    if (moduleList) renderDataState(moduleList, 'loading');
    try {
        const path = await app.dataAdapter.getLearningPath();
        app.courses = path.courses || [];
        renderCourseCards(app.courses);
        renderSelectedCourse(app.courses.find((course) => String(course.id) === String(app.selectedCourseId)) || app.courses[0]);
    } catch (error) {
        if (courseGrid) renderDataState(courseGrid, 'error', app.language === 'mn' ? 'Learning path ачаалж чадсангүй.' : 'Learning path could not be loaded.');
        if (moduleList) renderDataState(moduleList, 'error', app.language === 'mn' ? 'Module мэдээллийг ачаалж чадсангүй.' : 'Learning modules could not be loaded.');
        throw error;
    }
}

function renderCourseCards(courses) {
    const container = document.getElementById('course-grid');
    if (!container) return;
    const query = app.curriculumQuery;
    const filtered = courses.filter((course) => {
        const searchable = [localizeContent(course.title), localizeContent(course.description), ...(course.tags || []), ...(course.keywords || [])].join(' ').toLowerCase();
        const matchesTag = app.curriculumTag === 'all' || (course.tags || []).includes(app.curriculumTag);
        return matchesTag && (!query || searchable.includes(query));
    });
    if (!filtered.length) {
        container.innerHTML = `<div class="panel curriculum-empty" style="grid-column:1/-1">${app.language === 'mn' ? 'Ийм шүүлтүүртэй course олдсонгүй.' : 'No courses match these filters yet.'}</div>`;
        return;
    }
    const selectedIsVisible = filtered.some((course) => course.id === app.selectedCourseId);
    if (!selectedIsVisible) app.selectedCourseId = filtered[0].id;
    container.innerHTML = filtered.map((course) => `
        <article class="course-card ${String(course.id) === String(app.selectedCourseId) ? 'is-selected' : ''}">
            <div class="course-card-top"><span class="course-icon">${escapeHtml(course.icon || 'CO')}</span><span class="course-progress">${escapeHtml(course.progress ?? 0)}%</span></div>
            <h3>${escapeHtml(localizeContent(course.title))}</h3><p>${escapeHtml(localizeContent(course.description))}</p>
            <div class="course-tags">${(course.tags || []).map((tag) => `<span class="tag-chip tag-chip-small">${escapeHtml(tag)}</span>`).join('')}</div>
            <div class="course-card-meta"><span>${escapeHtml(localizeContent(course.level))}</span><span>${escapeHtml(localizeContent(course.duration))}</span></div>
            <button class="text-button" data-select-course="${escapeHtml(course.id)}">${app.language === 'mn' ? 'Замыг харах' : 'View path'} <span aria-hidden="true">→</span></button>
        </article>`).join('');
    container.querySelectorAll('[data-select-course]').forEach((button) => button.addEventListener('click', () => {
        app.selectedCourseId = button.dataset.selectCourse;
        renderCourseCards(app.courses);
        renderSelectedCourse(app.courses.find((course) => course.id === app.selectedCourseId));
    }));
    applyLanguage();
}

function renderSelectedCourse(course) {
    if (!course) return;
    const title = document.getElementById('curriculum-course-title');
    const meta = document.getElementById('curriculum-course-meta');
    const progress = document.getElementById('curriculum-course-progress');
    const progressBar = document.getElementById('curriculum-progress-bar');
    const container = document.getElementById('module-list');
    if (title) title.textContent = localizeContent(course.title);
    if (meta) meta.textContent = `${course.modules?.length || 0} ${app.language === 'mn' ? 'модуль' : 'modules'} · ${localizeContent(course.duration)}`;
    if (progress) progress.textContent = `${course.progress || 0}%`;
    if (progressBar) progressBar.style.width = `${course.progress || 0}%`;
    if (!container) return;
    container.innerHTML = (course.modules || []).map((module, index) => `
        <article class="module-card ${module.complete ? 'is-complete' : ''}" data-open-lesson="${index}" tabindex="0" role="button" aria-label="${escapeHtml(localizeContent(module.title))}">
            <span class="module-number">${module.complete ? '✓' : escapeHtml(module.number || String(index + 1).padStart(2, '0'))}</span>
            <div class="module-content"><strong>${escapeHtml(localizeContent(module.title))}</strong><span>${escapeHtml(localizeContent(module.meta))}</span></div>
            <span class="module-status">${escapeHtml(localizeContent(module.status))}</span>
        </article>`).join('');
    container.querySelectorAll('[data-open-lesson]').forEach((moduleCard) => {
        const open = () => void openLessonPreview(course, Number(moduleCard.dataset.openLesson));
        moduleCard.addEventListener('click', open);
        moduleCard.addEventListener('keydown', (event) => { if (event.key === 'Enter' || event.key === ' ') { event.preventDefault(); open(); } });
    });
}

async function openLessonPreview(course, moduleIndex) {
    const module = course?.modules?.[moduleIndex];
    const lesson = module?.lessons?.find((item) => item.status !== 'completed') || module?.lessons?.[0];
    if (!module || !lesson) {
        showToast(app.language === 'mn' ? 'Энэ модульд одоогоор хичээл алга.' : 'This module has no lesson yet.', 'error');
        return;
    }
    const preview = document.getElementById('lesson-preview');
    if (!preview) return;
    preview.dataset.courseId = String(course.id);
    preview.dataset.moduleIndex = String(moduleIndex);
    preview.dataset.lessonId = String(lesson.id);
    document.getElementById('lesson-preview-title').textContent = localizeContent(lesson.title || module.title);
    document.getElementById('lesson-preview-meta').textContent = `${localizeContent(module.title)} · ${lesson.estimated_minutes || 20} min`;
    document.getElementById('lesson-preview-objective').textContent = localizeContent(lesson.content || course.description);
    document.getElementById('lesson-preview-content').innerHTML = `<p>${escapeHtml(localizeContent(lesson.content || 'Work through this lesson at your own pace.')).replace(/\\n/g, '<br>')}</p>`;
    document.getElementById('lesson-preview-status').textContent = formatLessonStatus(lesson.status);
    document.getElementById('lesson-preview-keywords').innerHTML = (course.keywords || []).slice(0, 5).map((keyword) => `<span class="tag-chip tag-chip-small">${escapeHtml(keyword)}</span>`).join('');
    const completeButton = document.getElementById('complete-lesson');
    if (completeButton) {
        completeButton.disabled = lesson.status === 'completed';
        completeButton.textContent = lesson.status === 'completed' ? (app.language === 'mn' ? 'Дууссан' : 'Completed') : (app.language === 'mn' ? 'Дууссан гэж тэмдэглэх' : 'Mark lesson complete');
    }
    preview.classList.remove('is-hidden');
    preview.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    if (lesson.status !== 'completed' && backendEnabled && app.dataAdapter.startLesson) {
        try {
            await app.dataAdapter.startLesson(lesson.id);
            lesson.status = 'in_progress';
            document.getElementById('lesson-preview-status').textContent = formatLessonStatus('in_progress');
            renderSelectedCourse(course);
        } catch (error) {
            showToast(error.message || (app.language === 'mn' ? 'Хичээл нээж чадсангүй.' : 'Lesson could not be opened.'), 'error');
        }
    }
}

function formatLessonStatus(status) {
    const labels = {
        completed: app.language === 'mn' ? 'Дууссан' : 'Completed',
        in_progress: app.language === 'mn' ? 'Үзэж байна' : 'In progress',
        not_started: app.language === 'mn' ? 'Эхлээгүй' : 'Not started',
    };
    return labels[status] || labels.not_started;
}

async function completeLessonPreview() {
    const preview = document.getElementById('lesson-preview');
    const course = app.courses.find((item) => String(item.id) === String(preview?.dataset.courseId));
    const module = course?.modules?.[Number(preview?.dataset.moduleIndex)];
    const lesson = module?.lessons?.find((item) => String(item.id) === String(preview?.dataset.lessonId)) || module?.lessons?.[0];
    if (!module || !lesson) {
        showToast(app.language === 'mn' ? 'Энэ модульд хадгалах хичээл алга.' : 'This module has no lesson to complete yet.', 'error');
        return;
    }
    if (backendEnabled && app.dataAdapter.completeLesson) {
        try {
            await app.dataAdapter.completeLesson(lesson.id);
            lesson.status = 'completed';
            lesson.complete = true;
            preview.classList.add('is-hidden');
            await renderLearningPath();
            await renderDashboard();
            showToast(app.language === 'mn' ? 'Хичээл дууслаа. Ахиц хадгалагдлаа.' : 'Lesson complete. Progress saved.', 'success');
        } catch (error) {
            showToast(error.message || (app.language === 'mn' ? 'Ахиц хадгалах боломжгүй.' : 'Progress could not be saved.'), 'error');
        }
        return;
    }
    showToast(app.language === 'mn' ? 'Бодит бүртгэлтэй хэрэглэгчээр нэвтэрнэ үү.' : 'Sign in with a real account to save progress.', 'error');
}

async function renderProblems() {
    const container = document.getElementById('problem-grid');
    if (container) renderDataState(container, 'loading');
    try {
        const result = await app.dataAdapter.getProblems();
        app.problems = result.problems || [];
        renderProblemCards(app.problems);
    } catch (error) {
        if (container) renderDataState(container, 'error', app.language === 'mn' ? 'Practice бодлогуудыг ачаалж чадсангүй.' : 'Practice problems could not be loaded.');
        throw error;
    }
}

async function refreshDataViews() {
    const results = await Promise.allSettled([
        renderDashboard(),
        renderLearningPath(),
        renderProblems()
    ]);
    const failed = results.some((result) => result.status === 'rejected');
    if (failed && backendEnabled && window.codehavenApiAdapter === app.dataAdapter) {
        showToast(app.language === 'mn' ? 'Зарим мэдээллийг одоогоор ачаалж чадсангүй.' : 'Some live data could not be loaded yet.', 'error');
    }
}

function renderDataState(container, state, message = '') {
    if (!container) return;
    const copy = {
        loading: app.language === 'mn' ? 'Ачаалж байна…' : 'Loading…',
        empty: app.language === 'mn' ? 'Одоогоор мэдээлэл алга.' : 'Nothing is available yet.',
        error: message || (app.language === 'mn' ? 'Мэдээлэл ачаалж чадсангүй.' : 'Data could not be loaded.'),
    };
    container.innerHTML = `<div class="panel data-state data-state-${state}"><span class="data-state-indicator" aria-hidden="true"></span><strong>${escapeHtml(copy[state] || copy.empty)}</strong>${state === 'error' ? `<button class="text-button" data-retry-data>Retry <span aria-hidden="true">↻</span></button>` : ''}</div>`;
    container.querySelector('[data-retry-data]')?.addEventListener('click', () => void refreshDataViews());
}

function renderProblemCards(problems) {
    const container = document.getElementById('problem-grid');
    if (!container) return;
    const filtered = app.activeFilter === 'all' ? problems : problems.filter((problem) => problem.difficulty === app.activeFilter);
    if (!filtered.length) {
        container.innerHTML = `<div class="panel empty-state" style="grid-column:1/-1">${app.language === 'mn' ? 'Энэ шүүлтүүрт тохирох бодлого олдсонгүй.' : 'No problems match this filter yet.'}</div>`;
        return;
    }
    container.innerHTML = filtered.map((problem) => `
        <article class="problem-card">
            <div class="problem-card-top"><span class="pill ${problem.progress === 'Solved' ? 'pill-teal' : 'pill-muted'}">${escapeHtml(localizeContent(problem.progress || 'New'))}</span><span class="practice-symbol">${escapeHtml(problem.icon || '01')}</span></div>
            <h3>${escapeHtml(localizeContent(problem.title || 'Untitled problem'))}</h3><p>${escapeHtml(localizeContent(problem.description || ''))}</p>
            <div class="problem-tags">${(problem.tags || []).map((tag) => `<span class="tag-chip tag-chip-small">${escapeHtml(tag)}</span>`).join('')}</div>
            <div class="problem-card-footer"><span class="difficulty ${escapeHtml(problem.difficulty || 'easy')}">${escapeHtml(localizeContent(capitalize(problem.difficulty || 'easy')))} · ${escapeHtml(localizeContent(problem.topic || 'Practice'))}</span><button class="text-button" data-open-editor data-problem-id="${escapeHtml(problem.id || '')}">${localizeContent('Solve')} <span aria-hidden="true">→</span></button></div>
        </article>`).join('');
    container.querySelectorAll('[data-open-editor]').forEach((button) => button.addEventListener('click', openEditor));
    applyLanguage();
}

function capitalize(value) { return String(value || '').charAt(0).toUpperCase() + String(value || '').slice(1); }

function escapeHtml(value) {
    return String(value ?? '').replace(/[&<>'"]/g, (character) => ({
        '&': '&amp;', '<': '&lt;', '>': '&gt;', "'": '&#39;', '"': '&quot;'
    }[character]));
}

function getProblemById(problemId) {
    const normalizedId = String(problemId || '');
    return app.problems.find((problem) => String(problem.id) === normalizedId) || app.problems[0] || mockData.problems[0];
}

function renderEditorProblem(problem) {
    const current = problem || getProblemById();
    const title = document.getElementById('editor-title');
    const badge = document.querySelector('#editor-modal .problem-brief .pill');
    const problemTitle = document.querySelector('[data-editor-problem-title]');
    const description = document.querySelector('[data-editor-problem-description]');
    const editor = document.getElementById('code-editor');
    const modal = document.getElementById('editor-modal');
    if (!current || !modal) return;
    modal.dataset.problemId = current.id || '';
    if (title) title.textContent = localizeContent(current.title || 'Practice problem');
    if (badge) badge.textContent = String(current.topic || 'CODE').toUpperCase();
    if (problemTitle) problemTitle.textContent = localizeContent(current.title || 'Practice problem');
    if (description) description.textContent = localizeContent(current.description || 'Write a solution for this problem.');
    if (editor) editor.value = current.starter_code || `# ${localizeContent(current.title || 'Solve the problem')}\n\n# Write your solution here\n`;
    const output = document.getElementById('code-output');
    if (output) output.innerHTML = `<span class="output-label">${app.language === 'mn' ? 'ГАРАЛТ' : 'OUTPUT'}</span><code>${app.language === 'mn' ? 'Кодоо ажиллуулж үр дүнг энд харна.' : 'Run your code to see the output here.'}</code>`;
}


function localizeContent(value) {
    if (value && typeof value === 'object') return value[app.language] || value.en || Object.values(value)[0] || '';
    const source = String(value ?? '');
    const dictionary = app.language === 'mn' ? i18nPlainMn : {};
    return dictionary[source] || i18nTextTranslations[app.language]?.[source] || source;
}

async function openEditor(event) {
    const modal = document.getElementById('editor-modal');
    if (!modal) return;
    app.lastFocusedElement = document.activeElement;
    const problem = getProblemById(event?.currentTarget?.dataset.problemId);
    renderEditorProblem(problem);
    modal.classList.add('is-open');
    modal.setAttribute('aria-hidden', 'false');
    document.body.style.overflow = 'hidden';
    window.setTimeout(() => document.getElementById('code-editor')?.focus(), 50);

    setRuntimeStatus(backendEnabled ? 'connected' : 'ready');
    if (backendEnabled && app.dataAdapter === window.codehavenApiAdapter && problem?.id && window.codehavenApiAdapter.getProblem) {
        try {
            const liveProblem = await window.codehavenApiAdapter.getProblem(problem.id);
            if (modal.classList.contains('is-open') && String(modal.dataset.problemId) === String(problem.id)) {
                renderEditorProblem(liveProblem);
                document.getElementById('code-editor')?.focus();
            }
        } catch (error) {
            showToast(app.language === 'mn' ? 'Problem-ийн дэлгэрэнгүй мэдээлэл ачаалж чадсангүй.' : 'Problem details could not be loaded.', 'error');
        }
    }
}

function closeEditor() {
    const modal = document.getElementById('editor-modal');
    if (!modal?.classList.contains('is-open')) return;
    modal.classList.remove('is-open');
    modal.setAttribute('aria-hidden', 'true');
    document.body.style.overflow = '';
    app.lastFocusedElement?.focus?.();
}

function setRuntimeStatus(state) {
    const statusNode = document.getElementById('runtime-status');
    const label = statusNode?.querySelector('[data-runtime-status]');
    if (!statusNode || !label) return;
    const key = {
        ready: 'editor.runtime.ready',
        queued: 'editor.runtime.queued',
        running: 'editor.runtime.running',
        connected: 'editor.runtime.connected',
        offline: 'editor.runtime.offline',
    }[state] || 'editor.runtime.ready';
    statusNode.className = `runtime-status is-${state}`;
    label.textContent = i18nTranslations[app.language]?.[key] || key;
}

let editorRequestInFlight = false;

function setEditorRequestBusy(isBusy) {
    editorRequestInFlight = isBusy;
    const runButton = document.getElementById('run-code');
    const submitButton = document.getElementById('submit-code');
    [runButton, submitButton].forEach((button) => {
        if (!button) return;
        button.disabled = isBusy;
        button.setAttribute('aria-busy', String(isBusy));
    });
}

async function runCode() {
    const output = document.getElementById('code-output');
    const modal = document.getElementById('editor-modal');
    const editor = document.getElementById('code-editor');
    const problem = getProblemById(modal?.dataset.problemId);
    if (!output || editorRequestInFlight) return;
    const code = editor?.value?.trim();
    if (!code) {
        showToast(app.language === 'mn' ? 'Ажиллуулах кодоо оруулна уу.' : 'Enter code before running.', 'error');
        editor?.focus();
        return;
    }

    setEditorRequestBusy(true);
    try {
        if (backendEnabled && app.dataAdapter === window.codehavenApiAdapter && problem?.id && window.codehavenApiAdapter.runCode) {
            setRuntimeStatus('running');
            output.innerHTML = `<span class="output-label">RUNTIME</span><code class="output-pending">${app.language === 'mn' ? 'Sandbox дээр тест ажиллаж байна…' : 'Running tests in the sandbox…'}</code>`;
            const result = await window.codehavenApiAdapter.runCode({ problem_id: problem.id, code, language: problem.language || 'python' });
            const tests = result.test_results || [];
            const passed = Number(result.passed_tests || 0);
            const total = Number(result.total_tests || tests.length || 0);
            const detail = tests.map((test) => {
                const marker = test.passed ? '✓' : '×';
                const text = test.passed ? (test.actual_output || 'Passed') : (test.error || test.message || 'Output mismatch');
                return `${marker} Test ${test.test_number || ''}: ${escapeHtml(String(text))}`;
            }).join('<br>');
            output.innerHTML = `<span class="output-label">RUNTIME · ${passed}/${total}</span><code class="output-runtime">${detail || (app.language === 'mn' ? 'Тестийн үр дүн ирсэнгүй.' : 'No test output returned.')}</code>`;
            setRuntimeStatus('connected');
            showToast(app.language === 'mn' ? `${passed}/${total} тест амжилттай.` : `${passed}/${total} tests completed.`, passed === total ? 'success' : 'info');
            return;
        }

        setRuntimeStatus('running');
        const outputLabel = app.language === 'mn' ? 'DEMO ГАРАЛТ · 0.18с' : 'DEMO OUTPUT · 0.18s';
        const outputStatus = app.language === 'mn' ? 'Demo runner амжилттай дууслаа.' : 'Demo runner finished with exit code 0.';
        output.innerHTML = `<span class="output-label">${outputLabel}</span><code style="color:#75e6c5">[2, 4]<br><br>${outputStatus}</code>`;
        setRuntimeStatus('ready');
        showToast(app.language === 'mn' ? 'Demo код амжилттай ажиллалаа.' : 'Demo code ran successfully.', 'success');
    } catch (error) {
        setRuntimeStatus('offline');
        output.innerHTML = `<span class="output-label">RUNTIME ERROR</span><code class="output-error">${escapeHtml(error.message || 'Runtime execution is unavailable.')}</code>`;
        showToast(app.language === 'mn' ? 'Runtime одоогоор ажиллахгүй байна.' : 'Runtime execution is unavailable.', 'error');
    } finally {
        setEditorRequestBusy(false);
    }
}

async function submitCode() {
    const modal = document.getElementById('editor-modal');
    const editor = document.getElementById('code-editor');
    const problem = getProblemById(modal?.dataset.problemId);
    const code = editor?.value?.trim();
    if (!code) {
        showToast(app.language === 'mn' ? 'Илгээх кодоо оруулна уу.' : 'Enter code before submitting.', 'error');
        editor?.focus();
        return;
    }
    if (editorRequestInFlight) return;

    if (backendEnabled && app.dataAdapter === window.codehavenApiAdapter && problem?.id) {
        setEditorRequestBusy(true);
        try {
            setRuntimeStatus('queued');
            const result = await window.codehavenApiAdapter.submitCode({ problem_id: problem.id, code, language: problem.language || 'python' });
            const submissionId = result.submission?.id;
            showToast(app.language === 'mn' ? `Илгээлт хүлээгдэж байна (#${submissionId || ''}).` : `Submission queued (#${submissionId || 'pending'}).`, 'success');
            closeEditor();
            await refreshDataViews();
            if (submissionId) void pollSubmissionStatus(submissionId);
        } catch (error) {
            setRuntimeStatus('offline');
            showToast(app.language === 'mn' ? 'Илгээлтийг серверт хүргэж чадсангүй.' : (error.message || 'The submission could not be sent.'), 'error');
        } finally {
            setEditorRequestBusy(false);
        }
        return;
    }
    await runCode();
    showToast(app.language === 'mn' ? 'Demo шийдэл хадгалагдлаа.' : 'Demo solution saved to your practice history.', 'success');
    window.setTimeout(closeEditor, 500);
}

function notifySubmissionStatus(payload) {
    const submission = payload?.submission || payload || {};
    const status = submission.status || 'pending';
    if (status === 'pending') setRuntimeStatus('queued');
    if (status === 'running') setRuntimeStatus('running');
    if (status === 'accepted' || status === 'partial_accepted' || status === 'rejected') setRuntimeStatus('connected');
    if (status === 'error') setRuntimeStatus('offline');
    const score = submission.score == null ? '' : ` ${Number(submission.score).toFixed(0)}%`;
    const labels = {
        accepted: app.language === 'mn' ? `Зөв хариу${score}` : `Accepted${score}`,
        partial_accepted: app.language === 'mn' ? `Хэсэгчлэн зөв${score}` : `Partially accepted${score}`,
        rejected: app.language === 'mn' ? `Буруу хариу${score}` : `Rejected${score}`,
        error: app.language === 'mn' ? 'Үнэлгээний алдаа гарлаа.' : 'Evaluation failed.',
    };
    if (!['pending', 'running'].includes(status)) {
        showToast(labels[status] || (app.language === 'mn' ? `Илгээлтийн төлөв: ${status}` : `Submission status: ${status}`), status === 'accepted' ? 'success' : 'info');
    }
    return status;
}

async function pollSubmissionStatus(submissionId, maxAttempts = 12) {
    const adapter = window.codehavenApiAdapter;
    if (!adapter?.getSubmission) return null;

    if (adapter.streamSubmission) {
        try {
            let latest = null;
            let completed = false;
            await adapter.streamSubmission(submissionId, (payload) => {
                latest = payload;
                completed = !['pending', 'running'].includes(notifySubmissionStatus(payload));
            });
            if (latest && completed) {
                await refreshDataViews();
                return latest;
            }
        } catch (error) {
            // Fall back to short polling when an intermediary does not support SSE.
        }
    }

    for (let attempt = 0; attempt < maxAttempts; attempt += 1) {
        await new Promise((resolve) => window.setTimeout(resolve, 1500));
        try {
            const payload = await adapter.getSubmission(submissionId);
            const status = notifySubmissionStatus(payload);
            if (['pending', 'running'].includes(status)) continue;
            await refreshDataViews();
            return payload;
        } catch (error) {
            if (attempt === maxAttempts - 1) showToast(app.language === 'mn' ? 'Үнэлгээний төлөвийг шалгаж чадсангүй.' : 'Could not refresh submission status.', 'error');
        }
    }
    return null;
}

function toggleTheme() { setTheme(app.theme === 'light' ? 'dark' : 'light'); }

function setTheme(theme) {
    app.theme = theme;
    document.documentElement.dataset.theme = theme;
    localStorage.setItem('codehaven-theme', theme);
    document.querySelectorAll('[data-theme-choice]').forEach((button) => button.classList.toggle('is-active', button.dataset.themeChoice === theme));
    showToast(`${capitalize(theme)} theme enabled.`, 'info');
}

function showToast(message, type = 'info') {
    const region = document.getElementById('toast-region');
    if (!region) return;
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.textContent = message;
    region.appendChild(toast);
    window.setTimeout(() => toast.remove(), 3200);
}

window.codehaven = { app, showView, openEditor, closeEditor, apiAdapterContract };


const { translations: i18nTranslations, textTranslations: i18nTextTranslations, plainMn: i18nPlainMn } = window.CodehavenI18n;

function bindAuthentication() {
    document.querySelectorAll('[data-auth-tab]').forEach((tab) => {
        tab.addEventListener('click', () => setAuthMode(tab.dataset.authTab));
    });
    document.getElementById('show-otp-login')?.addEventListener('click', () => setAuthMode('otp-request'));
    document.getElementById('back-to-password-login')?.addEventListener('click', () => setAuthMode('login'));
    document.getElementById('google-auth')?.addEventListener('click', async () => {
        if (!backendEnabled || !window.codehavenApiAdapter) {
            showToast(app.language === 'mn' ? 'Google нэвтрэлт backend mode-д ажиллана.' : 'Google sign-in is available in backend mode.', 'info');
            return;
        }
        try {
            await window.codehavenApiAdapter.startGoogleLogin();
        } catch (error) {
            const serverError = error.payload?.error;
            showToast(app.language === 'mn' ? (serverError?.message_mn || 'Google-ээр нэвтрэх боломжгүй байна.') : (serverError?.message || error.message || 'Google sign-in is unavailable.'), 'error');
        }
    });
    document.getElementById('resend-otp')?.addEventListener('click', async () => {
        const email = document.querySelector('#otp-verify-form input[name="email"]')?.value;
        if (!email || !backendEnabled || !window.codehavenApiAdapter) return;
        try {
            await window.codehavenApiAdapter.requestOtp(email);
            showToast(app.language === 'mn' ? 'Шинэ код имэйл рүү илгээгдлээ.' : 'A new code was sent to your email.', 'success');
        } catch (error) {
            showToast(app.language === 'mn' ? 'Шинэ код илгээж чадсангүй.' : 'The new code could not be sent.', 'error');
        }
    });
    document.querySelectorAll('[data-auth-form]').forEach((form) => {
        form.addEventListener('submit', async (event) => {
            event.preventDefault();
            const fields = new FormData(form);
            const submit = form.querySelector('.auth-submit');
            if (submit) submit.disabled = true;
            try {
                if (form.id === 'otp-request-form') {
                    if (!backendEnabled || !window.codehavenApiAdapter) {
                        showToast(app.language === 'mn' ? 'OTP нэвтрэлт backend mode-д ажиллана.' : 'Email code sign-in is available in backend mode.', 'info');
                        return;
                    }
                    await window.codehavenApiAdapter.requestOtp(fields.get('email'));
                    document.querySelector('#otp-verify-form input[name="email"]').value = fields.get('email');
                    setAuthMode('otp-verify');
                    showToast(app.language === 'mn' ? 'Кодыг имэйлээ шалгана уу.' : 'Check your email for the six-digit code.', 'success');
                    return;
                }
                if (form.id === 'otp-verify-form') {
                    if (!backendEnabled || !window.codehavenApiAdapter) return;
                    app.user = await window.codehavenApiAdapter.verifyOtp(fields.get('email'), fields.get('code'));
                } else if (backendEnabled && window.codehavenApiAdapter) {
                    app.user = app.authMode === 'login'
                        ? await window.codehavenApiAdapter.login(fields.get('email'), fields.get('password'))
                        : await window.codehavenApiAdapter.register(fields.get('name'), fields.get('email'), fields.get('password'));
                } else {
                    showToast(app.authMode === 'login' ? (app.language === 'mn' ? 'Demo нэвтрэлт амжилттай.' : 'Demo sign in successful.') : (app.language === 'mn' ? 'Demo бүртгэл бэлэн боллоо.' : 'Demo account created.'), 'success');
                    window.setTimeout(() => showView('dashboard'), 500);
                    return;
                }
                sessionStorage.removeItem('codehaven-demo-mode');
                app.isDemoMode = false;
                app.dataAdapter = window.codehavenApiAdapter;
                hydrateUser(app.user);
                await refreshDataViews();
                showToast(app.language === 'mn' ? 'Амжилттай нэвтэрлээ.' : 'Signed in successfully.', 'success');
                window.setTimeout(() => showView('dashboard'), 500);
            } catch (error) {
                const serverError = error.payload?.error;
                const message = app.language === 'mn'
                    ? (serverError?.message_mn || 'Нэвтрэх үед алдаа гарлаа.')
                    : (serverError?.message || error.message || 'Authentication failed.');
                showToast(message, 'error');
            } finally {
                if (submit) submit.disabled = false;
            }
        });
    });
    document.querySelectorAll('.password-toggle').forEach((button) => {
        button.addEventListener('click', () => {
            const input = button.parentElement.querySelector('input');
            const showing = input.type === 'text';
            input.type = showing ? 'password' : 'text';
            button.textContent = showing ? (app.language === 'mn' ? 'Харах' : 'Show') : (app.language === 'mn' ? 'Нуух' : 'Hide');
            button.setAttribute('aria-label', showing ? (app.language === 'mn' ? 'Нууц үгийг харах' : 'Show password') : (app.language === 'mn' ? 'Нууц үгийг нуух' : 'Hide password'));
        });
    });
}

function setAuthMode(mode) {
    app.authMode = mode;
    const tabMode = mode === 'register' ? 'register' : 'login';
    document.querySelectorAll('[data-auth-tab]').forEach((tab) => {
        const active = tab.dataset.authTab === tabMode;
        tab.classList.toggle('is-active', active);
        tab.setAttribute('aria-selected', String(active));
    });
    document.querySelectorAll('[data-auth-form]').forEach((form) => form.classList.toggle('is-hidden', form.dataset.authForm !== mode));
    const title = document.getElementById('auth-title');
    const subtitle = document.getElementById('auth-subtitle');
    const loginFlow = mode === 'login' || mode === 'otp-request' || mode === 'otp-verify';
    if (title) title.textContent = loginFlow ? (app.language === 'mn' ? 'Тавтай морилно уу' : 'Welcome back') : (app.language === 'mn' ? 'Бүртгэл үүсгэх' : 'Create your account');
    if (subtitle) subtitle.dataset.i18n = mode === 'otp-request' ? 'auth.otp.subtitle' : mode === 'otp-verify' ? 'auth.otp.verifySubtitle' : loginFlow ? 'auth.login.subtitle' : 'auth.register.subtitle';
    applyLanguage();
}

function setLanguage(language) {
    if (!translations[language]) return;
    app.language = language;
    localStorage.setItem('codehaven-language', language);
    document.documentElement.lang = language;
    const languageSelect = document.getElementById('language-select');
    const settingsLanguageSelect = document.getElementById('settings-language-select');
    const landingLanguageSelect = document.getElementById('landing-language-select');
    if (languageSelect) languageSelect.value = language;
    if (settingsLanguageSelect) settingsLanguageSelect.value = language;
    if (landingLanguageSelect) landingLanguageSelect.value = language;
    applyLanguage();
    if (app.currentView === 'auth') setAuthMode(app.authMode);
    showToast(language === 'mn' ? 'Хэл Монгол хэлээр тохирлоо.' : 'Language set to English.', 'info');
}

function applyLanguage() {
    translatePlainTextNodes();
    const dictionary = i18nTranslations[app.language];
    document.querySelectorAll('[data-i18n]').forEach((node) => {
        const value = dictionary[node.dataset.i18n];
        if (value) node.textContent = value;
    });
    document.querySelectorAll('[data-i18n-placeholder]').forEach((node) => {
        const value = dictionary[node.dataset.i18nPlaceholder];
        if (value) node.placeholder = value;
    });
    document.querySelectorAll('[data-i18n-aria]').forEach((node) => {
        const value = dictionary[node.dataset.i18nAria];
        if (value) node.setAttribute('aria-label', value);
    });
    const editorModal = document.getElementById('editor-modal');
    if (editorModal?.classList.contains('is-open')) renderEditorProblem(getProblemById(editorModal.dataset.problemId));
    document.querySelectorAll('[data-i18n] input, [data-i18n] textarea').forEach((node) => {
        const value = dictionary[node.dataset.i18n];
        if (value) node.placeholder = value;
    });
    document.querySelectorAll('.password-toggle').forEach((button) => {
        const input = button.parentElement.querySelector('input');
        const showing = input?.type === 'text';
        button.textContent = showing ? (app.language === 'mn' ? 'Нуух' : 'Hide') : (app.language === 'mn' ? 'Харах' : 'Show');
    });
}


function translatePlainTextNodes() {
    const replacements = app.language === 'mn' ? plainMn : {};
    const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
    const nodes = [];
    let node;
    while ((node = walker.nextNode())) nodes.push(node);
    nodes.forEach((textNode) => {
        const parent = textNode.parentElement;
        if (!parent || parent.closest('[data-i18n]') || ['SCRIPT', 'STYLE', 'TEXTAREA', 'INPUT'].includes(parent.tagName)) return;
        const source = textNode.__codehavenSource || textNode.nodeValue.trim();
        if (!source) return;
        textNode.__codehavenSource = source;
        const replacement = replacements[source] || source;
        const leading = textNode.nodeValue.match(/^\s*/)?.[0] || '';
        const trailing = textNode.nodeValue.match(/\s*$/)?.[0] || '';
        textNode.nodeValue = `${leading}${replacement}${trailing}`;
    });
}


Object.assign(plainMn, {
    'View path': 'Замыг харах', 'Student': 'Суралцагч', '5 days': '5 өдөр', 'days': 'өдөр', 'h': 'ц', 'm': 'м', '12h 40m': '12ц 40м', '6h 25m': '6ц 25м',
    '68% complete': '68% дууссан', '82%': '82%', '68%': '68%', '55%': '55%', '38%': '38%',
    'Function scope': 'Function scope', 'Flatten a nested list': 'Давхар list-ийг задлах', 'Dictionary frequency counter': 'Dictionary-ийн давтамжийн тоолуур',
    'Even number filter': 'Тэгш тоо шүүх', 'Python': 'Python', 'Problem solving': 'Бодлого бодолт', 'Data structures': 'Өгөгдлийн бүтэц', 'Algorithms': 'Алгоритм', 'Strings': 'Тэмдэгт мөр', 'Stacks': 'Стек', 'Graphs': 'Граф', 'Web fundamentals': 'Web-ийн суурь',
    'Completed': 'Дууссан', 'In progress': 'Үргэлжилж байна', 'Next:': 'Дараагийнх:', 'List comprehension': 'List comprehension', 'Easy': 'Хялбар', 'Medium': 'Дунд', 'Hard': 'Хүнд', 'Solved': 'Бодсон', 'New': 'Шинэ', 'Solve': 'Бодох',
    '6 lessons · 42 min': '6 хичээл · 42 минут', '3 of 8 modules complete · 19 hours remaining': '8 модулиас 3 дууссан · 19 цаг үлдсэн',
    'Mon': 'Дав', 'Tue': 'Мяг', 'Wed': 'Лха', 'Thu': 'Пүр', 'Fri': 'Баа', 'Sat': 'Бям', 'Sun': 'Ням',
    'IN PROGRESS': 'ҮРГЭЛЖИЛЖ БАЙНА',
    'Python essentials': 'Python-ийн суурь', 'Variables, types and control flow · 6 lessons': 'Хувьсагч, төрөл болон удирдлагын урсгал · 6 хичээл',
    'Functions and clean code': 'Function болон цэвэр код', 'Scope, arguments and reusable patterns · 7 lessons': 'Хамрах хүрээ, аргумент болон дахин ашиглах хэв маяг · 7 хичээл',
    'Collections and comprehensions': 'Цуглуулга ба comprehension-ууд', 'Lists, dictionaries and expressive iteration · 8 lessons': 'Жагсаалт, dictionary болон илэрхий давталт · 8 хичээл',
    'Object-oriented thinking': 'Объектод чиглэсэн сэтгэлгээ', 'Classes, composition and maintainable systems · 9 lessons': 'Класс, зохиомж болон арчлахад хялбар систем · 9 хичээл',
    'Working with APIs': 'API-тай ажиллах', 'HTTP, JSON and your first useful integration · 6 lessons': 'HTTP, JSON болон анхны хэрэгтэй integration · 6 хичээл',
    'READY TO START': 'ЭХЛЭХЭД БЭЛЭН', 'Python foundations checkpoint': 'Python суурийн шалгах тест', 'Best score:': 'Хамгийн сайн оноо:', 'Begin checkpoint': 'Шалгах тест эхлүүлэх',
    'LOCKED': 'ТҮГЖЭЭТЭЙ', 'Data structures checkpoint': 'Өгөгдлийн бүтцийн шалгах тест', 'Complete the current module to unlock.': 'Одоогийн модулийг дуусгаснаар нээгдэнэ.', '68% of prerequisites complete': 'Шаардлагатай агуулгын 68% дууссан',
    'UPCOMING': 'УДАХГҮЙ', 'Web fundamentals project': 'Web-ийн суурийн төсөл', 'Build and ship a responsive profile page.': 'Responsive profile page бүтээж нийтэлнэ.', 'Unlocks in module 5': '5-р модульд нээгдэнэ',
    'Learning since June 2026': '2026 оны 6-р сараас суралцаж байна', 'PYTHON PATH': 'PYTHON-ИЙН ЗАМ', 'Light': 'Цайвар', 'Dark': 'Бараан', 'Set a comfortable reading size for code.': 'Код уншихад эвтэйхэн хэмжээ сонго.'
});
