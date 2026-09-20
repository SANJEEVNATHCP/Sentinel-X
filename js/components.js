/* =============================================
   FRAUDLENS AI — REUSABLE COMPONENTS
   ============================================= */

/* ── Navbar Component ───────────────────────── */
function renderNavbar() {
  const user = Auth.getCurrentUser();
  const isAuth = Auth.isAuthenticated();
  const hash = window.location.hash || '#/dashboard';

  const navLinks = [
    { href: '#/dashboard', icon: '📊', label: 'Dashboard', tooltip: 'Home Dashboard' },
    { href: '#/upi', icon: '💳', label: 'UPI Analysis', tooltip: 'Analyze UPI transactions' },
    { href: '#/scam', icon: '🔍', label: 'Scam Analysis', tooltip: 'Investigate scams' },
    { href: '#/results', icon: '📋', label: 'Results', tooltip: 'View past investigations' },
    { href: '#/profile', icon: '👤', label: 'Profile', tooltip: 'Your profile' }
  ];

  return `
    <nav class="navbar" id="main-navbar" role="navigation" aria-label="Main navigation">
      <div class="navbar-inner">
        <a href="#/dashboard" class="navbar-brand" aria-label="FraudLens AI Home">
          <span class="brand-icon" aria-hidden="true">🛡</span>
          <span class="brand-text">FRAUDLENS AI</span>
        </a>

        ${isAuth ? `
          <div class="navbar-links" id="nav-links">
            ${navLinks.map(link => `
              <a href="${link.href}" 
                 class="nav-link ${hash === link.href ? 'active' : ''}" 
                 data-tooltip="${link.tooltip}"
                 aria-current="${hash === link.href ? 'page' : 'false'}">
                <span class="nav-icon" aria-hidden="true">${link.icon}</span>
                <span>${link.label}</span>
              </a>
            `).join('')}
          </div>

          <div class="navbar-user">
            <div class="user-menu-wrapper" style="position: relative;">
              <button class="user-avatar-btn" id="user-menu-btn" 
                      aria-label="User menu"
                      aria-haspopup="true">
                <span class="user-avatar" aria-hidden="true">${user ? user.name.charAt(0).toUpperCase() : 'U'}</span>
                <span class="user-name">${user ? user.name.split(' ')[0] : 'User'}</span>
                <span aria-hidden="true">▾</span>
              </button>

              <div class="user-dropdown-menu" id="user-dropdown-menu" style="display: none; position: absolute; top: calc(100% + 8px); right: 0; min-width: 200px; background: #0b1329; border: 1px solid rgba(255,255,255,0.12); border-radius: 10px; padding: 6px; box-shadow: 0 10px 25px rgba(0,0,0,0.5); z-index: 1000;">
                <div style="padding: 8px 12px; border-bottom: 1px solid rgba(255,255,255,0.08); margin-bottom: 4px;">
                  <div style="font-weight: 600; font-size: 13px; color: var(--text-primary);">${user ? user.name : 'Analyst'}</div>
                  <div style="font-size: 11px; color: var(--text-muted);">${user ? user.email : 'demo@fraudlens.ai'}</div>
                </div>
                <a href="#/profile" class="user-dropdown-item" style="display: block; padding: 8px 12px; font-size: 13px; color: var(--text-primary); text-decoration: none; border-radius: 6px;">👤 Profile</a>
                <a href="#/dashboard" class="user-dropdown-item" style="display: block; padding: 8px 12px; font-size: 13px; color: var(--text-primary); text-decoration: none; border-radius: 6px;">📊 Dashboard</a>
                <a href="#/login" class="user-dropdown-item" style="display: block; padding: 8px 12px; font-size: 13px; color: var(--text-primary); text-decoration: none; border-radius: 6px;">🔑 Switch Account</a>
                <div style="border-top: 1px solid rgba(255,255,255,0.08); margin: 4px 0;"></div>
                <button type="button" class="user-dropdown-item" onclick="handleLogout()" style="display: block; width: 100%; text-align: left; padding: 8px 12px; font-size: 13px; color: #f87171; background: none; border: none; cursor: pointer; border-radius: 6px;">🚪 Log Out</button>
              </div>
            </div>

            <button class="btn btn-ghost btn-sm" id="desktop-logout-btn" onclick="handleLogout()" style="color: #f87171; font-size: 12px; margin-left: 4px;" title="Log out of current session">
              Log Out
            </button>

            <button class="hamburger" id="hamburger-btn" 
                    aria-label="Toggle navigation menu" 
                    aria-expanded="false">
              <span></span>
              <span></span>
              <span></span>
            </button>
          </div>
        ` : `
          <div class="navbar-user">
            <a href="#/login" class="btn btn-secondary btn-sm" id="nav-login-btn">
              🔑 Sign In
            </a>
            <a href="#/register" class="btn btn-primary btn-sm" id="nav-register-btn">
              ✨ Get Started
            </a>
          </div>
        `}
      </div>
    </nav>

    ${isAuth ? `
      <div class="mobile-nav-overlay" id="mobile-nav" role="navigation" aria-label="Mobile navigation">
        ${navLinks.map(link => `
          <a href="${link.href}" 
             class="mobile-nav-link ${hash === link.href ? 'active' : ''}"
             onclick="closeMobileNav()">
            <span aria-hidden="true">${link.icon}</span>
            <span>${link.label}</span>
          </a>
        `).join('')}
        <div style="margin-top: auto; padding-top: var(--space-xl);">
          <button class="btn btn-danger w-full" onclick="handleLogout()">Log Out</button>
        </div>
      </div>
    ` : ''}
  `;
}

