#!/usr/bin/env python3
"""Text for the GitHub issue opened when a scheduled Ball Keep job fails.

The workflow in .github/workflows/alert-on-failure.yml posts this with the
Actions token. Running this file prints the body and does not open an issue.
"""
from __future__ import annotations

WATCHED = (
    "BK News",
    "Weekly check (Monday and Tuesday)",
    "Daily site rebuild",
)


def issue_title(workflow: str, test: bool = False) -> str:
    if test:
        return "Test: Ball Keep failure alert"
    return f"Ball Keep job failed: {workflow}"


def issue_body(
    workflow: str,
    run_url: str,
    conclusion: str,
    head_sha: str = "",
    test: bool = False,
) -> str:
    if test:
        return (
            "This is a test of the scheduled-job alert. Close it.\n\n"
            "A real failure of BK News, the Monday/Tuesday ranks job, or the "
            "daily rebuild opens an issue with this same label and assigns the "
            "repository owner. A stale-data failure is a failed run of "
            "`scripts/check_freshness.py`, so it uses this path too.\n\n"
            "To test again: Actions, Alert when a scheduled job fails, Run workflow."
        )
    sha = f"\nCommit: `{head_sha}`" if head_sha else ""
    return (
        f"`{workflow}` finished with **{conclusion}**.{sha}\n\n"
        f"Run: {run_url}\n\n"
        "The ranks job and the news job used to fail for days without a ping. "
        "This issue is the ping. A freshness check that exits 1 is a failed run "
        "of `scripts/check_freshness.py`, so a stale wire or a stale scrape opens one of these too.\n\n"
        "Close this after the next green run."
    )


def main() -> int:
    print(issue_title(WATCHED[0]))
    print(issue_body(WATCHED[0], "https://github.com/balsalah51/BallKeep/actions", "failure", "abc"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
