# Genera hero e schede del profilo: python3 gen.py
import base64, math
from xml.dom.minidom import parseString

INK, CARD, LINE = "#0b0b0c", "#111112", "#2a2a2d"
PAPER, MUTE, DIM = "#ecebe6", "#8d8d8d", "#55555a"
ORANGE, BLUE = "#ff6a00", "#0517ff"
MONO = "font-family=\"ui-monospace,'SF Mono',SFMono-Regular,Menlo,Consolas,'Liberation Mono',monospace\""
SANS = "font-family=\"-apple-system,BlinkMacSystemFont,'Segoe UI',Helvetica,Arial,sans-serif\""
STILL = "@media (prefers-reduced-motion:reduce){*{animation:none!important}"

# ---- hero: terminale con una forma ASCII che si rifinisce da v0.1 a v1.0 ----
T, N = 8.0, 80                        # durata del ciclo, fotogrammi
CUTS = [1.3, 2.6, 3.9, 5.2]           # confini tra v0.1 | v0.2 | v0.5 | v0.9 | v1.0
ROUGH = [.42, .28, .16, .07, 0]
BACK = 7.6                            # da qui la forma torna grezza e il ciclo riparte
VERS = ["v0.1", "v0.2", "v0.5", "v0.9", "v1.0"]
COLS, ROWS, CW, RH, SCALE = 32, 16, 7.8, 15, 82   # CW = 0.6em a 13px, la larghezza dei mono comuni
RAMP = " .:-=+*#%@"
X0, YA, T0 = 29, 78, 1.15             # margine sinistro, inizio della forma, istante in cui parte l'output

def smooth(u): return u * u * (3 - 2 * u)

def rough(t):
    if t >= BACK: return ROUGH[0] * smooth((t - BACK) / (T - BACK))
    i = sum(t >= c for c in CUTS)
    if i < 4 and t > CUTS[i] - .5:
        return ROUGH[i] + (ROUGH[i + 1] - ROUGH[i]) * smooth((t - CUTS[i] + .5) / .5)
    return ROUGH[i]

def bump(x, y, z):
    return (math.sin(3.2*x + 1.7) * math.cos(2.3*y + .6) + math.sin(2.9*y + 3.1*z + .9)
            + math.sin(4.1*z - 1.2*x + 2.2) + .5 * math.sin(7*x + 5*y + 3*z)) / 3.5

def dist(x, y, z, a, k):              # negativa dentro la forma
    d = math.sqrt(x*x + y*y + z*z) or 1e-9
    ca, sa = math.cos(a), math.sin(a)
    return d - 1 - k * bump((x*ca + z*sa) / d, y / d, (z*ca - x*sa) / d)

def frame(t):
    a, k = 2 * math.pi * t / T, rough(t)
    lx, ly, lz = .9 * math.sin(4 * math.pi * t / T), -.5, .75   # la luce oscilla: anche la sfera pulita si muove
    ln = math.sqrt(lx*lx + ly*ly + lz*lz)
    rows = []
    for r in range(ROWS):
        row = ""
        for c in range(COLS):
            x, y, z = (c + .5 - COLS/2) * CW / SCALE, (r + .5 - ROWS/2) * RH / SCALE, 1.5
            while z > -1.5 and dist(x, y, z, a, k) > 0: z -= .04
            if z <= -1.5: row += " "; continue
            e = .02
            nx = dist(x+e, y, z, a, k) - dist(x-e, y, z, a, k)
            ny = dist(x, y+e, z, a, k) - dist(x, y-e, z, a, k)
            nz = dist(x, y, z+e, a, k) - dist(x, y, z-e, a, k)
            lum = max(0, (nx*lx + ny*ly + nz*lz) / (math.sqrt(nx*nx + ny*ny + nz*nz) * ln))
            row += RAMP[1 + int(lum * 8.99)]
        rows.append(row)
    return rows

def shape():
    out = ""
    for i in range(N):
        t = i * T / N
        g = ""
        for r, row in enumerate(frame(t)):
            s = row.strip()
            if s:   # textLength fissa la larghezza qualunque sia il font mono del lettore
                g += f'<text x="{X0 + (len(row) - len(row.lstrip())) * CW:.1f}" y="{YA + 11 + r * RH}" textLength="{len(s) * CW:.1f}">{s}</text>'
        still = " k" if i == int(6.4 / T * N) else ""
        fill = ORANGE if CUTS[3] <= t < BACK else PAPER
        out += f'<g class="f{still}" fill="{fill}" style="animation-delay:{T0 + t:.2f}s">{g}</g>'
    return f'<g {MONO} font-size="13" xml:space="preserve">{out}</g>'

