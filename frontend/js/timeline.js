const Timeline = {

  CATEGORY_COLORS: {
    political:  "var(--color-saffron)",
    financial:  "var(--color-india-green)",
    regulatory: "#DC3545",
    legal:      "#6F42C1",
    corporate:  "var(--color-ashoka-blue)",
    media:      "var(--text-muted)",
  },

  CATEGORY_ICONS: {
    political:  "🏛",
    financial:  "💰",
    regulatory: "📋",
    legal:      "⚖",
    corporate:  "🏢",
    media:      "📰",
  },

  render: (containerId, timelineData, convergenceData) => {
    const el = document.getElementById(containerId);
    if (!el) return;

    const events      = timelineData?.events      || [];
    const byYear      = timelineData?.by_year     || {};
    const convergences = convergenceData?.convergences || [];

    if (!events.length) {
      el.innerHTML = `
        <div style="padding:40px;text-align:center;color:var(--text-muted)">
          No timeline events found for this entity.
        </div>`;
      return;
    }

    const years = Object.keys(byYear).sort();

    el.innerHTML = `
      <div style="padding:0 16px">
        <div style="display:flex;gap:8px;flex-wrap:wrap;margin-bottom:20px">
          ${Object.entries(Timeline.CATEGORY_COLORS).map(([cat, color]) => `
            <span style="font-size:10px;padding:3px 8px;border-radius:12px;
                         background:var(--bg-tertiary);color:${color};
                         font-weight:600;text-transform:uppercase">
              ${Timeline.CATEGORY_ICONS[cat]||''} ${cat}
            </span>
          `).join("")}
        </div>
        ${convergences.filter(c=>c.severity==="HIGH").length ? `
        <div style="padding:10px 14px;background:rgba(220,53,69,0.1);
                    border:1px solid rgba(220,53,69,0.3);border-radius:8px;
                    margin-bottom:20px;font-size:12px;color:#DC3545">
          ⚠ ${convergences.filter(c=>c.severity==="HIGH").length} high-proximity
          temporal convergences detected
        </div>` : ""}
        <div style="position:relative">
          <div style="position:absolute;left:16px;top:0;bottom:0;
                      width:2px;background:var(--border-color)"></div>
          ${years.map(year => `
            <div style="margin-bottom:28px">
              <div style="display:flex;align-items:center;margin-bottom:12px">
                <div style="width:32px;height:32px;border-radius:50%;
                            background:var(--bg-secondary);
                            border:2px solid var(--accent-primary);
                            display:flex;align-items:center;justify-content:center;
                            font-size:10px;font-weight:700;
                            color:var(--accent-primary);z-index:1;
                            flex-shrink:0">
                  ${year.slice(2)}
                </div>
                <span style="margin-left:10px;font-size:13px;font-weight:700;
                             color:var(--text-secondary)">${year}</span>
              </div>
              <div style="margin-left:44px">
                ${(byYear[year]||[]).map(event => `
                  <div style="padding:10px 12px;margin-bottom:8px;
                              background:var(--bg-tertiary);border-radius:6px;
                              border-left:3px solid ${Timeline.CATEGORY_COLORS[event.category]||'var(--border-color)'}">
                    <div style="display:flex;align-items:center;gap:6px;margin-bottom:3px">
                      <span style="font-size:13px">
                        ${Timeline.CATEGORY_ICONS[event.category]||''}
                      </span>
                      <span style="font-size:12px;font-weight:600;
                                   color:var(--text-primary)">
                        ${event.title}
                      </span>
                    </div>
                    <div style="font-size:11px;color:var(--text-secondary);
                                margin-bottom:3px">${event.detail||''}</div>
                    <div style="display:flex;justify-content:space-between">
                      <span style="font-size:10px;color:var(--text-muted)">
                        ${event.date}
                      </span>
                      <span style="font-size:10px;color:var(--text-muted);
                                   background:var(--bg-secondary);
                                   padding:1px 6px;border-radius:4px">
                        ${event.source}
                      </span>
                    </div>
                  </div>
                `).join("")}
              </div>
            </div>
          `).join("")}
        </div>
      </div>
    `;
  },
};

window.Timeline = Timeline;
