(() => {
  "use strict";

  const config = window.CODECRAFT_CONFIG || {};
  const apiBase = String(config.API_BASE_URL || "http://localhost:8000").replace(/\/$/, "");
  const lesson = (id, title, outcome, task) => ({ id, title, outcome, task, minutes: 20 });
  const module = (title, summary, lessons) => ({ title, summary, lessons });
  const courses = [
    {
      id: "python", label: "Python", icon: "Py", color: "purple", eyebrow: "Програмчлалын сэтгэлгээ", duration: "6 долоо хоног", level: "Анхан шат",
      description: "Код хэрхэн ажилладгийг ойлгож, логик сэтгэлгээ болон асуудал задлах сууриа тавина.",
      starter: "name = 'CodeCraft'\nfor step in range(1, 4):\n    print(f'{step}. Сайн уу, {name}!')",
      modules: [
        module("01 · Эхлэл", "Орчин, өгөгдөл, гаралт", [lesson("py-start", "Python гэж юу вэ?", "Код, програм, interpreter-ийн ялгааг ойлгоно.", "print() ашиглан анхны програмаа ажиллуул."), lesson("py-values", "Хувьсагч ба өгөгдлийн төрөл", "string, integer, float, boolean утгыг зөв сонгоно.", "Өөрийн танилцуулга хадгалах 4 хувьсагч үүсгэ."), lesson("py-input", "Оролт, гаралт", "input, print болон type conversion ашиглана.", "Нас асуугаад дараа жилийн насыг хэвлэ.")]),
        module("02 · Логик", "Нөхцөл, давталт, алдаа", [lesson("py-if", "Нөхцөл шалгах", "if, elif, else ашиглан шийдвэр гаргана.", "Оноог үсгэн үнэлгээнд хөрвүүл."), lesson("py-loop", "for ба while", "Давтагдах ажлыг богино бичнэ.", "1–100 хоорондох тэгш тооны нийлбэрийг ол."), lesson("py-debug", "Алдаа уншиж засах", "Syntax, runtime, logic алдааг ялгана.", "Эвдэрхий тооны машинд 3 алдаа ол.")]),
        module("03 · Өгөгдөл", "List, dictionary, function", [lesson("py-list", "List ба collection", "Олон утгыг хадгалж, шүүж, эрэмбэлнэ.", "Хичээлийн онооны дундаж бод."), lesson("py-dict", "Dictionary", "key/value өгөгдлийг загварчилна.", "Сурагчийн profile dictionary үүсгэ."), lesson("py-function", "Function", "Параметр, return ашиглан кодоо хэсэгчлэнэ.", "Хөнгөлөлт боддог function бич.")]),
        module("04 · Мини төсөл", "CLI бүтээгдэхүүн", [lesson("py-files", "Файлтай ажиллах", "Текст өгөгдөл уншиж, хадгална.", "Тэмдэглэлээ файлд хадгал."), lesson("py-project", "Төсөл: Task tracker", "Бүх ойлголтоо нэг урсгалд нэгтгэнэ.", "Нэмэх, харах, дуусгах CLI app бүтээ."), lesson("py-review", "Шалгалт ба рефактор", "Кодоо уншигдахуйц болгож edge case шалгана.", "Төслөө function-уудаар хуваа.")])
      ]
    },
    {
      id: "html", label: "HTML", icon: "<>", color: "orange", eyebrow: "Вэбийн утга ба бүтэц", duration: "4 долоо хоног", level: "Анхан шат",
      description: "Хүртээмжтэй, хайлтын системд ойлгомжтой веб хуудсыг зөв бүтцээр байгуулна.",
      starter: "<main>\n  <h1>Миний анхны вэб</h1>\n  <p>Би semantic HTML ашиглаж байна.</p>\n  <button>Эхлэх</button>\n</main>",
      modules: [
        module("01 · Вэбийн суурь", "Browser ба document", [lesson("html-web", "Вэб хэрхэн ажилладаг вэ?", "Browser, server, URL, request-ийн үүргийг ойлгоно.", "Нэг web request-ийн урсгалыг зур."), lesson("html-doc", "HTML document", "doctype, head, body, metadata-г зөв бичнэ.", "Стандарт хангасан page үүсгэ."), lesson("html-text", "Текст ба холбоос", "Heading, paragraph, list, link ашиглана.", "Хувийн танилцуулга хий.")]),
        module("02 · Semantic HTML", "Утгатай бүтэц", [lesson("html-semantic", "Page landmark", "header, nav, main, section, footer сонгоно.", "Div page-ийг semantic болго."), lesson("html-media", "Зураг ба медиа", "Responsive image, figure, alt ашиглана.", "Тайлбартай gallery хий."), lesson("html-table", "Хүснэгт", "caption, scope бүхий table байгуулна.", "7 хоногийн хуваарь хий.")]),
        module("03 · Form ба accessibility", "Оролт, keyboard, screen reader", [lesson("html-form", "Form-ийн үндэс", "label, input, textarea, button холбоно.", "Бүртгэлийн form үүсгэ."), lesson("html-validation", "Browser validation", "Input type, required, constraint ашиглана.", "Алдааны төлөвүүдийг шалга."), lesson("html-a11y", "Accessibility", "Keyboard ба accessible name шалгана.", "Mouse-гүйгээр page-аа турш.")]),
        module("04 · Төсөл", "Portfolio бүтэц", [lesson("html-plan", "Контент төлөвлөх", "Wireframe-ийг outline болгоно.", "Landing page heading map гарга."), lesson("html-build", "Төсөл: Portfolio", "Бодит portfolio-ийн контентыг тэмдэглэнэ.", "Hero, work, about, contact хий."), lesson("html-audit", "HTML аудит", "Semantic ба accessibility алдааг засна.", "Checklist-ээр төслөө шалга.")])
      ]
    },
    {
      id: "css", label: "CSS", icon: "#", color: "blue", eyebrow: "Харагдац ба layout", duration: "7 долоо хоног", level: "Анхан → дунд",
      description: "Design token-оос responsive layout хүртэл бодит интерфэйсийг системтэй загварчилна.",
      starter: ":root {\n  --brand: #7c3aed;\n}\n.card {\n  padding: 24px;\n  border-radius: 18px;\n  color: white;\n  background: var(--brand);\n}",
      modules: [
        module("01 · CSS хэл", "Selector, cascade, box model", [lesson("css-start", "Selector", "Element, class, state-ийг зөв онилно.", "Profile card-ын selector бич."), lesson("css-cascade", "Cascade ба specificity", "Яагаад style үйлчилж байгааг тайлбарлана.", "Зөрчилтэй declaration цэгцэл."), lesson("css-box", "Box model", "Padding, border, margin-ийг тооцно.", "Card spacing тааруул.")]),
        module("02 · Layout", "Flexbox, Grid, position", [lesson("css-flex", "Flexbox", "Alignment ба wrapping хийнэ.", "Responsive navbar хий."), lesson("css-grid", "CSS Grid", "Хоёр хэмжээст layout байгуулна.", "Dashboard grid бүтээ."), lesson("css-position", "Position ба stacking", "Sticky, z-index-ийг ойлгоно.", "Sticky header хий.")]),
        module("03 · Responsive UI", "Mobile-first ба fluid type", [lesson("css-responsive", "Mobile-first", "Контентоор breakpoint сонгоно.", "Portfolio-г 3 дэлгэцэд тохируул."), lesson("css-fluid", "Fluid хэмжээ", "clamp, minmax, relative unit ашиглана.", "Heading ба grid fluid болго."), lesson("css-query", "Container query", "Орчиндоо дасан зохицох component хийнэ.", "Responsive card хий.")]),
        module("04 · Design system", "Token, component, state", [lesson("css-token", "Design token", "Өнгө, spacing, type-ээ variable болгоно.", "Theme token set үүсгэ."), lesson("css-component", "Component style", "Variant, size, state загварчилна.", "Button-ийн 3 variant хий."), lesson("css-motion", "Animation", "Transition, keyframe зорилготой ашиглана.", "Reduced-motion animation хий.")]),
        module("05 · Төсөл", "Responsive бүтээгдэхүүн", [lesson("css-figma", "Дизайнаас код руу", "Spacing, type, color хэмжинэ.", "Mockup hero-г кодло."), lesson("css-project", "Төсөл: SaaS landing", "Production responsive page бүтээнэ.", "6 section, nav, pricing хий."), lesson("css-audit", "Visual QA", "Overflow, contrast, edge case засна.", "320–1440px шалга.")])
      ]
    },
    {
      id: "javascript", label: "JavaScript", icon: "JS", color: "yellow", eyebrow: "Вэбийн логик ба үйлдэл", duration: "10 долоо хоног", level: "Анхан → дунд",
      description: "DOM, state, API, async урсгалаар интерактив frontend бүтээгдэхүүн бүтээнэ.",
      starter: "const button = document.querySelector('button');\nlet count = 0;\nbutton?.addEventListener('click', () => {\n  count += 1;\n  button.textContent = `Даралт: ${count}`;\n});",
      modules: [
        module("01 · JavaScript суурь", "Утга, operator, control flow", [lesson("js-values", "Утга ба хувьсагч", "const, let, primitive type хэрэглэнэ.", "Сагсны нийт үнэ бод."), lesson("js-logic", "Нөхцөл ба давталт", "Control flow ашиглана.", "Password strength шалга."), lesson("js-function", "Function", "Input/output-той function зохионо.", "Үнэ форматлах function бич.")]),
        module("02 · Modern JS", "Array, object, module", [lesson("js-array", "Array method", "map, filter, find, reduce сонгоно.", "Product list шүү."), lesson("js-object", "Object", "UI data-г загварчилна.", "Course card render хий."), lesson("js-module", "Module", "Export/import-аар хариуцлага салгана.", "Utility ба UI module болго.")]),
        module("03 · DOM ба state", "Event, render, form", [lesson("js-dom", "DOM", "Node-ийг аюулгүй шинэчилнэ.", "Todo item render хий."), lesson("js-event", "Event", "Propagation, delegation ашиглана.", "Dynamic delete холбо."), lesson("js-state", "UI state", "Нэг source of truth-оос render хийнэ.", "Filter-тэй task app хий."), lesson("js-form", "Form validation", "Submit ба error feedback хийнэ.", "Signup form бүтээ.")]),
        module("04 · Async ба API", "Promise, fetch, UI state", [lesson("js-async", "Async/await", "Асинхрон failure удирдана.", "Хоёр request нэгтгэ."), lesson("js-fetch", "REST API", "Status, JSON боловсруулна.", "API card list харуул."), lesson("js-ui", "Loading, empty, error", "UI бүх төлөвийг харуулна.", "Retry flow нэм."), lesson("js-storage", "Local storage", "Browser-д өгөгдөл хадгална.", "Task app persist хий.")]),
        module("05 · Frontend capstone", "Architecture, test, deploy", [lesson("js-architecture", "Architecture", "Feature data flow зурна.", "Capstone plan гарга."), lesson("js-project", "Төсөл: Dashboard", "API, filter, modal бүхий app бүтээнэ.", "MVP хэрэгжүүл."), lesson("js-quality", "Test ба performance", "DevTools-аар алдаа олно.", "Smoke test нэм."), lesson("js-deploy", "Deploy ба portfolio", "Production demo бэлдэнэ.", "Case study нийтэл.")])
      ]
    }
  ];

  const translations = {
    mn: { home: "Нүүр", curriculum: "Сурах зам", workspace: "Кодын орчин", progress: "Миний ахиц", login: "Нэвтрэх", language: "Хэл", theme: "Загвар", light: "Гэрэлтэй", dark: "Бараан", system: "Системийн", menu: "Цэс", skip: "Үндсэн агуулга руу очих", synced: "Realtime ахиц шинэчлэгдлээ." },
    en: { home: "Home", curriculum: "Learning path", workspace: "Code lab", progress: "My progress", login: "Sign in", language: "Language", theme: "Theme", light: "Light", dark: "Dark", system: "System", menu: "Menu", skip: "Skip to main content", synced: "Progress updated in real time." }
  };
  const state = { user: null, session: null, progress: {}, completed: JSON.parse(localStorage.getItem("codecraft-completed") || "{}"), preferences: JSON.parse(localStorage.getItem("codecraft-preferences") || '{"locale":"mn","theme":"system"}'), realtimeChannel: null };
  let client = window.supabase && config.SUPABASE_URL && config.SUPABASE_ANON_KEY ? window.supabase.createClient(config.SUPABASE_URL, config.SUPABASE_ANON_KEY) : null;
  const esc = (v) => String(v ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#039;" }[c]));
  const getCourse = (id) => courses.find((course) => course.id === id) || courses[0];
  const getLessons = (course) => course.modules.flatMap((item) => item.lessons);
  const doneFor = (id) => new Set(state.completed[id] || []);
  const progressFor = (course) => Math.max(Math.round(doneFor(course.id).size / getLessons(course).length * 100), Number(state.progress[course.id] || 0));
  const userName = () => state.user?.user_metadata?.display_name || state.user?.email?.split("@")[0] || "суралцагч";
  const t = (key) => translations[state.preferences.locale]?.[key] || translations.mn[key] || key;

  function applyPreferences() {
    const systemDark = matchMedia("(prefers-color-scheme: dark)").matches;
    document.documentElement.dataset.theme = state.preferences.theme === "system" ? (systemDark ? "dark" : "light") : state.preferences.theme;
    document.documentElement.lang = state.preferences.locale;
    localStorage.setItem("codecraft-preferences", JSON.stringify(state.preferences));
  }

  async function initialiseSupabase() {
    if (client || !window.supabase) return;
    try {
      const publicConfig = await api("/api/public-config");
      client = window.supabase.createClient(publicConfig.supabase_url, publicConfig.supabase_publishable_key);
    } catch { /* The academy remains usable offline when the API is not running. */ }
  }

  async function api(path, options = {}) {
    const headers = { "Content-Type": "application/json", ...(options.headers || {}) };
    if (state.session?.access_token) headers.Authorization = `Bearer ${state.session.access_token}`;
    const response = await fetch(`${apiBase}${path}`, { ...options, headers });
    if (!response.ok) throw new Error(await response.text());
    return response.json();
  }
  async function loadProgress() {
    if (!state.session) { state.progress = JSON.parse(localStorage.getItem("codecraft-progress") || "{}"); return; }
    try { const rows = await api("/api/progress"); state.progress = Object.fromEntries(rows.map((r) => [r.course_id, Number(r.progress_percent)])); }
    catch { state.progress = JSON.parse(localStorage.getItem("codecraft-progress") || "{}"); }
  }
  async function loadLessonProgress() {
    if (!state.session) return;
    try {
      const rows = await api("/api/lesson-progress");
      const completed = {};
      rows.forEach((row) => { (completed[row.course_id] ||= []).push(row.lesson_id); });
      state.completed = completed;
      localStorage.setItem("codecraft-completed", JSON.stringify(completed));
    } catch { /* Keep local progress available if the API is temporarily unreachable. */ }
  }
  async function saveProgress(course, value) {
    state.progress[course.id] = value; localStorage.setItem("codecraft-progress", JSON.stringify(state.progress));
    if (!state.session) return;
    try { await api("/api/progress", { method: "POST", body: JSON.stringify({ course_id: course.id, progress_percent: value }) }); } catch { /* offline-first */ }
  }
  async function saveLessonProgress(course, lessonId, completed) {
    if (!state.session) return;
    try { await api("/api/lesson-progress", { method: "POST", body: JSON.stringify({ course_id: course.id, lesson_id: lessonId, completed }) }); } catch { toast("Ахиц локал төхөөрөмж дээр хадгалагдлаа."); }
  }
  async function loadPreferences() {
    if (!state.session) return;
    try {
      const profile = await api("/api/profile");
      state.preferences = { locale: profile.locale || "mn", theme: profile.theme || "system" };
      applyPreferences();
    } catch { /* Preferences remain local when profile sync is unavailable. */ }
  }
  async function savePreferences() {
    applyPreferences();
    if (!state.session) return;
    try { await api("/api/preferences", { method: "POST", body: JSON.stringify(state.preferences) }); } catch { toast("Тохиргоо локал төхөөрөмж дээр хадгалагдлаа."); }
  }
  function subscribeRealtime() {
    if (!client || !state.session || !state.user) return;
    if (state.realtimeChannel) client.removeChannel(state.realtimeChannel);
    client.realtime.setAuth(state.session.access_token);
    const userFilter = `user_id=eq.${state.user.id}`;
    state.realtimeChannel = client.channel(`codecraft-progress-${state.user.id}`)
      .on("postgres_changes", { event: "*", schema: "public", table: "course_progress", filter: userFilter }, (payload) => {
        const row = payload.new;
        if (row?.course_id) { state.progress[row.course_id] = Number(row.progress_percent || 0); route(); toast(t("synced")); }
      })
      .on("postgres_changes", { event: "*", schema: "public", table: "lesson_progress", filter: userFilter }, (payload) => {
        const row = payload.new?.lesson_id ? payload.new : payload.old;
        if (!row?.course_id || !row?.lesson_id) return;
        const set = doneFor(row.course_id);
        if (payload.eventType === "DELETE") set.delete(row.lesson_id); else set.add(row.lesson_id);
        state.completed[row.course_id] = [...set];
        localStorage.setItem("codecraft-completed", JSON.stringify(state.completed));
        route(); toast(t("synced"));
      }).subscribe();
  }
  function toast(message) {
    document.querySelector(".cc-toast")?.remove(); const el = document.createElement("div"); el.className = "cc-toast"; el.role = "status"; el.textContent = message; document.body.appendChild(el); setTimeout(() => el.remove(), 3000);
  }
  function header(active) {
    return `<a class="cc-skip-link" href="#main-content">${t("skip")}</a><header class="cc-header"><div class="cc-header-inner"><a class="cc-brand" href="/" aria-label="CodeCraft Academy ${t("home")}"><span class="cc-brand-mark">C</span><span>CodeCraft<small>Academy</small></span></a><nav class="cc-nav" id="main-nav" aria-label="${t("menu")}"><a class="${active === "home" ? "is-active" : ""}" href="/">${t("home")}</a><a class="${active === "curriculum" ? "is-active" : ""}" href="/curriculum">${t("curriculum")}</a><a class="${active === "workspace" ? "is-active" : ""}" href="/workspace">${t("workspace")}</a><a class="${active === "profile" ? "is-active" : ""}" href="/profile">${t("progress")}</a></nav><div class="cc-header-actions"><label class="cc-select cc-language-select"><span>${t("language")}</span><select id="language-select" aria-label="${t("language")}"><option value="mn" ${state.preferences.locale === "mn" ? "selected" : ""}>Монгол</option><option value="en" ${state.preferences.locale === "en" ? "selected" : ""}>English</option></select></label><label class="cc-select cc-theme-select"><span>${t("theme")}</span><select id="theme-select" aria-label="${t("theme")}"><option value="system" ${state.preferences.theme === "system" ? "selected" : ""}>${t("system")}</option><option value="light" ${state.preferences.theme === "light" ? "selected" : ""}>${t("light")}</option><option value="dark" ${state.preferences.theme === "dark" ? "selected" : ""}>${t("dark")}</option></select></label><button class="cc-menu" aria-label="${t("menu")}" aria-controls="main-nav" aria-expanded="false"><span aria-hidden="true">☰</span><span>${t("menu")}</span></button>${state.user ? `<a class="cc-profile" href="/profile">${esc(userName())}<span class="cc-avatar">${esc(userName()[0].toUpperCase())}</span></a>` : `<button class="cc-login">${t("login")}</button>`}</div></div></header>`;
  }
  const footer = () => `<footer class="cc-footer"><div><strong>CodeCraft Academy</strong><p>Монгол хэлээр · Эхнээс нь · Бүтээж сурна.</p></div><div><a href="/curriculum">Сурах зам</a><a href="/workspace">Кодын орчин</a><span>© 2026</span></div></footer>`;
  function page(html, active) {
    document.querySelector("#app").innerHTML = `<div class="cc-app">${header(active)}<main id="main-content" class="cc-main" tabindex="-1">${html}</main>${footer()}</div>`;
    document.querySelector(".cc-menu")?.addEventListener("click", (event) => { const open = document.querySelector(".cc-nav").classList.toggle("is-open"); event.currentTarget.setAttribute("aria-expanded", String(open)); });
    document.querySelector(".cc-login")?.addEventListener("click", signIn);
    document.querySelector("#language-select")?.addEventListener("change", async (event) => { state.preferences.locale = event.currentTarget.value; await savePreferences(); route(); });
    document.querySelector("#theme-select")?.addEventListener("change", async (event) => { state.preferences.theme = event.currentTarget.value; await savePreferences(); });
    scrollTo({ top: 0, behavior: "instant" });
  }
  async function signIn() {
    if (!client) return toast("Demo горим идэвхтэй. Supabase тохируулсны дараа нэвтэрнэ.");
    const email = prompt("Email хаягаа оруулна уу:"); if (!email) return;
    const { error } = await client.auth.signInWithOtp({ email, options: { emailRedirectTo: location.origin } }); toast(error ? error.message : "Нэвтрэх холбоос илгээгдлээ.");
  }
  function backendCard() {
    return `<section class="cc-backend"><div><span class="cc-premium">PREMIUM · COMING SOON</span><p class="cc-eyebrow">Дараагийн шат</p><h2>Backend developer замнал</h2><p>Python API, FastAPI, PostgreSQL, authentication, deployment-ийг frontend замналаа дуусгасны дараа үргэлжлүүлнэ.</p><div class="cc-tags"><span>FastAPI</span><span>PostgreSQL</span><span>Auth</span><span>Deploy</span></div></div><button data-waitlist>Нээгдэхэд мэдэгдэл авах</button></section>`;
  }
  function card(course, index) {
    const p = progressFor(course); return `<article class="cc-course cc-reveal" style="--delay:${index * 70}ms"><div class="cc-course-top"><span class="cc-course-icon ${course.color}">${esc(course.icon)}</span><span class="cc-free">ҮНЭГҮЙ</span></div><p class="cc-kicker">${esc(course.eyebrow)}</p><h3>${course.label}</h3><p>${esc(course.description)}</p><div class="cc-course-meta"><span>${course.modules.length} модуль · ${getLessons(course).length} хичээл</span><span>${p}%</span></div><div class="cc-progress"><span style="width:${p}%"></span></div><a class="cc-card-link" href="/course?course=${course.id}">${p ? "Үргэлжлүүлэх" : "Хичээлээ үзэх"}<span>→</span></a></article>`;
  }
  function renderHome() {
    const count = courses.reduce((sum, c) => sum + getLessons(c).length, 0);
    const path = [["01", "Кодын суурь", "Python-оор логик сэтгэлгээ, асуудал задлах сууриа тавина.", "python"], ["02", "Вэбийн бүтэц", "HTML-ээр утгатай, хүртээмжтэй document байгуулна.", "html"], ["03", "Responsive интерфэйс", "CSS-ээр бүх дэлгэцэд ажиллах UI бүтээнэ.", "css"], ["04", "Бодит frontend app", "JavaScript, DOM, API, state-аар бүтээгдэхүүн гаргана.", "javascript"]];
    page(`<section class="cc-hero-home"><div class="cc-hero-copy cc-reveal"><span class="cc-pill"><i></i> Монгол хэл дээрх кодын академи</span><h1>Кодыг цээжлэхгүй.<br><em>Бүтээж</em> сурна.</h1><p>Тэгээс эхлээд HTML, CSS, JavaScript-ийг бүрэн эзэмшиж, ажилд орох portfolio бүхий frontend developer болоорой. Python суурь ч үнэгүй.</p><div class="cc-hero-actions"><a class="cc-primary cc-primary-lg" href="/curriculum">Үнэгүй эхлэх →</a><a class="cc-text-link" href="#roadmap">Сурах замыг харах ↓</a></div><div class="cc-proof"><span><strong>${count}</strong> хичээл</span><span><strong>4</strong> бодит төсөл</span><span><strong>₮0</strong> frontend замнал</span></div></div><div class="cc-code-card cc-reveal"><div class="cc-window-bar"><span></span><span></span><span></span><small>first-project.js</small></div><pre><code><b>const</b> learner = {\n  name: <i>"Чи"</i>,\n  level: <i>"beginner"</i>,\n  goal: <i>"frontend developer"</i>\n};\n\n<b>function</b> <strong>startJourney</strong>(student) {\n  student.level = <i>"builder"</i>;\n  <mark>return</mark> <i>"Өнөөдөр эхэлье 🚀"</i>;\n}</code></pre><div class="cc-terminal">› Таны эхний төсөл эндээс эхэлнэ.</div></div></section><section class="cc-trust"><span>Сууриас нь</span><b>→</b><span>Алхам алхмаар</span><b>→</b><span>Бодит дадлагаар</span><b>→</b><span>Portfolio-той</span></section><section class="cc-section" id="roadmap"><div class="cc-section-head"><div><p class="cc-eyebrow">Таны замнал</p><h2>Frontend developer болох 4 шат</h2></div><a class="cc-text-link" href="/curriculum">Бүрэн хөтөлбөр →</a></div><div class="cc-roadmap">${path.map((s) => `<a href="/course?course=${s[3]}" class="cc-roadmap-step"><span>${s[0]}</span><div><h3>${s[1]}</h3><p>${s[2]}</p></div></a>`).join("")}</div></section><section class="cc-section"><div class="cc-section-head"><div><p class="cc-eyebrow">Үнэгүй сургалтууд</p><h2>Хэл бүрийг эхнээс нь бүрэн сур</h2></div><span class="cc-section-note">Өөрийн хурдаар · Монгол хэлээр</span></div><div class="cc-courses">${courses.map(card).join("")}</div></section><section class="cc-project-strip"><div><p class="cc-eyebrow">Зөвхөн үзэх биш</p><h2>4 portfolio төсөл бүтээнэ</h2></div><div><span>01 · CLI Task Tracker</span><span>02 · Semantic Portfolio</span><span>03 · SaaS Landing Page</span><span>04 · Learning Dashboard</span></div></section>${backendCard()}`, "home");
    document.querySelector("[data-waitlist]")?.addEventListener("click", () => toast("Backend premium хөтөлбөр одоогоор бэлтгэгдэж байна."));
  }
  function renderCurriculum() {
    const total = courses.reduce((sum, c) => sum + getLessons(c).length, 0);
    page(`<section class="cc-page-hero"><div><p class="cc-eyebrow">Бүрэн curriculum</p><h1>Тэгээс frontend developer хүртэл.</h1><p>4 шат, ${courses.reduce((s, c) => s + c.modules.length, 0)} модуль, ${total} алхамчилсан хичээл. Дарааллын дагуу эсвэл хэрэгтэй хэлээсээ эхэл.</p></div><div class="cc-mini-stat"><strong>100%</strong><span>Frontend замнал<br>үнэгүй</span></div></section><section class="cc-path-list">${courses.map((course, i) => `<article class="cc-path-course"><div class="cc-path-number">0${i + 1}</div><div class="cc-path-main"><div class="cc-path-heading"><span class="cc-course-icon ${course.color}">${esc(course.icon)}</span><div><p class="cc-kicker">${esc(course.eyebrow)}</p><h2>${course.label}</h2></div><span class="cc-path-duration">${course.duration}</span></div><p>${esc(course.description)}</p><div class="cc-module-pills">${course.modules.map((m) => `<span>${esc(m.title.replace(/^\d+ · /, ""))}</span>`).join("")}</div><div class="cc-path-footer"><span>${course.modules.length} модуль · ${getLessons(course).length} хичээл · ${course.level}</span><a class="cc-primary" href="/course?course=${course.id}">Хөтөлбөр нээх →</a></div></div></article>`).join("")}</section>${backendCard()}`, "curriculum");
    document.querySelector("[data-waitlist]")?.addEventListener("click", () => toast("Backend хөтөлбөр coming soon."));
  }
  function renderCourse() {
    const course = getCourse(new URLSearchParams(location.search).get("course")); const done = doneFor(course.id); const p = progressFor(course);
    page(`<a class="cc-back-link" href="/curriculum">← Бүх сургалт</a><section class="cc-course-hero"><div><span class="cc-course-icon ${course.color}">${esc(course.icon)}</span><p class="cc-eyebrow">${esc(course.eyebrow)}</p><h1>${course.label}-ийг сууриас нь</h1><p>${esc(course.description)}</p><div class="cc-hero-actions"><a class="cc-primary cc-primary-lg" href="/lesson?course=${course.id}&lesson=${getLessons(course)[0].id}">${p ? "Үргэлжлүүлэн сурах" : "Эхний хичээлээ эхлэх"} →</a><a class="cc-secondary" href="/workspace?course=${course.id}">Код турших</a></div></div><aside><span>${course.level}</span><strong>${getLessons(course).length}</strong><small>хичээл</small><div class="cc-progress"><span style="width:${p}%"></span></div><p>${done.size} хичээл дууссан · ${p}%</p></aside></section><section class="cc-syllabus"><div class="cc-section-head"><div><p class="cc-eyebrow">Хөтөлбөр</p><h2>${course.modules.length} модуль · Алхам бүр тодорхой</h2></div><span>${course.duration}</span></div>${course.modules.map((m, mi) => `<article class="cc-module"><button class="cc-module-toggle" aria-expanded="${mi === 0}"><span class="cc-module-index">${String(mi + 1).padStart(2, "0")}</span><span><strong>${esc(m.title.replace(/^\d+ · /, ""))}</strong><small>${esc(m.summary)} · ${m.lessons.length} хичээл</small></span><span>⌄</span></button><div class="cc-lesson-list ${mi === 0 ? "is-open" : ""}">${m.lessons.map((l, li) => `<a href="/lesson?course=${course.id}&lesson=${l.id}" class="cc-lesson-row"><span class="cc-lesson-status ${done.has(l.id) ? "is-done" : ""}">${done.has(l.id) ? "✓" : `${mi + 1}.${li + 1}`}</span><span><strong>${esc(l.title)}</strong><small>${esc(l.outcome)}</small></span><time>${l.minutes} мин</time><b>→</b></a>`).join("")}</div></article>`).join("")}</section>`, "curriculum");
    document.querySelectorAll(".cc-module-toggle").forEach((b) => b.addEventListener("click", () => { const list = b.nextElementSibling; const open = list.classList.toggle("is-open"); b.setAttribute("aria-expanded", String(open)); }));
  }
  function renderLesson() {
    const q = new URLSearchParams(location.search); const course = getCourse(q.get("course")); const lessons = getLessons(course); const index = Math.max(0, lessons.findIndex((l) => l.id === q.get("lesson"))); const current = lessons[index]; const parent = course.modules.find((m) => m.lessons.includes(current)); const examples = { python: "topic = 'practice'\nminutes = 20\nprint(f'{topic}: {minutes} minutes')", html: "<section aria-labelledby=\"title\">\n  <h2 id=\"title\">Өнөөдрийн хичээл</h2>\n  <p>Утгатай бүтэц.</p>\n</section>", css: ".lesson-card {\n  display: grid;\n  gap: 1rem;\n  padding: clamp(1rem, 3vw, 2rem);\n}", javascript: "const lesson = { completed: false };\nlesson.completed = true;\nconsole.log(lesson);" };
    page(`<section class="cc-lesson-shell"><aside class="cc-lesson-sidebar"><a class="cc-back-link" href="/course?course=${course.id}">← ${course.label} хөтөлбөр</a><div class="cc-lesson-course"><span class="cc-course-icon ${course.color}">${esc(course.icon)}</span><div><strong>${course.label}</strong><small>${progressFor(course)}% дууссан</small></div></div><div class="cc-progress"><span style="width:${progressFor(course)}%"></span></div><nav>${course.modules.map((m) => `<div><p>${esc(m.title)}</p>${m.lessons.map((l) => `<a class="${l.id === current.id ? "is-active" : ""} ${doneFor(course.id).has(l.id) ? "is-done" : ""}" href="/lesson?course=${course.id}&lesson=${l.id}"><span>${doneFor(course.id).has(l.id) ? "✓" : "○"}</span>${esc(l.title)}</a>`).join("")}</div>`).join("")}</nav></aside><article class="cc-lesson-content"><p class="cc-eyebrow">${esc(parent.title)} · ${current.minutes} минут</p><h1>${esc(current.title)}</h1><p class="cc-lesson-lede">${esc(current.outcome)}</p><div class="cc-learn-box"><strong>Энэ хичээлийн дараа</strong><ul><li>${esc(current.outcome)}</li><li>Жишээг өөрчилж өөрийн хувилбарыг ажиллуулна.</li><li>Жижиг даалгавраар ойлголтоо бататгана.</li></ul></div><h2>1. Ойлголтоо зураглая</h2><p>Шинэ ойлголтыг жижиг хэсэг болгон задал. Мөр бүр ямар оролт авч, ямар өөрчлөлт хийж, юу буцааж байгааг тайлбарлаарай. Ингэвэл syntax цээжлэхээс илүү кодын урсгалыг ойлгодог болно.</p><h2>2. Жишээг ажиллуулъя</h2><div class="cc-code-example"><div><span>${course.label.toLowerCase()}</span><button data-copy>Хуулах</button></div><pre><code>${esc(examples[course.id])}</code></pre></div><a class="cc-secondary cc-open-lab" href="/workspace?course=${course.id}">Кодын орчинд турших →</a><h2>3. Өөрөө хий</h2><div class="cc-task"><span>ДАДЛАГА</span><strong>${esc(current.task)}</strong><p>Алдаа гарвал: алдааны мөр → хувьсагчийн утга → хүлээсэн үр дүн гэсэн дарааллаар шалга.</p></div><div class="cc-lesson-nav">${lessons[index - 1] ? `<a href="/lesson?course=${course.id}&lesson=${lessons[index - 1].id}">← Өмнөх</a>` : "<span></span>"}<button id="complete-lesson" class="${doneFor(course.id).has(current.id) ? "is-done" : ""}">${doneFor(course.id).has(current.id) ? "✓ Дууссан" : "Хичээл дуусгах"}</button>${lessons[index + 1] ? `<a href="/lesson?course=${course.id}&lesson=${lessons[index + 1].id}">Дараах →</a>` : `<a href="/course?course=${course.id}">Хөтөлбөр →</a>`}</div></article></section>`, "curriculum");
    document.querySelector("[data-copy]")?.addEventListener("click", async () => { try { await navigator.clipboard.writeText(examples[course.id]); toast("Код хуулагдлаа."); } catch { toast("Кодыг гараар хуулна уу."); } });
    document.querySelector("#complete-lesson")?.addEventListener("click", async (event) => { const button = event.currentTarget; const set = doneFor(course.id); set.has(current.id) ? set.delete(current.id) : set.add(current.id); state.completed[course.id] = [...set]; localStorage.setItem("codecraft-completed", JSON.stringify(state.completed)); button.classList.toggle("is-done", set.has(current.id)); button.textContent = set.has(current.id) ? "✓ Дууссан" : "Хичээл дуусгах"; toast("Ахиц хадгалагдлаа."); await Promise.all([saveLessonProgress(course, current.id, set.has(current.id)), saveProgress(course, Math.round(set.size / lessons.length * 100))]); });
  }
  function preview(language, code) {
    const safe = String(code).replace(/<\/script/gi, "<\\/script");
    if (language === "html") return `<style>body{font-family:system-ui;padding:24px}</style>${safe}`;
    if (language === "css") return `<style>body{font-family:system-ui;padding:24px}${safe}</style>${getCourse("html").starter}`;
    if (language === "javascript") return `<main style="font-family:system-ui;padding:24px"><button>Намайг дар</button><h3>Console</h3><pre id="out"></pre></main><script>const out=document.getElementById('out');console.log=(...a)=>out.textContent+=a.join(' ')+'\\n';try{${safe}}catch(e){out.textContent=e.message}</script>`;
    return `<main style="font-family:system-ui;padding:24px"><h3>Python output</h3><pre id="out">Python runtime ачаалж байна...</pre></main><script src="https://cdn.jsdelivr.net/pyodide/v0.26.2/full/pyodide.js"><\/script><script>const out=document.getElementById('out');loadPyodide({indexURL:'https://cdn.jsdelivr.net/pyodide/v0.26.2/full/'}).then(async(py)=>{out.textContent='';py.setStdout({batched:(text)=>out.textContent+=text+'\\n'});await py.runPythonAsync(${JSON.stringify(code)})}).catch((error)=>out.textContent='Python error: '+error.message)<\/script>`;
  }
  function renderWorkspace() {
    const course = getCourse(new URLSearchParams(location.search).get("course") || "html"); const saved = localStorage.getItem(`codecraft-code-${course.id}`) || course.starter;
    page(`<section class="cc-workspace-head"><div><p class="cc-eyebrow">Интерактив лаборатори</p><h1>Кодоо бич. Шууд үр дүнг хар.</h1><p>Алдаа гаргах нь суралцах үйл явцын нэг хэсэг.</p></div><a class="cc-secondary" href="/course?course=${course.id}">${course.label} хөтөлбөр →</a></section><div class="cc-language-tabs">${courses.map((c) => `<button class="cc-language-tab ${c.id === course.id ? "is-active" : ""}" data-language="${c.id}"><span class="cc-course-icon ${c.color}">${esc(c.icon)}</span>${c.label}</button>`).join("")}</div><section class="cc-workspace"><div class="cc-editor-panel"><div class="cc-panel-bar"><span>${course.label.toLowerCase()} · playground</span><button class="cc-run">▶ Ажиллуулах</button></div><textarea id="code-editor" class="cc-editor" spellcheck="false">${esc(saved)}</textarea><div class="cc-editor-foot"><span>Автоматаар хадгална</span><button data-reset>Жишээ сэргээх</button></div></div><div class="cc-preview-panel"><div class="cc-panel-bar"><span>Үр дүн</span><span class="cc-live-dot">LIVE</span></div><iframe class="cc-preview" sandbox="allow-scripts" title="Кодын үр дүн"></iframe></div></section>`, "workspace");
    const editor = document.querySelector("#code-editor"), frame = document.querySelector(".cc-preview"); const run = () => { frame.srcdoc = preview(course.id, editor.value); localStorage.setItem(`codecraft-code-${course.id}`, editor.value); }; run();
    document.querySelectorAll("[data-language]").forEach((b) => b.addEventListener("click", () => navigate(`/workspace?course=${b.dataset.language}`))); document.querySelector(".cc-run").addEventListener("click", () => { run(); toast("Код ажиллалаа."); }); document.querySelector("[data-reset]").addEventListener("click", () => { editor.value = course.starter; run(); }); editor.addEventListener("input", () => localStorage.setItem(`codecraft-code-${course.id}`, editor.value));
  }
  function renderProfile() {
    const total = Math.round(courses.reduce((sum, c) => sum + progressFor(c), 0) / courses.length);
    page(`<section class="cc-profile-hero"><div class="cc-avatar cc-avatar-lg">${esc(userName()[0].toUpperCase())}</div><div><p class="cc-eyebrow">Миний сурах замнал</p><h1>${esc(userName())}</h1><p>${state.user ? esc(state.user.email) : "Demo горим · Ахиц энэ төхөөрөмжид хадгалагдана"}</p></div><div class="cc-profile-score"><strong>${total}%</strong><span>нийт ахиц</span></div></section><section class="cc-profile-grid">${courses.map((c) => `<a href="/course?course=${c.id}" class="cc-progress-card"><span class="cc-course-icon ${c.color}">${esc(c.icon)}</span><div><strong>${c.label}</strong><small>${doneFor(c.id).size} / ${getLessons(c).length} хичээл</small><div class="cc-progress"><span style="width:${progressFor(c)}%"></span></div></div><b>${progressFor(c)}%</b></a>`).join("")}</section>`, "profile");
  }
  function navigate(path) { history.pushState({}, "", path); route(); }
  function route() { const path = location.pathname.replace(/\/$/, "") || "/"; ({ "/": renderHome, "/curriculum": renderCurriculum, "/course": renderCourse, "/lesson": renderLesson, "/workspace": renderWorkspace, "/profile": renderProfile }[path] || renderHome)(); }
  async function boot() {
    applyPreferences();
    await initialiseSupabase();
    if (client) {
      const { data } = await client.auth.getSession();
      state.session = data.session;
      state.user = data.session?.user || null;
      if (state.session) { await Promise.all([loadProgress(), loadLessonProgress(), loadPreferences()]); subscribeRealtime(); }
      client.auth.onAuthStateChange(async (_event, session) => {
        state.session = session;
        state.user = session?.user || null;
        if (session) { await Promise.all([loadProgress(), loadLessonProgress(), loadPreferences()]); subscribeRealtime(); }
        else if (state.realtimeChannel) { client.removeChannel(state.realtimeChannel); state.realtimeChannel = null; }
        route();
      });
    } else await loadProgress();
    addEventListener("popstate", route);
    addEventListener("beforeunload", () => { if (client && state.realtimeChannel) client.removeChannel(state.realtimeChannel); });
    document.addEventListener("click", (event) => { const a = event.target.closest("a[href]"); if (!a || a.origin !== location.origin || a.getAttribute("href").startsWith("#")) return; event.preventDefault(); navigate(a.getAttribute("href")); });
    route();
  }
  boot().catch(() => { document.querySelector("#app").innerHTML = `<main id="main-content" class="cc-main" tabindex="-1"><h1>Хуудас ачаалагдсангүй</h1><p>Сүлжээгээ шалгаад дахин оролдоно уу.</p><button class="cc-primary" onclick="location.reload()">Дахин ачаалах</button></main>`; });
})();
