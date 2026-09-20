/* =============================================
   FRAUDLENS AI — PROFILE PAGE
   ============================================= */

function renderProfilePage() {
  const user = Auth.getCurrentUser();
  const stats = InvestigationStore.getStats();
  const recent = InvestigationStore.getRecent(1);
  const lastInv = recent.length > 0 ? formatDate(recent[0].createdAt) : 'None yet';

  if (!user) return `<div class="container" style="padding-top: var(--space-3xl);">
    ${renderEmptyState('👤', 'Not logged in', 'Please log in to view your profile.', 'SIGN IN', '#/login')}
  </div>`;

  const initials = user.name.split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2);

  return `
    <div class="page-wrapper">
      <div class="container">
        <div class="page-header">
          <a href="#/dashboard" class="btn btn-ghost btn-sm" style="margin-bottom: var(--space-md);">← Back to Dashboard</a>
          <h1>Your Security <span class="text-gradient">Profile</span></h1>
          <div class="divider"></div>
          <p>Manage your account and control your FraudLens experience.</p>
        </div>

        <div class="profile-page">
          <!-- Profile Card -->
          <div class="profile-card reveal">
            <div class="profile-avatar" aria-hidden="true">${initials}</div>
            <div class="profile-info">
              <h2>${user.name}</h2>
              <p class="profile-email">${user.email}</p>
              <p class="profile-joined">Account created: ${formatDate(user.createdAt)}</p>
            </div>
          </div>

          <!-- Activity Summary -->
          <div class="profile-section reveal">
            <h3>Investigation Activity</h3>
            <div class="activity-grid">
              <div class="activity-item">
                <div class="activity-value">${stats.total}</div>
                <div class="activity-label">Total Analyses</div>
              </div>
              <div class="activity-item">
                <div class="activity-value" style="color: var(--risk-high);">${stats.highRisk}</div>
                <div class="activity-label">High-Risk Findings</div>
              </div>
              <div class="activity-item">
                <div class="activity-value">${lastInv}</div>
                <div class="activity-label">Last Investigation</div>
              </div>
            </div>
          </div>

          <!-- Investigation Breakdown -->
          <div class="profile-section reveal">
            <h3>Investigation Breakdown</h3>
            <div class="activity-grid" style="grid-template-columns: 1fr 1fr;">
              <div class="activity-item">
                <div class="activity-value" style="color: var(--text-accent);">${stats.upi}</div>
                <div class="activity-label">UPI Analyses</div>
              </div>
              <div class="activity-item">
                <div class="activity-value" style="color: var(--accent-secondary);">${stats.scam}</div>
                <div class="activity-label">Scam Investigations</div>
              </div>
            </div>
          </div>

          <!-- Data Management -->
          <div class="profile-section reveal">
            <h3>Data Management</h3>
            <p style="font-size: var(--fs-sm); color: var(--text-secondary); margin-bottom: var(--space-xl);">
              You can clear your investigation history at any time. This permanently removes all stored results.
            </p>
            <button class="btn btn-danger" id="clear-all-btn">
              🗑 Clear All Investigation Data
            </button>
          </div>

          <!-- Actions -->
          <div class="profile-actions reveal">
            <button class="btn btn-danger btn-lg" id="logout-btn">
              LOG OUT
            </button>
          </div>
        </div>
      </div>
    </div>
  `;
}

function initProfilePage() {
  initScrollReveal();

  // Clear all data
  const clearBtn = document.getElementById('clear-all-btn');
  if (clearBtn) {
    clearBtn.addEventListener('click', () => {
      showConfirmModal(
        'Clear All Data',
        'This will permanently delete all your investigation history, stored results, and uploaded files on the server. This action cannot be undone.',
        async () => {
          try {
            if (typeof API !== 'undefined' && API.Privacy) {
              await API.Privacy.wipeAll();
            }
          } catch (e) {
            console.warn('Backend wipe warning:', e);
          }
          localStorage.removeItem('fraudlens_investigations');
          Toast.success('All investigation data and server uploads have been permanently cleared.');
          // Refresh page
          window.location.hash = '#/profile';
          setTimeout(() => mountPage(), 100);
        }
      );
    });
  }

  // Logout
  const logoutBtn = document.getElementById('logout-btn');
  if (logoutBtn) {
    logoutBtn.addEventListener('click', () => {
      handleLogout();
    });
  }
}

function cleanupProfilePage() {}
