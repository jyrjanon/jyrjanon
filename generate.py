"""Generates animated SVG sections for the GitHub profile README. Edit DATA, run: python generate.py"""
import random, math, os, json, base64, urllib.request, datetime
STAMP = 'live profile · animated'
from xml.dom import minidom

DATA = dict(
    handle="jyrjanon", name="Jayrajsinh Rana", initials="JR", ascii_text="JAYRAJSINH RANA",
    tagline="Computer Engineering Student | Python Developer | Open Source Contributor",
    tags=["TypeScript", "JavaScript", "HTML", "Python"],
    projects=[("TermsGuard", "A browser extension and web platform", "JavaScript", 43),
              ("anonjyrj", "No description provided.", "Markdown", 0),
              ("Finguide_AI", "No description provided.", "HTML", 100),
              ("openenv-email-support", "No description provided.", "Python", 98)],
    stats=[("Stars", 0, "#58a6ff"), ("Contributions", 47, "#22d3ee"), ("Repos", 11, "#a78bfa"), ("Followers", 8, "#4ade80")],
    contributions=47,
)

def get(url, raw=False, data=None, auth=False):
    h = {"User-Agent": "readme-gen"}
    if auth and os.environ.get("GH_TOKEN"): h["Authorization"] = "Bearer " + os.environ["GH_TOKEN"]
    r = urllib.request.urlopen(urllib.request.Request(url, data=data, headers=h), timeout=20)
    b = r.read()
    return (b, r.headers.get("Content-Type", "image/png")) if raw else json.loads(b)

def fetch_live(d):
    """Pulls current avatar, stats, repos and contribution calendar. Every step falls back to the static DATA."""
    global STAMP
    h = d["handle"]; d["avatar"] = None; d["cal"] = None; d["last"] = None
    STAMP = "LIVE · synced " + datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None).strftime("%H:%M:%S UTC")
    try:
        ev = get(f"https://api.github.com/users/{h}/events/public?per_page=1", auth=True)[0]
        ago = int((datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None) - datetime.datetime.strptime(ev["created_at"], "%Y-%m-%dT%H:%M:%SZ")).total_seconds() // 60)
        t = f"{ago}m ago" if ago < 60 else f"{ago//60}h ago" if ago < 1440 else f"{ago//1440}d ago"
        d["last"] = f'Last activity: {ev["type"].replace("Event","")} on {ev["repo"]["name"].split("/")[-1]} · {t}'
    except Exception as e: print("activity fallback:", e)
    try:
        b, ct = get(f"https://github.com/{h}.png?size=120", raw=True)
        d["avatar"] = f"data:{ct.split(';')[0]};base64," + base64.b64encode(b).decode()
    except Exception as e: print("avatar fallback:", e)
    try:
        u = get(f"https://api.github.com/users/{h}", auth=True)
        repos = [r for r in get(f"https://api.github.com/users/{h}/repos?per_page=100&sort=pushed", auth=True)]
        stars = sum(r["stargazers_count"] for r in repos)
        st = dict((k, (v, c)) for k, v, c in d["stats"])
        d["stats"] = [("Stars", stars, "#58a6ff"), ("Contributions", st["Contributions"][0], "#22d3ee"),
                      ("Repos", u["public_repos"], "#a78bfa"), ("Followers", u["followers"], "#4ade80")]
        top = [r for r in repos if not r["fork"]][:4]
        pr = []
        for r in top:
            try:
                L = get(r["languages_url"], auth=True); tot = sum(L.values()) or 1
                lang, n = max(L.items(), key=lambda x: x[1]) if L else ("-", 0)
                pr.append((r["name"], r["description"] or "No description provided.", lang, round(100 * n / tot)))
            except Exception: pr.append((r["name"], r["description"] or "No description provided.", r["language"] or "-", 0))
        if pr: d["projects"] = pr
    except Exception as e: print("stats fallback:", e)
    try:
        q = json.dumps({"query": 'query{user(login:"%s"){contributionsCollection{contributionCalendar{totalContributions weeks{contributionDays{contributionCount}}}}}}' % h}).encode()
        c = get("https://api.github.com/graphql", data=q, auth=True)["data"]["user"]["contributionsCollection"]["contributionCalendar"]
        d["cal"] = [[x["contributionCount"] for x in w["contributionDays"]] for w in c["weeks"]]
        d["contributions"] = c["totalContributions"]
        d["stats"] = [(a, d["contributions"] if a == "Contributions" else b, col) for a, b, col in d["stats"]]
    except Exception as e: print("calendar fallback:", e)
    return d