def steps():
    y, pitch = YA + ROWS * RH + 24, (COLS * CW - 26.4) / 4
    start, end = [0] + CUTS, CUTS + [BACK]
    css = out = ""
    for i, v in enumerate(VERS):
        last = i == 4
        k = {0: DIM, 100 * start[i] / T: ORANGE if last else PAPER, 100 * end[i] / T: DIM if last else MUTE, 100: DIM if last else MUTE}
        css += f"@keyframes v{i}{{" + "".join(f"{p:.2f}%{{fill:{c}}}" for p, c in sorted(k.items())) + "}"
        x = X0 + i * pitch
        out += f'<text x="{x:.1f}" y="{y}" fill="{ORANGE if last else MUTE}" style="animation:v{i} {T}s steps(1,end) {T0}s infinite">{v}</text>'
        if not last:
            out += f'<rect x="{x + 32:.1f}" y="{y - 4}" width="{pitch - 38:.1f}" height="1" fill="{DIM}"/>'
    return css, f'<g {MONO} font-size="11">{out}</g>'

def hero():
    W, H = 846, 398
    on = lambda d: f'class="i" style="animation-delay:{d:.2f}s"'
    chevron = lambda y, extra="": f'<path d="M{X0 + 1} {y - 9}l5 4.5-5 4.5" fill="none" stroke="{ORANGE}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" {extra}/>'
    cmd = "".join(f'<text x="{X0 + (2 + i) * CW:.1f}" y="60" {on(.5 + .09 * i)}>{ch}</text>' for i, ch in enumerate("fetch"))
    xi, xv = X0 + COLS * CW + 30, X0 + COLS * CW + 30 + 9 * CW
    rows = [("builds", "desktop apps · firmware · iPhone · Android"), ("stack", "Rust · Swift · C++ · Kotlin · TypeScript"),
            ("web", "iterix.it"), ("privacy", "no cloud, no accounts. It stays on your device.")]
    info = (f'<text x="{xi}" y="124" font-size="15" font-weight="700" fill="{PAPER}" {on(T0 + .05)}>skfallin</text>'
            f'<text x="{xi}" y="146" fill="{MUTE}" {on(T0 + .1)}>Iterate until it ships.</text>'
            f'<rect x="{xi}" y="160" width="{841 - 24 - xi:.1f}" height="1" fill="{LINE}" {on(T0 + .15)}/>')
    for i, (k, v) in enumerate(rows):
        info += f'<g {on(T0 + .2 + .05 * i)}><text x="{xi}" y="{186 + i * 22}" fill="{ORANGE}">{k}</text><text x="{xv:.1f}" y="{186 + i * 22}" fill="{PAPER}">{v}</text></g>'
    info += f'<g {on(T0 + .5)}>' + "".join(f'<rect x="{xi + i * 20}" y="{184 + len(rows) * 22}" width="14" height="14" rx="2" fill="{c}"/>' for i, c in enumerate([LINE, DIM, PAPER, ORANGE, BLUE])) + "</g>"
    scss, stepper = steps()
    css = ("text{white-space:pre}.i{opacity:0;animation:on 1ms linear forwards}@keyframes on{to{opacity:1}}"
           f".f{{visibility:hidden;animation:f {T}s steps(1,end) infinite}}@keyframes f{{0%{{visibility:visible}}{100 / N}%,100%{{visibility:hidden}}}}"
           f".c1{{animation:mv .45s steps(5,start) .5s forwards,off 1ms linear {T0}s forwards}}@keyframes mv{{to{{transform:translateX({5 * CW}px)}}}}@keyframes off{{to{{opacity:0}}}}"
           ".c2{opacity:0;animation:bl 1.1s steps(1,end) 1.9s infinite}@keyframes bl{0%{opacity:1}50%{opacity:0}}"
           + scss + STILL + ".i,.c2{opacity:1}.c1{opacity:0}.k{visibility:visible}}")
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="A terminal. The command fetch prints skfallin: iterate until it ships, with an ASCII shape that refines from a rough v0.1 into a clean v1.0 sphere."><title>skfallin</title>
<style>{css}</style>
<rect x="5.5" y=".5" width="835" height="{H - 1}" rx="12" fill="{INK}" stroke="{LINE}"/>
<path d="M6 33.5h834" stroke="{LINE}"/>
<circle cx="26" cy="17" r="5" fill="{LINE}"/><circle cx="43" cy="17" r="5" fill="{LINE}"/><circle cx="60" cy="17" r="5" fill="{LINE}"/>
<text x="423" y="21" text-anchor="middle" {MONO} font-size="11.5" fill="{MUTE}">skfallin — zsh</text>
<g {MONO} font-size="13" fill="{PAPER}">{chevron(60)}{cmd}<rect class="c1" x="{X0 + 2 * CW:.1f}" y="48" width="{CW}" height="16"/>
{info}{chevron(H - 24, on(1.9))}<rect class="c2" x="{X0 + 2 * CW:.1f}" y="{H - 36}" width="{CW}" height="16"/></g>
<g {on(T0)}>{shape()}{stepper}</g>
</svg>'''

# ---- schede ----
def card(w, h, vh, visual, name, line, tag="", css=""):
    big = w > 300
    text = f'<text x="21" y="{vh + (31 if big else 27)}" {SANS} font-size="{16 if big else 14}" font-weight="600" fill="{PAPER}">{name}</text>'
    text += f'<text x="21" y="{vh + (53 if big else 46)}" {SANS} font-size="{12.5 if big else 11.5}" fill="{MUTE}">{line}</text>'
    if tag: text += f'<text x="{w - 21}" y="{vh + 30}" text-anchor="end" {MONO} font-size="10.5" fill="{MUTE}">{tag}</text>'
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h + 10}" viewBox="0 0 {w} {h + 10}" role="img" aria-label="{name}. {line}"><title>{name}</title>
<style>{css}{STILL}}}</style>
<defs><clipPath id="c"><rect x="5" width="{w - 10}" height="{h}" rx="12"/></clipPath><clipPath id="v"><rect x="5" width="{w - 10}" height="{vh}"/></clipPath></defs>
<g clip-path="url(#c)"><rect x="5" width="{w - 10}" height="{h}" fill="{CARD}"/><g clip-path="url(#v)">{visual}</g>{text}</g>
<rect x="5.5" y=".5" width="{w - 11}" height="{h - 1}" rx="11.5" fill="none" stroke="{LINE}"/>
</svg>'''

