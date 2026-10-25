(function () {
  const form = document.getElementById("today-form");
  const input = document.getElementById("today-sleeper");
  const userInput = document.getElementById("today-user");
  const hits = document.getElementById("today-hits");
  if (!form || !input) return;
  const LEAGUE_KEY = "bk-sleeper-league";
  const USER_KEY = "bk-sleeper-user";
  const SLEEPER = "https://api.sleeper.app/v1";

  function saved(key) {
    try { return localStorage.getItem(key) || ""; } catch (e) { return ""; }
  }
  function remember(key, value) {
    try {
      if (value) localStorage.setItem(key, value);
      else localStorage.removeItem(key);
    } catch (e) {}
  }
  function note(text) {
    if (!hits) return;
    hits.hidden = false;
    hits.textContent = text;
  }

  const known = saved(LEAGUE_KEY);
  const knownUser = saved(USER_KEY);
  if (known) input.value = known;
  if (userInput && knownUser) userInput.value = knownUser;

  function openLeague(id) {
    remember(LEAGUE_KEY, id);
    location.href = "league.html?sleeper=" + encodeURIComponent(id);
  }

  form.addEventListener("submit", function (e) {
    e.preventDefault();
    const id = String(input.value || "").trim();
    const username = userInput ? String(userInput.value || "").trim() : "";
    if (username) remember(USER_KEY, username);
    if (id) {
      openLeague(id);
      return;
    }
    if (!username) return;
    note("Looking up " + username + " on Sleeper.");
    fetch(SLEEPER + "/user/" + encodeURIComponent(username))
      .then(function (r) { return r.ok ? r.json() : null; })
      .then(function (user) {
        if (!user || !user.user_id) throw new Error("No Sleeper user named " + username + ".");
        return fetch(SLEEPER + "/user/" + encodeURIComponent(user.user_id) + "/leagues/nfl/2026");
      })
      .then(function (r) { return r.ok ? r.json() : []; })
      .then(function (leagues) {
        leagues = leagues || [];
        if (!leagues.length) throw new Error("No 2026 football leagues for " + username + ".");
        if (leagues.length === 1) {
          openLeague(leagues[0].league_id);
          return;
        }
        if (!hits) return;
        hits.hidden = false;
        hits.textContent = "";
        const label = document.createElement("span");
        label.textContent = username + " has " + leagues.length + " leagues. Pick one. ";
        hits.appendChild(label);
        leagues.forEach(function (league) {
          const btn = document.createElement("button");
          btn.type = "button";
          btn.className = "cta alt";
          btn.style.margin = "4px";
          btn.textContent = league.name || league.league_id;
          btn.addEventListener("click", function () { openLeague(league.league_id); });
          hits.appendChild(btn);
        });
      })
      .catch(function (err) { note(err.message || "Sleeper lookup failed."); });
  });

  if (!known || !hits) return;
  fetch(SLEEPER + "/league/" + encodeURIComponent(known) + "/rosters")
    .then(function (r) { return r.ok ? r.json() : []; })
    .then(function (rosters) {
      const n = (rosters || []).reduce(function (acc, row) {
        return acc + ((row.players || []).length);
      }, 0);
      if (!n) return;
      const who = knownUser ? knownUser + " · " : "";
      note(who + "Remembered league loaded " + n + " rostered names. Open My Team to price them.");
    })
    .catch(function () {});
})();
