# Genera banner e schede del profilo: python3 gen.py
import math, random
BLUE, ORANGE, PAPER, INK = "#0517ff", "#ff6a00", "#f1f0eb", "#101010"
SANS = "font-family=\"'Helvetica Neue',Helvetica,Arial,sans-serif\" font-weight=\"800\""
MONO = "font-family=\"ui-monospace,SFMono-Regular,Menlo,Consolas,monospace\" font-weight=\"600\""

def blob(cx, cy, r, rough, seed):
    random.seed(seed)
    pts = [(cx + r*(1+random.uniform(-rough, rough))*math.cos(a), cy + r*(1+random.uniform(-rough, rough))*math.sin(a))
           for a in (2*math.pi*i/28 for i in range(28))]
    return " ".join(f"{x:.0f},{y:.0f}" for x, y in pts)

def hero():
    steps = [("v0.1", .42), ("v0.2", .28), ("v0.5", .16), ("v0.9", .07), ("v1.0", 0)]
    s = ""
    for i, (lab, rough) in enumerate(steps):
        cx = 190 + i*328
        last = i == len(steps)-1
        shape = (f'<circle cx="{cx}" cy="190" r="92" fill="{ORANGE}"/>' if last else
                 f'<polygon points="{blob(cx,190,92,rough,i+3)}" fill="none" stroke="{PAPER}" stroke-width="5" stroke-linejoin="round"/>')
        s += (f'<g opacity=".5">{shape}<text x="{cx}" y="340" text-anchor="middle" {MONO} font-size="24" fill="{PAPER}">{lab}</text>'
              f'<animate attributeName="opacity" values=".5;1;1;.5;.5" keyTimes="0;.08;.2;.3;1" dur="6s" begin="{i*1.1:.1f}s" repeatCount="indefinite"/></g>')
        if not last:
            s += f'<path d="M{cx+130} 190h60m-14-12 14 12-14 12" fill="none" stroke="{PAPER}" stroke-width="4" opacity=".5"/>'
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1692 760" role="img" aria-label="skfallin: tools that ship">
<rect width="1692" height="760" rx="28" fill="{BLUE}"/>
{s}
<text x="76" y="640" {SANS} font-size="250" letter-spacing="-12" fill="{PAPER}">skfallin</text>
<g {MONO} font-size="26" fill="{PAPER}">
<text x="1616" y="520" text-anchor="end">ITERATE UNTIL IT SHIPS.</text>
<text x="1616" y="562" text-anchor="end" opacity=".75">DESKTOP APPS · FIRMWARE · IPHONE · ANDROID</text>
<text x="1616" y="604" text-anchor="end" opacity=".75">RUST · SWIFT · C++ · KOTLIN · TYPESCRIPT</text>
</g>
<rect x="1196" y="630" width="420" height="12" fill="{ORANGE}"/>
</svg>'''

def tile(w, bg, fg, acc, label, name, lines, glyph, size):
    t = "".join(f'<text x="40" y="{318+i*34}" {MONO} font-size="24" fill="{fg}" opacity=".8">{l}</text>' for i, l in enumerate(lines))
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} 420" role="img" aria-label="{name}">
<rect x="6" y="6" width="{w-12}" height="408" rx="22" fill="{bg}"/>
<text x="40" y="66" {MONO} font-size="20" fill="{fg}" opacity=".8">{label}</text>
{glyph.format(fg=fg, acc=acc, bg=bg)}
<text x="40" y="270" {SANS} font-size="{size}" letter-spacing="-2" fill="{fg}">{name}</text>
{t}
</svg>'''

watch = ('<g transform="translate(700 150)"><circle r="84" fill="none" stroke="{fg}" stroke-width="10"/><rect x="-14" y="-112" width="28" height="22" fill="{fg}"/>'
         '<path d="M0 0V-58" stroke="{acc}" stroke-width="10" stroke-linecap="round"><animateTransform attributeName="transform" type="rotate" from="0" to="360" dur="8s" repeatCount="indefinite"/></path><circle r="9" fill="{fg}"/></g>')
