/* =============================================
   FRAUDLENS AI — LOGIN PAGE
   ============================================= */

function renderLoginPage() {
  return `
    <div class="auth-page" id="login-page">
      <!-- Left: Visual -->
      <div class="auth-visual">
        <canvas class="auth-visual-canvas" id="auth-particles" aria-hidden="true"></canvas>
        <div class="auth-visual-overlay">
          <div class="auth-brand">
            <span class="brand-icon" aria-hidden="true">🛡</span>
            <span>FRAUDLENS AI</span>
          </div>
          <p class="auth-tagline">
            <strong>See the Risk.</strong><br>
            <strong>Understand the Evidence.</strong><br>
            <strong>Act Safely.</strong>
          </p>
        </div>
      </div>

      <!-- Right: Form -->
      <div class="auth-form-container">
        <div class="auth-form-inner">
          <h1>Welcome Back</h1>
          <p class="auth-subtitle">Continue your investigation.</p>

          ${Auth.isAuthenticated() ? `
            <div style="background: rgba(59, 130, 246, 0.12); border: 1px solid rgba(59, 130, 246, 0.3); border-radius: 8px; padding: 12px 14px; margin-bottom: 20px;">
              <div style="font-size: 13px; color: var(--text-primary); margin-bottom: 8px;">
                ℹ️ Currently signed in as: <strong>${(Auth.getCurrentUser() || {}).email || 'Active User'}</strong>
              </div>
              <div style="display: flex; gap: 8px;">
                <a href="#/dashboard" class="btn btn-primary btn-sm">Go to Dashboard</a>
                <button type="button" class="btn btn-secondary btn-sm" onclick="handleLogout()" style="color: #f87171;">Sign Out</button>
              </div>
            </div>
          ` : ''}

          <form id="login-form" novalidate>
            <div class="form-group">
              <label class="form-label" for="login-email">Email</label>
              <input type="email" id="login-email" class="form-input" 
                     placeholder="your@email.com" required autocomplete="email"
                     aria-describedby="login-email-error">
              <span class="form-error" id="login-email-error" role="alert"></span>
            </div>
            <div class="form-group">
              <label class="form-label" for="login-password">Password</label>
              <input type="password" id="login-password" class="form-input" 
                     placeholder="Enter your password" required autocomplete="current-password"
                     aria-describedby="login-password-error">
              <span class="form-error" id="login-password-error" role="alert"></span>
            </div>
            <button type="submit" class="btn btn-primary btn-lg w-full" id="login-submit">
              <span class="btn-text">SIGN IN →</span>
              <span class="btn-spinner" aria-hidden="true"></span>
            </button>
            <button type="button" class="btn btn-ghost btn-sm w-full" id="fill-demo-btn" style="margin-top: 10px; font-size: 12px; color: var(--accent-primary);">
              ⚡ Quick Fill Demo Account (demo@fraudlens.ai)
            </button>
          </form>

          <div class="auth-divider">or</div>

          <p class="auth-link">
            Don't have an account? <a href="#/register">Create Account</a>
          </p>
        </div>
      </div>
    </div>
  `;
}

function initLoginPage() {
  // Auth particles
  const canvas = document.getElementById('auth-particles');
  if (canvas) {
    const particles = new ParticleSystem(canvas);
    particles.start();
    window._authParticles = particles;
  }

  // Quick fill demo account
  const demoBtn = document.getElementById('fill-demo-btn');
  if (demoBtn) {
    demoBtn.addEventListener('click', () => {
      document.getElementById('login-email').value = 'demo@fraudlens.ai';
      document.getElementById('login-password').value = 'FraudLens@2026';
      Toast.info('Demo credentials prefilled.');
    });
  }

  // Form handling
  const form = document.getElementById('login-form');
  if (form) {
    form.addEventListener('submit', async (e) => {
      e.preventDefault();
      const email = document.getElementById('login-email').value.trim();
      const password = document.getElementById('login-password').value;
      const submitBtn = document.getElementById('login-submit');

      // Clear errors
      document.getElementById('login-email-error').textContent = '';
      document.getElementById('login-password-error').textContent = '';
      document.getElementById('login-email').classList.remove('error');
      document.getElementById('login-password').classList.remove('error');

      // Validate
      let valid = true;
      if (!email) {
        document.getElementById('login-email-error').textContent = 'Email is required.';
        document.getElementById('login-email').classList.add('error');
        valid = false;
      } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
        document.getElementById('login-email-error').textContent = 'Enter a valid email address.';
        document.getElementById('login-email').classList.add('error');
        valid = false;
      }
      if (!password) {
        document.getElementById('login-password-error').textContent = 'Password is required.';
        document.getElementById('login-password').classList.add('error');
        valid = false;
      }

      if (!valid) return;

      // Loading state
      submitBtn.classList.add('btn-loading');
      submitBtn.disabled = true;

      try {
        const result = await Auth.login(email, password);
        submitBtn.classList.remove('btn-loading');
        submitBtn.disabled = false;

        if (result.success) {
          Toast.success('Welcome back! Redirecting to dashboard...');
          // Trigger sync in background
          if (InvestigationStore.syncFromBackend) {
            InvestigationStore.syncFromBackend();
          }
          setTimeout(() => {
            window.location.hash = '#/dashboard';
          }, 400);
        } else {
          Toast.error(result.error);
          document.getElementById('login-email').classList.add('error');
          document.getElementById('login-password').classList.add('error');
        }
      } catch (err) {
        submitBtn.classList.remove('btn-loading');
        submitBtn.disabled = false;
        Toast.error(err.message || 'Login failed. Please verify backend is running.');
      }
    });
  }
}

function cleanupLoginPage() {
  if (window._authParticles) { window._authParticles.stop(); window._authParticles = null; }
}
