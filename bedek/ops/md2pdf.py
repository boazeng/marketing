# -*- coding: utf-8 -*-
"""
Renders the working markdown as branded PDFs for SharePoint.

SharePoint shows a .md file as raw text -- hashes, pipes and all -- so anyone
in the organisation who opens PLAN.md sees source rather than a document.
These are the same files, typeset: brand palette, real tables, RTL.

The markdown stays the source of truth; this is a view of it.

    python md2pdf.py    -> ../_pdf/*.pdf
"""
import io, json, os, re, sys

sys.stdout.reconfigure(encoding="utf-8")

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, ".."))
OUT = os.path.join(ROOT, "_pdf")

C = next(d for d in json.load(io.open(
    os.path.join(ROOT, "brand", "palette", "directions.json"), encoding="utf-8"))
    if d["name"] == "bridge")["colors"]
MARK = io.open(os.path.join(ROOT, "assets", "logos", "mark.svg"), encoding="utf-8").read()

DOCS = [
    ("PLAN.md",               "תוכנית העבודה"),
    ("DECISIONS.md",          "החלטות"),
    ("brand/brand-brief.md",  "מיצוב המותג"),
    ("content/messaging.md",  "מסרים מאושרים"),
    ("social/meta-setup.md",  "הקמת פייסבוק ואינסטגרם"),
    ("ops/playbook.md",       "Playbook — שיווק מוצר חדש"),
]


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def inline(s):
    s = esc(s)
    s = re.sub(r"`([^`]+)`", r'<code>\1</code>', s)
    s = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", s)
    s = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2">\1</a>', s)
    return s


def md(text):
    """Enough markdown for these documents -- headings, tables, lists, rules."""
    out, i, lines = [], 0, text.split("\n")
    while i < len(lines):
        l = lines[i]
        if l.startswith("|") and i + 1 < len(lines) and set(lines[i+1].replace("|", "").strip()) <= set("-: "):
            head = [c.strip() for c in l.strip("|").split("|")]
            i += 2
            rows = []
            while i < len(lines) and lines[i].startswith("|"):
                rows.append([c.strip() for c in lines[i].strip("|").split("|")])
                i += 1
            out.append("<table><thead><tr>" +
                       "".join(f"<th>{inline(h)}</th>" for h in head) +
                       "</tr></thead><tbody>" +
                       "".join("<tr>" + "".join(f"<td>{inline(c)}</td>" for c in r) + "</tr>"
                               for r in rows) + "</tbody></table>")
            continue
        if re.match(r"^#{1,4} ", l):
            n = len(l) - len(l.lstrip("#"))
            out.append(f"<h{n}>{inline(l[n:].strip())}</h{n}>")
        elif l.strip() in ("---", "***"):
            out.append("<hr>")
        elif re.match(r"^\s*[-*] ", l):
            items = []
            while i < len(lines) and re.match(r"^\s*[-*] ", lines[i]):
                items.append(f"<li>{inline(re.sub(r'^\\s*[-*] ', '', lines[i]))}</li>")
                i += 1
            out.append("<ul>" + "".join(items) + "</ul>")
            continue
        elif re.match(r"^\s*\d+\. ", l):
            items = []
            while i < len(lines) and re.match(r"^\s*\d+\. ", lines[i]):
                items.append(f"<li>{inline(re.sub(r'^\\s*\\d+\\. ', '', lines[i]))}</li>")
                i += 1
            out.append("<ol>" + "".join(items) + "</ol>")
            continue
        elif l.startswith("```"):
            i += 1
            buf = []
            while i < len(lines) and not lines[i].startswith("```"):
                buf.append(esc(lines[i])); i += 1
            out.append("<pre>" + "\n".join(buf) + "</pre>")
        elif l.startswith(">"):
            out.append(f"<blockquote>{inline(l.lstrip('> '))}</blockquote>")
        elif l.strip():
            out.append(f"<p>{inline(l)}</p>")
        i += 1
    return "\n".join(out)


