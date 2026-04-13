function sanitize(str) {
  const d = document.createElement("div");
  d.textContent = String(str || "");
  return d.innerHTML;
}

const Components = {
  Spinner: (size = "sm") => {
    const el = document.createElement("div");
    el.className = "spinner";
    if (size === "lg") { el.style.width = "40px"; el.style.height = "40px"; }
    return el;
  },

  Toast: (message, type = "info") => {
    const el = document.createElement("div");
    el.className = "toast";
    el.style.borderLeftColor = type === "error" ? "var(--color-risk-very-high)"
      : type === "success" ? "var(--color-green)"
      : "var(--color-saffron)";
    el.textContent = message;
    const container = document.getElementById("toast-container");
    if (container) {
      container.appendChild(el);
      setTimeout(() => el.remove(), 4000);
    }
    return el;
  },

  RiskBadge: (level) => {
    const el = document.createElement("span");
    el.className = `risk-badge risk-badge--${level}`;
    el.textContent = level.replace("_", " ");
    return el;
  },

  RiskBar: (score, level) => {
    const wrapper = document.createElement("div");
    wrapper.className = "risk-score-bar";
    wrapper.innerHTML = `
      <div class="risk-score-bar__track" style="flex:1">
        <div class="risk-score-bar__fill risk-score-bar__fill--${level}"
             style="width:${score}%"></div>
      </div>
      <span style="font-size:var(--font-size-sm);font-weight:600;
                   color:var(--text-secondary);min-width:40px;text-align:right">
        ${score}/100
      </span>
    `;
    return wrapper;
  },

  EntityBadge: (type) => {
    const el = document.createElement("span");
    const t = (type || "").toLowerCase();
    el.className = `badge badge--${t}`;
    el.textContent = type;
    return el;
  },

  ResultCard: (entity, onClick) => {
    const el = document.createElement("div");
    el.className = "result-card";
    el.setAttribute("role", "button");
    el.setAttribute("tabindex", "0");
    const type = (entity.entity_type || "").toLowerCase();
    const icons = { politician: "P", company: "C", contract: "K",
                    auditreport: "A", ministry: "M" };
    const icon = icons[type] || "?";
    el.innerHTML = `
      <div class="result-card__icon result-card__icon--${type}">
        <span style="font-weight:bold;font-size:16px;color:var(--accent-primary)">${icon}</span>
      </div>
      <div class="result-card__content">
        <div class="result-card__name">${sanitize(entity.name || entity.entity_id || "")}</div>
        <div class="result-card__meta">
          <span class="badge badge--${type}">${entity.entity_type || ""}</span>
          ${entity.state ? `<span>${entity.state}</span>` : ""}
          ${entity.party ? `<span>${entity.party}</span>` : ""}
          ${entity.risk_score != null
            ? `<span class="risk-badge risk-badge--${entity.risk_level || "LOW"}">
                 ${entity.risk_score}/100
               </span>`
            : ""}
        </div>
      </div>
    `;
    el.addEventListener("click", () => onClick && onClick(entity));
    el.addEventListener("keydown", (e) => {
      if (e.key === "Enter") onClick && onClick(entity);
    });
    return el;
  },

  FindingItem: (finding) => {
    const el = document.createElement("div");
    el.className = `finding-item finding-item--${finding.severity || "LOW"}`;
    const evidence = (finding.evidence || [])
      .slice(0, 3)
      .map(e => `<span class="evidence-chip">${e.substring(0, 60)}</span>`)
      .join("");
    el.innerHTML = `
      <div class="finding-item__severity" style="color:${
        finding.severity === "HIGH" ? "var(--color-risk-high)"
        : finding.severity === "VERY_HIGH" ? "var(--color-risk-very-high)"
        : finding.severity === "MODERATE" ? "#856404"
        : "var(--color-risk-low)"
      }">${finding.severity || "LOW"}</div>
      <div class="finding-item__desc">${finding.description || ""}</div>
      ${evidence ? `<div style="margin-top:var(--space-2)">${evidence}</div>` : ""}
    `;
    return el;
  },

  FeedItem: (item) => {
    const el = document.createElement("div");
    el.className = "feed-item";
    const level = item.risk_level || "MODERATE";
    el.innerHTML = `
      <div class="feed-item__indicator feed-item__indicator--${level}"></div>
      <div style="flex:1">
        <div class="feed-item__headline">${sanitize(item.headline || item.message || "")}</div>
        <div class="feed-item__meta">
          ${item.source ? `<span>${sanitize(item.source)}</span>` : ""}
          ${item.detected_at
            ? `<span>${new Date(item.detected_at).toLocaleString("en-IN")}</span>`
            : ""}
        </div>
      </div>
    `;
    return el;
  },

  StatCard: (value, label) => {
    const el = document.createElement("div");
    el.className = "stat-card";
    el.innerHTML = `
      <div class="stat-card__value">${value}</div>
      <div class="stat-card__label">${label}</div>
    `;
    return el;
  },

  Skeleton: (height = 60, width = "100%") => {
    const el = document.createElement("div");
    el.className = "skeleton";
    el.style.height = `${height}px`;
    el.style.width = typeof width === "number" ? `${width}px` : width;
    return el;
  },

  SkeletonGroup: (count = 3) => {
    const frag = document.createDocumentFragment();
    for (let i = 0; i < count; i++) {
      const el = Components.Skeleton(72, "100%");
      el.style.marginBottom = "12px";
      frag.appendChild(el);
    }
    return frag;
  },
};

window.Components = Components;
