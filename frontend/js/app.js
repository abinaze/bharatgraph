function sanitize(str) {
  const d = document.createElement("div");
  d.textContent = String(str || "");
  return d.innerHTML;
}

const State = {
  theme: localStorage.getItem("bg-theme") || "dark",
  language: "en",
  searchResults: [],
  currentEntity: null,
  feedSocket: null,
  apiConnected: false,
};

const Views = {
  home: () => {
    const main = document.getElementById("app-main");
    main.innerHTML = `
      <section style="padding:var(--space-20) 0 var(--space-12);">
        <div class="container container--narrow" style="text-align:center">
          <div style="font-size:11px;font-weight:600;letter-spacing:.15em;
                      text-transform:uppercase;color:var(--accent-primary);
                      margin-bottom:var(--space-4)">
            Sach Ko Prakash Mein Laana
          </div>
          <h1 style="font-size:clamp(2rem,5vw,3.5rem);font-weight:700;
                     color:var(--text-primary);margin-bottom:var(--space-4);
                     line-height:1.15">
            Public Transparency<br>
            <span style="color:var(--color-saffron)">Intelligence Platform</span>
          </h1>
          <p style="font-size:var(--font-size-lg);color:var(--text-secondary);
                    max-width:580px;margin:0 auto var(--space-10);
                    line-height:var(--line-height-relaxed)">
            Every claim backed by official records. Every relationship traceable
            to its source. Investigative intelligence for journalists, researchers,
            and citizens.
          </p>
          <div style="max-width:640px;margin:0 auto var(--space-4)">
            <div class="search-bar" id="home-search-bar">
              <input class="search-bar__input" id="home-search-input"
                     placeholder="Search any politician, company, scheme, or ministry"
                     autocomplete="off" spellcheck="false">
              <button class="search-bar__btn" id="home-search-btn">Search</button>
            </div>
          </div>
          <div style="display:flex;align-items:center;justify-content:center;
                      gap:var(--space-4);flex-wrap:wrap;font-size:var(--font-size-xs);
                      color:var(--text-muted)">
            <span>21 official data sources</span>
            <span>|</span>
            <span>12 parallel investigators</span>
            <span>|</span>
            <span>22 Indian languages</span>
          </div>
        </div>
      </section>

      <section style="padding:var(--space-12) 0;background:var(--bg-secondary);
                      border-top:1px solid var(--border-color);">
        <div class="container">
          <div class="grid grid--4" id="stats-grid">
            ${[1,2,3,4].map(() => `
              <div class="skeleton" style="height:100px;border-radius:12px"></div>
            `).join("")}
          </div>
        </div>
      </section>

      <section style="padding:var(--space-12) 0">
        <div class="container">
          <div style="display:grid;grid-template-columns:1fr 380px;gap:var(--space-8)">
            <div>
              <h2 class="section-title">How It Works</h2>
              <p class="section-subtitle">
                Enter any entity. The platform runs 12 specialist investigators
                in parallel, each analysing from a different angle.
                Findings are synthesised — where three or more investigators
                agree, confidence is marked as high.
              </p>
              <div style="display:flex;flex-direction:column;gap:var(--space-4)">
                ${[
                  ["01", "Search", "Enter any politician, company, ministry, or scheme name in any Indian language."],
                  ["02", "Investigate", "12 specialist AI investigators run in parallel across 21 official data sources."],
                  ["03", "Synthesise", "Findings are cross-validated. Agreed patterns are marked with high confidence."],
                  ["04", "Export", "Download a court-grade PDF dossier with a SHA-256 integrity hash."],
                ].map(([num, title, desc]) => `
                  <div style="display:flex;gap:var(--space-4);padding:var(--space-5);
                              background:var(--bg-card);border:1px solid var(--border-color);
                              border-radius:var(--radius-lg)">
                    <div style="width:36px;height:36px;border-radius:50%;
                                background:rgba(255,153,51,0.15);
                                display:flex;align-items:center;justify-content:center;
                                font-size:var(--font-size-xs);font-weight:700;
                                color:var(--color-saffron);flex-shrink:0">${num}</div>
                    <div>
                      <div style="font-weight:600;margin-bottom:var(--space-1)">${title}</div>
                      <div style="font-size:var(--font-size-sm);color:var(--text-secondary)">${desc}</div>
                    </div>
                  </div>
                `).join("")}
              </div>
            </div>
            <div>
              <div style="display:flex;align-items:center;justify-content:space-between;
                          margin-bottom:var(--space-4)">
                <h2 style="font-size:var(--font-size-xl);font-weight:600">Live Feed</h2>
                <span class="feed-item__indicator feed-item__indicator--MODERATE"
                      style="animation:pulse 1s infinite"></span>
              </div>
              <div id="home-feed" style="border:1px solid var(--border-color);
                                         border-radius:var(--radius-lg);
                                         overflow:hidden;background:var(--bg-card)">
                <div style="padding:40px;text-align:center;color:var(--text-muted);
                             font-size:var(--font-size-sm)">
                  Connecting to live feed...
                </div>
              </div>
              <div style="margin-top:var(--space-3);text-align:center">
                <a href="#/live-feed" data-route="/live-feed"
                   onclick="Router.navigate('/live-feed');return false;"
                   style="font-size:var(--font-size-sm);color:var(--accent-primary)">
                  View all intelligence
                </a>
              </div>
            </div>
          </div>
        </div>
      </section>
    `;

    document.getElementById("home-search-btn").addEventListener("click", () => {
      const q = document.getElementById("home-search-input").value.trim();
      if (q) Router.navigate(`/search?q=${encodeURIComponent(q)}`);
    });

    document.getElementById("home-search-input").addEventListener("keydown", (e) => {
      if (e.key === "Enter") {
        const q = e.target.value.trim();
        if (q) Router.navigate(`/search?q=${encodeURIComponent(q)}`);
      }
    });

    Api.stats().then(data => {
      const grid = document.getElementById("stats-grid");
      if (!grid) return;
      const nodes = data.nodes || {};
      const stats = [
        [Object.values(nodes).reduce((a,b)=>a+b,0).toLocaleString("en-IN"), "Total Entities"],
        [(nodes.Politician || 0).toLocaleString("en-IN"), "Politicians Tracked"],
        [(nodes.Company || 0).toLocaleString("en-IN"), "Companies Mapped"],
        [(nodes.Contract || 0).toLocaleString("en-IN"), "Contracts Indexed"],
      ];
      grid.innerHTML = stats
        .map(([v,l]) => `
          <div class="stat-card">
            <div class="stat-card__value">${v || "—"}</div>
            <div class="stat-card__label">${l}</div>
          </div>
        `).join("");
    }).catch(() => {
      const grid = document.getElementById("stats-grid");
      if (grid) grid.innerHTML = `
        <div style="grid-column:1/-1;text-align:center;color:var(--text-muted);
                    font-size:var(--font-size-sm);padding:var(--space-8)">
          API unavailable. Start the backend: uvicorn api.main:app --reload
        </div>
      `;
    });

    Views._connectFeedToHome();
  },

  _connectFeedToHome: () => {
    try {
      const ws = Api.createFeedSocket();
      ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        const container = document.getElementById("home-feed");
        if (!container) { ws.close(); return; }
        container.innerHTML = "";
        const item = Components.FeedItem({
          headline: data.message || "New intelligence available",
          risk_level: "MODERATE",
          detected_at: data.at,
          source: "BharatGraph Feed",
        });
        container.appendChild(item);
      };
      ws.onerror = () => {};
    } catch (_) {}
  },

  search: () => {
    const params = new URLSearchParams(window.location.hash.split("?")[1] || "");
    const query  = params.get("q") || "";
    const type   = params.get("type") || "";
    const main   = document.getElementById("app-main");

    main.innerHTML = `
      <div style="padding:var(--space-8) 0">
        <div class="container">
          <div class="search-bar" style="max-width:700px;margin-bottom:var(--space-6)">
            <input class="search-bar__input" id="search-input"
                   placeholder="Search entities..." id="search-input-field"
                   autocomplete="off">
            <button class="search-bar__btn" id="search-btn">Search</button>
          </div>

          <div style="display:flex;align-items:center;gap:var(--space-3);
                      margin-bottom:var(--space-3);flex-wrap:wrap">
            <select id="lang-select" style="font-size:var(--font-size-xs);padding:4px 8px;
                    background:var(--bg-secondary);color:var(--text-primary);
                    border:1px solid var(--border-color);border-radius:6px;cursor:pointer"
                    onchange="State.language=this.value;applyLanguage(this.value)">
              <option value="en">🇮🇳 English</option>
              <option value="hi">हिन्दी</option>
              <option value="ta">தமிழ்</option>
              <option value="te">తెలుగు</option>
              <option value="kn">ಕನ್ನಡ</option>
              <option value="ml">മലയാളം</option>
              <option value="mr">मराठी</option>
              <option value="bn">বাংলা</option>
              <option value="gu">ગુજરાતી</option>
              <option value="pa">ਪੰਜਾਬੀ</option>
              <option value="or">ଓଡ଼ିଆ</option>
              <option value="as">অসমীয়া</option>
              <option value="ur">اردو</option>
              <option value="kok">कोंकणी</option>
              <option value="mai">मैथिली</option>
              <option value="mni">ꯃꯩꯇꯩꯂꯣꯟ</option>
              <option value="sat">ᱥᱟᱱᱛᱟᱲᱤ</option>
              <option value="ks">كٲشُر</option>
              <option value="ne">नेपाली</option>
              <option value="doi">डोगरी</option>
              <option value="sa">संस्कृतम्</option>
              <option value="sd">سنڌي</option>
            </select>
          </div>

          <div style="display:flex;align-items:center;gap:var(--space-2);
                      margin-bottom:var(--space-6);flex-wrap:wrap">
            <span style="font-size:var(--font-size-sm);color:var(--text-muted)">Filter:</span>
            ${["All","politician","company","audit","contract","ministry","tender","electoralbond","regulatory","enforcement","insolvency","ngo"].map(t => `
              <button class="btn btn--sm ${type === t || (!type && t==="All") ? "btn--primary" : "btn--secondary"}"
                      onclick="Router.navigate('/search?q=${encodeURIComponent(query)}${t!=="All"?"&type="+t.toLowerCase():""}')">
                ${t.charAt(0).toUpperCase()+t.slice(1)}
              </button>
            `).join("")}
          </div>

          <div id="search-results">
            ${query ? Components.SkeletonGroup(5).outerHTML || "" : ""}
          </div>
        </div>
      </div>
    `;

    document.getElementById("search-btn").addEventListener("click", () => {
      const q = document.getElementById("search-input").value.trim();
      if (q) Router.navigate(`/search?q=${encodeURIComponent(q)}`);
    });
    document.getElementById("search-input").addEventListener("keydown", (e) => {
      if (e.key === "Enter") {
        const q = e.target.value.trim();
        if (q) Router.navigate(`/search?q=${encodeURIComponent(q)}`);
      }
    });

    if (!query) {
      document.getElementById("search-results").innerHTML = `
        <div style="text-align:center;padding:var(--space-16);color:var(--text-muted)">
          Enter a name to begin searching
        </div>
      `;
      return;
    }

    const skeletons = document.createElement("div");
    skeletons.appendChild(Components.SkeletonGroup(5));
    document.getElementById("search-results").innerHTML = "";
    document.getElementById("search-results").appendChild(skeletons);

    const lang = (typeof State !== 'undefined' && State.language) ? State.language : 'en';
    const searchPromise = (lang && lang !== 'en')
      ? Api.multilingualSearch(query, lang)
      : Api.search(query, type ? type.toLowerCase() : null, 20, lang);
    searchPromise.then(rawData => {
      // Normalise shape: multilingual returns {id, type} while main search
      // returns {entity_id, entity_type}. Unify before rendering.
      const data = {
        ...rawData,
        total: rawData.total || (rawData.results || []).length,
        query: rawData.query || query,
        results: (rawData.results || []).map(r => ({
          entity_id:   r.entity_id   || r.id   || "",
          entity_type: r.entity_type || r.type  || "Unknown",
          name:        r.name        || r.title || r.entity_id || r.id || "",
          state:       r.state       || null,
          party:       r.party       || null,
          source:      r.source      || r.dataset || null,
          sources:     r.sources     || [],
        })),
      };
      const container = document.getElementById("search-results");
      if (!container) return;
      container.innerHTML = "";

      if (!data.results || data.results.length === 0) {
        container.innerHTML = `
          <div style="text-align:center;padding:var(--space-16);color:var(--text-muted)">
            No results found for "${query}"
          </div>
        `;
        return;
      }

      const header = document.createElement("div");
      header.style.cssText = "margin-bottom:var(--space-4);font-size:var(--font-size-sm);color:var(--text-muted)";
      header.textContent = `${data.total} result${data.total !== 1 ? "s" : ""} for "${data.query}"`;
      container.appendChild(header);

      const list = document.createElement("div");
      list.style.cssText = "display:flex;flex-direction:column;gap:var(--space-3)";
      data.results.forEach(entity => {
        list.appendChild(Components.ResultCard(entity, (e) => {
          Router.navigate(`/entity/${e.entity_id}`);
        }));
      });
      container.appendChild(list);
    }).catch(err => {
      const container = document.getElementById("search-results");
      if (container) container.innerHTML = `
        <div style="text-align:center;padding:var(--space-8);color:var(--color-risk-very-high)">
          Search failed. The API may be starting up — please retry in a moment.
        </div>
      `;
    });
  },

  entity: ({ id }) => {
    const main = document.getElementById("app-main");
    main.innerHTML = `
      <div style="padding:var(--space-8) 0">
        <div class="container">
          <div id="entity-content">
            <div style="display:flex;flex-direction:column;gap:var(--space-4)">
              ${[120,80,400,300].map(h =>
                `<div class="skeleton" style="height:${h}px;border-radius:12px"></div>`
              ).join("")}
            </div>
          </div>
        </div>
      </div>
    `;

    Promise.all([
      Api.profile(id).catch(() => null),
      Api.risk(id).catch(() => null),
      Api.graphConnections(id, 2).catch(() => null),
    ]).then(([profile, risk, graph]) => {
      const container = document.getElementById("entity-content");
      if (!container) return;

      if (!profile && !risk) {
        container.innerHTML = `
          <div style="text-align:center;padding:var(--space-16);color:var(--text-muted)">
            Entity not found: ${id}
          </div>
        `;
        return;
      }

      const name  = profile?.name || risk?.entity_name || id;
      const type  = profile?.entity_type || "Unknown";
      const score = risk?.risk_score ?? 0;
      const level = risk?.risk_level || "UNKNOWN";

      container.innerHTML = `
        <div style="margin-bottom:var(--space-6)">
          <a href="#/search" onclick="history.back();return false;"
             style="font-size:var(--font-size-sm);color:var(--text-muted);
                    text-decoration:none">
            &larr; Back to results
          </a>
        </div>

        <div style="display:grid;grid-template-columns:1fr 320px;
                    gap:var(--space-6);align-items:start">
          <div>
            <div style="margin-bottom:var(--space-6)">
              <div style="display:flex;align-items:center;gap:var(--space-3);
                          margin-bottom:var(--space-2)">
                <span class="badge badge--${type.toLowerCase()}">${type}</span>
              </div>
              <h1 style="font-size:var(--font-size-3xl);font-weight:700;
                         color:var(--text-primary);margin-bottom:var(--space-2)">${name}</h1>
              ${profile?.overview
                ? Object.entries(profile.overview)
                    .filter(([,v]) => v)
                    .map(([k,v]) => `
                      <span style="font-size:var(--font-size-sm);
                                   color:var(--text-secondary);
                                   margin-right:var(--space-4)">
                        <strong>${k}:</strong> ${v}
                      </span>
                    `).join("")
                : ""}
            </div>

            <div id="dossier-tabs" style="margin-bottom:var(--space-4)">
              <div class="tab-bar">
                <button class="tab-bar__tab active" data-tab="findings">Findings</button>
                <button class="tab-bar__tab" data-tab="graph">Relationship Graph</button>
                <button class="tab-bar__tab" data-tab="evidence">Evidence Locker</button>
              </div>
            </div>

            <div id="tab-content-findings">
              <h3 style="font-size:var(--font-size-base);font-weight:600;
                         margin-bottom:var(--space-4)">Analytical Findings</h3>
              <div id="findings-list">
                ${risk?.factors?.filter(f => f.score > 0).map(f =>
                  `<div class="finding-item finding-item--${f.score > 20 ? "HIGH" : "MODERATE"}">
                    <div class="finding-item__severity">${f.name.replace(/_/g," ")}</div>
                    <div class="finding-item__desc">${f.description}</div>
                  </div>`
                ).join("") || `<p style="color:var(--text-muted)">No findings in current dataset.</p>`}
              </div>
            </div>

            <div id="tab-content-graph" style="display:none">
              <div class="graph-container" id="entity-graph">
                <div class="graph-controls">
                  <button class="btn btn--sm btn--secondary" onclick="document.getElementById('entity-graph').querySelector('svg') && window.d3.select('#entity-graph svg').call(window.d3.zoom().transform, window.d3.zoomIdentity)">Reset</button>
                </div>
                <div class="graph-legend" id="graph-legend"></div>
              </div>
            </div>

            <div id="tab-content-evidence" style="display:none">
              ${risk?.sources?.map(s => `
                <div class="evidence-item" style="padding:var(--space-3) var(--space-4);
                     margin-bottom:var(--space-2);background:var(--bg-secondary);
                     border:1px solid var(--border-color);border-radius:var(--radius-md)">
                  <div style="font-size:var(--font-size-sm);font-weight:600">${s.institution}</div>
                  <div style="font-size:var(--font-size-xs);color:var(--text-muted)">
                    ${s.document_title}
                    ${s.url ? `| <a href="${s.url}" target="_blank">${s.url}</a>` : ""}
                  </div>
                </div>
              `).join("") || `<p style="color:var(--text-muted)">No evidence sources in current dataset.</p>`}
            </div>
          </div>

          <div style="display:flex;flex-direction:column;gap:var(--space-4)">
            <div class="card">
              <div class="card__header">
                <div class="card__title">Structural Risk Indicator</div>
              </div>
              <div class="card__body">
                <div id="risk-bar-container" style="margin-bottom:var(--space-4)"></div>
                <div id="risk-badge-container" style="margin-bottom:var(--space-4)"></div>
                <p style="font-size:var(--font-size-xs);color:var(--text-muted);
                          line-height:var(--line-height-relaxed)">
                  ${risk?.explanation || "Risk explanation unavailable."}
                </p>
              </div>
            </div>

            <div class="card">
              <div class="card__body">
                <a href="${Api.exportPdf(id)}" target="_blank"
                   class="btn btn--secondary" style="width:100%;justify-content:center">
                  Download PDF Dossier
                </a>
              </div>
            </div>
          </div>
        </div>
      `;

      const barContainer = document.getElementById("risk-bar-container");
      if (barContainer) barContainer.appendChild(Components.RiskBar(score, level));
      const badgeContainer = document.getElementById("risk-badge-container");
      if (badgeContainer) badgeContainer.appendChild(Components.RiskBadge(level));

      document.querySelectorAll(".tab-bar__tab").forEach(tab => {
        tab.addEventListener("click", () => {
          document.querySelectorAll(".tab-bar__tab").forEach(t => t.classList.remove("active"));
          tab.classList.add("active");
          const tabId = tab.dataset.tab;
          ["findings","graph","evidence"].forEach(t => {
            const el = document.getElementById(`tab-content-${t}`);
            if (el) el.style.display = t === tabId ? "block" : "none";
          });
          if (tabId === "graph" && graph) {
            GraphRenderer.init("entity-graph", graph);
            GraphRenderer.renderLegend("graph-legend");
          }
        });
      });
    });
  },

  liveFeed: () => {
    const main = document.getElementById("app-main");
    main.innerHTML = `
      <div style="padding:var(--space-8) 0">
        <div class="container">
          <div style="display:flex;align-items:center;gap:var(--space-4);
                      margin-bottom:var(--space-6)">
            <h1 class="section-title" style="margin-bottom:0">Live Intelligence Feed</h1>
            <div style="display:flex;align-items:center;gap:var(--space-2);
                        font-size:var(--font-size-xs);color:var(--text-muted)">
              <span class="feed-item__indicator feed-item__indicator--MODERATE"
                    style="animation:pulse 1s infinite"></span>
              <span id="feed-status">Connecting...</span>
            </div>
          </div>
          <p class="section-subtitle">
            Real-time analytical intelligence derived from CAG audit reports,
            government procurement data, and official regulatory filings.
          </p>
          <div id="feed-container" class="card">
            <div style="padding:60px;text-align:center;color:var(--text-muted)">
              Connecting to feed...
            </div>
          </div>
        </div>
      </div>
    `;

    const feedItems = [];
    try {
      const ws = Api.createFeedSocket();
      ws.onopen = () => {
        const status = document.getElementById("feed-status");
        if (status) status.textContent = "Connected";
      };
      ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        feedItems.unshift({
          headline: data.message || "Feed update received",
          risk_level: "MODERATE",
          detected_at: data.at || new Date().toISOString(),
          source: "BharatGraph API",
        });
        if (feedItems.length > 50) feedItems.pop();
        const container = document.getElementById("feed-container");
        if (!container) { ws.close(); return; }
        container.innerHTML = "";
        feedItems.forEach(item => container.appendChild(Components.FeedItem(item)));
      };
      ws.onerror = () => {
        const status = document.getElementById("feed-status");
        if (status) status.textContent = "API not reachable";
      };
      ws.onclose = () => {
        const status = document.getElementById("feed-status");
        if (status) status.textContent = "Disconnected";
      };
    } catch (_) {
      const status = document.getElementById("feed-status");
      if (status) status.textContent = "WebSocket unavailable";
    }
  },


  "connection-map": (params) => {
    const urlParams = new URLSearchParams(window.location.hash.split("?")[1] || "");
    const entityId  = urlParams.get("entity") || "";
    const entityName = urlParams.get("name") || entityId;
    const main = document.getElementById("app-main");
    main.innerHTML = `
      <div style="padding:var(--space-8) 0">
        <div class="container">
          <h2 style="font-size:var(--font-size-xl);font-weight:700;color:var(--text-primary);margin-bottom:4px">
            Connection Map
          </h2>
          <p style="font-size:var(--font-size-sm);color:var(--text-secondary);margin-bottom:var(--space-6)">
            Evidence-based relationship map for: <strong>${sanitize(entityName)}</strong>
          </p>

          <div style="display:grid;grid-template-columns:1fr 340px;gap:var(--space-6)">
            <!-- Graph area -->
            <div style="background:var(--bg-secondary);border-radius:12px;
                        border:1px solid var(--border-color);min-height:500px;
                        display:flex;flex-direction:column">
              <div style="padding:12px 16px;border-bottom:1px solid var(--border-color);
                          display:flex;align-items:center;justify-content:space-between">
                <span style="font-size:12px;font-weight:600;color:var(--text-secondary)">
                  Relationship Graph
                </span>
                <div style="display:flex;gap:6px">
                  <span style="font-size:10px;color:var(--text-muted)">
                    ● Strong  ◐ Medium  ○ Weak
                  </span>
                </div>
              </div>
              <div id="conn-graph" style="flex:1;min-height:440px;position:relative">
                <div class="spinner" style="position:absolute;top:50%;left:50%;transform:translate(-50%,-50%)"></div>
              </div>
            </div>

            <!-- Evidence list -->
            <div>
              <div style="font-size:11px;font-weight:700;text-transform:uppercase;
                          letter-spacing:.08em;color:var(--text-muted);margin-bottom:10px">
                Evidence Chain
              </div>
              <div id="conn-evidence-list">
                <div class="spinner" style="margin:20px auto"></div>
              </div>

              <div style="margin-top:16px">
                <div style="font-size:11px;font-weight:700;text-transform:uppercase;
                            letter-spacing:.08em;color:var(--text-muted);margin-bottom:10px">
                  Path Finder
                </div>
                <div style="display:flex;flex-direction:column;gap:8px">
                  <input id="path-target" class="search-bar__input"
                         placeholder="Target entity ID..."
                         style="font-size:12px;padding:8px 12px">
                  <button onclick="Views._findPath('${encodeURIComponent(entityId)}')"
                          class="btn btn--secondary" style="font-size:12px">Find Shortest Path</button>
                </div>
                <div id="path-result" style="margin-top:10px"></div>
              </div>
            </div>
          </div>
        </div>
      </div>
    `;

    if (!entityId) return;

    // Load evidence
    Api.nodeEvidence(entityId).then(data => {
      const edges = data.edges || [];
      const listEl = document.getElementById("conn-evidence-list");
      if (!listEl) return;

      listEl.innerHTML = edges.length ? edges.map(e => `
        <div style="padding:10px 12px;margin-bottom:6px;background:var(--bg-secondary);
                    border-radius:8px;border:1px solid var(--border-color);cursor:pointer"
             onclick="EvidencePanel.open('${sanitize(e.connected_id||'')}','${sanitize(e.connected_to||'')}')">
          <div style="font-size:10px;font-weight:700;text-transform:uppercase;
                      color:var(--color-saffron);margin-bottom:2px">${sanitize(e.rel_label||"")}</div>
          <div style="font-size:12px;font-weight:600;color:var(--text-primary)">
            ${sanitize(e.connected_to||e.connected_id||"—")}
          </div>
          <div style="font-size:10px;color:var(--text-secondary);margin-top:2px">
            ${sanitize(e.why||"")}
          </div>
          <div style="font-size:10px;color:var(--text-muted);margin-top:2px">
            📄 ${sanitize(e.source||"")}
          </div>
        </div>`).join("") : `<div style="text-align:center;padding:20px;color:var(--text-muted);font-size:12px">
          No connections in current dataset</div>`;

      // Render D3 graph
      Views._renderConnectionGraph(entityId, entityName, edges);
    }).catch(() => {
      const el = document.getElementById("conn-graph");
      if (el) el.innerHTML = `<div style="text-align:center;padding:60px;color:var(--text-muted)">
        Could not load graph data</div>`;
    });
  },

  _findPath: (entityA) => {
    const b = document.getElementById("path-target").value.trim();
    const res = document.getElementById("path-result");
    if (!b || !res) return;
    res.innerHTML = `<div class="spinner" style="margin:10px auto"></div>`;
    Api._request(`/connection-map?a=${encodeURIComponent(entityA)}&b=${encodeURIComponent(b)}`)
      .then(data => {
        const path = data.path || data.paths || [];
        res.innerHTML = path.length ? `
          <div style="padding:10px;background:var(--bg-secondary);border-radius:8px;
                      border:1px solid var(--border-color);font-size:12px">
            <div style="font-weight:600;color:var(--color-saffron);margin-bottom:6px">
              ${path.length} hop path found
            </div>
            ${(Array.isArray(path[0]) ? path[0] : path).map(n =>
              `<span style="color:var(--text-primary)">${sanitize(n)}</span>
               <span style="color:var(--text-muted);margin:0 4px">→</span>`
            ).join("").replace(/<span[^>]*>→<\/span>$/, "")}
          </div>` : `
          <div style="color:var(--text-muted);font-size:12px">No path found</div>`;
      }).catch(() => {
        res.innerHTML = `<div style="color:var(--text-muted);font-size:12px">Path search unavailable</div>`;
      });
  },

  _renderConnectionGraph: (centerId, centerName, edges) => {
    const container = document.getElementById("conn-graph");
    if (!container || !window.d3) {
      if (container) container.innerHTML = `
        <div style="text-align:center;padding:60px;color:var(--text-muted);font-size:12px">
          Graph visualization requires D3.js</div>`;
      return;
    }

    const w = container.clientWidth || 600, h = container.clientHeight || 440;
    container.innerHTML = "";

    const nodes = [{id: centerId, name: centerName, group: "center"}];
    const links = [];
    const seen = new Set([centerId]);
    edges.slice(0, 20).forEach(e => {
      const tid = e.connected_id || e.connected_to || Math.random().toString();
      if (!seen.has(tid)) { seen.add(tid); nodes.push({id:tid, name:e.connected_to||tid, group:e.rel_label||"OTHER"}); }
      links.push({source:centerId, target:tid, label:e.rel_label||"", strength:e.strength||"medium"});
    });

    const svg = d3.select(container).append("svg").attr("width","100%").attr("height","100%")
      .attr("viewBox",`0 0 ${w} ${h}`);
    const sim = d3.forceSimulation(nodes)
      .force("link",d3.forceLink(links).id(d=>d.id).distance(120))
      .force("charge",d3.forceManyBody().strength(-300))
      .force("center",d3.forceCenter(w/2,h/2));

    const link = svg.append("g").selectAll("line").data(links).join("line")
      .attr("stroke","#555").attr("stroke-width",1.5).attr("stroke-opacity",0.6);

    const node = svg.append("g").selectAll("circle").data(nodes).join("circle")
      .attr("r", d => d.group==="center"?16:10)
      .attr("fill", d => d.group==="center"?"var(--color-saffron)":"var(--accent-primary)")
      .attr("stroke","var(--bg-primary)").attr("stroke-width",2)
      .style("cursor","pointer")
      .on("click", (e,d) => { if(d.id!==centerId) EvidencePanel.open(d.id, d.name); });

    const label = svg.append("g").selectAll("text").data(nodes).join("text")
      .text(d => (d.name||d.id).slice(0,18))
      .attr("font-size","10px").attr("fill","var(--text-primary)")
      .attr("text-anchor","middle").attr("dy","26px");

    sim.on("tick", () => {
      link.attr("x1",d=>d.source.x).attr("y1",d=>d.source.y)
          .attr("x2",d=>d.target.x).attr("y2",d=>d.target.y);
      node.attr("cx",d=>d.x).attr("cy",d=>d.y);
      label.attr("x",d=>d.x).attr("y",d=>d.y);
    });
  },

  about: () => {
    const main = document.getElementById("app-main");
    main.innerHTML = `
      <div style="padding:var(--space-12) 0">
        <div class="container container--narrow">
          <h1 class="section-title">About BharatGraph</h1>
          <p class="section-subtitle">
            A public transparency platform built on official government data.
          </p>

          <div style="display:flex;flex-direction:column;gap:var(--space-6)">
            ${[
              ["Legal Notice",
               "BharatGraph processes only publicly available government records published by the Election Commission of India, Ministry of Corporate Affairs, Government e-Marketplace, Comptroller and Auditor General, Press Information Bureau, and Parliament of India. All outputs are statistical observations derived from official sources. No claim made by this platform constitutes a legal finding or an accusation of wrongdoing."],
              ["Right to Correction",
               "Any individual or organisation featured in this platform has the right to submit corrections. Contact us through the GitHub repository issue tracker with documentary evidence. Verified corrections will be incorporated within 14 days."],
              ["Data Sources",
               "21 official Indian government data sources plus international datasets from OpenSanctions (sanctions and PEP screening), ICIJ Offshore Leaks (Panama, Pandora, Paradise Papers), and Wikidata (entity enrichment)."],
              ["Methodology",
               "The BharatGraph Multi-Investigator Engine runs 12 specialist AI investigators in parallel. Each queries the knowledge graph independently. Findings confirmed by three or more investigators are marked as high-confidence. All language output is validated against a forbidden-words list that prohibits accusatory terminology."],
            ].map(([title, body]) => `
              <div class="card">
                <div class="card__header"><div class="card__title">${title}</div></div>
                <div class="card__body">
                  <p style="font-size:var(--font-size-sm);color:var(--text-secondary);
                             line-height:var(--line-height-relaxed)">${body}</p>
                </div>
              </div>
            `).join("")}
          </div>
        </div>
      </div>
    `;
  },
};