def shot(name, w, h, vh, secs):       # schermata vera che scorre piano dentro la scheda
    data = base64.b64encode(open(f"assets/img/{name}.webp", "rb").read()).decode()
    css = f".p{{animation:p {secs}s ease-in-out infinite}}@keyframes p{{0%,10%{{transform:translateY(0)}}50%,60%{{transform:translateY({vh - h}px)}}100%{{transform:translateY(0)}}}}"
    return f'<image class="p" href="data:image/webp;base64,{data}" x="5" width="{w}" height="{h}"/>', css

def stopwatch():                      # l'icona dell'app ridisegnata: quadrante, due tasti, onda vocale
    cx, cy, r = 211.5, 138, 126
    bars = "".join(f'<rect class="w" x="{cx - 26 + i * 10.4 - 1:.1f}" y="{cy - 18 - h / 2:.1f}" width="2" height="{h}" rx="1" style="animation-duration:{d}s"/>'
                   for i, (h, d) in enumerate([(14, .9), (35, 1.3), (59, 1.1), (29, .8), (52, 1.4), (22, 1)]))
    key = lambda s, c: f'<rect x="-23" y="{-r - 14}" width="46" height="30" rx="6" fill="{c}" transform="translate({cx} {cy}) rotate({s * 45})"/>'
    css = ".w{transform-box:fill-box;transform-origin:center;animation:w 1s ease-in-out infinite alternate}@keyframes w{from{transform:scaleY(.3)}to{transform:scaleY(1)}}"
    return (f'<rect x="5" width="413" height="206" fill="#f4f3ef"/>{key(-1, "#fcc21b")}{key(1, "#2f6bea")}'
            f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="#232323"/><circle cx="{cx}" cy="{cy}" r="{r - 11}" fill="#060606" stroke="#3d3d3d" stroke-width="1.5"/>'
            f'<g fill="#ff4b12">{bars}</g><text x="{cx}" y="{cy + 46}" text-anchor="middle" {SANS} font-size="12.5" font-weight="500" letter-spacing="5" fill="#9a9a9a">STOPWATCH</text>'), css

