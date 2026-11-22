"""Validate the curated catalog and report upstream changes for editorial review."""
import argparse
import json
import re
import subprocess
from calendar import monthrange
from datetime import date
from pathlib import Path
from urllib.parse import urlsplit

parser = argparse.ArgumentParser()
parser.add_argument("inventory", type=Path)
parser.add_argument("--accept", metavar="REPO", help="record reviewed upstream file revisions")
args = parser.parse_args()
projects = json.loads(Path("projects.json").read_text())
policy = json.loads(Path("maintenance/policy.json").read_text())
baseline_path = Path("maintenance/reviewed.json")
baseline = json.loads(baseline_path.read_text())
inventory = {r["name"]: r for r in json.loads(args.inventory.read_text())}
if not 0 < len(inventory) < 1000:
    raise ValueError("Incomplete public repository inventory")
tracked = {p["repo"] for p in projects if "repo" in p}
if args.accept and args.accept not in tracked:
    parser.error("choose a public repository from projects.json")

# Read only public repositories explicitly present in the inventory. The query
# returns Git object IDs, so routine runs never need the contents of a guide.
query = []
paths_by_repo = {}
seen = set()
notes = []
for project in projects:
    repo = project.get("repo")
    slug = repo or project["id"]
    if slug in seen or not re.fullmatch(r'[A-Za-z0-9_-]+', slug):
        raise ValueError(f"Duplicate or invalid project ID: {slug}")
    seen.add(slug)
    if "image" in project:
        image = Path(project["image"])
        if image.parent != Path("images") or not (Path("docs") / image).is_file() or not project["alt"]:
            raise ValueError(f"Invalid screenshot or alt text: {slug}")
    if not repo:
        continue
    if repo not in inventory:
        raise ValueError(f"Review {repo}: missing from the public inventory; publication stopped")
    if inventory[repo]["isArchived"]:
        notes.append(f"{repo}: repository archived; review catalog status")
    guide = urlsplit(project["guide"])
    prefix = f"/IllyaYalovyy/{repo}/blob/"
    paths = {"guide": "HEAD:README.md"}
    if guide.path.startswith(prefix):
        ref, path = guide.path.removeprefix(prefix).split("/", 1)
        paths["guide"] = f"{ref}:{path}"
    if "imageSource" in project:
        owner, name, ref, path = urlsplit(project["imageSource"]).path.lstrip("/").split("/", 3)
        if (owner, name) != ("IllyaYalovyy", repo):
            raise ValueError(f"Unexpected screenshot source: {repo}")
        paths["screenshot"] = f"{ref}:{path}"
    fields = " ".join(f"{key}:object(expression:{json.dumps(expr)}){{oid}}" for key, expr in paths.items())
    query.append(f'r{len(query)}:repository(owner:"IllyaYalovyy",name:{json.dumps(repo)}){{{fields}}}')
    paths_by_repo[repo] = paths

if query:
    response = subprocess.check_output(["gh", "api", "graphql", "-f", "query=query {" + " ".join(query) + "}"])
    data = json.loads(response)["data"]
    for i, (repo, paths) in enumerate(paths_by_repo.items()):
        blobs = data[f"r{i}"]
        current = {}
        for kind, expr in paths.items():
            blob = blobs[kind]
            if blob is None:
                notes.append(f"{repo}: missing {kind} ({expr})")
                continue
            current[kind] = blob["oid"]
            if baseline.get(repo, {}).get(kind) != blob["oid"]:
                notes.append(f"{repo}: review {kind} ({expr}, {blob['oid'][:10]})")
        if args.accept == repo:
            if len(current) != len(paths):
                raise ValueError(f"Cannot accept missing source for {repo}")
            baseline[repo] = current

if args.accept:
    baseline_path.write_text(json.dumps(baseline, indent=2, sort_keys=True) + "\n")

today = date.today()
cutoff = date(today.year - 2, today.month, min(today.day, monthrange(today.year - 2, today.month)[1]))
for name, repo in sorted(inventory.items()):
    if name not in tracked and name not in policy["ignore"] and not repo["isArchived"] and repo["pushedAt"][:10] >= cutoff.isoformat():
        notes.append(f"{name}: recent public repository; review for inclusion")
print("\n".join(sorted(notes)) or "No editorial changes detected.")
