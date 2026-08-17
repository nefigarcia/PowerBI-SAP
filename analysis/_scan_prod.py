"""Ad-hoc scanner for the production Amalgamated Sales Reports.

Walks definition/pages/<pageId>/ folders, reads page.json + each visuals/<id>/visual.json,
and prints a per-page summary compatible with the AWIP scan output.
"""

import json
import re
from pathlib import Path


ROOT = Path(r"C:/Users/nefgt/Documents/Kingspan/PowerBI-SAP/production-reference-odata/Amalgamated Sales Reports - JC.Report/definition")
PAGES = ROOT / "pages"


def load_json(p):
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception as e:
        return {"__error__": str(e)}


def visual_type(v):
    # newer format: v['visual']['visualType']
    return (v.get("visual") or {}).get("visualType", "?")


def visual_title(v):
    # look under visual.objects.title[].properties.text.expr.Literal.Value
    try:
        titles = ((v.get("visual") or {}).get("objects") or {}).get("title") or []
        if titles:
            t = titles[0]
            props = t.get("properties") or {}
            expr = props.get("text", {}).get("expr", {})
            lit = expr.get("Literal", {}).get("Value")
            if lit:
                # values are wrapped like "'the title'"
                return lit.strip("'")
    except Exception:
        pass
    return ""


def visual_projections(v):
    """Return list of (role, queryRef) tuples for the projections section."""
    out = []
    try:
        proj = (v.get("visual") or {}).get("query", {}).get("queryState") or {}
        for role, spec in proj.items():
            projs = spec.get("projections") or []
            for p in projs:
                qref = p.get("queryRef") or ""
                nrn = p.get("nativeQueryRef") or ""
                out.append((role, qref or nrn))
    except Exception:
        pass
    return out


def visual_tables(v):
    text = json.dumps(v)
    return sorted(set(re.findall(r'"Entity"\s*:\s*"([^"]+)"', text)))


def visual_position(v):
    try:
        pos = v.get("position") or {}
        return pos.get("x"), pos.get("y"), pos.get("width"), pos.get("height")
    except Exception:
        return None, None, None, None


def main():
    pages_meta = load_json(PAGES / "pages.json")
    order = pages_meta.get("pageOrder", [])
    print(f"total pages: {len(order)}")
    print()
    for idx, pid in enumerate(order, start=1):
        pdir = PAGES / pid
        page = load_json(pdir / "page.json")
        display = page.get("displayName", "?")
        visibility = page.get("visibility", "Visible")
        # find visuals
        vdir = pdir / "visuals"
        vfiles = sorted(vdir.glob("*/visual.json")) if vdir.is_dir() else []
        print(f"=== PAGE {idx:2d} name={display!r} id={pid} visibility={visibility} visuals={len(vfiles)} ===")
        # sort visuals by (y,x) to give a rough reading order
        visuals = []
        for vf in vfiles:
            v = load_json(vf)
            x, y, w, h = visual_position(v)
            visuals.append((v, vf.parent.name, x or 0, y or 0, w, h))
        visuals.sort(key=lambda t: ((t[3] or 0) // 100, (t[2] or 0)))
        for i, (v, vid, x, y, w, h) in enumerate(visuals):
            vt = visual_type(v)
            title = visual_title(v)
            projs = visual_projections(v)
            tables = visual_tables(v)
            print(f"  [{i:2d}] type={vt:16s} title={title!r} pos=({x},{y}) size=({w},{h}) tables={tables}")
            for role, q in projs[:10]:
                print(f"        proj[{role}]: {q}")
            if len(projs) > 10:
                print(f"        ... and {len(projs) - 10} more")


if __name__ == "__main__":
    main()
