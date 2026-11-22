# Illya Yalovyy’s project registry

[Browse the public directory](https://illyayalovyy.github.io/) for project descriptions, screenshots, setup instructions and current releases.

The initial survey covered all 21 public repositories on the account on 2026-11-21. Fifteen had a push on or after 2024-11-21. The current catalog is curated and also includes Minecraft projects distributed outside GitHub. A recent push is a discovery criterion and does not establish a maintenance commitment.

## Maintain the directory

Edit `projects.json` to add, regroup or retire projects. GitHub entries identify the repository and setup guide. Other entries use a stable id and an editorial release status. Where a screenshot is available, the entry includes an accessible description alongside the local WebP image. The host refresh reports recently pushed public repositories that are absent from the catalog and its explicit exclusion list.

GitHub Pages serves the committed `docs/` directory from main. Each visit checks GitHub’s public latest-release API, caching successful lookups in the browser tab for one hour. A static snapshot keeps the directory usable without JavaScript or when rate-limited. Release links lead to the original notes and downloads. After editorial changes, regenerate the snapshot with the commands below and commit the updated source and docs together.

## Scheduled maintenance

A Linux host with Python 3, Git, the GitHub CLI, flock and systemd can maintain the static snapshot. Sign in to gh as an account with push access to this registry. Routine runs use public repository metadata and Git object IDs. They make no model calls and require no paid services.

Run `maintenance/refresh --check` to inspect what the published branch would change. Run `maintenance/refresh --publish` to update it. Both use a disposable checkout of origin/main and leave working copies alone. A failed metadata query stops publication. An ordinary fast-forward push protects concurrent edits; a later run retries from the latest main. Identical inputs produce no commit. Automatic commits use Illya Yalovyy’s noreply identity and the host’s normal Git hooks.

Run `maintenance/install-timer` on the selected host. It installs a user timer for 09:00 local time with up to ten minutes of jitter and catches up missed runs when the user manager starts. Re-run the installer after changing the launcher or units. The checker and builder come from the registry on each run.

- Run now: `systemctl --user start project-registry.service`
- Check schedule: `systemctl --user list-timers project-registry.timer`
- Inspect the last run or failure: `journalctl --user -u project-registry.service -n 40`
- Read the last successful editorial scan: `cat "${XDG_STATE_HOME:-$HOME/.local/state}/project-registry/review.txt"`
- Disable the schedule: `systemctl --user disable --now project-registry.timer`

### Editorial review

The host publishes release versions, dates and links automatically. The local report flags new candidates, archived projects, and changed or missing upstream guides and screenshot files. A tracked repository disappearing from the public inventory stops the run for investigation. Private previews use only the metadata and screenshots explicitly approved for this site. Their status and external store listings require editorial confirmation.

For a reported item, inspect the affected file or diff. Update the relevant catalog fields or approved image as needed. Add intentionally omitted public repositories to `maintenance/policy.json`. To acknowledge a reviewed source revision, run the following in your editing checkout, then regenerate the site, inspect the diff and commit the changes together.

```sh
gh repo list IllyaYalovyy --visibility public --limit 1000 --json name,latestRelease,pushedAt,isArchived > /tmp/registry-inventory.json
python3 maintenance/inspect.py /tmp/registry-inventory.json --accept REPO
python3 build.py /tmp/registry-inventory.json
```

Use a human for publication decisions. If AI assistance is requested for ambiguous prose, give it only the affected catalog entry and the relevant upstream diff. Review its proposed wording before publishing.

## Preview locally

With Python 3 and an authenticated GitHub CLI, run:

```sh
gh repo list IllyaYalovyy --visibility public --limit 500 --json name,latestRelease > /tmp/registry-inventory.json
python3 build.py /tmp/registry-inventory.json
python3 -m http.server --directory docs 8000
```

Open http://localhost:8000. The published site serves static files on GitHub Pages and needs no visitor credentials.
