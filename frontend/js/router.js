const Router = {
  _routes: {},
  _current: null,

  register: (path, handler) => {
    Router._routes[path] = handler;
  },

  navigate: (path, pushState = true) => {
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
    return null;
  },

  _updateNav: (path) => {
    document.querySelectorAll(".navbar__nav-link").forEach(link => {
      const href = link.getAttribute("data-route");
      link.classList.toggle("active", href === path || (href !== "/" && path.startsWith(href)));
    });
  },

  init: () => {
    window.addEventListener("popstate", () => {
      const hash = window.location.hash.slice(1) || "/";
      Router.navigate(hash, false);
    });
    const hash = window.location.hash.slice(1) || "/";
    Router.navigate(hash, false);
  },
};

window.Router = Router;
