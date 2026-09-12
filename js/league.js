(function () {
  const SLEEPER = "https://api.sleeper.app/v1";
  const form = document.getElementById("league-form");
  const app = document.getElementById("league-app");
  if (!form || !app) return;

  const state = {
    lookup: null,
    includePicks: true,
    mode: "sf",
    meta: null,
    teams: [],
    owned: {},
  };

  function esc(s) {
    return String(s == null ? "" : s).replace(/[&<>"']/g, function (c) {
      return ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[c];
    });
  }

  function fmt(n) {
    return Math.round(n || 0).toLocaleString("en-US");
  }

  function norm(name) {
    let n = String(name || "").toLowerCase();
    n = n.replace(/\./g, " ");
    n = n.replace(/\b(jr|sr|iii|ii|iv)\b/g, "");
    n = n.replace(/['’]/g, "");
    n = n.replace(/\s+/g, " ").trim();
    return n;
  }

  function valOf(p) {
    if (!p) return 0;
    if (state.mode === "oneqb") return p.oneqb || 0;
    if (state.mode === "ppr") return p.ppr || 0;
    if (state.mode === "classic") return p.classic || 0;
    return p.sf || 0;
  }

  function rankOf(p) {
    if (!p) return 0;
    if (state.mode === "ppr" || state.mode === "classic") return p.board || 0;
    return p.keep || 0;
  }

  function packFromSleeper(id) {
    return (state.lookup.bySleeper || {})[String(id)] || null;
  }

  function rosterIds(r) {
    const seen = {};
    const out = [];
    (r.players || []).concat(r.taxi || []).concat(r.reserve || []).forEach(function (sid) {
      const id = String(sid || "");
      if (!id || seen[id]) return;
      seen[id] = true;
      out.push(id);
    });
    return out;
  }

  function packFromName(name) {
    return (state.lookup.byName || {})[norm(name)] || null;
  }

  function pickBand(worstIndex, n) {
    if (n <= 0) return "Mid";
    const third = n / 3;
    if (worstIndex < third) return "Early";
    if (worstIndex < 2 * third) return "Mid";
    return "Late";
  }

  function pickLabel(season, round, band) {
    const year = String(season);
    if (round >= 3) return year + " 3rd";
    if (round === 2) {
      if (parseInt(year, 10) >= 2028) return year + " 2nd";
      return year + " " + band + " 2nd";
    }
    return year + " " + band + " 1st";
  }

  function pickValue(label) {
    const hits = state.lookup.picks || [];
    for (let i = 0; i < hits.length; i++) {
      if (hits[i].name === label) return hits[i].value || 0;
    }
    const m = label.match(/(\d{4})\s+(Early|Mid|Late)?\s*(1st|2nd|3rd)/);
    if (!m) return 0;
    const yr = parseInt(m[1], 10);
    const year = yr >= 2029 ? "2029" : "2028";
    const fallback = year + " " + (m[3] === "1st" ? (m[2] || "Mid") + " 1st" : m[3] === "2nd" ? "2nd" : "3rd");
    for (let i = 0; i < hits.length; i++) {
      if (hits[i].name === fallback) return hits[i].value || 0;
    }
    return 0;
  }

  function face(p) {
    if (p && p.image) return p.image;
    return "img/logo.jpg";
  }

  function href(p) {
    if (p && p.slug) return "players/" + p.slug + ".html";
    return "";
  }

  async function loadLookup() {
    if (state.lookup) return state.lookup;
    const res = await fetch("data/league-lookup.json");
    if (!res.ok) throw new Error("Lookup file missing.");
    state.lookup = await res.json();
    return state.lookup;
  }

  function detectMode(league) {
    const slots = (league && league.roster_positions) || [];
    const sf = slots.indexOf("SUPER_FLEX") !== -1 || slots.filter(function (s) { return s === "QB"; }).length >= 2;
    const rec = ((league && league.scoring_settings) || {}).rec;
    const typ = ((league && league.settings) || {}).type;
    const dynasty = typ === 2 || typ === 1;
    if (dynasty) return sf ? "sf" : "oneqb";
    if (rec === 0.5) return "classic";
    if (rec === 0 || rec === 0.0) return "ppr";
    return sf ? "sf" : "ppr";
  }

  function standingsOrder(teams) {
    const copy = teams.slice();
    copy.sort(function (a, b) {
      if (a.wins !== b.wins) return a.wins - b.wins;
      return (a.fpts || 0) - (b.fpts || 0);
    });
    const order = {};
    copy.forEach(function (t, i) { order[t.id] = i; });
    return order;
  }

  function scoreTeams() {
    const worst = standingsOrder(state.teams);
    const n = state.teams.length;
    state.teams.forEach(function (t) {
      t.assets = [];
      (t.rawPlayers || []).forEach(function (raw) {
        const p = raw.pack;
        const value = valOf(p);
        t.assets.push({
          kind: "player",
          name: (p && p.name) || raw.name || "Unranked",
          pos: (p && p.pos) || raw.pos || "",
          team: (p && p.team) || "",
          value: value,
          rank: rankOf(p),
          image: face(p),
          href: href(p),
          matched: !!p && value > 0,
        });
      });
      if (state.includePicks) {
        (t.picks || []).forEach(function (pk) {
          const band = pickBand(worst[t.id] == null ? Math.floor(n / 2) : worst[t.id], n);
          const label = pickLabel(pk.season, pk.round, band);
          const value = pickValue(label);
          t.assets.push({
            kind: "pick",
            name: label,
            pos: "PICK",
            team: "",
            value: value,
            rank: 0,
            image: "img/logo.jpg",
            href: "",
            matched: value > 0,
          });
        });
      }
      t.assets.sort(function (a, b) { return b.value - a.value; });
      t.total = t.assets.reduce(function (s, a) { return s + (a.value || 0); }, 0);
      t.posSum = { QB: 0, RB: 0, WR: 0, TE: 0, PICK: 0 };
      t.assets.forEach(function (a) {
        const key = t.posSum[a.pos] != null ? a.pos : (a.kind === "pick" ? "PICK" : "");
        if (key) t.posSum[key] += a.value || 0;
      });
      t.faces = t.assets.filter(function (a) { return a.kind === "player" && a.image && a.image !== "img/logo.jpg"; }).slice(0, 2);
      if (t.faces.length < 2) {
        t.assets.filter(function (a) { return a.kind === "player"; }).slice(0, 2).forEach(function (a) {
          if (t.faces.indexOf(a) === -1) t.faces.push(a);
        });
        t.faces = t.faces.slice(0, 2);
      }
    });
    state.teams.sort(function (a, b) { return b.total - a.total; });
    state.teams.forEach(function (t, i) { t.power = i + 1; });
  }

  function ownedKeys() {
    const keys = {};
    state.teams.forEach(function (t) {
      (t.rawPlayers || []).forEach(function (raw) {
        if (raw.pack) {
          keys[norm(raw.pack.name)] = true;
          if (raw.pack.sleeper_id) keys["sid:" + raw.pack.sleeper_id] = true;
        } else if (raw.name) {
          keys[norm(raw.name)] = true;
        }
      });
    });
    return keys;
  }

  function waivers() {
    const taken = ownedKeys();
    const pool = [];
    const seen = {};
    const src = state.lookup.byName || {};
    Object.keys(src).forEach(function (k) {
      const p = src[k];
      if (!p || seen[k]) return;
      if (taken[k] || (p.sleeper_id && taken["sid:" + p.sleeper_id])) return;
      const value = valOf(p);
      if (!value) return;
      seen[k] = true;
      pool.push({
        name: p.name,
        pos: p.pos,
        team: p.team,
        value: value,
        rank: rankOf(p),
        image: face(p),
        href: href(p),
        wire: false,
      });
    });
    pool.sort(function (a, b) { return b.value - a.value; });
    const wire = {};
    (state.lookup.waiver || []).forEach(function (w) { wire[norm(w.name)] = true; });
    pool.forEach(function (p) { p.wire = !!wire[norm(p.name)]; });
    return pool.slice(0, 24);
  }

  function paint() {
    if (!state.meta) {
      app.hidden = true;
      app.innerHTML = "";
      return;
    }
    scoreTeams();
    const max = Math.max.apply(null, state.teams.map(function (t) { return t.total; }).concat([1]));
    const picksOn = state.includePicks;
    const dynasty = state.meta.kind === "dynasty" || state.meta.kind === "keeper";
    const modeBtns = [
      ["sf", "Superflex"],
      ["oneqb", "1QB"],
      ["ppr", "PPR"],
      ["classic", "Classic"],
    ].map(function (pair) {
      return '<button type="button" class="league-chip' + (state.mode === pair[0] ? " is-on" : "") + '" data-mode="' + pair[0] + '">' + pair[1] + "</button>";
    }).join("");

    const bars = state.teams.map(function (t) {
      const pct = Math.max(4, Math.round((t.total / max) * 100));
      return '<div class="bar-row"><span class="bar-lab">' + esc(t.name) + '</span><span class="bar-track"><span class="bar-fill" style="width:' + pct + '%;background:#c8102e"></span></span><span class="bar-val">' + fmt(t.total) + "</span></div>";
    }).join("");

    const stacks = state.teams.map(function (t) {
      const tot = t.total || 1;
      function w(pos) { return Math.round(((t.posSum[pos] || 0) / tot) * 100); }
      return '<div class="stack-row"><span class="bar-lab">' + esc(t.name) + '</span><div class="pos-stack" title="QB RB WR TE picks">' +
        '<span class="ps qb" style="width:' + w("QB") + '%"></span>' +
        '<span class="ps rb" style="width:' + w("RB") + '%"></span>' +
        '<span class="ps wr" style="width:' + w("WR") + '%"></span>' +
        '<span class="ps te" style="width:' + w("TE") + '%"></span>' +
        '<span class="ps pk" style="width:' + w("PICK") + '%"></span></div></div>';
    }).join("");

    const rows = state.teams.map(function (t) {
      const faces = (t.faces || []).map(function (f) {
        const img = '<img src="' + esc(f.image) + '" alt="' + esc(f.name) + '" width="72" height="72" />';
        return f.href ? '<a href="' + esc(f.href) + '">' + img + "</a>" : img;
      }).join("");
      const rec = (t.wins != null) ? (t.wins + "-" + (t.losses || 0)) : "";
      return '<tr>' +
        '<td class="rk">' + t.power + "</td>" +
        '<td class="league-team-cell"><div class="league-faces">' + faces + "</div><div><strong>" + esc(t.name) + "</strong><small>" + esc(t.owner || "") + (rec ? " · " + rec : "") + "</small></div></td>" +
        '<td class="val">' + fmt(t.total) + "</td>" +
        '<td class="desk-only val">' + fmt(t.posSum.QB) + "</td>" +
        '<td class="desk-only val">' + fmt(t.posSum.RB) + "</td>" +
        '<td class="desk-only val">' + fmt(t.posSum.WR) + "</td>" +
        '<td class="desk-only val">' + fmt(t.posSum.TE) + "</td>" +
        "</tr>";
    }).join("");

    const cards = state.teams.map(function (t) {
      const faces = (t.faces || []).map(function (f) {
        const img = '<img src="' + esc(f.image) + '" alt="' + esc(f.name) + '" width="160" height="160" />';
        return '<div class="league-hero-face">' + (f.href ? '<a href="' + esc(f.href) + '">' + img + "</a>" : img) + "<span>" + esc(f.name) + "</span></div>";
      }).join("");
      const roster = t.assets.map(function (a) {
        const name = a.href ? '<a href="' + esc(a.href) + '">' + esc(a.name) + "</a>" : esc(a.name);
        return "<li><span>" + name + ' <small>' + esc(a.pos) + "</small></span><strong>" + (a.matched ? fmt(a.value) : "skip") + "</strong></li>";
      }).join("");
      const nPlayers = t.assets.filter(function (a) { return a.kind === "player"; }).length;
      const nPicks = t.assets.filter(function (a) { return a.kind === "pick"; }).length;
      const count = nPlayers + " player" + (nPlayers === 1 ? "" : "s") +
        (nPicks ? " · " + nPicks + " pick" + (nPicks === 1 ? "" : "s") : "");
      return '<article class="league-card">' +
        '<p class="kicker">#' + t.power + (t.wins != null ? " · " + t.wins + "-" + (t.losses || 0) : "") + "</p>" +
        "<h3>" + esc(t.name) + "</h3>" +
        '<p class="league-total">' + fmt(t.total) + "</p>" +
        '<div class="league-heroes">' + faces + "</div>" +
        '<p class="roster-count">' + count + "</p>" +
        "<ol>" + roster + "</ol></article>";
    }).join("");

    const adds = waivers().map(function (p, i) {
      const name = p.href ? '<a href="' + esc(p.href) + '">' + esc(p.name) + "</a>" : esc(p.name);
      const img = '<img class="face" src="' + esc(p.image) + '" alt="" width="28" height="28" />';
      return "<tr><td class=\"rk\">" + (i + 1) + "</td><td>" + img + name + (p.wire ? ' <small class="wire">wire</small>' : "") + "</td><td>" + esc(p.pos) + "</td><td>" + esc(p.team) + "</td><td class=\"val\">" + fmt(p.value) + "</td></tr>";
    }).join("");

    app.hidden = false;
    app.innerHTML =
      '<section class="league-head">' +
        "<p class=\"kicker\">" + esc(state.meta.platform) + " · " + esc(state.meta.season) + " · " + esc(state.meta.kind) + " · " + esc(state.meta.scoring) + "</p>" +
        "<h2>" + esc(state.meta.name) + "</h2>" +
        '<p class="note">' + state.teams.length + " teams. Full roster on each card. Values use the " + (state.mode === "sf" ? "Superflex Keep" : state.mode === "oneqb" ? "1QB Keep" : state.mode === "classic" ? "Classic" : "PPR Board") + " curve. Unranked roster names stay a skip.</p>" +
        '<div class="league-controls">' +
          '<div class="league-modes">' + modeBtns + "</div>" +
          (dynasty ? '<label class="league-toggle"><input type="checkbox" data-picks ' + (picksOn ? "checked" : "") + " /> Include draft picks</label>" : "") +
        "</div>" +
      "</section>" +
      '<section class="panel graph" aria-label="Team BK Value">' +
        '<p class="kicker">Power rankings</p><h3>Team BK Value</h3>' +
        '<div class="bar-chart">' + bars + "</div>" +
      "</section>" +
      '<section class="panel graph" aria-label="Value by position">' +
        '<p class="kicker">Mix</p><h3>Value by position</h3>' +
        '<p class="note stack-key"><span class="dot qb"></span>QB <span class="dot rb"></span>RB <span class="dot wr"></span>WR <span class="dot te"></span>TE <span class="dot pk"></span>Picks</p>' +
        '<div class="stack-chart">' + stacks + "</div>" +
      "</section>" +
      '<section class="panel">' +
        '<p class="kicker">Table</p><h3>Every roster</h3>' +
        '<div class="table-wrap"><table class="rank-table faces"><thead><tr><th>Rk</th><th>Team</th><th>BK Value</th><th class="desk-only">QB</th><th class="desk-only">RB</th><th class="desk-only">WR</th><th class="desk-only">TE</th></tr></thead><tbody>' + rows + "</tbody></table></div>" +
      "</section>" +
      '<section class="league-grid">' + cards + "</section>" +
      '<section class="panel">' +
        '<p class="kicker">Available</p><h3>Best leftover values</h3>' +
        '<p class="note">Ranked names not on any roster, sorted by the active curve. Wire marks a name that already sits on the Week 1 waiver mash.</p>' +
        '<div class="table-wrap"><table class="rank-table faces"><thead><tr><th>Rk</th><th>Player</th><th>Pos</th><th>Team</th><th>BK Value</th></tr></thead><tbody>' + adds + "</tbody></table></div>" +
      "</section>";
  }

  function showError(msg) {
    app.hidden = false;
    app.innerHTML = '<p class="league-error">' + esc(msg) + "</p>";
  }

  function applyDemo() {
    const demo = state.lookup.demo;
    if (!demo) throw new Error("Sample league missing.");
    state.meta = {
      name: demo.name,
      season: demo.season,
      kind: demo.kind,
      scoring: demo.scoring,
      platform: "Sample",
    };
    state.mode = demo.superflex ? "sf" : "oneqb";
    state.includePicks = true;
    state.teams = (demo.teams || []).map(function (t) {
      const raw = (t.sleeper_ids || []).map(function (id) {
        return { pack: packFromSleeper(id), name: "", pos: "" };
      });
      if (!raw.length) {
        (t.players || []).forEach(function (name) {
          raw.push({ pack: packFromName(name), name: name, pos: "" });
        });
      }
      return {
        id: t.id,
        name: t.name,
        owner: t.owner,
        wins: t.wins,
        losses: t.losses,
        fpts: 0,
        rawPlayers: raw,
        picks: [
          { season: "2027", round: 1 },
          { season: "2027", round: 2 },
          { season: "2027", round: 3 },
          { season: "2028", round: 1 },
          { season: "2028", round: 2 },
          { season: "2028", round: 3 },
          { season: "2029", round: 1 },
          { season: "2029", round: 2 },
          { season: "2029", round: 3 },
        ],
      };
    });
    paint();
    history.replaceState(null, "", "league.html?demo=1");
  }

  async function loadSleeper(id) {
    id = String(id || "").trim();
    if (!id) throw new Error("Enter a Sleeper league ID.");
    const urls = [
      SLEEPER + "/league/" + encodeURIComponent(id),
      SLEEPER + "/league/" + encodeURIComponent(id) + "/rosters",
      SLEEPER + "/league/" + encodeURIComponent(id) + "/users",
      SLEEPER + "/league/" + encodeURIComponent(id) + "/traded_picks",
    ];
    const parts = await Promise.all(urls.map(function (u) { return fetch(u); }));
    if (!parts[0].ok) throw new Error("Sleeper did not find that league. Check the ID and that the league is public.");
    const league = await parts[0].json();
    const rosters = parts[1].ok ? await parts[1].json() : [];
    const users = parts[2].ok ? await parts[2].json() : [];
    const traded = parts[3].ok ? await parts[3].json() : [];
    const byUser = {};
    (users || []).forEach(function (u) { byUser[u.user_id] = u; });
    const rec = ((league.scoring_settings) || {}).rec;
    const typ = ((league.settings) || {}).type;
    state.meta = {
      name: league.name || "Sleeper league",
      season: String(league.season || ""),
      kind: typ === 2 ? "dynasty" : typ === 1 ? "keeper" : "redraft",
      scoring: rec === 1 || rec === 1.0 ? "PPR" : rec === 0.5 ? "Half-PPR" : "Standard",
      platform: "Sleeper",
    };
    state.mode = detectMode(league);
    state.includePicks = state.meta.kind !== "redraft";
    const year = parseInt(league.season, 10) || 2026;
    const seasons = [year + 1, year + 2, year + 3];
    const rounds = Math.min(3, ((league.settings) || {}).draft_rounds || 3);
    const owned = {};
    (rosters || []).forEach(function (r) {
      owned[r.roster_id] = [];
      seasons.forEach(function (s) {
        for (let rd = 1; rd <= rounds; rd++) {
          owned[r.roster_id].push({ season: String(s), round: rd });
        }
      });
    });
    (traded || []).forEach(function (t) {
      const yr = parseInt(t.season, 10);
      if (seasons.indexOf(yr) === -1) return;
      if (t.round < 1 || t.round > rounds) return;
      const from = owned[t.roster_id] || [];
      const idx = from.findIndex(function (p) { return p.season === String(t.season) && p.round === t.round; });
      if (idx >= 0) from.splice(idx, 1);
      if (!owned[t.owner_id]) owned[t.owner_id] = [];
      owned[t.owner_id].push({ season: String(t.season), round: t.round });
    });
    state.teams = (rosters || []).map(function (r) {
      const user = byUser[r.owner_id] || {};
      const teamName = (user.metadata && user.metadata.team_name) || user.display_name || ("Roster " + r.roster_id);
      const ids = rosterIds(r);
      return {
        id: r.roster_id,
        name: teamName,
        owner: user.display_name || "",
        wins: (r.settings || {}).wins || 0,
        losses: (r.settings || {}).losses || 0,
        fpts: (r.settings || {}).fpts || 0,
        rawPlayers: ids.map(function (sid) {
          return { pack: packFromSleeper(sid), name: "", pos: "", sleeper: sid };
        }),
        picks: owned[r.roster_id] || [],
      };
    });
    paint();
    history.replaceState(null, "", "league.html?sleeper=" + encodeURIComponent(id));
  }

  form.addEventListener("click", async function (e) {
    const demo = e.target.closest("[data-demo]");
    const load = e.target.closest("[data-load]");
    if (!demo && !load) return;
    e.preventDefault();
    try {
      await loadLookup();
      if (demo) applyDemo();
      else await loadSleeper(document.getElementById("sleeper-id").value);
    } catch (err) {
      showError(err.message || "Could not load that league.");
    }
  });

  form.addEventListener("submit", async function (e) {
    e.preventDefault();
    try {
      await loadLookup();
      await loadSleeper(document.getElementById("sleeper-id").value);
    } catch (err) {
      showError(err.message || "Could not load that league.");
    }
  });

  app.addEventListener("change", function (e) {
    if (e.target.matches("[data-picks]")) {
      state.includePicks = !!e.target.checked;
      paint();
    }
  });
  app.addEventListener("click", function (e) {
    const chip = e.target.closest("[data-mode]");
    if (!chip) return;
    state.mode = chip.getAttribute("data-mode");
    paint();
  });

  const params = new URLSearchParams(location.search);
  loadLookup().then(function () {
    if (params.get("demo")) applyDemo();
    else if (params.get("sleeper")) {
      document.getElementById("sleeper-id").value = params.get("sleeper");
      return loadSleeper(params.get("sleeper"));
    }
  }).catch(function () {});
})();
