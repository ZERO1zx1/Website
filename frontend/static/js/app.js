/* Codehaven frontend prototype. Replace mockAdapter with apiAdapter in the integration phase. */

const mockData = {
    user: { id: 7, name: 'Nara Sukh', initials: 'NS', role: 'Student', focus: 'Python & problem solving' },
    courses: [
        { id: 'python', icon: 'PY', level: { en: 'Beginner → Intermediate', mn: 'Анхан шат → Дунд шат' }, duration: { en: '6 weeks · 42 lessons', mn: '6 долоо хоног · 42 хичээл' }, title: { en: 'Python foundations', mn: 'Python-ийн суурь' }, description: { en: 'Learn Python syntax, data structures, functions, files, and practical problem solving.', mn: 'Python-ийн syntax, өгөгдлийн бүтэц, function, file болон бодит асуудал шийдэхийг сурна.' }, progress: 38, tags: ['python', 'programming', 'backend'], keywords: ['variables', 'functions', 'lists', 'dictionaries', 'oop'], modules: [{ number: '01', title: { en: 'Python essentials', mn: 'Python-ийн үндэс' }, meta: { en: 'Variables, types and control flow · 6 lessons', mn: 'Хувьсагч, төрөл, control flow · 6 хичээл' }, status: { en: 'Complete', mn: 'Дууссан' }, complete: true }, { number: '02', title: { en: 'Functions and clean code', mn: 'Function ба цэвэр код' }, meta: { en: 'Scope, arguments and reusable patterns · 7 lessons', mn: 'Scope, argument болон дахин ашиглах загвар · 7 хичээл' }, status: { en: 'Complete', mn: 'Дууссан' }, complete: true }, { number: '03', title: { en: 'Collections and comprehensions', mn: 'Collection ба comprehension' }, meta: { en: 'Lists, dictionaries and expressive iteration · 8 lessons', mn: 'List, dictionary болон iteration · 8 хичээл' }, status: { en: 'In progress', mn: 'Үргэлжилж байна' }, complete: false }] },
        { id: 'web', icon: 'WEB', level: { en: 'Beginner', mn: 'Анхан шат' }, duration: { en: '4 weeks · 28 lessons', mn: '4 долоо хоног · 28 хичээл' }, title: { en: 'HTML & CSS responsive web', mn: 'HTML ба CSS responsive web' }, description: { en: 'Build semantic, accessible, responsive pages with modern HTML and CSS.', mn: 'Modern HTML, CSS ашиглан semantic, хүртээмжтэй, responsive page бүтээнэ.' }, progress: 0, tags: ['html', 'css', 'frontend'], keywords: ['semantic html', 'flexbox', 'grid', 'responsive', 'accessibility'], modules: [{ number: '01', title: { en: 'HTML structure', mn: 'HTML бүтэц' }, meta: { en: 'Semantic elements, forms and accessible markup · 7 lessons', mn: 'Semantic element, form болон хүртээмжтэй markup · 7 хичээл' }, status: { en: 'Start here', mn: 'Эндээс эхэл' }, complete: false }, { number: '02', title: { en: 'CSS layout systems', mn: 'CSS layout system' }, meta: { en: 'Box model, Flexbox, Grid and responsive rules · 9 lessons', mn: 'Box model, Flexbox, Grid болон responsive дүрэм · 9 хичээл' }, status: { en: 'Locked', mn: 'Түгжээтэй' }, complete: false }] },
        { id: 'javascript', icon: 'JS', level: { en: 'Beginner → Intermediate', mn: 'Анхан шат → Дунд шат' }, duration: { en: '6 weeks · 36 lessons', mn: '6 долоо хоног · 36 хичээл' }, title: { en: 'JavaScript interactive web', mn: 'JavaScript интерактив web' }, description: { en: 'Make websites interactive with DOM, events, async requests, and browser APIs.', mn: 'DOM, event, async request болон browser API ашиглан website-ийг интерактив болгоно.' }, progress: 0, tags: ['javascript', 'frontend', 'web'], keywords: ['dom', 'events', 'fetch', 'async', 'modules'], modules: [{ number: '01', title: { en: 'JavaScript essentials', mn: 'JavaScript-ийн үндэс' }, meta: { en: 'Values, functions, arrays and objects · 8 lessons', mn: 'Утга, function, array болон object · 8 хичээл' }, status: { en: 'Start here', mn: 'Эндээс эхэл' }, complete: false }, { number: '02', title: { en: 'DOM and browser events', mn: 'DOM ба browser event' }, meta: { en: 'Build interactions that respond to real users · 8 lessons', mn: 'Бодит хэрэглэгчийн үйлдэлд хариулах interaction · 8 хичээл' }, status: { en: 'Locked', mn: 'Түгжээтэй' }, complete: false }] },
        { id: 'flask', icon: 'API', level: { en: 'Intermediate', mn: 'Дунд шат' }, duration: { en: '5 weeks · 30 lessons', mn: '5 долоо хоног · 30 хичээл' }, title: { en: 'Python Flask backend', mn: 'Python Flask backend' }, description: { en: 'Create APIs, authentication, roles, databases, and production-ready Flask services.', mn: 'API, authentication, role, database болон production-ready Flask service бүтээнэ.' }, progress: 0, tags: ['python', 'flask', 'backend', 'api'], keywords: ['flask', 'rest api', 'jwt', 'supabase', 'docker'], modules: [{ number: '01', title: { en: 'Flask API foundations', mn: 'Flask API-ийн үндэс' }, meta: { en: 'Routes, blueprints, validation and JSON responses · 8 lessons', mn: 'Route, blueprint, validation болон JSON response · 8 хичээл' }, status: { en: 'Start here', mn: 'Эндээс эхэл' }, complete: false }, { number: '02', title: { en: 'Auth and data services', mn: 'Auth ба data service' }, meta: { en: 'JWT, role permissions and Supabase persistence · 10 lessons', mn: 'JWT, role permission болон Supabase хадгалалт · 10 хичээл' }, status: { en: 'Locked', mn: 'Түгжээтэй' }, complete: false }] },
        { id: 'fullstack', icon: 'FS', level: { en: 'Intermediate → Advanced', mn: 'Дунд шат → Ахисан шат' }, duration: { en: '10 weeks · 60 lessons', mn: '10 долоо хоног · 60 хичээл' }, title: { en: 'Full-stack developer path', mn: 'Full-stack developer зам' }, description: { en: 'Ship a complete product from accessible frontend to secure backend and deployment.', mn: 'Хүртээмжтэй frontend-ээс найдвартай backend, deployment хүртэл бүрэн бүтээгдэхүүн бүтээнэ.' }, progress: 0, tags: ['full-stack', 'frontend', 'backend', 'deployment'], keywords: ['architecture', 'testing', 'security', 'docker', 'deployment'], modules: [{ number: '01', title: { en: 'Product architecture', mn: 'Бүтээгдэхүүний architecture' }, meta: { en: 'Design contracts across browser, API and database · 8 lessons', mn: 'Browser, API болон database хоорондын contract · 8 хичээл' }, status: { en: 'Start here', mn: 'Эндээс эхэл' }, complete: false }, { number: '02', title: { en: 'Ship and operate', mn: 'Бүтээж ажиллуулах' }, meta: { en: 'Testing, Docker, deployment and observability · 10 lessons', mn: 'Test, Docker, deployment болон observability · 10 хичээл' }, status: { en: 'Locked', mn: 'Түгжээтэй' }, complete: false }] }
    ],
    recentPractice: [
        { title: 'Function scope', category: 'Python foundations', status: 'Completed', score: '92%', icon: 'ƒ' },
        { title: 'Flatten a nested list', category: 'Problem solving', status: 'Completed', score: '84%', icon: '[]' },
        { title: 'Dictionary frequency counter', category: 'Data structures', status: 'In progress', score: '—', icon: '{}' }
    ],
    problems: [
        { id: 1, title: 'Even number filter', description: 'Practice list comprehensions by selecting values that match a condition.', difficulty: 'easy', topic: 'Python', progress: 'Solved', icon: '01' },
        { id: 2, title: 'First unique character', description: 'Use a frequency map to find the first character that appears once.', difficulty: 'medium', topic: 'Data structures', progress: 'New', icon: '02' },
        { id: 3, title: 'Merge overlapping ranges', description: 'Sort and combine ranges into the smallest non-overlapping set.', difficulty: 'hard', topic: 'Algorithms', progress: 'New', icon: '03' },
        { id: 4, title: 'Reverse words in place', description: 'Transform a sentence while preserving whitespace and word order rules.', difficulty: 'easy', topic: 'Strings', progress: 'Solved', icon: '04' },
        { id: 5, title: 'Balanced brackets', description: 'Build a stack-based checker for nested brackets and expressions.', difficulty: 'medium', topic: 'Stacks', progress: 'New', icon: '05' },
        { id: 6, title: 'Shortest path grid', description: 'Find the shortest route through a grid with blocked cells.', difficulty: 'hard', topic: 'Graphs', progress: 'New', icon: '06', tags: ['python', 'algorithms'], keywords: ['graphs', 'bfs', 'grid'] },
        { id: 7, title: 'Accessible profile card', description: 'Build semantic profile markup with labels, landmarks, and keyboard-friendly actions.', difficulty: 'easy', topic: 'HTML', progress: 'New', icon: '07', tags: ['html', 'frontend'], keywords: ['semantic html', 'aria', 'forms'] },
        { id: 8, title: 'Responsive dashboard layout', description: 'Use CSS Grid and Flexbox to create a dashboard that works on small screens.', difficulty: 'easy', topic: 'CSS', progress: 'New', icon: '08', tags: ['css', 'frontend'], keywords: ['grid', 'flexbox', 'responsive'] },
        { id: 9, title: 'Interactive theme toggle', description: 'Connect DOM events and local storage to build a persistent theme switcher.', difficulty: 'medium', topic: 'JavaScript', progress: 'New', icon: '09', tags: ['javascript', 'frontend'], keywords: ['dom', 'events', 'localstorage'] },
        { id: 10, title: 'Flask JSON API', description: 'Create a validated Flask endpoint that returns consistent JSON responses.', difficulty: 'medium', topic: 'Flask', progress: 'New', icon: '10', tags: ['python', 'flask', 'backend'], keywords: ['routes', 'json', 'validation'] },
        { id: 11, title: 'Role-aware full-stack route', description: 'Design a protected frontend and backend route for different user roles.', difficulty: 'hard', topic: 'Full-stack', progress: 'New', icon: '11', tags: ['full-stack', 'security'], keywords: ['auth', 'rbac', 'api'] },
        { id: 12, title: 'Ship with Docker', description: 'Package a tested web application and document its local production workflow.', difficulty: 'hard', topic: 'Deployment', progress: 'New', icon: '12', tags: ['full-stack', 'deployment'], keywords: ['docker', 'testing', 'deployment'] }
    ]
};