function initNavbar() {
  const navbar = document.getElementById('main-navbar');
  const hamburger = document.getElementById('hamburger-btn');
  const mobileNav = document.getElementById('mobile-nav');
  const userMenuBtn = document.getElementById('user-menu-btn');
  const userDropdown = document.getElementById('user-dropdown-menu');

  // Scroll behavior
  window.addEventListener('scroll', () => {
    if (navbar) {
      navbar.classList.toggle('scrolled', window.scrollY > 20);
    }
  });

  // Hamburger toggle
  if (hamburger) {
    hamburger.addEventListener('click', () => {
      const isOpen = hamburger.classList.toggle('open');
      hamburger.setAttribute('aria-expanded', isOpen);
      if (mobileNav) mobileNav.classList.toggle('open', isOpen);
    });
  }

  // User menu dropdown toggle
  if (userMenuBtn && userDropdown) {
    userMenuBtn.addEventListener('click', (e) => {
      e.stopPropagation();
      const isVisible = userDropdown.style.display === 'block';
      userDropdown.style.display = isVisible ? 'none' : 'block';
    });

    document.addEventListener('click', () => {
      userDropdown.style.display = 'none';
    });
  }
}

function closeMobileNav() {
  const hamburger = document.getElementById('hamburger-btn');
  const mobileNav = document.getElementById('mobile-nav');
  if (hamburger) hamburger.classList.remove('open');
  if (mobileNav) mobileNav.classList.remove('open');
}

function handleLogout() {
  Auth.logout();
  closeMobileNav();
  window.location.hash = '#/login';
  Toast.info('You have been logged out.');
}

/* ── Risk Badge ─────────────────────────────── */
function getRiskLevel(score) {
  if (score >= 70) return { level: 'HIGH RISK', class: 'high', color: 'var(--risk-high)' };
  if (score >= 50) return { level: 'SUSPICIOUS', class: 'suspicious', color: 'var(--risk-suspicious)' };
  if (score >= 30) return { level: 'MODERATE', class: 'moderate', color: 'var(--risk-moderate)' };
  return { level: 'LOW', class: 'low', color: 'var(--risk-low)' };
}

function renderRiskBadge(score) {
  const risk = getRiskLevel(score);
  return `<span class="badge badge-${risk.class}" aria-label="Risk level: ${risk.level}">
    <span aria-hidden="true">${risk.class === 'high' ? '🔴' : risk.class === 'suspicious' ? '🟠' : risk.class === 'moderate' ? '🟡' : '🟢'}</span>
    ${risk.level}
  </span>`;
}

