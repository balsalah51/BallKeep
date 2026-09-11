"""Touches and Targets: 2026 Sleeper counting stats plus Keep and Board BK Value."""
from __future__ import annotations

import json
from pathlib import Path

from seo import also_on_desk, breadcrumbs, breadcrumb_jsonld, rank_search_bar, rank_search_key

ROOT = Path(__file__).resolve().parents[1]
USAGE_PATH = ROOT / "data/weekly/usage-2026.json"
SEASON = 2026


def _num(v) -> int:
    if v in (None, "", "-"):
        return 0
    try:
        return int(float(v))
    except (TypeError, ValueError):
        return 0


def _player_href(name: str, key: str, media: dict) -> str:
    from build_site import PLAYER_PAGES, player_url, slugify

    href = player_url(name)
    if href:
        return href
    slug = (media.get(key) or {}).get("slug") or PLAYER_PAGES.get(key) or slugify(name)
    if slug and (ROOT / "players" / f"{slug}.html").exists():
        return f"players/{slug}.html"
    return ""


def load_usage_rows(keep, board, media=None):
    """One row per skill player with 2026 volume. Default sort is targets."""
    from build_site import esc, face_src, fmt_val, norm_name

    media = media or {}
    raw = {}
    if USAGE_PATH.exists():
        blob = json.loads(USAGE_PATH.read_text())
        raw = blob.get("players") or {}

    keep_by = {}
    for r in keep or []:
        key = r.get("key") or norm_name(r.get("name") or "")
        if key:
            keep_by[key] = r
    board_by = {}
    for r in board or []:
        key = r.get("key") or norm_name(r.get("name") or "")
        if key:
            board_by[key] = r

    rows = []
    for name, st in raw.items():
        if not isinstance(st, dict):
            continue
        pos = st.get("pos") or ""
        if pos not in {"QB", "RB", "WR", "TE"}:
            continue
        targets = _num(st.get("rec_tgt"))
        rushes = _num(st.get("rush_att"))
        rec = _num(st.get("rec"))
        tds = _num(st.get("rush_td")) + _num(st.get("rec_td"))
        if not (targets or rushes or rec or tds):
            continue
        key = norm_name(name)
        med = media.get(key) or {}
        kr = keep_by.get(key) or {}
        br = board_by.get(key) or {}
        row = {
            "key": key,
            "name": st.get("name") or name,
            "pos": pos or med.get("pos") or "",
            "team": st.get("team") or med.get("team") or "",
            "targets": targets,
            "rushes": rushes,
            "rec": rec,
            "tds": tds,
            "gp": _num(st.get("gp")),
            "keep_value": kr.get("value") or 0,
            "board_value": br.get("value") or 0,
            "keep_bk": kr.get("bk") or 0,
            "board_bk": br.get("bk") or 0,
        }
        row["keep_txt"] = fmt_val(row["keep_value"]) if row["keep_value"] else "skip"
        row["board_txt"] = fmt_val(row["board_value"]) if row["board_value"] else "skip"
        row["_face"] = face_src(row, media)
        href = _player_href(row["name"], key, media)
        if href:
            row["_anchor"] = (
                f'<a class="player-link" href="{esc(href)}"><strong>{esc(row["name"])}</strong></a>'
            )
        else:
            row["_anchor"] = f"<strong>{esc(row['name'])}</strong>"
        rows.append(row)

    rows.sort(key=lambda r: (-r["targets"], -r["rushes"], -r["rec"], -r["tds"], r["name"]))
    for i, r in enumerate(rows, 1):
        r["bk"] = i
    return rows


def _page_js() -> str:
    return """<script>
(function () {
  var box = document.getElementById("touch-sort");
  var list = document.getElementById("touch-list");
  if (!list) return;
  function rows() {
    return Array.prototype.slice.call(list.querySelectorAll(".touch-row"));
  }
  window.applyRankFilter = function () {
    var inp = document.querySelector(".rank-search-input");
    var q = inp ? String(inp.value || "").trim().toLowerCase() : "";
    var posBtn = document.querySelector("#touch-pos button.active");
    var pos = posBtn ? String(posBtn.getAttribute("data-pos") || "all").toLowerCase() : "all";
    rows().forEach(function (row) {
      var hay = (row.getAttribute("data-name") || "").toLowerCase();
      var nameOk = !q || hay.indexOf(q) !== -1;
      var rowPos = (row.getAttribute("data-pos") || "").toLowerCase();
      var posOk = pos === "all" || rowPos === pos;
      row.style.display = (nameOk && posOk) ? "" : "none";
    });
  };
  function paint() {
    var btn = box ? box.querySelector("button.active") : null;
    var key = btn ? btn.getAttribute("data-sort") : "targets";
    var ordered = rows().sort(function (a, b) {
      var av = Number(a.getAttribute("data-" + key) || 0);
      var bv = Number(b.getAttribute("data-" + key) || 0);
      if (bv !== av) return bv - av;
      return String(a.getAttribute("data-name") || "").localeCompare(String(b.getAttribute("data-name") || ""));
    });
    ordered.forEach(function (row, i) {
      var rk = row.querySelector(".c-rank");
      if (rk) rk.textContent = String(i + 1);
      list.appendChild(row);
    });
    if (window.applyRankFilter) window.applyRankFilter();
  }
  if (box) box.addEventListener("click", function (e) {
    var b = e.target.closest("button");
    if (!b) return;
    box.querySelectorAll("button").forEach(function (x) { x.classList.remove("active"); });
    b.classList.add("active");
    paint();
  });
})();
</script>
"""


