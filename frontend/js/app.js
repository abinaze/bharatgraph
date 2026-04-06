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
                   value="${query}" placeholder="Search entities..."
                   autocomplete="off">
            <button class="search-bar__btn" id="search-btn">Search</button>
          </div>

          <div style="display:flex;align-items:center;gap:var(--space-2);
                      margin-bottom:var(--space-6);flex-wrap:wrap">
            <span style="font-size:var(--font-size-sm);color:var(--text-muted)">Filter:</span>
            ${["All","politician","company","audit"].map(t => `
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
    searchPromise.then(data => {
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
          Search failed. Ensure the API is running. (${err.message})
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

function initApp() {
  document.documentElement.setAttribute("data-theme", State.theme);

  Router.register("/",         Views.home);
  Router.register("/search",   Views.search);
  Router.register("/entity/:id", Views.entity);
  Router.register("/live-feed", Views.liveFeed);
  Router.register("/about",    Views.about);

  Api.health().then(() => {
    State.apiConnected = true;
  }).catch(() => {
    Components.Toast("API not connected. Start: uvicorn api.main:app --reload", "error");
  });

  Router.init();
}

window.addEventListener("DOMContentLoaded", initApp);
window.toggleTheme = toggleTheme;
