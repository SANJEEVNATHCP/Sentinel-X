/* =============================================
   FRAUDLENS AI — RESULTS / HISTORY PAGE
   ============================================= */

function renderResultsPage() {
  const all = InvestigationStore.getAll();
  const hash = window.location.hash;
  const idMatch = hash.match(/id=([\w_]+)/);

  // If specific ID, show detail
  if (idMatch) {
    const inv = InvestigationStore.getById(idMatch[1]);
    if (inv) return renderResultDetail(inv);
  }

  return `
    <div class="page-wrapper results-page">
      <div class="container">
        <div class="page-header">
          <a href="#/dashboard" class="btn btn-ghost btn-sm" style="margin-bottom: var(--space-md);">← Back to Dashboard</a>
          <h1>Your Investigation <span class="text-gradient">History</span></h1>
          <div class="divider"></div>
          <p>Every completed investigation, summarized in one place.</p>
        </div>

        ${all.length > 0 ? `
          <!-- Filters -->
          <div class="filter-bar" role="tablist" aria-label="Filter investigations">
            <button class="filter-pill active" data-filter="all" role="tab" aria-selected="true">All</button>
            <button class="filter-pill" data-filter="upi" role="tab">UPI</button>
            <button class="filter-pill" data-filter="scam" role="tab">Scam</button>
            <button class="filter-pill" data-filter="high" role="tab">High Risk</button>
            <button class="filter-pill" data-filter="suspicious" role="tab">Suspicious</button>
          </div>

          <!-- Search -->
          <div class="search-input-wrap">
            <span class="search-icon" aria-hidden="true">🔍</span>
            <input type="text" class="search-input" id="results-search" 
                   placeholder="Search investigations..." 
                   aria-label="Search investigations">
          </div>

          <!-- Results List -->
          <div id="results-list">
            ${renderResultsList(all)}
          </div>
        ` : `
          ${renderEmptyState(
            '🔎',
            'No investigations yet.',
            'Your first analysis will appear here.',
            'START ANALYSIS',
            '#/upi'
          )}
        `}
      </div>
    </div>
  `;
}

function renderResultsList(investigations) {
  if (investigations.length === 0) {
    return `
      <div class="empty-state" style="padding: var(--space-2xl);">
        <p style="color: var(--text-muted);">No matching investigations found.</p>
      </div>
    `;
  }

  return investigations.map(inv => {
    const risk = getRiskLevel(inv.riskScore);
    const typeIcon = inv.type === 'upi' ? '💳' : '🛡';
    const typeLabel = inv.type === 'upi' ? 'UPI ANALYSIS' : `SCAM — ${(inv.subType || 'general').toUpperCase()}`;

    return `
      <div class="investigation-card" data-type="${inv.type}" data-score="${inv.riskScore}" data-id="${inv.id}">
        <div class="investigation-card-header">
          <div>
            <span style="display: flex; align-items: center; gap: 6px; font-size: var(--fs-xs); font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; color: var(--text-accent); margin-bottom: 4px;">
              ${typeIcon} ${typeLabel}
            </span>
            <span class="text-xs text-muted">${formatDate(inv.createdAt)}</span>
          </div>
          <div style="text-align: right;">
            <div style="font-size: var(--fs-3xl); font-weight: 900; color: ${risk.color}; line-height: 1;">${inv.riskScore}</div>
            <div class="text-xs text-muted">/100</div>
          </div>
        </div>

        <div class="investigation-card-body">
          ${renderRiskBadge(inv.riskScore)}
          <p class="summary" style="margin-top: var(--space-sm);">${inv.summary || 'Investigation completed.'}</p>
        </div>

        <div class="investigation-card-footer">
          <a href="#/results?id=${inv.id}" class="btn btn-secondary btn-sm">VIEW REPORT</a>
          <button class="btn btn-ghost btn-sm delete-inv-btn" data-id="${inv.id}" aria-label="Delete investigation">🗑</button>
        </div>
      </div>
    `;
  }).join('');
}