CSS = f"""
@page {{ size: A4; margin: 18mm 16mm 20mm; }}
* {{ box-sizing: border-box; }}
body {{ margin:0; direction:rtl; font-family:Heebo,"Segoe UI",sans-serif;
  font-size:10.5pt; line-height:1.65; color:{C['inkStrong']}; }}
header {{ display:flex; align-items:center; gap:10px; padding-bottom:10px;
  border-bottom:2px solid {C['brand']}; margin-bottom:22px; }}
header svg {{ width:34px; height:34px; }}
.brand {{ font-family:Rubik,Heebo,sans-serif; font-weight:800; font-size:19pt;
  color:{C['brand']}; }}
.docname {{ margin-inline-start:auto; font-size:10pt; color:{C['inkFaint']}; }}
h1 {{ font-family:Rubik,Heebo,sans-serif; font-weight:800; font-size:21pt;
  color:{C['brandInk']}; margin:0 0 4px; letter-spacing:-.02em; }}
h2 {{ font-family:Rubik,Heebo,sans-serif; font-weight:700; font-size:14pt;
  color:{C['brandInk']}; margin:20px 0 6px; page-break-after:avoid; }}
h3 {{ font-weight:700; font-size:11.5pt; margin:14px 0 4px; page-break-after:avoid; }}
h4 {{ font-weight:700; font-size:10.5pt; margin:12px 0 3px; }}
p {{ margin:0 0 7px; }}
ul,ol {{ margin:0 0 8px; padding-inline-start:20px; }}
li {{ margin-bottom:3px; }}
table {{ width:100%; border-collapse:collapse; margin:8px 0 14px; font-size:9.5pt;
  page-break-inside:avoid; }}
th {{ background:{C['brandSoft']}; color:{C['brandInk']}; text-align:start;
  padding:5px 8px; border:0.4pt solid {C['border']}; font-weight:700; }}
td {{ padding:5px 8px; border:0.4pt solid {C['border']}; vertical-align:top; }}
code {{ font-family:"Space Grotesk",Consolas,monospace; font-size:9pt;
  background:{C['mist']}; padding:1px 4px; border-radius:3px;
  direction:ltr; unicode-bidi:embed; }}
pre {{ font-family:"Space Grotesk",Consolas,monospace; font-size:8.5pt;
  background:{C['mist']}; padding:9px 11px; border-radius:5px; direction:ltr;
  text-align:left; overflow-wrap:anywhere; page-break-inside:avoid; }}
blockquote {{ margin:8px 0; padding:6px 12px; border-inline-start:3px solid {C['accent']};
  background:{C['accentSoft']}; }}
a {{ color:{C['brand']}; }}
hr {{ border:0; border-top:0.5pt solid {C['border']}; margin:16px 0; }}
"""


def build(rel, title):
    src = io.open(os.path.join(ROOT, rel), encoding="utf-8").read()
    html = f"""<!doctype html><html lang="he" dir="rtl"><head><meta charset="utf-8">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Heebo:wght@400;500;700&family=Rubik:wght@700;800&family=Space+Grotesk:wght@500&display=swap">
<style>{CSS}</style></head><body>
<header>{MARK}<span class="brand">בדק</span><span class="docname">{title}</span></header>
{md(src)}
</body></html>"""
    name = os.path.splitext(os.path.basename(rel))[0] + ".pdf"
    out = os.path.join(OUT, name)
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page()
        pg.set_content(html)
        pg.wait_for_timeout(1800)
        pg.pdf(path=out, format="A4", print_background=True)
        b.close()
    print(f"   {name}  {os.path.getsize(out)//1024}KB")
    return out


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    for rel, title in DOCS:
        if os.path.exists(os.path.join(ROOT, rel)):
            build(rel, title)
        else:
            print(f"   skip {rel} (missing)")
