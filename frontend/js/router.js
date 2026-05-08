const Router = {
  _routes: {},
  _current: null,

  register: (path, handler) => {
    Router._routes[path] = handler;
  },

  navigate: (path, pushState = true) => {
    // JS-4 FIX: stop D3 force simulation before clearing main DOM.
    // Without this, the simulation timer keeps running indefinitely after
    // navigation, consuming CPU and holding references to removed elements.
    if (window.GraphRenderer && GraphRenderer._currentSimulation) {
      GraphRenderer._currentSimulation.stop();
      GraphRenderer._currentSimulation = null;
    }
    // FEED-4 FIX: close open WebSocket feed socket on navigation
    if (window._activeFeedSocket && window._activeFeedSocket.readyState <= 1) {
      window._activeFeedSocket.close();
      window._activeFeedSocket = null;
    }
    if (pushState) {
      window.history.pushState({}, "", `#${path}`);
    }
    const cleanPath = path.split("?")[0];
    const matched = Router._match(cleanPath);
    if (matched) {
      Router._current = cleanPath;
      const main = document.getElementById("app-main");
      if (main) {
        main.innerHTML = "";
        const spinner = Components.Spinner("lg");
        spinner.style.margin = "80px auto";
        main.appendChild(spinner);
      }
      matched.handler(matched.params);
      Router._updateNav(cleanPath);
    }
  },

  _match: (path) => {
    if (Router._routes[path]) {
      return { handler: Router._routes[path], params: {} };
    }
    for (const [pattern, handler] of Object.entries(Router._routes)) {
      if (!pattern.includes(":")) continue;
      const regex = new RegExp(
        "^" + pattern.replace(/:([^/]+)/g, "(?<$1>[^/]+)") + "$"
      );
      const match = path.match(regex);
      if (match) return { handler, params: match.groups || {} };
    }
    // LOGIC FIX: catch-all route -- render 404 view instead of frozen spinner
    if (Router._routes["*"]) {
      return { handler: Router._routes["*"], params: { path } };
    }
    return null;
  },

  _updateNav: (path) => {
    document.querySelectorAll(".navbar__nav-link").forEach(link => {
      const href = link.getAttribute("data-route");
      link.classList.toggle("active", href === path || (href !== "/" && (path === href || path.startsWith(href + "/"))));
    });
  },

  init: () => {
    // H-09 FIX: listen to both popstate (browser back/forward) AND
    // hashchange (direct URL entry, anchor link clicks). Both are needed
    // for a hash-router. popstate alone misses direct URL navigation.
    const _handleNav = () => {
      const hash = window.location.hash.slice(1) || "/";
      Router.navigate(hash, false);
    };
    window.addEventListener("popstate",   _handleNav);
    window.addEventListener("hashchange", _handleNav);
    _handleNav();
  },
};

window.Router = Router;