def _stat(lab: str, val, extra="") -> str:
    from build_site import esc

    cls = f"touch-stat {extra}".strip()
    return (
        f'<div class="{cls}">'
        f'<span class="stat-lab">{esc(lab)}</span>'
        f'<span class="stat-num">{esc(str(val))}</span>'
        "</div>"
    )


def _cards(rows) -> str:
    from build_site import esc

    if not rows:
        return (
            '<p class="note">No 2026 regular-season targets, rushes, receptions, or skill TDs on the tape yet. '
            "Week 1 is still filling in.</p>"
        )
    body = []
    for r in rows:
        pos = r.get("pos") or ""
        team = r.get("team") or ""
        dn = rank_search_key(r.get("name"), pos, team)
        face = (
            f'<img class="face" src="{esc(r["_face"])}" alt="{esc(r["name"])} headshot" '
            f'width="40" height="40" loading="lazy" />'
        )
        meta = (
            f'<div class="row-meta"><span class="pos {esc(pos)}">{esc(pos)}</span>'
            f" · {esc(team)}</div>"
        )
        keep_cls = "keep-val" if r["keep_value"] else "skip-val"
        board_cls = "board-val" if r["board_value"] else "skip-val"
        body.append(
            f'<article class="touch-row" data-pos="{esc(pos)}" data-name="{dn}" '
            f'data-targets="{r["targets"]}" data-touches="{r["rushes"]}" '
            f'data-rec="{r["rec"]}" data-td="{r["tds"]}">'
            f'<div class="touch-who">'
            f'<span class="rk c-rank">{r["bk"]}</span>'
            f"{face}"
            f'<span class="name-stack">{r["_anchor"]}{meta}</span>'
            f"</div>"
            f'<div class="touch-stats">'
            f'{_stat("Targets", r["targets"])}'
            f'{_stat("Touches", r["rushes"])}'
            f'{_stat("Rec", r["rec"])}'
            f'{_stat("TDs", r["tds"])}'
            f"</div>"
            f'<div class="touch-bk">'
            f'{_stat("Keep", r["keep_txt"], keep_cls)}'
            f'{_stat("Board", r["board_txt"], board_cls)}'
            f"</div>"
            "</article>"
        )
    return f'<div class="touches-list" id="touch-list">{"".join(body)}</div>'


def write_touches_page(b, keep, board, media):
    from build_site import pos_filter

    rows = load_usage_rows(keep, board, media)
    chips, chip_js = pos_filter("touch-pos")
    sorts = (
        '<div class="filters sort-bar" id="touch-sort" role="group" aria-label="Sort counting stats">'
        '<button type="button" class="active" data-sort="targets">Targets</button>'
        '<button type="button" data-sort="touches">Touches</button>'
        '<button type="button" data-sort="rec">Receptions</button>'
        '<button type="button" data-sort="td">TDs</button>'
        "</div>"
    )
    extra = also_on_desk(b.FB_ALSO.get("touches.html") or [])
    count = f"{len(rows)} names" if rows else "no names yet"
    body = f"""
    <p class="kicker">{SEASON} NFL season · Week 1 so far · {count}</p>
    <h1>Touches and Targets</h1>
    <p class="note">Sleeper {SEASON} regular-season totals only. Early tape. Each number sits on its own label. Touches are rushes. Receptions sit in their own box. TDs are rushing plus receiving, not passing. Keep is Superflex dynasty BK Value. Board is redraft PPR BK Value. Unranked on a board is a skip. Sort with the buttons. Filter by position with the chips.</p>
    {rank_search_bar(chips)}
    {sorts}
    <div class="panel touches-panel">{_cards(rows)}</div>
    <section class="sources">
      <p class="kicker">Source</p>
      <h2>Where the numbers come from.</h2>
      <ul>
        <li><a href="https://sleeper.com/">Sleeper</a> NFL regular-season stats, {SEASON}. Targets, rushes, receptions, and skill TDs.</li>
        <li>Keep BK Value from <a href="the-keep.html">The Keep</a>. Board BK Value from <a href="board.html">The Board</a>.</li>
      </ul>
    </section>
    {extra}
    """
    b.write(
        "touches.html",
        b.page(
            "Touches and Targets",
            "touches.html",
            body,
            extra_js=chip_js + _page_js(),
            crumbs=breadcrumbs([
                ("Ball Keep", "index.html"),
                ("Touches and Targets", None),
            ]),
            extra_jsonld=[
                breadcrumb_jsonld([
                    ("Ball Keep", "https://ballkeep.com/"),
                    ("Touches and Targets", "https://ballkeep.com/touches.html"),
                ]),
            ],
        ),
    )
    return rows
