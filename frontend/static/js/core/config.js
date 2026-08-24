(() => {
  const root = document.documentElement;
  window.CODECRAFT_CONFIG = Object.freeze({
    apiBase: root.dataset.apiBase || '',
    backendEnabled: root.dataset.backend === 'enabled',
  });
})();
