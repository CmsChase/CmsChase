"""Generate self-hosted GitHub badges (no Shields.io dependency)."""
import json
import os
import subprocess
from pathlib import Path
from urllib.request import Request, urlopen
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"
REPOS = {"rea": "morluto/rea", "deno": "denoland/deno", "filetime": "alexcrichton/filetime"}

def stars(repo):
    headers = {"Accept": "application/vnd.github+json",
               "X-GitHub-Api-Version": "2022-11-28",
               "User-Agent": "CmsChase-profile"}
    if os.environ.get("GH_TOKEN"):
        headers["Authorization"] = "Bearer " + os.environ["GH_TOKEN"]
    with urlopen(Request("https://api.github.com/repos/" + repo, headers=headers), timeout=20) as resp:
        return int(json.load(resp)["stargazers_count"])

def compact(n):
    if n >= 1_000_000:
        return f"{n/1_000_000:.1f}M"
    if n >= 10_000:
        return f"{n/1000:.1f}k"
    return f"{n:,}"

def svg(label, value):
    label, value = escape(label), escape(value)
    lw, rw = max(44, int(len(label) * 7 + 16)), max(50, int(len(value) * 7.4 + 18))
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{lw+rw}" height="20" role="img" aria-label="{label}: {value}">
<title>{label}: {value}</title>
<rect width="{lw+rw}" height="20" rx="3" fill="#555"/>
<path d="M{lw} 0h{rw}v20h-{rw}z" fill="#168363"/>
<g fill="#fff" text-anchor="middle" font-family="Verdana,DejaVu Sans,sans-serif" font-size="11">
<text x="{lw/2:.1f}" y="14">{label}</text><text x="{lw+rw/2:.1f}" y="14">{value}</text>
</g></svg>
'''

def main():
    ASSETS.mkdir(exist_ok=True)
    for name, repo in REPOS.items():
        (ASSETS / f"stars-{name}.svg").write_text(svg("stars", compact(stars(repo))), encoding="utf-8")
    date = subprocess.check_output(["git", "log", "-1", "--format=%cs", "--", "README.md"],
                                    cwd=ROOT, text=True).strip()
    if not date:
        raise RuntimeError("No README.md commit history found")
    (ASSETS / "readme-updated.svg").write_text(svg("README updated", date), encoding="utf-8")

if __name__ == "__main__":
    main()
