"""Build a static Pages site from the editorial catalog and a GitHub inventory."""
import json
import shutil
import sys
from collections import defaultdict
from datetime import datetime, timezone
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OWNER = "https://github.com/IllyaYalovyy"
projects = json.loads((ROOT / "projects.json").read_text())
inventory = {r["name"]: r for r in json.loads(Path(sys.argv[1]).read_text())}
groups = defaultdict(list)
released = []
for project in projects:
    repo = project["repo"]
    metadata = inventory[repo]
    if metadata["latestRelease"]:
        released.append((metadata["latestRelease"], project))
    groups[project["category"]].append(project)


def link(url, label):
    return f'<a href="{escape(url, quote=True)}">{escape(label)}</a>'


def card(project):
    repo = project["repo"]
    metadata = inventory[repo]
    release = metadata["latestRelease"]
    version = link(release["url"], release["tagName"]) if release else "No GitHub release"
    preview = ""
    if "image" in project:
        preview = f'<a class="preview" href="{project["image"]}"><img loading="lazy" src="{project["image"]}" alt="{escape(project["alt"])}"></a>'
    guide_label = "Project vision" if repo == "axiolog" else "Setup guide"
    return f"""<article id="{repo}"><div class="entry"><div class="meta">{escape(project["platform"])} · <span class="version">{version}</span></div>
<h3>{escape(project["name"])}</h3><p>{escape(project["description"])}</p></div>{preview}
<div class="setup"><p>{escape(project["instructions"])}</p><div class="links">{link(project["guide"], guide_label)} {link(OWNER + "/" + repo, "Source")}</div></div></article>"""


nav = []
sections = []
for i, (category, members) in enumerate(groups.items()):
    anchor = f"group-{i}"
    nav.append(link("#" + anchor, category))
    cards = "".join(card(p) for p in members)
    sections.append(f'<section id="{anchor}"><h2>{escape(category)} <small>{len(members)}</small></h2><div class="grid">{cards}</div></section>')

rows = []
for release, project in sorted(released, key=lambda item: item[0]["publishedAt"], reverse=True):
    day = release["publishedAt"][:10]
    rows.append(f'<tr><th scope="row">{link("#" + project["repo"], project["name"])}</th><td>{link(release["url"], release["tagName"])}</td><td><time datetime="{day}">{day}</time></td></tr>')
today = datetime.now(timezone.utc).date().isoformat()
page = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Illya Yalovyy · Open-source projects</title><meta name="description" content="Browse Illya Yalovyy’s open-source applications, desktop extensions and developer tools. Find releases, screenshots and installation guides."><link rel="stylesheet" href="style.css"><script defer src="releases.js"></script></head>
<body><a class="skip" href="#directory">Skip to projects</a><header><div class="wrap mast"><strong>Illya Yalovyy</strong>{link(OWNER, "GitHub profile")}</div></header>
<main class="wrap"><div class="hero"><div><h1>Open-source<br>projects<span>.</span></h1><p>Applications, extensions and tools by Illya Yalovyy.</p><nav aria-label="Project categories">{''.join(nav)}</nav></div>
<section class="ledger"><h2>Latest releases</h2><table><thead><tr><th>Project</th><th>Version</th><th>Published (UTC)</th></tr></thead><tbody>{''.join(rows)}</tbody></table><p class="meta">Release snapshot · {today} UTC</p></section></div>
<div id="directory">{''.join(sections)}</div></main><footer class="wrap">Illya Yalovyy · {link(OWNER + "/IllyaYalovyy.github.io", "Registry source")}</footer></body></html>"""
out = ROOT / "docs"
out.mkdir(exist_ok=True)
(out / "index.html").write_text(page)
shutil.copy(ROOT / "style.css", out)
shutil.copy(ROOT / "releases.js", out)
(out / ".nojekyll").touch()
