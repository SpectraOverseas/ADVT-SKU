const dashboardMap = {
  '2025': 'SKU WISE AD SPEND.html',
  '2026': 'SKU WISE AD SPEND 2026.html'
};

const isAuthenticated = sessionStorage.getItem('isAuthenticated') === 'true';
if (!isAuthenticated) {
  window.location.href = 'index.html';
}

const dashboardCard = document.getElementById('dashboardCard');
const yearSelection = document.getElementById('yearSelection');

dashboardCard.addEventListener('click', () => {
  yearSelection.classList.remove('is-hidden');
  dashboardCard.setAttribute('aria-expanded', 'true');
});

yearSelection.addEventListener('click', (event) => {
  const target = event.target;
  if (!(target instanceof HTMLElement)) {
    return;
  }
  const year = target.dataset.year;
  if (!year || !dashboardMap[year]) {
    return;
  }
  window.location.href = dashboardMap[year];
});
