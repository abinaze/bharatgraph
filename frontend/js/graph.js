const GraphRenderer = {
  // H-07 FIX: expanded from 8 to 22 node types -- all graph nodes now coloured
  NODE_COLORS: {
    Politician:        "#FF9933",
    Company:           "#138808",
    Contract:          "#000080",
    AuditReport:       "#DC3545",
    Ministry:          "#0A0F2E",
    Scheme:            "#6F42C1",
    Party:             "#17A2B8",
    PressRelease:      "#20C997",
    NGO:               "#FD7E14",
    ElectoralBond:     "#E83E8C",
    InsolvencyOrder:   "#6C757D",
    Tender:            "#007BFF",
    RegulatoryOrder:   "#FF6B35",
    EnforcementAction: "#DC3545",
    ParliamentQuestion:"#0DCAF0",
    VigilanceCircular: "#FFC107",
    ICIJEntity:        "#6610F2",
    SanctionedEntity:  "#D63384",
    CourtCase:         "#198754",
    LocalBody:         "#0D6EFD",
    DataGovDocument:   "#20C997",
    CrimeReport:       "#DC3545",
    Unknown:           "#6C757D",
  },

  NODE_ICONS: {
    Politician:        "P",
    Company:           "C",
    Contract:          "K",
    AuditReport:       "A",
    Ministry:          "M",
    Scheme:            "S",
    Party:             "Y",
    PressRelease:      "N",
    NGO:               "G",
    ElectoralBond:     "B",
    InsolvencyOrder:   "I",
    Tender:            "T",
    RegulatoryOrder:   "R",
    EnforcementAction: "E",
    ParliamentQuestion:"Q",
    VigilanceCircular: "V",
    ICIJEntity:        "X",
    SanctionedEntity:  "Z",
    CourtCase:         "J",
    LocalBody:         "L",
    DataGovDocument:   "D",
    CrimeReport:       "CR",
  },

  init: (containerId, data) => {
    const container = document.getElementById(containerId);
    if (!container) return;
    container.innerHTML = "";

    if (!window.d3) {
      container.innerHTML = `<div style="display:flex;align-items:center;justify-content:center;height:100%;color:var(--text-muted);font-size:14px;">D3.js not loaded -- graph unavailable</div>`;
      return;
    }

    const d3 = window.d3;
    const width  = container.offsetWidth  || container.clientWidth  || 800;
    const height = container.offsetHeight || container.clientHeight || 500;

    const svg = d3.select(`#${containerId}`)
      .append("svg")
      .attr("width",   "100%")
      .attr("height",  "100%")
      .attr("viewBox", `0 0 ${width} ${height}`);

    const g = svg.append("g");

    // BUG-3 FIX: store zoom behavior on GraphRenderer so resetZoom() can
    // reference the exact instance that is bound to this SVG.
    // Previously _zoomBehavior was never assigned, so resetZoom got undefined
    // and fell back to creating an unattached new d3.zoom() with zero effect.
    GraphRenderer._zoomBehavior = d3.zoom()
      .scaleExtent([0.3, 4])
      .on("zoom", (event) => g.attr("transform", event.transform));
    svg.call(GraphRenderer._zoomBehavior);

    const nodes = (data.nodes || []).map(n => ({ ...n }));
    const links = (data.edges || []).map(e => ({
      source: e.source,
      target: e.target,
      relationship: e.relationship,
    }));

    const simulation = d3.forceSimulation(nodes)
      .force("link",      d3.forceLink(links).id(d => d.id).distance(120))
      .force("charge",    d3.forceManyBody().strength(-300))
      .force("center",    d3.forceCenter(width / 2, height / 2))
      .force("collision", d3.forceCollide(40));

    // M-11 FIX: id="arrowhead" is global in SVG namespace. If GraphRenderer.init()
    // is called more than once (tab switch), duplicate IDs appear and the browser
    // uses the first (possibly removed) element. Use container-scoped unique ID.
    const markerId = "arrowhead-" + containerId;
    const defs = svg.append("defs");
    defs.append("marker")
      .attr("id",          markerId)
      .attr("viewBox",     "-0 -5 10 10")
      .attr("refX",        28)
      .attr("refY",        0)
      .attr("orient",      "auto")
      .attr("markerWidth", 6)
      .attr("markerHeight",6)
      .append("path")
      .attr("d",    "M 0,-5 L 10,0 L 0,5")
      .attr("fill", "rgba(255,255,255,0.3)");

    const link = g.append("g")
      .selectAll("line")
      .data(links)
      .join("line")
      .attr("stroke",       "rgba(255,255,255,0.15)")
      .attr("stroke-width", 1.5)
      .attr("marker-end",   "url(#" + markerId + ")");

    const linkLabel = g.append("g")
      .selectAll("text")
      .data(links)
      .join("text")
      .text(d => d.relationship)
      .attr("fill",        "rgba(255,255,255,0.4)")
      .attr("font-size",   "8px")
      .attr("text-anchor", "middle")
      .attr("font-family", "Inter, sans-serif");

    const node = g.append("g")
      .selectAll("g")
      .data(nodes)
      .join("g")
      .attr("cursor", "pointer")
      .call(d3.drag()
        .on("start", (event, d) => {
          if (!event.active) simulation.alphaTarget(0.3).restart();
          d.fx = d.x; d.fy = d.y;
        })
        .on("drag",  (event, d) => { d.fx = event.x; d.fy = event.y; })
        .on("end",   (event, d) => {
          if (!event.active) simulation.alphaTarget(0);
          d.fx = null; d.fy = null;
        })
      )
      // BUG-26 FIX: added missing closing ); on .on("click") chain
      .on("click", (event, d) => {
        event.stopPropagation();
        if (window.EvidencePanel) {
          EvidencePanel.open(d.id, d.name || d.id);
        } else if (window.Router) {
          Router.navigate(`/entity/${d.id}`);
        }
      });

    node.append("circle")
      .attr("r",            22)
      .attr("fill",         d => GraphRenderer.NODE_COLORS[d.label] || "#6C757D")
      .attr("stroke",       "rgba(255,255,255,0.3)")
      .attr("stroke-width", 2);

    node.append("text")
      .text(d => GraphRenderer.NODE_ICONS[d.label] || "?")
      .attr("text-anchor",       "middle")
      .attr("dominant-baseline", "central")
      .attr("fill",              "white")
      .attr("font-size",         "12px")
      .attr("font-weight",       "bold")
      .attr("font-family",       "Inter, sans-serif")
      .attr("pointer-events",    "none");

    node.append("text")
      .text(d => (d.name || d.id || "").substring(0, 18))
      .attr("text-anchor", "middle")
      .attr("y",           34)
      .attr("fill",        "var(--text-secondary)")
      .attr("font-size",   "9px")
      .attr("font-family", "Inter, sans-serif")
      .attr("pointer-events", "none");

    node.append("title").text(d => `${d.label}: ${d.name || d.id}`);

    simulation.on("tick", () => {
      link
        .attr("x1", d => d.source.x)
        .attr("y1", d => d.source.y)
        .attr("x2", d => d.target.x)
        .attr("y2", d => d.target.y);

      linkLabel
        .attr("x", d => ((d.source.x || 0) + (d.target.x || 0)) / 2)
        .attr("y", d => ((d.source.y || 0) + (d.target.y || 0)) / 2);

      node.attr("transform", d => `translate(${d.x || 0},${d.y || 0})`);
    });

    // L-06 FIX: store simulation so tab-switch can stop it (prevents
    // D3 force simulation running in background consuming CPU when graph is hidden)
    GraphRenderer._currentSimulation = simulation;
    // L-06 FIX: store simulation ref so tab-switch can call .stop()
    // D3 force runs in background consuming CPU when graph tab is hidden
    return simulation;
  },

  // BUG-2 FIX: Reset button had `const` inside an inline onclick expression
  // which is a JS SyntaxError. Moved all reset logic here as a named function.
  // BUG-3 FIX: uses stored _zoomBehavior reference -- not a new d3.zoom() object.
  resetZoom: (containerId) => {
    if (!window.d3) return;
    const svg = window.d3.select("#" + containerId + " svg");
    if (!svg || svg.empty()) return;
    if (GraphRenderer._zoomBehavior) {
      svg.transition().duration(300)
         .call(GraphRenderer._zoomBehavior.transform, window.d3.zoomIdentity);
    } else {
      svg.call(window.d3.zoom().transform, window.d3.zoomIdentity);
    }
  },

  renderLegend: (containerId) => {
    const el = document.getElementById(containerId);
    if (!el) return;
    el.innerHTML = Object.entries(GraphRenderer.NODE_COLORS)
      .filter(([k]) => k !== "Unknown")
      .map(([label, color]) => `
        <div class="graph-legend__item">
          <div class="graph-legend__dot" style="background:${color}"></div>
          <span>${label}</span>
        </div>
      `).join("");
  },
};

window.GraphRenderer = GraphRenderer;
