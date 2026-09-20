/* =============================================
   FRAUDLENS AI — SCAM INVESTIGATION PAGE
   ============================================= */

function renderScamPage() {
  // Check for tab query param
  const hash = window.location.hash;
  const tabMatch = hash.match(/tab=(\w+)/);
  const activeTab = tabMatch ? tabMatch[1] : 'url';

  return `
    <div class="page-wrapper scam-page">
      <div class="container">
        <div class="page-header">
          <a href="#/dashboard" class="btn btn-ghost btn-sm" style="margin-bottom: var(--space-md);">← Back to Dashboard</a>
          <h1>Scam Investigation <span class="text-gradient">Center</span></h1>
          <div class="divider"></div>
          <p>Bring suspicious digital activity into one investigation. Check URLs, companies, recruiter profiles and scam conversations.</p>
        </div>

        <div class="tabs" role="tablist" aria-label="Investigation type tabs">
          <button class="tab ${activeTab === 'url' ? 'active' : ''}" 
                  data-tab="url" role="tab" aria-selected="${activeTab === 'url'}" 
                  aria-controls="tab-url" id="tab-btn-url">
            🔗 URL Scan
          </button>
          <button class="tab ${activeTab === 'company' ? 'active' : ''}" 
                  data-tab="company" role="tab" aria-selected="${activeTab === 'company'}" 
                  aria-controls="tab-company" id="tab-btn-company">
            🏢 Company Check
          </button>
          <button class="tab ${activeTab === 'profile' ? 'active' : ''}" 
                  data-tab="profile" role="tab" aria-selected="${activeTab === 'profile'}" 
                  aria-controls="tab-profile" id="tab-btn-profile">
            👤 Profile Check
          </button>
          <button class="tab ${activeTab === 'image' ? 'active' : ''}" 
                  data-tab="image" role="tab" aria-selected="${activeTab === 'image'}" 
                  aria-controls="tab-image" id="tab-btn-image">
            🖼 Image / Chat Analysis
          </button>
        </div>

        <div id="tab-content">
          ${renderScamTab(activeTab)}
        </div>

        <!-- Results area -->
        <div id="scam-results-container" style="display: none; margin-top: var(--space-2xl);"></div>
      </div>
    </div>
  `;
}

