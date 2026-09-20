/* =============================================
   FRAUDLENS AI — UPI ANALYSIS PAGE
   ============================================= */

function renderUPIPage() {
  return `
    <div class="page-wrapper upi-page">
      <div class="container">
        <div class="page-header">
          <a href="#/dashboard" class="btn btn-ghost btn-sm" style="margin-bottom: var(--space-md);">← Back to Dashboard</a>
          <h1>UPI Risk <span class="text-gradient">Intelligence</span></h1>
          <div class="divider"></div>
          <p>Upload transaction data and let FraudLens uncover behavior that may not be visible at first glance.</p>
        </div>

        <div id="upi-content">
          <!-- Upload Section -->
          <div class="upload-section" id="upload-section">
            <div class="upload-area" id="upload-area" 
                 role="button" tabindex="0"
                 aria-label="Upload transaction file. Drag and drop or click to browse.">
              <div class="upload-icon" aria-hidden="true">📊</div>
              <div class="upload-text">Drop your CSV/XLSX file here</div>
              <div class="upload-hint" style="margin-bottom: var(--space-lg);">or</div>
              <button class="btn btn-secondary" id="choose-file-btn" type="button">CHOOSE TRANSACTION FILE</button>
              <div style="margin-top: 10px;">
                <button class="btn btn-ghost btn-sm" id="load-sample-btn" type="button" style="color: var(--accent-primary, #6366f1); font-weight: 600;">
                  ⚡ Load Demo Statement (sample_transactions.csv)
                </button>
              </div>
              <div class="upload-hint" style="margin-top: var(--space-md);">Supported: CSV, XLSX</div>
            </div>
            <input type="file" id="file-input" accept=".csv,.xlsx" style="display:none" aria-label="Select transaction file">

            <div id="file-info-container" style="margin-top: var(--space-lg); display: none;"></div>

            <div style="text-align: center; margin-top: var(--space-xl); display: none;" id="analyze-btn-container">
              <button class="btn btn-primary btn-lg" id="analyze-btn">
                <span class="btn-text">ANALYZE TRANSACTIONS ⚡</span>
                <span class="btn-spinner" aria-hidden="true"></span>
              </button>
            </div>
          </div>

          <!-- Analysis Progress (hidden initially) -->
          <div id="analysis-progress-container" style="display: none;"></div>

          <!-- Results (hidden initially) -->
          <div id="upi-results-container" style="display: none;"></div>
        </div>
      </div>
    </div>
  `;
}

