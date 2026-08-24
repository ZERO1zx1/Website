(() => {
  const filters = document.querySelectorAll('[data-filter]');
  const cards = document.querySelectorAll('.course-card[data-category]');
  if (!filters.length || !cards.length) return;

  filters.forEach((button) => {
    button.addEventListener('click', () => {
      filters.forEach((item) => {
        item.classList.toggle('is-active', item === button);
        item.setAttribute('aria-pressed', item === button ? 'true' : 'false');
      });
      const value = button.dataset.filter;
      cards.forEach((card) => {
        card.hidden = value !== 'all' && card.dataset.category !== value;
      });
    });
  });
})();
