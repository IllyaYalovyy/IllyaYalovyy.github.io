# Illya Yalovyy’s project registry

[Browse the public directory](https://illyayalovyy.github.io/) for project descriptions, screenshots, setup instructions and current releases.

The initial survey covered all 21 public repositories on the account on 2026-11-21. Fifteen had a push on or after 2024-11-21. Categories distinguish installable tools from designs, exercises and forks. A recent push is a discovery criterion and does not establish a maintenance commitment.

## Maintain the directory

Edit `projects.json` to add, regroup or retire projects. Each entry identifies the source repository, public description, platform and setup guide. Where a screenshot is available, the entry records its upstream source and accessible description alongside the local WebP image. Review the roster periodically for new projects.

GitHub Pages serves the committed `docs/` directory from main. Each visit checks GitHub’s public latest-release API, caching successful lookups in the browser tab for one hour. A static snapshot keeps the directory usable without JavaScript or when rate-limited. Release links lead to the original notes and downloads. After editorial changes, regenerate the snapshot with the commands below and commit the updated source and docs together.

## Preview locally

With Python 3 and an authenticated GitHub CLI, run:

```sh
gh repo list IllyaYalovyy --visibility public --limit 500 --json name,latestRelease > /tmp/registry-inventory.json
python3 build.py /tmp/registry-inventory.json
python3 -m http.server --directory docs 8000
```

Open http://localhost:8000. The published site serves static files on GitHub Pages and needs no visitor credentials.
