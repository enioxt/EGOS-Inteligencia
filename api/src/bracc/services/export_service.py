"""Investigation export in multiple formats: Markdown, HTML, JSON."""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from bracc.services.pdf_service import _get_labels

if TYPE_CHECKING:
    from bracc.models.investigation import Annotation, InvestigationResponse, Tag


def render_investigation_md(
    investigation: InvestigationResponse,
    annotations: list[Annotation],
    tags: list[Tag],
    entities: list[dict[str, str]],
    lang: str = "pt",
) -> str:
    """Render investigation as Markdown."""
    L = _get_labels(lang)
    lines: list[str] = []

    lines.append(f"# {investigation.title}")
    lines.append("")
    if investigation.description:
        lines.append(investigation.description)
        lines.append("")
    lines.append(f"**{L['label_created']}:** {investigation.created_at}")
    lines.append("")

    # Tags
    lines.append(f"## {L['label_tags']}")
    if tags:
        lines.append(", ".join(f"`{t.name}`" for t in tags))
    else:
        lines.append(f"*{L['label_no_tags']}*")
    lines.append("")

    # Entities
    lines.append(f"## {L['label_entities']}")
    if entities:
        lines.append(f"| {L['label_entity_name']} | {L['label_entity_type']} | {L['label_entity_document']} |")
        lines.append("| --- | --- | --- |")
        for e in entities:
            lines.append(f"| {e.get('name', '')} | {e.get('type', '')} | {e.get('document', '')} |")
    else:
        lines.append(f"*{L['label_no_entities']}*")
    lines.append("")

    # Annotations
    lines.append(f"## {L['label_annotations']}")
    if annotations:
        for a in annotations:
            lines.append(f"- **{a.created_at}** — {a.text}")
    else:
        lines.append(f"*{L['label_no_annotations']}*")
    lines.append("")

    lines.append("---")
    lines.append(f"*{L['disclaimer']}*")
    lines.append("")

    return "\n".join(lines)


def render_investigation_html(
    investigation: InvestigationResponse,
    annotations: list[Annotation],
    tags: list[Tag],
    entities: list[dict[str, str]],
    lang: str = "pt",
) -> str:
    """Render investigation as standalone HTML (no external deps)."""
    L = _get_labels(lang)
    esc = _html_escape

    tag_html = ""
    if tags:
        tag_html = " ".join(
            f'<span style="background:{t.color or "#555"};color:#fff;padding:2px 8px;'
            f'border-radius:4px;font-size:0.85em">{esc(t.name)}</span>'
            for t in tags
        )
    else:
        tag_html = f"<em>{esc(L['label_no_tags'])}</em>"

    entity_rows = ""
    if entities:
        for e in entities:
            entity_rows += (
                f"<tr><td>{esc(e.get('name', ''))}</td>"
                f"<td>{esc(e.get('type', ''))}</td>"
                f"<td><code>{esc(e.get('document', ''))}</code></td></tr>"
            )
    else:
        entity_rows = f'<tr><td colspan="3"><em>{esc(L["label_no_entities"])}</em></td></tr>'

    ann_html = ""
    if annotations:
        for a in annotations:
            ann_html += f"<li><strong>{esc(str(a.created_at))}</strong> — {esc(a.text)}</li>"
    else:
        ann_html = f"<li><em>{esc(L['label_no_annotations'])}</em></li>"

    return f"""<!DOCTYPE html>
<html lang="{lang}">
<head>
<meta charset="utf-8">
<title>{esc(investigation.title)}</title>
<style>
  body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
         max-width: 800px; margin: 2rem auto; padding: 0 1rem; color: #1a1a1a; }}
  h1 {{ border-bottom: 2px solid #333; padding-bottom: 0.5rem; }}
  table {{ width: 100%; border-collapse: collapse; margin: 1rem 0; }}
  th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
  th {{ background: #f5f5f5; }}
  .disclaimer {{ margin-top: 2rem; padding-top: 1rem; border-top: 1px solid #ddd;
                 font-size: 0.85rem; color: #666; }}
</style>
</head>
<body>
<h1>{esc(investigation.title)}</h1>
<p>{esc(investigation.description or '')}</p>
<p><strong>{esc(L['label_created'])}:</strong> {esc(str(investigation.created_at))}</p>

<h2>{esc(L['label_tags'])}</h2>
<p>{tag_html}</p>

<h2>{esc(L['label_entities'])}</h2>
<table>
<thead><tr>
  <th>{esc(L['label_entity_name'])}</th>
  <th>{esc(L['label_entity_type'])}</th>
  <th>{esc(L['label_entity_document'])}</th>
</tr></thead>
<tbody>{entity_rows}</tbody>
</table>

<h2>{esc(L['label_annotations'])}</h2>
<ul>{ann_html}</ul>

<div class="disclaimer"><em>{esc(L['disclaimer'])}</em></div>
</body>
</html>"""


def _html_escape(text: str) -> str:
    """Minimal HTML escaping."""
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )
