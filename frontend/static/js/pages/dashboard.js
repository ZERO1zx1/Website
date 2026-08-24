(() => {
  'use strict';

  const dashboard = document.querySelector('[data-dashboard]');
  if (!dashboard || typeof window.codecraftApi !== 'function') return;

  const query = (selector) => dashboard.querySelector(selector);
  const text = (selector, value) => {
    const node = query(selector);
    if (node) node.textContent = value;
  };
  const clampPercent = (value) => Math.max(0, Math.min(100, Number(value) || 0));

  const renderSummary = (summary) => {
    const courses = Array.isArray(summary.courses) ? summary.courses : [];
    const completed = Number(summary.completed_lessons) || 0;
    const overall = clampPercent(summary.overall_percent);
    text('[data-stat-overall]', `${overall}%`);
    text('[data-stat-completed]', completed);
    text('[data-stat-completed-caption]', `${Number(summary.total_lessons) || 0} хичээлээс`);
    text('[data-stat-courses]', courses.length);
    text('[data-stat-overall-caption]', completed ? 'Таны хадгалсан бодит ахиц' : 'Эхний хичээлээ эхлүүлээрэй');
    text('[data-sync-status]', 'Сервертэй синк хийгдсэн');
    text('[data-focus-count]', `${Math.min(completed, 1)} / 1`);

    const next = courses.find((course) => clampPercent(course.progress_percent) < 100) || courses[0];
    if (next) {
      const percent = clampPercent(next.progress_percent);
      text('[data-next-course]', next.title || 'Дараагийн хичээл');
      text('[data-next-percent]', `${percent}% дууссан`);
      text('[data-next-description]', `${Number(next.completed_lessons) || 0} / ${Number(next.total_lessons) || 0} хичээл дууссан. Дараагийн lesson-ээ сонгоод үргэлжлүүлээрэй.`);
      const bar = query('[data-next-bar]');
      if (bar) bar.style.width = `${percent}%`;
      text('[data-next-meta]', `${Math.max(0, (Number(next.total_lessons) || 0) - (Number(next.completed_lessons) || 0))} lesson үлдлээ`);
      const link = query('[data-next-link]');
      if (link) {
        const nextLesson = next.next_lesson_slug;
        link.href = nextLesson
          ? `${dashboard.dataset.lessonUrl}?course=${encodeURIComponent(next.course_id || '')}&lesson=${encodeURIComponent(nextLesson)}`
          : `${dashboard.dataset.courseUrl}?id=${encodeURIComponent(next.course_id || '')}`;
        link.textContent = nextLesson ? 'Дараагийн lesson →' : 'Course харах →';
      }
    }

    const list = query('[data-course-progress-list]');
    if (!list) return;
    list.replaceChildren();
    if (!courses.length) {
      const empty = document.createElement('p');
      empty.className = 'empty-state';
      empty.textContent = 'Одоогоор ахицын мэдээлэл алга. Сургалтын замаас хичээлээ эхлүүлээрэй.';
      list.append(empty);
      return;
    }
    const icons = { html: '&lt;&gt;', css: 'CSS', javascript: 'JS', python: 'Py' };
    const colors = { html: 'orange', css: 'teal', javascript: 'yellow', python: 'purple' };
    courses.forEach((course) => {
      const row = document.createElement('div');
      row.className = 'progress-course';
      const icon = document.createElement('span');
      icon.className = `course-icon ${colors[course.course_id] || 'purple'}`;
      icon.textContent = icons[course.course_id] || 'CC';
      const details = document.createElement('div');
      const title = document.createElement('strong');
      title.textContent = course.title || course.course_id || 'Course';
      const meta = document.createElement('small');
      meta.textContent = `${Number(course.completed_lessons) || 0} / ${Number(course.total_lessons) || 0} хичээл`;
      details.append(title, meta);
      const percent = clampPercent(course.progress_percent);
      const value = document.createElement('b');
      value.textContent = `${percent}%`;
      const progress = document.createElement('div');
      progress.className = 'progress-bar';
      const fill = document.createElement('i');
      fill.style.width = `${percent}%`;
      progress.append(fill);
      row.append(icon, details, value, progress);
      list.append(row);
    });
  };

  const renderGamification = (payload) => {
    const profile = payload.profile || {};
    text('[data-gamification-level]', `Level ${Number(profile.level) || 1}`);
    text('[data-gamification-xp]', `${Number(profile.total_xp) || 0} XP`);
    text('[data-gamification-streak]', `${Number(profile.current_streak) || 0} өдөр`);
    text('[data-gamification-longest]', `${Number(profile.longest_streak) || 0} өдөр`);
    text('[data-gamification-message]', Number(profile.current_streak) ? 'Сайн байна. Өнөөдрийн хэмнэлээ үргэлжлүүлээрэй.' : 'Өнөөдөр нэг жижиг challenge хийж хэмнэлээ эхлүүл.');
    const badgeList = query('[data-gamification-badges]');
    if (!badgeList) return;
    badgeList.replaceChildren();
    const badges = Array.isArray(payload.badges) ? payload.badges : [];
    if (!badges.length) {
      const placeholder = document.createElement('span');
      placeholder.className = 'badge-placeholder';
      placeholder.textContent = 'Эхний badge-ээ аваарай';
      badgeList.append(placeholder);
      return;
    }
    badges.forEach((item) => {
      const badge = document.createElement('span');
      badge.className = 'earned-badge';
      const definition = item.badges || {};
      badge.textContent = definition.title || 'Badge';
      if (definition.description) badge.title = definition.description;
      badgeList.append(badge);
    });
  };

  const showUnauthenticated = () => {
    text('[data-sync-status]', 'Нэвтэрч хадгална');
    const list = query('[data-course-progress-list]');
    if (!list) return;
    list.replaceChildren();
    const message = document.createElement('p');
    message.className = 'empty-state';
    message.append('Ахиц хадгалахын тулд эхлээд ');
    const link = document.createElement('a');
    link.href = dashboard.dataset.loginUrl || '/auth?mode=login';
    link.textContent = 'нэвтэрнэ үү';
    message.append(link, '.');
    list.append(message);
  };

  const showError = (error) => {
    text('[data-sync-status]', 'Синк холбогдсонгүй');
    const list = query('[data-course-progress-list]');
    if (!list) return;
    list.replaceChildren();
    const message = document.createElement('p');
    message.className = 'empty-state';
    message.textContent = error?.message || 'Ахиц түр ачаалагдсангүй. Дахин оролдоно уу.';
    list.append(message);
  };

  Promise.all([window.codecraftApi('/api/learning/summary'), window.codecraftApi('/api/learning/gamification')])
    .then(([summary, gamification]) => { renderSummary(summary); renderGamification(gamification); })
    .catch((error) => {
      if (error?.status === 401 || error?.message?.includes('session')) showUnauthenticated();
      else showError(error);
    });
})();
