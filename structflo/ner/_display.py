"""Interactive HTML visualization for NER extraction results.

Renders annotated text with color-coded entity highlights, tooltips,
and a filterable legend. Works in Jupyter notebooks via IPython.display.
"""

from __future__ import annotations

import html
import uuid
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from structflo.ner._entities import NERResult

# ── Color palette per entity category ──────────────────────────────────

_COLORS: dict[str, dict[str, str]] = {
    "ChemicalEntity": {"bg": "#dbeafe", "border": "#3b82f6", "label": "Compound"},
    "TargetEntity": {"bg": "#dcfce7", "border": "#22c55e", "label": "Target"},
    "DiseaseEntity": {"bg": "#fce7f3", "border": "#ec4899", "label": "Disease"},
    "BioactivityEntity": {"bg": "#fef3c7", "border": "#f59e0b", "label": "Bioactivity"},
    "AssayEntity": {"bg": "#e0e7ff", "border": "#6366f1", "label": "Assay"},
    "MechanismEntity": {"bg": "#f3e8ff", "border": "#a855f7", "label": "Mechanism"},
    "NEREntity": {"bg": "#f1f5f9", "border": "#94a3b8", "label": "Other"},
}


def _color_for(entity_cls_name: str) -> dict[str, str]:
    return _COLORS.get(entity_cls_name, _COLORS["NEREntity"])


# ── HTML rendering ─────────────────────────────────────────────────────


