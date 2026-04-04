const EvidencePanel = {
  _visible: false,
  _container: null,

  init: () => {
    const panel = document.createElement("div");
    panel.id = "evidence-panel";
    panel.style.cssText = `
      position: fixed; top: 0; right: -420px; width: 400px; height: 100vh;
      background: var(--bg-secondary); border-left: 1px solid var(--border-color);
      box-shadow: -4px 0 24px rgba(0,0,0,0.3); z-index: 500;
      overflow-y: auto; transition: right 0.3s ease; padding: 0;
    `;
    document.body.appendChild(panel);
    EvidencePanel._container = panel;

    const overlay = document.createElement("div");
    overlay.id = "evidence-overlay";
    overlay.style.cssText = `
      position:fixed;inset:0;background:rgba(0,0,0,0.4);
      z-index:499;display:none;
    `;
    overlay.addEventListener("click", EvidencePanel.close);
    document.body.appendChild(overlay);
  },

  open: async (entityId, entityName) => {
    if (!EvidencePanel._container) EvidencePanel.init();
    EvidencePanel._container.innerHTML = `
      <div style="padding:20px">
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:16px">
          <span style="font-size:11px;font-weight:600;letter-spacing:.1em;
                       text-transform:uppercase;color:var(--color-saffron)">
            Evidence Panel
          </span>
          <button onclick="EvidencePanel.close()"
                  style="background:none;border:none;color:var(--text-muted);
                         font-size:20px;cursor:pointer;line-height:1">×</button>
        </div>
        <h2 style="font-size:18px;font-weight:700;color:var(--text-primary);margin-bottom:4px">
          ${entityName || entityId}
        </h2>
        <div style="font-size:12px;color:var(--text-muted);margin-bottom:20px">
          Entity ID: ${entityId}
        </div>
        <div id="panel-content">
          <div class="spinner" style="margin:40px auto"></div>
        </div>
      </div>
    `;
    EvidencePanel._container.style.right = "0";
    document.getElementById("evidence-overlay").style.display = "block";
    EvidencePanel._visible = true;

    try {
      const data = await Api.nodeEvidence(entityId);
      EvidencePanel._render(data, entityId);
    } catch (err) {
      document.getElementById("panel-content").innerHTML = `
        <p style="color:var(--color-risk-very-high);font-size:13px">
          Could not load evidence. Ensure API is running.
        </p>`;
    }
  },

  _render: (data, entityId) => {
    const info   = data.entity_info || {};
    const edges  = data.edges || [];
    const el     = document.getElementById("panel-content");
    if (!el) return;

    const riskColour = {
      "LOW":"var(--color-risk-low)","MODERATE":"#856404",
      "HIGH":"var(--color-risk-high)","VERY_HIGH":"var(--color-risk-very-high)"
    }[info.risk_level] || "var(--text-muted)";

    el.innerHTML = `
      ${info.risk_score != null ? `
      <div style="padding:12px;background:var(--bg-tertiary);border-radius:8px;margin-bottom:16px">
        <div style="font-size:11px;text-transform:uppercase;letter-spacing:.08em;
                    color:var(--text-muted);margin-bottom:6px">Structural Risk</div>
        <div style="display:flex;align-items:center;gap:8px">
          <div style="flex:1;height:6px;background:var(--bg-primary);border-radius:3px;overflow:hidden">
            <div style="width:${info.risk_score}%;height:100%;background:${riskColour};border-radius:3px"></div>
          </div>
          <span style="font-weight:700;font-size:13px;color:${riskColour}">
            ${info.risk_score}/100
          </span>
        </div>
      </div>` : ""}

      <div style="margin-bottom:20px">
        <div style="font-size:12px;font-weight:600;text-transform:uppercase;
                    letter-spacing:.08em;color:var(--text-muted);margin-bottom:8px">
          Connections (${edges.length})
        </div>
        ${edges.slice(0, 15).map(edge => `
          <div style="padding:10px 12px;margin-bottom:8px;background:var(--bg-tertiary);
                      border-radius:6px;border-left:3px solid ${edge.color || '#666'}">
            <div style="display:flex;align-items:center;gap:6px;margin-bottom:4px">
              <span style="font-size:10px;font-weight:600;text-transform:uppercase;
                           color:${edge.color};letter-spacing:.06em">${edge.rel_label}</span>
              <span style="font-size:10px;color:var(--text-muted)">
                ${edge.strength === "strong" ? "●" : edge.strength === "medium" ? "◐" : "○"}
                ${edge.strength}
              </span>
            </div>
            <div style="font-size:13px;font-weight:500;color:var(--text-primary);margin-bottom:2px">
              ${edge.connected_to || edge.connected_id}
            </div>
            <div style="font-size:11px;color:var(--text-secondary);margin-bottom:4px">
              <strong>WHY:</strong> ${edge.why}
            </div>
            <div style="font-size:10px;color:var(--text-muted)">
              <strong>SOURCE:</strong> ${edge.source}
            </div>
            ${edge.next_leads && edge.next_leads.length ? `
            <div style="margin-top:6px;padding-top:6px;border-top:1px solid var(--border-color)">
              <div style="font-size:10px;color:var(--color-saffron);font-weight:600;margin-bottom:3px">
                NEXT LEADS
              </div>
              ${edge.next_leads.map(l => `
                <div style="font-size:10px;color:var(--text-muted);margin-bottom:2px">→ ${l}</div>
              `).join("")}
            </div>` : ""}
          </div>
        `).join("")}
      </div>

      <button onclick="EvidencePanel._investigate('${entityId}')"
              class="btn btn--primary" style="width:100%;margin-bottom:8px">
        Investigate Further (6 Layers)
      </button>
      <button onclick="Router.navigate('/entity/${entityId}');EvidencePanel.close();"
              class="btn btn--secondary" style="width:100%">
        Open Full Dossier
      </button>
    `;
  },

  _investigate: async (entityId) => {
    const btn = document.querySelector("#panel-content .btn--primary");
    if (btn) { btn.textContent = "Investigating..."; btn.disabled = true; }
    try {
      const data = await Api._request(`/investigate/${entityId}`);
      const el   = document.getElementById("panel-content");
      if (!el) return;
      const total = data.total_items || 0;
      el.innerHTML += `
        <div style="margin-top:16px;padding:12px;background:var(--bg-tertiary);
                    border-radius:8px;border:1px solid var(--color-saffron)">
          <div style="font-size:11px;font-weight:600;color:var(--color-saffron);
                      margin-bottom:8px">6-LAYER INVESTIGATION COMPLETE</div>
          ${(data.layers || []).map(l => `
            <div style="display:flex;justify-content:space-between;
                        font-size:11px;margin-bottom:4px">
              <span style="color:var(--text-secondary)">Layer ${l.layer}: ${l.name}</span>
              <span style="color:var(--text-primary);font-weight:600">${l.count} items</span>
            </div>
          `).join("")}
          <div style="margin-top:6px;padding-top:6px;border-top:1px solid var(--border-color);
                      font-size:12px;font-weight:600;color:var(--text-primary)">
            Total: ${total} investigative items
          </div>
        </div>
      `;
    } catch (err) {
      if (btn) { btn.textContent = "Investigate Further"; btn.disabled = false; }
    }
  },

  close: () => {
    if (EvidencePanel._container)
      EvidencePanel._container.style.right = "-420px";
    const overlay = document.getElementById("evidence-overlay");
    if (overlay) overlay.style.display = "none";
    EvidencePanel._visible = false;
  },
};

window.EvidencePanel = EvidencePanel;
