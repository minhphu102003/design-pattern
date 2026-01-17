import json

EXPORTERS: dict[str, callable]= {}


def exporter(fmt: str):
  def _wrap(fn):
    if fmt in EXPORTERS:
      raise ValueError(f"exporter for {fmt} already registered")
    EXPORTERS[fmt] = fn
    return fn
  return _wrap


def unregister_exporter(fmt: str) -> bool:
   return EXPORTERS.pop(fmt, None) is not None

@exporter("json")
def export_json(data: list[dict]) -> str:
    return json.dumps(data)


@exporter("csv")
def export_csv(data: list[dict]) -> str:
    if not data:
        return ""
    headers = list(data[0].keys())
    lines = [",".join(headers)]
    for row in data:
        lines.append(",".join(str(row.get(h, "")) for h in headers))
    return "\n".join(lines)

@exporter("html")
def export_html(data: list[dict]) -> str:
    rows = "".join("<tr>" + "".join(f"<td>{v}</td>" for v in r.values()) + "</tr>" for r in data)
    return f"<table>{rows}</table>"
