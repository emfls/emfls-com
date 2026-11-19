(function () {
  function resolveBasePrefix() {
    if (document.body && document.body.dataset && document.body.dataset.root !== undefined) {
      return document.body.dataset.root;
    }
    var p = window.location.pathname || "/";
    if (p === "/emfls-com" || p.indexOf("/emfls-com/") === 0) {
      return "/emfls-com/";
    }
    return "/";
  }

  function escapeHtml(str) {
    return String(str || "")
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }

  function initSearch() {
    var base = resolveBasePrefix();
    var navLinks = document.querySelectorAll("[data-nav-rel]");
    for (var i = 0; i < navLinks.length; i++) {
      var rel = navLinks[i].getAttribute("data-nav-rel") || "";
      navLinks[i].setAttribute("href", base + rel);
    }

    var form = document.getElementById("studio-search-form");
    var input = document.getElementById("studio-search-input");
    var resultsBox = document.getElementById("studio-search-results");
    if (!form || !input || !resultsBox) return;

    var cache = null;

    function loadIndex() {
      if (cache) return Promise.resolve(cache);
      return fetch(base + "search-index.json")
        .then(function (r) {
          if (!r.ok) throw new Error("Index fetch failed");
          return r.json();
        })
        .then(function (data) {
          cache = Array.isArray(data) ? data : [];
          return cache;
        });
    }

    function renderMatches(items, query) {
      var q = String(query || "").trim().toLowerCase();
      if (!q) {
        resultsBox.innerHTML = "";
        return;
      }
      var terms = q.split(/\s+/).filter(Boolean);
      var matched = items.filter(function (item) {
        var hay = (item.title + " " + item.category_label + " " + item.summary).toLowerCase();
        return terms.every(function (t) { return hay.indexOf(t) !== -1; });
      }).slice(0, 8);

      if (!matched.length) {
        resultsBox.innerHTML = '<p style="margin:8px 0 0;color:#4a5568">No matching field guides found for "' + escapeHtml(query) + '".</p>';
        return;
      }
      var html = '<div class="grid-2">';
      for (var j = 0; j < matched.length; j++) {
        var item = matched[j];
        html +=
          '<article class="card">' +
          '<div><div class="card-meta">' + escapeHtml(item.category_label) + ' · ' + escapeHtml(item.reading_minutes) + ' min read</div>' +
          '<h3><a href="' + escapeHtml(base + item.path) + '">' + escapeHtml(item.title) + '</a></h3></div>' +
          '<p>' + escapeHtml(item.summary) + '</p>' +
          '</article>';
      }
      html += "</div>";
      resultsBox.innerHTML = html;
    }

    function runQuery() {
      var q = input.value;
      if (!String(q || "").trim()) {
        resultsBox.innerHTML = "";
        return;
      }
      loadIndex()
        .then(function (items) { renderMatches(items, q); })
        .catch(function () {
          resultsBox.innerHTML = '<p style="margin:8px 0 0;color:#4a5568">Browse categories above to read all 18 guides.</p>';
        });
    }

    form.addEventListener("submit", function (e) {
      e.preventDefault();
      runQuery();
    });
    input.addEventListener("input", runQuery);
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initSearch);
  } else {
    initSearch();
  }
})();
