---
name: email-designer
description: Build and compile professional HTML emails using MJML. Outlook-safe, responsive, and mobile-first.
license: MIT
---

# Email Designer Skill

Use this skill to build and compile **Outlook-safe, responsive HTML emails** for automated workflows. Suitable for transactional notifications, automated reports, system alerts, and any programmatically generated email.

## When to use

- Any task that needs to generate an HTML email programmatically
- Automated notification emails (account updates, report deliveries, alerts)
- Transactional emails with dynamic data tables
- Bulk campaign compilation from template + variable data
- Any workflow where email body HTML needs to be generated before passing to a mail sender

---

## Framework: MJML

**MJML** (https://mjml.io) compiles a simplified XML-like markup into table-based, inlined-CSS, Outlook-safe HTML. You write clean, readable templates; MJML handles the horrifying table nesting, VML fallbacks, and CSS inlining automatically.

### Why MJML

| Problem | MJML solution |
|---|---|
| Outlook ignores CSS | Generates VML fallbacks automatically |
| Gmail strips `<head>` styles | Inlines all CSS at compile time |
| Mobile responsiveness | Generates `@media` queries automatically |
| Max-width 600px standard | Enforced via `mj-body width="600px"` |

### MJML version

This skill uses **MJML 5** (async API). Node v18+ compatible.

### Compilation flow

```
.mjml template
    ↓ variable substitution ({{key}} → value)
    ↓ mjml() async compile
    → compiled .html (table-based, inlined CSS, Outlook VML, responsive)
```

---

## File structure

```
skills/email-designer/
  SKILL.md                          This file
  generate.js                       Node.js compiler (CLI entry point)
  render.py                         Python wrapper (for use in automation scripts)
  package.json                      npm manifest (mjml dependency)
  node_modules/                     npm dependencies
  templates/
    base.mjml                       Reusable header/footer layout reference
    notification.mjml               Generic notification email with data table
```

---

## Default colour tokens

These are the default token values. Override them by editing the template `mj-attributes` section.

| Token | Hex | Usage |
|---|---|---|
| `primary-dark` | `#001f3f` | Header background, footer background, section headings |
| `accent` | `#00d1b2` | CTA buttons, table headers, accent borders, links |
| `text-light` | `#ffffff` | Email card background, button text, header text |
| `text-body` | `#2e2e2e` | Body text, paragraph text |
| `bg-outer` | `#f0f4f8` | Outer email background (behind the white card) |

Typography: **`Arial, Helvetica, sans-serif`** — system fonts only. Web fonts are unreliable in email clients. No Google Fonts, no CDN fonts.

---

## Standard email layout structure

```
┌──────────────────────────────────────────┐
│  [HEADER] #001f3f (primary-dark)          │
│  "{{brand_name}}" bold white left  |      │
│   "{{brand_tagline}}" accent right        │
├──────────────────────────────────────────┤
│  [WHITE CARD] #ffffff, 32px padding       │
│                                          │
│  Dear {{recipient_name}},                │
│                                          │
│  [CONTENT BLOCKS]                        │
│  Data table (accent header),             │
│  info boxes, CTA button                  │
│                                          │
│  [CTA BUTTON] #00d1b2, white text        │
│                                          │
├──────────────────────────────────────────┤
│  [DIVIDER] 1px #e8ecf0                   │
├──────────────────────────────────────────┤
│  [FOOTER] #001f3f (primary-dark)         │
│  White text disclosure + copyright       │
└──────────────────────────────────────────┘
```

---

## Template variables

All templates use `{{variable_name}}` syntax. The Python `render.py` substitutes these before passing to MJML.

### Base template (`base.mjml`)

| Variable | Example | Description |
|---|---|---|
| `{{recipient_name}}` | `Jane` | First name for greeting |
| `{{brand_name}}` | `Acme` | Brand name displayed in header left |
| `{{brand_tagline}}` | `Automated Comms` | Short tagline displayed in header right |
| `{{body_content}}` | (MJML elements) | Main body content slot |
| `{{contact_email}}` | `noreply@example.com` | CTA button email link |
| `{{sender_name}}` | `Jane Smith` | Displayed in footer disclosure |
| `{{sender_email}}` | `jane@example.com` | Linked in footer disclosure |
| `{{organisation_name}}` | `Acme Corp` | Displayed in footer copyright |
| `{{year}}` | `2026` | Copyright year |

### Notification template (`notification.mjml`)

| Variable | Example | Description |
|---|---|---|
| `{{recipient_name}}` | `Jane` | First name for greeting |
| `{{brand_name}}` | `Acme` | Brand name displayed in header left |
| `{{brand_tagline}}` | `Automated Comms` | Short tagline in header right |
| `{{preview_text}}` | `Your weekly report` | Email client preview text |
| `{{intro_text}}` | `Your data for this week...` | Opening paragraph after greeting |
| `{{table_heading}}` | `REPORT SUMMARY` | Section heading above data table |
| `{{data_table}}` | (HTML table) | Compiled HTML table from `build_data_table()` |
| `{{info_box_text}}` | `Data refreshes every 24 hours.` | Highlighted info box content |
| `{{sender_name}}` | `Jane Smith` | Displayed in footer disclosure |
| `{{sender_email}}` | `jane@example.com` | Linked in footer disclosure |
| `{{organisation_name}}` | `Acme Corp` | Copyright in footer |
| `{{year}}` | `2026` | Copyright year |

---

## How to generate an email

### Python (for automation scripts)

```python
import sys
sys.path.insert(0, '/workspace')
from skills.email_designer import render

# Build generic data table
rows = [
    {"title": "Q1 Report", "date": "1 April 2026", "count": 142, "status": "Complete"},
]
columns = [
    {"key": "title",  "label": "Report"},
    {"key": "date",   "label": "Date"},
    {"key": "count",  "label": "Records", "align": "center"},
    {"key": "status", "label": "Status",  "align": "center"},
]
table_html = render.build_data_table(rows, columns)

# Compile email
html = render.compile_template(
    template="templates/notification.mjml",
    variables={
        "recipient_name": "Jane",
        "brand_name": "Acme",
        "brand_tagline": "Automated Comms",
        "preview_text": "Your Q1 report is ready",
        "intro_text": "Please find your Q1 report summary below.",
        "table_heading": "REPORT SUMMARY",
        "data_table": table_html,
        "info_box_text": "Data is refreshed every 24 hours.",
        "sender_name": "Jane Smith",
        "sender_email": "jane@example.com",
        "organisation_name": "Acme Corp",
        "year": "2026",
    },
    output_path="/tmp/notification-email.html",
)
```

### Node.js / CLI

```sh
# Via config JSON file
node skills/email-designer/generate.js config.json output.html

# Via stdin
echo '{"template":"templates/notification.mjml","variables":{"recipient_name":"Jane",...},"output":"out.html"}' \
  | node skills/email-designer/generate.js

# Quick test
cd skills/email-designer && python3 render.py
```

### Config JSON shape

```json
{
  "template": "templates/notification.mjml",
  "output": "/tmp/out.html",
  "variables": {
    "recipient_name": "Jane",
    "brand_name": "Acme",
    "brand_tagline": "Automated Comms",
    "preview_text": "Your weekly report",
    "intro_text": "Here is your summary for this week.",
    "table_heading": "SUMMARY",
    "data_table": "<table>...</table>",
    "info_box_text": "Data refreshes every 24 hours.",
    "sender_name": "Jane Smith",
    "sender_email": "jane@example.com",
    "organisation_name": "Acme Corp",
    "year": "2026"
  }
}
```

---

## Attachments

MJML handles email body only. Attachments are handled by the sending layer (SMTP, transactional email API, etc.). Pass file paths or base64-encoded data to the mail sender separately from MJML compilation.

---

## Email size limit

Gmail clips emails above **102KB**. The `generate.js` script logs the compiled size and warns if it exceeds this limit. Target: keep compiled HTML under 80KB to leave room for base64-encoded small assets.

---

## Outlook quirks (handled by MJML automatically)

| Quirk | MJML solution |
|---|---|
| No `background-image` support | Uses VML `<v:rect>` fallbacks |
| No `border-radius` | Uses inline styles where possible |
| Ignores `margin: auto` | Uses `align="center"` on `<table>` |
| No CSS `max-width` | Uses fixed `width` attribute on tables |
| No Flexbox/Grid | Table-based layout throughout |
| No `:hover` | Hover effects not used |

---

## Dark mode

The templates include `@media (prefers-color-scheme: dark)` blocks that adjust backgrounds and text colours for dark mode email clients. Key overrides:

- Email body: `#1a1a1a`
- Content wrapper: `#2a2a2a`
- Footer: `#111`

These are CSS-only and will gracefully degrade in clients that do not support `prefers-color-scheme`.

---

## Creating new templates

1. Copy `templates/base.mjml` as your starting point
2. Replace `{{body_content}}` with your MJML body elements
3. Add your template variables to the variable table above
4. Test: `node skills/email-designer/generate.js config.json /tmp/out.html`
5. Check size: must be under 102KB

---

## Dependencies

Install once:

```sh
cd skills/email-designer && npm install
```

Dependencies are listed in `package.json`. The `node_modules/` directory should be in `.gitignore` — run `npm install` if it is missing.

---

## Email Strategy

Any task that involves drafting, writing, or optimising email content (not just compiling HTML) **must** consult the strategy reference before producing copy:

```
skills/email-designer/EMAIL_STRATEGY.md
```

Key enforced rules (hard — not optional):
- **Context first.** Do not write a single word of copy until audience, goal, recipient role, campaign stage, and compliance constraints are confirmed.
- **Subject lines ≤ 50 characters.** Preview text ≤ 75 characters.
- **One primary CTA per email.** Ownership/progression verbs only (Reserve, Claim, Secure, Start, Book, Access).
- **No fake scarcity, no fabricated metrics, no deceptive urgency.** All claims must be verifiable and sourced.
- **Always produce 2–3 variants** for A/B testing with a documented hypothesis per variant.
- **Flesch-Kincaid target: 60–70.** Short paragraphs, active voice.
- **Unsubscribe path required** in every commercial email.
- **Subject line priority hierarchy:** Urgency+Exclusivity > Ownership+Value > Curiosity+Benefit.
- **Timing:** Send Tue–Thu, mid-morning (09:00–11:00 local time). Design mobile-first.
