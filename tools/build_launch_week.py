"""Render UReach week-1 social posts (1080x1350, 4:5) from HTML with headless Chromium."""
import base64, pathlib
from playwright.sync_api import sync_playwright

ROOT = pathlib.Path(__file__).parent
SRC = ROOT / "src"
OUT = ROOT / "posts"
OUT.mkdir(exist_ok=True)
FS = ROOT / "node_modules/@fontsource"


def b64(p):
    p = pathlib.Path(p)
    mime = "image/png" if p.suffix == ".png" else "image/jpeg"
    return f"data:{mime};base64," + base64.b64encode(p.read_bytes()).decode()


def face(fam, pkg, w):
    rules = []
    for sub, rng in (("latin", "U+0000-00FF,U+2013-2014,U+2018-201E,U+20AC,U+2022,U+00B7"), ("greek", "U+0370-03FF,U+1F00-1FFF")):
        f = FS / pkg / "files" / f"{pkg}-{sub}-{w}-normal.woff2"
        rules.append(f"@font-face{{font-family:'{fam}';font-weight:{w};src:url('{f.as_uri()}') format('woff2');unicode-range:{rng}}}")
    return "\n".join(rules)


FONTS = "\n".join([face("Display", "commissioner", w) for w in (400, 600, 800, 900)] +
                  [face("Body", "manrope", w) for w in (500, 700)])
LOGO = b64(SRC / "logo.png")

CSS = FONTS + """
:root{--ink:#1a120c;--ink2:#2a1d14;--cream:#f6eee4;--orange:#ef9b3c;--ember:#d9692a;--muted:#c9b8a6}
*{box-sizing:border-box;margin:0;padding:0}
html,body{width:1080px;height:1350px;background:var(--ink);overflow:hidden}
.post{position:relative;width:1080px;height:1350px;background:var(--ink);color:var(--cream);font-family:'Body',sans-serif}
.photo{position:absolute;left:0;top:0;width:1080px;object-fit:cover}
.fade{position:absolute;left:0;right:0;pointer-events:none}
.panel{position:absolute;left:0;right:0;bottom:0;padding:0 72px 64px}
.kicker{display:inline-flex;align-items:center;gap:14px;font:700 24px/1 'Body';letter-spacing:.22em;text-transform:uppercase;color:var(--orange)}
.kicker:before{content:"";width:44px;height:3px;background:var(--orange)}
h1{font:900 112px/0.96 'Display';letter-spacing:-.025em;margin-top:26px;color:var(--cream);text-wrap:balance}
h1 em{font-style:normal;color:var(--orange)}
.gr{font:600 34px/1.25 'Display';color:var(--muted);margin-top:22px}
.row{display:flex;justify-content:space-between;align-items:flex-end;gap:32px;margin-top:40px}
.detail{font:500 29px/1.4 'Body';color:var(--cream);opacity:.92;max-width:600px}
.price{flex:none;text-align:right}
.price small{display:block;font:700 20px/1 'Body';letter-spacing:.18em;text-transform:uppercase;color:var(--muted);margin-bottom:10px}
.price b{font:800 76px/0.9 'Display';color:var(--orange);letter-spacing:-.02em}
.price b span{font-size:34px;font-weight:600;color:var(--cream);margin-left:4px}
.foot{display:flex;justify-content:space-between;align-items:center;margin-top:44px;padding-top:30px;border-top:1px solid rgba(246,238,228,.18)}
.foot img{height:54px}
.foot .cta{font:700 26px/1 'Body';color:var(--cream);display:flex;align-items:center;gap:16px}
.foot .cta i{font-style:normal;background:var(--orange);color:var(--ink);padding:14px 22px;border-radius:999px}
.tag{position:absolute;top:44px;right:48px;font:700 18px/1 'Body';letter-spacing:.14em;text-transform:uppercase;color:#fff;background:rgba(20,14,10,.55);padding:12px 16px;border-radius:6px;backdrop-filter:blur(6px)}
"""

FOOT = f"""<div class="foot"><img src="{LOGO}" alt="UReach"><div class="cta">@ureach.world <i>Link in bio</i></div></div>"""


def page(body):
    return f"<!doctype html><html><head><meta charset='utf-8'><style>{CSS}</style></head><body><div class='post'>{body}</div></body></html>"


