(function () {
  var KEY = "bk-theme";
  function apply(theme) {
    document.documentElement.setAttribute("data-theme", theme);
    try { localStorage.setItem(KEY, theme); } catch (e) {}
    var btn = document.getElementById("theme-toggle");
    if (btn) {
      btn.setAttribute("aria-pressed", theme === "light" ? "true" : "false");
      btn.textContent = theme === "light" ? "Dark" : "Light";
    }
  }
  var saved = null;
  try { saved = localStorage.getItem(KEY); } catch (e) {}
  apply(saved === "light" ? "light" : "dark");
  document.addEventListener("click", function (e) {
    var btn = e.target && e.target.closest && e.target.closest("#theme-toggle");
    if (!btn) return;
    var next = document.documentElement.getAttribute("data-theme") === "light" ? "dark" : "light";
    apply(next);
  });
  function syncDrawer() {
    var d = document.querySelector("header.site details.nav-drawer");
    if (!d) return;
    if (window.matchMedia("(min-width: 861px)").matches) d.setAttribute("open", "");
    else d.removeAttribute("open");
  }
  syncDrawer();
  window.addEventListener("resize", syncDrawer);
})();
