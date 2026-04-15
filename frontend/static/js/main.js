const pages = {
  home: () => import('./home.js'),
  dividends: () => import('./dividends.js'),
};

const container = document.getElementById('page');
let currentPage = null;

async function navigate(path) {
  const id = path.replace(/^\//, '') || 'home';
  const loader = pages[id] ?? pages.home;

  if (currentPage?.unmount) currentPage.unmount();

  const [html, mod] = await Promise.all([
    fetch(`/${id}`).then(r => r.text()),
    loader(),
  ]);

  container.innerHTML = html;
  currentPage = mod;
  mod.mount(container);

  document.querySelectorAll('.tab').forEach(tab => {
    tab.classList.toggle('active', tab.getAttribute('href') === id);
  });
}

document.querySelectorAll('.tab').forEach(tab => {
  tab.addEventListener('click', (e) => {
    e.preventDefault();
    const path = tab.getAttribute('href');
    history.pushState(null, '', '/' + path);
    navigate(path);
  });
});

window.addEventListener('popstate', () => navigate(location.pathname));

navigate(location.pathname);
