"""Touches and Targets: 2025 Sleeper counting stats plus Keep and Board BK Value."""
from __future__ import annotations

import json
from pathlib import Path

from seo import also_on_desk, breadcrumbs, breadcrumb_jsonld, rank_search_bar, rank_search_key

ROOT = Path(__file__).resolve().parents[1]
USAGE_PATH = ROOT / "data/weekly/usage-2025.json"


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
    """One row per skill player with 2025 volume. Default sort is targets."""
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


def _sort_js() -> str:
    return """<script>
(function () {
  var box = document.getElementById("touch-sort");
  var table = document.querySelector("table.touches-table");
  if (!box || !table) return;
  function paint() {
    var btn = box.querySelector("button.active");
    var key = btn ? btn.getAttribute("data-sort") : "targets";
    var tbody = table.querySelector("tbody");
    var rows = Array.prototype.slice.call(tbody.querySelectorAll("tr"));
    rows.sort(function (a, b) {
      var av = Number(a.getAttribute("data-" + key) || 0);
      var bv = Number(b.getAttribute("data-" + key) || 0);
      if (bv !== av) return bv - av;
      return String(a.getAttribute("data-name") || "").localeCompare(String(b.getAttribute("data-name") || ""));
    });
    rows.forEach(function (tr, i) {
      var rk = tr.querySelector(".c-rank");
      if (rk) rk.textContent = String(i + 1);
      tbody.appendChild(tr);
    });
    if (window.applyRankFilter) window.applyRankFilter();
  }
  box.addEventListener("click", function (e) {
    var b = e.target.closest("button");
    if (!b) return;
    box.querySelectorAll("button").forEach(function (x) { x.classList.remove("active"); });
    b.classList.add("active");
    paint();
  });
})();
</script>
"""


def _table(rows) -> str:
    from build_site import esc

    body = []
    for r in rows:
        pos = r.get("pos") or ""
        team = r.get("team") or ""
        dn = rank_search_key(r.get("name"), pos, team)
        face = (
            f'<img class="face" src="{esc(r["_face"])}" alt="{esc(r["name"])} headshot" '
            f'width="28" height="28" loading="lazy" />'
        )
        meta = (
            f'<div class="row-meta"><span class="pos {esc(pos)}">{esc(pos)}</span>'
            f" · {esc(team)}</div>"
        )
        stack = f'<span class="name-stack">{r["_anchor"]}{meta}</span>'
        keep_cls = "keep-val" if r["keep_value"] else "skip-val"
        board_cls = "board-val" if r["board_value"] else "skip-val"
        body.append(
            f'<tr data-pos="{esc(pos)}" data-name="{dn}" '
            f'data-targets="{r["targets"]}" data-touches="{r["rushes"]}" '
            f'data-rec="{r["rec"]}" data-td="{r["tds"]}">'
            f'<td class="rk c-rank">{r["bk"]}</td>'
            f'<td class="c-name">{face}{stack}</td>'
            f'<td class="c-pos"><span class="pos {esc(pos)}">{esc(pos)}</span></td>'
            f'<td class="c-team">{esc(team)}</td>'
            f'<td class="c-stat">{r["targets"]}</td>'
            f'<td class="c-stat">{r["rushes"]}</td>'
            f'<td class="c-stat">{r["rec"]}</td>'
            f'<td class="c-stat">{r["tds"]}</td>'
            f'<td class="c-val {keep_cls}">{esc(r["keep_txt"])}</td>'
            f'<td class="c-val {board_cls}">{esc(r["board_txt"])}</td>'
            "</tr>"
        )
    return (
        '<div class="table-wrap"><table class="rank-table faces touches-table">'
        "<thead><tr>"
        "<th>BK</th><th>Player</th><th>Pos</th><th>Team</th>"
        "<th>Targets</th><th>Touches</th><th>Rec</th><th>TDs</th>"
        '<th class="c-val">Keep</th><th class="c-val">Board</th>'
        "</tr></thead>"
        f"<tbody>{''.join(body)}</tbody></table></div>"
    )


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
    body = f"""
    <p class="kicker">2025 NFL season · Counting stats · {len(rows)} names</p>
    <h1>Touches and Targets</h1>
    <p class="note">Sleeper 2025 regular-season totals. Touches are rushes. Receptions sit in their own column. TDs are rushing plus receiving, not passing. Keep is Superflex dynasty BK Value. Board is redraft PPR BK Value. Unranked on a board is a skip. Sort with the buttons. Filter by position with the chips.</p>
    {rank_search_bar(chips)}
    {sorts}
    <div class="panel">{_table(rows)}</div>
    <section class="sources">
      <p class="kicker">Source</p>
      <h2>Where the numbers come from.</h2>
      <ul>
        <li><a href="https://sleeper.com/">Sleeper</a> NFL regular-season stats, 2025. Targets, rushes, receptions, and skill TDs.</li>
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
            extra_js=chip_js + _sort_js(),
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