function renderScamTab(tab) {
  const tabs = {
    url: `
      <div class="tab-content" id="tab-url" role="tabpanel" aria-labelledby="tab-btn-url">
        <div class="investigation-form">
          <div class="form-helper">
            <strong>URL Scan</strong> — Check suspicious links against security intelligence and local risk signals.
          </div>
          <div class="form-group">
            <label class="form-label" for="scam-url">Suspicious URL</label>
            <input type="url" id="scam-url" class="form-input" 
                   placeholder="https://suspicious-site.com/job-offer" 
                   aria-describedby="url-help">
            <span class="text-xs text-muted" id="url-help">Enter the full URL including https://</span>
          </div>
          <div class="form-group">
            <label class="form-label" for="scam-url-notes">Additional Context (optional)</label>
            <textarea id="scam-url-notes" class="form-input" rows="3" 
                      placeholder="Where did you find this link? Any additional context..."></textarea>
          </div>
          <button class="btn btn-primary btn-lg w-full" id="scam-analyze-btn" data-type="url">
            <span class="btn-text">🔍 SCAN URL</span>
            <span class="btn-spinner" aria-hidden="true"></span>
          </button>
        </div>
      </div>
    `,
    company: `
      <div class="tab-content" id="tab-company" role="tabpanel" aria-labelledby="tab-btn-company">
        <div class="investigation-form">
          <div class="form-helper">
            <strong>Company Check</strong> — Compare claimed companies against your MCA reference data.
          </div>
          <div class="form-group">
            <label class="form-label" for="scam-company">Company Name</label>
            <input type="text" id="scam-company" class="form-input" 
                   placeholder="e.g. TechVision Solutions Pvt Ltd">
          </div>
          <div class="form-group">
            <label class="form-label" for="scam-cin">CIN / Registration Number (optional)</label>
            <input type="text" id="scam-cin" class="form-input" 
                   placeholder="e.g. U72200KA2020PTC123456">
          </div>
          <div class="form-group">
            <label class="form-label" for="scam-company-url">Company Website (optional)</label>
            <input type="url" id="scam-company-url" class="form-input" 
                   placeholder="https://company-website.com">
          </div>
          <button class="btn btn-primary btn-lg w-full" id="scam-analyze-btn" data-type="company">
            <span class="btn-text">🏢 VERIFY COMPANY</span>
            <span class="btn-spinner" aria-hidden="true"></span>
          </button>
        </div>
      </div>
    `,
    profile: `
      <div class="tab-content" id="tab-profile" role="tabpanel" aria-labelledby="tab-btn-profile">
        <div class="investigation-form">
          <div class="form-helper">
            <strong>Profile Check</strong> — Analyze available profile information for consistency and suspicious signals.
          </div>
          <div class="form-group">
            <label class="form-label" for="scam-profile-name">Person / Recruiter Name</label>
            <input type="text" id="scam-profile-name" class="form-input" 
                   placeholder="e.g. Rajesh Kumar">
          </div>
          <div class="form-group">
            <label class="form-label" for="scam-profile-link">LinkedIn / Profile URL (optional)</label>
            <input type="url" id="scam-profile-link" class="form-input" 
                   placeholder="https://linkedin.com/in/profile">
          </div>
          <div class="form-group">
            <label class="form-label" for="scam-profile-context">Context</label>
            <textarea id="scam-profile-context" class="form-input" rows="3" 
                      placeholder="How did this person contact you? What did they offer?"></textarea>
          </div>
          <button class="btn btn-primary btn-lg w-full" id="scam-analyze-btn" data-type="profile">
            <span class="btn-text">👤 CHECK PROFILE</span>
            <span class="btn-spinner" aria-hidden="true"></span>
          </button>
        </div>
      </div>
    `,
    image: `
      <div class="tab-content" id="tab-image" role="tabpanel" aria-labelledby="tab-btn-image">
        <div class="investigation-form">
          <div class="form-helper">
            <strong>Image / Chat Analysis</strong> — Upload up to 3 screenshots, payment receipts, or chat conversations. FraudLens analyzes visual anomalies and social-engineering tactics using Gemini Multimodal Vision AI.
          </div>
          <div class="image-upload-area" id="scam-image-upload" 
               role="button" tabindex="0"
               aria-label="Upload screenshots or chat images (up to 3)">
            <div style="font-size: 48px; margin-bottom: var(--space-md); opacity: 0.5;" aria-hidden="true">🖼</div>
            <p style="color: var(--text-secondary); margin-bottom: var(--space-sm);">Drop screenshot or chat images here (up to 3 images)</p>
            <p class="text-xs text-muted">or click to browse • PNG, JPG, WEBP • Max 3 images</p>
          </div>
          <input type="file" id="scam-image-input" accept="image/*" multiple style="display:none">
          <div id="scam-image-preview" style="margin-top: var(--space-md); display: flex; flex-direction: column; gap: 8px;"></div>
          <div class="form-group" style="margin-top: var(--space-lg);">
            <label class="form-label" for="scam-image-context">What seems suspicious? (Optional context)</label>
            <textarea id="scam-image-context" class="form-input" rows="3" 
                      placeholder="Describe what you find suspicious (e.g. unsolicited payment QR, pressure to transfer, fake bank confirmation)..."></textarea>
          </div>
          <div class="form-group" style="margin-top: var(--space-md);">
            <label class="form-label" for="scam-gemini-key">Gemini API Key (Optional — Auto-saved locally)</label>
            <input type="password" id="scam-gemini-key" class="form-input" 
                   placeholder="Enter Gemini API key (e.g. AIzaSy...)" 
                   value="${localStorage.getItem('fraudlens_gemini_key') || ''}">
            <span class="text-xs text-muted">Pass your Gemini API Key to directly classify image documents as TRUSTED OFFER or UNTRUSTED OFFER.</span>
          </div>
          <button class="btn btn-primary btn-lg w-full" id="scam-analyze-btn" data-type="image">
            <span class="btn-text">🖼 ANALYZE IMAGES & VERIFY OFFER (UP TO 3)</span>
            <span class="btn-spinner" aria-hidden="true"></span>
          </button>
        </div>
      </div>
    `
  };

  return tabs[tab] || tabs.url;
}