plane = ('<g transform="translate(596 44) scale(.21)"><path d="M212 236 512 690 448 372Z" fill="{fg}"/><path d="M812 236 512 690 576 372Z" fill="{fg}"/>'
         '<path d="M448 372 512 690 576 372 512 250Z" fill="{acc}"/><rect x="252" y="744" width="520" height="56" fill="{fg}"><animate attributeName="width" values="0;520;520" keyTimes="0;.6;1" dur="3s" repeatCount="indefinite"/></rect></g>')
keys = '<g transform="translate(40 100)">' + "".join(
    f'<rect x="{c*44}" y="{r*44}" width="36" height="36" rx="6" fill="{{fg}}" opacity=".18"/>' for r in range(2) for c in range(8)) + \
    '<rect x="132" y="0" width="36" height="36" rx="6" fill="{acc}"><animate attributeName="x" values="132;132;264;264;44;44;132" dur="4s" calcMode="discrete" repeatCount="indefinite"/></rect></g>'
beads = '<g transform="translate(300 120)">' + "".join(
    f'<circle cx="{70*math.cos(2*math.pi*i/10):.0f}" cy="{70*math.sin(2*math.pi*i/10):.0f}" r="11" fill="{{{"acc" if i==0 else "fg"}}}"/>' for i in range(10)) + \
    '<animateTransform attributeName="transform" type="rotate" additive="sum" from="0" to="360" dur="20s" repeatCount="indefinite"/></g>'
random.seed(7)
x, bars = 40, ""
while x < 370:
    w = random.choice([4, 8, 12]); bars += f'<rect x="{x}" y="100" width="{w}" height="84" fill="{{fg}}"/>'; x += w + random.choice([6, 10])
bars += '<rect x="40" y="138" width="336" height="6" fill="{acc}"><animate attributeName="y" values="100;178;100" dur="3s" repeatCount="indefinite"/></rect>'
pin = '<g transform="translate(52 142)">' + "".join(
    f'<circle cx="{i*56}" r="15" fill="none" stroke="{{fg}}" stroke-width="5"/><circle cx="{i*56}" r="15" fill="{{fg}}" opacity="0">'
    f'<animate attributeName="opacity" values="0;1;1;0" keyTimes="0;.02;.9;1" dur="5s" begin="{i*.45:.2f}s" repeatCount="indefinite"/></circle>' for i in range(6)) + '</g>'

out = {
 "hero": hero(),
 "tile-stopwatch": tile(846, ORANGE, INK, PAPER, "C++ · SWIFT · FIRMWARE", "StopWatch", ["Community firmware for the M5Stack StopWatch,", "with an iPhone companion and Home Assistant."], watch, 84),
 "tile-telegram": tile(846, INK, PAPER, ORANGE, "RUST · WINDOWS · MACOS · LINUX", "Telegram Downloader", ["Save every file from a Telegram group.", "One app, no terminal."], plane, 66),
 "tile-inputcheck": tile(422, PAPER, INK, BLUE, "C++ · WIN32", "InputCheck", ["Portable keyboard and", "mouse tester."], keys, 56),
 "tile-rosario": tile(422, BLUE, PAPER, ORANGE, "KOTLIN · ANDROID", "Rosario", ["A guided Rosary,", "fully offline."], beads, 56),
 "tile-steak": tile(422, INK, PAPER, ORANGE, "SWIFT · IPHONE", "Steak", ["Food journal with", "barcode scanning."], bars, 56),
 "tile-fakepass": tile(422, ORANGE, INK, PAPER, "LOGOS · IOS TWEAK", "Fakepass", ["Lock-screen PIN for", "rootless arm64e."], pin, 56),
}
for k, v in out.items():
    open(f"assets/{k}.svg", "w").write(v)
