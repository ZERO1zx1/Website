(() => {
  const editor = document.querySelector('#code-editor');
  const output = document.querySelector('#output-content');
  const status = document.querySelector('#output-status');
  const language = document.querySelector('#editor-language');
  const fileName = document.querySelector('#editor-file-name');
  const title = document.querySelector('#challenge-title');
  const hook = document.querySelector('#challenge-hook');
  const xp = document.querySelector('#challenge-xp');
  const hintPanel = document.querySelector('#hint-panel');
  const hintContent = document.querySelector('#hint-content');
  const challenges = [...document.querySelectorAll('.challenge')];
  if (!editor || !output || !status || !language) return;

  const initial = Object.fromEntries(challenges.map((challenge) => [challenge.dataset.id, challenge.dataset.starter || '']));
  let active = document.querySelector('.challenge.is-active');
  const emptyOutput = 'Кодоо ажиллуулахад үр дүн энд харагдана.';

  const setFileName = (value) => {
    fileName.textContent = `challenge.${value === 'javascript' ? 'js' : value}`;
  };

  const resetOutput = () => {
    output.textContent = emptyOutput;
    status.textContent = 'Бэлэн';
  };

  const selectChallenge = (challenge) => {
    challenges.forEach((item) => {
      const selected = item === challenge;
      item.classList.toggle('is-active', selected);
      item.setAttribute('aria-pressed', selected ? 'true' : 'false');
    });
    active = challenge;
    language.value = challenge.dataset.language || 'python';
    editor.value = challenge.dataset.starter || '';
    setFileName(language.value);
    title.textContent = challenge.dataset.title || 'Challenge';
    hook.textContent = challenge.dataset.hook || '';
    xp.textContent = challenge.dataset.xp ? `+${challenge.dataset.xp} XP` : 'LESSON';
    hintContent.textContent = challenge.dataset.hint || 'Өөрчлөлтөө жижиг хэсгээр хийж дахин ажиллуулаарай.';
    hintPanel.hidden = true;
    resetOutput();
  };

  const readPayload = async (response) => {
    const raw = await response.text();
    try {
      return raw ? JSON.parse(raw) : {};
    } catch {
      return {error: `Сервер JSON биш response буцаалаа (HTTP ${response.status}).`};
    }
  };

  challenges.forEach((challenge) => {
    challenge.setAttribute('aria-pressed', challenge.classList.contains('is-active') ? 'true' : 'false');
    challenge.addEventListener('click', () => selectChallenge(challenge));
  });

  language.addEventListener('change', () => {
    const sameLanguage = challenges.find((item) => item.dataset.language === language.value);
    if (sameLanguage) selectChallenge(sameLanguage);
    setFileName(language.value);
  });

  document.querySelector('#show-hint')?.addEventListener('click', () => {
    hintPanel.hidden = !hintPanel.hidden;
  });

  document.querySelector('#reset-code')?.addEventListener('click', () => {
    if (active) editor.value = initial[active.dataset.id] || '';
    resetOutput();
  });

  document.querySelector('#run-code')?.addEventListener('click', async () => {
    status.textContent = 'Ажиллаж байна…';
    output.textContent = 'Түр хүлээнэ үү…';
    try {
      if (window.CODECRAFT_CONFIG.backendEnabled && active?.dataset.id) {
        const response = await fetch(`${window.CODECRAFT_CONFIG.apiBase}/api/submissions/run`, {
          method: 'POST',
          headers: {'Content-Type': 'application/json'},
          credentials: 'same-origin',
          body: JSON.stringify({
            challenge_id: active?.dataset.id,
            language: language.value,
            code: editor.value,
          }),
        });
        const payload = await readPayload(response);
        if (!response.ok) throw new Error(payload.error?.message_mn || payload.error || 'Нэвтэрсний дараа ажиллуулна уу.');
        const summary = payload.total_tests ? `${payload.passed_tests}/${payload.total_tests} test pass` : '';
        output.textContent = summary ? `${summary}\n\n${payload.output || payload.stdout || JSON.stringify(payload, null, 2)}` : (payload.output || payload.stdout || JSON.stringify(payload, null, 2));
      } else {
        output.textContent = 'Demo output\n\nCodeCraft Academy-д тавтай морил!\n\nBackend холбогдсон үед энд бодит үр дүн гарна.';
      }
      status.textContent = 'Дууслаа';
      window.showToast?.('Код амжилттай ажиллалаа.');
    } catch (error) {
      output.textContent = error.message;
      status.textContent = 'Алдаа';
      window.showToast?.(error.message, true);
    }
  });

  document.querySelector('#submit-code')?.addEventListener('click', async (event) => {
    const button = event.currentTarget;
    const rewardStatus = document.querySelector('#reward-status');
    if (!window.CODECRAFT_CONFIG.backendEnabled || !active?.dataset.id) {
      status.textContent = 'Backend шаардлагатай';
      output.textContent = 'Шалгуулахын тулд backend болон sandbox тохиргоотой орчинд ажиллана уу.';
      return;
    }
    button.disabled = true;
    status.textContent = 'Шалгаж байна…';
    if (rewardStatus) rewardStatus.textContent = '';
    try {
      const response = await fetch(`${window.CODECRAFT_CONFIG.apiBase}/api/submissions/catalog`, {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        credentials: 'same-origin',
        body: JSON.stringify({challenge_id: active.dataset.id, language: language.value, code: editor.value}),
      });
      const payload = await readPayload(response);
      if (!response.ok) throw new Error(payload.error?.message_mn || payload.error || 'Шалгалт хийх боломжгүй байна.');
      const results = payload.results || {};
      const passed = Number(results.passed_tests) || 0;
      const total = Number(results.total_tests) || 0;
      output.textContent = `${passed}/${total} test pass\n\n${JSON.stringify(results.test_results || [], null, 2)}`;
      status.textContent = results.status === 'accepted' ? 'Accepted' : 'Дахин оролдоорой';
      const xpReward = payload.reward?.xp?.xp_amount || 0;
      if (rewardStatus) rewardStatus.textContent = results.status === 'accepted' ? `+${xpReward} XP` : 'XP авахын тулд бүх test-ийг pass болгоно.';
      window.showToast?.(results.status === 'accepted' ? 'Challenge амжилттай. XP нэмэгдлээ.' : 'Зарим test зөрж байна.', results.status !== 'accepted');
    } catch (error) {
      status.textContent = 'Алдаа';
      output.textContent = error.message;
      window.showToast?.(error.message, true);
    } finally {
      button.disabled = false;
    }
  });
})();