def render_html(result: NERResult) -> str:
    """Return a self-contained HTML string visualizing the NER result.

    Entities with character offsets are rendered as inline highlights over
    the source text.  Entities without offsets are listed in a separate
    section below.
    """
    uid = uuid.uuid4().hex[:8]

    # Partition entities into positioned and unpositioned
    positioned = []
    unpositioned = []
    for ent in result.all_entities():
        if ent.char_start is not None and ent.char_end is not None:
            positioned.append(ent)
        else:
            unpositioned.append(ent)

    # Sort by start offset, then by longest span first (to handle nesting)
    positioned.sort(key=lambda e: (e.char_start, -(e.char_end - e.char_start)))

    # Resolve overlaps: keep only non-overlapping spans (greedy, longest first)
    selected = []
    occupied_end = -1
    for ent in positioned:
        if ent.char_start >= occupied_end:
            selected.append(ent)
            occupied_end = ent.char_end

    # Build annotated text
    text = result.source_text
    parts: list[str] = []
    cursor = 0
    for ent in selected:
        color = _color_for(type(ent).__name__)
        # Plain text before entity
        if ent.char_start > cursor:
            parts.append(html.escape(text[cursor : ent.char_start]))
        # Tooltip content
        tips = [f"type: {ent.entity_type}"]
        if ent.attributes:
            tips.extend(f"{k}: {v}" for k, v in ent.attributes.items())
        tooltip = html.escape(" | ".join(tips))
        # Entity span
        parts.append(
            f'<mark class="ner-ent" '
            f'data-category="{type(ent).__name__}" '
            f'style="background:{color["bg"]};border-bottom:2px solid {color["border"]};'
            f'padding:2px 4px;border-radius:4px;cursor:default" '
            f'title="{tooltip}">'
            f"{html.escape(text[ent.char_start : ent.char_end])}"
            f'<span style="font-size:0.7em;font-weight:600;vertical-align:super;'
            f'margin-left:2px;color:{color["border"]}">'
            f"{html.escape(ent.entity_type)}</span></mark>"
        )
        cursor = ent.char_end
    # Remaining text
    if cursor < len(text):
        parts.append(html.escape(text[cursor:]))

    annotated_html = "".join(parts)

    # Unpositioned entities table
    unpositioned_section = ""
    if unpositioned:
        rows = []
        for ent in unpositioned:
            color = _color_for(type(ent).__name__)
            attrs = ", ".join(f"{k}={v}" for k, v in ent.attributes.items()) or "—"
            rows.append(
                f'<tr data-category="{type(ent).__name__}">'
                f'<td style="padding:4px 8px"><span style="display:inline-block;'
                f"width:10px;height:10px;border-radius:50%;background:{color['border']};"
                f'margin-right:6px"></span>{html.escape(ent.text)}</td>'
                f'<td style="padding:4px 8px;color:#64748b">'
                f"{html.escape(ent.entity_type)}</td>"
                f'<td style="padding:4px 8px;color:#64748b;font-size:0.85em">'
                f"{html.escape(attrs)}</td></tr>"
            )
        unpositioned_section = (
            '<div style="margin-top:16px">'
            '<h4 style="margin:0 0 6px;font-size:0.85em;color:#64748b">'
            "Entities without text spans</h4>"
            '<table style="border-collapse:collapse;width:100%;font-size:0.9em">'
            '<thead><tr style="border-bottom:1px solid #e2e8f0">'
            '<th style="text-align:left;padding:4px 8px">Text</th>'
            '<th style="text-align:left;padding:4px 8px">Type</th>'
            '<th style="text-align:left;padding:4px 8px">Attributes</th>'
            "</tr></thead><tbody>" + "".join(rows) + "</tbody></table></div>"
        )

    # Legend
    seen = {type(e).__name__ for e in result.all_entities()}
    legend_items = []
    for cls_name, color in _COLORS.items():
        if cls_name not in seen:
            continue
        legend_items.append(
            f'<button class="ner-legend-btn" data-target="{cls_name}" '
            f'style="display:inline-flex;align-items:center;gap:4px;'
            f"padding:4px 10px;border:1.5px solid {color['border']};border-radius:16px;"
            f"background:{color['bg']};cursor:pointer;font-size:0.8em;font-weight:500;"
            f'font-family:inherit">'
            f'<span style="width:8px;height:8px;border-radius:50%;'
            f'background:{color["border"]}"></span>'
            f"{html.escape(color['label'])}</button>"
        )
    legend_html = (
        '<div style="display:flex;flex-wrap:wrap;gap:6px;margin-bottom:12px">'
        + "".join(legend_items)
        + "</div>"
    )

    # Entity counts summary
    counts = {}
    for ent in result.all_entities():
        label = _color_for(type(ent).__name__)["label"]
        counts[label] = counts.get(label, 0) + 1
    count_parts = " · ".join(f"<b>{v}</b> {k}" for k, v in counts.items())
    summary = f'<div style="font-size:0.8em;color:#64748b;margin-bottom:10px">{count_parts}</div>'

    # JS for toggling entity categories
    script = (
        f"<script>"
        f"(function(){{"
        f"var w=document.getElementById('ner-{uid}');"
        f"w.querySelectorAll('.ner-legend-btn').forEach(function(btn){{"
        f"btn.addEventListener('click',function(){{"
        f"var cat=btn.dataset.target;"
        f"var active=btn.dataset.active!=='false';"
        f"btn.dataset.active=active?'false':'true';"
        f"btn.style.opacity=active?'0.35':'1';"
        f"w.querySelectorAll('[data-category=\"'+cat+'\"]').forEach(function(el){{"
        f"if(el.classList.contains('ner-ent'))"
        f"el.style.background=active?'transparent':el.style.borderBottomColor.replace('solid ','');"
        f"el.style.opacity=active?'0.3':'1';"
        f"}});"
        f"}});"
        f"}});"
        f"}})()</script>"
    )

    return (
        f'<div id="ner-{uid}" style="font-family:system-ui,-apple-system,sans-serif;'
        f'max-width:900px;padding:20px">'
        f"{legend_html}{summary}"
        f'<div style="line-height:2;font-size:1em;white-space:pre-wrap">'
        f"{annotated_html}</div>"
        f"{unpositioned_section}"
        f"{script}</div>"
    )


def display(result: NERResult) -> None:
    """Render the NER result as interactive HTML in a Jupyter notebook."""
    try:
        from IPython.display import HTML  # noqa: PLC0415
        from IPython.display import display as ipy_display  # noqa: PLC0415
    except ImportError as exc:
        raise ImportError(
            "IPython is required for display(). "
            "Use render_html() to get the raw HTML string instead."
        ) from exc

    ipy_display(HTML(render_html(result)))
