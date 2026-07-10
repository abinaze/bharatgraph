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
      // CodeQL #22 FIX: avoid template literal with user-controlled path
      console.error("[API] request failed for path: " + String(path).substring(0, 100) + " -- " + String(err.message).substring(0, 200));
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

  multilingualSearch: (query, lang = "en") => {
    const params = new URLSearchParams({ q: query, lang });
    return Api._request(`/search/multilingual?${params}`);
  },

  riskMultilingual: (entityId, lang = "en") =>
    Api._request(`/risk/multilingual/${entityId}?lang=${lang}`),

  exportPdf: (entityId) => `${API_BASE}/export/pdf/${entityId}`,

  verifyHash: (hash) => Api._request(`/verify/${hash}`),

  nodeEvidence: (entityId) => Api._request(`/node-evidence/${entityId}`),

  // Phase 33: timeline
  timeline: function(entityId, category) {
    var p = category ? "?category=" + encodeURIComponent(category) : "";
    return Api._request("/timeline/" + entityId + p);
  },
  timelineByYear: function(entityId) {
    return Api._request("/timeline/" + entityId + "/by-year");
  },
  // Phase 33: graph analytics
  graphAnalytics: function(entityId, depth) {
    var d = depth ? "?depth=" + depth : "";
    return Api._request("/graph/analytics/" + entityId + d);
  },
  graphBetweenness: function(limit) {
    var l = limit ? "?limit=" + limit : "";
    return Api._request("/graph/centrality/betweenness" + l);
  },
  graphPagerank: function(limit) {
    var l = limit ? "?limit=" + limit : "";
    return Api._request("/graph/centrality/pagerank" + l);
  },
  graphCommunities: function(minSize) {
    var m = minSize ? "?min_size=" + minSize : "";
    return Api._request("/graph/communities" + m);
  },

  // Phase 34: forensic detection

  // Phase 35: investigation (multi-investigator results)
  investigate: function(entityId) {
    return Api._request("/investigate/" + entityId);
  },
  forensicsCircularOwnership: function(maxLen) {
    var p = maxLen ? "?max_cycle_length=" + maxLen : "";
    return Api._request("/forensics/circular-ownership" + p);
  },
  forensicsGhostCompanies: function(minScore) {
    var p = minScore ? "?min_score=" + minScore : "";
    return Api._request("/forensics/ghost-companies" + p);
  },
  forensicsShadowDirectors: function(minCount) {
    var p = minCount ? "?min_company_count=" + minCount : "";
    return Api._request("/forensics/shadow-directors" + p);
  },
  forensicsBenfords: function(entityId) {
    return Api._request("/forensics/benfords/" + entityId);
  },
  // Phase 34: self-learning
  selfLearningPatterns: function() {
    return Api._request("/self-learning/patterns");
  },
  selfLearningWeights: function() {
    return Api._request("/self-learning/weights");
  },
  selfLearningAudit: function() {
    return Api._request("/self-learning/audit");
  },
  // Phase 34: case memory
  caseMemoryStats: function() {
    return Api._request("/case-memory/stats");
  },
  caseMemorySimilar: function(findingTypes) {
    var p = findingTypes ? "?finding_types=" + encodeURIComponent(findingTypes) : "";
    return Api._request("/case-memory/similar" + p);
  },

  /**
   * BUG-7 FIX: was always sending text as a URL query string on a POST,
   * which caused 414 URI Too Long for text > ~2000 chars and silently
   * truncated anything beyond the browser's URL limit.
   *
   * Fix: short text (< 400 chars) keeps the fast query-param path;
   * long text is sent as a JSON body so there is no length limit.
   */
  translate: (text, sourceLang = "en", targetLang = "hi") => {
    const baseParams = new URLSearchParams({
      source_lang: sourceLang,
      target_lang: targetLang,
    });
    if (text.length < 400) {
      // Short text: send via query string (original fast path)
      baseParams.append("text", text);
      return Api._request(`/translate?${baseParams}`, { method: "POST" });
    }
    // Long text: send as JSON body to avoid URL length limits
    baseParams.append("text", "");           // keep param present but empty
    return Api._request(`/translate?${baseParams}`, {
      method: "POST",
      body: JSON.stringify({ text }),
    });
  },

  languages: () => Api._request("/languages"),

  uiLabels: (lang = "en") => Api._request(`/ui-labels?lang=${lang}`),

  createFeedSocket: () => {
    // L-02 FIX: strip trailing slash before appending /ws/feed
    // to avoid wss://example.com//ws/feed with double slash
    const wsUrl = API_BASE.replace(/\/$/, "").replace(/^http/, "ws") + "/ws/feed";
    return new WebSocket(wsUrl);
  },
};

window.Api = Api;