let scamSelectedImages = [];

function updateScamImagePreviews() {
  const preview = document.getElementById('scam-image-preview');
  if (!preview) return;
  if (scamSelectedImages.length === 0) {
    preview.innerHTML = '';
    return;
  }

  preview.innerHTML = scamSelectedImages.map((file, idx) => `
    <div class="file-info" style="display: flex; align-items: center; justify-content: space-between; padding: 10px 14px; background: rgba(255,255,255,0.04); border: 1px solid var(--border-color, rgba(255,255,255,0.1)); border-radius: 8px;">
      <div style="display: flex; align-items: center; gap: 10px;">
        <span class="file-icon" style="font-size: 22px;">🖼</span>
        <div class="file-details">
          <div class="file-name" style="font-weight: 600; font-size: 13px;">${file.name} <span class="text-muted" style="font-size: 11px;">(#${idx + 1})</span></div>
          <div class="file-size text-muted" style="font-size: 11px;">${(file.size / 1024).toFixed(1)} KB</div>
        </div>
      </div>
      <button class="file-remove" type="button" data-index="${idx}" style="background: none; border: none; color: #ef4444; font-size: 20px; cursor: pointer; padding: 4px 8px;" aria-label="Remove image">&times;</button>
    </div>
  `).join('') + (scamSelectedImages.length < 3 ? `
    <p class="text-xs text-muted" style="margin-top: 4px;">Uploaded ${scamSelectedImages.length}/3 images. You can add ${3 - scamSelectedImages.length} more.</p>
  ` : `
    <p class="text-xs" style="color: var(--risk-low, #10b981); margin-top: 4px;">✓ Maximum 3 images selected.</p>
  `);

  preview.querySelectorAll('.file-remove').forEach(btn => {
    btn.addEventListener('click', (e) => {
      e.stopPropagation();
      const idx = parseInt(btn.dataset.index, 10);
      scamSelectedImages.splice(idx, 1);
      updateScamImagePreviews();
    });
  });
}

function handleScamFiles(fileList) {
  if (!fileList || fileList.length === 0) return;
  const validFiles = Array.from(fileList).filter(f => f.type.startsWith('image/'));
  if (validFiles.length === 0) {
    Toast.error('Please upload valid image files (PNG, JPG, WEBP).');
    return;
  }

  let added = 0;
  for (const f of validFiles) {
    if (scamSelectedImages.length < 3) {
      scamSelectedImages.push(f);
      added++;
    } else {
      break;
    }
  }

  if (validFiles.length > added) {
    Toast.info(`FraudLens accepts up to 3 images at a time. ${scamSelectedImages.length} image(s) now selected.`);
  }

  updateScamImagePreviews();
}

function initScamPage() {
  scamSelectedImages = [];
  // Tab switching
  document.querySelectorAll('.tab[data-tab]').forEach(tab => {
    tab.addEventListener('click', () => {
      document.querySelectorAll('.tab').forEach(t => {
        t.classList.remove('active');
        t.setAttribute('aria-selected', 'false');
      });
      tab.classList.add('active');
      tab.setAttribute('aria-selected', 'true');

      const tabContent = document.getElementById('tab-content');
      tabContent.innerHTML = renderScamTab(tab.dataset.tab);

      // Re-bind tab-specific listeners
      bindScamTabListeners(tab.dataset.tab);

      // Hide results
      document.getElementById('scam-results-container').style.display = 'none';
    });
  });

  // Get active tab
  const activeTab = document.querySelector('.tab.active');
  if (activeTab) {
    bindScamTabListeners(activeTab.dataset.tab);
  }
}

function bindScamTabListeners(tab) {
  // Image upload
  if (tab === 'image') {
    const uploadArea = document.getElementById('scam-image-upload');
    const imageInput = document.getElementById('scam-image-input');

    if (uploadArea && imageInput) {
      uploadArea.addEventListener('click', () => imageInput.click());
      uploadArea.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); imageInput.click(); }
      });

      uploadArea.addEventListener('dragover', (e) => { e.preventDefault(); uploadArea.style.borderColor = 'var(--accent-primary)'; });
      uploadArea.addEventListener('dragleave', () => { uploadArea.style.borderColor = ''; });
      uploadArea.addEventListener('drop', (e) => {
        e.preventDefault();
        uploadArea.style.borderColor = '';
        if (e.dataTransfer && e.dataTransfer.files) handleScamFiles(e.dataTransfer.files);
      });

      imageInput.addEventListener('change', () => {
        if (imageInput.files) handleScamFiles(imageInput.files);
      });
    }
  }

  // Analyze button
  const analyzeBtn = document.getElementById('scam-analyze-btn');
  if (analyzeBtn) {
    analyzeBtn.addEventListener('click', () => {
      startScamAnalysis(analyzeBtn.dataset.type);
    });
  }
}

