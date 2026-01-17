import json
import csv

def export_report(data: list[dict], fmt: str) -> str:
    if fmt == "json":
        return json.dumps(data)
    elif fmt == "csv":
        # simplified CSV
        if not data:
            return ""
        headers = list(data[0].keys())
        lines = [",".join(headers)]
        for row in data:
            lines.append(",".join(str(row.get(h, "")) for h in headers))
        return "\n".join(lines)
    elif fmt == "html":
        rows = "".join("<tr>" + "".join(f"<td>{v}</td>" for v in r.values()) + "</tr>" for r in data)
        return f"<table>{rows}</table>"
    else:
        raise ValueError("unknown format")
