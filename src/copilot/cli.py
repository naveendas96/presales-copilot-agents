from __future__ import annotations

import argparse
from pathlib import Path

from .graph import build


def main() -> None:
    p = argparse.ArgumentParser("copilot")
    p.add_argument("rfp")
    p.add_argument("-o", "--out", default="out/proposal.md")
    a = p.parse_args()
    s = build().invoke({"rfp": Path(a.rfp).read_text()})
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    Path(a.out).write_text(s["proposal"])
    cov = sum(d["capability"] != "UNMAPPED" for d in s["design"])
    print(f"requirements={len(s['requirements'])} covered={cov} total_days={s['estimate']['total_days']} "
          f"risks={len(s['risks'])} open_items={len(s['critique'])} -> {a.out}")


if __name__ == "__main__":
    main()
