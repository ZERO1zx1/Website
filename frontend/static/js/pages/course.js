(() => {
  const page = document.querySelector('[data-course-page]');
  if (!page || typeof window.codecraftApi !== 'function') return;

  const courseSlug = page.dataset.courseSlug;
  const rows = [...page.querySelectorAll('[data-lesson-slug]')];
  const progressValue = page.querySelector('[data-course-progress-value]');
  const progressBar = page.querySelector('[data-course-progress-bar]');
  const status = page.querySelector('[data-course-progress-status]');

  const showLogin = () => {
    if (status) status.textContent = 'Ахиц хадгалахын тулд нэвтэрнэ үү.';
  };

  const render = (summary) => {
    const course = (summary.courses || []).find((item) => item.course_id === courseSlug);
    if (!course) return;
    const completed = new Set(summary.completed_lesson_keys || []);
    const currentKey = `${courseSlug}:`;
    let nextFound = false;
    rows.forEach((row) => {
      const key = `${currentKey}${row.dataset.lessonSlug}`;
      const isComplete = completed.has(key);
      const isNext = !isComplete && !nextFound;
      if (isNext) nextFound = true;
      row.classList.toggle('is-complete', isComplete);
      row.classList.toggle('is-next', isNext);
      const marker = row.querySelector('.lesson-check');
      if (marker) marker.textContent = isComplete ? '✓' : isNext ? '→' : '○';
      if (isNext) row.setAttribute('aria-current', 'step');
      else row.removeAttribute('aria-current');
    });
    if (progressValue) progressValue.textContent = `${course.completed_lessons} / ${course.total_lessons}`;
    if (progressBar) progressBar.style.width = `${Math.max(0, Math.min(100, Number(course.progress_percent) || 0))}%`;
    if (status) status.textContent = course.next_lesson_title ? `Дараагийн алхам: ${course.next_lesson_title}` : 'Энэ замыг бүрэн дуусгалаа.';
  };

  window.codecraftApi('/api/learning/summary')
    .then(render)
    .catch((error) => {
      if (error?.status === 401) showLogin();
      else if (status) status.textContent = 'Ахицын мэдээллийг ачаалж чадсангүй.';
    });
})();
