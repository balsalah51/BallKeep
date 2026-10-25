(function () {
  const form = document.getElementById("today-form");
  const input = document.getElementById("today-sleeper");
  const hits = document.getElementById("today-hits");
  if (!form || !input) return;
  const KEY = "bk-sleeper-league";

  function saved() {
    try { return localStorage.getItem(KEY) || ""; } catch (e) { return ""; }
  }
  function remember(id) {
    try { localStorage.setItem(KEY, id); } catch (e) {}
  }

  const known = saved();
  if (known) input.value = known;

  form.addEventListener("submit", function (e) {
    e.preventDefault();
    const id = String(input.value || "").trim();
    if (!id) return;
    remember(id);
    location.href = "league.html?sleeper=" + encodeURIComponent(id);
  });

  if (!known || !hits) return;
  fetch("https://api.sleeper.app/v1/league/" + encodeURIComponent(known) + "/rosters")
    .then(function (r) { return r.ok ? r.json() : []; })
    .then(function (rosters) {
      const n = (rosters || []).reduce(function (acc, row) {
        return acc + ((row.players || []).length);
      }, 0);
      if (!n) return;
      hits.hidden = false;
      hits.textContent = "Remembered league loaded " + n + " rostered names. Open My Team to price them.";
    })
    .catch(function () {});
})();
