"""Fetch jobs from the command line (or a scheduled task): python -m jobsearch.fetch"""

from jobsearch.config import load_settings
from jobsearch.db import session_scope
from jobsearch.pipeline import fetch_all


def main() -> None:
    with session_scope() as session:
        report = fetch_all(session, load_settings())
    for r in report.sources:
        line = f"{r.source}: {r.fetched} fetched, {r.new} new, {r.merged} merged, {r.too_old} too old"
        if r.closed:
            line += f", {r.closed} closed"
        print(line + (f"  [error: {r.error}]" if r.error else ""))
    print(f"Total new: {report.new}. Archived: {report.archived}.")


if __name__ == "__main__":
    main()
