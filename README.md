# Illya Yalovyy’s project registry

[Browse the public directory](https://illyayalovyy.github.io/) for project descriptions, screenshots, setup instructions and current releases.

The initial survey covered all 21 public repositories on the account on 2026-11-21. Fifteen had a push on or after 2024-11-21. The current catalog is curated and also includes Minecraft projects distributed outside GitHub. A recent push is a discovery criterion and does not establish a maintenance commitment.

## Maintain the directory

Edit `projects.json` to add, regroup or retire projects. GitHub entries identify the repository and setup guide. Other entries use a stable id and an editorial release status. Where a screenshot is available, the entry includes an accessible description alongside the local WebP image. Review the roster periodically for new projects.

GitHub Pages serves the committed `docs/` directory from main. Each visit checks GitHub’s public latest-release API, caching successful lookups in the browser tab for one hour. A static snapshot keeps the directory usable without JavaScript or when rate-limited. Release links lead to the original notes and downloads. After editorial changes, regenerate the snapshot with the commands below and commit the updated source and docs together.

## Preview locally

With Python 3 and an authenticated GitHub CLI, run:

```sh
gh repo list IllyaYalovyy --visibility public --limit 500 --json name,latestRelease > /tmp/registry-inventory.json
python3 build.py /tmp/registry-inventory.json
python3 -m http.server --directory docs 8000
```

Open http://localhost:8000. The published site serves static files on GitHub Pages and needs no visitor credentials.
