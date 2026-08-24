(() => {
  const params = new URLSearchParams(location.search);
  let mode = params.get('mode') === 'register' ? 'register' : 'login';
  const form = document.querySelector('#auth-form');
  const message = document.querySelector('#auth-message');
  const nameField = document.querySelector('#name-field');
  const consent = document.querySelector('#consent-field');
  const submit = document.querySelector('#auth-submit');
  const title = document.querySelector('#auth-title');
  const subtitle = document.querySelector('#auth-subtitle');

  function setMode(nextMode) {
    mode = nextMode;
    const register = mode === 'register';
    document.querySelectorAll('[data-auth-mode]').forEach((item) => item.classList.toggle('is-active', item.dataset.authMode === mode));
    nameField.hidden = !register;
    consent.hidden = !register;
    title.textContent = register ? 'Өөрийн замаа эхлүүл.' : 'Тавтай морил.';
    subtitle.textContent = register ? 'Үнэгүй бүртгэлээр ахицаа хадгал.' : 'Суралцах орон зайдаа үргэлжлүүлэн нэвтэр.';
    submit.textContent = register ? 'Бүртгэл үүсгэх →' : 'Нэвтрэх →';
  }

  document.querySelectorAll('[data-auth-mode]').forEach((item) => item.addEventListener('click', () => setMode(item.dataset.authMode)));
  setMode(mode);
  async function readPayload(response) {
    const raw = await response.text();
    try { return raw ? JSON.parse(raw) : {}; } catch { return {error: {message_mn: `Сервер JSON биш response буцаалаа (HTTP ${response.status}).`}}; }
  }
  function backendUnavailable() {
    return window.CODECRAFT_CONFIG?.backendEnabled === false;
  }
  document.querySelector('#google-login')?.addEventListener('click', async () => {
    if (backendUnavailable()) {
      message.className = 'form-message error';
      message.textContent = 'Local preview горимд auth backend асаагүй байна.';
      return;
    }
    try {
      const response = await fetch('/api/auth/google/start', {credentials: 'same-origin'});
      const payload = await readPayload(response);
      if (!response.ok) throw new Error(payload.error?.message_mn || 'Google login тохиргоо бэлэн биш байна.');
      window.location.assign(payload.url);
    } catch (error) {
      message.className = 'form-message error';
      message.textContent = error.message;
    }
  });

  form.addEventListener('submit', async (event) => {
    event.preventDefault();
    message.className = 'form-message';
    message.textContent = 'Түр хүлээнэ үү…';
    if (backendUnavailable()) {
      message.className = 'form-message error';
      message.textContent = 'Local preview горимд auth backend асаагүй байна. Supabase тохируулсны дараа нэвтрэлт ажиллана.';
      return;
    }
    try {
      const response = await fetch(`/api/auth/${mode === 'register' ? 'register' : 'login'}`, {
        method: 'POST', credentials: 'same-origin', headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(Object.fromEntries(new FormData(form).entries())),
      });
      const payload = await readPayload(response);
      if (!response.ok) throw new Error(payload.error?.message_mn || payload.error?.message || 'Нэвтрэхэд алдаа гарлаа.');
      localStorage.setItem('codecraft_user', JSON.stringify(payload.user || {}));
      location.assign('/dashboard');
    } catch (error) {
      message.className = 'form-message error';
      message.textContent = error.message;
    }
  });
})();
