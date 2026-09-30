"""Generate the animated SVG cards used in the profile README.

Run from the repository root:  python3 scripts/generate_svgs.py
Outputs: docs/banner.svg, docs/focus.svg, docs/hobbies.svg, docs/footer.svg
"""
import math
from pathlib import Path

DOCS = Path(__file__).resolve().parent.parent / "docs"
FONT = "'Segoe UI', Ubuntu, 'Helvetica Neue', Helvetica, Arial, sans-serif"

# Palette shared by every card (matches the tokyonight stats cards)
BG0, BG1, BG2 = "#0d1117", "#161b2e", "#1a1b27"
TILE, TILE_BORDER = "#161b22", "#30363d"
GREEN, BLUE, PINK, YELLOW = "#6fdc8c", "#58a6ff", "#ff4081", "#ffc837"
TEXT, MUTED = "#c9d1d9", "#8b949e"


def common_defs(w, h):
    return f'''
    <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="{BG0}"/><stop offset="0.6" stop-color="{BG1}"/><stop offset="1" stop-color="{BG2}"/>
    </linearGradient>
    <linearGradient id="brand" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="#4caf50"/><stop offset="1" stop-color="#2196f3"/>
    </linearGradient>
    <linearGradient id="txt" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0" stop-color="{GREEN}"/><stop offset="1" stop-color="{BLUE}"/>
    </linearGradient>
    <pattern id="grid" width="40" height="40" patternUnits="userSpaceOnUse">
      <path d="M40 0H0V40" fill="none" stroke="#ffffff" stroke-opacity="0.035"/>
    </pattern>
    <clipPath id="card"><rect width="{w}" height="{h}" rx="16"/></clipPath>'''


def background(w, h):
    return f'''<rect width="{w}" height="{h}" fill="url(#bg)"/>
    <rect width="{w}" height="{h}" fill="url(#grid)"/>'''


def contour(cx, cy, r, amp, phase, sx=1.35):
    """Closed, smooth, wobbly ring — one topographic contour line."""
    n = 72
    pts = []
    for k in range(n):
        t = 2 * math.pi * k / n
        rr = r * (1 + amp * (0.55 * math.sin(3 * t + phase) + 0.30 * math.sin(5 * t + 2 * phase)
                             + 0.15 * math.sin(7 * t + 0.5)))
        pts.append((cx + rr * math.cos(t) * sx, cy + rr * math.sin(t)))
    d = f"M{pts[0][0]:.1f},{pts[0][1]:.1f}"
    for i in range(n):  # Catmull-Rom -> cubic Bezier
        p0, p1, p2, p3 = pts[i - 1], pts[i], pts[(i + 1) % n], pts[(i + 2) % n]
        c1 = (p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6)
        c2 = (p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6)
        d += f" C{c1[0]:.1f},{c1[1]:.1f} {c2[0]:.1f},{c2[1]:.1f} {p2[0]:.1f},{p2[1]:.1f}"
    return d + "Z"


def contours(centers, opacity=0.55, drift=True):
    paths = []
    for cx, cy, count, base, ph in centers:
        for j in range(count):
            op = max(opacity - j * 0.045, 0.08)
            dash = "" if j % 3 else ' stroke-dasharray="6 5"'
            paths.append(f'<path d="{contour(cx, cy, base + j * 17, 0.10 + 0.012 * j, ph + j * 0.18)}" '
                         f'stroke="url(#brand)" stroke-opacity="{op:.2f}" stroke-width="{1.6 if j % 3 == 0 else 1}"{dash}/>')
    anim = ('<animateTransform attributeName="transform" type="translate" values="0 0; -6 4; 0 0" '
            'dur="14s" repeatCount="indefinite"/>') if drift else ""
    return '<g fill="none">\n      ' + "\n      ".join(paths) + f"\n      {anim}\n    </g>"


def svg(w, h, title, desc, body, extra_defs=""):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-labelledby="t d">
  <title id="t">{title}</title>
  <desc id="d">{desc}</desc>
  <defs>{common_defs(w, h)}{extra_defs}
  </defs>
  <g clip-path="url(#card)" font-family="{FONT}">
    {body}
  </g>