FONT = "'SF Mono','Fira Code',Consolas,'Courier New',monospace"
SANS = "'Segoe UI',-apple-system,Helvetica,Arial,sans-serif"

def wrap(w, h, body, css=""):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">
<defs>
<linearGradient id="bd" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#3b82f6"/><stop offset=".5" stop-color="#22d3ee" stop-opacity=".5"/><stop offset="1" stop-color="#8b5cf6"/></linearGradient>
<radialGradient id="g1"><stop offset="0" stop-color="#3b82f6" stop-opacity=".55"/><stop offset="1" stop-color="#3b82f6" stop-opacity="0"/></radialGradient>
<radialGradient id="g2"><stop offset="0" stop-color="#8b5cf6" stop-opacity=".45"/><stop offset="1" stop-color="#8b5cf6" stop-opacity="0"/></radialGradient>
<radialGradient id="g3"><stop offset="0" stop-color="#22c55e" stop-opacity=".35"/><stop offset="1" stop-color="#22c55e" stop-opacity="0"/></radialGradient>
<linearGradient id="tx" x1="0" x2="1"><stop offset="0" stop-color="#fff"/><stop offset="1" stop-color="#93c5fd"/></linearGradient>
<clipPath id="c"><rect x="1" y="1" width="{w-2}" height="{h-2}" rx="22"/></clipPath>
</defs>
<style>
text{{font-family:{SANS}}} .m{{font-family:{FONT}}}
@keyframes fl1{{0%,100%{{transform:translate(0,0)}}50%{{transform:translate(60px,20px)}}}}
@keyframes fl2{{0%,100%{{transform:translate(0,0)}}50%{{transform:translate(-70px,-15px)}}}}
@keyframes fade{{from{{opacity:0;transform:translateY(10px)}}to{{opacity:1;transform:none}}}}
@keyframes blink{{0%,49%{{opacity:1}}50%,100%{{opacity:0}}}}
@keyframes spin{{to{{transform:rotate(360deg)}}}}
@keyframes pulse{{0%,100%{{opacity:.5}}50%{{opacity:1}}}}
@keyframes ring{{from{{stroke-dashoffset:var(--c)}}to{{stroke-dashoffset:var(--o)}}}}
@keyframes bar{{from{{transform:scaleX(0)}}to{{transform:scaleX(1)}}}}
@keyframes sweep{{0%{{transform:translateX(-300px)}}100%{{transform:translateX(1100px)}}}}
{css}
</style>
<rect x="1" y="1" width="{w-2}" height="{h-2}" rx="22" fill="#070d18" stroke="url(#bd)" stroke-width="1.5"/>
<g clip-path="url(#c)">
<circle cx="180" cy="0" r="230" fill="url(#g1)" style="animation:fl1 9s ease-in-out infinite"/>
<circle cx="{w-120}" cy="{h}" r="220" fill="url(#g2)" style="animation:fl2 11s ease-in-out infinite"/>
<circle cx="{w*0.6}" cy="0" r="200" fill="url(#g3)" style="animation:fl1 13s ease-in-out infinite"/>
{body}
</g>
<circle cx="{w-20-len(STAMP)*6-12}" cy="{h-15}" r="3.5" fill="#22c55e" style="animation:pulse 1.4s infinite"/><text x="{w-20}" y="{h-12}" text-anchor="end" font-size="10" fill="#64748b" class="m">{STAMP}</text>
</svg>'''

def hero(d):
    if d.get("avatar"):
        av = f'<clipPath id="av"><circle cx="90" cy="90" r="43"/></clipPath><image href="{d["avatar"]}" x="47" y="47" width="86" height="86" preserveAspectRatio="xMidYMid slice" clip-path="url(#av)"/>'
    else:
        av = f'<text x="90" y="101" text-anchor="middle" font-size="30" font-weight="800" fill="#93c5fd">{d["initials"]}</text>'
    pills = ""; x = 40
    for i, t in enumerate(d["tags"]):
        wd = 22 + len(t) * 8
        pills += f'<g style="animation:fade .6s {0.4+i*0.15}s both"><rect x="{x}" y="196" width="{wd}" height="34" rx="17" fill="#0f1b30" stroke="#2563eb" stroke-opacity=".7"/><text x="{x+wd/2}" y="218" text-anchor="middle" font-size="14" font-weight="600" fill="#e2e8f0">{t}</text></g>'
        x += wd + 14
    body = f'''
