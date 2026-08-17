"""Ad-hoc scanner for the AWIP monolithic report.json.

Reads sections[].visualContainers[] and prints a per-page CSV-ish summary.
"""

import json
import sys
import re
from pathlib import Path


REPORT = Path(r"C:/Users/nefgt/Documents/Kingspan/PowerBI-SAP/AWIP_Commercial_Sales.PBIP/AWIP_Commercial_Sales.Report/report.json")


def extract_title(cfg):
    m = re.search(r'"text"\s*:\s*\{\s*"expr"\s*:\s*\{\s*"Literal"\s*:\s*\{\s*"Value"\s*:\s*"\'([^\']*)\'"', cfg)
    if m:
        return m.group(1)
    return ""


def extract_query_refs(cfg):
    return re.findall(r'"queryRef"\s*:\s*"([^"]+)"', cfg)


def extract_tables(cfg):
    return set(re.findall(r'"Entity"\s*:\s*"([^"]+)"', cfg))


def main():
    r = json.loads(REPORT.read_text(encoding="utf-8"))
    print(f"total sections: {len(r['sections'])}")
    print()
    for s in sorted(r["sections"], key=lambda x: x.get("ordinal", 0)):
        vcs = s.get("visualContainers", [])
        # Detect page-level hidden state
        hidden = ""
        try:
            page_cfg = json.loads(s.get("config", "{}") or "{}")
            if isinstance(page_cfg, dict):
                # sometimes displayOption drives hidden state
                pass
        except Exception:
            pass
        do = s.get("displayOption")
        print(f"=== PAGE ord={s.get('ordinal')} name={s.get('displayName')!r} id={s.get('name')} visuals={len(vcs)} displayOption={do} ===")
        for i, vc in enumerate(vcs):
            cfg = vc.get("config", "") or ""
            try:
                cfg_obj = json.loads(cfg)
            except Exception:
                cfg_obj = {}
            sv = cfg_obj.get("singleVisual", {}) if isinstance(cfg_obj, dict) else {}
            vtype = sv.get("visualType", "?")
            title = extract_title(cfg)
            qrefs = extract_query_refs(cfg)
            tables = extract_tables(cfg)
            x = vc.get("x", "?")
            y = vc.get("y", "?")
            w = vc.get("width", "?")
            h = vc.get("height", "?")
            print(f"  [{i:2d}] type={vtype:16s} title={title!r} pos=({x},{y}) size=({w},{h}) tables={sorted(tables)}")
            if qrefs:
                for q in qrefs[:10]:
                    print(f"        qref: {q}")
                if len(qrefs) > 10:
                    print(f"        ... and {len(qrefs) - 10} more")


if __name__ == "__main__":
    main()
