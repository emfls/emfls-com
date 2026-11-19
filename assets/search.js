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

  function words(text) {
    return text.toLowerCase().match(/[\p{L}\p{N}]+/gu) || [];
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

    var indexRequest = null;

    function loadIndex() {
      if (!indexRequest) {
        indexRequest = fetch(base + "search-index.json")
          .then(function (response) {
            if (!response.ok) throw new Error("Index fetch failed");
            return response.json();
          })
          .then(function (items) {
            if (!Array.isArray(items) || !items.every(function (item) {
              return item && typeof item.title === "string" && typeof item.path === "string"
                && /^[a-z0-9-]+\/[a-z0-9-]+\/$/.test(item.path);
            })) {
              throw new Error("Invalid search index");
            }
            return items;
          })
          .catch(function (error) {
            indexRequest = null;
            throw error;
          });
      }
      return indexRequest;
    }

    function renderMatches(items, query) {
      var terms = words(query);
      if (!terms.length) {
        resultsBox.innerHTML = "";
        return;
      }
      var matched = items.map(function (item) {
        var primary = words(item.title + " " + item.path);
        var secondary = words([item.category_label, item.summary, item.description].join(" "));
        var score = 0;
        for (var i = 0; i < terms.length; i++) {
          var term = terms[i];
          if (primary.some(function (word) { return word.startsWith(term); })) {
            score += 2;
          } else if (secondary.some(function (word) { return word.startsWith(term); })) {
            score += 1;
          } else {
            return { item: item, score: 0 };
          }
        }
        return { item: item, score: score };
      }).filter(function (match) {
        return match.score > 0;
      }).sort(function (a, b) {
        return b.score - a.score;
      }).slice(0, 8);

      if (!matched.length) {
        resultsBox.innerHTML = '<p style="margin:8px 0 0;color:#4a5568">No matching field guides found for "' + escapeHtml(query) + '".</p>';
        return;
      }
      var html = '<div class="grid-2">';
      for (var j = 0; j < matched.length; j++) {
        var item = matched[j].item;
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
      if (!q.trim()) {
        resultsBox.innerHTML = "";
        return;
      }
      loadIndex().then(function (items) {
        if (input.value === q) renderMatches(items, q);
      }, function () {
        if (input.value === q) {
          resultsBox.textContent = "Search is temporarily unavailable. Browse the guide categories on this page or try again.";
        }
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