/* ── Loading Animation ──────────────────────── */
function renderLoadingAnimation(steps, currentStep = 0) {
  return `
    <div class="analysis-progress" role="status" aria-live="polite">
      <div class="analysis-progress-header">
        <span class="progress-icon" aria-hidden="true">◉</span>
        <h3>Investigating Signals...</h3>
      </div>
      <div class="progress-steps">
        ${steps.map((step, i) => {
          let status = 'pending';
          let icon = '○';
          if (i < currentStep) { status = 'done'; icon = '✓'; }
          else if (i === currentStep) { status = 'active'; icon = '◉'; }
          return `
            <div class="progress-step ${status}">
              <span class="step-icon" aria-hidden="true">${icon}</span>
              <span>${step}</span>
            </div>
          `;
        }).join('')}
      </div>
    </div>
  `;
}

/* ── Empty State ────────────────────────────── */
function renderEmptyState(icon, title, description, actionText, actionHash) {
  return `
    <div class="empty-state">
      <div class="empty-icon" aria-hidden="true">${icon}</div>
      <h3>${title}</h3>
      <p>${description}</p>
      ${actionText ? `
        <a href="${actionHash || '#/dashboard'}" class="btn btn-primary">
          ${actionText}
        </a>
      ` : ''}
    </div>
  `;
}

/* ── Confirmation Modal ─────────────────────── */
function showConfirmModal(title, message, onConfirm) {
  const backdrop = document.createElement('div');
  backdrop.className = 'modal-backdrop';
  backdrop.id = 'confirm-backdrop';

  const modal = document.createElement('div');
  modal.className = 'modal';
  modal.setAttribute('role', 'dialog');
  modal.setAttribute('aria-modal', 'true');
  modal.setAttribute('aria-labelledby', 'confirm-title');
  modal.innerHTML = `
    <div class="modal-header">
      <h3 class="modal-title" id="confirm-title">${title}</h3>
      <button class="modal-close" id="confirm-close" aria-label="Close dialog">&times;</button>
    </div>
    <p style="margin-bottom: var(--space-lg); font-size: var(--fs-sm);">${message}</p>
    <div class="confirm-actions">
      <button class="btn btn-ghost" id="confirm-cancel">Cancel</button>
      <button class="btn btn-danger" id="confirm-ok">✓ Confirm &amp; Delete</button>
    </div>
  `;

  document.body.appendChild(backdrop);
  document.body.appendChild(modal);

  const close = () => {
    backdrop.remove();
    modal.remove();
  };

  backdrop.addEventListener('click', close);
  modal.querySelector('#confirm-close').addEventListener('click', close);
  modal.querySelector('#confirm-cancel').addEventListener('click', close);
  modal.querySelector('#confirm-ok').addEventListener('click', () => {
    close();
    if (onConfirm) onConfirm();
  });
}

/* ── Privacy Modal ──────────────────────────── */
function showPrivacyModal() {
  const backdrop = document.createElement('div');
  backdrop.className = 'modal-backdrop';

  const modal = document.createElement('div');
  modal.className = 'modal';
  modal.setAttribute('role', 'dialog');
  modal.setAttribute('aria-modal', 'true');
  modal.innerHTML = `
    <div class="modal-header">
      <h3 class="modal-title">Data Privacy</h3>
      <button class="modal-close" aria-label="Close dialog">&times;</button>
    </div>
    <div style="font-size: var(--fs-sm); color: var(--text-secondary); line-height: 1.7;">
      <p style="margin-bottom: var(--space-md);">FraudLens AI is designed around session-based analysis. Your data privacy is central to our approach:</p>
      <p style="margin-bottom: var(--space-md);"><strong style="color: var(--text-white);">🔒 Secure Processing</strong><br>All analysis happens within your session. Data is processed locally where possible.</p>
      <p style="margin-bottom: var(--space-md);"><strong style="color: var(--text-white);">🗑 Session Data Deletion</strong><br>When you end an investigation session, sensitive raw data can be permanently deleted.</p>
      <p><strong style="color: var(--text-white);">📋 Derived Results Only</strong><br>Only the derived investigation results (risk scores, evidence summaries) are stored for your reference.</p>
    </div>
  `;

  document.body.appendChild(backdrop);
  document.body.appendChild(modal);

  const close = () => { backdrop.remove(); modal.remove(); };
  backdrop.addEventListener('click', close);
  modal.querySelector('.modal-close').addEventListener('click', close);
}

