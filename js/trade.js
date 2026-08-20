(function () {
  const data = window.BK_TRADE;
  if (!data) return;

  const catalog = (data.players || []).concat(data.picks || []);
  const byId = Object.fromEntries(catalog.map((p) => [p.id, p]));
  const state = { a: [], b: [] };
  let pending = catalog[0] ? catalog[0].id : null;
  const root = document.getElementById("trade-app");
  if (!root) return;

  function fmt(n) {
    return Math.round(n).toLocaleString("en-US");
  }

  function meta(p) {
    return p.pos === "PICK" ? "Pick" : `${p.pos} ${p.team}`.trim();
  }

  function search(q) {
    q = (q || "").trim().toLowerCase();
    const pool = q
      ? catalog.filter((p) => (p.name + " " + p.pos + " " + p.team).toLowerCase().indexOf(q) !== -1)
      : catalog;
    return pool.slice(0, 16);
  }

  function total(side) {
    return state[side].reduce((sum, id) => sum + (byId[id].value || 0), 0);
  }

  function add(side, id) {
    if (!id || !byId[id] || state[side].indexOf(id) !== -1) return;
    state[side].push(id);
    paint();
  }

  function paintHits() {
    const q = root.querySelector("[data-q]").value;
    const box = root.querySelector("[data-hits]");
    box.innerHTML = search(q).map((p) => {
      const on = p.id === pending ? " picked" : "";
      return `<button type="button" class="trade-hit${on}" data-id="${p.id}">
        <strong>${p.name}</strong>
        <span>${meta(p)} · Rank ${p.rank} · ${fmt(p.value)}</span>
      </button>`;
    }).join("") || "<p class='note'>No matches.</p>";
  }

  function paintSide(key) {
    const ul = root.querySelector(`[data-list="${key}"]`);
    if (!state[key].length) {
      ul.innerHTML = '<li class="empty">Add names from search.</li>';
    } else {
      ul.innerHTML = state[key].map((id) => {
        const p = byId[id];
        return `<li>
          <span><strong>${p.name}</strong><small>${meta(p)} · #${p.rank} · ${fmt(p.value)}</small></span>
          <button type="button" data-remove="${key}" data-id="${p.id}" aria-label="Remove">×</button>
        </li>`;
      }).join("");
    }
    root.querySelector(`[data-total="${key}"]`).textContent = fmt(total(key));
  }

  function paintVerdict() {
    const a = total("a");
    const b = total("b");
    const diff = a - b;
    const pct = Math.abs(diff) / Math.max(a, b, 1);
    let label = "Fair Trade";
    let cls = "fair";
    if (a && b && pct > 0.08) {
      label = diff > 0 ? "Side A Wins" : "Side B Wins";
      cls = diff > 0 ? "a" : "b";
    }
    const gap = diff === 0 ? "Even" : (diff > 0 ? `A +${fmt(diff)}` : `B +${fmt(-diff)}`);
    const box = root.querySelector("[data-verdict]");
    box.className = "trade-verdict " + cls;
    box.innerHTML = `<p class="kicker">Result</p><h3>${label}</h3><p>${fmt(a)} vs ${fmt(b)} · ${gap}</p>`;
  }

  function paint() {
    paintHits();
    paintSide("a");
    paintSide("b");
    paintVerdict();
  }

  root.innerHTML = `
    <div class="trade-search">
      <label for="trade-q">Search This Board</label>
      <input id="trade-q" data-q type="search" placeholder="Player or pick…" autocomplete="off" />
      <div class="trade-hits" data-hits></div>
      <p class="note">Click a name, then send it to a side. Values are Ball Keep Value from this list's rank.</p>
      <div class="trade-add-btns">
        <button type="button" class="cta" data-to="a">Add to Side A</button>
        <button type="button" class="cta alt" data-to="b">Add to Side B</button>
      </div>
    </div>
    <div class="trade-board">
      <section class="trade-side">
        <header><h3>Side A</h3><p class="trade-total" data-total="a">0</p></header>
        <ul class="trade-list" data-list="a"></ul>
        <button type="button" class="trade-clear" data-clear="a">Clear</button>
      </section>
      <section class="trade-side">
        <header><h3>Side B</h3><p class="trade-total" data-total="b">0</p></header>
        <ul class="trade-list" data-list="b"></ul>
        <button type="button" class="trade-clear" data-clear="b">Clear</button>
      </section>
    </div>
    <div class="trade-verdict fair" data-verdict></div>
  `;

  root.querySelector("[data-q]").addEventListener("input", paintHits);
  root.addEventListener("click", (e) => {
    const hit = e.target.closest(".trade-hit");
    if (hit) {
      pending = hit.getAttribute("data-id");
      paintHits();
      return;
    }
    const to = e.target.closest("[data-to]");
    if (to) {
      add(to.getAttribute("data-to"), pending);
      return;
    }
    const rm = e.target.closest("[data-remove]");
    if (rm) {
      const side = rm.getAttribute("data-remove");
      const id = rm.getAttribute("data-id");
      state[side] = state[side].filter((x) => x !== id);
      paint();
      return;
    }
    const clr = e.target.closest("[data-clear]");
    if (clr) {
      state[clr.getAttribute("data-clear")] = [];
      paint();
    }
  });

  paint();
})();