def photo_post(img, photo_h, pos, kicker, h1, gr, detail, plabel, price, extra="", tag="Sample work · fictional brand"):
    return page(f"""
<img class="photo" src="{b64(SRC/img)}" style="height:{photo_h}px;object-position:{pos}">
<div class="fade" style="top:{photo_h-420}px;height:422px;background:linear-gradient(180deg,rgba(26,18,12,0) 0%,rgba(26,18,12,.75) 55%,var(--ink) 100%)"></div>
{extra}
<div class="tag">{tag}</div>
<div class="panel">
  <div class="kicker">{kicker}</div>
  <h1>{h1}</h1>
  <div class="row"><div class="detail">{detail}</div>
  <div class="price"><small>{plabel}</small><b>{price}</b></div></div>
  {FOOT}
</div>""")


POSTS = {}

# 1 — Free website draft: beach restaurant photo inside a browser frame
browser = f"""
<div style="position:absolute;left:72px;right:72px;top:96px;height:560px;border-radius:22px;overflow:hidden;background:#fff;box-shadow:0 40px 90px -20px rgba(0,0,0,.7)">
  <div style="height:54px;background:#f1ebe3;display:flex;align-items:center;gap:10px;padding:0 22px">
    <i style="width:14px;height:14px;border-radius:50%;background:#e8705f"></i><i style="width:14px;height:14px;border-radius:50%;background:#efbd4e"></i><i style="width:14px;height:14px;border-radius:50%;background:#7cc06b"></i>
    <span style="margin-left:18px;flex:1;max-width:520px;background:#fff;border-radius:10px;padding:9px 16px;font:500 19px 'Body';color:#7d6f62">thalassa-kitchen.com</span></div>
  <div style="position:relative;height:506px">
    <img src="{b64(SRC/'ur00.jpg')}" style="position:absolute;inset:0;width:100%;height:100%;object-fit:cover;object-position:30% 60%">
    <div style="position:absolute;inset:0;background:linear-gradient(90deg,rgba(20,12,6,.72),rgba(20,12,6,.05) 70%)"></div>
    <div style="position:absolute;left:40px;top:30px;right:40px;display:flex;justify-content:space-between;font:700 19px 'Body';color:#fff;letter-spacing:.06em">
      <span style="font:800 24px 'Display';letter-spacing:.02em">THALASSA</span><span style="opacity:.9">MENU &nbsp; ABOUT &nbsp; CONTACT</span></div>
    <div style="position:absolute;left:40px;bottom:46px;color:#fff">
      <div style="font:800 52px/1 'Display';letter-spacing:-.01em">Dinner by the sea</div>
      <div style="font:500 22px 'Body';opacity:.9;margin-top:12px">Fresh fish &amp; meze by the sea</div>
      <div style="display:inline-block;margin-top:22px;background:#ef9b3c;color:#1a120c;font:700 21px 'Body';padding:14px 24px;border-radius:999px">Book a table</div>
    </div>
  </div>
</div>"""
POSTS["01-free-website"] = page(f"""
<div style="position:absolute;inset:0 0 auto 0;height:760px;background:radial-gradient(900px 520px at 70% 10%,#5a3518 0%,var(--ink) 70%)"></div>
{browser}
<div class="panel">
  <div class="kicker">Websites</div>
  <h1>Your website.<br><em>First draft free.</em></h1>
  <div class="row"><div class="detail">Love it, then pay a small monthly plan. Don’t love it, pay nothing.</div>
  <div class="price"><small>Then from</small><b>€29<span>/mo</span></b></div></div>
  {FOOT}
</div>
<div class="tag" style="top:30px;right:96px;background:rgba(20,14,10,.0);padding:0;font-size:16px;color:var(--muted)">Sample work · fictional brand</div>""")

# 2 — Custom painting
POSTS["02-custom-painting"] = photo_post(
    "ur15.jpg", 820, "50% 30%", "Custom painting",
    "A painting made<br>for <em>your</em> wall.",
    "Ένας πίνακας φτιαγμένος για τον δικό σας τοίχο.",
    "Send a photo of your room. We design the art and show it hanging on your wall first.",
    "One-time", "€79", tag="Sample work")

# 3 — Social media plan: grid of six sample posts
tiles = ["ur01s.jpg", "ur07s.jpg", "ur30s.jpg", "ur02s.jpg", "ur09s.jpg", "ur22s.jpg"]
grid = "".join(f'<img src="{b64(SRC/t)}" style="width:100%;height:100%;object-fit:cover;border-radius:14px">' for t in tiles)
POSTS["03-social-media"] = page(f"""
<div style="position:absolute;left:72px;right:72px;top:72px;height:600px;display:grid;grid-template-columns:repeat(3,1fr);grid-template-rows:repeat(2,1fr);gap:14px">{grid}</div>
<div class="tag" style="top:92px;right:92px">Sample work</div>
<div class="panel">
  <div class="kicker">Social media</div>
  <h1>12 posts a month.<br><em>Done for you.</em></h1>
  <div class="row"><div class="detail">Designed posts with captions in your language. Scheduling included.</div>
  <div class="price"><small>Monthly</small><b>€149<span>/mo</span></b></div></div>
  {FOOT}
</div>""")

