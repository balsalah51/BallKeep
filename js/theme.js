(function () {
  var COOKIE = "bk-theme";
  var YEAR = 60 * 60 * 24 * 365;

  function readCookie() {
    var match = document.cookie.match(/(?:^|; )bk-theme=(dark|light)/);
    return match ? match[1] : "";
  }

  function current() {
    return readCookie() || document.documentElement.getAttribute("data-theme") || "light";
  }

  function write(theme) {
    document.cookie = COOKIE + "=" + theme + "; Path=/; Max-Age=" + YEAR + "; SameSite=Lax";
    document.documentElement.setAttribute("data-theme", theme);
    document.documentElement.style.colorScheme = theme;
    sync(theme);
  }

  function sync(theme) {
    theme = theme || current();
    var dark = theme === "dark";
    document.querySelectorAll("[data-theme-toggle]").forEach(function (btn) {
      btn.setAttribute("aria-pressed", dark ? "true" : "false");
      btn.setAttribute("aria-label", dark ? "Switch to light mode" : "Switch to dark mode");
    });
    var meta = document.querySelector('meta[name="theme-color"]');
    if (meta) {
      if (!meta.getAttribute("data-light-theme")) {
        meta.setAttribute("data-light-theme", meta.getAttribute("content") || "");
      }
      meta.setAttribute("content", dark ? "#0b1220" : meta.getAttribute("data-light-theme"));
    }
  }

  document.addEventListener("click", function (event) {
    var btn = event.target.closest("[data-theme-toggle]");
    if (!btn) return;
    write(current() === "dark" ? "light" : "dark");
  });

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", function () { sync(); });
  } else {
    sync();
  }
})();
