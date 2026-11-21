// The static release snapshot remains readable offline and without JavaScript.
async function refreshReleases() {
  const rows = new Map(Array.from(document.querySelectorAll("tbody tr"), row =>
    [row.querySelector("a").hash.slice(1), row]));
  async function refresh(card) {
    const repo = card.id;
    const key = "latest:" + repo;
    let cached;
    try { cached = JSON.parse(sessionStorage.getItem(key)); } catch {}
    let release;
    if (cached && Date.now() - cached.time < 3600000) {
      release = cached.release;
    } else {
      const response = await fetch("https://api.github.com/repos/IllyaYalovyy/" + repo + "/releases/latest");
      if (response.status === 404) release = null;
      else if (response.ok) release = await response.json();
      else throw new Error("Release lookup unavailable");
      try { sessionStorage.setItem(key, JSON.stringify({time: Date.now(), release})); } catch {}
    }
    const version = card.querySelector(".version");
    if (!release) {
      rows.delete(repo);
      version.textContent = "No GitHub release";
      return;
    }
    const link = document.createElement("a");
    link.href = "https://github.com/IllyaYalovyy/" + repo + "/releases/tag/" + encodeURIComponent(release.tag_name);
    link.textContent = release.tag_name;
    version.replaceChildren(link);
    const row = document.createElement("tr");
    const heading = document.createElement("th");
    heading.scope = "row";
    const project = document.createElement("a");
    project.href = "#" + repo;
    project.textContent = card.querySelector("h3").textContent;
    heading.append(project);
    row.append(heading);
    row.insertCell().append(link.cloneNode(true));
    const date = document.createElement("time");
    date.dateTime = release.published_at;
    date.textContent = release.published_at.slice(0, 10);
    row.insertCell().append(date);
    rows.set(repo, row);
  }
  const results = await Promise.allSettled(Array.from(document.querySelectorAll("article[data-github]"), refresh));
  document.querySelector("tbody").replaceChildren(...Array.from(rows.values()).sort((a,b) =>
    b.querySelector("time").dateTime.localeCompare(a.querySelector("time").dateTime)));
  if (results.every(r => r.status === "fulfilled")) {
    document.querySelector(".ledger .meta").textContent = "Release data checked within the past hour";
  }
}
refreshReleases();