const mockAdapter = {
    async getUser() { return mockData.user; },
    async getDashboard() { return { recentPractice: mockData.recentPractice }; },
    async getLearningPath() { return { modules: mockData.courses[0].modules, courses: mockData.courses }; },
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
const hasBackendSession = Boolean(localStorage.getItem('codehaven-access-token') || hasOAuthSession);
const demoMode = sessionStorage.getItem('codehaven-demo-mode') === 'true';
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
    authMode: 'login'
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
            app.dataAdapter = mockAdapter;
        }
    }
    hydrateUser(app.user || { name: app.language === 'mn' ? 'Зочин' : 'Guest' });
    bindAuthentication();
    applyLanguage();
    if (app.user) await refreshDataViews();
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
    document.querySelectorAll('[data-theme-choice]').forEach((button) => {
        button.addEventListener('click', () => setTheme(button.dataset.themeChoice));
    });
    document.getElementById('mobile-menu')?.addEventListener('click', () => {
        document.querySelector('.sidebar')?.classList.toggle('is-open');
    });
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
            renderProblemCards(app.problems.filter((problem) => `${problem.title} ${problem.topic}`.toLowerCase().includes(query)));
        } else {
            renderProblemCards(app.problems);
        }
    });
    document.addEventListener('keydown', (event) => {
        if ((event.metaKey || event.ctrlKey) && event.key.toLowerCase() === 'k') {
            event.preventDefault();
            document.getElementById('global-search')?.focus();
        }
        if (event.key === 'Escape') closeEditor();
        if ((event.metaKey || event.ctrlKey) && event.key === 'Enter' && document.getElementById('editor-modal')?.classList.contains('is-open')) runCode();
    });
}

