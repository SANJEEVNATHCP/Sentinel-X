/* =============================================
   FRAUDLENS AI — REGISTER PAGE
   ============================================= */

function renderRegisterPage() {
  return `
    <div class="auth-page" id="register-page">
      <!-- Left: Visual -->
      <div class="auth-visual">
        <canvas class="auth-visual-canvas" id="auth-particles-reg" aria-hidden="true"></canvas>
        <div class="auth-visual-overlay">
          <div class="auth-brand">
            <span class="brand-icon" aria-hidden="true">🛡</span>
            <span>FRAUDLENS AI</span>
          </div>
          <p class="auth-tagline">
            AI-powered fraud intelligence that doesn't just detect threats —
            <strong>it explains why they matter.</strong>
          </p>
        </div>
      </div>

      <!-- Right: Form -->
      <div class="auth-form-container">
        <div class="auth-form-inner">
          <h1>Create Your FraudLens Account</h1>
          <p class="auth-subtitle">Build your private fraud investigation workspace.</p>

          <form id="register-form" novalidate>
            <div class="form-group">
              <label class="form-label" for="reg-name">Full Name</label>
              <input type="text" id="reg-name" class="form-input" 
                     placeholder="Enter your full name" required autocomplete="name"
                     aria-describedby="reg-name-error">
              <span class="form-error" id="reg-name-error" role="alert"></span>
            </div>
            <div class="form-group">
              <label class="form-label" for="reg-email">Email</label>
              <input type="email" id="reg-email" class="form-input" 
                     placeholder="your@email.com" required autocomplete="email"
                     aria-describedby="reg-email-error">
              <span class="form-error" id="reg-email-error" role="alert"></span>
            </div>
            <div class="form-group">
              <label class="form-label" for="reg-password">Password</label>
              <input type="password" id="reg-password" class="form-input" 
                     placeholder="Create a password (min. 6 characters)" required autocomplete="new-password"
                     aria-describedby="reg-password-error">
              <span class="form-error" id="reg-password-error" role="alert"></span>
            </div>
            <div class="form-group">
              <label class="form-label" for="reg-confirm">Confirm Password</label>
              <input type="password" id="reg-confirm" class="form-input" 
                     placeholder="Confirm your password" required autocomplete="new-password"
                     aria-describedby="reg-confirm-error">
              <span class="form-error" id="reg-confirm-error" role="alert"></span>
            </div>
            <button type="submit" class="btn btn-primary btn-lg w-full" id="reg-submit">
              <span class="btn-text">CREATE ACCOUNT →</span>
              <span class="btn-spinner" aria-hidden="true"></span>
            </button>
          </form>

          <div class="auth-divider">or</div>

          <p class="auth-link">
            Already have an account? <a href="#/login">Sign In</a>
          </p>
        </div>
      </div>
    </div>
  `;
}

function initRegisterPage() {
  const canvas = document.getElementById('auth-particles-reg');
  if (canvas) {
    const particles = new ParticleSystem(canvas);
    particles.start();
    window._authParticles = particles;
  }

  const form = document.getElementById('register-form');
  if (form) {
    form.addEventListener('submit', async (e) => {
      e.preventDefault();
      const name = document.getElementById('reg-name').value.trim();
      const email = document.getElementById('reg-email').value.trim();
      const password = document.getElementById('reg-password').value;
      const confirm = document.getElementById('reg-confirm').value;
      const submitBtn = document.getElementById('reg-submit');

      // Clear errors
      ['reg-name', 'reg-email', 'reg-password', 'reg-confirm'].forEach(id => {
        document.getElementById(id).classList.remove('error');
        document.getElementById(id + '-error').textContent = '';
      });

      // Validate
      let valid = true;

      if (!name || name.length < 2) {
        document.getElementById('reg-name-error').textContent = 'Full name is required (min. 2 characters).';
        document.getElementById('reg-name').classList.add('error');
        valid = false;
      }

      if (!email) {
        document.getElementById('reg-email-error').textContent = 'Email is required.';
        document.getElementById('reg-email').classList.add('error');
        valid = false;
      } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
        document.getElementById('reg-email-error').textContent = 'Enter a valid email address.';
        document.getElementById('reg-email').classList.add('error');
        valid = false;
      }

      if (!password || password.length < 8) {
        document.getElementById('reg-password-error').textContent = 'Password must be at least 8 characters.';
        document.getElementById('reg-password').classList.add('error');
        valid = false;
      }

      if (password !== confirm) {
        document.getElementById('reg-confirm-error').textContent = 'Passwords do not match.';
        document.getElementById('reg-confirm').classList.add('error');
        valid = false;
      }

      if (!valid) return;

      // Loading state
      submitBtn.classList.add('btn-loading');
      submitBtn.disabled = true;

      try {
        const result = await Auth.register(name, email, password, confirm);
        submitBtn.classList.remove('btn-loading');
        submitBtn.disabled = false;

        if (result.success) {
          Toast.success('Account created! Welcome to FraudLens AI.');
          if (InvestigationStore.syncFromBackend) {
            InvestigationStore.syncFromBackend();
          }
          setTimeout(() => {
            window.location.hash = '#/dashboard';
          }, 400);
        } else {
          Toast.error(result.error);
        }
      } catch (err) {
        submitBtn.classList.remove('btn-loading');
        submitBtn.disabled = false;
        Toast.error(err.message || 'Registration failed.');
      }
    });
  }
}

function cleanupRegisterPage() {
  if (window._authParticles) { window._authParticles.stop(); window._authParticles = null; }
}
