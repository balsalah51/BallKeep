(function () {
  window.__bkBoard = true;
  var PAGE = 50;
  var shown = PAGE;

  function showAll() {
    var t = table();
    return !!(t && t.getAttribute("data-show-all") === "1");
  }
  function pageSize() {
    return showAll() ? 1e9 : PAGE;
  }

  function wrap() {
    return document.querySelector(".table-wrap:has(table.rank-table)") ||
      document.querySelector(".table-wrap");
  }
  function table() {
    return document.querySelector("table.rank-table");
  }
  function rows() {
    var t = table();
    return t ? Array.prototype.slice.call(t.querySelectorAll("tbody tr")) : [];
  }
  function needle() {
    var inp = document.querySelector(".rank-search-input");
    return inp ? String(inp.value || "").trim().toLowerCase() : "";
  }
  function wantPos() {
    var btn = document.querySelector(".rank-bar .filters button.active") ||
      document.querySelector(".filters button.active");
    if (!btn) return "all";
    return String(btn.getAttribute("data-pos") || btn.getAttribute("data-group") || "all").toLowerCase();
  }
  function matches(tr) {
    var q = needle();
    var pos = wantPos();
    var hay = (tr.getAttribute("data-name") || "").toLowerCase();
    var nameOk = !q || hay.indexOf(q) !== -1;
    var rowPos = (tr.getAttribute("data-pos") || "").toLowerCase();
    var rowGroup = (tr.getAttribute("data-group") || "").toLowerCase();
    var posOk = pos === "all" || rowPos === pos || rowGroup === pos;
    return nameOk && posOk;
  }
  function emptyEl() {
    return document.querySelector(".board-empty");
  }
  function moreBtn() {
    return document.querySelector(".board-more");
  }
  function countEl() {
    return document.querySelector(".board-count");
  }

  function paint() {
    var all = rows();
    var vis = 0;
    var matched = 0;
    all.forEach(function (tr) {
      if (!matches(tr)) {
        tr.hidden = true;
        tr.classList.remove("is-shown");
        return;
      }
      matched += 1;
      if (matched <= shown || showAll()) {
        tr.hidden = false;
        tr.classList.add("is-shown");
        vis += 1;
      } else {
        tr.hidden = true;
        tr.classList.remove("is-shown");
      }
    });
    var empty = emptyEl();
    if (empty) empty.hidden = matched !== 0;
    var more = moreBtn();
    if (more) more.hidden = showAll() || matched <= shown;
    var count = countEl();
    if (count) {
      count.textContent = matched
        ? (showAll() ? matched + " players" : vis + " of " + matched + " players")
        : "No matching players";
    }
  }

  window.applyRankFilter = function () {
    shown = pageSize();
    paint();
  };

  document.addEventListener("input", function (e) {
    if (e.target && e.target.classList && e.target.classList.contains("rank-search-input")) {
      window.applyRankFilter();
    }
  });
  document.addEventListener("click", function (e) {
    var b = e.target.closest(".rank-bar .filters button, .board-pos button");
    if (b && b.closest(".filters")) {
      var box = b.closest(".filters");
      box.querySelectorAll("button").forEach(function (x) { x.classList.remove("active"); });
      b.classList.add("active");
      window.applyRankFilter();
      return;
    }
    if (e.target.closest(".board-more")) {
      shown += pageSize() === 1e9 ? 1e9 : PAGE;
      paint();
      return;
    }
    var dens = e.target.closest("[data-density]");
    if (dens) {
      var t = table();
      if (!t) return;
      t.classList.toggle("comfortable", dens.getAttribute("data-density") === "comfortable");
      t.classList.toggle("compact", dens.getAttribute("data-density") !== "comfortable");
      dens.parentNode.querySelectorAll("[data-density]").forEach(function (x) {
        x.classList.toggle("active", x === dens);
      });
      return;
    }
    var src = e.target.closest(".board-sources");
    if (src) {
      var t2 = table();
      if (!t2) return;
      var on = t2.classList.toggle("show-sources");
      src.classList.toggle("active", on);
      src.setAttribute("aria-pressed", on ? "true" : "false");
      src.textContent = on ? "Hide sources" : "Show sources";
      return;
    }
    var sortBtn = e.target.closest("[data-sort]");
    if (sortBtn) {
      var key = sortBtn.getAttribute("data-sort");
      var t3 = table();
      if (!t3) return;
      var tb = t3.tBodies[0];
      var list = rows();
      var dir = sortBtn.getAttribute("data-dir") === "asc" ? "desc" : "asc";
      sortBtn.parentNode.querySelectorAll("[data-sort]").forEach(function (x) {
        if (x !== sortBtn) x.removeAttribute("data-dir");
      });
      sortBtn.setAttribute("data-dir", dir);
      list.sort(function (a, b) {
        var av = a.getAttribute("data-" + key) || a.getAttribute("data-rank") || "";
        var bv = b.getAttribute("data-" + key) || b.getAttribute("data-rank") || "";
        var an = parseFloat(av);
        var bn = parseFloat(bv);
        var cmp;
        if (!isNaN(an) && !isNaN(bn)) cmp = an - bn;
        else cmp = String(av).localeCompare(String(bv));
        return dir === "asc" ? cmp : -cmp;
      });
      list.forEach(function (tr) { tb.appendChild(tr); });
      paint();
    }
  });

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", paint);
  } else {
    paint();
  }
})();