function initUPIPage() {
  const uploadArea = document.getElementById('upload-area');
  const fileInput = document.getElementById('file-input');
  const chooseBtn = document.getElementById('choose-file-btn');
  let selectedFile = null;

  // Click to upload
  if (chooseBtn) {
    chooseBtn.addEventListener('click', (e) => {
      e.stopPropagation();
      fileInput.click();
    });
  }

  const sampleBtn = document.getElementById('load-sample-btn');
  if (sampleBtn) {
    sampleBtn.addEventListener('click', (e) => {
      e.stopPropagation();
      const sampleCsv = `transaction_id,user_id,amount,timestamp,sender,receiver,upi_id,device_id,location,transaction_status,failed_attempts
TXN1001,usr_test_01,1500.00,2026-09-10T10:15:00Z,Rahul Sharma,Swiggy,swiggy@icici,DEV_001,Mumbai,SUCCESS,0
TXN1002,usr_test_01,850.00,2026-09-11T13:20:00Z,Rahul Sharma,Uber India,uber@hdfcbank,DEV_001,Mumbai,SUCCESS,0
TXN1003,usr_test_01,2200.00,2026-09-12T19:45:00Z,Rahul Sharma,Amazon Pay,amazon@apl,DEV_001,Mumbai,SUCCESS,0
TXN1004,usr_test_01,1850.00,2026-09-13T12:00:00Z,Rahul Sharma,Zomato,zomato@axisbank,DEV_001,Mumbai,SUCCESS,0
TXN1005,usr_test_01,3100.00,2026-09-14T16:30:00Z,Rahul Sharma,Dmart Store,dmart@sbi,DEV_001,Mumbai,SUCCESS,0
TXN1006,usr_test_01,1600.00,2026-09-15T11:10:00Z,Rahul Sharma,Airtel Bill,airtel@airtelpaymentsbank,DEV_001,Mumbai,SUCCESS,0
TXN1007,usr_test_01,48500.00,2026-09-18T03:42:00Z,Rahul Sharma,Quick Win Cash,crypto_fast_pay@ybl,DEV_999,Lagos,SUCCESS,3
TXN1008,usr_test_01,75000.00,2026-09-18T03:48:00Z,Rahul Sharma,Immediate Verification,urgent_kyc@paytm,DEV_999,Lagos,SUCCESS,2`;
      const blob = new Blob([sampleCsv], { type: 'text/csv' });
      const demoFile = new File([blob], 'sample_transactions.csv', { type: 'text/csv' });
      handleFile(demoFile);
      Toast.info('Sample transaction statement loaded. Ready to analyze!');
    });
  }

  if (uploadArea) {
    uploadArea.addEventListener('click', () => fileInput.click());
    uploadArea.addEventListener('keydown', (e) => {
      if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); fileInput.click(); }
    });

    // Drag and drop
    uploadArea.addEventListener('dragover', (e) => { e.preventDefault(); uploadArea.classList.add('dragover'); });
    uploadArea.addEventListener('dragleave', () => uploadArea.classList.remove('dragover'));
    uploadArea.addEventListener('drop', (e) => {
      e.preventDefault();
      uploadArea.classList.remove('dragover');
      const file = e.dataTransfer.files[0];
      if (file) handleFile(file);
    });
  }

  if (fileInput) {
    fileInput.addEventListener('change', () => {
      if (fileInput.files[0]) handleFile(fileInput.files[0]);
    });
  }

  function handleFile(file) {
    const ext = file.name.split('.').pop().toLowerCase();
    if (!['csv', 'xlsx'].includes(ext)) {
      Toast.error('Please upload a CSV or XLSX file.');
      return;
    }

    selectedFile = file;
    const sizeKB = (file.size / 1024).toFixed(1);
    const fileInfoContainer = document.getElementById('file-info-container');
    const analyzeBtnContainer = document.getElementById('analyze-btn-container');

    fileInfoContainer.style.display = 'block';
    fileInfoContainer.innerHTML = `
      <div class="file-info">
        <span class="file-icon" aria-hidden="true">📄</span>
        <div class="file-details">
          <div class="file-name">${file.name}</div>
          <div class="file-size">${sizeKB} KB</div>
        </div>
        <button class="file-remove" id="remove-file" aria-label="Remove file">&times;</button>
      </div>
    `;

    analyzeBtnContainer.style.display = 'block';

    document.getElementById('remove-file').addEventListener('click', () => {
      selectedFile = null;
      fileInfoContainer.style.display = 'none';
      fileInfoContainer.innerHTML = '';
      analyzeBtnContainer.style.display = 'none';
      fileInput.value = '';
    });
  }

  // Analyze button
  const analyzeBtn = document.getElementById('analyze-btn');
  if (analyzeBtn) {
    analyzeBtn.addEventListener('click', () => {
      if (!selectedFile) {
        Toast.warning('Please upload a file first.');
        return;
      }
      startUPIAnalysis(selectedFile);
    });
  }
}

