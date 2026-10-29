import json
import os
from collections import Counter
from datetime import datetime, timezone
from html import escape
from pathlib import Path
from urllib.request import Request, urlopen

USER = "Autistic-coder"
TOKEN = os.getenv("GH_TOKEN", "")
def get(url):
    headers = {"Accept": "application/vnd.github+json", "User-Agent": "github-profile-signal"}
    if TOKEN:
        headers["Authorization"] = "Bearer " + TOKEN
    with urlopen(Request(url, headers=headers), timeout=25) as resp:
        return json.load(resp)

profile = get(f"https://api.github.com/users/{USER}")
repos = []
page = 1
while True:
    batch = get(f"https://api.github.com/users/{USER}/repos?per_page=100&page={page}&type=owner")
    repos.extend(batch)
    if len(batch) < 100:
        break
    page += 1
originals = [r for r in repos if not r["fork"] and not r.get("private", False)]
stars = sum(r["stargazers_count"] for r in originals)
counts = Counter(r.get("language") for r in originals if r.get("language"))
colors = ["#ff7b24", "#37c8e8", "#b78cff", "#f64e9d", "#eaca3a"]
top = counts.most_common(5)
total = sum(c for _, c in top)
x, width = 32.0, 1036.0
segments = []
labels = []
for idx, (lang, count) in enumerate(top):
    w = width * count / total if total else 0
    segments.append(f'<rect x="{x:.1f}" y="218" width="{max(w-3,0):.1f}" height="10" rx="4" fill="{colors[idx]}"/>')
    lx = 32 + (idx % 3) * 345
    ly = 263 + (idx // 3) * 22
    labels.append(f'<circle cx="{lx+4}" cy="{ly-4}" r="3" fill="{colors[idx]}"/><text x="{lx+14}" y="{ly}" class="legend">{escape(lang)} ({count})</text>')
    x += w
if not top:
    labels.append('<text x="32" y="263" class="legend">No primary language data available</text>')
stamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="1100" height="320" viewBox="0 0 1100 320" role="img" aria-label="GitHub signal showing current repository count, stars, followers and primary languages">
<style>
.bg{{fill:#0d0e12;stroke:#35343d;stroke-width:1.4}}
.h{{font:700 14px monospace;fill:#ff791f}}
.ts{{font:12px monospace;fill:#a8b7cf}}
.n{{font:700 45px monospace;fill:#f0f6ff}}
.lab{{font:11px monospace;letter-spacing:1px;fill:#9cabbe}}
.legend{{font:12px monospace;fill:#dae1e9}}
</style>
<rect class="bg" x="1" y="1" width="1098" height="318" rx="20"/>
<text x="32" y="42" class="h">04 / GITHUB SIGNAL</text>
<text x="780" y="42" class="ts">{stamp}</text>
<text x="32" y="119" class="n">{profile["public_repos"]}</text>
<text x="377" y="119" class="n">{stars:02d}</text>
<text x="725" y="119" class="n">{profile["followers"]}</text>
<text x="32" y="147" class="lab">PUBLIC REPOSITORIES</text>
<text x="377" y="147" class="lab">STARS · OWNED ORIGINALS</text>
<text x="725" y="147" class="lab">FOLLOWERS</text>
<path d="M32 173H1068" stroke="#303239"/>
<text x="32" y="201" class="lab">PRIMARY REPO LANGUAGES</text>
{''.join(segments)}
{''.join(labels)}
</svg>'''
Path("assets/github-signal.svg").write_text(svg, encoding="utf-8")
print(f"Updated signal: {profile['public_repos']} repositories, {stars} stars, {profile['followers']} followers")
