/* =============================================
   FRAUDLENS AI — CENTRALIZED API CLIENT
   Connects the frontend seamlessly with the FastAPI backend on port 8000
   ============================================= */

const API_BASE = (typeof window !== 'undefined' && window.location && window.location.origin && window.location.origin.includes(':8000'))
  ? window.location.origin
  : 'http://127.0.0.1:8000';

const API = {
  BASE_URL: API_BASE,

  getToken() {
    return localStorage.getItem('fraudlens_token');
  },

  setToken(token) {
    if (token) {
      localStorage.setItem('fraudlens_token', token);
    } else {
      localStorage.removeItem('fraudlens_token');
    }
  },

  removeToken() {
    localStorage.removeItem('fraudlens_token');
  },

  async request(path, options = {}) {
    const url = `${this.BASE_URL}${path}`;
    const headers = options.headers || {};
    const token = this.getToken();

    if (token && !headers['Authorization']) {
      headers['Authorization'] = `Bearer ${token}`;
    }

    // Only set application/json if not sending FormData
    if (!(options.body instanceof FormData) && !headers['Content-Type']) {
      headers['Content-Type'] = 'application/json';
    }

    try {
      const response = await fetch(url, {
        ...options,
        headers
      });

      // Handle 204 No Content
      if (response.status === 204) {
        return null;
      }

      let data;
      const contentType = response.headers.get('content-type');
      if (contentType && contentType.includes('application/json')) {
        data = await response.json();
      } else {
        data = await response.text();
      }

      if (!response.ok) {
        const errorMsg = (data && (data.message || data.detail || data.error)) || `Request failed with status ${response.status}`;
        const error = new Error(errorMsg);
        error.status = response.status;
        error.data = data;
        throw error;
      }

      // Backend wraps responses in { status: "success", data: ... }
      if (data && typeof data === 'object' && 'data' in data && 'status' in data) {
        return data.data;
      }

      return data;
    } catch (err) {
      console.error(`API Error [${options.method || 'GET'} ${path}]:`, err);
      throw err;
    }
  },

  // ---------------------------------------------
  // Authentication Endpoints
  // ---------------------------------------------
  Auth: {
    async register(name, email, password, confirmPassword) {
      const payload = {
        name,
        email,
        password,
        confirm_password: confirmPassword || password
      };
      const res = await API.request('/api/auth/register', {
        method: 'POST',
        body: JSON.stringify(payload)
      });
      if (res && res.access_token) {
        API.setToken(res.access_token);
        localStorage.setItem('fraudlens_user', JSON.stringify(res.user));
        localStorage.setItem('fraudlens_session', Date.now().toString());
      }
      return res;
    },

    async login(email, password) {
      const payload = { email, password };
      const res = await API.request('/api/auth/login', {
        method: 'POST',
        body: JSON.stringify(payload)
      });
      if (res && res.access_token) {
        API.setToken(res.access_token);
        localStorage.setItem('fraudlens_user', JSON.stringify(res.user));
        localStorage.setItem('fraudlens_session', Date.now().toString());
      }
      return res;
    },

    async me() {
      return await API.request('/api/auth/me');
    },

    async logout() {
      try {
        await API.request('/api/auth/logout', { method: 'POST' });
      } catch (e) {
        // Continue local cleanup even if remote call fails
      }
      API.removeToken();
      localStorage.removeItem('fraudlens_user');
      localStorage.removeItem('fraudlens_session');
    }
  },

  // ---------------------------------------------
  // Dashboard & Metrics Endpoints
  // ---------------------------------------------
  Dashboard: {
    async get() {
      return await API.request('/api/dashboard');
    }
  },

  // ---------------------------------------------
  // UPI Transactions Endpoints
  // ---------------------------------------------
  Transactions: {
    async analyze(file) {
      const formData = new FormData();
      formData.append('file', file);
      return await API.request('/api/transactions/analyze', {
        method: 'POST',
        body: formData
      });
    }
  },

  // ---------------------------------------------
  // Scam & Company Intelligence Endpoints
  // ---------------------------------------------
  Scam: {
    async scanUrl(url) {
      return await API.request('/api/scam/url', {
        method: 'POST',
        body: JSON.stringify({ url })
      });
    },

    async verifyCompany(companyName, domain = null, recruiterEmail = null) {
      return await API.request('/api/company/verify', {
        method: 'POST',
        body: JSON.stringify({
          company_name: companyName,
          domain: domain || null,
          recruiter_email: recruiterEmail || null
        })
      });
    },

    async analyzeMulti(data) {
      return await API.request('/api/scam/analyze', {
        method: 'POST',
        body: JSON.stringify(data)
      });
    },

    async analyzeImage(files, context = null, customKey = null) {
      const formData = new FormData();
      if (Array.isArray(files) || (typeof FileList !== 'undefined' && files instanceof FileList)) {
        Array.from(files).slice(0, 3).forEach(f => {
          formData.append('files', f);
        });
        if (files.length > 0) {
          formData.append('file', files[0]);
        }
      } else if (files) {
        formData.append('file', files);
        formData.append('files', files);
      }
      if (context) {
        formData.append('context', context);
      }
      const headers = {};
      const key = customKey || localStorage.getItem('fraudlens_gemini_key');
      if (key && key.trim()) {
        headers['x-gemini-key'] = key.trim();
      }
      return await API.request('/api/scam/image-analysis', {
        method: 'POST',
        headers,
        body: formData
      });
    },

    async verifyOfferLetter(file, companyName = null) {
      const formData = new FormData();
      formData.append('file', file);
      if (companyName) formData.append('company_name', companyName);
      return await API.request('/api/company/offer-letter', {
        method: 'POST',
        body: formData
      });
    }
  },

  // ---------------------------------------------
  // Results & Reports Endpoints
  // ---------------------------------------------
  Results: {
    async list(type = null, riskLevel = null, search = null) {
      const params = new URLSearchParams();
      if (type) params.append('type', type);
      if (riskLevel) params.append('risk_level', riskLevel);
      if (search) params.append('search', search);

      const qs = params.toString();
      return await API.request(`/api/results${qs ? '?' + qs : ''}`);
    },

    async get(resultId) {
      return await API.request(`/api/results/${resultId}`);
    },

    async delete(resultId) {
      return await API.request(`/api/results/${resultId}`, {
        method: 'DELETE'
      });
    },

    getDownloadUrl(resultId, format = 'pdf') {
      const token = API.getToken();
      return `${API_BASE}/api/results/${resultId}/download?format=${format}&token=${encodeURIComponent(token || '')}`;
    },

    /**
     * Fetches the JSON report and triggers a browser file download.
     * The file is named FraudLens_XGBoost_Report_<resultId>.json.
     */
    async downloadJson(resultId) {
      const url = API.Results.getDownloadUrl(resultId, 'json');
      const response = await fetch(url);
      if (!response.ok) {
        const text = await response.text();
        throw new Error(text || `Download failed: ${response.status}`);
      }
      const blob = await response.blob();
      const objectUrl = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = objectUrl;
      link.download = `FraudLens_XGBoost_Report_${resultId}.json`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      URL.revokeObjectURL(objectUrl);
    }
  },

  // ---------------------------------------------
  // Privacy & Lifecycle Endpoints
  // ---------------------------------------------
  Privacy: {
    async endTask(investigationId) {
      return await API.request(`/api/investigations/${investigationId}/end`, {
        method: 'POST'
      });
    },

    async wipeAll() {
      return await API.request('/api/privacy/wipe-all', {
        method: 'POST'
      });
    }
  },

  // ---------------------------------------------
  // Health & Subsystem Diagnostics
  // ---------------------------------------------
  Health: {
    async check() {
      return await API.request('/api/health');
    }
  }
};
