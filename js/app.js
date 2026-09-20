/* =============================================
   FRAUDLENS AI — APPLICATION ROUTER
   ============================================= */

const routes = {
  '#/dashboard': { render: renderHomePage, init: initHomePage, cleanup: cleanupHomePage, auth: true, title: 'Dashboard' },
  '#/upi': { render: renderUPIPage, init: initUPIPage, cleanup: cleanupUPIPage, auth: true, title: 'UPI Analysis' },
  '#/scam': { render: renderScamPage, init: initScamPage, cleanup: cleanupScamPage, auth: true, title: 'Scam Investigation' },
  '#/results': { render: renderResultsPage, init: initResultsPage, cleanup: cleanupResultsPage, auth: true, title: 'Results' },
  '#/profile': { render: renderProfilePage, init: initProfilePage, cleanup: cleanupProfilePage, auth: true, title: 'Profile' },
  '#/login': { render: renderLoginPage, init: initLoginPage, cleanup: cleanupLoginPage, auth: false, title: 'Sign In' },
  '#/register': { render: renderRegisterPage, init: initRegisterPage, cleanup: cleanupRegisterPage, auth: false, title: 'Create Account' },
};

let currentRoute = null;

function getRouteKey(hash) {
  // Strip query params for route matching
  return hash.split('?')[0] || '#/dashboard';
}

function mountPage() {
  const hash = window.location.hash || '#/dashboard';
  const routeKey = getRouteKey(hash);
  const route = routes[routeKey];

  // Default redirect
  if (!route) {
    window.location.hash = '#/dashboard';
    return;
  }

  // Auth guard for protected routes
  if (route.auth && !Auth.isAuthenticated()) {
    window.location.hash = '#/login';
    return;
  }

  // Cleanup previous route
  if (currentRoute && currentRoute.cleanup) {
    currentRoute.cleanup();
  }

  // Update page title
  document.title = `${route.title} — FraudLens AI`;

  // Render navbar
  const navContainer = document.getElementById('app-nav');
  const mainContainer = document.getElementById('app-main');

  // Render navigation bar
  navContainer.innerHTML = renderNavbar();
  initNavbar();

  // Auth pages have custom container styling
  if (!route.auth) {
    mainContainer.style.paddingTop = '0';
    mainContainer.innerHTML = route.render();
  } else {
    mainContainer.style.paddingTop = '';
    mainContainer.innerHTML = route.render();
  }

  // Init page
  if (route.init) route.init();

  currentRoute = route;

  // Scroll to top
  window.scrollTo(0, 0);
}

// Listen for hash changes
window.addEventListener('hashchange', mountPage);

// Initial mount
window.addEventListener('DOMContentLoaded', () => {
  // Map pathname paths (/login, /register) to hashes if needed
  const path = window.location.pathname.toLowerCase();
  if (path.endsWith('/login') && !window.location.hash) {
    window.location.hash = '#/login';
    return;
  } else if (path.endsWith('/register') && !window.location.hash) {
    window.location.hash = '#/register';
    return;
  }

  // Set default hash if none
  if (!window.location.hash) {
    window.location.hash = Auth.isAuthenticated() ? '#/dashboard' : '#/login';
  } else {
    mountPage();
  }
});