function hydrateUser(user) {
    document.querySelectorAll('#sidebar-user-name').forEach((node) => { node.textContent = user.name; });
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
    if (viewName === 'practice') void renderProblems().catch(() => renderProblemCards(app.problems));
    if (viewName === 'auth') document.querySelector('.auth-card input')?.focus();
    applyLanguage();
}

async function renderDashboard() {
    const dashboard = await app.dataAdapter.getDashboard();
    const container = document.getElementById('recent-practice-list');
    if (!container) return;
    container.innerHTML = dashboard.recentPractice.map((item) => `
        <div class="practice-row">
            <div class="practice-title"><span class="practice-symbol">${item.icon}</span><div><strong>${item.title}</strong><small>${item.category}</small></div></div>
            <span class="practice-meta"><span class="status-dot"></span>${item.status}</span>
            <span class="practice-score">${item.score}</span>
            <button class="text-button" data-open-editor>Review <span aria-hidden="true">→</span></button>
        </div>`).join('');
    container.querySelectorAll('[data-open-editor]').forEach((button) => button.addEventListener('click', openEditor));
    applyLanguage();
}

async function renderLearningPath() {
    const path = await app.dataAdapter.getLearningPath();
    app.courses = path.courses?.length ? path.courses : mockData.courses;
    renderCourseCards(app.courses);
    renderSelectedCourse(app.courses.find((course) => course.id === app.selectedCourseId) || app.courses[0]);
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
        <article class="course-card ${course.id === app.selectedCourseId ? 'is-selected' : ''}">
            <div class="course-card-top"><span class="course-icon">${course.icon}</span><span class="course-progress">${course.progress}%</span></div>
            <h3>${localizeContent(course.title)}</h3><p>${localizeContent(course.description)}</p>
            <div class="course-tags">${(course.tags || []).map((tag) => `<span class="tag-chip tag-chip-small">${tag}</span>`).join('')}</div>
            <div class="course-card-meta"><span>${localizeContent(course.level)}</span><span>${localizeContent(course.duration)}</span></div>
            <button class="text-button" data-select-course="${course.id}">${app.language === 'mn' ? 'Замыг харах' : 'View path'} <span aria-hidden="true">→</span></button>
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
        <article class="module-card ${module.complete ? 'is-complete' : ''}" data-open-lesson="${index}" tabindex="0" role="button">
            <span class="module-number">${module.complete ? '✓' : module.number}</span>
            <div class="module-content"><strong>${localizeContent(module.title)}</strong><span>${localizeContent(module.meta)}</span></div>
            <span class="module-status">${localizeContent(module.status)}</span>
        </article>`).join('');
    container.querySelectorAll('[data-open-lesson]').forEach((moduleCard) => {
        const open = () => openLessonPreview(course, Number(moduleCard.dataset.openLesson));
        moduleCard.addEventListener('click', open);
        moduleCard.addEventListener('keydown', (event) => { if (event.key === 'Enter' || event.key === ' ') { event.preventDefault(); open(); } });
    });
}

function openLessonPreview(course, moduleIndex) {
    const module = course?.modules?.[moduleIndex];
    if (!module) return;
    const preview = document.getElementById('lesson-preview');
    if (!preview) return;
    preview.dataset.courseId = course.id;
    preview.dataset.moduleIndex = String(moduleIndex);
    document.getElementById('lesson-preview-title').textContent = localizeContent(module.title);
    document.getElementById('lesson-preview-meta').textContent = localizeContent(module.meta);
    document.getElementById('lesson-preview-objective').textContent = localizeContent(course.description);
    document.getElementById('lesson-preview-keywords').innerHTML = (course.keywords || []).slice(0, 5).map((keyword) => `<span class="tag-chip tag-chip-small">${keyword}</span>`).join('');
    preview.classList.remove('is-hidden');
    preview.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

function completeLessonPreview() {
    const preview = document.getElementById('lesson-preview');
    const course = app.courses.find((item) => item.id === preview?.dataset.courseId);
    const module = course?.modules?.[Number(preview?.dataset.moduleIndex)];
    if (!module) return;
    module.complete = true;
    module.status = { en: 'Complete', mn: 'Дууссан' };
    renderCourseCards(app.courses);
    renderSelectedCourse(course);
    preview.classList.add('is-hidden');
    showToast(app.language === 'mn' ? 'Хичээл дууслаа. Ахиц хадгалагдлаа.' : 'Lesson complete. Progress saved in demo mode.', 'success');
}

async function renderProblems() {
    const result = await app.dataAdapter.getProblems();
    app.problems = result.problems || [];
    renderProblemCards(app.problems);
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

function renderProblemCards(problems) {
    const container = document.getElementById('problem-grid');
    if (!container) return;
    const filtered = app.activeFilter === 'all' ? problems : problems.filter((problem) => problem.difficulty === app.activeFilter);
    if (!filtered.length) {
        container.innerHTML = '<div class="panel" style="grid-column:1/-1;padding:2rem;color:var(--color-text-secondary)">No problems match this filter yet.</div>';
        return;
    }
    container.innerHTML = filtered.map((problem) => `
        <article class="problem-card">
            <div class="problem-card-top"><span class="pill ${problem.progress === 'Solved' ? 'pill-teal' : 'pill-muted'}">${localizeContent(problem.progress)}</span><span class="practice-symbol">${problem.icon}</span></div>
            <h3>${localizeContent(problem.title)}</h3><p>${localizeContent(problem.description)}</p>
            <div class="problem-tags">${(problem.tags || []).map((tag) => `<span class="tag-chip tag-chip-small">${tag}</span>`).join('')}</div>
            <div class="problem-card-footer"><span class="difficulty ${problem.difficulty}">${localizeContent(capitalize(problem.difficulty))} · ${localizeContent(problem.topic)}</span><button class="text-button" data-open-editor>${localizeContent('Solve')} <span aria-hidden="true">→</span></button></div>
        </article>`).join('');
    container.querySelectorAll('[data-open-editor]').forEach((button) => button.addEventListener('click', openEditor));
    applyLanguage();
}

function capitalize(value) { return value.charAt(0).toUpperCase() + value.slice(1); }

function localizeContent(value) {
    if (value && typeof value === 'object') return value[app.language] || value.en || Object.values(value)[0] || '';
    const source = String(value ?? '');
    const dictionary = app.language === 'mn' ? plainMn : {};
    return dictionary[source] || textTranslations[app.language]?.[source] || source;
}

function openEditor() {
    const modal = document.getElementById('editor-modal');
    if (!modal) return;
    app.lastFocusedElement = document.activeElement;
    modal.classList.add('is-open');
    modal.setAttribute('aria-hidden', 'false');
    document.body.style.overflow = 'hidden';
    window.setTimeout(() => document.getElementById('code-editor')?.focus(), 50);
}

function closeEditor() {
    const modal = document.getElementById('editor-modal');
    if (!modal?.classList.contains('is-open')) return;
    modal.classList.remove('is-open');
    modal.setAttribute('aria-hidden', 'true');
    document.body.style.overflow = '';
    app.lastFocusedElement?.focus?.();
}

function runCode() {
    const output = document.getElementById('code-output');
    if (!output) return;
    const outputLabel = app.language === 'mn' ? 'ГАРАЛТ · 0.18с' : 'OUTPUT · 0.18s';
    const outputStatus = app.language === 'mn' ? 'Процесс амжилттай дууслаа.' : 'Process finished with exit code 0.';
    output.innerHTML = `<span class="output-label">${outputLabel}</span><code style="color:#75e6c5">[2, 4]<br><br>${outputStatus}</code>`;
    showToast(app.language === 'mn' ? 'Код амжилттай ажиллалаа. Сайн байна.' : 'Code ran successfully. Nice work.', 'success');
}

function submitCode() {
    runCode();
    showToast(app.language === 'mn' ? 'Шийдэл дадлагын түүхэнд хадгалагдлаа.' : 'Solution saved to your practice history.', 'success');
    window.setTimeout(closeEditor, 500);
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


const translations = {
    en: {
        'landing.signin': 'Sign in',
        'landing.getStarted': 'Get started',
        'landing.kicker': 'PRACTICAL LEARNING, BUILT AROUND YOU',
        'landing.title': 'Build real coding confidence, one clear step at a time.',
        'landing.description': 'Learn the fundamentals, practice with feedback, and follow a path that turns curiosity into useful skills.',
        'landing.start': 'Start learning free',
        'landing.returning': 'I already have an account',
        'landing.proof1': 'Structured learning paths',
        'landing.proof2': 'Practice with useful feedback',
        'landing.proof3': 'Progress you can understand',
        'landing.live': 'YOUR NEXT STEP',
        'landing.cardTitle': 'Functions and clean code',
        'landing.cardDescription': 'A focused lesson, a small challenge, and a clear sense of progress.',
        'landing.complete': '68% complete',
        'landing.mastery': 'overall mastery',
        'landing.feature1Title': 'Learn with direction',
        'landing.feature1Text': 'A calm path from foundations to practical programming.',
        'landing.feature2Title': 'Practice without pressure',
        'landing.feature2Text': 'Small problems, visible feedback, and room to try again.',
        'landing.feature3Title': 'See your progress',
        'landing.feature3Text': 'Mastery and activity views that make improvement tangible.',
        'curriculum.eyebrow': 'YOUR CURRICULUM',
        'curriculum.title': 'Learning paths',
        'curriculum.description': 'Choose a technology, follow the sequence, and build practical confidence.',
        'curriculum.searchPlaceholder': 'Search courses, tags, keywords...',
        'curriculum.all': 'All',
        'curriculum.selected': 'SELECTED PATH',
        'lesson.previewKicker': 'LESSON PREVIEW',
        'lesson.objective': 'What you will learn',
        'lesson.keywords': 'Keywords',
        'lesson.markComplete': 'Mark lesson complete',
        'auth.preview': 'Preview login / register',
        'auth.kicker': 'YOUR LEARNING SPACE',
        'auth.welcome': 'Build skills that move with you.',
        'auth.intro': 'A focused workspace for learning, practicing and shipping better code.',
        'auth.benefit.progress': 'See progress that makes sense',
        'auth.benefit.practice': 'Practice with feedback, not pressure',
        'auth.benefit.path': 'Follow a path built around your goals',
        'auth.secure': 'SECURE ACCESS',
        'auth.login.subtitle': 'Sign in to continue your learning journey.',
        'auth.register.subtitle': 'Create your account and start learning today.',
        'auth.login.tab': 'Sign in',
        'auth.register.tab': 'Create account',
        'auth.email': 'Email address',
        'auth.password': 'Password',
        'auth.name': 'Full name',
        'auth.remember': 'Remember me',
        'auth.forgot': 'Forgot password?',
        'auth.login.submit': 'Sign in',
        'auth.register.submit': 'Create account',
        'auth.register.password.placeholder': 'Create a password',
        'auth.email.placeholder': 'you@example.com',
        'auth.password.placeholder': 'Enter your password',
        'auth.name.placeholder': 'Your full name',
        'auth.terms': 'I agree to the Terms of Service and Privacy Policy.',
        'auth.or': 'or continue with',
        'auth.useCode': 'Use an email code instead',
        'auth.usePassword': 'Use password instead',
        'auth.otp.subtitle': 'We will send a six-digit code to your email.',
        'auth.otp.verifySubtitle': 'Enter the six-digit code from your email.',
        'auth.otp.send': 'Send login code',
        'auth.otp.code': 'Email code',
        'auth.otp.placeholder': '000000',
        'auth.otp.verify': 'Verify and sign in',
        'auth.otp.resend': 'Send a new code',
        'auth.google': 'Continue with Google',
        'auth.demo': 'Frontend preview only.',
        'auth.demo.continue': 'Continue as demo learner',
        'editor.workspace': 'Practice workspace',
        'editor.title': 'List comprehensions',
        'editor.problem.title': 'Transform a list of values',
        'editor.problem.description': 'Write a function that returns only the even numbers from a list. Keep the original order.',
        'editor.example': 'Example',
        'editor.hint': 'Need a hint?',
        'editor.reveal': 'Reveal step 1 →',
        'editor.autosaved': 'Autosaved',
        'editor.output': 'OUTPUT',
        'editor.emptyOutput': 'Run your code to see the output here.',
        'editor.toRun': 'to run',
        'editor.save': 'Save for later',
        'editor.run': 'Run code',
        'editor.submit': 'Submit solution',
        'editor.close': 'Close editor'
    },
    mn: {
        'landing.signin': 'Нэвтрэх',
        'landing.getStarted': 'Эхлэх',
        'landing.kicker': 'ТАНД ТОХИРСОН ПРАКТИК СУРАЛЦАХ ОРЧИН',
        'landing.title': 'Алхам бүрээр бодит код бичих итгэлээ бүтээ.',
        'landing.description': 'Суурь ойлголтоо эзэмшиж, feedback-тэй дадлага хийж, сонирхлоо хэрэгтэй ур чадвар болгон хөгжүүлээрэй.',
        'landing.start': 'Үнэгүй суралцаж эхлэх',
        'landing.returning': 'Би бүртгэлтэй',
        'landing.proof1': 'Бүтэцтэй суралцах зам',
        'landing.proof2': 'Хэрэгтэй feedback-тэй дадлага',
        'landing.proof3': 'Ойлгомжтой ахиц дэвшил',
        'landing.live': 'ТАНЫ ДАРААГИЙН АЛХАМ',
        'landing.cardTitle': 'Function ба цэвэр код',
        'landing.cardDescription': 'Төвлөрсөн хичээл, жижиг бодлого, ойлгомжтой ахиц.',
        'landing.complete': '68% дууссан',
        'landing.mastery': 'нийт эзэмшилт',
        'landing.feature1Title': 'Чиглэлтэй суралц',
        'landing.feature1Text': 'Сууриас практик programming хүртэл тайван, бүтэцтэй зам.',
        'landing.feature2Title': 'Дарамтгүй дадлага хий',
        'landing.feature2Text': 'Жижиг бодлого, харагдах feedback, дахин оролдох боломж.',
        'landing.feature3Title': 'Ахицаа хараарай',
        'landing.feature3Text': 'Mastery болон идэвхийн ойлгомжтой мэдээллээр хөгжлөө хэмж.',
        'curriculum.eyebrow': 'ТАНЫ СУРАЛЦАХ ЗАМ',
        'curriculum.title': 'Суралцах замууд',
        'curriculum.description': 'Технологио сонгож, дарааллаа дагаж, практик ур чадвараа хөгжүүлээрэй.',
        'curriculum.searchPlaceholder': 'Course, tag, keyword хайх...',
        'curriculum.all': 'Бүгд',
        'curriculum.selected': 'СОНГОСОН ЗАМ',
        'lesson.previewKicker': 'ХИЧЭЭЛИЙН ТОВЧООН',
        'lesson.objective': 'Та юу сурах вэ?',
        'lesson.keywords': 'Түлхүүр үгс',
        'lesson.markComplete': 'Хичээлийг дууссан гэж тэмдэглэх',
        'auth.preview': 'Нэвтрэх / бүртгүүлэх харах',
        'auth.kicker': 'ТАНЫ СУРАЛЦАХ ОРЧИН',
        'auth.welcome': 'Өөртэй тань хамт хөгжих ур чадвар бүтээ.',
        'auth.intro': 'Код бичих, дадлага хийх, бодит бүтээгдэхүүн бүтээхэд төвлөрсөн орчин.',
        'auth.benefit.progress': 'Ойлгомжтой ахиц дэвшлээ хар',
        'auth.benefit.practice': 'Дарамтгүй, хэрэгтэй feedback-тэй дадлага хий',
        'auth.benefit.path': 'Зорилгод тань тохирсон замаар суралц',
        'auth.secure': 'АЮУЛГҮЙ НЭВТРЭЛТ',
        'auth.login.subtitle': 'Суралцах замаа үргэлжлүүлэхийн тулд нэвтэрнэ үү.',
        'auth.register.subtitle': 'Бүртгэл үүсгээд өнөөдөр суралцаж эхлээрэй.',
        'auth.login.tab': 'Нэвтрэх',
        'auth.register.tab': 'Бүртгэл үүсгэх',
        'auth.email': 'Имэйл хаяг',
        'auth.password': 'Нууц үг',
        'auth.name': 'Бүтэн нэр',
        'auth.remember': 'Намайг сана',
        'auth.forgot': 'Нууц үгээ мартсан уу?',
        'auth.login.submit': 'Нэвтрэх',
        'auth.register.submit': 'Бүртгэл үүсгэх',
        'auth.register.password.placeholder': 'Нууц үг үүсгэх',
        'auth.email.placeholder': 'you@example.com',
        'auth.password.placeholder': 'Нууц үгээ оруулна уу',
        'auth.name.placeholder': 'Бүтэн нэрээ оруулна уу',
        'auth.terms': 'Үйлчилгээний нөхцөл болон Нууцлалын бодлогыг зөвшөөрч байна.',
        'auth.or': 'эсвэл дараахаар үргэлжлүүлэх',
        'auth.useCode': 'Имэйлийн кодоор нэвтрэх',
        'auth.usePassword': 'Нууц үгээр нэвтрэх',
        'auth.otp.subtitle': 'Бид таны имэйл рүү зургаан оронтой код илгээнэ.',
        'auth.otp.verifySubtitle': 'Имэйлээр ирсэн зургаан оронтой кодыг оруулна уу.',
        'auth.otp.send': 'Нэвтрэх код илгээх',
        'auth.otp.code': 'Имэйлийн код',
        'auth.otp.placeholder': '000000',
        'auth.otp.verify': 'Баталгаажуулаад нэвтрэх',
        'auth.otp.resend': 'Шинэ код илгээх',
        'auth.google': 'Google-ээр үргэлжлүүлэх',
        'auth.demo': 'Зөвхөн frontend preview.',
        'auth.demo.continue': 'Demo хэрэглэгчээр үргэлжлүүлэх',
        'editor.workspace': 'Дадлагын орчин',
        'editor.title': 'List comprehension',
        'editor.problem.title': 'Жагсаалтын утгуудыг хувиргах',
        'editor.problem.description': 'Жагсаалтаас зөвхөн тэгш тоонуудыг буцаах function бичнэ үү. Анхны дарааллыг хадгална.',
        'editor.example': 'Жишээ',
        'editor.hint': 'Санамж хэрэгтэй юу?',
        'editor.reveal': '1-р алхмыг харах →',
        'editor.autosaved': 'Автоматаар хадгалсан',
        'editor.output': 'ГАРАЛТ',
        'editor.emptyOutput': 'Кодоо ажиллуулбал үр дүн энд харагдана.',
        'editor.toRun': 'ажиллуулах',
        'editor.save': 'Дараа хийхээр хадгалах',
        'editor.run': 'Код ажиллуулах',
        'editor.submit': 'Шийдэл илгээх',
        'editor.close': 'Editor хаах'
    }
};

const textTranslations = {
    en: {
        'View path': 'View path', 'Student': 'Student', 'Overview': 'Overview', 'Learning path': 'Learning path',
        'Practice': 'Practice', 'Assessments': 'Assessments', 'Profile': 'Profile', 'Preferences': 'Preferences',
        'Tuesday, August 13, 2026': 'Tuesday, August 13, 2026', 'Keep your momentum, Nara.': 'Keep your momentum, Nara.',
        'Learning activity': 'Learning activity', 'Hours studied': 'Hours studied', 'Skill map': 'Skill map',
        'Where you’re growing': 'Where you’re growing', 'Recent practice': 'Recent practice', 'Review': 'Review',
        'Solve': 'Solve', 'Sign in': 'Sign in', 'Create account': 'Create account'
    },
    mn: {
        'View path': 'Замыг харах', 'Student': 'Суралцагч', 'Overview': 'Тойм', 'Learning path': 'Суралцах зам',
        'Practice': 'Дадлага', 'Assessments': 'Шалгалт', 'Profile': 'Профайл', 'Preferences': 'Тохиргоо',
        'Tuesday, August 13, 2026': '2026 оны 8-р сарын 13, Мягмар', 'Keep your momentum, Nara.': 'Ахицын эрчээ үргэлжлүүлээрэй, Нара.',
        'Learning activity': 'Суралцсан идэвх', 'Hours studied': 'Суралцсан цаг', 'Skill map': 'Ур чадварын зураг',
        'Where you’re growing': 'Таны хөгжиж буй ур чадвар', 'Recent practice': 'Сүүлийн дадлага', 'Review': 'Дахин харах',
        'Solve': 'Бодох', 'Sign in': 'Нэвтрэх', 'Create account': 'Бүртгэл үүсгэх'
    }
};

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
    document.getElementById('continue-demo')?.addEventListener('click', async () => {
        sessionStorage.setItem('codehaven-demo-mode', 'true');
        app.isDemoMode = true;
        app.dataAdapter = mockAdapter;
        app.user = mockData.user;
        hydrateUser(app.user);
        await refreshDataViews();
        showView('dashboard');
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
    const dictionary = translations[app.language];
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


const plainMn = {
    'Student workspace': 'Суралцагчийн орчин', 'Your space': 'Таны орчин', 'UP NEXT': 'ДАРААГИЙН АЛХАМ',
    'Build your first API': 'Анхны API-гаа бүтээ', '6 lessons · 42 min': '6 хичээл · 42 минут',
    'Overview': 'Тойм', 'Learning': 'Суралцах', 'Practice': 'Дадлага', 'Assessments': 'Шалгалт',
    'Profile': 'Профайл', 'Preferences': 'Тохиргоо', 'Dashboard': 'Хянах самбар', 'Learning path': 'Суралцах зам',
    'Practice library': 'Дадлагын сан', 'Account': 'Бүртгэл', 'Sign in': 'Нэвтрэх',
    'Tuesday, August 13, 2026': '2026 оны 8-р сарын 13, Мягмар', 'Keep your momentum, Nara.': 'Ахицын эрчээ үргэлжлүүлээрэй, Нара.',
    'Small, consistent practice compounds into real confidence.': 'Бага боловч тогтмол дадлага бодит итгэл болж хуримтлагдана.',
    'View weekly review': 'Долоо хоногийн тойм харах', 'Overall mastery': 'Нийт эзэмшил', 'Problems solved': 'Бодсон бодлого',
    'Study time': 'Суралцсан цаг', 'Current streak': 'Одоогийн дараалал', 'from last month': 'өнгөрсөн сараас',
    'this week': 'энэ долоо хоногт', 'On track': 'Төлөвлөгөөний дагуу', 'of 15h goal': '15 цагийн зорилгоос',
    'Best: 12 days': 'Хамгийн их: 12 өдөр', 'Continue learning': 'Суралцахаа үргэлжлүүлэх', 'complete': 'дууссан',
    'Python foundations': 'Python-ийн суурь', 'Functions, data structures and the patterns you need to write clean, useful programs.': 'Цэвэр, хэрэгтэй програм бичихэд шаардлагатай function ба data structure-ууд.',
    'Next:': 'Дараагийнх:', 'List comprehensions': 'List comprehension', 'Resume lesson': 'Хичээлээ үргэлжлүүлэх',
    'Today’s focus': 'Өнөөдрийн төвлөрөл', 'One clear next step': 'Нэг тодорхой дараагийн алхам',
    'Review function scope': 'Function scope-оо давтах', 'Completed 10 min ago': '10 минутын өмнө дуусгасан',
    'Finish list comprehensions': 'List comprehension-оо дуусгах', 'Estimated 18 min': 'Ойролцоогоор 18 минут',
    'Try one medium problem': 'Дунд түвшний нэг бодлого бодох', 'Suggested for your level': 'Таны түвшинд санал болгосон',
    'Learning activity': 'Суралцсан идэвх', 'Hours studied': 'Суралцсан цаг', 'Last 7 days': 'Сүүлийн 7 өдөр',
    'vs. previous week': 'өмнөх долоо хоногтой харьцуулахад', 'Skill map': 'Ур чадварын зураг',
    'Where you’re growing': 'Таны хөгжиж буй ур чадвар', 'Advanced': 'Ахисан', 'Intermediate': 'Дунд', 'Starter': 'Эхлэл',
    'View full skill map': 'Бүх ур чадварыг харах', 'Pick up where you left off': 'Үргэлжлүүлэн хийх',
    'Recent practice': 'Сүүлийн дадлага', 'View all practice': 'Бүх дадлагыг харах', 'Review': 'Дахин харах',
    'Your curriculum': 'Таны сургалтын хөтөлбөр', 'A practical sequence that turns concepts into working software.': 'Ойлголтыг ажилладаг програм болгох практик дараалал.',
    'Python developer path': 'Python хөгжүүлэгчийн зам', '3 of 8 modules complete · 19 hours remaining': '8 модулиас 3 дууссан · 19 цаг үлдсэн',
    'Complete': 'Дууссан', 'In progress': 'Үргэлжилж байна', 'Up next': 'Дараагийн алхам', 'Locked': 'Түгжээтэй',
    'Build fluency': 'Чадвараа батжуулах', 'Choose a challenge that matches your energy today.': 'Өнөөдрийн эрч хүчид тохирох бодлогыг сонгоорой.',
    'Quick practice': 'Шуурхай дадлага', 'All problems': 'Бүх бодлого', 'Easy': 'Хялбар', 'Medium': 'Дунд', 'Hard': 'Хүнд',
    'Newest first': 'Шинэ нь эхэндээ', 'Solved': 'Бодсон', 'New': 'Шинэ', 'Practice list comprehensions by selecting values that match a condition.': 'Нөхцөл хангасан утгуудыг сонгож list comprehension дадлага хий.',
    'First unique character': 'Анхны давтагдаагүй тэмдэгт', 'Use a frequency map to find the first character that appears once.': 'Нэг л удаа гарсан эхний тэмдэгтийг frequency map ашиглан ол.',
    'Merge overlapping ranges': 'Давхардсан мужуудыг нэгтгэх', 'Sort and combine ranges into the smallest non-overlapping set.': 'Мужуудыг эрэмбэлж, хамгийн бага давхардалгүй багц болгон нэгтгэ.',
    'Reverse words in place': 'Үгсийг байрлалд нь урвуулах', 'Transform a sentence while preserving whitespace and word order rules.': 'Өгүүлбэрийг whitespace болон үгийн дарааллын дүрмийг хадгалан өөрчил.',
    'Balanced brackets': 'Тэнцвэртэй хаалт', 'Build a stack-based checker for nested brackets and expressions.': 'Давхар хаалт, илэрхийллийг шалгах stack суурьтай checker бүтээ.',
    'Shortest path grid': 'Grid дээрх хамгийн богино зам', 'Find the shortest route through a grid with blocked cells.': 'Хаалттай нүднүүдтэй grid дээр хамгийн богино замыг ол.',
    'Measure progress': 'Ахиц хэмжих', 'Low-pressure checkpoints to see what is sticking.': 'Юу тогтож үлдсэнийг дарамтгүй шалгах цэгүүд.',
    'Ready to start': 'Эхлэхэд бэлэн', 'Python foundations checkpoint': 'Python суурийн шалгах тест',
    '12 questions · 20 minutes · 3 attempts available': '12 асуулт · 20 минут · 3 оролдлого', 'Begin checkpoint': 'Шалгах тест эхлүүлэх',
    'Your account': 'Таны бүртгэл', 'Keep your learning preferences and goals in one place.': 'Суралцах тохиргоо болон зорилгоо нэг дор удирдана.',
    'Edit profile': 'Профайл засах', 'Focus': 'Төвлөрөл', 'Weekly goal': 'Долоо хоногийн зорилго', 'Current level': 'Одоогийн түвшин',
    'Make it yours': 'Өөртөө тохируулах', 'Weekly reminders': 'Долоо хоногийн сануулга', 'Focus mode': 'Төвлөрсөн горим',
    'A gentle nudge when your goal is waiting.': 'Зорилго тань хүлээж байхад зөөлөн сануулна.', 'Reduce visual noise while solving.': 'Бодлого бодох үед илүүдэл мэдээллийг багасгана.',
    'Workspace': 'Ажлын орчин', 'Tune the workspace for your best learning sessions.': 'Хамгийн сайн суралцахад тохируулан ажлын орчноо өөрчил.',
    'Color theme': 'Өнгөний theme', 'Choose the environment that feels easiest on your eyes.': 'Нүдэнд хамгийн эвтэйхэн орчныг сонго.',
    'Language': 'Хэл', 'Choose the language for the learning workspace.': 'Суралцах орчны хэлээ сонго.', 'English': 'Англи хэл', 'Монгол': 'Монгол хэл',
    'Editor font size': 'Editor-ийн үсгийн хэмжээ', 'Code ran successfully. Nice work.': 'Code амжилттай ажиллалаа. Сайн байна.',
    'Solution saved to your practice history.': 'Шийдэл дадлагын түүхэнд хадгалагдлаа.'
};

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