</svg>
'''


# --------------------------------------------------------------------------- banner

def banner():
    W, H = 1000, 280
    title = "Hi, I'm Sebastián Olarte"
    n, tx, tw = len(title), 60, 560  # fixed text box so the caret can follow exactly
    start, dur, total = 0.4, 2.6, 4.0
    kt, ws, xs = ["0"], ["0"], [f"{tx + 4:.1f}"]
    for i in range(n + 1):
        kt.append(f"{(start + dur * i / n) / total:.4f}")
        ws.append(f"{tw * i / n:.1f}")
        xs.append(f"{tx + tw * i / n + 4:.1f}")
    kt.append("1"); ws.append(ws[-1]); xs.append(xs[-1])

    defs = f'''
    <clipPath id="typing">
      <rect x="{tx - 4}" y="70" height="90" width="0">
        <animate attributeName="width" dur="{total}s" fill="freeze" calcMode="discrete" keyTimes="{';'.join(kt)}" values="{';'.join(ws)}"/>
      </rect>
    </clipPath>'''
    body = f'''{background(W, H)}
    {contours([(820, 150, 9, 18, 0.4), (40, 310, 6, 22, 2.1)])}
    <!-- survey benchmark marker -->
    <g transform="translate(820 150)" stroke="{GREEN}" fill="none">
      <circle r="5" fill="{GREEN}" stroke="none"/>
      <circle r="5">
        <animate attributeName="r" values="5;22" dur="2.4s" repeatCount="indefinite"/>
        <animate attributeName="stroke-opacity" values="0.9;0" dur="2.4s" repeatCount="indefinite"/>
      </circle>
      <path d="M-14 0H-8M8 0H14M0 -14V-8M0 8V14" stroke-width="1.5"/>
    </g>
    <text x="{tx}" y="72" font-size="15" letter-spacing="4" fill="{MUTED}">4.6097° N · 74.0817° W — BOGOTÁ, COLOMBIA</text>
    <g clip-path="url(#typing)">
      <text x="{tx}" y="138" font-size="52" font-weight="700" fill="url(#txt)" textLength="{tw}" lengthAdjust="spacingAndGlyphs">{title}</text>
    </g>
    <rect x="{tx + 4}" y="96" width="3" height="52" rx="1.5" fill="{PINK}">
      <animate attributeName="x" dur="{total}s" fill="freeze" calcMode="discrete" keyTimes="{';'.join(kt)}" values="{';'.join(xs)}"/>
      <animate attributeName="opacity" values="1;1;0;0" keyTimes="0;0.5;0.5;1" dur="0.9s" repeatCount="indefinite"/>
    </rect>
    <text x="{tx}" y="186" font-size="22" fill="{TEXT}" opacity="0">Software &amp; Topographic Engineering
      <animate attributeName="opacity" from="0" to="1" begin="3.1s" dur="0.8s" fill="freeze"/>
    </text>
    <text x="{tx}" y="220" font-size="17" fill="{MUTED}" opacity="0">Web development · Data science · Cartography &amp; GIS
      <animate attributeName="opacity" from="0" to="1" begin="3.5s" dur="0.8s" fill="freeze"/>
    </text>'''
    return svg(W, H, title, "Software and Topographic Engineering from Bogotá, Colombia", body, defs)


# --------------------------------------------------------------------------- tiles

def tile(x, y, w, h, icon, title, lines, delay):
    sub = "".join(f'<text x="{x + 116}" y="{y + h / 2 + 16 + 20 * i:.0f}" font-size="14" fill="{MUTED}">{l}</text>'
                  for i, l in enumerate(lines))
    return f'''<g opacity="0">
      <animate attributeName="opacity" from="0" to="1" begin="{delay:.2f}s" dur="0.6s" fill="freeze"/>
      <animateTransform attributeName="transform" type="translate" from="0 12" to="0 0" begin="{delay:.2f}s" dur="0.6s" fill="freeze"/>
      <rect x="{x}" y="{y}" width="{w}" height="{h}" rx="14" fill="{TILE}" fill-opacity="0.85" stroke="{TILE_BORDER}"/>
      <rect x="{x + 16}" y="{y + h / 2 - 43:.0f}" width="86" height="86" rx="14" fill="#0d1117" stroke="{TILE_BORDER}"/>
      <g transform="translate({x + 59} {y + h / 2:.0f})">{icon}</g>
      <text x="{x + 116}" y="{y + h / 2 - 10:.0f}" font-size="19" font-weight="700" fill="url(#txt)">{title}</text>
      {sub}
    </g>'''


def grid_card(W, heading, subheading, items, title, desc, tile_h=150):
    cols, margin, gap, top = 3, 30, 20, 96
    tw = (W - 2 * margin - (cols - 1) * gap) / cols
    rows = math.ceil(len(items) / cols)
    H = top + rows * tile_h + (rows - 1) * gap + margin
    tiles = []
    for i, (icon, name, lines) in enumerate(items):
        r, c = divmod(i, cols)
        tiles.append(tile(margin + c * (tw + gap), top + r * (tile_h + gap), tw, tile_h,
                          icon, name, lines, 0.15 + 0.12 * i))
    body = f'''{background(W, H)}
    {contours([(W - 60, H - 30, 6, 20, 1.2)], opacity=0.35)}
    <text x="{margin}" y="52" font-size="26" font-weight="700" fill="url(#txt)">{heading}</text>
    <text x="{margin}" y="76" font-size="14" letter-spacing="2" fill="{MUTED}">{subheading}</text>
    {"".join(tiles)}'''
    return svg(W, H, title, desc, body)


# icons are drawn around (0, 0) inside a 90x90 box

ICON_MUSIC = f'''
      <path d="M-26 8V0A26 26 0 0 1 26 0V8" fill="none" stroke="{MUTED}" stroke-width="4" stroke-linecap="round"/>
      <rect x="-32" y="2" width="11" height="22" rx="4" fill="{GREEN}"/>
      <rect x="21" y="2" width="11" height="22" rx="4" fill="{BLUE}"/>''' + "".join(
    f'''
      <rect x="{-14 + i * 6}" y="-2" width="4" height="26" rx="2" fill="url(#txt)" transform-origin="{-12 + i * 6} 24">
        <animateTransform attributeName="transform" type="scale" values="1 {a};1 {b};1 {c};1 {a}" dur="{d}s" repeatCount="indefinite"/>
      </rect>''' for i, (a, b, c, d) in enumerate(
        [(0.3, 0.9, 0.5, 1.1), (0.8, 0.4, 1, 0.9), (0.5, 1, 0.3, 1.2), (1, 0.6, 0.8, 1.0), (0.4, 0.8, 0.6, 1.3)]))

ICON_GAME = f'''
      <path d="M-30 -8Q-30 -18 -19 -18H19Q30 -18 30 -8L34 14Q35 23 26 23Q21 23 17 15H-17Q-21 23 -26 23Q-35 23 -34 14Z"
            fill="#21262d" stroke="{BLUE}" stroke-width="2"/>
      <path d="M-18 -6V6M-24 0H-12" stroke="{TEXT}" stroke-width="4" stroke-linecap="round"/>''' + "".join(
    f'''
      <circle cx="{cx}" cy="{cy}" r="3.6" fill="{col}">
        <animate attributeName="opacity" values="1;0.25;1" dur="1.6s" begin="{b}s" repeatCount="indefinite"/>
      </circle>''' for cx, cy, col, b in
    [(18, -8, GREEN, 0), (25, -1, PINK, 0.4), (18, 6, YELLOW, 0.8), (11, -1, BLUE, 1.2)])

ICON_MATH = f'''
      <path d="M-32 18H32M-26 26V-28" stroke="{MUTED}" stroke-width="1.5"/>
      <path d="M-26 0C-19 -22 -12 -22 -5 0S9 22 16 0S28 -18 32 -10" fill="none" stroke="url(#txt)" stroke-width="3"
            stroke-linecap="round" stroke-dasharray="130" stroke-dashoffset="130">
        <animate attributeName="stroke-dashoffset" values="130;0;0;130" keyTimes="0;0.45;0.8;1" dur="4s" repeatCount="indefinite"/>
      </path>
      <text x="8" y="-14" font-size="22" font-style="italic" fill="{YELLOW}" font-family="Georgia, 'Times New Roman', serif">∫</text>
      <text x="20" y="-14" font-size="15" font-style="italic" fill="{TEXT}" font-family="Georgia, 'Times New Roman', serif">π</text>'''

_board = "".join(
    f'<rect x="{-32 + c * 16}" y="{-32 + r * 16}" width="16" height="16" fill="{"#30363d" if (r + c) % 2 else "#8b949e"}" fill-opacity="{0.9 if (r + c) % 2 else 0.6}"/>'
    for r in range(4) for c in range(4))
# knight hops along L-shapes: (0,3) -> (1,1) -> (3,0) -> (2,2) -> (0,3)
_hops = [(0, 3), (1, 1), (3, 0), (2, 2), (0, 3)]
_kv = ";".join(f"{-24 + c * 16} {-24 + r * 16 + 7}" for c, r in _hops)
ICON_CHESS = f'''
      {_board}
      <rect x="-32" y="-32" width="64" height="64" fill="none" stroke="{TILE_BORDER}"/>
      <text font-size="21" text-anchor="middle" fill="{GREEN}" stroke="#0d1117" stroke-width="0.8" font-family="'Segoe UI Symbol', 'DejaVu Sans', 'Noto Sans Symbols 2', sans-serif">♞
        <animateTransform attributeName="transform" type="translate" calcMode="discrete" values="{_kv}" dur="4s" repeatCount="indefinite"/>
      </text>'''

ICON_TRAVEL = f'''
      <path id="route" d="M-30 20Q-4 -44 30 -8" fill="none" stroke="{MUTED}" stroke-width="2" stroke-dasharray="4 5"/>
      <circle cx="-30" cy="20" r="4" fill="{GREEN}"/>
      <path d="M30 -18a6 6 0 0 1 6 6c0 5-6 10-6 10s-6-5-6-10a6 6 0 0 1 6-6z" transform="translate(-6 2)" fill="{PINK}"/>
      <path d="M8 0L-6 -2L-8 -8L-11 -8L-9 -2L-13 -1.5L-15 -5L-17 -5L-15.5 0L-17 5L-15 5L-13 1.5L-9 2L-11 8L-8 8L-6 2Z" fill="{BLUE}">
        <animateMotion dur="3.6s" repeatCount="indefinite" rotate="auto" path="M-30 20Q-4 -44 30 -8"/>
      </path>'''


def _wheel(cx):
    spokes = "".join(f'<path d="M0 0L{13 * math.cos(a):.1f} {13 * math.sin(a):.1f}"/>'
                     for a in [k * math.pi / 3 for k in range(6)])
    return f'''<g transform="translate({cx} 12)">
        <circle r="13" fill="none" stroke="{TEXT}" stroke-width="2.5"/>
        <g stroke="{MUTED}" stroke-width="1">{spokes}
          <animateTransform attributeName="transform" type="rotate" from="0" to="360" dur="1.4s" repeatCount="indefinite"/>
        </g>
      </g>'''


ICON_BIKE = f'''
      <path d="M-36 29H36" stroke="{TILE_BORDER}" stroke-width="2" stroke-dasharray="8 6">
        <animate attributeName="stroke-dashoffset" from="0" to="28" dur="0.8s" repeatCount="indefinite"/>
      </path>
      {_wheel(-19)}
      {_wheel(19)}
      <path d="M-19 12L-1 12L-7 -8L-19 12M-7 -8H12M-1 12L12 -8L19 12" fill="none" stroke="url(#txt)" stroke-width="3" stroke-linejoin="round"/>
      <path d="M-13 -11H-2M9 -15H16" stroke="{TEXT}" stroke-width="3" stroke-linecap="round"/>
      <path d="M12 -8L11 -15" stroke="{TEXT}" stroke-width="2.5"/>'''

ICON_WEB = f'''
      <rect x="-34" y="-26" width="68" height="52" rx="6" fill="#21262d" stroke="{TILE_BORDER}"/>
      <path d="M-34 -16H34" stroke="{TILE_BORDER}"/>
      <circle cx="-27" cy="-21" r="2" fill="{PINK}"/><circle cx="-20" cy="-21" r="2" fill="{YELLOW}"/><circle cx="-13" cy="-21" r="2" fill="{GREEN}"/>
      <path d="M-12 -4L-20 5L-12 14M12 -4L20 5L12 14" fill="none" stroke="url(#txt)" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>
      <path d="M4 -6L-4 16" stroke="{MUTED}" stroke-width="2.5" stroke-linecap="round"/>
      <rect x="24" y="12" width="2" height="9" fill="{PINK}">
        <animate attributeName="opacity" values="1;1;0;0" keyTimes="0;0.5;0.5;1" dur="0.9s" repeatCount="indefinite"/>
      </rect>'''

ICON_DATA = f'''
      <path d="M-32 26H32M-32 26V-30" stroke="{MUTED}" stroke-width="1.5"/>''' + "".join(
    f'''
      <rect x="{-26 + i * 14}" y="{26 - hgt}" width="9" height="{hgt}" rx="2" fill="url(#brand)" fill-opacity="0.8">
        <animate attributeName="height" values="0;{hgt}" dur="1s" begin="{0.2 * i:.1f}s" fill="freeze"/>
        <animate attributeName="y" values="26;{26 - hgt}" dur="1s" begin="{0.2 * i:.1f}s" fill="freeze"/>
      </rect>''' for i, hgt in enumerate([18, 30, 24, 44])) + f'''
      <path d="M-22 4L-8 -10L6 -4L22 -26" fill="none" stroke="{YELLOW}" stroke-width="2.5" stroke-linecap="round"
            stroke-dasharray="70" stroke-dashoffset="70">
        <animate attributeName="stroke-dashoffset" values="70;0" begin="0.8s" dur="1.2s" fill="freeze"/>
      </path>
      <circle cx="22" cy="-26" r="3.5" fill="{YELLOW}"/>'''

ICON_GIS = f'''
      <g fill="none" stroke="url(#brand)">
        <path d="{contour(0, 8, 10, 0.12, 0.3, 1.5)}" stroke-width="1.5"/>
        <path d="{contour(0, 8, 18, 0.12, 0.6, 1.5)}" stroke-opacity="0.7"/>
        <path d="{contour(0, 8, 26, 0.12, 0.9, 1.3)}" stroke-opacity="0.45" stroke-dasharray="4 4"/>
      </g>
      <g>
        <animateTransform attributeName="transform" type="translate" values="0 0;0 -4;0 0" dur="1.6s" repeatCount="indefinite"/>
        <path d="M0 -30a11 11 0 0 1 11 11c0 9-11 19-11 19s-11-10-11-19a11 11 0 0 1 11-11z" fill="{PINK}"/>
        <circle cy="-19" r="4" fill="#0d1117"/>
      </g>
      <ellipse cy="2" rx="6" ry="2" fill="#000" fill-opacity="0.45"/>'''


def focus():
    items = [
        (ICON_WEB, "Web Development", ["React · Next.js · Node.js", "Tailwind · FastAPI"]),
        (ICON_DATA, "Data Science &amp; ML", ["Python · R · Jupyter", "Models, stats &amp; dashboards"]),
        (ICON_GIS, "Cartography &amp; GIS", ["Topography · Spatial data", "Satellite &amp; climate data"]),
    ]
    return grid_card(1000, "What I do", "WHERE MAPS, DATA AND THE WEB MEET", items,
                     "What I do", "Web development, data science and cartography", tile_h=140)


def hobbies():
    items = [
        (ICON_MUSIC, "Music", ["Listening to and", "enjoying bands"]),
        (ICON_GAME, "Gaming", ["Adventure and", "open-world games"]),
        (ICON_MATH, "Maths", ["Calculus and", "statistics"]),
        (ICON_CHESS, "Chess", ["Strategy, tactics", "and openings"]),
        (ICON_TRAVEL, "Traveling", ["Exploring new places", "and cultures"]),
        (ICON_BIKE, "Cycling", ["Riding my bike", "around the city"]),
    ]
    return grid_card(1000, "Beyond the code", "WHAT I ENJOY WHEN I'M NOT PROGRAMMING", items,
                     "Hobbies and interests", "Music, gaming, maths, chess, traveling and cycling")


def footer():
    W, H = 1000, 110
    body = f'''{background(W, H)}
    {contours([(120, 120, 5, 18, 0.8), (880, -10, 5, 18, 2.4)], opacity=0.4)}
    <text x="{W / 2}" y="52" text-anchor="middle" font-size="22" font-weight="700" fill="url(#txt)">Thanks for visiting!</text>
    <text x="{W / 2}" y="80" text-anchor="middle" font-size="14" letter-spacing="2" fill="{MUTED}">¡GRACIAS POR LA VISITA! · BOGOTÁ, COLOMBIA</text>'''
    return svg(W, H, "Thanks for visiting!", "Footer", body)


if __name__ == "__main__":
    for name, fn in {"banner": banner, "focus": focus, "hobbies": hobbies, "footer": footer}.items():
        (DOCS / f"{name}.svg").write_text(fn(), encoding="utf-8")
        print(f"docs/{name}.svg")