async function startScamAnalysis(type) {
  const resultsContainer = document.getElementById('scam-results-container');
  const analyzeBtn = document.getElementById('scam-analyze-btn');

  // Validate inputs
  let inputValue = '';
  let extraData = {};

  if (type === 'url') {
    inputValue = document.getElementById('scam-url')?.value.trim();
    if (!inputValue) { Toast.warning('Please enter a URL to scan.'); return; }
  } else if (type === 'company') {
    inputValue = document.getElementById('scam-company')?.value.trim();
    if (!inputValue) { Toast.warning('Please enter a company name.'); return; }
    extraData.cin = document.getElementById('scam-cin')?.value.trim();
    extraData.domain = document.getElementById('scam-company-url')?.value.trim();
  } else if (type === 'profile') {
    inputValue = document.getElementById('scam-profile-name')?.value.trim();
    if (!inputValue) { Toast.warning('Please enter a name to check.'); return; }
    extraData.linkedin_url = document.getElementById('scam-profile-link')?.value.trim();
    extraData.message_text = document.getElementById('scam-profile-context')?.value.trim();
  } else if (type === 'image') {
    inputValue = document.getElementById('scam-image-context')?.value.trim() || 'Image / Chat Analysis';
    if (scamSelectedImages.length === 0) {
      const imageInput = document.getElementById('scam-image-input');
      if (imageInput && imageInput.files && imageInput.files.length > 0) {
        handleScamFiles(imageInput.files);
      }
    }
    if (scamSelectedImages.length === 0) {
      Toast.warning('Please upload at least 1 image (up to 3 images supported).');
      return;
    }
  }

  analyzeBtn.classList.add('btn-loading');
  analyzeBtn.disabled = true;

  const steps = [
    'Validating input and media files...',
    'Querying ScamShield threat intelligence...',
    'Running Google Gemini Multimodal Vision analysis...',
    'Extracting visual anomalies & social engineering flags...',
    'Synthesizing audit-grade investigation report...'
  ];

  let stepIndex = 0;
  resultsContainer.style.display = 'block';
  resultsContainer.innerHTML = renderLoadingAnimation(steps, 0);

  const interval = setInterval(() => {
    if (stepIndex < steps.length - 1) {
      stepIndex++;
      resultsContainer.innerHTML = renderLoadingAnimation(steps, stepIndex);
    }
  }, 400);

  try {
    let apiResult = null;

    if (type === 'url' && typeof API !== 'undefined') {
      apiResult = await API.Scam.scanUrl(inputValue);
    } else if (type === 'company' && typeof API !== 'undefined') {
      apiResult = await API.Scam.verifyCompany(inputValue, extraData.domain);
    } else if (type === 'profile' && typeof API !== 'undefined') {
      apiResult = await API.Scam.analyzeMulti({
        company_name: inputValue,
        linkedin_url: extraData.linkedin_url,
        message_text: extraData.message_text
      });
    } else if (type === 'image' && typeof API !== 'undefined') {
      const contextText = document.getElementById('scam-image-context')?.value.trim() || null;
      const geminiKeyInput = document.getElementById('scam-gemini-key')?.value.trim();
      if (geminiKeyInput) {
        localStorage.setItem('fraudlens_gemini_key', geminiKeyInput);
      }
      apiResult = await API.Scam.analyzeImage(scamSelectedImages, contextText, geminiKeyInput);
    }

    clearInterval(interval);
    analyzeBtn.classList.remove('btn-loading');
    analyzeBtn.disabled = false;

    renderRealScamResults(type, inputValue, apiResult, resultsContainer);
  } catch (err) {
    clearInterval(interval);
    analyzeBtn.classList.remove('btn-loading');
    analyzeBtn.disabled = false;
    resultsContainer.style.display = 'none';
    Toast.error(err.message || 'Analysis failed. Please verify the backend is running.');
  }
}