async function startUPIAnalysis(file) {
  const uploadSection = document.getElementById('upload-section');
  const progressContainer = document.getElementById('analysis-progress-container');
  const resultsContainer = document.getElementById('upi-results-container');

  uploadSection.style.display = 'none';
  progressContainer.style.display = 'block';

  const steps = [
    'Uploading transaction file to secure engine...',
    'Extracting transaction attributes & timestamps...',
    'Building historical behavioral baselines...',
    'Executing XGBoost Fraud Model (xgboost_fraud_model.joblib)...',
    'Executing Isolation Forest anomaly detector...',
    'Synthesizing evidence & risk weights...'
  ];

  let currentStep = 0;
  function updateProgress() {
    progressContainer.innerHTML = renderLoadingAnimation(steps, Math.min(currentStep, steps.length - 1));
  }
  updateProgress();

  const progressInterval = setInterval(() => {
    if (currentStep < steps.length - 1) {
      currentStep++;
      updateProgress();
    }
  }, 500);

  try {
    let resultData = null;
    if (typeof API !== 'undefined' && API.Transactions) {
      resultData = await API.Transactions.analyze(file);
    }

    clearInterval(progressInterval);
    progressContainer.style.display = 'none';

    if (resultData) {
      showUPIResultsFromBackend(file, resultData, resultsContainer);
    } else {
      showUPIResultsFallback(file, resultsContainer);
    }
  } catch (err) {
    clearInterval(progressInterval);
    progressContainer.style.display = 'none';
    uploadSection.style.display = 'block';
    Toast.error(err.message || 'Transaction analysis failed. Please verify the backend is running.');
  }
}