function toggleTheme() {
  State.theme = State.theme === "dark" ? "light" : "dark";
  document.documentElement.setAttribute("data-theme", State.theme);
  localStorage.setItem("bg-theme", State.theme);
  const btn = document.getElementById("theme-btn");
  if (btn) btn.textContent = State.theme === "dark" ? "Light" : "Dark";
}


// ── Language Application ──────────────────────────────────────────────────────
// BUG-10 FIX: full DOM translation via data-i18n attributes
async function applyLanguage(lang) {
  const badge = document.getElementById("lang-badge");
  if (!lang || lang === "en") {
    document.querySelectorAll("[data-i18n]").forEach(el => {
      const def = el.getAttribute("data-i18n-default");
      if (!def) return;
      if (el.hasAttribute("placeholder")) el.placeholder = def;
      else el.textContent = def;
    });
    if (badge) badge.textContent = "EN";
    State.uiLabels = {};
    return;
  }
  try {
    const data   = await Api.uiLabels(lang);
    const labels = data.labels || {};
    // Apply every translated label to every matching data-i18n DOM element.
    // Auto-scales: new keys in languages.py are applied automatically.
    document.querySelectorAll("[data-i18n]").forEach(el => {
      const value = labels[el.getAttribute("data-i18n")];
      if (!value) return;
      if (el.hasAttribute("placeholder")) el.placeholder = value;
      else el.textContent = value;
    });
    // Also update dynamic search input (rendered after page load)
    const ph = document.querySelector(".search-bar__input, #search-input");
    if (ph && labels.search_placeholder) ph.placeholder = labels.search_placeholder;
    if (badge) { badge.textContent = lang.toUpperCase(); badge.title = data.native_name || lang; }
    State.uiLabels   = labels;
    State.langName   = data.language_name || lang;
    State.nativeName = data.native_name   || lang;
  } catch (e) {
    console.warn("[i18n] Could not load UI labels for", lang, e.message);
  }
}
window.applyLanguage = applyLanguage;

function initApp() {
  document.documentElement.setAttribute("data-theme", State.theme);

  Router.register("/",         Views.home);
  Router.register("/search",   Views.search);
  Router.register("/entity/:id", Views.entity);
  Router.register("/connection-map", Views["connection-map"]);
  Router.register("/live-feed", Views.liveFeed);
  Router.register("/about",    Views.about);

  Api.health().then(() => {
    State.apiConnected = true;
  }).catch(() => {
    Components.Toast("API not connected. Start: uvicorn api.main:app --reload", "error");
  });

  Router.init();

  // Apply language on load if not English
  if (State.language && State.language !== "en") {
    applyLanguage(State.language);
  }
}

window.addEventListener("DOMContentLoaded", initApp);
window.toggleTheme = toggleTheme;
