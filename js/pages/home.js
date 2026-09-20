/* =============================================
   FRAUDLENS AI — HOME / DASHBOARD PAGE
   ============================================= */

function renderHomePage() {
  const stats = InvestigationStore.getStats();
  const recent = InvestigationStore.getRecent(5);
  const allInv = InvestigationStore.getAll();
  const hasData = allInv.length > 0;

  return `
    <div class="page-wrapper">
      <!-- ═══ HERO SECTION ═══ -->
      <section class="hero" id="hero-section" aria-label="Hero section">
        <canvas class="hero-canvas" id="hero-particles" aria-hidden="true"></canvas>
        <div class="hero-content">
          <div class="hero-text">
            <div class="hero-badge">
              <span class="pulse-dot"></span>
              AI-Powered Fraud Intelligence
            </div>
            <h1 class="hero-title">
              See Beyond the<br><span class="highlight">Suspicion.</span>
            </h1>
            <p class="hero-subtitle">
              FraudLens AI combines behavioral intelligence, company verification,
              URL security analysis and AI-powered evidence to help you understand
              fraud before you act.
            </p>
            <p class="hero-tagline">
              Detect the signal. Verify the source. Understand the risk.
            </p>
            <div class="hero-actions">
              <a href="#analysis-options" class="btn btn-primary btn-lg" id="hero-cta-start">
                ⚡ START AN INVESTIGATION
              </a>
              <a href="#why-section" class="btn btn-secondary btn-lg" id="hero-cta-explore">
                🔍 EXPLORE FRAUD INTELLIGENCE
              </a>
            </div>
          </div>
          <div class="hero-visual" aria-hidden="true">
            <div class="shield-container">
              <canvas class="shield-canvas" id="shield-animation"></canvas>
            </div>
          </div>
        </div>
        <div class="scroll-indicator" aria-hidden="true">
          <span>Scroll to explore</span>
          <div class="scroll-line"></div>
        </div>
      </section>

      <!-- ═══ ANALYSIS OPTIONS ═══ -->
      <section class="analysis-section section" id="analysis-options" aria-label="Choose your investigation type">
        <div class="container">
          <div class="section-header reveal">
            <h2>Choose What You Want to <span class="text-gradient">Investigate</span></h2>
            <div class="divider"></div>
            <p>From suspicious transactions to suspicious recruiters, FraudLens brings multiple fraud signals into one investigation.</p>
          </div>

          <div class="analysis-grid">
            <!-- Card 1: UPI -->
            <div class="analysis-card reveal reveal-delay-1" onclick="window.location.hash='#/upi'" role="link" tabindex="0" aria-label="UPI Risk Intelligence">
              <div class="card-icon">💳</div>
              <h3>UPI Risk Intelligence</h3>
              <p>Upload transaction data and uncover behavioral anomalies, unusual transaction patterns, new beneficiaries, device changes, location anomalies and suspicious activity.</p>
              <div class="card-tags">
                <span class="card-tag">Behavior Analysis</span>
                <span class="card-tag">Anomaly Detection</span>
                <span class="card-tag">Risk Scoring</span>
              </div>
              <div class="card-action">
                <span>ANALYZE TRANSACTIONS</span>
                <span class="arrow">→</span>
              </div>
            </div>

            <!-- Card 2: Scam -->
            <div class="analysis-card reveal reveal-delay-2" onclick="window.location.hash='#/scam'" role="link" tabindex="0" aria-label="Scam Investigation">
              <div class="card-icon">🔍</div>
              <h3>Scam Investigation</h3>
              <p>Investigate suspicious URLs, job listings, recruiters, company claims, profile links and scam conversations using AI-powered evidence analysis.</p>
              <div class="card-tags">
                <span class="card-tag">URL Intelligence</span>
                <span class="card-tag">AI Vision</span>
                <span class="card-tag">Company Verification</span>
              </div>
              <div class="card-action">
                <span>INVESTIGATE A SCAM</span>
                <span class="arrow">→</span>
              </div>
            </div>

            <!-- Card 3: Results -->
            <div class="analysis-card reveal reveal-delay-3" onclick="window.location.hash='#/results'" role="link" tabindex="0" aria-label="Investigation History">
              <div class="card-icon">📈</div>
              <h3>Investigation History</h3>
              <p>Review your previous investigations, risk scores, evidence, graphs and recommendations from one secure workspace.</p>
              <div class="card-tags">
                <span class="card-tag">Risk History</span>
                <span class="card-tag">Evidence Reports</span>
                <span class="card-tag">PDF Export</span>
              </div>
              <div class="card-action">
                <span>VIEW RESULTS</span>
                <span class="arrow">→</span>
              </div>
            </div>

            <!-- Card 4: Profile -->
            <div class="analysis-card reveal reveal-delay-4" onclick="window.location.hash='#/profile'" role="link" tabindex="0" aria-label="Your Security Profile">
              <div class="card-icon">👤</div>
              <h3>Your Security Profile</h3>
              <p>Manage your FraudLens account, review your activity and securely control your session.</p>
              <div class="card-tags">
                <span class="card-tag">Account</span>
                <span class="card-tag">Activity</span>
                <span class="card-tag">Privacy</span>
              </div>
              <div class="card-action">
                <span>OPEN PROFILE</span>
                <span class="arrow">→</span>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- ═══ QUICK INVESTIGATION ═══ -->
      <section class="quick-section section" aria-label="Quick investigation">
        <div class="container">
          <div class="section-header reveal">
            <h2>Start With a <span class="text-gradient">Signal</span></h2>
            <p>Already have something suspicious? Start an investigation in seconds.</p>
          </div>
          <div class="quick-buttons reveal">
            <button class="quick-btn" onclick="window.location.hash='#/scam?tab=url'" aria-label="Check a URL">
              <span class="quick-icon">🔗</span>
              CHECK A URL
            </button>
            <button class="quick-btn" onclick="window.location.hash='#/scam?tab=company'" aria-label="Verify a company">
              <span class="quick-icon">🏢</span>
              VERIFY A COMPANY
            </button>
            <button class="quick-btn" onclick="window.location.hash='#/upi'" aria-label="Analyze transactions">
              <span class="quick-icon">📊</span>
              ANALYZE TRANSACTIONS
            </button>
          </div>
        </div>
      </section>

      <!-- ═══ LIVE SECURITY OVERVIEW ═══ -->
      <section class="overview-section section" aria-label="Your fraud intelligence overview">
        <div class="container">
          <div class="section-header reveal">
            <h2>Your Fraud Intelligence <span class="text-gradient">Overview</span></h2>
          </div>
          ${hasData ? `
            <div class="overview-grid reveal">
              <div class="stat-card">
                <div class="stat-icon" aria-hidden="true">🔎</div>
                <div class="stat-value" data-count="${stats.total}">0</div>
                <div class="stat-label">Total Investigations</div>
              </div>
              <div class="stat-card">
                <div class="stat-icon" aria-hidden="true">🔴</div>
                <div class="stat-value" data-count="${stats.highRisk}">0</div>
                <div class="stat-label">High-Risk Detections</div>
              </div>
              <div class="stat-card">
                <div class="stat-icon" aria-hidden="true">🛡</div>
                <div class="stat-value" data-count="${stats.scam}">0</div>
                <div class="stat-label">Scam Investigations</div>
              </div>
              <div class="stat-card">
                <div class="stat-icon" aria-hidden="true">💳</div>
                <div class="stat-value" data-count="${stats.upi}">0</div>
                <div class="stat-label">UPI Analyses</div>
              </div>
            </div>
          ` : `
            <div class="overview-empty reveal">
              <p>📊 Your investigation activity will appear here.</p>
            </div>
          `}
        </div>
      </section>

      <!-- ═══ RISK ACTIVITY GRAPH ═══ -->
      ${hasData ? `
        <section class="graph-section section" aria-label="Risk activity chart">
          <div class="container">
            <div class="section-header reveal">
              <h2>Your Risk <span class="text-gradient">Activity</span></h2>
            </div>
            <div class="graph-container reveal">
              ${renderRiskChart(allInv)}
            </div>
          </div>
        </section>
      ` : ''}

      <!-- ═══ WHY FRAUDLENS ═══ -->
      <section class="why-section section" id="why-section" aria-label="Why FraudLens">
        <div class="container">
          <div class="section-header reveal">
            <h2>More Than a <span class="text-gradient">Fraud Score.</span></h2>
            <div class="divider"></div>
            <p>FraudLens turns scattered warning signs into an understandable investigation.</p>
          </div>
          <div class="why-grid">
            <div class="why-block reveal reveal-delay-1">
              <div class="why-number">01</div>
              <h3>Detect</h3>
              <p>Identify suspicious patterns using machine learning, behavioral analysis and security intelligence.</p>
            </div>
            <div class="why-block reveal reveal-delay-2">
              <div class="why-number">02</div>
              <h3>Verify</h3>
              <p>Cross-check companies, domains, URLs and available evidence before drawing conclusions.</p>
            </div>
            <div class="why-block reveal reveal-delay-3">
              <div class="why-number">03</div>
              <h3>Explain</h3>
              <p>Understand exactly which observable signals contributed to the risk assessment.</p>
            </div>
          </div>
        </div>
      </section>

      <!-- ═══ EVIDENCE ENGINE SHOWCASE ═══ -->
      <section class="evidence-section section" aria-label="Evidence engine showcase">
        <div class="container">
          <div class="section-header reveal">
            <h2>Don't Just Take the Score.<br><span class="text-gradient">See the Evidence.</span></h2>
          </div>
          <div class="evidence-container reveal" id="evidence-showcase">
            <div class="evidence-score">
              <div class="score-ring" id="score-ring">
                <svg viewBox="0 0 180 180" xmlns="http://www.w3.org/2000/svg">
                  <circle class="ring-bg" cx="90" cy="90" r="80"/>
                  <circle class="ring-fill" cx="90" cy="90" r="80"/>
                </svg>
                <div class="score-text">
                  <div class="score-number">87</div>
                  <div class="score-total">/ 100</div>
                </div>
              </div>
              <div class="score-label">
                ${renderRiskBadge(87)}
              </div>
            </div>
            <div class="evidence-bars">
              <div class="evidence-bar">
                <span class="bar-indicator high"></span>
                <div class="bar-content">
                  <div class="bar-label">🔴 Payment request</div>
                  <div class="bar-track"><div class="bar-fill high" data-width="88" style="width:0"></div></div>
                </div>
                <span class="bar-value">+22</span>
              </div>
              <div class="evidence-bar">
                <span class="bar-indicator high"></span>
                <div class="bar-content">
                  <div class="bar-label">🔴 Domain mismatch</div>
                  <div class="bar-track"><div class="bar-fill high" data-width="72" style="width:0"></div></div>
                </div>
                <span class="bar-value">+18</span>
              </div>
              <div class="evidence-bar">
                <span class="bar-indicator suspicious"></span>
                <div class="bar-content">
                  <div class="bar-label">🟠 Recruiter inconsistency</div>
                  <div class="bar-track"><div class="bar-fill suspicious" data-width="60" style="width:0"></div></div>
                </div>
                <span class="bar-value">+15</span>
              </div>
              <div class="evidence-bar">
                <span class="bar-indicator suspicious"></span>
                <div class="bar-content">
                  <div class="bar-label">🟠 URL anomaly</div>
                  <div class="bar-track"><div class="bar-fill suspicious" data-width="56" style="width:0"></div></div>
                </div>
                <span class="bar-value">+14</span>
              </div>
              <div class="evidence-bar">
                <span class="bar-indicator moderate"></span>
                <div class="bar-content">
                  <div class="bar-label">🟡 Urgency language</div>
                  <div class="bar-track"><div class="bar-fill moderate" data-width="40" style="width:0"></div></div>
                </div>
                <span class="bar-value">+10</span>
              </div>
              <div class="evidence-bar">
                <span class="bar-indicator moderate"></span>
                <div class="bar-content">
                  <div class="bar-label">🟡 Company inconsistency</div>
                  <div class="bar-track"><div class="bar-fill moderate" data-width="32" style="width:0"></div></div>
                </div>
                <span class="bar-value">+08</span>
              </div>
            </div>
          </div>
          <div class="text-center reveal" style="margin-top: var(--space-xl);">
            <a href="#how-section" class="btn btn-secondary">EXPLORE HOW IT WORKS →</a>
          </div>
        </div>
      </section>

      <!-- ═══ HOW IT WORKS ═══ -->
      <section class="how-section section" id="how-section" aria-label="How it works">
        <div class="container">
          <div class="section-header reveal">
            <h2>How <span class="text-gradient">It Works</span></h2>
          </div>
          <div class="timeline reveal">
            <div class="timeline-step">
              <div class="timeline-marker">01</div>
              <div class="timeline-content">
                <h3>Submit</h3>
                <p>Provide a transaction, URL, listing or screenshot.</p>
              </div>
            </div>
            <div class="timeline-step">
              <div class="timeline-marker">02</div>
              <div class="timeline-content">
                <h3>Analyze</h3>
                <p>FraudLens combines AI, ML, security signals and reference data.</p>
              </div>
            </div>
            <div class="timeline-step">
              <div class="timeline-marker">03</div>
              <div class="timeline-content">
                <h3>Investigate</h3>
                <p>Evidence is collected and risk factors are identified.</p>
              </div>
            </div>
            <div class="timeline-step">
              <div class="timeline-marker">04</div>
              <div class="timeline-content">
                <h3>Understand</h3>
                <p>Receive a clear risk score, explanation and recommended action.</p>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- ═══ PRIVACY SECTION ═══ -->
      <section class="privacy-section section" aria-label="Data privacy">
        <div class="container">
          <div class="privacy-container reveal">
            <h2>Your Data. Your <span class="text-gradient">Control.</span></h2>
            <div class="divider"></div>
            <p style="max-width: 640px; margin: 0 auto; font-size: var(--fs-base);">
              FraudLens is designed around session-based analysis. When you end an investigation,
              sensitive raw session data can be permanently deleted while your derived investigation
              result remains available.
            </p>
            <div class="privacy-icons">
              <div class="privacy-icon-item">
                <div class="p-icon">🔒</div>
                <div class="p-label">Secure Processing</div>
                <div class="p-desc">Analysis within your session</div>
              </div>
              <div class="privacy-icon-item">
                <div class="p-icon">🗑</div>
                <div class="p-label">Session Data Deletion</div>
                <div class="p-desc">Raw data can be removed</div>
              </div>
              <div class="privacy-icon-item">
                <div class="p-icon">📋</div>
                <div class="p-label">Derived Results Only</div>
                <div class="p-desc">Only summaries are retained</div>
              </div>
            </div>
            <div style="margin-top: var(--space-2xl);">
              <button class="btn btn-secondary" onclick="showPrivacyModal()">LEARN ABOUT DATA PRIVACY →</button>
            </div>
          </div>
        </div>
      </section>

      <!-- ═══ CHROME EXTENSION ═══ -->
      <section class="extension-section section" aria-label="Chrome extension">
        <div class="container">
          <div class="extension-container reveal">
            <div class="extension-text">
              <h2>FraudLens Goes Where You <span class="text-gradient">Browse.</span></h2>
              <p>Investigating a suspicious job listing or website? Scan the page directly from your browser with the FraudLens Chrome extension.</p>
              <button class="btn btn-primary btn-lg">EXPLORE THE EXTENSION →</button>
            </div>
            <div class="browser-mockup">
              <div class="browser-toolbar">
                <div class="browser-dots" aria-hidden="true">
                  <span></span><span></span><span></span>
                </div>
                <div class="browser-url">🔒 suspicious-job-offer.com</div>
              </div>
              <div class="browser-content">
                <div class="site-title">Software Engineer — Remote</div>
                <div class="site-detail">Salary: ₹80,000/month</div>
                <div class="site-detail site-warning">⚠ Registration fee: ₹1,999</div>
                <div class="site-detail">Start immediately — No experience required</div>
                <div class="fraudlens-badge">
                  <div class="fl-brand">🛡 FRAUDLENS AI</div>
                  <div class="fl-score">87/100</div>
                  <div class="fl-level">HIGH RISK</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- ═══ RECENT INVESTIGATIONS ═══ -->
      <section class="recent-section section" aria-label="Recent investigations">
        <div class="container">
          <div class="section-header reveal">
            <h2>Recent <span class="text-gradient">Investigations</span></h2>
          </div>
          ${recent.length > 0 ? `
            <div class="recent-grid reveal">
              ${recent.map(inv => {
                const risk = getRiskLevel(inv.riskScore);
                return `
                  <div class="recent-card">
                    <div class="recent-card-header">
                      <span class="recent-card-type">
                        ${inv.type === 'upi' ? '💳' : '🛡'} ${inv.type.toUpperCase()} INVESTIGATION
                      </span>
                      <span class="recent-card-date">${formatDate(inv.createdAt)}</span>
                    </div>
                    <div class="recent-card-score">
                      <span class="score" style="color: ${risk.color}">${inv.riskScore}</span>
                      <span class="total">/100</span>
                    </div>
                    ${renderRiskBadge(inv.riskScore)}
                    <p class="recent-card-summary">${inv.summary || 'Investigation completed.'}</p>
                    <div class="recent-card-actions">
                      <a href="#/results?id=${inv.id}" class="btn btn-secondary btn-sm">VIEW REPORT</a>
                    </div>
                  </div>
                `;
              }).join('')}
            </div>
          ` : `
            <div class="reveal">
              ${renderEmptyState(
                '🔎',
                'Your investigation workspace is ready.',
                'Run your first analysis to start building your FraudLens intelligence history.',
                'START FIRST INVESTIGATION',
                '#/upi'
              )}
            </div>
          `}
        </div>
      </section>

      <!-- ═══ FINAL CTA ═══ -->
      <section class="cta-section section" aria-label="Call to action">
        <div class="container">
          <div class="cta-container reveal">
            <h2>Something Doesn't Look Right?</h2>
            <p class="cta-subtitle">Don't guess. <strong style="color: var(--text-white);">Investigate.</strong></p>
            <a href="#analysis-options" class="btn btn-primary btn-xl" style="position: relative;">
              ⚡ START AN INVESTIGATION
            </a>
          </div>
        </div>
      </section>

      <!-- ═══ FOOTER ═══ -->
      <footer class="footer" role="contentinfo">
        <div class="container">
          <p>© ${new Date().getFullYear()} FraudLens AI — See the Risk. Understand the Evidence. Act Safely.</p>
        </div>
      </footer>
    </div>
  `;
}

