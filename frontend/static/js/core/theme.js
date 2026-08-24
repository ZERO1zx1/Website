(() => {
  const storedTheme = localStorage.getItem('codecraft_theme');
  const systemTheme = window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
  document.documentElement.dataset.theme = storedTheme && storedTheme !== 'system' ? storedTheme : systemTheme;
})();
