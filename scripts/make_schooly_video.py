"""Silent captioned walkthrough of the Schooly demo, built from real headless-Edge captures.

Every demo frame is a screenshot of explore/schooly/index.html in a given URL state; the numbers
in captions are parsed from the same page's rendered DOM. Outputs go to the site's
projects/schooly/video/ folder: schooly_demo.webm (VP9), poster.jpg, captions.vtt, shots.json.
"""
import json, re, subprocess, sys, tempfile, shutil
from pathlib import Path
import numpy as np
import cv2
from PIL import Image, ImageDraw, ImageFont

sys.stdout.reconfigure(encoding="utf-8")
SITE = Path("C:/Users/Jupyter/yuye06.github.io")
OUT = SITE / "projects/schooly/video"
OUT.mkdir(parents=True, exist_ok=True)
CAP = Path(__file__).resolve().parent / "caps"
CAP.mkdir(exist_ok=True)
EDGE = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
DEMO = "file:///C:/Users/Jupyter/yuye06.github.io/explore/schooly/index.html"
NOTE = "file:///C:/Users/Jupyter/yuye06.github.io/projects/schooly/index.html"
LIST = "file:///C:/Users/Jupyter/yuye06.github.io/projects/index.html"
VW, VH, FPS, STRIP = 1600, 900, 8, 120
DC = (18, 228, 1166, 615)   # demo cards (map + results), CSS px in a 1200x900 viewport
DSF = 1.5
NAVY, INK, MUTED, BLUE = (31, 58, 104), (20, 33, 61), (91, 100, 119), (47, 109, 181)
F = "C:/Windows/Fonts/"
def font(name, size): return ImageFont.truetype(F + name, size)
FT, FB, FS = font("segoeui.ttf", 30), font("segoeuib.ttf", 30), font("segoeui.ttf", 20)
PROFILE = Path(tempfile.mkdtemp(prefix="edgeprof_"))


def edge(args, url):
    cmd = [EDGE, "--headless=new", "--disable-gpu", "--no-first-run", "--hide-scrollbars",
           f"--user-data-dir={PROFILE}", "--virtual-time-budget=4000"] + args + [url]
    return subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=120)


def shot(name, url, w=1200, h=900):
    p = CAP / f"{name}.png"
    edge([f"--window-size={w},{h}", f"--force-device-scale-factor={DSF}", f"--screenshot={p}"], url)
    assert p.exists(), name
    return Image.open(p).convert("RGB")


def metrics(url):
    dom = edge(["--dump-dom"], url).stdout
    body = re.search(r'<tbody id="tbl">(.*?)</tbody>', dom, re.S).group(1)
    rows = []
    for tr in re.findall(r"<tr>(.*?)</tr>", body, re.S):
        cells = [re.sub(r"<[^>]+>|&nbsp;", "", c).strip() for c in re.findall(r"<td[^>]*>(.*?)</td>", tr, re.S)]
        rows.append(cells)
    num = lambda s: float(re.sub(r"[^0-9.\-]", "", s))
    return {"shade_existing": num(rows[0][1]), "shade_after": num(rows[0][2]), "bld_after": num(rows[1][2]),
            "tree_after": num(rows[2][2]), "never_existing": num(rows[3][1]), "never_after": num(rows[3][2]),
            "trees": int(rows[5][2]), "rows": rows}


def wrap(draw, text, fnt, width):
    words, lines, cur = text.split(), [], ""
    for w_ in words:
        t = (cur + " " + w_).strip()
        if draw.textlength(t, font=fnt) <= width: cur = t
        else: lines.append(cur); cur = w_
    return lines + [cur]