function renderResultDetail(inv) {
  const risk = getRiskLevel(inv.riskScore);
  const typeIcon = inv.type === 'upi' ? '💳' : '🛡';

  return `
    <div class="page-wrapper results-page">
      <div class="container">
        <div class="page-header" style="text-align: left;">
          <a href="#/results" class="btn btn-ghost btn-sm" style="margin-bottom: var(--space-md);">← Back to Results</a>
        </div>

        <div class="results-container">
          <div class="result-card-full">
            <div class="result-header">
              <div>
                <h2>${typeIcon} ${inv.type === 'upi' ? 'UPI Analysis' : 'Scam Investigation'} Report</h2>
                <p class="text-sm text-muted">${inv.input || inv.fileName || ''} • ${formatDate(inv.createdAt)}</p>
              </div>
              <div class="result-score-large">
                <span class="score" style="color: ${risk.color}">${inv.riskScore}</span>
                <span class="total">/100</span>
                <div style="margin-top: var(--space-sm)">${renderRiskBadge(inv.riskScore)}</div>
              </div>
            </div>

            <div class="result-summary">
              <h3>Summary</h3>
              <p>${inv.summary || 'Investigation completed.'}</p>
            </div>

            ${inv.evidence && inv.evidence.length > 0 ? `
              <div class="result-evidence-list">
                <h3 style="margin-bottom: var(--space-md);">Evidence Detected</h3>
                ${inv.evidence.map(ev => `
                  <div class="result-evidence-item">
                    <span class="evidence-dot" style="background: ${ev.level === 'high' ? 'var(--risk-high)' : ev.level === 'suspicious' ? 'var(--risk-suspicious)' : 'var(--risk-moderate)'}"></span>
                    <span class="evidence-text">${ev.text}</span>
                    <span class="evidence-weight" style="color: ${ev.level === 'high' ? 'var(--risk-high)' : ev.level === 'suspicious' ? 'var(--risk-suspicious)' : 'var(--risk-moderate)'}">${ev.weight}</span>
                  </div>
                `).join('')}
              </div>
            ` : ''}

            <div class="result-recommendation">
              <h4>💡 Recommendation</h4>
              <p>${inv.riskScore >= 70 
                ? 'High risk signals were detected. Exercise extreme caution with this entity.'
                : inv.riskScore >= 50 
                ? 'Suspicious indicators found. Verify through independent channels before proceeding.'
                : 'Minor concerns noted. Proceed with standard caution.'
              }</p>
            </div>

            <div style="display: flex; flex-wrap: wrap; gap: var(--space-md); margin-top: var(--space-xl); align-items: center;">
              <a href="${typeof API !== 'undefined' ? API.Results.getDownloadUrl(inv.investigation_id || inv.id, 'pdf') : '#'}" target="_blank" class="btn btn-primary">
                📥 DOWNLOAD PDF REPORT
              </a>
              <a href="${typeof API !== 'undefined' ? API.Results.getDownloadUrl(inv.investigation_id || inv.id, 'json') : '#'}" target="_blank" class="btn btn-secondary">
                📄 EXPORT JSON
              </a>
              <a href="#/results" class="btn btn-ghost">← ALL RESULTS</a>
              <button class="btn btn-danger btn-sm" onclick="deleteInvestigation('${inv.id}')">DELETE</button>
            </div>
          </div>
        </div>
      </div>
    </div>
  `;
}

function initResultsPage() {
  // Sync with backend on open
  if (typeof InvestigationStore !== 'undefined' && InvestigationStore.syncFromBackend) {
    InvestigationStore.syncFromBackend().then(() => {
      const activeFilter = document.querySelector('.filter-pill.active')?.dataset.filter || 'all';
      filterResults(activeFilter);
    }).catch(e => console.warn('Sync error:', e));
  }
  // Filter pills
  document.querySelectorAll('.filter-pill').forEach(pill => {
    pill.addEventListener('click', () => {
      document.querySelectorAll('.filter-pill').forEach(p => {
        p.classList.remove('active');
        p.setAttribute('aria-selected', 'false');
      });
      pill.classList.add('active');
      pill.setAttribute('aria-selected', 'true');

      filterResults(pill.dataset.filter);
    });
  });

  // Search
  const searchInput = document.getElementById('results-search');
  if (searchInput) {
    searchInput.addEventListener('input', () => {
      filterResults(document.querySelector('.filter-pill.active')?.dataset.filter || 'all');
    });
  }

  // Delete buttons
  document.querySelectorAll('.delete-inv-btn').forEach(btn => {
    btn.addEventListener('click', (e) => {
      e.stopPropagation();
      deleteInvestigation(btn.dataset.id);
    });
  });
}

function filterResults(filter) {
  const searchTerm = document.getElementById('results-search')?.value.toLowerCase() || '';
  let investigations = InvestigationStore.getAll();

  // Apply filter
  if (filter === 'upi') {
    investigations = investigations.filter(i => i.type === 'upi');
  } else if (filter === 'scam') {
    investigations = investigations.filter(i => i.type === 'scam');
  } else if (filter === 'high') {
    investigations = investigations.filter(i => i.riskScore >= 70);
  } else if (filter === 'suspicious') {
    investigations = investigations.filter(i => i.riskScore >= 50 && i.riskScore < 70);
  }

  // Apply search
  if (searchTerm) {
    investigations = investigations.filter(i =>
      (i.summary || '').toLowerCase().includes(searchTerm) ||
      (i.input || '').toLowerCase().includes(searchTerm) ||
      (i.fileName || '').toLowerCase().includes(searchTerm)
    );
  }

  const listEl = document.getElementById('results-list');
  if (listEl) {
    listEl.innerHTML = renderResultsList(investigations);

    // Re-bind delete buttons
    document.querySelectorAll('.delete-inv-btn').forEach(btn => {
      btn.addEventListener('click', (e) => {
        e.stopPropagation();
        deleteInvestigation(btn.dataset.id);
      });
    });
  }
}

function deleteInvestigation(id) {
  showConfirmModal(
    'Delete Investigation',
    'Are you sure you want to permanently delete this investigation? This action cannot be undone.',
    () => {
      InvestigationStore.delete(id);
      Toast.success('Investigation deleted.');
      // If on detail page, go back to list
      if (window.location.hash.includes('id=')) {
        window.location.hash = '#/results';
      } else {
        // Refresh list
        const activeFilter = document.querySelector('.filter-pill.active')?.dataset.filter || 'all';
        filterResults(activeFilter);
      }
    }
  );
}

function cleanupResultsPage() {}