function initHomePage() {
  // Start particle animation
  const heroCanvas = document.getElementById('hero-particles');
  if (heroCanvas) {
    const particles = new ParticleSystem(heroCanvas);
    particles.start();
    window._heroParticles = particles;
  }

  // Start shield animation
  const shieldCanvas = document.getElementById('shield-animation');
  if (shieldCanvas) {
    const shield = new ShieldAnimation(shieldCanvas);
    shield.start();
    window._shieldAnimation = shield;
  }

  // Init scroll reveal
  initScrollReveal();

  // Evidence showcase observer
  const evidenceEl = document.getElementById('evidence-showcase');
  if (evidenceEl) {
    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          animateEvidenceBars();
          const ring = document.getElementById('score-ring');
          if (ring) animateScoreRing(ring, 87);
          observer.unobserve(entry.target);
        }
      });
    }, { threshold: 0.3 });
    observer.observe(evidenceEl);
  }

  // Smooth scroll for in-page links
  document.querySelectorAll('a[href^="#"][href*="-"]').forEach(link => {
    link.addEventListener('click', (e) => {
      const targetId = link.getAttribute('href');
      if (targetId.startsWith('#') && !targetId.startsWith('#/')) {
        e.preventDefault();
        const el = document.querySelector(targetId);
        if (el) {
          el.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
      }
    });
  });

  // Make analysis cards keyboard accessible
  document.querySelectorAll('.analysis-card[role="link"]').forEach(card => {
    card.addEventListener('keydown', (e) => {
      if (e.key === 'Enter' || e.key === ' ') {
        e.preventDefault();
        card.click();
      }
    });
  });

  // Pull live verified metrics from backend
  if (typeof API !== 'undefined' && API.Dashboard && Auth.isAuthenticated()) {
    API.Dashboard.get().then(data => {
      if (data) {
        const statValues = document.querySelectorAll('.overview-grid .stat-card .stat-value');
        if (statValues.length >= 4) {
          statValues[0].textContent = data.total_investigations ?? 0;
          statValues[1].textContent = data.high_risk_detections ?? 0;
          statValues[2].textContent = data.scam_investigations ?? 0;
          statValues[3].textContent = data.upi_analyses ?? 0;
        }
      }
    }).catch(e => console.warn('Live dashboard fetch:', e));
  }
}

function cleanupHomePage() {
  if (window._heroParticles) { window._heroParticles.stop(); window._heroParticles = null; }
  if (window._shieldAnimation) { window._shieldAnimation.stop(); window._shieldAnimation = null; }
}