LAST = [""]
def frame_from(img, caption, crop=None, tag="Screen capture of the live demo · illustrative campus, not real school data"):
    LAST[0] = caption
    if crop:
        x, y, w, h = [int(v * DSF) for v in crop]
        img = img.crop((x, y, x + w, y + h))
    canvas = Image.new("RGB", (VW, VH), (236, 239, 244))
    s = min((VW - 40) / img.width, (VH - STRIP - 30) / img.height)
    im = img.resize((int(img.width * s), int(img.height * s)), Image.LANCZOS)
    canvas.paste(im, ((VW - im.width) // 2, (VH - STRIP - im.height) // 2 + 6))
    d = ImageDraw.Draw(canvas)
    d.rectangle([0, VH - STRIP, VW, VH], fill=NAVY)
    lines = wrap(d, caption, FT, VW - 80)[:2]
    y0 = VH - STRIP + (14 if len(lines) == 2 else 28)
    for i, ln in enumerate(lines): d.text((40, y0 + i * 40), ln, font=FT, fill=(255, 255, 255))
    if tag:
        tw = d.textlength(tag, font=FS)
        d.rectangle([VW - tw - 34, 8, VW - 10, 40], fill=(255, 246, 234), outline=(240, 211, 173))
        d.text((VW - tw - 22, 11), tag, font=FS, fill=(138, 75, 12))
    return canvas


def card(title, lines, foot=None):
    LAST[0] = title + ". " + " ".join(lines)
    c = Image.new("RGB", (VW, VH), (255, 255, 255))
    d = ImageDraw.Draw(c)
    d.rectangle([0, 0, 18, VH], fill=NAVY)
    d.text((110, 230), title, font=font("segoeuib.ttf", 64), fill=NAVY)
    y = 340
    for ln in lines:
        for sub in wrap(d, ln, font("segoeui.ttf", 34), VW - 260):
            d.text((110, y), sub, font=font("segoeui.ttf", 34), fill=INK); y += 50
        y += 14
    if foot: d.text((110, VH - 120), foot, font=FS, fill=MUTED)
    return c


def bars_card(base, zone, edge_, n):
    LAST[0] = f"Same {n} trees, different placement. Zone shade-hours per cell: existing {base:.2f} h; {n} trees inside the zones {zone:.2f} h; {n} trees at the campus edge {edge_:.2f} h. Values describe this invented campus only."
    c = Image.new("RGB", (VW, VH), (255, 255, 255))
    d = ImageDraw.Draw(c)
    d.rectangle([0, 0, 18, VH], fill=NAVY)
    d.text((110, 90), f"Same {n} trees, different placement", font=font("segoeuib.ttf", 52), fill=NAVY)
    d.text((110, 170), "Student-use zone shade-hours per cell, sum of nine hourly samples (08:00–16:00), computed by the demo",
           font=FS, fill=MUTED)
    vals = [("Existing campus", base, (157, 183, 216)), (f"+{n} trees inside student-use zones", zone, BLUE),
            (f"+{n} trees at the campus edge", edge_, (120, 140, 170))]
    mx = max(v for _, v, _ in vals) or 1
    y = 270
    for lab, v, col in vals:
        d.text((110, y), lab, font=FT, fill=INK)
        w = int(900 * v / mx)
        d.rectangle([110, y + 48, 110 + max(w, 3), y + 98], fill=col)
        d.text((130 + max(w, 3), y + 54), f"{v:.2f} h", font=FB, fill=INK)
        y += 160
    d.text((110, VH - 110), "Invented campus and simplified shadow geometry: these values describe this demo only, not any real school.",
           font=FS, fill=MUTED)
    return c


SHOTS = []          # (image, caption-or-None, seconds)
def add(img, caption, sec): SHOTS.append((img, LAST[0], sec))

# ---------------------------------------------------------------- captures
q = lambda **k: DEMO + "?" + "&".join(f"{a}={b}" for a, b in k.items())
N = 10
m_base = metrics(q(hour=12, t=""))  # baseline values (t= keeps URL mode without trees)
m_zone = metrics(q(preset="zone", n=N, hour=12))
m_edge = metrics(q(preset="edge", n=N, hour=12))
m_hand = metrics(q(hour=10, t="40,40;48,46;56,40;90,36;100,44"))
print(json.dumps({"base": m_base, "zone": m_zone, "edge": m_edge, "hand": m_hand}, ensure_ascii=False, indent=1))

add(card("Schooly", ["From campus evidence to community action.",
                     "A silent walkthrough of the working demo prototype: where shade reaches the ground students use, "
                     "and how tree placement changes it."],
         "Illustrative campus and simplified geometry. No real school, student or community data. Recorded 20 November 2026."),
    None, 6)
add(frame_from(shot("list", LIST, 1200, 900), "Schooly is listed with the other research projects at yuye06.github.io/projects.", tag=None), "", 5)
add(frame_from(shot("note", NOTE, 1200, 900), "The project note states the question, the approach and what the demo does and does not show.", tag=None), "", 6)
img12 = shot("base12", q(hour=12, t=""))
add(frame_from(img12, "An invented campus: buildings in gray, student-use zones in blue, existing trees in green.", crop=DC), "", 7)
add(frame_from(img12, "Shade is computed in the browser from the sun's position for 15 August at 35.1° N, on a 1 m grid.",
               crop=(40, 230, 680, 500)), "", 6)
for h in range(8, 17):
    add(frame_from(shot(f"sweep{h:02d}", q(hour=h, t="")),
                   f"{h:02d}:00 MDT. Moving the time slider recomputes building and tree shadows for each of nine school hours.", crop=DC), "", 1.3)
add(frame_from(img12, f"Existing campus: {m_base['shade_existing']:.2f} h of zone shade per cell; "
                      f"{m_base['never_existing']:.0f}% of zone ground is never shaded at the sampled hours.",
               crop=(700, 230, 470, 330)), "", 6)
imgz = shot("zone12", q(preset="zone", n=N, hour=12))
add(frame_from(imgz, f"Preset: {N} proposed trees (dashed) inside the student-use zones.", crop=DC), "", 6)
add(frame_from(imgz, f"Zone shade rises from {m_zone['shade_existing']:.2f} h to {m_zone['shade_after']:.2f} h per cell, "
                     f"and never-shaded ground falls to {m_zone['never_after']:.0f}%.", crop=(700, 230, 470, 440)), "", 7)
add(frame_from(shot("zone15", q(preset="zone", n=N, hour=15)), "At 15:00 the same trees cast longer shadows across the zones.", crop=DC), "", 4)
imge = shot("edge12", q(preset="edge", n=N, hour=12))
add(frame_from(imge, f"Preset: the same {N} trees along the campus edge instead.", crop=DC), "", 6)
add(frame_from(imge, f"Zone shade stays at {m_edge['shade_after']:.2f} h per cell: on this campus the edge trees' shadows "
                     f"almost never reach student-use ground.", crop=(700, 230, 470, 440)), "", 7)
add(frame_from(shot("edge15", q(preset="edge", n=N, hour=15)), "At 15:00 the edge trees' shadows still fall mostly outside the zones.", crop=DC), "", 4)
add(bars_card(m_base["shade_existing"], m_zone["shade_after"], m_edge["shade_after"], N), "", 8)
add(frame_from(shot("hand10", q(hour=10, t="40,40;48,46;56,40;90,36;100,44")),
               "Trees can also be placed by clicking on the plan and removed by clicking them; every value is recalculated.", crop=DC), "", 6)
add(frame_from(shot("open", q(hour=12, t="", open=1), 1200, 1500),
               "The method and its limits are on the page: simplified crowns, clear sky, one date; not SOLWEIG, Tmrt or UTCI.",
               crop=(700, 520, 470, 640)), "", 8)
add(card("Planned, not yet built", [
    "Community step: example feedback from staff and families, grouped by topic and correctable by reviewers.",
    "Decision step: an evidence-linked brief with a human approval state. No external action is taken.",
    "Research-derived New Mexico campus layers only after a data-release review."]), "", 8)
add(card("Try it", ["Demo: yuye06.github.io/explore/schooly", "Project note: yuye06.github.io/projects/schooly",
                    "Source: github.com/yuye06/yuye06.github.io"],
         "Prototype by Yuye Zhou. Illustrative data only; your edits stay in your own browser."), "", 6)

def fmt(s):
    h, r = divmod(s, 3600); m, r = divmod(r, 60)
    return f"{int(h):02d}:{int(m):02d}:{r:06.3f}"

# ---------------------------------------------------------------- encode
XF = int(0.5 * FPS)
path = OUT / "schooly_demo.webm"
wr = cv2.VideoWriter(str(path), cv2.VideoWriter_fourcc(*"VP90"), FPS, (VW, VH))
assert wr.isOpened()
cues, t, prev = [], 0.0, None
captions = []
for i, (img, _, sec) in enumerate(SHOTS):
    arr = cv2.cvtColor(np.asarray(img), cv2.COLOR_RGB2BGR)
    n = int(round(sec * FPS))
    k0 = 0
    if prev is not None and sec >= 3:
        for k in range(XF):
            a = (k + 1) / (XF + 1)
            wr.write(cv2.addWeighted(prev, 1 - a, arr, a, 0)); k0 += 1
    for _ in range(n - k0): wr.write(arr)
    prev = arr
    t1 = t + n / FPS
    captions.append((t, t1))
    t = t1
wr.release()
total = t
img_list = [s[0] for s in SHOTS]
QA = CAP / "frames"; QA.mkdir(exist_ok=True)
for i, im in enumerate(img_list): im.resize((800, 450)).save(QA / f"f{i:02d}.png")
vtt = ["WEBVTT", ""]
for i, ((a, b), (_, cap, _)) in enumerate(zip(captions, SHOTS), 1):
    vtt += [str(i), f"{fmt(a)} --> {fmt(b)}", cap, ""]
(OUT / "captions.vtt").write_text(chr(10).join(vtt), encoding="utf-8")
(OUT / "transcript.json").write_text(json.dumps([{"start": round(a, 1), "end": round(b, 1), "text": cap} for (a, b), (_, cap, _) in zip(captions, SHOTS)], ensure_ascii=False, indent=1), encoding="utf-8")
img_list[5].save(OUT / "poster.jpg", quality=88)

# cue text: reuse the caption strings by re-deriving them from the frames list
print("duration_s", round(total, 1), "shots", len(SHOTS), "size_MB", round(path.stat().st_size / 1e6, 2))
json.dump({"duration_s": total, "times": captions, "metrics": {"base": m_base, "zone": m_zone, "edge": m_edge, "hand": m_hand}},
          open(OUT / "shots.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
shutil.rmtree(PROFILE, ignore_errors=True)