# 4 — Logo & brand kit
POSTS["04-brand-kit"] = photo_post(
    "ur04.jpg", 820, "62% 40%", "Logo &amp; brand kit",
    "A brand people<br><em>remember.</em>",
    "Μια επωνυμία που μένει στο μυαλό.",
    "Three logo concepts and two revision rounds. Full brand kit with cards and templates: €179.",
    "Logo from", "€89")

# 5 — Promo reel: yacht with video player overlay
player = """
<div style="position:absolute;left:0;right:0;top:250px;display:flex;justify-content:center">
  <div style="width:150px;height:150px;border-radius:50%;background:rgba(246,238,228,.92);display:flex;align-items:center;justify-content:center;box-shadow:0 20px 60px rgba(0,0,0,.4)">
    <div style="width:0;height:0;border-left:48px solid #1a120c;border-top:30px solid transparent;border-bottom:30px solid transparent;margin-left:12px"></div></div></div>
<div style="position:absolute;left:72px;right:72px;top:560px;display:flex;align-items:center;gap:18px;font:700 22px 'Body';color:#fff">
  <span>0:12</span><div style="flex:1;height:6px;border-radius:3px;background:rgba(255,255,255,.35)"><div style="width:40%;height:100%;border-radius:3px;background:#ef9b3c"></div></div><span>0:30</span></div>"""
POSTS["05-promo-reel"] = photo_post(
    "ur31.jpg", 760, "28% 50%", "Promo reel",
    "30 seconds<br><em>that sell.</em>",
    "30 δευτερόλεπτα που πουλάνε.",
    "A vertical video with music, text and your logo. Ready for Reels and TikTok.",
    "One-time", "€99", extra=player)

# 6 — Jingle: studio with waveform
import random
random.seed(7)
bars = "".join(f'<i style="flex:1;height:{int(18+150*abs(random.gauss(0,.45)))}px;background:#ef9b3c;border-radius:4px;opacity:{0.55+0.45*random.random():.2f}"></i>' for _ in range(52))
wave = f'<div style="position:absolute;left:72px;right:72px;top:470px;height:190px;display:flex;align-items:center;gap:7px">{bars}</div>'
POSTS["06-jingle"] = photo_post(
    "ur26.jpg", 800, "45% 50%", "Music &amp; jingles",
    "Give your brand<br><em>a sound.</em>",
    "Δώστε στην επιχείρησή σας τον δικό της ήχο.",
    "An original jingle by a professional music producer. Yours to keep, full rights.",
    "One-time", "€149", extra=wave, tag="Sample work")

# 7 — 3D visualisation: café render with camera-angle markers
marks = """
<div style="position:absolute;left:72px;top:72px;display:flex;gap:12px">
  <span style="font:700 20px 'Body';letter-spacing:.12em;color:#1a120c;background:#ef9b3c;padding:12px 16px;border-radius:6px">VIEW 1</span>
  <span style="font:700 20px 'Body';letter-spacing:.12em;color:#fff;background:rgba(20,14,10,.55);padding:12px 16px;border-radius:6px">VIEW 2</span>
  <span style="font:700 20px 'Body';letter-spacing:.12em;color:#fff;background:rgba(20,14,10,.55);padding:12px 16px;border-radius:6px">VIEW 3</span></div>"""
POSTS["07-3d-visual"] = photo_post(
    "ur23.jpg", 820, "70% 50%", "3D visualisation",
    "See your café<br><em>before you build it.</em>",
    "Δείτε τον χώρο σας πριν τον φτιάξετε.",
    "A photo-real render of your shop, café or office from three camera angles.",
    "One-time", "€149", extra=marks, tag="Sample render")

with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page(viewport={"width": 1080, "height": 1350})
    for name, html in POSTS.items():
        f = OUT / f"{name}.html"
        f.write_text(html)
        pg.goto(f.as_uri())
        pg.wait_for_timeout(400)
        pg.evaluate("document.fonts.ready")
        pg.screenshot(path=str(OUT / f"{name}.jpg"), type="jpeg", quality=92)
        print("rendered", name)
    b.close()
