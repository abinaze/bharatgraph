// Evidence Panel — tabbed deep investigation panel
// Tabs: Overview | Connections | Provenance | Timeline | Investigate
const EvidencePanel = {
  _visible: false,
  _container: null,
  _currentId: null,
  _currentName: null,

  init: () => {
    const panel = document.createElement("div");
    panel.id = "evidence-panel";
    panel.style.cssText = `
      position:fixed;top:0;right:-480px;width:460px;height:100vh;
      background:var(--bg-secondary);border-left:1px solid var(--border-color);
      box-shadow:-4px 0 32px rgba(0,0,0,0.4);z-index:500;
      display:flex;flex-direction:column;transition:right 0.3s cubic-bezier(.4,0,.2,1);
    `;
    document.body.appendChild(panel);
    EvidencePanel._container = panel;

    const overlay = document.createElement("div");
    overlay.id = "evidence-overlay";
    overlay.style.cssText = `position:fixed;inset:0;background:rgba(0,0,0,0.45);z-index:499;display:none;`;
    overlay.addEventListener("click", EvidencePanel.close);
    document.body.appendChild(overlay);
  },

  open: async (entityId, entityName) => {
    if (!EvidencePanel._container) EvidencePanel.init();
    EvidencePanel._currentId   = entityId;
    EvidencePanel._currentName = entityName;

    EvidencePanel._container.innerHTML = `
      <div style="padding:16px 20px;border-bottom:1px solid var(--border-color);
                  display:flex;justify-content:space-between;align-items:center;
                  background:var(--bg-tertiary);flex-shrink:0">
        <div>
          <div style="font-size:10px;font-weight:700;letter-spacing:.12em;
                      text-transform:uppercase;color:var(--color-saffron)">Evidence Panel</div>
          <div style="font-size:15px;font-weight:700;color:var(--text-primary);margin-top:2px">
            ${sanitize(entityName || entityId)}
          </div>
          <div style="font-size:10px;color:var(--text-muted)">ID: ${sanitize(entityId)}</div>
        </div>
        <button onclick="EvidencePanel.close()"
                style="background:var(--bg-secondary);border:1px solid var(--border-color);
                       color:var(--text-muted);width:32px;height:32px;border-radius:50%;
                       cursor:pointer;font-size:18px;display:flex;align-items:center;
                       justify-content:center">×</button>
      </div>

      <!-- Tab bar -->
      <div style="display:flex;border-bottom:1px solid var(--border-color);
                  background:var(--bg-tertiary);flex-shrink:0">
        ${["overview","connections","timeline","investigate"].map((t,i) => `
          <button id="ep-tab-${t}"
                  onclick="EvidencePanel._switchTab('${t}')"
                  style="flex:1;padding:10px 4px;font-size:10px;font-weight:600;
                         text-transform:uppercase;letter-spacing:.07em;
                         border:none;cursor:pointer;transition:all .2s;
                         border-bottom:2px solid ${i===0?'var(--accent-primary)':'transparent'};
                         background:transparent;
                         color:${i===0?'var(--accent-primary)':'var(--text-muted)'}">
            ${t.charAt(0).toUpperCase()+t.slice(1)}
          </button>
        `).join("")}
      </div>

      <!-- Tab content area -->
      <div id="ep-body" style="flex:1;overflow-y:auto;padding:16px 20px">
        <div class="spinner" style="margin:60px auto"></div>
      </div>

      <!-- Bottom action bar -->
      <div style="padding:12px 20px;border-top:1px solid var(--border-color);
                  background:var(--bg-tertiary);flex-shrink:0;display:flex;gap:8px">
        <button onclick="Router.navigate('/entity/${entityId}');EvidencePanel.close();"
                class="btn btn--primary" style="flex:1;font-size:12px">Full Dossier</button>
        <button onclick="EvidencePanel._investigate('${entityId}')"
                id="ep-investigate-btn"
                class="btn btn--secondary" style="flex:1;font-size:12px">Investigate (6 Layers)</button>
        <button onclick="EvidencePanel._openConnectionMap('${entityId}','${sanitize(entityName||entityId)}')"
                class="btn btn--secondary" style="flex:1;font-size:12px">Map Links</button>
      </div>
    `;

    EvidencePanel._container.style.right = "0";
    document.getElementById("evidence-overlay").style.display = "block";
    EvidencePanel._visible = true;

    // Load overview tab by default
    try {
      const data = await Api.nodeEvidence(entityId);
      EvidencePanel._data = data;
      EvidencePanel._renderOverview(data, entityId);
    } catch (err) {
      document.getElementById("ep-body").innerHTML = `
        <div style="text-align:center;padding:40px 20px;color:var(--text-muted)">
          <div style="font-size:32px;margin-bottom:12px">⚠️</div>
          <div style="font-weight:600;margin-bottom:4px">Evidence unavailable</div>
          <div style="font-size:12px">API may be offline or entity not in database.</div>
        </div>`;
    }
  },

  _switchTab: (tab) => {
    ["overview","connections","timeline","investigate"].forEach(t => {
      const btn = document.getElementById(`ep-tab-${t}`);
      if (btn) {
        btn.style.borderBottom = t===tab ? "2px solid var(--accent-primary)" : "2px solid transparent";
        btn.style.color        = t===tab ? "var(--accent-primary)" : "var(--text-muted)";
      }
    });
    const d = EvidencePanel._data;
    const id = EvidencePanel._currentId;
    if      (tab==="overview")     d ? EvidencePanel._renderOverview(d,id)    : null;
    else if (tab==="connections")  d ? EvidencePanel._renderConnections(d,id) : null;
    else if (tab==="timeline")     EvidencePanel._renderTimeline(id);
    else if (tab==="investigate")  EvidencePanel._renderInvestigateTab(id);
  },

  _renderOverview: (data, entityId) => {
    const info = data.entity_info || {};
    const edges = data.edges || [];
    const rc = {"LOW":"var(--color-risk-low)","MODERATE":"#d4a017",
                "HIGH":"var(--color-risk-high)","VERY_HIGH":"var(--color-risk-very-high)"}[info.risk_level] || "var(--text-muted)";
    const el = document.getElementById("ep-body");
    if (!el) return;

    el.innerHTML = `
      ${info.risk_score != null ? `
      <div style="padding:14px;background:var(--bg-tertiary);border-radius:10px;margin-bottom:16px;
                  border:1px solid var(--border-color)">
        <div style="font-size:10px;text-transform:uppercase;letter-spacing:.08em;
                    color:var(--text-muted);margin-bottom:8px">Structural Risk Indicator</div>
        <div style="display:flex;align-items:center;gap:10px;margin-bottom:6px">
          <div style="flex:1;height:8px;background:var(--bg-primary);border-radius:4px;overflow:hidden">
            <div style="width:${info.risk_score}%;height:100%;background:${rc};border-radius:4px;
                        transition:width 1s ease"></div>
          </div>
          <span style="font-weight:800;font-size:15px;color:${rc}">${info.risk_score}/100</span>
        </div>
        <div style="font-size:11px;font-weight:600;color:${rc}">${info.risk_level || "UNKNOWN"}</div>
        ${info.risk_factors && info.risk_factors.length ? `
        <div style="margin-top:8px;display:flex;flex-wrap:wrap;gap:4px">
          ${info.risk_factors.slice(0,4).map(f => `
            <span style="font-size:10px;padding:2px 8px;border-radius:12px;
                         background:rgba(255,255,255,0.05);color:var(--text-secondary)">
              ${sanitize(f)}
            </span>`).join("")}
        </div>` : ""}
      </div>` : ""}

      <!-- Summary stats -->
      <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:8px;margin-bottom:16px">
        ${[
          ["Connections", edges.length],
          ["Entity Type", info.entity_type || "—"],
          ["Source", info.source || "—"]
        ].map(([l,v]) => `
          <div style="padding:10px;background:var(--bg-tertiary);border-radius:8px;
                      border:1px solid var(--border-color);text-align:center">
            <div style="font-size:14px;font-weight:700;color:var(--text-primary)">${sanitize(String(v))}</div>
            <div style="font-size:10px;color:var(--text-muted);margin-top:2px">${l}</div>
          </div>`).join("")}
      </div>

      <!-- Top connections preview -->
      <div style="font-size:11px;font-weight:700;text-transform:uppercase;letter-spacing:.08em;
                  color:var(--text-muted);margin-bottom:10px">Key Connections</div>
      ${edges.length ? edges.slice(0,5).map(e => `
        <div style="padding:10px 12px;margin-bottom:8px;background:var(--bg-tertiary);
                    border-radius:8px;border-left:3px solid ${e.color||'var(--accent-primary)'}">
          <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:3px">
            <span style="font-size:10px;font-weight:700;text-transform:uppercase;
                         color:${e.color||'var(--accent-primary)'};">${sanitize(e.rel_label||"LINKED")}</span>
            <span style="font-size:10px;color:var(--text-muted)">
              ${e.strength==="strong"?"●●●":e.strength==="medium"?"●●○":"●○○"} ${sanitize(e.strength||"")}
            </span>
          </div>
          <div style="font-size:13px;font-weight:600;color:var(--text-primary)">
            ${sanitize(e.connected_to||e.connected_id||"—")}
          </div>
          <div style="font-size:11px;color:var(--text-secondary);margin-top:3px">
            ${sanitize(e.why||"")}
          </div>
          <div style="font-size:10px;color:var(--text-muted);margin-top:2px">
            📄 ${sanitize(e.source||"")}
          </div>
        </div>`).join("") : `
        <div style="text-align:center;padding:30px;color:var(--text-muted);font-size:12px">
          No connections indexed yet
        </div>`}

      ${edges.length > 5 ? `
      <button onclick="EvidencePanel._switchTab('connections')"
              class="btn btn--secondary" style="width:100%;font-size:12px;margin-top:4px">
        View all ${edges.length} connections →
      </button>` : ""}
    `;
  },

  _renderConnections: (data, entityId) => {
    const edges = data.edges || [];
    const el = document.getElementById("ep-body");
    if (!el) return;

    // Group by relationship type
    const groups = {};
    edges.forEach(e => {
      const k = e.rel_label || "OTHER";
      if (!groups[k]) groups[k] = [];
      groups[k].push(e);
    });

    el.innerHTML = `
      <div style="margin-bottom:12px;font-size:12px;color:var(--text-muted)">
        ${edges.length} total connections across ${Object.keys(groups).length} relationship types
      </div>
      ${Object.entries(groups).map(([rel, items]) => `
        <div style="margin-bottom:16px">
          <div style="font-size:10px;font-weight:700;text-transform:uppercase;letter-spacing:.08em;
                      color:var(--color-saffron);margin-bottom:8px;padding-bottom:4px;
                      border-bottom:1px solid var(--border-color)">
            ${sanitize(rel)} (${items.length})
          </div>
          ${items.map(e => `
            <div style="padding:10px 12px;margin-bottom:6px;background:var(--bg-tertiary);
                        border-radius:8px;cursor:pointer"
                 onclick="EvidencePanel.open('${sanitize(e.connected_id||"")}','${sanitize(e.connected_to||"")}')">
              <div style="display:flex;justify-content:space-between">
                <span style="font-size:13px;font-weight:600;color:var(--text-primary)">
                  ${sanitize(e.connected_to||e.connected_id||"—")}
                </span>
                <span style="font-size:10px;color:var(--text-muted)">→</span>
              </div>
              <div style="font-size:11px;color:var(--text-secondary);margin-top:2px">
                ${sanitize(e.why||"")}
              </div>
              <div style="display:flex;gap:8px;margin-top:4px">
                <span style="font-size:10px;color:var(--text-muted)">📄 ${sanitize(e.source||"")}</span>
                ${e.date ? `<span style="font-size:10px;color:var(--text-muted)">📅 ${sanitize(e.date)}</span>` : ""}
              </div>
              ${e.next_leads && e.next_leads.length ? `
              <div style="margin-top:6px">
                ${e.next_leads.map(l => `
                  <span style="font-size:10px;color:var(--color-saffron);margin-right:8px">→ ${sanitize(l)}</span>
                `).join("")}
              </div>` : ""}
            </div>`).join("")}
        </div>`).join("") || `
        <div style="text-align:center;padding:30px;color:var(--text-muted)">
          No connections found in current dataset
        </div>`}
    `;
  },

  _renderTimeline: async (entityId) => {
    const el = document.getElementById("ep-body");
    if (!el) return;
    el.innerHTML = `<div class="spinner" style="margin:60px auto"></div>`;
    try {
      const data = await Api._request(`/profile/${entityId}`);
      const events = (data.timeline || data.timeline_events || []).sort((a,b) => (a.date||"").localeCompare(b.date||""));
      if (!events.length) {
        el.innerHTML = `<div style="text-align:center;padding:40px;color:var(--text-muted);font-size:12px">
          No timeline events indexed for this entity</div>`;
        return;
      }
      el.innerHTML = `
        <div style="margin-bottom:12px;font-size:12px;color:var(--text-muted)">${events.length} events</div>
        <div style="position:relative;padding-left:20px;border-left:2px solid var(--border-color)">
          ${events.map(ev => `
            <div style="position:relative;margin-bottom:16px">
              <div style="position:absolute;left:-25px;top:4px;width:10px;height:10px;
                          border-radius:50%;background:var(--accent-primary)"></div>
              <div style="font-size:10px;color:var(--color-saffron);font-weight:600;margin-bottom:2px">
                ${sanitize(ev.date||"Unknown date")}
              </div>
              <div style="font-size:13px;font-weight:600;color:var(--text-primary)">
                ${sanitize(ev.title||ev.event||"")}
              </div>
              <div style="font-size:11px;color:var(--text-secondary);margin-top:3px">
                ${sanitize(ev.description||ev.summary||"")}
              </div>
              <div style="font-size:10px;color:var(--text-muted);margin-top:2px">
                📄 ${sanitize(ev.source||"")}
              </div>
            </div>`).join("")}
        </div>`;
    } catch {
      el.innerHTML = `<div style="text-align:center;padding:40px;color:var(--text-muted);font-size:12px">
        Timeline data unavailable</div>`;
    }
  },

  _renderInvestigateTab: async (entityId) => {
    const el = document.getElementById("ep-body");
    if (!el) return;
    el.innerHTML = `
      <div style="margin-bottom:16px">
        <div style="font-size:13px;font-weight:600;color:var(--text-primary);margin-bottom:8px">
          6-Layer Investigation Engine
        </div>
        <div style="font-size:12px;color:var(--text-secondary);margin-bottom:12px">
          Runs 6 specialist investigators in parallel: Direct Evidence → Relationship Mapping →
          Pattern Detection → Timeline Analysis → Network Influence → Evidence Validation
        </div>
        <button onclick="EvidencePanel._runInvestigation('${entityId}')"
                id="ep-run-btn" class="btn btn--primary" style="width:100%;margin-bottom:8px">
          Run Full Investigation
        </button>
        <button onclick="EvidencePanel._runContradiction('${entityId}')"
                id="ep-contra-btn" class="btn btn--secondary" style="width:100%;margin-bottom:8px">
          Contradiction Search
        </button>
        <button onclick="EvidencePanel._openConnectionMap('${entityId}','${sanitize(EvidencePanel._currentName||entityId)}')"
                class="btn btn--secondary" style="width:100%">
          Connection Map
        </button>
      </div>
      <div id="ep-investigation-results"></div>
    `;
  },

  _runInvestigation: async (entityId) => {
    const btn = document.getElementById("ep-run-btn");
    const res = document.getElementById("ep-investigation-results");
    if (btn) { btn.textContent = "Investigating..."; btn.disabled = true; }
    try {
      const data = await Api._request(`/investigate/${entityId}`);
      if (res) {
        const total = data.total_items || 0;
        const layers = data.layers || [];
        res.innerHTML = `
          <div style="padding:14px;background:var(--bg-tertiary);border-radius:10px;
                      border:1px solid var(--color-saffron)">
            <div style="font-size:11px;font-weight:700;color:var(--color-saffron);margin-bottom:10px">
              INVESTIGATION COMPLETE — ${total} ITEMS
            </div>
            ${layers.map(l => `
              <div style="display:flex;justify-content:space-between;
                          font-size:12px;margin-bottom:6px;padding-bottom:6px;
                          border-bottom:1px solid var(--border-color)">
                <span style="color:var(--text-secondary)">Layer ${l.layer}: ${sanitize(l.name)}</span>
                <span style="font-weight:700;color:var(--text-primary)">${l.count}</span>
              </div>`).join("")}
            ${data.confidence ? `
            <div style="margin-top:8px;font-size:11px;color:var(--text-muted)">
              Confidence: <strong style="color:var(--text-primary)">${data.confidence}%</strong>
            </div>` : ""}
          </div>`;
      }
    } catch {
      if (res) res.innerHTML = `<div style="color:var(--text-muted);font-size:12px;margin-top:8px">
        Investigation API unavailable</div>`;
    } finally {
      if (btn) { btn.textContent = "Run Full Investigation"; btn.disabled = false; }
    }
  },

  _runContradiction: async (entityId) => {
    const btn = document.getElementById("ep-contra-btn");
    const res = document.getElementById("ep-investigation-results");
    if (btn) { btn.textContent = "Searching contradictions..."; btn.disabled = true; }
    try {
      const data = await Api._request(`/adversarial/${entityId}`);
      if (res) {
        const items = data.counterevidence || data.items || [];
        res.innerHTML = `
          <div style="padding:14px;background:var(--bg-tertiary);border-radius:10px;
                      border:1px solid var(--color-risk-high);margin-top:8px">
            <div style="font-size:11px;font-weight:700;color:var(--color-risk-high);margin-bottom:10px">
              CONTRADICTION SEARCH — ${items.length} items found
            </div>
            ${items.slice(0,5).map(item => `
              <div style="margin-bottom:8px;padding:8px;background:var(--bg-primary);border-radius:6px">
                <div style="font-size:11px;color:var(--text-primary);margin-bottom:2px">
                  ${sanitize(item.claim||item.finding||"")}
                </div>
                <div style="font-size:10px;color:var(--color-risk-high)">
                  CONTRADICTS: ${sanitize(item.contradicts||"")}
                </div>
              </div>`).join("") || `
            <div style="font-size:12px;color:var(--text-muted)">No contradictions found</div>`}
          </div>`;
      }
    } catch {
      if (res) res.innerHTML = `<div style="color:var(--text-muted);font-size:12px;margin-top:8px">
        Contradiction search unavailable</div>`;
    } finally {
      if (btn) { btn.textContent = "Contradiction Search"; btn.disabled = false; }
    }
  },

  _openConnectionMap: (entityId, entityName) => {
    EvidencePanel.close();
    Router.navigate(`/connection-map?entity=${encodeURIComponent(entityId)}&name=${encodeURIComponent(entityName)}`);
  },

  _investigate: async (entityId) => {
    EvidencePanel._switchTab("investigate");
    setTimeout(() => EvidencePanel._runInvestigation(entityId), 300);
  },

  close: () => {
    if (EvidencePanel._container)
      EvidencePanel._container.style.right = "-480px";
    const overlay = document.getElementById("evidence-overlay");
    if (overlay) overlay.style.display = "none";
    EvidencePanel._visible = false;
  },
};

window.EvidencePanel = EvidencePanel;