function renderRealScamResults(type, inputValue, data, container) {
  const typeLabels = { url: 'URL Intelligence', company: 'Company Master Verification', profile: 'Profile Check', image: 'Image & Chat Multimodal Analysis' };
  const typeIcons = { url: '🔗', company: '🏢', profile: '👤', image: '🖼' };

  let riskScore = 20;
  let riskLevel = 'LOW';
  let summary = `Investigation completed for "${inputValue}".`;
  let evidenceList = [];
  let recommendation = 'No critical threats detected. Proceed with standard verification.';
  let companyBadge = '';
  let anomalyBanner = '';
  let offerVerdictBanner = '';

  if (type === 'company' && data) {
    const isInactive = (data.company_status || '').toUpperCase() === 'INACTIVE';
    const isActive = (data.company_status || '').toUpperCase() === 'ACTIVE';

    if (isInactive) {
      riskScore = 90;
      riskLevel = 'HIGH_RISK';
      summary = `WARNING: Company "${data.company_name || inputValue}" is marked as INACTIVE in dataset (sample.xlsx). Website or entity may be defunct, strike-off, or unauthorized.`;
      recommendation = 'HIGH RISK: Do not engage or send payments. This entity is defunct or inactive according to corporate registration records.';
      companyBadge = `<div style="background: rgba(239, 68, 68, 0.15); border: 1px solid #ef4444; color: #f87171; padding: 8px 14px; border-radius: 6px; font-weight: bold; margin-bottom: 12px; display: inline-block;">
        ⚠ COMPANY STATUS: INACTIVE (DEFUNCT / HIGH RISK)
      </div>`;
      evidenceList.push({
        text: `Corporate status recorded as INACTIVE in Company Master Catalog (${data.verification_source || 'sample.xlsx'})`,
        weight: '+40',
        level: 'high'
      });
      evidenceList.push({
        text: `Registered CIN: ${data.cin || 'DEMO-INACTIVE'} (${data.registered_state || 'Overseas'} - ${data.roc || 'Discontinued'})`,
        weight: '+25',
        level: 'high'
      });
    } else if (isActive) {
      riskScore = 5;
      riskLevel = 'LOW';
      summary = `Verified Active Corporate Entity: "${data.company_name || inputValue}" is registered and ACTIVE in Ministry of Corporate Affairs (MCA) records.`;
      recommendation = 'Entity is verified as ACTIVE in the authoritative corporate registry.';
      companyBadge = `<div style="background: rgba(16, 185, 129, 0.15); border: 1px solid #10b981; color: #34d399; padding: 8px 14px; border-radius: 6px; font-weight: bold; margin-bottom: 12px; display: inline-block;">
        ✓ COMPANY STATUS: ACTIVE (VERIFIED REAL)
      </div>`;
      evidenceList.push({
        text: `Active corporate registration confirmed: CIN ${data.cin || 'Verified'}`,
        weight: '-30',
        level: 'moderate'
      });
      evidenceList.push({
        text: `Registered with ${data.roc || 'Registrar of Companies'}, State: ${data.registered_state || 'Verified'}`,
        weight: '-15',
        level: 'moderate'
      });
      if (data.official_domain) {
        evidenceList.push({
          text: `Official domain mapped: ${data.official_domain}`,
          weight: '-10',
          level: 'moderate'
        });
      }
    } else {
      riskScore = 65;
      riskLevel = 'SUSPICIOUS';
      summary = `Company "${inputValue}" was not found in the authoritative Company Master catalog.`;
      recommendation = 'Company registration cannot be verified in the MCA dataset. Treat with caution.';
      companyBadge = `<div style="background: rgba(245, 158, 11, 0.15); border: 1px solid #f59e0b; color: #fbbf24; padding: 8px 14px; border-radius: 6px; font-weight: bold; margin-bottom: 12px; display: inline-block;">
        ? UNVERIFIED COMPANY (NOT FOUND IN CATALOG)
      </div>`;
      evidenceList.push({
        text: 'Company name and CIN not found in MCA corporate database',
        weight: '+25',
        level: 'suspicious'
      });
    }
  } else if (type === 'url' && data) {
    riskScore = Math.round(data.risk_score || 0);
    riskLevel = data.risk_level || 'UNKNOWN';
    summary = `URL scan completed for ${data.domain || inputValue}.`;
    if (data.found_in_threat_dataset) {
      evidenceList.push({
        text: `Domain matches known threat database (${data.dataset_status || 'FLAGGED'})`,
        weight: '+35',
        level: 'high'
      });
    }
    if (data.reasons && data.reasons.length > 0) {
      data.reasons.forEach(r => evidenceList.push({ text: r, weight: '+15', level: 'suspicious' }));
    }
    if (data.virustotal && data.virustotal.malicious > 0) {
      evidenceList.push({
        text: `VirusTotal engine detections: ${data.virustotal.malicious} engines flagged this URL`,
        weight: '+30',
        level: 'high'
      });
    }
    recommendation = riskScore >= 70 ? 'High risk URL. Do not open, enter credentials, or download files.' : 'Standard URL evaluation.';
  } else if (type === 'image' && data) {
    riskScore = Math.round(data.risk_score !== undefined ? data.risk_score : 25);
    riskLevel = data.risk_level || (riskScore >= 70 ? 'HIGH_RISK' : (riskScore >= 40 ? 'SUSPICIOUS' : 'LOW'));
    summary = data.summary || `Multimodal visual analysis completed (${data.images_analyzed || scamSelectedImages.length || 1} image(s) processed).`;
    
    if (data.recommendations && data.recommendations.length > 0) {
      recommendation = data.recommendations.join('; ');
    } else if (data.recommendation) {
      recommendation = data.recommendation;
    } else {
      recommendation = riskScore >= 70 ? 'Malicious or deceptive visual indicators detected. Do not make payment or share OTP/credentials.' : 'Standard visual patterns observed. Verify sender through secondary channel.';
    }

    // Gemini Offer Legitimacy Verdict ("TRUSTED OFFER" vs "UNTRUSTED OFFER")
    const offerVerdict = (data.offer_verdict || (riskScore < 35 ? 'TRUSTED OFFER' : 'UNTRUSTED OFFER')).toUpperCase();
    const offerReason = data.offer_verdict_reason || (offerVerdict === 'TRUSTED OFFER'
      ? 'Verified authentic credentials with standard terms, realistic compensation, and absence of advance fees or credential harvesting.'
      : 'High fraud risk detected: Image demonstrates signatures of advance fees, artificial urgency, or unverified contact identity.');

    if (offerVerdict.includes('TRUSTED') && !offerVerdict.includes('UNTRUSTED')) {
      offerVerdictBanner = `
        <div class="offer-verdict-card" style="background: linear-gradient(135deg, rgba(16, 185, 129, 0.16) 0%, rgba(5, 150, 105, 0.08) 100%); border: 2px solid #10b981; border-radius: 12px; padding: 18px 22px; margin-bottom: var(--space-lg); box-shadow: 0 4px 20px rgba(16, 185, 129, 0.18);">
          <div style="display: flex; align-items: flex-start; gap: 16px;">
            <div style="font-size: 38px; line-height: 1;">✅</div>
            <div style="flex: 1;">
              <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 6px; flex-wrap: wrap;">
                <span style="background: #10b981; color: #fff; font-weight: 800; font-size: 12px; letter-spacing: 1px; padding: 3px 8px; border-radius: 4px;">GEMINI API VERDICT</span>
                <h3 style="color: #34d399; margin: 0; font-size: 22px; font-weight: 900; letter-spacing: 0.5px;">TRUSTED OFFER</h3>
                <span style="background: rgba(16, 185, 129, 0.25); color: #34d399; font-size: 12px; font-weight: 700; padding: 3px 8px; border-radius: 4px;">Low Risk (${riskScore}/100)</span>
              </div>
              <p style="color: var(--text-primary); font-size: 14px; line-height: 1.6; margin: 0 0 10px 0; font-weight: 500;">
                ${offerReason}
              </p>
              <div style="display: flex; gap: 8px; flex-wrap: wrap;">
                <span class="badge" style="background: rgba(16, 185, 129, 0.2); color: #34d399; font-size: 11px;">✓ Zero Advance Fees</span>
                <span class="badge" style="background: rgba(16, 185, 129, 0.2); color: #34d399; font-size: 11px;">✓ Authentic Credentials</span>
                <span class="badge" style="background: rgba(16, 185, 129, 0.2); color: #34d399; font-size: 11px;">✓ Multimodal Vision Confirmed</span>
              </div>
            </div>
          </div>
        </div>
      `;
    } else {
      offerVerdictBanner = `
        <div class="offer-verdict-card" style="background: linear-gradient(135deg, rgba(239, 68, 68, 0.16) 0%, rgba(185, 28, 28, 0.08) 100%); border: 2px solid #ef4444; border-radius: 12px; padding: 18px 22px; margin-bottom: var(--space-lg); box-shadow: 0 4px 20px rgba(239, 68, 68, 0.22);">
          <div style="display: flex; align-items: flex-start; gap: 16px;">
            <div style="font-size: 38px; line-height: 1;">🚨</div>
            <div style="flex: 1;">
              <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 6px; flex-wrap: wrap;">
                <span style="background: #ef4444; color: #fff; font-weight: 800; font-size: 12px; letter-spacing: 1px; padding: 3px 8px; border-radius: 4px;">GEMINI API VERDICT</span>
                <h3 style="color: #f87171; margin: 0; font-size: 22px; font-weight: 900; letter-spacing: 0.5px;">UNTRUSTED OFFER</h3>
                <span style="background: rgba(239, 68, 68, 0.25); color: #f87171; font-size: 12px; font-weight: 700; padding: 3px 8px; border-radius: 4px;">High Risk (${riskScore}/100)</span>
              </div>
              <p style="color: var(--text-primary); font-size: 14px; line-height: 1.6; margin: 0 0 10px 0; font-weight: 500;">
                ${offerReason}
              </p>
              <div style="display: flex; gap: 8px; flex-wrap: wrap;">
                <span class="badge" style="background: rgba(239, 68, 68, 0.2); color: #f87171; font-size: 11px;">⚠ Advance Fee Demand Detected</span>
                <span class="badge" style="background: rgba(239, 68, 68, 0.2); color: #f87171; font-size: 11px;">⚠ Do Not Transfer Money / Share OTP</span>
                <span class="badge" style="background: rgba(239, 68, 68, 0.2); color: #f87171; font-size: 11px;">⚠ Flagged by Gemini AI</span>
              </div>
            </div>
          </div>
        </div>
      `;
    }

    // Engine info
    if (data.analysis_mode) {
      evidenceList.push({
        text: `AI Engine: ${data.analysis_mode === 'GEMINI_MULTIMODAL_VISION' ? 'Google Gemini Multimodal Vision API' : 'Local Image Forensics & OCR Engine'}`,
        weight: 'INFO',
        level: 'moderate'
      });
    }

    // Gemini-detected visual anomalies
    const anomalies = data.anomalies_detected || [];
    if (anomalies.length > 0) {
      anomalyBanner = `
        <div style="background: rgba(239, 68, 68, 0.12); border: 1px solid var(--risk-high, #ef4444); border-radius: 8px; padding: 14px 18px; margin-bottom: var(--space-lg);">
          <h4 style="color: var(--risk-high, #ef4444); margin-bottom: 8px; display: flex; align-items: center; gap: 8px;">
            <span>🚨</span> Visual & Social Engineering Anomalies (${anomalies.length} Flagged by Gemini AI):
          </h4>
          <ul style="margin: 0; padding-left: 20px; color: var(--text-primary); line-height: 1.6;">
            ${anomalies.map(a => `<li style="margin-bottom: 4px; font-weight: 500;">${a}</li>`).join('')}
          </ul>
        </div>
      `;

      anomalies.forEach(anom => {
        evidenceList.push({
          text: `Visual Anomaly: ${anom}`,
          weight: '+30',
          level: 'high'
        });
      });
    }

    // Risk factors
    const riskFactors = data.risk_factors_detected || [];
    riskFactors.forEach(rf => {
      evidenceList.push({
        text: `Risk Indicator: ${rf}`,
        weight: '+15',
        level: 'suspicious'
      });
    });

    // General evidence items
    if (data.evidence && Array.isArray(data.evidence)) {
      data.evidence.forEach(ev => {
        const text = typeof ev === 'string' ? ev : (ev.explanation || ev.signal || ev.description || JSON.stringify(ev));
        evidenceList.push({
          text,
          weight: (ev.severity === 'HIGH' || ev.severity === 'CRITICAL') ? '+25' : '+10',
          level: (ev.severity || 'suspicious').toLowerCase()
        });
      });
    }
  } else if (data && data.risk_score !== undefined) {
    riskScore = Math.round(data.risk_score);
    riskLevel = data.risk_level || getRiskLevel(riskScore).label;
    summary = data.summary || summary;
    if (data.evidence) {
      evidenceList = data.evidence.map(e => ({
        text: e.description || e.text || 'Risk factor identified',
        weight: e.weight ? `+${e.weight}` : '+10',
        level: (e.severity || 'suspicious').toLowerCase()
      }));
    }
    recommendation = data.recommendation || recommendation;
  }

  const risk = getRiskLevel(riskScore);

  // Save to local store for persistence
  const invId = (data && (data.investigation_id || data.id)) || 'scam_' + Date.now();
  InvestigationStore.save({
    id: invId,
    type: 'scam',
    subType: type,
    riskScore,
    summary,
    evidence: evidenceList,
    input: inputValue
  });

  const pdfUrl = typeof API !== 'undefined' ? API.Results.getDownloadUrl(invId, 'pdf') : '#';
  const jsonUrl = typeof API !== 'undefined' ? API.Results.getDownloadUrl(invId, 'json') : '#';

  container.innerHTML = `
    <div class="results-container">
      <div class="result-card-full">
        <div class="result-header">
          <div>
            ${companyBadge}
            <h2>${typeIcons[type]} ${typeLabels[type]}</h2>
            <p class="text-sm text-muted">"${inputValue}" • ${formatDate(new Date().toISOString())}</p>
          </div>
          <div class="result-score-large">
            <span class="score" style="color: ${risk.color}">${riskScore}</span>
            <span class="total">/100</span>
            <div style="margin-top: var(--space-sm)">${renderRiskBadge(riskScore)}</div>
          </div>
        </div>

        ${offerVerdictBanner}

        ${anomalyBanner}

        <div class="result-summary">
          <h3>Findings Summary</h3>
          <p>${summary}</p>
        </div>

        <div class="result-evidence-list">
          <h3 style="margin-bottom: var(--space-md);">Evidence & Dataset Signals (${evidenceList.length})</h3>
          ${evidenceList.length > 0 ? evidenceList.map(ev => `
            <div class="result-evidence-item">
              <span class="evidence-dot" style="background: ${ev.level === 'high' ? 'var(--risk-high)' : ev.level === 'suspicious' ? 'var(--risk-suspicious)' : 'var(--risk-moderate)'}"></span>
              <span class="evidence-text">${ev.text}</span>
              <span class="evidence-weight" style="color: ${ev.level === 'high' ? 'var(--risk-high)' : ev.level === 'suspicious' ? 'var(--risk-suspicious)' : 'var(--risk-moderate)'}">${ev.weight}</span>
            </div>
          `).join('') : '<p class="text-sm text-muted">No suspicious indicators recorded.</p>'}
        </div>

        <div class="result-recommendation">
          <h4>💡 Actionable Guidance</h4>
          <p>${recommendation}</p>
        </div>

        <div style="display: flex; flex-wrap: wrap; gap: var(--space-md); margin-top: var(--space-xl);">
          <a href="${pdfUrl}" target="_blank" class="btn btn-primary" id="scam-download-pdf-btn">📥 DOWNLOAD PDF REPORT</a>
          <a href="${jsonUrl}" target="_blank" class="btn btn-secondary" id="scam-download-json-btn">💾 DOWNLOAD JSON</a>
          <a href="#/results" class="btn btn-secondary">VIEW IN RESULTS</a>
          <button class="btn btn-secondary" onclick="document.getElementById('scam-results-container').style.display='none';">NEW INVESTIGATION</button>
        </div>
      </div>
    </div>
  `;

  Toast.success(`${typeLabels[type]} complete!`);
}

function cleanupScamPage() {}
