/* Codehaven frontend prototype. Replace mockAdapter with apiAdapter in the integration phase. */

const mockData = {
    user: { id: 7, name: 'Nara Sukh', initials: 'NS', role: 'Student', focus: 'Python & problem solving' },
    recentPractice: [
        { title: 'Function scope', category: 'Python foundations', status: 'Completed', score: '92%', icon: 'ƒ' },
        { title: 'Flatten a nested list', category: 'Problem solving', status: 'Completed', score: '84%', icon: '[]' },
        { title: 'Dictionary frequency counter', category: 'Data structures', status: 'In progress', score: '—', icon: '{}' }
    ],
    modules: [
        { number: '01', title: 'Python essentials', meta: 'Variables, types and control flow · 6 lessons', status: 'Complete', complete: true },
        { number: '02', title: 'Functions and clean code', meta: 'Scope, arguments and reusable patterns · 7 lessons', status: 'Complete', complete: true },
        { number: '03', title: 'Collections and comprehensions', meta: 'Lists, dictionaries and expressive iteration · 8 lessons', status: 'In progress', complete: false },
        { number: '04', title: 'Object-oriented thinking', meta: 'Classes, composition and maintainable systems · 9 lessons', status: 'Up next', complete: false },
        { number: '05', title: 'Working with APIs', meta: 'HTTP, JSON and your first useful integration · 6 lessons', status: 'Locked', complete: false }
    ],
    problems: [
        { id: 1, title: 'Even number filter', description: 'Practice list comprehensions by selecting values that match a condition.', difficulty: 'easy', topic: 'Python', progress: 'Solved', icon: '01' },
        { id: 2, title: 'First unique character', description: 'Use a frequency map to find the first character that appears once.', difficulty: 'medium', topic: 'Data structures', progress: 'New', icon: '02' },
        { id: 3, title: 'Merge overlapping ranges', description: 'Sort and combine ranges into the smallest non-overlapping set.', difficulty: 'hard', topic: 'Algorithms', progress: 'New', icon: '03' },
        { id: 4, title: 'Reverse words in place', description: 'Transform a sentence while preserving whitespace and word order rules.', difficulty: 'easy', topic: 'Strings', progress: 'Solved', icon: '04' },
        { id: 5, title: 'Balanced brackets', description: 'Build a stack-based checker for nested brackets and expressions.', difficulty: 'medium', topic: 'Stacks', progress: 'New', icon: '05' },
        { id: 6, title: 'Shortest path grid', description: 'Find the shortest route through a grid with blocked cells.', difficulty: 'hard', topic: 'Graphs', progress: 'New', icon: '06' }
    ]
};

const mockAdapter = {
    async getUser() { return mockData.user; },
    async getDashboard() { return { recentPractice: mockData.recentPractice }; },
    async getLearningPath() { return { modules: mockData.modules }; },
    async getProblems() { return { problems: mockData.problems }; }
};

// This interface matches the backend contract planned for phase two.
const apiAdapterContract = {
    getUser: 'GET /api/auth/me',
    getDashboard: 'GET /api/analytics/mastery/:userId',
    getLearningPath: 'GET /api/courses/:courseId',
    getProblems: 'GET /api/problems',
    submitCode: 'POST /api/submissions'
};

const app = {
    dataAdapter: mockAdapter,
    user: null,
    currentView: 'dashboard',
    activeFilter: 'all',
    lastFocusedElement: null,
    theme: localStorage.getItem('codehaven-theme') || 'light'
};

const viewLabels = {
    dashboard: ['Overview', 'Dashboard'],
    learn: ['Learning', 'Learning path'],
    practice: ['Practice', 'Practice library'],
    assessments: ['Assessments', 'Assessments'],
    profile: ['Your space', 'Profile'],
    settings: ['Your space', 'Preferences']
};

window.addEventListener('DOMContentLoaded', initializeApp);

async function initializeApp() {
    document.documentElement.dataset.theme = app.theme;
    bindNavigation();
    bindInteractions();
    app.user = await app.dataAdapter.getUser();
    hydrateUser(app.user);
    await Promise.all([renderDashboard(), renderLearningPath(), renderProblems()]);
    showView('dashboard');
}

function bindNavigation() {
    document.querySelectorAll('[data-view]').forEach((control) => {
        control.addEventListener('click', () => showView(control.dataset.view));
    });
}

function bindInteractions() {
    document.getElementById('theme-toggle')?.addEventListener('click', toggleTheme);
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
        renderProblemCards(mockData.problems);
    }));
    document.getElementById('global-search')?.addEventListener('input', (event) => {
        const query = event.target.value.trim().toLowerCase();
        if (query.length > 0) {
            showView('practice');
            renderProblemCards(mockData.problems.filter((problem) => `${problem.title} ${problem.topic}`.toLowerCase().includes(query)));
        } else {
            renderProblemCards(mockData.problems);
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
    app.currentView = viewName;
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
    if (viewName === 'practice') renderProblemCards(mockData.problems);
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
}

async function renderLearningPath() {
    const path = await app.dataAdapter.getLearningPath();
    const container = document.getElementById('module-list');
    if (!container) return;
    container.innerHTML = path.modules.map((module) => `
        <article class="module-card ${module.complete ? 'is-complete' : ''}">
            <span class="module-number">${module.complete ? '✓' : module.number}</span>
            <div class="module-content"><strong>${module.title}</strong><span>${module.meta}</span></div>
            <span class="module-status">${module.status}</span>
        </article>`).join('');
}

async function renderProblems() {
    const result = await app.dataAdapter.getProblems();
    renderProblemCards(result.problems);
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
            <div class="problem-card-top"><span class="pill ${problem.progress === 'Solved' ? 'pill-teal' : 'pill-muted'}">${problem.progress}</span><span class="practice-symbol">${problem.icon}</span></div>
            <h3>${problem.title}</h3><p>${problem.description}</p>
            <div class="problem-card-footer"><span class="difficulty ${problem.difficulty}">${capitalize(problem.difficulty)} · ${problem.topic}</span><button class="text-button" data-open-editor>Solve <span aria-hidden="true">→</span></button></div>
        </article>`).join('');
    container.querySelectorAll('[data-open-editor]').forEach((button) => button.addEventListener('click', openEditor));
}

function capitalize(value) { return value.charAt(0).toUpperCase() + value.slice(1); }

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
    output.innerHTML = '<span class="output-label">OUTPUT · 0.18s</span><code style="color:#75e6c5">[2, 4]\n\nProcess finished with exit code 0.</code>';
    showToast('Code ran successfully. Nice work.', 'success');
}

function submitCode() {
    runCode();
    showToast('Solution saved to your practice history.', 'success');
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
