import json, os, subprocess, sys, tempfile
from pathlib import Path

SKILL_DIR = Path(__file__).parent.resolve()
GENERATE_JS = SKILL_DIR / "generate.js"
NODE_MODULES = SKILL_DIR / "node_modules"


def _check_dependencies():
    if not GENERATE_JS.exists():
        raise FileNotFoundError("generate.js not found at " + str(GENERATE_JS))
    if not NODE_MODULES.exists():
        raise RuntimeError("Node modules not installed. Run: cd " + str(SKILL_DIR) + " && npm install")


def build_data_table(rows, columns=None):
    """Build an HTML table from a list of row dicts and optional column definitions.

    Parameters
    ----------
    rows : list[dict]
        Data rows. Each dict maps column keys to cell values.
    columns : list[dict], optional
        Column definitions. Each dict must have:
          - ``key``   (str) : dict key to read from each row
          - ``label`` (str) : column header label
          - ``align`` (str, optional) : "left" (default) or "center"
        If omitted, columns are inferred from the keys of the first row,
        with left alignment and title-cased labels.

    Returns
    -------
    str
        Self-contained HTML table string suitable for embedding in an email.
    """
    if columns is None:
        if not rows:
            return ""
        columns = [
            {"key": k, "label": k.replace("_", " ").title()}
            for k in rows[0].keys()
        ]

    accent = "#00d1b2"
    primary_dark = "#001f3f"

    def _th_style(align="left"):
        return (
            "background-color:{accent};color:#ffffff;font-weight:bold;"
            "padding:11px 10px;text-align:{align};white-space:nowrap;"
        ).format(accent=accent, align=align)

    def _td_style(align="left"):
        return "padding:10px 10px;border-bottom:1px solid #e8ecf0;color:#2e2e2e;vertical-align:top;text-align:{};".format(align)

    header_cells = "".join(
        '<th style="{}">{}</th>'.format(
            _th_style(col.get("align", "left")), col["label"]
        )
        for col in columns
    )

    row_html_list = []
    for row in rows:
        cells = "".join(
            '<td style="{}">{}</td>'.format(
                _td_style(col.get("align", "left")),
                str(row.get(col["key"], "-")),
            )
            for col in columns
        )
        row_html_list.append("<tr>{}</tr>".format(cells))

    return (
        '<table style="width:100%;border-collapse:collapse;'
        'font-family:Arial,Helvetica,sans-serif;font-size:14px;">'
        "<thead><tr>{}</tr></thead>"
        "<tbody>{}</tbody>"
        "</table>"
    ).format(header_cells, "".join(row_html_list))


def build_webinar_table(webinars):
    """Backward-compatible helper: build a table from webinar dicts.

    Each dict: name, date, eligible_attendees, points
    Delegates to build_data_table() with the appropriate column spec.
    """
    columns = [
        {"key": "name",               "label": "Webinar",            "align": "left"},
        {"key": "date",               "label": "Date",               "align": "left"},
        {"key": "eligible_attendees", "label": "Eligible Attendees", "align": "center"},
        {"key": "points",         "label": "Points",             "align": "center"},
    ]
    return build_data_table(webinars, columns)


def compile_template(template, variables, output_path=None):
    """Compile MJML template with variable substitution.

    Parameters
    ----------
    template : str
        Path to .mjml template (absolute or relative to this skill directory).
    variables : dict
        Template variables for {{key}} substitution.
    output_path : str, optional
        Write compiled HTML to this path as well.

    Returns
    -------
    str
        Compiled HTML.
    """
    _check_dependencies()
    config = {"template": template, "variables": variables}
    if output_path:
        config["output"] = output_path
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".json", delete=False, encoding="utf-8"
    ) as f:
        json.dump(config, f)
        cp = f.name
    try:
        r = subprocess.run(
            ["node", str(GENERATE_JS), cp],
            capture_output=True,
            text=True,
            cwd=str(SKILL_DIR),
        )
        if r.returncode != 0:
            raise RuntimeError(
                "generate.js failed (exit {}):\n{}".format(r.returncode, r.stderr)
            )
        if r.stderr:
            sys.stderr.write(r.stderr)
        if output_path:
            return Path(output_path).read_text(encoding="utf-8")
        return r.stdout
    finally:
        try:
            os.unlink(cp)
        except OSError:
            pass


if __name__ == "__main__":
    from datetime import datetime

    rows = [
        {"title": "Introduction to Machine Learning", "date": "1 June 2026", "attendees": 142, "status": "Processed"},
        {"title": "Advanced Data Pipelines",          "date": "3 June 2026", "attendees": 87,  "status": "Processed"},
    ]
    columns = [
        {"key": "title",     "label": "Session",   "align": "left"},
        {"key": "date",      "label": "Date",      "align": "left"},
        {"key": "attendees", "label": "Attendees", "align": "center"},
        {"key": "status",    "label": "Status",    "align": "center"},
    ]

    variables = {
        "recipient_name":    "Jane",
        "brand_name":        "Acme",
        "brand_tagline":     "Automated Comms",
        "preview_text":      "Your session report is ready",
        "intro_text":        "Please find your session summary below, processed on <strong>{}</strong>.".format(
            datetime.today().strftime("%-d %B %Y")
        ),
        "table_heading":     "SESSION SUMMARY",
        "data_table":        build_data_table(rows, columns),
        "info_box_text":     "Data is refreshed every 24 hours. Contact your account manager with any queries.",
        "sender_name":       "Jane Smith",
        "sender_email":      "jane@example.com",
        "organisation_name": "Acme Corp",
        "year":              str(datetime.today().year),
    }

    out = "/tmp/notification-email.html"
    html = compile_template(
        template="templates/notification.mjml",
        variables=variables,
        output_path=out,
    )
    print("Compiled. Output: {} ({:,} bytes)".format(out, len(html)))
