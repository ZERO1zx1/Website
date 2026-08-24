(() => {
  const form = document.querySelector('[data-quiz-form]');
  if (!form || typeof window.codecraftApi !== 'function') return;

  const input = form.querySelector('[name="answer"]');
  const submit = form.querySelector('button[type="submit"]');
  const feedback = form.querySelector('[data-quiz-feedback]');
  const courseSlug = form.dataset.courseSlug;
  const lessonSlug = form.dataset.lessonSlug;

  form.addEventListener('submit', async (event) => {
    event.preventDefault();
    const answer = input.value.trim();
    if (!answer) return;
    submit.disabled = true;
    feedback.className = 'form-message';
    feedback.textContent = 'Хариуг шалгаж байна…';
    try {
      const result = await window.codecraftApi('/api/learning/quiz-attempts', {
        method: 'POST',
        body: JSON.stringify({
          course_slug: courseSlug,
          lesson_slug: lessonSlug,
          answer,
        }),
      });
      const attempt = result.quiz_attempt || result;
      const correct = attempt.correct === true || Number(attempt.score) >= Number(attempt.total_questions || 1);
      feedback.className = `form-message ${correct ? 'is-success' : 'is-error'}`;
      feedback.textContent = correct
        ? 'Зөв. Ойлголтоо өөрийн үгээр баталлаа.'
        : 'Одоохондоо зөрж байна. Хариуны тайлбарыг харахаасаа өмнө lesson-ийн жишээг дахин туршаарай.';
      if (correct) window.showToast?.('Review амжилттай.', false);
    } catch (error) {
      if (error?.status === 401) {
        window.location.href = form.closest('[data-lesson-page]')?.dataset.loginUrl || '/account/login';
        return;
      }
      feedback.className = 'form-message is-error';
      feedback.textContent = error.message || 'Review шалгах боломжгүй байна.';
    } finally {
      submit.disabled = false;
    }
  });
})();
