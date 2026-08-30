import json
import subprocess
from pathlib import Path
from textwrap import wrap

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).parent
BUILD = ROOT / "build"
AUDIO = ROOT / "assets" / "narration.wav"
WIDTH = 1920
HEIGHT = 1080
FPS = 30

BACKGROUND = (12, 18, 34)
PANEL = (26, 35, 58)
PANEL_LIGHT = (35, 46, 73)
WHITE = (244, 247, 255)
MUTED = (168, 180, 204)
PURPLE = (126, 99, 255)
TEAL = (52, 211, 178)
GOLD = (255, 190, 82)
RED = (255, 111, 126)


def font(size, bold=False):
    name = "DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf"
    return ImageFont.truetype(f"/usr/share/fonts/truetype/dejavu/{name}", size)


def text(draw, xy, value, size, color=WHITE, bold=False, spacing=10):
    draw.multiline_text(xy, value, font=font(size, bold), fill=color, spacing=spacing)


def card(draw, box, fill=PANEL, radius=30, outline=None):
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=2)


def header(draw, eyebrow, title, number):
    draw.rounded_rectangle((110, 72, 178, 84), radius=6, fill=PURPLE)
    text(draw, (200, 54), eyebrow.upper(), 25, MUTED, True)
    text(draw, (110, 125), title, 60, WHITE, True)
    text(draw, (1740, 65), f"0{number}", 28, MUTED, True)


def metric(draw, x, value, label, color):
    card(draw, (x, 760, x + 490, 950))
    draw.rounded_rectangle((x + 35, 800, x + 47, 910), radius=6, fill=color)
    text(draw, (x + 82, 785), value, 58, WHITE, True)
    text(draw, (x + 82, 865), label, 25, MUTED)


def title_slide(data, number):
    image = Image.new("RGB", (WIDTH, HEIGHT), BACKGROUND)
    draw = ImageDraw.Draw(image)
    draw.ellipse((1410, -260, 2150, 480), fill=(28, 35, 71), outline=PURPLE, width=4)
    draw.ellipse((1530, -140, 2030, 360), outline=TEAL, width=3)
    draw.rounded_rectangle((110, 85, 184, 99), radius=7, fill=PURPLE)
    text(draw, (215, 64), data["eyebrow"].upper(), 26, MUTED, True)
    text(draw, (110, 235), data["title"], 96, WHITE, True)
    text(draw, (110, 365), data["date"], 78, PURPLE, True)
    subtitle = "\n".join(wrap(data["subtitle"], 54))
    text(draw, (116, 485), subtitle, 34, MUTED, spacing=18)
    for index, item in enumerate(data["metrics"]):
        metric(draw, 110 + index * 550, item["value"], item["label"], [PURPLE, TEAL, GOLD][index])
    return image


def health_slide(data, number):
    image = Image.new("RGB", (WIDTH, HEIGHT), BACKGROUND)
    draw = ImageDraw.Draw(image)
    header(draw, data["eyebrow"], data["title"], number)

    card(draw, (110, 280, 725, 925))
    text(draw, (160, 330), "CYCLE TIME", 24, MUTED, True)
    text(draw, (160, 410), data["cycle_time"]["value"], 125, TEAL, True)
    text(draw, (405, 485), data["cycle_time"]["unit"], 36, WHITE, True)
    text(draw, (160, 570), data["cycle_time"]["change"], 31, TEAL, True)
    draw.line((160, 660, 675, 660), fill=PANEL_LIGHT, width=3)
    text(draw, (160, 715), "BUILD SUCCESS", 23, MUTED, True)
    text(draw, (160, 765), data["build_success"], 58, WHITE, True)
    draw.rounded_rectangle((350, 792, 665, 817), radius=12, fill=PANEL_LIGHT)
    draw.rounded_rectangle((350, 792, 655, 817), radius=12, fill=PURPLE)

    card(draw, (780, 280, 1810, 925))
    text(draw, (835, 330), "VELOCITY / STORY POINTS", 24, MUTED, True)
    values = [item["value"] for item in data["velocity"]]
    baseline = 815
    for index, item in enumerate(data["velocity"]):
        value = item["value"]
        x = 870 + index * 220
        height = int(value / max(values) * 380)
        color = PURPLE if index == len(values) - 1 else PANEL_LIGHT
        draw.rounded_rectangle((x, baseline - height, x + 120, baseline), radius=20, fill=color)
        text(draw, (x + 31, baseline - height - 55), str(value), 30, WHITE, True)
        text(draw, (x + 28, 845), item["label"], 23, MUTED, True)
    return image


def shipped_slide(data, number):
    image = Image.new("RGB", (WIDTH, HEIGHT), BACKGROUND)
    draw = ImageDraw.Draw(image)
    header(draw, data["eyebrow"], data["title"], number)
    for index, item in enumerate(data["items"]):
        column = index % 2
        row = index // 2
        x = 110 + column * 860
        y = 285 + row * 330
        card(draw, (x, y, x + 810, y + 285))
        color = [PURPLE, TEAL, GOLD, RED][index]
        draw.ellipse((x + 42, y + 48, x + 126, y + 132), fill=color)
        text(draw, (x + 65, y + 70), f"{index + 1:02d}", 22, BACKGROUND, True)
        text(draw, (x + 165, y + 46), item["title"], 36, WHITE, True)
        lines = "\n".join(wrap(item["body"], 38))
        text(draw, (x + 165, y + 115), lines, 27, MUTED, spacing=12)
    return image


