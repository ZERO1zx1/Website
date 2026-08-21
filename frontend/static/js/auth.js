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
  form.addEventListener('submit', async (event) => {
    event.preventDefault();
    message.textContent = 'Түр хүлээнэ үү…';
    try {
      const response = await fetch(`/api/auth/${mode === 'register' ? 'register' : 'login'}`, {
        method: 'POST', credentials: 'same-origin', headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(Object.fromEntries(new FormData(form).entries())),
      });
      const payload = await response.json();
      if (!response.ok) throw new Error(payload.error?.message_mn || payload.error?.message || 'Нэвтрэхэд алдаа гарлаа.');
      localStorage.setItem('codecraft_user', JSON.stringify(payload.user || {}));
      location.assign('/dashboard');
    } catch (error) {
      message.className = 'form-message error';
      message.textContent = error.message;
    }
  });
  document.querySelector('#google-login').addEventListener('click', async () => {
    const response = await fetch('/api/auth/google/start', {credentials: 'same-origin'});
    const payload = await response.json();
    if (response.ok) location.assign(payload.url);
    else message.textContent = payload.error?.message_mn || 'Google тохиргоо бэлэн биш байна.';
  });
})();
