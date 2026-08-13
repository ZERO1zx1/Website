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
    theme: localStorage.getItem('codehaven-theme') || 'light',
    language: localStorage.getItem('codehaven-language') || 'en',
    authMode: 'login'
};

const viewLabels = {
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
    app.user = await app.dataAdapter.getUser();
    hydrateUser(app.user);
    bindAuthentication();
    applyLanguage();
    await Promise.all([renderDashboard(), renderLearningPath(), renderProblems()]);
    applyLanguage();
    showView('dashboard');
}

function bindNavigation() {
    document.querySelectorAll('[data-view]').forEach((control) => {
        control.addEventListener('click', () => showView(control.dataset.view));
    });
}

function bindInteractions() {
    document.getElementById('theme-toggle')?.addEventListener('click', toggleTheme);
    document.getElementById('language-select')?.addEventListener('change', (event) => setLanguage(event.target.value));
    document.getElementById('settings-language-select')?.addEventListener('change', (event) => setLanguage(event.target.value));
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
    applyLanguage();
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


const translations = {
    en: {
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
        'auth.demo': 'Frontend preview only.',
        'auth.demo.continue': 'Continue as demo learner'
    },
    mn: {
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
        'auth.demo': 'Зөвхөн frontend preview.',
        'auth.demo.continue': 'Demo хэрэглэгчээр үргэлжлүүлэх'
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
    document.querySelectorAll('[data-auth-form]').forEach((form) => {
        form.addEventListener('submit', (event) => {
            event.preventDefault();
            showToast(app.authMode === 'login' ? (app.language === 'mn' ? 'Demo нэвтрэлт амжилттай.' : 'Demo sign in successful.') : (app.language === 'mn' ? 'Demo бүртгэл бэлэн боллоо.' : 'Demo account created.'), 'success');
            window.setTimeout(() => showView('dashboard'), 500);
        });
    });
    document.querySelectorAll('.password-toggle').forEach((button) => {
        button.addEventListener('click', () => {
            const input = button.parentElement.querySelector('input');
            const showing = input.type === 'text';
            input.type = showing ? 'password' : 'text';
            button.textContent = showing ? (app.language === 'mn' ? 'Харах' : 'Show') : (app.language === 'mn' ? 'Нуух' : 'Hide');
            button.setAttribute('aria-label', showing ? 'Show password' : 'Hide password');
        });
    });
    document.getElementById('continue-demo')?.addEventListener('click', () => showView('dashboard'));
}

function setAuthMode(mode) {
    app.authMode = mode;
    document.querySelectorAll('[data-auth-tab]').forEach((tab) => {
        const active = tab.dataset.authTab === mode;
        tab.classList.toggle('is-active', active);
        tab.setAttribute('aria-selected', String(active));
    });
    document.querySelectorAll('[data-auth-form]').forEach((form) => form.classList.toggle('is-hidden', form.dataset.authForm !== mode));
    const title = document.getElementById('auth-title');
    const subtitle = document.getElementById('auth-subtitle');
    if (title) title.textContent = mode === 'login' ? (app.language === 'mn' ? 'Тавтай морилно уу' : 'Welcome back') : (app.language === 'mn' ? 'Бүртгэл үүсгэх' : 'Create your account');
    if (subtitle) subtitle.dataset.i18n = mode === 'login' ? 'auth.login.subtitle' : 'auth.register.subtitle';
    applyLanguage();
}

function setLanguage(language) {
    if (!translations[language]) return;
    app.language = language;
    localStorage.setItem('codehaven-language', language);
    document.documentElement.lang = language;
    const languageSelect = document.getElementById('language-select');
    const settingsLanguageSelect = document.getElementById('settings-language-select');
    if (languageSelect) languageSelect.value = language;
    if (settingsLanguageSelect) settingsLanguageSelect.value = language;
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
    'Python': 'Python', 'Problem solving': 'Бодлого бодолт', 'Data structures': 'Өгөгдлийн бүтэц', 'Web fundamentals': 'Web-ийн суурь',
    'Completed': 'Дууссан', 'In progress': 'Үргэлжилж байна', 'Next:': 'Дараагийнх:', 'List comprehension': 'List comprehension',
    '6 lessons · 42 min': '6 хичээл · 42 минут', '3 of 8 modules complete · 19 hours remaining': '8 модулиас 3 дууссан · 19 цаг үлдсэн',
    'Mon': 'Дав', 'Tue': 'Мяг', 'Wed': 'Лха', 'Thu': 'Пүр', 'Fri': 'Баа', 'Sat': 'Бям', 'Sun': 'Ням'
});
