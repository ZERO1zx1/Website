(() => {
  'use strict';

  const lesson = document.querySelector('[data-lesson-page]');
  if (!lesson || typeof window.codecraftApi !== 'function') return;

  const courseSlug = lesson.dataset.courseSlug;
  const lessonSlug = lesson.dataset.lessonSlug;
  const completionButton = lesson.querySelector('[data-completion-button]');
  const progressValue = lesson.querySelector('[data-lesson-progress-value]');
  const progressBar = lesson.querySelector('[data-lesson-progress-bar]');
  const progressStatus = lesson.querySelector('[data-lesson-progress-status]');
  let isCompleted = false;

  const renderProgress = (summary) => {
    const course = (summary.courses || []).find((item) => item.course_id === courseSlug);
    isCompleted = (summary.completed_lesson_keys || []).includes(`${courseSlug}:${lessonSlug}`);
    if (course) {
      if (progressValue) progressValue.textContent = `${course.completed_lessons} / ${course.total_lessons}`;
      if (progressBar) progressBar.style.width = `${Math.max(0, Math.min(100, Number(course.progress_percent) || 0))}%`;
    }
    if (progressStatus) progressStatus.textContent = isCompleted ? 'Энэ хичээл дууссан байна.' : 'Энэ хичээл дуусаагүй байна.';
    if (completionButton) {
      completionButton.textContent = isCompleted ? 'Дууссан ✓' : 'Дууссанд тооцох';
      completionButton.classList.toggle('is-complete', isCompleted);
      completionButton.setAttribute('aria-pressed', String(isCompleted));
    }
  };

  const loadProgress = async () => {
    try {
      renderProgress(await window.codecraftApi('/api/learning/summary'));
    } catch (error) {
      if (progressStatus) progressStatus.textContent = error?.status === 401 ? 'Ахиц хадгалахын тулд нэвтэрнэ үү.' : 'Ахицын мэдээллийг ачаалж чадсангүй.';
      if (completionButton && error?.status === 401) completionButton.textContent = 'Нэвтэрч хадгалах';
    }
  };

  completionButton?.addEventListener('click', async () => {
    completionButton.disabled = true;
    try {
      const nextState = !isCompleted;
      const payload = await window.codecraftApi('/api/learning/lessons', {
        method: 'PUT',
        body: JSON.stringify({ course_slug: courseSlug, lesson_slug: lessonSlug, completed: nextState }),
      });
      renderProgress(await window.codecraftApi('/api/learning/summary'));
      window.showToast(payload.message_mn || (nextState ? 'Хичээлийг дууссанд тооцлоо.' : 'Хичээлийн тэмдэглэгээг цуцаллаа.'));
    } catch (error) {
      if (error?.status === 401) {
        window.location.href = lesson.dataset.loginUrl || '/auth?mode=login';
        return;
      }
      window.showToast(error.message, true);
    } finally {
      completionButton.disabled = false;
    }
  });

  lesson.querySelector('[data-copy-code]')?.addEventListener('click', async (event) => {
    const code = lesson.querySelector('.code-block code')?.textContent || '';
    try {
      await navigator.clipboard.writeText(code);
      event.currentTarget.textContent = 'Хууллаа ✓';
      window.setTimeout(() => { event.currentTarget.textContent = 'Хуулах'; }, 2000);
    } catch {
      event.currentTarget.textContent = 'Хуулах боломжгүй';
    }
  });

  loadProgress();
})();