<rect x="16" y="16" width="{940-32}" height="{260-32}" rx="18" fill="none" stroke="#1d4ed8" stroke-opacity=".35"/>
<g style="transform-origin:90px 90px;animation:spin 14s linear infinite"><circle cx="90" cy="90" r="52" fill="none" stroke="#3b82f6" stroke-width="2" stroke-dasharray="6 8"/></g>
<circle cx="90" cy="90" r="44" fill="#1e293b"/>{av}
<circle cx="90" cy="90" r="44" fill="none" stroke="#60a5fa" stroke-width="2"/>
<text x="170" y="62" font-size="13" letter-spacing="4" fill="#94a3b8" font-weight="700" class="m">@{d["handle"]}</text>
<text x="168" y="122" font-size="50" font-weight="800" fill="url(#tx)" style="animation:fade .8s both">{d["name"]}</text>
<text x="170" y="157" font-size="16" fill="#94a3b8" style="animation:fade .8s .2s both">{d["tagline"]}</text>
<rect x="0" y="40" width="3" height="180" fill="#60a5fa" opacity=".25" style="animation:sweep 6s linear infinite"/>
<circle cx="900" cy="46" r="5" fill="#3b82f6" style="animation:pulse 2s infinite"/>
<g transform="translate(130,0)">{pills}</g>'''
    # shift pills to left align with text
    body = body.replace('<g transform="translate(130,0)">', '<g transform="translate(0,0)">')
    return wrap(940, 260, body)

GLYPHS = {
"A": [".###.", "#...#", "#####", "#...#", "#...#"], "H": ["#...#", "#...#", "#####", "#...#", "#...#"],
"I": ["#####", "..#..", "..#..", "..#..", "#####"], "J": ["..###", "....#", "....#", "#...#", ".###."],
"N": ["#...#", "##..#", "#.#.#", "#..##", "#...#"], "R": ["####.", "#...#", "####.", "#..#.", "#...#"],
"S": [".####", "#....", ".###.", "....#", "####."], "Y": ["#...#", ".#.#.", "..#..", "..#..", "..#.."],
"B": ["####.", "#...#", "####.", "#...#", "####."], "E": ["#####", "#....", "####.", "#....", "#####"],
" ": ["...", "...", "...", "...", "..."]}
GLYPHS["J"] = ["..###", "...#.", "...#.", "#..#.", ".##.."]

def ascii_rows(t):
    rows = ["", "", "", "", ""]
    for ch in t.upper():
        g = GLYPHS.get(ch, GLYPHS[" "])
        for i in range(5): rows[i] += "".join("##" if c == "#" else "  " for c in g[i]) + "  "
    return [r.rstrip() for r in rows]

def wordmark(d):
    rows = ascii_rows(d["ascii_text"]); n = max(len(r) for r in rows); fs = 11; lh = 15
    tl = 860; y0 = 78; x0 = 40
    base = hot = ""
    for i, r in enumerate(rows):
        r2 = r.replace("##", "%@")
        base += f'<text x="{x0}" y="{y0+i*lh}" xml:space="preserve" textLength="{tl}" lengthAdjust="spacingAndGlyphs" class="m" font-size="{fs}" fill="url(#tx)" style="animation:fade .6s {0.6+i*0.15}s both">{r}</text>'
        hot += f'<text x="{x0}" y="{y0+i*lh}" xml:space="preserve" textLength="{tl}" lengthAdjust="spacingAndGlyphs" class="m" font-size="{fs}" fill="#22d3ee">{r2}</text>'
    body = f'''
