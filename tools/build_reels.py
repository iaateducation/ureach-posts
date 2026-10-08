"""Vertical 1080x1920 reels from UReach sample photos: animated photo card + text overlay + end card."""
import base64, pathlib, subprocess
from playwright.sync_api import sync_playwright

R = pathlib.Path(__file__).parent
SRC, OUT = R / "src", R / "reels"
OUT.mkdir(exist_ok=True)
FS = R / "node_modules/@fontsource"


def b64(p):
    return "data:image/png;base64," + base64.b64encode(pathlib.Path(p).read_bytes()).decode()


def face(fam, pkg, w):
    out = []
    for sub, rng in (("latin", "U+0000-00FF,U+2013-2014,U+2018-201E,U+20AC,U+2022,U+00B7"), ("greek", "U+0370-03FF,U+1F00-1FFF")):
        f = FS / pkg / "files" / f"{pkg}-{sub}-{w}-normal.woff2"
        out.append(f"@font-face{{font-family:'{fam}';font-weight:{w};src:url('{f.as_uri()}');unicode-range:{rng}}}")
    return "\n".join(out)


FONTS = "\n".join([face("D", "commissioner", w) for w in (600, 800, 900)] + [face("B", "manrope", w) for w in (500, 700)])
LOGO = b64(SRC / "logo.png")
CSS = FONTS + """
*{margin:0;padding:0;box-sizing:border-box}
html,body{width:1080px;height:1920px;background:transparent;overflow:hidden;color:#f6eee4;font-family:'B',sans-serif}
.k{display:inline-flex;align-items:center;gap:16px;font:700 30px/1 'B';letter-spacing:.2em;text-transform:uppercase;color:#ef9b3c}
.k:before{content:"";width:52px;height:4px;background:#ef9b3c}
h1{font:900 112px/.96 'D';letter-spacing:-.025em;margin-top:30px}
h1 em{font-style:normal;color:#ef9b3c}
.gr{font:600 40px/1.25 'D';color:#d9c9b6;margin-top:26px}
.tag{position:absolute;right:56px;font:700 22px/1 'B';letter-spacing:.14em;text-transform:uppercase;color:#fff;background:rgba(20,14,10,.6);padding:14px 18px;border-radius:8px}
"""

REELS = {
    "thalassa": ("ur00.jpg", "Websites", "A website that<br>makes people <em>hungry.</em>",
                 "Ιστοσελίδα με δωρεάν πρώτο σχέδιο.", "Free first draft, then", "€49/mo", "Sample work · fictional brand"),
    "cafe": ("ur23.jpg", "3D visualisation", "Walk through it<br><em>before you build it.</em>",
             "Δείτε τον χώρο σας σε 3D.", "Photo-real render", "from €149", "Sample render"),
    "studio": ("ur26.jpg", "Studio &amp; venue sound", "Great rooms<br><em>sound great.</em>",
               "Ακουστικός σχεδιασμός για στούντιο και μπαρ.", "Acoustic layout + gear plan", "from €249", "Sample work"),
    "yacht": ("ur31.jpg", "Brand video", "Sell the<br><em>experience.</em>",
              "Ένα βίντεο που πουλάει την εμπειρία σας.", "Script, voice-over, music", "€279", "Sample work · fictional brand"),
}

# photo card geometry
CW, CH, CY = 1080, 605, 470


def overlay(kicker, h1, gr, line1, price, tag):
    return f"""<!doctype html><html><head><meta charset=utf-8><style>{CSS}</style></head><body>
<div style="position:absolute;left:64px;top:150px"><img src="{LOGO}" style="height:64px"></div>
<div class="tag" style="top:{CY+24}px">{tag}</div>
<div style="position:absolute;left:64px;right:64px;top:{CY+CH+90}px">
  <div class="k">{kicker}</div><h1>{h1}</h1><div class="gr">{gr}</div>
  <div style="display:flex;justify-content:space-between;align-items:flex-end;margin-top:56px;padding-top:36px;border-top:2px solid rgba(246,238,228,.2)">
    <div style="font:500 34px/1.35 'B'">{line1}</div>
    <div style="font:800 76px/.9 'D';color:#ef9b3c;text-align:right">{price}</div></div>
</div></body></html>"""


