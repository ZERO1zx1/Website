(() => {
  'use strict';
  const config = window.CODECRAFT_CONFIG || {};
  const root = document.documentElement;
  const storedTheme = localStorage.getItem('codecraft_theme');
  const getSystemTheme = () => window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
  const applyTheme = (theme, save = true) => {
    const resolved = theme === 'system' || !theme ? getSystemTheme() : theme;
    root.dataset.theme = resolved;
    if (save && theme) localStorage.setItem('codecraft_theme', theme);
  };
  applyTheme(storedTheme || 'system', false);
  
  window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (e) => {
    if (!localStorage.getItem('codecraft_theme') || localStorage.getItem('codecraft_theme') === 'system') {
      applyTheme('system', false);
    }
  });

  document.querySelectorAll('[data-theme-toggle]').forEach((button) => {
    button.addEventListener('click', () => {
      const current = root.dataset.theme;
      const next = current === 'dark' ? 'light' : 'dark';
      applyTheme(next, true);
    });
  });
  const menuButton = document.querySelector('[data-mobile-menu]');
  const menuPanel = document.querySelector('[data-mobile-menu-panel]');
  if (menuButton && menuPanel) {
    menuButton.addEventListener('click', () => {
      const open = menuPanel.getAttribute('aria-hidden') === 'true';
      menuPanel.setAttribute('aria-hidden', String(!open));
      menuPanel.classList.toggle('is-open', open);
      menuButton.setAttribute('aria-expanded', String(open));
    });
  }
  window.showToast = (message, error = false) => {
    const toast = document.querySelector('[data-toast]');
    if (!toast) return;
    toast.textContent = message;
    toast.className = `toast is-visible${error ? ' is-error' : ''}`;
    window.clearTimeout(window.__toastTimer);
    window.__toastTimer = window.setTimeout(() => toast.classList.remove('is-visible'), 3200);
  };
  window.codecraftApi = async (path, options = {}) => {
    const headers = {'Content-Type': 'application/json', ...(options.headers || {})};
    const response = await fetch(`${config.apiBase || ''}${path}`, {
      ...options,
      credentials: 'same-origin',
      headers,
    });
    let payload = {};
    try { payload = await response.json(); } catch { payload = {error: await response.text()}; }
    if (!response.ok) throw new Error(payload.message_mn || payload.error || 'Хүсэлтийг гүйцэтгэх боломжгүй байна.');
    return payload;
  };
  const user = JSON.parse(localStorage.getItem('codecraft_user') || '{}');
  document.querySelectorAll('[data-user-name]').forEach((element) => { element.textContent = user.name || user.email?.split('@')[0] || 'суралцагч'; });
})();
