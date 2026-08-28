#!/usr/bin/env python3
import json
import os
import re
import urllib.request
from datetime import datetime

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
API = "https://api.github.com"
SIMPLE_ICONS = "https://raw.githubusercontent.com/simple-icons/simple-icons/e178757a97ed3b8e8477d825e77a60e6073977ea/icons/{}.svg"

PYTHON_LOGO = "M14.25.18l.9.2.73.26.59.3.45.32.34.34.25.34.16.33.1.3.04.26.02.2-.01.13V8.5l-.05.63-.13.55-.21.46-.26.38-.3.31-.33.25-.35.19-.35.14-.33.1-.3.07-.26.04-.21.02H8.77l-.69.05-.59.14-.5.22-.41.27-.33.32-.27.35-.2.36-.15.37-.1.35-.07.32-.04.27-.02.21v3.06H3.17l-.21-.03-.28-.07-.32-.12-.35-.18-.36-.26-.36-.36-.35-.46-.32-.59-.28-.73-.21-.88-.14-1.05-.05-1.23.06-1.22.16-1.04.24-.87.32-.71.36-.57.4-.44.42-.33.42-.24.4-.16.36-.1.32-.05.24-.01h.16l.06.01h8.16v-.83H6.18l-.01-2.75-.02-.37.05-.34.11-.31.17-.28.25-.26.31-.23.38-.2.44-.18.51-.15.58-.12.64-.1.71-.06.77-.04.84-.02 1.27.05zm-6.3 1.98l-.23.33-.08.41.08.41.23.34.33.22.41.09.41-.09.33-.22.23-.34.08-.41-.08-.41-.23-.33-.33-.22-.41-.09-.41.09zm13.09 3.95l.28.06.32.12.35.18.36.27.36.35.35.47.32.59.28.73.21.88.14 1.04.05 1.23-.06 1.23-.16 1.04-.24.86-.32.71-.36.57-.4.45-.42.33-.42.24-.4.16-.36.09-.32.05-.24.02-.16-.01h-8.22v.82h5.84l.01 2.76.02.36-.05.34-.11.31-.17.29-.25.25-.31.24-.38.2-.44.17-.51.15-.58.13-.64.09-.71.07-.77.04-.84.01-1.27-.04-1.07-.14-.9-.2-.73-.25-.59-.3-.45-.33-.34-.34-.25-.34-.16-.33-.1-.3-.04-.25-.02-.2.01-.13v-5.34l.05-.64.13-.54.21-.46.26-.38.3-.32.33-.24.35-.2.35-.14.33-.1.3-.06.26-.04.21-.02.13-.01h5.84l.69-.05.59-.14.5-.21.41-.28.33-.32.27-.35.2-.36.15-.36.1-.35.07-.32.04-.28.02-.21V6.07h2.09l.14.01zm-6.47 14.25l-.23.33-.08.41.08.41.23.33.33.23.41.08.41-.08.33-.23.23-.33.08-.41-.08-.41-.23-.33-.33-.23-.41-.08-.41.08z"

# Los lenguajes se identifican por nombre; aquí el logo (Simple Icons) y color.
LANGUAGES = {
    "Python": {"logo": "python", "color": "#FFD43B"},
}

HEADERS = {"User-Agent": "github-stats-cards"}
TOKEN = os.environ.get("GHSTATS_TOKEN")


def esc(s):
    return (s or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def fetch(url):
    h = dict(HEADERS)
    if TOKEN:
        h["Authorization"] = f"token {TOKEN}"
    req = urllib.request.Request(url, headers=h)
    with urllib.request.urlopen(req) as r:
        return json.load(r)


def fetch_logo(name):
    url = SIMPLE_ICONS.format(name)
    try:
        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req) as r:
            data = r.read().decode()
        start = data.index('d="') + 3
        end = data.index('"', start)
        return data[start:end]
    except Exception:
        return None


def truncate(s, n):
    s = s or ""
    return s if len(s) <= n else s[: n - 1].rstrip() + "…"


def render_card(repo, cfg):
    name = esc(repo["name"])
    desc = esc(truncate(repo.get("description") or cfg.get("fallback_desc", ""), 52))
    lang = repo.get("language") or cfg.get("fallback_lang", "")
    stars = repo.get("stargazers_count", 0)
    forks = repo.get("forks_count", 0)
    meta = esc(cfg.get("fallback_desc", ""))

    lang_cfg = LANGUAGES.get(lang, {})
    logo_path = fetch_logo(lang_cfg.get("logo", lang.lower())) or PYTHON_LOGO
    lang_color = lang_cfg.get("color", "#abb2bf")

    star_icon = "★"
    fork_icon = "⑂"

    svg = f'''<svg width="420" height="112" viewBox="0 0 420 112" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="{name}">
  <defs>
    <style>
      .bg {{ fill: #282c34; }}
      .border {{ fill: none; stroke: #3e4451; stroke-width: 1.5; }}
      .name {{ font-family: 'Segoe UI', Arial, sans-serif; font-size: 16px; font-weight: 600; fill: #e5c07b; }}
      .desc {{ font-family: 'Segoe UI', Arial, sans-serif; font-size: 12px; fill: #abb2bf; }}
      .meta {{ font-family: 'Segoe UI', Arial, sans-serif; font-size: 12px; fill: #5c6370; }}
      .lang {{ font-family: 'Segoe UI', Arial, sans-serif; font-size: 12px; fill: #abb2bf; }}
      .lang-dot {{ fill: {lang_color}; }}
    </style>
  </defs>

  <rect class="bg" width="420" height="112" rx="10"/>
  <rect class="border" x="0.75" y="0.75" width="418.5" height="110.5" rx="9.25"/>

  <g transform="translate(22, 26)">
    <circle cx="19" cy="19" r="19" fill="#1e2024"/>
    <g transform="translate(5, 5) scale(1.1667)">
      <path fill="{lang_color}" d="{logo_path}"/>
    </g>
  </g>

  <g transform="translate(62, 34)">
    <text class="name" x="0" y="0">{name}</text>
    <text class="desc" x="0" y="24">{desc}</text>
  </g>

  <g transform="translate(62, 90)">
    <circle class="lang-dot" cx="4" cy="4" r="4"/>
    <text class="lang" x="15" y="8">{esc(lang)}</text>
    <text class="meta" x="130" y="8">{star_icon} {stars}</text>
    <text class="meta" x="200" y="8">{fork_icon} {forks}</text>
  </g>
</svg>
'''
    return svg


def main():
    with open(os.path.join(ROOT, "projects.json"), encoding="utf-8") as f:
        cfg = json.load(f)
    owner = cfg["owner"]
    out_dir = os.path.join(ROOT, "assets", "cards")
    os.makedirs(out_dir, exist_ok=True)

    for repo_name in cfg["repos"]:
        try:
            repo = fetch(f"{API}/repos/{owner}/{repo_name}")
        except Exception as e:
            print(f"WARN: no se pudo obtener {repo_name}: {e}")
            continue
        slug = re.sub(r"[^a-z0-9]+", "-", repo_name.lower()).strip("-")
        svg = render_card(repo, {"fallback_desc": repo.get("description", ""), "fallback_lang": repo.get("language", "")})
        path = os.path.join(out_dir, f"{slug}.svg")
        with open(path, "w", encoding="utf-8") as f:
            f.write(svg)
        print(f"OK: {slug}.svg ({repo.get('language','?')})")


if __name__ == "__main__":
    main()