def keyboard():                       # ogni tasto premuto resta segnato, come nel tester
    rows = [[1]*13 + [2], [1.5] + [1]*12 + [1.5], [1.75] + [1]*12 + [1.25], [1.25] + [1]*11 + [2.75], [1.25]*3 + [6.25] + [1.25]*4]
    u, out, n = 11.4, "", 0
    for r, row in enumerate(rows):
        x = 20
        for k in row:
            out += f'<rect class="k" x="{x:.1f}" y="{27 + r * u:.1f}" width="{k * u - 1.6:.1f}" height="{u - 1.6:.1f}" rx="2" style="animation-delay:{.4 + n * .06:.2f}s"/>'
            x += k * u; n += 1
    css = f".k{{fill:#232325;animation:k 9s steps(1,end) infinite}}@keyframes k{{0%{{fill:{PAPER}}}1.5%{{fill:{ORANGE}}}60%,100%{{fill:#232325}}}}"
    return f'<rect x="5" width="201" height="112" fill="{INK}"/>{out}', css

def beads():                          # cinque decine: i grani si accendono uno alla volta
    dim, out = "#5661f6", ""
    for i in range(55):
        a = 2 * math.pi * (i + .5) / 55 + math.pi
        out += f'<circle class="b" cx="{92 + 60 * math.cos(a):.1f}" cy="{56 + 37 * math.sin(a):.1f}" r="{3.4 if i % 11 == 10 else 2}" style="animation-delay:{.3 + i * .16:.2f}s"/>'
    out += "".join(f'<circle cx="{158 + i * 7}" cy="56" r="{3.4 if i == 0 else 2}" fill="{PAPER}"/>' for i in range(4))
    out += f'<path d="M185 56h12M190 51v10" stroke="{PAPER}" stroke-width="2.4" stroke-linecap="round"/>'
    css = f".b{{fill:{dim};animation:b 14s steps(1,end) infinite}}@keyframes b{{0%{{fill:{ORANGE}}}2%{{fill:{PAPER}}}72%,100%{{fill:{dim}}}}}"
    return f'<rect x="5" width="201" height="112" fill="{BLUE}"/>{out}', css

def pin():                            # sei cifre una alla volta, poi si azzera tutto insieme
    out = "".join(f'<circle cx="{40.5 + i * 26}" cy="56" r="8.5" fill="{INK}" stroke="{INK}" stroke-width="2.5" style="animation:d{i} 5s steps(1,end) infinite"/>' for i in range(6))
    css = "".join(f"@keyframes d{i}{{0%{{fill:{ORANGE}}}{12 + i * 8}%{{fill:{INK}}}84%,100%{{fill:{ORANGE}}}}}" for i in range(6))
    return f'<rect x="5" width="201" height="112" fill="{ORANGE}"/>{out}', css

tg, steak = shot("telegram", 413, 289, 206, 14), shot("steak", 201, 435, 112, 18)
out = {
    "hero": hero(),
    "tile-stopwatch": card(423, 276, 206, *stopwatch()[:1], "StopWatch", "Community firmware for the M5Stack StopWatch C152", "M5Stack · iPhone", stopwatch()[1]),
    "tile-telegram": card(423, 276, 206, tg[0], "Telegram Downloader", "Save every file from a Telegram group. One app, no terminal.", "Win · macOS · Linux", tg[1]),
    "tile-inputcheck": card(211, 172, 112, keyboard()[0], "InputCheck", "Keyboard and mouse tester", css=keyboard()[1]),
    "tile-rosario": card(211, 172, 112, beads()[0], "Rosario", "A guided Rosary, offline", css=beads()[1]),
    "tile-steak": card(211, 172, 112, steak[0], "Steak", "iPhone food journal", css=steak[1]),
    "tile-fakepass": card(211, 172, 112, pin()[0], "Fakepass Reborn", "Lock-screen PIN, rootless", css=pin()[1]),
}
for k, v in out.items():
    parseString(v)                    # controllo: ogni SVG deve essere XML valido
    open(f"assets/{k}.svg", "w").write(v)
    print(f"{k}: {len(v) / 1024:.0f} KB")
