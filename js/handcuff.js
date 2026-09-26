(function () {
  const root = document.getElementById("handcuff-app");
  if (!root) return;

  const state = {
    lookup: null,
    pending: null,
    room: null,
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

  async function load() {
    if (state.lookup) return state.lookup;
    const res = await fetch("data/handcuff-lookup.json");
    state.lookup = await res.json();
    return state.lookup;
  }

  function rooms() {
    return (state.lookup && state.lookup.rooms) || [];
  }

  function catalog() {
    return (state.lookup && state.lookup.players) || [];
  }

  function roomById(id) {
    return rooms().find(function (r) { return r.id === id; }) || null;
  }

  function search(q) {
    const src = catalog();
    q = (q || "").trim().toLowerCase();
    const pool = q
      ? src.filter(function (p) {
        return (p.name + " " + p.pos + " " + p.team).toLowerCase().indexOf(q) !== -1;
      })
      : src.filter(function (p) { return p.role === "starter"; });
    const seen = {};
    const out = [];
    for (let i = 0; i < pool.length; i++) {
      const p = pool[i];
      if (seen[p.room]) continue;
      seen[p.room] = 1;
      out.push(p);
      if (out.length >= 12) break;
    }
    return out;
  }

  function paintHits() {
    const q = root.querySelector("[data-q]").value;
    const box = root.querySelector("[data-hits]");
    const hits = search(q);
    box.innerHTML = hits.map(function (p) {
      const room = roomById(p.room);
      const on = p.room === state.pending ? " picked" : "";
      const heir = room ? room.heir.name : "";
      return (
        '<button type="button" class="trade-hit' + on + '" data-id="' + esc(p.room) + '">' +
        "<strong>" + esc(p.name) + "</strong>" +
        "<span>" + esc(p.pos) + " " + esc(p.team) +
        (heir ? " · cuff " + esc(heir) : "") +
        (room && room.status && room.status !== "Active" ? " · " + esc(room.status) : "") +
        "</span></button>"
      );
    }).join("") || "<p class='note'>No matches.</p>";
  }

  function sideLine(p) {
    const bits = [];
    if (p.keep_pos) bits.push(p.keep_pos + " Keep" + (p.keep ? " #" + p.keep : ""));
    if (p.board_pos) bits.push(p.board_pos + " Board" + (p.board ? " #" + p.board : ""));
    if (p.clock && p.clock !== "Off") bits.push(p.clock);
    return bits.join(" · ");
  }

  function paintRoom() {
    const room = state.room;
    const starter = room && room.starter;
    const heir = room && room.heir;
    root.querySelector("[data-starter-name]").textContent = starter ? starter.name : "Name him";
    root.querySelector("[data-starter-total]").textContent = starter ? fmt(starter.board_val) : "0";
    root.querySelector("[data-starter-meta]").textContent = starter
      ? sideLine(starter) + " · Board value"
      : "Keep and Board on the starter.";
    root.querySelector("[data-heir-name]").textContent = heir ? heir.name : "Next back";
    root.querySelector("[data-heir-total]").textContent = heir ? fmt(heir.board_val) : "0";
    root.querySelector("[data-heir-meta]").textContent = heir
      ? sideLine(heir) + " · Board value"
      : "Keep and Board on the handcuff.";
    root.querySelector("[data-hole-total]").textContent = room ? fmt(room.hole) : "0";
    root.querySelector("[data-verdict]").textContent = room
      ? room.verdict
      : "Search a running back. The cuff stays dark until a name is in.";
    const holeBox = root.querySelector("[data-hole]");
    holeBox.className = "split-clock window" + (room && room.tag ? " t-" + room.tag.toLowerCase().replace(/\s+/g, "-") : "");
    const status = [];
    if (room && room.status) status.push(room.status);
    if (room && room.team) status.push(room.team + " RB");
    root.querySelector("[data-status]").textContent = status.join(" · ");

    const ul = root.querySelector("[data-line]");
    if (!room) {
      ul.innerHTML = '<li class="empty">The backfield is empty. Search a running back.</li>';
      return;
    }
    const line = [room.starter.name].concat(room.behind || []);
    ul.innerHTML = line.map(function (name, i) {
      const lab = i === 0 ? "Starter" : (i === 1 ? "Cuff" : "Next");
      return (
        "<li><span><strong>" + esc(name) + "</strong><small>" + lab +
        (i === 0 && room.status && room.status !== "Active" ? " · " + esc(room.status) : "") +
        "</small></span></li>"
      );
    }).join("");
  }

  function paint() {
    paintHits();
    paintRoom();
  }

  function openRoom(id) {
    state.room = roomById(id);
    paint();
  }

  function loadSample(key) {
    const names = ((state.lookup && state.lookup.samples) || {})[key] || [];
    const byName = {};
    catalog().forEach(function (p) { byName[norm(p.name)] = p; });
    for (let i = 0; i < names.length; i++) {
      const p = byName[norm(names[i])];
      if (p) {
        state.pending = p.room;
        openRoom(p.room);
        return;
      }
    }
    state.room = null;
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
    if (e.target.closest("[data-open]")) {
      if (state.pending) openRoom(state.pending);
      return;
    }
    const sample = e.target.closest("[data-sample]");
    if (sample) {
      loadSample(sample.getAttribute("data-sample"));
      return;
    }
    if (e.target.closest("[data-clear]")) {
      state.pending = null;
      state.room = null;
      paint();
    }
  });

  load().then(paint).catch(function () {
    root.querySelector("[data-verdict]").textContent = "The cuff could not load. Refresh the page.";
  });
})();