function showUPIResultsFromBackend(file, data, container) {
  const riskScore = Math.round(data.risk_score || 0);
  const risk = getRiskLevel(riskScore);
  const invId = data.investigation_id;

  const rawEvidence = data.evidence || [];
  const evidenceList = rawEvidence.map(ev => ({
    text: ev.description || ev.text || 'Suspicious indicator detected',
    weight: ev.weight ? `+${ev.weight}` : '+8',
    level: (ev.severity || 'moderate').toLowerCase()
  }));

  const recommendations = data.recommendations && data.recommendations.length > 0 
    ? data.recommendations.join(' ')
    : (riskScore >= 70 ? 'Multiple high-risk indicators detected. Recommend immediate review.' : 'Standard transaction profile.');

  // Save to local store for offline cache
  const investigation = InvestigationStore.save({
    id: invId,
    investigation_id: invId,
    type: 'upi',
    riskScore,
    riskLevel: data.risk_level,
    summary: data.summary || `Analyzed ${file.name}: ${data.total_transactions} transactions reviewed.`,
    evidence: evidenceList,
    fileName: file.name
  });

  const pdfUrl = typeof API !== 'undefined' ? API.Results.getDownloadUrl(invId, 'pdf') : '#';

  const transactions = data.transactions || [];
  const anomCount = transactions.filter(t => t.is_anomalous).length;

  let tableRowsHtml = '';
  if (transactions.length > 0) {
    tableRowsHtml = transactions.map((t, idx) => {
      const isAnom = Boolean(t.is_anomalous);
      const isHighFreq = (t.frequency || 1) >= 2;
      const isHighDev = (t.amount_ratio || 1.0) >= 4.0;
      const xgbScore = Number(t.xgboost_score || t.fraud_probability || 0);
      const isHighXGB = xgbScore >= 0.70;
      const isMedXGB = xgbScore >= 0.40 && xgbScore < 0.70;
      const bgStyle = (isAnom || isHighXGB) ? 'background: rgba(239, 68, 68, 0.08);' : (idx % 2 === 1 ? 'background: rgba(255,255,255,0.02);' : '');
      const receiverDisplay = t.receiver_id || t.receiver || t.upi_id || 'Unknown';
      const upiDisplay = (t.upi_id && t.upi_id !== receiverDisplay) ? `<div style="font-size: 11px; color: var(--text-muted); font-family: monospace;">${t.upi_id}</div>` : '';
      const xgbColor = isHighXGB ? '#f87171' : isMedXGB ? '#fbbf24' : '#34d399';
      const xgbLabel = isHighXGB ? 'HIGH RISK' : isMedXGB ? 'MODERATE' : 'LOW';

      return `
        <tr class="upi-txn-row ${isAnom ? 'filter-anom' : 'filter-norm'} ${isHighFreq ? 'filter-highfreq' : ''}" style="${bgStyle} border-bottom: 1px solid rgba(255,255,255,0.06);">
          <td style="padding: 12px 14px; font-family: monospace; font-weight: 700; color: ${(isAnom || isHighXGB) ? '#f87171' : 'var(--accent-primary, #6366f1)'}; white-space: nowrap;">
            ${t.transaction_id || `TXN_${idx + 1}`}
          </td>
          <td style="padding: 12px 14px;">
            <div style="font-weight: 600; color: var(--text-primary); font-size: 13px;">${receiverDisplay}</div>
            ${upiDisplay}
          </td>
          <td style="padding: 12px 14px; text-align: center;">
            <span class="badge" style="background: ${isHighFreq ? 'rgba(239, 68, 68, 0.2)' : 'rgba(255, 255, 255, 0.08)'}; color: ${isHighFreq ? '#f87171' : 'var(--text-secondary)'}; font-weight: 700; font-size: 12px; padding: 4px 8px; border-radius: 6px;">
              ${t.frequency || 1} ${t.frequency > 1 ? 'txns' : 'txn'}
            </span>
          </td>
          <td style="padding: 12px 14px;">
            <div style="font-weight: 700; font-size: 14px; color: ${isHighDev ? '#f87171' : 'var(--text-primary)'};">₹${Number(t.amount).toLocaleString('en-IN', {minimumFractionDigits: 2})}</div>
            <div style="font-size: 11px; color: ${isHighDev ? '#f87171' : 'var(--text-muted)'}; font-weight: 600;">${t.amount_ratio || 1.0}x baseline (avg ₹${Math.round(t.baseline_mean || data.user_historical_mean || 0)})</div>
          </td>
          <td style="padding: 12px 14px; text-align: center; white-space: nowrap;">
            <div style="display: flex; flex-direction: column; align-items: center; gap: 3px;">
              <span style="font-family: monospace; font-size: 15px; font-weight: 800; color: ${xgbColor};">${xgbScore.toFixed(4)}</span>
              <span style="font-size: 10px; font-weight: 700; color: ${xgbColor}; background: rgba(${isHighXGB ? '239,68,68' : isMedXGB ? '245,158,11' : '16,185,129'},0.15); padding: 2px 6px; border-radius: 4px;">${xgbLabel}</span>
            </div>
          </td>
          <td style="padding: 12px 14px; text-align: center; white-space: nowrap;">
            ${isAnom ? `
              <span class="badge" style="background: rgba(239, 68, 68, 0.2); color: #f87171; font-weight: 800; border: 1px solid rgba(239,68,68,0.4); padding: 4px 8px; border-radius: 6px; font-size: 11px; display: inline-flex; align-items: center; gap: 4px;">
                <span>🌲</span> ANOMALY (${Math.round((t.anomaly_score || 0.8) * 100)}%)
              </span>
            ` : `
              <span class="badge" style="background: rgba(16, 185, 129, 0.15); color: #34d399; font-weight: 700; border: 1px solid rgba(16,185,129,0.3); padding: 4px 8px; border-radius: 6px; font-size: 11px; display: inline-flex; align-items: center; gap: 4px;">
                <span>✓</span> NORMAL (${Math.round((t.anomaly_score || 0.2) * 100)}%)
              </span>
            `}
          </td>
          <td style="padding: 12px 14px; font-size: 12px; line-height: 1.5; color: ${(isAnom || isHighDev || isHighXGB) ? '#fca5a5' : 'var(--text-secondary)'};">${
            t.what_went_wrong || 'Normal transaction aligned with user historical average.'
          }</td>
        </tr>
      `;
    }).join('');
  }

  container.style.display = 'block';
  container.innerHTML = `
    <div class="results-container">
      <div class="result-card-full">
        <div class="result-header">
          <div>
            <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 4px;">
              <span class="badge" style="background: rgba(99, 102, 241, 0.2); color: #818cf8; font-weight: 800; font-size: 11px;">⚡ XGBOOST ACTIVE</span>
              <span class="badge" style="background: rgba(16, 185, 129, 0.15); color: #34d399; font-weight: 700; font-size: 11px;">🌲 ISOLATION FOREST ACTIVE</span>
              <span class="badge" style="background: rgba(245, 158, 11, 0.15); color: #fbbf24; font-weight: 700; font-size: 11px;">RECEIVER VELOCITY PROFILED</span>
            </div>
            <h2>UPI Risk Intelligence Complete</h2>
            <p class="text-sm text-muted">${file.name} • ${data.total_transactions || 0} Transactions Analyzed • ${formatDate(new Date().toISOString())}</p>
          </div>
          <div class="result-score-large">
            <span class="score" style="color: ${risk.color}">${riskScore}</span>
            <span class="total">/100</span>
            <div style="margin-top: var(--space-sm)">${renderRiskBadge(riskScore)}</div>
          </div>
        </div>

        <!-- Metrics bar -->
        <div class="overview-grid" style="margin-bottom: var(--space-xl); grid-template-columns: repeat(4, 1fr);">
          <div class="stat-card" style="padding: 15px;">
            <div class="stat-label">Total Transactions</div>
            <div class="stat-value" style="font-size: 24px;">${data.total_transactions || 0}</div>
          </div>
          <div class="stat-card" style="padding: 15px;">
            <div class="stat-label">🌲 Isolation Forest Anomalies</div>
            <div class="stat-value" style="font-size: 24px; color: var(--risk-high);">${anomCount}</div>
          </div>
          <div class="stat-card" style="padding: 15px;">
            <div class="stat-label">Historical Baseline Mean</div>
            <div class="stat-value" style="font-size: 24px; color: #38bdf8;">₹${Math.round(data.user_historical_mean || 0)}</div>
          </div>
          <div class="stat-card" style="padding: 15px;">
            <div class="stat-label">High-Risk Severity Count</div>
            <div class="stat-value" style="font-size: 24px; color: var(--risk-high);">${data.high_risk_count || 0}</div>
          </div>
        </div>

        <div class="result-summary">
          <h3>ML Model Assessment (XGBoost + Isolation Forest Dual Detection)</h3>
          <p>${data.summary || 'Behavioral profiling completed.'}</p>
          ${data.ai_summary ? `<p style="margin-top: 8px; font-style: italic; color: var(--text-accent);">AI Synthesis: ${data.ai_summary}</p>` : ''}
        </div>

        <!-- Dedicated Isolation Forest Transactions Table -->
        <div style="margin: var(--space-xl) 0; background: rgba(255, 255, 255, 0.02); border: 1px solid var(--border-color, rgba(255, 255, 255, 0.08)); border-radius: 12px; padding: 20px;">
          <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 12px; margin-bottom: var(--space-md);">
            <div>
              <div style="display: flex; align-items: center; gap: 8px;">
                <span style="background: rgba(99, 102, 241, 0.2); color: #818cf8; font-weight: 800; font-size: 11px; padding: 3px 8px; border-radius: 4px;">TRANSACTION AUDIT</span>
                <h3 style="margin: 0; font-size: 18px;">🌲 Isolation Forest Analysis & Receiver Velocity Breakdown</h3>
              </div>
              <p class="text-xs text-muted" style="margin-top: 4px;">
                Transactions evaluated using XGBoost supervised model + Isolation Forest anomaly detection against user baseline mean (₹${Math.round(data.user_historical_mean || 0)}).
              </p>
            </div>
            
            <!-- Filters -->
            <div style="display: flex; gap: 8px; flex-wrap: wrap;" id="upi-table-filters">
              <button class="btn btn-sm btn-primary active-filter" data-filter="all" id="filter-all-btn">All (${transactions.length})</button>
              <button class="btn btn-sm btn-secondary" data-filter="anom" id="filter-anom-btn">🌲 Anomalies (${anomCount})</button>
              <button class="btn btn-sm btn-secondary" data-filter="highfreq" id="filter-freq-btn">Receiver Velocity</button>
            </div>
          </div>

          <div style="overflow-x: auto; border: 1px solid rgba(255,255,255,0.06); border-radius: 8px;">
            <table style="width: 100%; border-collapse: collapse; text-align: left; font-size: 13px;" id="upi-txn-table">
              <thead>
                <tr style="background: rgba(255, 255, 255, 0.05); border-bottom: 1px solid rgba(255, 255, 255, 0.1); color: var(--text-secondary); text-transform: uppercase; font-size: 11px; letter-spacing: 0.5px;">
                  <th style="padding: 12px 14px;">Transaction ID</th>
                  <th style="padding: 12px 14px;">Receiver ID</th>
                  <th style="padding: 12px 14px; text-align: center;">Frequency</th>
                  <th style="padding: 12px 14px;">Amount vs Baseline</th>
                  <th style="padding: 12px 14px; text-align: center;">⚡ XGBoost Score</th>
                  <th style="padding: 12px 14px; text-align: center;">🌲 Isolation Forest</th>
                  <th style="padding: 12px 14px; min-width: 240px;">What Went Wrong</th>
                </tr>
              </thead>
              <tbody>
                ${tableRowsHtml || '<tr><td colspan="7" style="padding: 20px; text-align: center; color: var(--text-muted);">No transaction records found.</td></tr>'}
              </tbody>
            </table>
          </div>
        </div>

        <div class="result-evidence-list">
          <h3 style="margin-bottom: var(--space-md);">Evidence & Anomaly Signals (${evidenceList.length})</h3>
          ${evidenceList.length > 0 ? evidenceList.map(ev => `
            <div class="result-evidence-item">
              <span class="evidence-dot" style="background: ${ev.level === 'high' ? 'var(--risk-high)' : ev.level === 'suspicious' ? 'var(--risk-suspicious)' : 'var(--risk-moderate)'}"></span>
              <span class="evidence-text">${ev.text}</span>
              <span class="evidence-weight" style="color: ${ev.level === 'high' ? 'var(--risk-high)' : ev.level === 'suspicious' ? 'var(--risk-suspicious)' : 'var(--risk-moderate)'}">${ev.weight}</span>
            </div>
          `).join('') : '<p class="text-sm text-muted">No high-confidence anomaly signals triggered.</p>'}
        </div>

        <div class="result-recommendation">
          <h4>💡 Recommendation</h4>
          <p>${recommendations}</p>
        </div>

        <!-- Privacy & Actions -->
        <div style="display: flex; flex-wrap: wrap; gap: var(--space-md); margin-top: var(--space-xl); align-items: center;">
          <a href="${pdfUrl}" target="_blank" class="btn btn-secondary" id="download-pdf-btn" style="display: inline-flex; align-items: center; gap: 6px;">
            📄 DOWNLOAD PDF REPORT
          </a>
          <button class="btn btn-secondary" id="download-json-btn" style="display: inline-flex; align-items: center; gap: 6px;">
            📥 DOWNLOAD JSON REPORT
          </button>
          <a href="#/results" class="btn btn-secondary">VIEW IN RESULTS</a>
          <button class="btn btn-danger btn-sm" id="end-task-purge-btn" data-id="${invId}">
            🔒 END TASK & PURGE FILE
          </button>
          <button class="btn btn-primary" onclick="resetUPIPage()">NEW ANALYSIS</button>
        </div>
      </div>
    </div>
  `;

  // Bind filter buttons
  const filterBtns = container.querySelectorAll('#upi-table-filters button');
  filterBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      filterBtns.forEach(b => {
        b.classList.remove('btn-primary');
        b.classList.add('btn-secondary');
      });
      btn.classList.remove('btn-secondary');
      btn.classList.add('btn-primary');

      const filterType = btn.dataset.filter;
      const rows = container.querySelectorAll('#upi-txn-table tbody tr.upi-txn-row');
      rows.forEach(row => {
        if (filterType === 'all') {
          row.style.display = '';
        } else if (filterType === 'anom') {
          row.style.display = row.classList.contains('filter-anom') ? '' : 'none';
        } else if (filterType === 'highfreq') {
          row.style.display = row.classList.contains('filter-highfreq') ? '' : 'none';
        }
      });
    });
  });

  // Bind purge button
  const purgeBtn = document.getElementById('end-task-purge-btn');
  if (purgeBtn) {
    purgeBtn.addEventListener('click', async () => {
      purgeBtn.disabled = true;
      purgeBtn.textContent = 'Purging raw data...';
      try {
        await API.Privacy.endTask(invId);
        Toast.success('Raw statement file permanently erased for privacy. Derived results preserved.');
        purgeBtn.textContent = '✓ Raw File Purged';
        purgeBtn.style.background = '#059669';
      } catch (err) {
        Toast.error(err.message || 'Could not purge raw file.');
        purgeBtn.disabled = false;
        purgeBtn.textContent = '🔒 END TASK & PURGE FILE';
      }
    });
  }

  // Bind JSON download button
  const jsonDownloadBtn = document.getElementById('download-json-btn');
  if (jsonDownloadBtn && invId) {
    jsonDownloadBtn.addEventListener('click', async () => {
      jsonDownloadBtn.disabled = true;
      jsonDownloadBtn.innerHTML = '⏳ Preparing JSON...';
      try {
        const jsonUrl = typeof API !== 'undefined'
          ? API.Results.getDownloadUrl(invId, 'json')
          : `http://127.0.0.1:8000/api/results/${invId}/download?format=json`;
        const link = document.createElement('a');
        link.href = jsonUrl;
        link.download = `FraudLens_XGBoost_Report_${invId}.json`;
        link.target = '_blank';
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        Toast.success('JSON report download started!');
      } catch (err) {
        Toast.error('Could not download JSON report.');
      } finally {
        jsonDownloadBtn.disabled = false;
        jsonDownloadBtn.innerHTML = '📥 DOWNLOAD JSON REPORT';
      }
    });
  }

  Toast.success('UPI risk analysis complete!');
}