END = f"""<!doctype html><html><head><meta charset=utf-8><style>{CSS}
body{{background:#1a120c}}</style></head><body>
<div style="position:absolute;inset:0;background:radial-gradient(900px 700px at 50% 30%,#5a3518 0%,#1a120c 70%)"></div>
<div style="position:absolute;left:0;right:0;top:560px;display:flex;flex-direction:column;align-items:center;gap:56px;text-align:center">
  <img src="{LOGO}" style="height:150px">
  <div style="font:900 84px/1 'D';letter-spacing:-.02em">Your website.<br><span style="color:#ef9b3c">First draft free.</span></div>
  <div style="font:600 40px/1.3 'D';color:#d9c9b6">Websites · Logos · Videos · Music · Art</div>
  <div style="font:700 40px/1 'B';background:#ef9b3c;color:#1a120c;padding:26px 44px;border-radius:999px">Link in bio · @ureach.world</div>
  <div style="font:500 34px/1 'B';color:#d9c9b6">WhatsApp +357 95 909 207</div>
</div></body></html>"""

with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page(viewport={"width": 1080, "height": 1920})
    for name, (img, k, h, g, l1, pr, tag) in REELS.items():
        (OUT / f"{name}_ov.html").write_text(overlay(k, h, g, l1, pr, tag))
        pg.goto((OUT / f"{name}_ov.html").as_uri()); pg.wait_for_timeout(300)
        pg.screenshot(path=str(OUT / f"{name}_ov.png"), omit_background=True)
    (OUT / "end.html").write_text(END)
    pg.goto((OUT / "end.html").as_uri()); pg.wait_for_timeout(300)
    pg.screenshot(path=str(OUT / "end.png"))
    b.close()

D, FPS = 10, 30
for name, (img, *_rest) in REELS.items():
    src = SRC / img
    n = D * FPS
    fc = (
        # blurred, darkened full-frame background
        f"[0:v]split=2[s1][s2];[s1]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,boxblur=40:2,eq=brightness=-0.32:saturation=0.85,setsar=1[bg];"
        # slowly zooming photo card (render at 2x then downscale for smooth motion)
        f"[s2]trim=end_frame=1,scale=2160:1210:force_original_aspect_ratio=increase,crop=2160:1210,zoompan=z='1+0.10*on/{n}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={n}:s=2160x1210:fps={FPS},scale={CW}:{CH},setsar=1[card];"
        f"[bg][card]overlay=0:{CY}[a];"
        f"[1:v]format=rgba,fade=in:st=0.5:d=0.8:alpha=1[ov];"
        f"[a][ov]overlay=0:0[b];"
        f"[2:v]format=rgba,fade=in:st=7.4:d=0.6:alpha=1[end];"
        f"[b][end]overlay=0:0,format=yuv420p[v]"
    )
    cmd = ["ffmpeg", "-y", "-loglevel", "error",
           "-loop", "1", "-framerate", str(FPS), "-t", str(D), "-i", str(src),
           "-loop", "1", "-framerate", str(FPS), "-t", str(D), "-i", str(OUT / f"{name}_ov.png"),
           "-loop", "1", "-framerate", str(FPS), "-t", str(D), "-i", str(OUT / "end.png"),
           "-f", "lavfi", "-t", str(D), "-i", "anullsrc=r=44100:cl=stereo",
           "-filter_complex", fc, "-map", "[v]", "-map", "3:a",
           "-c:v", "libx264", "-profile:v", "high", "-preset", "slow", "-crf", "20", "-r", str(FPS),
           "-c:a", "aac", "-b:a", "128k", "-movflags", "+faststart", "-t", str(D),
           str(OUT / f"{name}.mp4")]
    subprocess.run(cmd, check=True)
    print("built", name)
