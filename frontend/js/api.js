const API_BASE = window.BHARATGRAPH_API_URL || "http://localhost:8000";

const Api = {
  _request: async (path, options = {}) => {
    const url = `${API_BASE}${path}`;
    try {
      const response = await fetch(url, {
        headers: { "Content-Type": "application/json", ...options.headers },
        ...options,
      });
      if (!response.ok) {
        const error = await response.json().catch(() => ({ detail: response.statusText }));
        throw new Error(error.detail || `HTTP ${response.status}`);
      }
      return response.json();
    } catch (err) {
      console.error(`[API] ${path}:`, err.message);
      throw err;
    }
  },

  health: () => Api._request("/health"),

  stats: () => Api._request("/stats"),

  search: (query, type = null, limit = 20, lang = "en") => {
    const params = new URLSearchParams({ q: query, limit });
    if (type)  params.append("type", type);
    if (lang && lang !== "en") params.append("lang", lang);
    return Api._request(`/search?${params}`);
  },

  profile: (entityId) => Api._request(`/profile/${entityId}`),

  risk: (entityId) => Api._request(`/risk/${entityId}`),

  graphConnections: (entityId, depth = 2) =>
    Api._request(`/graph/connections/${entityId}?depth=${depth}`),

  politicianContracts: (limit = 50) =>
    Api._request(`/graph/pattern/politician-contracts?limit=${limit}`),

  languages: () => Api._request("/languages"),

  multilingualSearch: (query, lang = "en") => {
    const params = new URLSearchParams({ q: query, lang });
    return Api._request(`/search/multilingual?${params}`);
  },

  riskMultilingual: (entityId, lang = "en") =>
    Api._request(`/risk/multilingual/${entityId}?lang=${lang}`),

  exportPdf: (entityId) => `${API_BASE}/export/pdf/${entityId}`,

  verifyHash: (hash) => Api._request(`/verify/${hash}`),

  nodeEvidence: (entityId) => Api._request(`/node-evidence/${entityId}`),

  createFeedSocket: () => {
    const wsUrl = API_BASE.replace(/^http/, "ws") + "/ws/feed";
    return new WebSocket(wsUrl);
  },
};

window.Api = Api;
