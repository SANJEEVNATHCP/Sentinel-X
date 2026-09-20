/* =============================================
   FRAUDLENS AI — AUTH MODULE (CONNECTED TO BACKEND)
   ============================================= */

const Auth = {
  STORAGE_KEY: 'fraudlens_user',
  SESSION_KEY: 'fraudlens_session',

  async register(name, email, password, confirmPassword = null) {
    try {
      if (typeof API !== 'undefined' && API.Auth) {
        const res = await API.Auth.register(name, email, password, confirmPassword || password);
        return { success: true, user: res.user };
      }
    } catch (err) {
      console.warn('Backend registration failed, checking fallback:', err);
      return { success: false, error: err.message || 'Registration failed' };
    }

    // Fallback if API object not found
    const users = JSON.parse(localStorage.getItem('fraudlens_users') || '[]');
    if (users.find(u => u.email === email)) {
      return { success: false, error: 'An account with this email already exists.' };
    }
    const user = {
      id: 'usr_' + Date.now(),
      name,
      email,
      password: btoa(password),
      createdAt: new Date().toISOString()
    };
    users.push(user);
    localStorage.setItem('fraudlens_users', JSON.stringify(users));
    this._setSession(user);
    return { success: true, user };
  },

  async login(email, password) {
    try {
      if (typeof API !== 'undefined' && API.Auth) {
        const res = await API.Auth.login(email, password);
        const user = {
          id: res.user.id,
          name: res.user.full_name || res.user.name || 'User',
          email: res.user.email,
          createdAt: res.user.created_at || new Date().toISOString()
        };
        this._setSession(user);
        return { success: true, user };
      }
    } catch (err) {
      console.warn('Backend login failed:', err);
      return { success: false, error: err.message || 'Invalid email or password.' };
    }

    // Fallback if offline
    const users = JSON.parse(localStorage.getItem('fraudlens_users') || '[]');
    const user = users.find(u => u.email === email && u.password === btoa(password));
    if (!user) {
      return { success: false, error: 'Invalid email or password.' };
    }
    this._setSession(user);
    return { success: true, user };
  },

  async logout() {
    try {
      if (typeof API !== 'undefined' && API.Auth) {
        await API.Auth.logout();
      }
    } catch (e) {}
    localStorage.removeItem(this.SESSION_KEY);
    localStorage.removeItem(this.STORAGE_KEY);
    localStorage.removeItem('fraudlens_token');
  },

  isAuthenticated() {
    const hasToken = typeof API !== 'undefined' ? !!API.getToken() : false;
    const hasSession = !!localStorage.getItem(this.SESSION_KEY);
    return hasToken || hasSession;
  },

  getCurrentUser() {
    const data = localStorage.getItem(this.STORAGE_KEY);
    if (data) {
      try {
        const parsed = JSON.parse(data);
        return {
          id: parsed.id,
          name: parsed.name || parsed.full_name || 'Investigator',
          email: parsed.email || 'demo@fraudlens.ai',
          createdAt: parsed.createdAt || parsed.created_at || new Date().toISOString()
        };
      } catch (e) {}
    }
    return null;
  },

  _setSession(user) {
    const sessionUser = {
      id: user.id,
      name: user.name || user.full_name || 'Investigator',
      email: user.email,
      createdAt: user.createdAt || user.created_at || new Date().toISOString()
    };
    localStorage.setItem(this.STORAGE_KEY, JSON.stringify(sessionUser));
    localStorage.setItem(this.SESSION_KEY, Date.now().toString());
  }
};

/* =============================================
   INVESTIGATION DATA STORE & BACKEND BRIDGE
   ============================================= */
const InvestigationStore = {
  STORAGE_KEY: 'fraudlens_investigations',

  getAll() {
    return JSON.parse(localStorage.getItem(this.STORAGE_KEY) || '[]');
  },

  getByType(type) {
    return this.getAll().filter(i => (i.type || '').toLowerCase() === (type || '').toLowerCase());
  },

  getById(id) {
    return this.getAll().find(i => i.id === id || i.investigation_id === id);
  },

  save(investigation) {
    const all = this.getAll();
    investigation.id = investigation.id || 'inv_' + Date.now();
    investigation.createdAt = investigation.createdAt || new Date().toISOString();
    
    // Check if already exists in store
    const idx = all.findIndex(i => i.id === investigation.id);
    if (idx >= 0) {
      all[idx] = { ...all[idx], ...investigation };
    } else {
      all.unshift(investigation);
    }

    localStorage.setItem(this.STORAGE_KEY, JSON.stringify(all));
    return investigation;
  },

  delete(id) {
    const all = this.getAll().filter(i => i.id !== id && i.investigation_id !== id);
    localStorage.setItem(this.STORAGE_KEY, JSON.stringify(all));
    if (typeof API !== 'undefined' && API.Results) {
      API.Results.delete(id).catch(err => console.warn('Could not delete from backend:', err));
    }
  },

  getStats() {
    const all = this.getAll();
    return {
      total: all.length,
      highRisk: all.filter(i => (i.riskScore || i.risk_score || 0) >= 70).length,
      scam: all.filter(i => (i.type || '').toLowerCase().includes('scam') || (i.type || '').toLowerCase().includes('url')).length,
      upi: all.filter(i => (i.type || '').toLowerCase() === 'upi').length,
    };
  },

  getRecent(limit = 5) {
    return this.getAll().slice(0, limit);
  },

  async syncFromBackend() {
    if (typeof API === 'undefined' || !API.Results || !Auth.isAuthenticated()) return;
    try {
      const results = await API.Results.list();
      if (Array.isArray(results)) {
        const mapped = results.map(r => ({
          id: r.id,
          investigation_id: r.investigation_id,
          type: (r.type || '').toLowerCase(),
          riskScore: Math.round(r.risk_score || 0),
          riskLevel: r.risk_level,
          summary: r.summary,
          createdAt: r.created_at,
          evidence: []
        }));

        // Merge with local storage
        const currentLocal = this.getAll();
        const mergedMap = new Map();
        currentLocal.forEach(item => mergedMap.set(item.id, item));
        mapped.forEach(item => mergedMap.set(item.id, { ...mergedMap.get(item.id), ...item }));
        
        const mergedList = Array.from(mergedMap.values()).sort(
          (a, b) => new Date(b.createdAt) - new Date(a.createdAt)
        );
        localStorage.setItem(this.STORAGE_KEY, JSON.stringify(mergedList));
      }
    } catch (e) {
      console.warn('Could not sync results from backend:', e);
    }
  }
};

/* =============================================
   TOAST NOTIFICATION SYSTEM
   ============================================= */
const Toast = {
  container: null,

  init() {
    if (!this.container) {
      this.container = document.createElement('div');
      this.container.className = 'toast-container';
      this.container.setAttribute('role', 'status');
      this.container.setAttribute('aria-live', 'polite');
      document.body.appendChild(this.container);
    }
  },

  show(message, type = 'info', duration = 4000) {
    this.init();
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    const icons = { success: '✓', error: '✕', warning: '⚠', info: 'ℹ' };
    toast.innerHTML = `<span>${icons[type] || 'ℹ'}</span> <span>${message}</span>`;
    this.container.appendChild(toast);
    setTimeout(() => {
      toast.style.animation = 'fadeIn 0.3s ease reverse';
      setTimeout(() => toast.remove(), 300);
    }, duration);
  },

  success(msg) { this.show(msg, 'success'); },
  error(msg) { this.show(msg, 'error'); },
  warning(msg) { this.show(msg, 'warning'); },
  info(msg) { this.show(msg, 'info'); }
};
