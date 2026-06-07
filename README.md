# MJML Email Designer

## What this is

A self-contained MJML email compiler for agentic workflows. It produces Outlook-safe, Gmail-safe, mobile-first HTML emails from `.mjml` templates with `{{variable}}` substitution. Write clean, readable MJML; this skill handles table-based layout, CSS inlining, VML fallbacks, and dark mode — everything email clients demand.

---

## Requirements

- **Node.js 18+** (for the MJML compiler)
- **Python 3.9+** (optional — for the Python `render.py` wrapper)

---

## Install

```sh
cd skills/email-designer
npm install
```

That's it. The `node_modules/` directory is gitignored — run `npm install` again if it goes missing.

---

## Quick start

### CLI (JSON config → output HTML)

```sh
# Write a config file
cat > /tmp/config.json << 'JSON'
{
  "template": "templates/notification.mjml",
  "output": "/tmp/out.html",
  "variables": {
    "recipient_name":    "Jane",
    "brand_name":        "Acme",
    "brand_tagline":     "Automated Comms",
    "preview_text":      "Your weekly report is ready",
    "intro_text":        "Here is your summary for this week.",
    "table_heading":     "REPORT SUMMARY",
    "data_table":        "<table><thead><tr><th>Item</th></tr></thead><tbody><tr><td>Example row</td></tr></tbody></table>",
    "info_box_text":     "Data refreshes every 24 hours.",
    "sender_name":       "Jane Smith",
    "sender_email":      "jane@example.com",
    "organisation_name": "Acme Corp",
    "year":              "2026"
  }
}
JSON

node skills/email-designer/generate.js /tmp/config.json /tmp/out.html
```

### Python wrapper

```python
import sys
sys.path.insert(0, '/workspace')
from skills.email_designer import render

rows = [
    {"title": "Q1 Report", "date": "1 April 2026", "count": 142, "status": "Complete"},
]
columns = [
    {"key": "title",  "label": "Report"},
    {"key": "date",   "label": "Date"},
    {"key": "count",  "label": "Records", "align": "center"},
    {"key": "status", "label": "Status",  "align": "center"},
]

html = render.compile_template(
    template="templates/notification.mjml",
    variables={
        "recipient_name":    "Jane",
        "brand_name":        "Acme",
        "brand_tagline":     "Automated Comms",
        "preview_text":      "Your Q1 report is ready",
        "intro_text":        "Please find your Q1 report summary below.",
        "table_heading":     "REPORT SUMMARY",
        "data_table":        render.build_data_table(rows, columns),
        "info_box_text":     "Data is refreshed every 24 hours.",
        "sender_name":       "Jane Smith",
        "sender_email":      "jane@example.com",
        "organisation_name": "Acme Corp",
        "year":              "2026",
    },
    output_path="/tmp/notification-email.html",
)
print(f"Compiled {len(html):,} bytes")
```

---

## Templates included

| Template | Description |
|---|---|
| `base.mjml` | Layout skeleton with branded header, white card body, CTA button slot (`{{body_content}}`), and footer. Use as a starting point for new templates. |
| `notification.mjml` | Ready-to-use notification email with greeting, intro text, section heading, data table slot (`{{data_table}}`), info box, and footer. |

---

## Colour tokens

Override these by editing the `mj-attributes` section in any template.

| Token | Hex | Usage |
|---|---|---|
| `primary-dark` | `#001f3f` | Header background, footer background, section headings |
| `accent` | `#00d1b2` | CTA buttons, table headers, accent borders, links |
| `text-light` | `#ffffff` | Header text, button text |
| `text-body` | `#2e2e2e` | Body text, paragraph text |
| `bg-outer` | `#f0f4f8` | Outer email background (behind the white card) |

---

## Creating new templates

1. Copy `templates/base.mjml` as your starting point.
2. Replace the `{{body_content}}` comment with your MJML body elements (e.g. `<mj-text>`, `<mj-button>`, `<mj-image>`).
3. Add any new `{{variables}}` you need and document them.
4. Test compilation: `node skills/email-designer/generate.js config.json /tmp/out.html`
5. Check compiled size — Gmail clips emails above **102KB**. The compiler logs the size automatically.

---

## Variable reference

Variables used across all included templates:

| Variable | Templates | Example value | Description |
|---|---|---|---|
| `{{recipient_name}}` | base, notification | `Jane` | First name for greeting |
| `{{brand_name}}` | base, notification | `Acme` | Brand name in header (left) |
| `{{brand_tagline}}` | base, notification | `Automated Comms` | Short tagline in header (right) |
| `{{preview_text}}` | base, notification | `Your report is ready` | Email client preview text (≤75 chars) |
| `{{body_content}}` | base | (MJML elements) | Main content slot in base template |
| `{{contact_email}}` | base | `noreply@example.com` | CTA button `mailto:` link |
| `{{intro_text}}` | notification | `Here is your summary...` | Opening paragraph after greeting |
| `{{table_heading}}` | notification | `REPORT SUMMARY` | Section heading above data table |
| `{{data_table}}` | notification | (HTML table) | Compiled HTML table from `build_data_table()` |
| `{{info_box_text}}` | notification | `Data refreshes every 24h.` | Highlighted info box below table |
| `{{sender_name}}` | base, notification | `Jane Smith` | Sender name in footer |
| `{{sender_email}}` | base, notification | `jane@example.com` | Sender email linked in footer |
| `{{organisation_name}}` | base, notification | `Acme Corp` | Copyright holder in footer |
| `{{year}}` | base, notification | `2026` | Copyright year in footer |

---

## Licence

MIT — see [LICENSE](LICENSE).
