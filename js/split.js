(function () {
  const root = document.getElementById("split-app");
  if (!root) return;

  const state = {
    lookup: null,
    room: [],
    pending: null,
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

  function byName(name) {
    const src = (state.lookup && state.lookup.players) || [];
    const key = norm(name);
    for (let i = 0; i < src.length; i++) {
      if (norm(src[i].name) === key) return src[i];
    }
    return null;
  }

  async function load() {
    if (state.lookup) return state.lookup;
    const res = await fetch("data/split-lookup.json");
    state.lookup = await res.json();
    return state.lookup;
  }

  function search(q) {
    const catalog = (state.lookup && state.lookup.players) || [];
    q = (q || "").trim().toLowerCase();
    const pool = q
      ? catalog.filter(function (p) {
        return (p.name + " " + p.pos + " " + p.team).toLowerCase().indexOf(q) !== -1;
      })
      : catalog;
    return pool.slice(0, 12);
  }

  function windowOf(players) {
    if (!players.length) {
      return {
        year: null,
        verdict: "Add names from the search. The two clocks stay dark until a room is in.",
        keep: 0,
        board: 0,
        age: null,
      };
    }
    let kv = 0;
    let bv = 0;
    const ages = [];
    players.forEach(function (p) {
      kv += p.keep_val || 0;
      bv += p.board_val || 0;
      if (p.age != null && p.age !== "") ages.push(Number(p.age));
    });
    const avgAge = ages.length ? ages.reduce(function (a, b) { return a + b; }, 0) / ages.length : null;
    const total = kv + bv;
    const boardShare = total ? bv / total : 0.5;
    const ageTerm = avgAge == null ? 0 : (avgAge - 25.5) / 8;
    const score = (boardShare - 0.5) * 2.2 + ageTerm;
    let year = 2027;
    let verdict = "This room can win soon and still has years.";
    if (score >= 0.28) {
      year = 2026;
      verdict = "This room is trying to win 2026.";
    } else if (score <= -0.28) {
      year = 2028;
      verdict = "This room is built for 2028.";
    }
    return { year: year, verdict: verdict, keep: kv, board: bv, age: avgAge };
  }

  function paintHits() {
    const q = root.querySelector("[data-q]").value;
    const box = root.querySelector("[data-hits]");
    const hits = search(q);
    box.innerHTML = hits.map(function (p) {
      const on = p.id === state.pending ? " picked" : "";
      return (
        '<button type="button" class="trade-hit' + on + '" data-id="' + esc(p.id) + '">' +
        "<strong>" + esc(p.name) + "</strong>" +
        "<span>" + esc(p.keep_pos || p.pos) + " Keep #" + p.keep +
        " · " + esc(p.board_pos || p.pos) + " Board #" + p.board + "</span>" +
        "</button>"
      );
    }).join("") || "<p class='note'>No matches.</p>";
  }

  function paintRoom() {
    const ul = root.querySelector("[data-room]");
    if (!state.room.length) {
      ul.innerHTML = '<li class="empty">The room is empty. Search a name.</li>';
      return;
    }
    ul.innerHTML = state.room.map(function (p) {
      return (
        "<li>" +
        "<span><strong>" + esc(p.name) + "</strong><small>" +
        esc(p.keep_pos || p.pos) + " Keep #" + p.keep + " · " +
        esc(p.board_pos || p.pos) + " Board #" + p.board +
        (p.age ? " · age " + p.age : "") +
        "</small></span>" +
        '<button type="button" data-remove="' + esc(p.id) + '" aria-label="Remove">×</button>' +
        "</li>"
      );
    }).join("");
  }

  function paintWindow() {
    const w = windowOf(state.room);
    root.querySelector("[data-keep-total]").textContent = fmt(w.keep);
    root.querySelector("[data-board-total]").textContent = fmt(w.board);
    const yearEl = root.querySelector("[data-year]");
    yearEl.textContent = w.year ? String(w.year) : "Year";
    root.querySelector("[data-verdict]").textContent = w.verdict;
    const box = root.querySelector("[data-window]");
    box.className = "split-clock window" + (w.year ? " y" + w.year : "");
    const meta = [];
    if (w.age != null) meta.push("Age " + w.age.toFixed(1));
    if (state.room.length) meta.push(state.room.length + (state.room.length === 1 ? " name" : " names"));
    root.querySelector("[data-meta]").textContent = meta.join(" · ");
  }

  function paint() {
    paintHits();
    paintRoom();
    paintWindow();
  }

  function add(id) {
    const catalog = (state.lookup && state.lookup.players) || [];
    const p = catalog.find(function (x) { return x.id === id; });
    if (!p) return;
    if (state.room.some(function (x) { return x.id === p.id; })) return;
    state.room.push(p);
    paint();
  }

  function loadSample(key) {
    const names = ((state.lookup && state.lookup.samples) || {})[key] || [];
    state.room = [];
    names.forEach(function (name) {
      const p = byName(name);
      if (p) state.room.push(p);
    });
    paint();
  }

  root.addEventListener("input", function (e) {
    if (e.target && e.target.hasAttribute("data-q")) paintHits();
  });
  root.addEventListener("click", function (e) {
    const hit = e.target.closest("[data-id]");
    if (hit && hit.classList.contains("trade-hit")) {
      state.pending = hit.getAttribute("data-id");
      paintHits();
      return;
    }
    if (e.target.closest("[data-add]")) {
      if (state.pending) add(state.pending);
      return;
    }
    const sample = e.target.closest("[data-sample]");
    if (sample) {
      loadSample(sample.getAttribute("data-sample"));
      return;
    }
    if (e.target.closest("[data-clear]")) {
      state.room = [];
      paint();
      return;
    }
    const rm = e.target.closest("[data-remove]");
    if (rm) {
      const id = rm.getAttribute("data-remove");
      state.room = state.room.filter(function (p) { return p.id !== id; });
      paint();
    }
  });

  load().then(paint).catch(function () {
    root.querySelector("[data-verdict]").textContent = "The clocks could not load. Refresh the page.";
  });
})();