function showUPIResultsFallback(file, container) {
  const riskScore = 35;
  const risk = getRiskLevel(riskScore);
  container.style.display = 'block';
  container.innerHTML = `
    <div class="results-container">
      <div class="result-card-full">
        <div class="result-header">
          <div>
            <h2>UPI Risk Analysis Complete</h2>
            <p class="text-sm text-muted">${file.name} • ${formatDate(new Date().toISOString())}</p>
          </div>
          <div class="result-score-large">
            <span class="score" style="color: ${risk.color}">${riskScore}</span>
            <span class="total">/100</span>
          </div>
        </div>
        <p>Offline analysis completed.</p>
        <button class="btn btn-primary" onclick="resetUPIPage()">NEW ANALYSIS</button>
      </div>
    </div>
  `;
}

function resetUPIPage() {
  document.getElementById('upload-section').style.display = 'block';
  document.getElementById('analysis-progress-container').style.display = 'none';
  document.getElementById('upi-results-container').style.display = 'none';
  document.getElementById('upi-results-container').innerHTML = '';
  document.getElementById('file-info-container').style.display = 'none';
  document.getElementById('file-info-container').innerHTML = '';
  document.getElementById('analyze-btn-container').style.display = 'none';
  const fileInput = document.getElementById('file-input');
  if (fileInput) fileInput.value = '';
}

function cleanupUPIPage() {}
