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
  const emailCodeToggle = document.querySelector('#email-code-toggle');
  const emailCodePanel = document.querySelector('#email-code-panel');
  const otpRequestForm = document.querySelector('#email-code-request-form');
  const otpVerifyForm = document.querySelector('#email-code-verify-form');
  const otpEmail = document.querySelector('#otp-email');
  const otpCode = document.querySelector('#otp-code');
  const otpMessage = document.querySelector('#otp-message');
  let otpChallenge = '';
  let otpAddress = '';

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

  function showMessage(target, text, isError = false) {
    target.className = isError ? 'form-message error' : 'form-message';
    target.textContent = text;
  }

  function saveUser(payload) {
    localStorage.setItem('codecraft_user', JSON.stringify(payload.user || {}));
    location.assign('/dashboard');
  }

  document.querySelector('#google-login')?.addEventListener('click', async () => {
    if (backendUnavailable()) {
      showMessage(message, 'Local preview горимд auth backend асаагүй байна.', true);
      return;
    }
    try {
      const response = await fetch('/api/auth/google/start', {credentials: 'same-origin'});
      const payload = await readPayload(response);
      if (!response.ok) throw new Error(payload.error?.message_mn || 'Google login тохиргоо бэлэн биш байна.');
      window.location.assign(payload.url);
    } catch (error) {
      showMessage(message, error.message, true);
    }
  });

  emailCodeToggle?.addEventListener('click', () => {
    const open = emailCodePanel.hidden;
    emailCodePanel.hidden = !open;
    form.hidden = open;
    emailCodeToggle.textContent = open ? 'Нууц үгээр нэвтрэх' : 'Gmail security code-оор нэвтрэх';
    if (open) otpEmail.focus();
  });

  form.addEventListener('submit', async (event) => {
    event.preventDefault();
    showMessage(message, 'Түр хүлээнэ үү…');
    if (backendUnavailable()) {
      showMessage(message, 'Backend auth асаагүй байна. Server болон .env тохиргоог шалгана уу.', true);
      return;
    }
    try {
      const response = await fetch(`/api/auth/${mode === 'register' ? 'register' : 'login'}`, {
        method: 'POST', credentials: 'same-origin', headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(Object.fromEntries(new FormData(form).entries())),
      });
      const payload = await readPayload(response);
      if (!response.ok) throw new Error(payload.error?.message_mn || payload.error?.message || 'Нэвтрэхэд алдаа гарлаа.');
      saveUser(payload);
    } catch (error) {
      showMessage(message, error.message, true);
    }
  });

  otpRequestForm?.addEventListener('submit', async (event) => {
    event.preventDefault();
    showMessage(otpMessage, 'Gmail рүү security code илгээж байна…');
    if (backendUnavailable()) {
      showMessage(otpMessage, 'Backend auth асаагүй байна. Server болон .env тохиргоог шалгана уу.', true);
      return;
    }
    try {
      const email = String(new FormData(otpRequestForm).get('email') || '').trim().toLowerCase();
      const response = await fetch('/api/auth/otp/request', {
        method: 'POST', credentials: 'same-origin', headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({email}),
      });
      const payload = await readPayload(response);
      if (!response.ok) throw new Error(payload.error?.message_mn || payload.error?.message || 'Security code илгээгдсэнгүй.');
      otpAddress = email;
      otpChallenge = payload.challenge || '';
      otpVerifyForm.hidden = false;
      otpCode.focus();
      showMessage(otpMessage, `${email} хаяг руу код илгээгдлээ. 10 минутын дотор оруулна уу.`);
    } catch (error) {
      showMessage(otpMessage, error.message, true);
    }
  });

  otpVerifyForm?.addEventListener('submit', async (event) => {
    event.preventDefault();
    if (!otpChallenge || !otpAddress) {
      showMessage(otpMessage, 'Эхлээд Gmail рүү security code авна уу.', true);
      return;
    }
    showMessage(otpMessage, 'Код шалгаж байна…');
    try {
      const code = String(new FormData(otpVerifyForm).get('code') || '').trim();
      const response = await fetch('/api/auth/otp/verify', {
        method: 'POST', credentials: 'same-origin', headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({email: otpAddress, challenge: otpChallenge, code}),
      });
      const payload = await readPayload(response);
      if (!response.ok) throw new Error(payload.error?.message_mn || payload.error?.message || 'Security code буруу байна.');
      saveUser(payload);
    } catch (error) {
      showMessage(otpMessage, error.message, true);
    }
  });
})();