<rect x="14" y="14" width="912" height="172" rx="14" fill="#0b1220" stroke="#1e293b"/>
<circle cx="36" cy="34" r="6" fill="#ff5f57"/><circle cx="56" cy="34" r="6" fill="#febc2e"/><circle cx="76" cy="34" r="6" fill="#28c840"/>
<clipPath id="t"><rect x="100" y="24" width="0" height="20"><animate attributeName="width" values="0;260;260;0" keyTimes="0;.2;.9;1" dur="10s" repeatCount="indefinite"/></rect></clipPath>
<text x="104" y="38" font-size="11" fill="#64748b" class="m" clip-path="url(#t)">{d["handle"]}@github:~$ ./wordmark.sh --name</text>
{base}
<clipPath id="sc"><rect x="0" y="60" width="70" height="90"><animate attributeName="x" values="-80;940" dur="4s" repeatCount="indefinite"/></rect></clipPath>
<g clip-path="url(#sc)" style="filter:drop-shadow(0 0 4px #22d3ee)">{hot}</g>
<rect x="{x0+tl+6}" y="{y0+3*lh}" width="9" height="16" fill="#60a5fa" style="animation:blink 1s steps(1) infinite"/>
<text x="470" y="172" text-anchor="middle" font-size="12" fill="#475569" class="m">$ whoami → student · builder · open-source</text>'''
    return wrap(940, 200, body)

def projects(d):
    body = '<text x="36" y="44" font-size="13" letter-spacing="4" fill="#3b82f6" class="m" font-weight="700">PROJECTS.LIST</text><text x="190" y="44" font-size="12" fill="#475569" class="m">./projects.sh --all</text>'
    body += f'<text x="904" y="44" text-anchor="end" font-size="12" fill="#64748b" class="m">{len(d["projects"])} projects</text><line x1="30" y1="58" x2="910" y2="58" stroke="#1d4ed8" stroke-opacity=".6"/>'
    C = 2 * math.pi * 30
    for i, (nm, desc, lang, pct) in enumerate(d["projects"]):
        x = 30 + (i % 2) * 450; y = 78 + (i // 2) * 170; off = C * (1 - pct / 100)
        col = "#facc15" if pct < 50 else "#f97316" if pct == 100 else "#38bdf8"
        body += f'''<g style="animation:fade .7s {i*0.2}s both">
<rect x="{x}" y="{y}" width="430" height="150" rx="12" fill="#0b1424" stroke="#1d4ed8" stroke-opacity=".6"/>
<text x="{x+16}" y="{y+22}" font-size="11" fill="#64748b" class="m">● {nm}</text>
<circle cx="{x+410}" cy="{y+20}" r="5" fill="#334155"/>
<text x="{x+16}" y="{y+62}" font-size="22" font-weight="800" fill="#f1f5f9" class="m">{nm if len(nm)<18 else nm[:17]+"…"}<tspan fill="#3b82f6" style="animation:blink 1s steps(1) infinite"> _</tspan></text>
<text x="{x+16}" y="{y+88}" font-size="13" fill="#64748b">{desc}</text>
<rect x="{x+16}" y="{y+104}" width="{len(lang)*9+22}" height="24" rx="12" fill="#0f2547" stroke="#2563eb"/><text x="{x+27}" y="{y+120}" font-size="11" fill="#60a5fa" font-weight="600">{lang}</text>
<circle cx="{x+365}" cy="{y+85}" r="30" fill="none" stroke="#1e293b" stroke-width="9"/>
<circle cx="{x+365}" cy="{y+85}" r="30" fill="none" stroke="{col}" stroke-width="9" stroke-linecap="round" stroke-dasharray="{C:.1f}" style="--c:{C:.1f};--o:{off:.1f};stroke-dashoffset:{off:.1f};animation:ring 2s {0.3+i*0.2}s ease-out both;transform:rotate(-90deg);transform-origin:{x+365}px {y+85}px"/>
<text x="{x+365}" y="{y+90}" text-anchor="middle" font-size="13" font-weight="700" fill="#e2e8f0">{pct}%</text>
</g>'''
    return wrap(940, 440, body)

def stats(d):
    body = f'<text x="36" y="56" font-size="30" font-weight="800" fill="#f8fafc">Profile Signal</text><text x="36" y="82" font-size="14" fill="#64748b">{d.get("last") or "Live GitHub stats, animated"}</text>'
    mx = max(v for _, v, _ in d["stats"]) or 1
    for i, (lab, val, col) in enumerate(d["stats"]):
        x = 30 + i * 220; frac = max(val / mx, 0.06)
        body += f'''<g style="animation:fade .7s {i*0.15}s both"><rect x="{x}" y="100" width="200" height="110" rx="14" fill="#0b1424" stroke="#1d4ed8" stroke-opacity=".6"/>