def next_slide(data, number):
    image = Image.new("RGB", (WIDTH, HEIGHT), BACKGROUND)
    draw = ImageDraw.Draw(image)
    header(draw, data["eyebrow"], data["title"], number)
    card(draw, (110, 285, 1260, 925))
    for index, item in enumerate(data["goals"]):
        y = 350 + index * 175
        if index < 2:
            draw.line((178, y + 82, 178, y + 190), fill=PANEL_LIGHT, width=4)
        draw.ellipse((145, y + 28, 211, y + 94), fill=PURPLE if index == 0 else PANEL_LIGHT)
        text(draw, (165, y + 47), f"{index + 1:02d}", 18, WHITE, True)
        text(draw, (255, y + 17), item["title"], 34, WHITE, True)
        text(draw, (255, y + 70), item["body"], 25, MUTED)

    card(draw, (1320, 285, 1810, 925), fill=PURPLE)
    text(draw, (1375, 350), "PLANNED\nCAPACITY", 25, (222, 216, 255), True, spacing=5)
    text(draw, (1370, 500), data["capacity"]["value"], 125, WHITE, True)
    text(draw, (1378, 650), data["capacity"]["label"], 32, WHITE, True)
    draw.line((1375, 735, 1755, 735), fill=(166, 147, 255), width=3)
    note = "\n".join(wrap(data["capacity"]["note"], 20))
    text(draw, (1375, 785), note, 27, (222, 216, 255), spacing=10)
    return image


def probe(path, *args):
    return float(subprocess.check_output([
        "ffprobe", "-v", "error", *args,
        "-of", "default=noprint_wrappers=1:nokey=1", str(path),
    ], text=True).strip())


def manifest(name, segments):
    lines = ["ffconcat version 1.0"]
    for path, seconds in segments:
        lines.append(f"file '{path.resolve()}'")
        lines.append(f"duration {seconds:.6f}")
    lines.append(f"file '{segments[-1][0].resolve()}'")
    target = BUILD / name
    target.write_text("\n".join(lines) + "\n")
    return target


BUILD.mkdir(exist_ok=True)
source = json.loads((ROOT / "slides.json").read_text())
renderers = {
    "title": title_slide,
    "health": health_slide,
    "shipped": shipped_slide,
    "next": next_slide,
}
slide_images = [renderers[data["layout"]](data, index) for index, data in enumerate(source["slides"], 1)]
slide_paths = []
for index, image in enumerate(slide_images, 1):
    path = BUILD / f"slide-{index:02d}.png"
    image.save(path)
    slide_paths.append(path)

demo = ROOT / source["demo"]["video"]
cue = float(source["demo"]["cue_seconds"])
duration = probe(AUDIO, "-show_entries", "format=duration")
demo_duration = probe(demo, "-select_streams", "v:0", "-show_entries", "stream=duration")
slide_duration = duration / len(slide_paths)

before = []
after = []
for index, path in enumerate(slide_paths):
    start = index * slide_duration
    end = start + slide_duration
    if end <= cue:
        before.append((path, slide_duration))
    elif start >= cue:
        after.append((path, slide_duration))
    else:
        before.append((path, cue - start))
        after.append((path, end - cue))

filters = (
    f"[0:v]fps={FPS},trim=end={cue:.6f},setpts=PTS-STARTPTS,format=yuv420p,setsar=1[pre];"
    f"[1:v]fps={FPS},scale={WIDTH}:{HEIGHT}:flags=lanczos,format=yuv420p,setsar=1[mid];"
    f"[2:v]fps={FPS},trim=end={duration - cue:.6f},setpts=PTS-STARTPTS,format=yuv420p,setsar=1[post];"
    "[pre][mid][post]concat=n=3:v=1:a=0[v];"
    "[3:a]asplit=2[head][tail];"
    f"[head]atrim=end={cue:.6f},asetpts=PTS-STARTPTS,pan=stereo|c0=c0|c1=c0,"
    "aformat=sample_fmts=fltp:sample_rates=48000:channel_layouts=stereo[a0];"
    f"[1:a]atrim=end={demo_duration:.6f},asetpts=PTS-STARTPTS,"
    "aformat=sample_fmts=fltp:sample_rates=48000:channel_layouts=stereo[a1];"
    f"[tail]atrim=start={cue:.6f},asetpts=PTS-STARTPTS,pan=stereo|c0=c0|c1=c0,"
    "aformat=sample_fmts=fltp:sample_rates=48000:channel_layouts=stereo[a2];"
    "[a0][a1][a2]concat=n=3:v=0:a=1[a]"
)

subprocess.run([
    "ffmpeg", "-y", "-v", "error",
    "-f", "concat", "-safe", "0", "-i", str(manifest("slides-pre.ffconcat", before)),
    "-i", str(demo),
    "-f", "concat", "-safe", "0", "-i", str(manifest("slides-post.ffconcat", after)),
    "-i", str(AUDIO),
    "-filter_complex", filters,
    "-map", "[v]", "-map", "[a]",
    "-c:v", "libx264", "-preset", "veryfast", "-crf", "20",
    "-c:a", "aac", "-profile:a", "aac_low", "-b:a", "192k", "-ar", "48000",
    "-movflags", "+faststart",
    str(BUILD / f"{source['output']}.mp4"),
], check=True)

print(BUILD / f"{source['output']}.mp4")