/* ── SVG Risk Chart ─────────────────────────── */
function renderRiskChart(investigations) {
  if (!investigations || investigations.length === 0) {
    return `<div class="overview-empty">
      <p>Your risk activity chart will appear here after your first investigation.</p>
    </div>`;
  }

  const recent = investigations.slice(0, 10).reverse();
  const width = 800;
  const height = 220;
  const padding = { top: 20, right: 30, bottom: 40, left: 45 };
  const chartW = width - padding.left - padding.right;
  const chartH = height - padding.top - padding.bottom;

  const xStep = chartW / Math.max(recent.length - 1, 1);

  const points = recent.map((inv, i) => ({
    x: padding.left + i * xStep,
    y: padding.top + chartH - (inv.riskScore / 100) * chartH,
    score: inv.riskScore,
    date: new Date(inv.createdAt).toLocaleDateString('en-US', { month: 'short', day: 'numeric' }),
    id: inv.id
  }));

  const pathD = points.map((p, i) => `${i === 0 ? 'M' : 'L'} ${p.x} ${p.y}`).join(' ');
  const areaD = pathD + ` L ${points[points.length - 1].x} ${padding.top + chartH} L ${points[0].x} ${padding.top + chartH} Z`;

  // Y-axis labels
  const yLabels = [0, 25, 50, 75, 100];

  return `
    <svg viewBox="0 0 ${width} ${height}" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Risk activity chart">
      <defs>
        <linearGradient id="areaGrad" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stop-color="rgba(59,130,246,0.2)"/>
          <stop offset="100%" stop-color="rgba(59,130,246,0)"/>
        </linearGradient>
      </defs>

      <!-- Grid lines -->
      ${yLabels.map(v => {
        const y = padding.top + chartH - (v / 100) * chartH;
        return `
          <line x1="${padding.left}" y1="${y}" x2="${width - padding.right}" y2="${y}" 
                stroke="rgba(255,255,255,0.04)" stroke-width="1"/>
          <text x="${padding.left - 10}" y="${y + 4}" text-anchor="end" 
                fill="rgba(139,153,176,0.5)" font-size="10" font-family="Inter">${v}</text>
        `;
      }).join('')}

      <!-- Area fill -->
      <path d="${areaD}" fill="url(#areaGrad)"/>

      <!-- Line -->
      <path d="${pathD}" fill="none" stroke="rgba(59,130,246,0.6)" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>

      <!-- Points -->
      ${points.map(p => {
        const risk = getRiskLevel(p.score);
        const color = risk.class === 'high' ? '#ef4444' : risk.class === 'suspicious' ? '#f97316' : risk.class === 'moderate' ? '#eab308' : '#22c55e';
        return `
          <circle cx="${p.x}" cy="${p.y}" r="4" fill="${color}" stroke="var(--bg-card)" stroke-width="2" 
                  style="cursor:pointer" data-inv-id="${p.id}"/>
          <text x="${p.x}" y="${height - 8}" text-anchor="middle" fill="rgba(139,153,176,0.5)" 
                font-size="10" font-family="Inter">${p.date}</text>
        `;
      }).join('')}
    </svg>
  `;
}

/* ── Utility: Format Date ───────────────────── */
function formatDate(isoString) {
  const d = new Date(isoString);
  return d.toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' });
}

function formatTimeAgo(isoString) {
  const diff = Date.now() - new Date(isoString).getTime();
  const mins = Math.floor(diff / 60000);
  if (mins < 60) return `${mins}m ago`;
  const hrs = Math.floor(mins / 60);
  if (hrs < 24) return `${hrs}h ago`;
  const days = Math.floor(hrs / 24);
  return `${days}d ago`;
}