<text x="{x+18}" y="130" font-size="13" fill="#94a3b8" font-weight="600">{lab}</text>
<text x="{x+18}" y="172" font-size="40" font-weight="800" fill="{col}">{val}</text>
<rect x="{x+18}" y="188" width="164" height="8" rx="4" fill="#1e293b"/>
<rect x="{x+18}" y="188" width="{164*frac:.0f}" height="8" rx="4" fill="{col}" style="transform-origin:{x+18}px 0;animation:bar 1.6s {0.3+i*0.15}s ease-out both"/></g>'''
    return wrap(940, 240, body)

def heatmap(d):
    random.seed(7); W = 53; cells = {}
    if d.get("cal"):
        cal = d["cal"][-W:]
        for wk, days in enumerate(cal):
            for dy, c in enumerate(days): cells[(wk, dy)] = 0 if c == 0 else 1 if c < 2 else 2 if c < 4 else 3 if c < 7 else 4
    else:
        while len(cells) < min(d["contributions"], 40):
            cells[(random.randrange(W), random.randrange(7))] = random.choice([1, 1, 2, 3, 4])
    shades = ["#111b2e", "#1e3a8a", "#2563eb", "#3b82f6", "#60a5fa"]
    body = f'<text x="36" y="52" font-size="26" font-weight="800" fill="#f8fafc">Contribution Activity</text><text x="36" y="76" font-size="14" fill="#64748b">{d["contributions"]} contributions in the last year</text>'
    for wk in range(W):
        for dy in range(7):
            lv = cells.get((wk, dy), 0); x = 36 + wk * 16.4; y = 96 + dy * 17
            anim = f' style="animation:fade .5s {wk*0.03:.2f}s both"'
            if lv >= 3: anim = f' style="animation:fade .5s {wk*0.03:.2f}s both,pulse 2.5s {random.random()*2:.1f}s ease-in-out infinite"'
            body += f'<rect x="{x:.1f}" y="{y}" width="13" height="13" rx="3" fill="{shades[lv]}"{anim}/>'
    return wrap(940, 240, body)

def readme(d, live=False):
    names = [("hero", d["name"]), ("wordmark", "wordmark"), ("projects", "Projects"), ("stats", "Profile stats"), ("heatmap", "Contribution activity")]
    src = (lambda k: f"https://YOUR-APP.vercel.app/api/svg?s={k}") if live else (lambda k: f"assets/{k}.svg")
    return "".join(f'<p align="center"><img src="{src(k)}" alt="{a}" width="100%"/></p>\n' for k, a in names)

out = {"hero": hero, "wordmark": wordmark, "projects": projects, "stats": stats, "heatmap": heatmap}
if __name__ == "__main__":
    DATA = fetch_live(DATA)
    for k, f in out.items():
        x = f(DATA); minidom.parseString(x)
        open(f"assets/{k}.svg", "w").write(x)
    if not os.path.exists("README.md"):  # never overwrite your edited README
        open("README.md", "w").write(readme(DATA, live=True))
    open("README.static.md", "w").write(readme(DATA))
    print("done")
