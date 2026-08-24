(() => {
  'use strict';

  const page = document.querySelector('[data-profile-page]');
  if (!page || typeof window.codecraftApi !== 'function') return;
  const themeSelect = page.querySelector('[data-preference-theme]');
  const localeSelect = page.querySelector('[data-preference-locale]');
  const saveStatus = page.querySelector('[data-save-status]');
  const storedUser = JSON.parse(localStorage.getItem('codecraft_user') || '{}');
  const text = (selector, value) => { const node = page.querySelector(selector); if (node) node.textContent = value; };

  const populateProfile = (profile = {}) => {
    const name = profile.display_name || profile.name || profile.email?.split('@')[0] || 'CodeCraft суралцагч';
    text('[data-profile-name]', name);
    text('[data-profile-email]', profile.email || 'Имэйл олдсонгүй');
    text('[data-profile-role]', (profile.role || 'student').toUpperCase());
    text('[data-profile-initials]', name.split(' ').map((part) => part[0]).slice(0, 2).join('').toUpperCase());
    if (themeSelect) themeSelect.value = profile.theme || localStorage.getItem('codecraft_theme') || 'system';
    if (localeSelect) localeSelect.value = profile.locale || 'mn';
    window.localStorage.setItem('codecraft_user', JSON.stringify({ ...profile, name }));
  };

  const renderCourses = (summary = {}) => {
    const container = page.querySelector('[data-profile-courses]');
    if (!container) return;
    container.replaceChildren();
    const courses = Array.isArray(summary.courses) ? summary.courses : [];
    if (!courses.length) {
      const empty = document.createElement('p');
      empty.className = 'empty-state';
      empty.textContent = 'Одоогоор ахицын мэдээлэл алга.';
      container.append(empty);
      return;
    }
    const colors = { html: 'orange', css: 'teal', javascript: 'yellow', python: 'purple' };
    courses.forEach((course) => {
      const row = document.createElement('div');
      row.className = 'progress-course';
      const icon = document.createElement('span');
      icon.className = `course-icon ${colors[course.course_id] || 'purple'}`;
      icon.textContent = ({ html: '<>', css: 'CSS', javascript: 'JS', python: 'Py' })[course.course_id] || 'CC';
      const details = document.createElement('div');
      const title = document.createElement('strong');
      title.textContent = course.title || course.course_id || 'Course';
      const meta = document.createElement('small');
      meta.textContent = `${Number(course.completed_lessons) || 0} / ${Number(course.total_lessons) || 0} хичээл`;
      details.append(title, meta);
      const percent = Math.max(0, Math.min(100, Number(course.progress_percent) || 0));
      const value = document.createElement('b');
      value.textContent = `${percent}%`;
      const progress = document.createElement('div');
      progress.className = 'progress-bar';
      const fill = document.createElement('i');
      fill.style.width = `${percent}%`;
      progress.append(fill);
      row.append(icon, details, value, progress);
      container.append(row);
    });
  };

  const savePreferences = async () => {
    if (!themeSelect || !localeSelect) return;
    saveStatus.textContent = 'Хадгалж байна…';
    try {
      const payload = await window.codecraftApi('/api/learning/profile', {
        method: 'PATCH',
        body: JSON.stringify({ theme: themeSelect.value, locale: localeSelect.value }),
      });
      const profile = payload.profile || {};
      localStorage.setItem('codecraft_theme', profile.theme || themeSelect.value);
      const resolved = (profile.theme || themeSelect.value) === 'system' ? (window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light') : (profile.theme || themeSelect.value);
      document.documentElement.dataset.theme = resolved;
      populateProfile(profile);
      saveStatus.textContent = 'Хадгалагдсан';
      window.showToast(payload.message_mn || 'Тохиргоог хадгаллаа.');
    } catch (error) {
      saveStatus.textContent = 'Хадгалагдсангүй';
      window.showToast(error.message, true);
    }
  };

  page.querySelector('[data-logout]')?.addEventListener('click', async () => {
    try { await fetch(`${window.CODECRAFT_CONFIG.apiBase}/api/auth/logout`, { method: 'POST', credentials: 'same-origin' }); } catch (_) {}
    window.localStorage.removeItem('codecraft_user');
    window.location.href = page.dataset.homeUrl || '/';
  });
  themeSelect?.addEventListener('change', savePreferences);
  localeSelect?.addEventListener('change', savePreferences);

  const showUnauthenticated = () => {
    populateProfile(storedUser);
    if (saveStatus) saveStatus.textContent = 'Нэвтрэх шаардлагатай';
    const container = page.querySelector('[data-profile-courses]');
    if (!container) return;
    container.replaceChildren();
    const empty = document.createElement('p');
    empty.className = 'empty-state';
    empty.append('Ахиц харахын тулд ');
    const link = document.createElement('a');
    link.href = page.dataset.loginUrl || '/auth?mode=login';
    link.textContent = 'нэвтэрнэ үү';
    empty.append(link, '.');
    container.append(empty);
  };

  Promise.all([window.codecraftApi('/api/learning/profile'), window.codecraftApi('/api/learning/summary')])
    .then(([profile, summary]) => { populateProfile(profile.profile); renderCourses(summary); saveStatus.textContent = 'Хадгалагдсан'; })
    .catch((error) => {
      if (error?.status === 401) showUnauthenticated();
      else { saveStatus.textContent = 'Синк холбогдсонгүй'; window.showToast(error.message, true); }
    });
})();
